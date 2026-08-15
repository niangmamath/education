"""Give an assignment an optional due date.

A date and not a moment: a child's week is counted in days, and an hour of the
day would be a precision nobody means. It is nullable because most activities
are simply given, without being expected by any particular day.

Revision ID: 0007_assignment_due_date
Revises: 0006_assignments
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_assignment_due_date"
down_revision: str | None = "0006_assignments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("assignments", sa.Column("due_on", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("assignments", "due_on")
