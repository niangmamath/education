"""Identity and family persistence models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Final

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.security import FAMILY_CODE_LENGTH

# A child profile exists before it may be used: one created by its own parent is
# usable at once, one a child opened by itself waits for that parent.
CHILD_STATUS_PENDING: Final = "pending"
CHILD_STATUS_ACTIVE: Final = "active"
CHILD_STATUS_DISABLED: Final = "disabled"
CHILD_STATUSES: Final = (
    CHILD_STATUS_PENDING,
    CHILD_STATUS_ACTIVE,
    CHILD_STATUS_DISABLED,
)


class Parent(Base):
    """Adult account that owns and manages child profiles."""

    __tablename__ = "auth_parents"
    __table_args__ = (
        UniqueConstraint("email", name="uq_auth_parents_email"),
        UniqueConstraint("family_code", name="uq_auth_parents_family_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    # The identifier a child types to reach this family. It is the parent's public
    # handle, which is why it is neither the email nor the primary key: those two
    # must never travel on a child's login screen.
    family_code: Mapped[str] = mapped_column(String(FAMILY_CODE_LENGTH), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    children: Mapped[list[Child]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", passive_deletes=True
    )


class Child(Base):
    """Restricted child profile attached to exactly one parent account in the MVP."""

    __tablename__ = "auth_children"
    __table_args__ = (
        # Uniqueness is familial, not global: two families may each have a `lea`,
        # and it is the family code that tells them apart at login. The composite
        # index this constraint creates also serves lookups by parent, so the
        # foreign key needs no index of its own.
        UniqueConstraint(
            "parent_id", "pseudonym", name="uq_auth_children_parent_pseudonym"
        ),
        CheckConstraint(
            "char_length(pseudonym) >= 3", name="ck_auth_children_pseudonym_length"
        ),
        CheckConstraint(
            "status IN ('pending', 'active', 'disabled')",
            name="ck_auth_children_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_parents.id", ondelete="CASCADE"),
        nullable=False,
    )
    pseudonym: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=CHILD_STATUS_ACTIVE,
        server_default=CHILD_STATUS_ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent: Mapped[Parent] = relationship(back_populates="children")
