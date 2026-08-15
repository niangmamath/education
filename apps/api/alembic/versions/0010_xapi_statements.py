"""Store the statements the content runtime sends, as the server received them.

Kept apart from `attempt_responses` on purpose. A statement is what a source
said; a response is what the platform holds a child to have answered. The second
is derived from the first when the first is an answer, and `response_id` records
that link so a conclusion can be traced back to the observation behind it.

`(attempt_id, statement_id)` is unique so that a retransmission is recognised
instead of counted twice, and it is scoped to the attempt rather than global so
that no one can suppress another family's statement by claiming its identifier.

Revision ID: 0010_xapi_statements
Revises: 0009_question_attribution
Create Date: 2026-08-15
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_xapi_statements"
down_revision: str | None = "0009_question_attribution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "xapi_statements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("statement_id", sa.String(length=64), nullable=False),
        sa.Column("actor_key", sa.String(length=64), nullable=False),
        sa.Column("verb_id", sa.String(length=255), nullable=False),
        sa.Column("object_id", sa.String(length=500), nullable=False),
        sa.Column("result_success", sa.Boolean(), nullable=True),
        sa.Column("result_response", sa.Text(), nullable=True),
        sa.Column("statement", postgresql.JSONB(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("response_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["response_id"], ["attempt_responses.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_xapi_statements_attempt_statement",
        "xapi_statements",
        ["attempt_id", "statement_id"],
        unique=True,
    )
    op.create_index("ix_xapi_statements_attempt", "xapi_statements", ["attempt_id"])


def downgrade() -> None:
    op.drop_index("ix_xapi_statements_attempt", table_name="xapi_statements")
    op.drop_index("uq_xapi_statements_attempt_statement", table_name="xapi_statements")
    op.drop_table("xapi_statements")
