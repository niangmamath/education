"""Assigning an activity from the catalogue to one child.

An assignment is the link between the catalogue and a person, and it is the
first table of the project that holds both. It therefore carries two guarantees
the rest of the platform will lean on.

The first is **history**. An assignment is never rewritten and never deleted: it
is cancelled, or it runs its course. Re-giving the same activity creates a second
row, so that "she did it twice" and "she did it once" stay different facts. A
project rule says an observation must never overwrite the history, and this is
where that starts to cost something.

The second is that an activity that has been assigned **cannot be deleted**. The
foreign key restricts rather than cascades: losing an activity would leave every
attempt of step 10 pointing at nothing. Activities are archived, not removed.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Final

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.catalog import Activity
from app.models.identity import Child, Parent

# Given, taken up, finished — or called off. Nothing returns from the last two:
# re-giving an activity is a new assignment, not a revived one.
ASSIGNMENT_STATUS_ASSIGNED: Final = "assigned"
ASSIGNMENT_STATUS_IN_PROGRESS: Final = "in_progress"
ASSIGNMENT_STATUS_COMPLETED: Final = "completed"
ASSIGNMENT_STATUS_CANCELLED: Final = "cancelled"
ASSIGNMENT_STATUSES: Final = (
    ASSIGNMENT_STATUS_ASSIGNED,
    ASSIGNMENT_STATUS_IN_PROGRESS,
    ASSIGNMENT_STATUS_COMPLETED,
    ASSIGNMENT_STATUS_CANCELLED,
)

# The two states in which an activity is still owed. They are what the partial
# unique index below counts, and what the child's "to do" list shows.
ASSIGNMENT_OPEN_STATUSES: Final = (
    ASSIGNMENT_STATUS_ASSIGNED,
    ASSIGNMENT_STATUS_IN_PROGRESS,
)

# Who decided. A parent may let the platform assign a remediation for her, and
# when she does she must still be able to tell what she chose from what was done
# in her name. Set by the server; a payload that mentions it is refused.
ASSIGNMENT_ORIGIN_PARENT: Final = "parent"
ASSIGNMENT_ORIGIN_SYSTEM: Final = "system"
ASSIGNMENT_ORIGINS: Final = (ASSIGNMENT_ORIGIN_PARENT, ASSIGNMENT_ORIGIN_SYSTEM)

MAX_NOTE_LENGTH: Final = 500

# A child cannot be given an unbounded pile of work. The ceiling counts only what
# is still owed, so finishing frees a slot; it exists so that a slip of the hand,
# or a parent working through a list, cannot bury a six-year-old.
MAX_OPEN_ASSIGNMENTS: Final = 20


class Assignment(Base):
    """One activity given to one child by their parent."""

    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('assigned', 'in_progress', 'completed', 'cancelled')",
            name="ck_assignments_status",
        ),
        # A status without its moment would be a claim with no date behind it.
        CheckConstraint(
            "(status <> 'in_progress' AND status <> 'completed') "
            "OR started_at IS NOT NULL",
            name="ck_assignments_started_at",
        ),
        CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_assignments_completed_at",
        ),
        CheckConstraint(
            "status <> 'cancelled' OR cancelled_at IS NOT NULL",
            name="ck_assignments_cancelled_at",
        ),
        CheckConstraint("origin IN ('parent', 'system')", name="ck_assignments_origin"),
        # The same activity may not be owed twice at once — that would be a
        # slip of the hand, not an intention. It may be given again once the
        # first one is finished or called off, and that is a second row.
        Index(
            "uq_assignments_open_per_activity",
            "child_id",
            "activity_id",
            unique=True,
            postgresql_where=text("status IN ('assigned', 'in_progress')"),
        ),
        # The child's own lists are the most frequent read of this table.
        Index("ix_assignments_child_status", "child_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_children.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Who gave it. Kept even after the fact, because a family may have more than
    # one adult one day and "who asked for this" is a question worth answering.
    assigned_by_parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_parents.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Restricted, not cascaded: an activity that has been given to someone is
    # part of that child's history and may no longer be removed.
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_activities.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ASSIGNMENT_STATUS_ASSIGNED,
        server_default=ASSIGNMENT_STATUS_ASSIGNED,
    )
    # Whether the parent asked for this, or the platform did on her behalf. The
    # owning parent stays on `assigned_by_parent_id` either way — the assignment
    # belongs to that account — and this says who made the call.
    origin: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ASSIGNMENT_ORIGIN_PARENT,
        server_default=ASSIGNMENT_ORIGIN_PARENT,
    )
    # A word from the parent to the child, shown with the activity.
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # When it is expected, if it is expected at all. A date and not a moment: a
    # child's week is counted in days, and an hour of the day would be a
    # precision nobody means.
    due_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    child: Mapped[Child] = relationship()
    assigned_by: Mapped[Parent] = relationship()
    activity: Mapped[Activity] = relationship()
