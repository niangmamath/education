"""School referential: levels, subjects, domains and competencies.

The referential is **versioned as a whole**. A version holds its own levels,
subjects, domains and competencies, so re-importing a programme produces a new
coherent set instead of editing the one results already point at.

That guarantee is carried by the schema rather than by the import code: every
child row repeats the `version_id` of its parent and references it through a
composite foreign key. A competency therefore cannot be attached to a domain of
another version, and a prerequisite cannot cross a version boundary — the
database refuses it, whatever writes to it.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Final

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# A version is prepared, then serves, then steps aside. Only one may serve at a
# time, which a partial unique index enforces below.
VERSION_STATUS_DRAFT: Final = "draft"
VERSION_STATUS_PUBLISHED: Final = "published"
VERSION_STATUS_ARCHIVED: Final = "archived"
VERSION_STATUSES: Final = (
    VERSION_STATUS_DRAFT,
    VERSION_STATUS_PUBLISHED,
    VERSION_STATUS_ARCHIVED,
)

CODE_LENGTH: Final = 50
LABEL_LENGTH: Final = 200


class ReferentialVersion(Base):
    """One coherent edition of the school referential."""

    __tablename__ = "ref_versions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_ref_versions_code"),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_ref_versions_status",
        ),
        # Two published versions would leave every reader guessing which one is
        # in force, so the database allows only one.
        Index(
            "uq_ref_versions_single_published",
            "status",
            unique=True,
            postgresql_where=text("status = 'published'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    label: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=VERSION_STATUS_DRAFT,
        server_default=VERSION_STATUS_DRAFT,
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

    levels: Mapped[list[Level]] = relationship(
        back_populates="version", cascade="all, delete-orphan", passive_deletes=True
    )
    subjects: Mapped[list[Subject]] = relationship(
        back_populates="version", cascade="all, delete-orphan", passive_deletes=True
    )


class Level(Base):
    """A school year, from CP to CM2 for the MVP."""

    __tablename__ = "ref_levels"
    __table_args__ = (
        UniqueConstraint("version_id", "code", name="uq_ref_levels_version_code"),
        # Not redundant with the primary key: it is what lets a child row point
        # at this row *and* at its version in a single foreign key.
        UniqueConstraint("id", "version_id", name="uq_ref_levels_id_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ref_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    label: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    # School years are ordered, and that order is neither alphabetical nor
    # derivable from the code.
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    version: Mapped[ReferentialVersion] = relationship(back_populates="levels")
    competencies: Mapped[list[Competency]] = relationship(
        back_populates="level",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="domain,level",
    )


class Subject(Base):
    """A school subject, mathematics or French for the MVP."""

    __tablename__ = "ref_subjects"
    __table_args__ = (
        UniqueConstraint("version_id", "code", name="uq_ref_subjects_version_code"),
        UniqueConstraint("id", "version_id", name="uq_ref_subjects_id_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ref_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    label: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    version: Mapped[ReferentialVersion] = relationship(back_populates="subjects")
    domains: Mapped[list[Domain]] = relationship(
        back_populates="subject", cascade="all, delete-orphan", passive_deletes=True
    )


class Domain(Base):
    """A field inside a subject, such as numbers and calculation."""

    __tablename__ = "ref_domains"
    __table_args__ = (
        UniqueConstraint("version_id", "code", name="uq_ref_domains_version_code"),
        UniqueConstraint("id", "version_id", name="uq_ref_domains_id_version"),
        # The composite reference is the point: a domain cannot sit under a
        # subject belonging to another version.
        ForeignKeyConstraint(
            ["subject_id", "version_id"],
            ["ref_subjects.id", "ref_subjects.version_id"],
            name="fk_ref_domains_subject",
            ondelete="CASCADE",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    label: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    subject: Mapped[Subject] = relationship(back_populates="domains")
    competencies: Mapped[list[Competency]] = relationship(
        back_populates="domain",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="competencies,domain,level",
    )


class Competency(Base):
    """What a child is expected to master, at one level and in one domain."""

    __tablename__ = "ref_competencies"
    __table_args__ = (
        # The stable identifier the rest of the platform quotes, unique inside
        # its version so the same competency keeps its code from edition to
        # edition.
        UniqueConstraint("version_id", "code", name="uq_ref_competencies_version_code"),
        UniqueConstraint("id", "version_id", name="uq_ref_competencies_id_version"),
        ForeignKeyConstraint(
            ["domain_id", "version_id"],
            ["ref_domains.id", "ref_domains.version_id"],
            name="fk_ref_competencies_domain",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["level_id", "version_id"],
            ["ref_levels.id", "ref_levels.version_id"],
            name="fk_ref_competencies_level",
            ondelete="CASCADE",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    domain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    level_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    label: Mapped[str] = mapped_column(String(LABEL_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Both parent references include `version_id`, which SQLAlchemy sees as two
    # relationships writing the same column. They do, and they always agree:
    # `version_id` is set explicitly on every insert and a composite foreign key
    # refuses any disagreement. The overlap is therefore declared rather than
    # worked around, and the warning it would otherwise raise stays out of the
    # way of the real ones.
    domain: Mapped[Domain] = relationship(
        back_populates="competencies", overlaps="competencies,level"
    )
    level: Mapped[Level] = relationship(
        back_populates="competencies", overlaps="competencies,domain"
    )

    prerequisites: Mapped[list[CompetencyPrerequisite]] = relationship(
        back_populates="competency",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="[CompetencyPrerequisite.competency_id, CompetencyPrerequisite.version_id]",
    )


class CompetencyPrerequisite(Base):
    """An edge of the competency tree: one competency requires another first.

    The pair is the primary key, so the same prerequisite cannot be declared
    twice. A competency cannot require itself, and both ends belong to the same
    version. A longer cycle, where A requires B which requires A, is beyond what
    a constraint can express and belongs to the import validation of 07.2.
    """

    __tablename__ = "ref_competency_prerequisites"
    __table_args__ = (
        CheckConstraint(
            "competency_id <> prerequisite_id",
            name="ck_ref_prerequisites_not_self",
        ),
        ForeignKeyConstraint(
            ["competency_id", "version_id"],
            ["ref_competencies.id", "ref_competencies.version_id"],
            name="fk_ref_prerequisites_competency",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["prerequisite_id", "version_id"],
            ["ref_competencies.id", "ref_competencies.version_id"],
            name="fk_ref_prerequisites_prerequisite",
            ondelete="CASCADE",
        ),
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    competency: Mapped[Competency] = relationship(
        back_populates="prerequisites",
        foreign_keys=[competency_id, version_id],
    )
