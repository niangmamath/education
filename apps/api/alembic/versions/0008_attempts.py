"""Create attempts, their responses and the results read from them.

Three tables, and the line between them is the point of the step: an attempt and
a response are facts, a result is an interpretation. The interpretation records
which rule produced it and the counts it read, so that "why" has an answer.

Two constraints carry rules. The partial unique index allows one attempt in
progress per assignment, so two requests to start arriving together cannot both
win — the second is refused by the database rather than by a check that read the
table a moment earlier. Responses carry no unique key on the question: answering
twice is two facts, and the later does not erase the earlier.

Revision ID: 0008_attempts
Revises: 0007_assignment_due_date
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_attempts"
down_revision: str | None = "0007_assignment_due_date"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attempts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default="in_progress", nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned')",
            name="ck_attempts_status",
        ),
        sa.CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_attempts_completed_at",
        ),
        sa.ForeignKeyConstraint(
            ["assignment_id"], ["assignments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attempts_assignment", "attempts", ["assignment_id"])
    op.create_index(
        "uq_attempts_one_in_progress",
        "attempts",
        ["assignment_id"],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'"),
    )

    op.create_table(
        "attempt_responses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("question_ref", sa.String(length=200), nullable=False),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attempt_responses_attempt", "attempt_responses", ["attempt_id"])

    op.create_table(
        "attempt_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("competency_code", sa.String(length=50), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("answered", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("rule_code", sa.String(length=50), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "outcome IN ('mastered', 'partial', 'not_mastered')",
            name="ck_attempt_results_outcome",
        ),
        sa.CheckConstraint(
            "answered >= 0 AND correct >= 0 AND correct <= answered",
            name="ck_attempt_results_counts",
        ),
        sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_attempt_results_competency",
        "attempt_results",
        ["attempt_id", "competency_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_attempt_results_competency", table_name="attempt_results")
    op.drop_table("attempt_results")
    op.drop_index("ix_attempt_responses_attempt", table_name="attempt_responses")
    op.drop_table("attempt_responses")
    op.drop_index(
        "uq_attempts_one_in_progress",
        table_name="attempts",
        postgresql_where=sa.text("status = 'in_progress'"),
    )
    op.drop_index("ix_attempts_assignment", table_name="attempts")
    op.drop_table("attempts")
