"""Attribute questions to competencies, and record where a response came from.

Two corrections to what step 10 left open.

`catalog_activity_questions` is **optional**, and that is the point: without it
the platform cannot tell which question works on which competency — H5P does not
say — so a reading applies to every competency of the activity. With it, each
question counts only towards what it actually works on. The rows are declared by
whoever registers the activity, because only that person knows.

`attempt_responses.source` makes the trust boundary visible. `declared` means the
browser said so; `xapi` will mean the runtime's own statement reached the server.
Recording which is which now is what lets step 11 decide what prevails without
having to guess about rows written before it existed.

Revision ID: 0009_question_attribution
Revises: 0008_attempts
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_question_attribution"
down_revision: str | None = "0008_attempts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_activity_questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("activity_id", sa.UUID(), nullable=False),
        sa.Column("question_ref", sa.String(length=200), nullable=False),
        sa.Column("competency_code", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["catalog_activities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "activity_id",
            "question_ref",
            "competency_code",
            name="uq_catalog_activity_questions",
        ),
    )
    op.create_index(
        "ix_catalog_activity_questions_activity",
        "catalog_activity_questions",
        ["activity_id"],
    )

    op.add_column(
        "attempt_responses",
        sa.Column(
            "source", sa.String(length=16), server_default="declared", nullable=False
        ),
    )
    op.create_check_constraint(
        "ck_attempt_responses_source",
        "attempt_responses",
        "source IN ('declared', 'xapi')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_attempt_responses_source", "attempt_responses", type_="check"
    )
    op.drop_column("attempt_responses", "source")
    op.drop_index(
        "ix_catalog_activity_questions_activity",
        table_name="catalog_activity_questions",
    )
    op.drop_table("catalog_activity_questions")
