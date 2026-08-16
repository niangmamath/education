"""Let the parent set how far the platform may act, and record who acted.

Two columns, and they exist together because neither is honest without the other.

`auth_children.remediation_mode` is the parent's answer to "may the platform
assign a repair for me?". It is held on the child rather than on the parent:
trust in automation is about one child's situation, and a family with a
six-year-old and an eleven-year-old plausibly answers differently for each.
`proposed` is the default, so a parent who never opens the setting is never
acted for.

`assignments.origin` says who made the call. A parent who lets the platform act
must still be able to tell what she chose from what was done in her name — and
without this column, the two would look identical the next day.

Revision ID: 0011_remediation_settings
Revises: 0010_xapi_statements
Create Date: 2026-08-16
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_remediation_settings"
down_revision: str | None = "0010_xapi_statements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_children",
        sa.Column(
            "remediation_mode",
            sa.String(length=16),
            server_default="proposed",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_auth_children_remediation_mode",
        "auth_children",
        "remediation_mode IN ('proposed', 'automatic')",
    )

    op.add_column(
        "assignments",
        sa.Column(
            "origin", sa.String(length=16), server_default="parent", nullable=False
        ),
    )
    op.create_check_constraint(
        "ck_assignments_origin", "assignments", "origin IN ('parent', 'system')"
    )


def downgrade() -> None:
    op.drop_constraint("ck_assignments_origin", "assignments", type_="check")
    op.drop_column("assignments", "origin")
    op.drop_constraint(
        "ck_auth_children_remediation_mode", "auth_children", type_="check"
    )
    op.drop_column("auth_children", "remediation_mode")
