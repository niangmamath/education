"""Create assignments, the link between the catalogue and a child.

Two constraints carry rules rather than shapes. The activity reference
**restricts** instead of cascading: an activity that has been given to someone is
part of that child's history and may no longer be deleted. The partial unique
index refuses the same activity being owed twice at once, while leaving it free
to be given again once the first assignment is finished or called off — which is
a second row, never a revived one.

Revision ID: 0006_assignments
Revises: 0005_catalog_activities
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_assignments"
down_revision: str | None = "0005_catalog_activities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("child_id", sa.UUID(), nullable=False),
        sa.Column("assigned_by_parent_id", sa.UUID(), nullable=False),
        sa.Column("activity_id", sa.UUID(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default="assigned", nullable=False
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('assigned', 'in_progress', 'completed', 'cancelled')",
            name="ck_assignments_status",
        ),
        sa.CheckConstraint(
            "(status <> 'in_progress' AND status <> 'completed') "
            "OR started_at IS NOT NULL",
            name="ck_assignments_started_at",
        ),
        sa.CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_assignments_completed_at",
        ),
        sa.CheckConstraint(
            "status <> 'cancelled' OR cancelled_at IS NOT NULL",
            name="ck_assignments_cancelled_at",
        ),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["catalog_activities.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by_parent_id"], ["auth_parents.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["child_id"], ["auth_children.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assignments_child_status", "assignments", ["child_id", "status"]
    )
    op.create_index(
        "uq_assignments_open_per_activity",
        "assignments",
        ["child_id", "activity_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('assigned', 'in_progress')"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_assignments_open_per_activity",
        table_name="assignments",
        postgresql_where=sa.text("status IN ('assigned', 'in_progress')"),
    )
    op.drop_index("ix_assignments_child_status", table_name="assignments")
    op.drop_table("assignments")
