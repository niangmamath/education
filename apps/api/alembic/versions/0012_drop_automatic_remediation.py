"""Take back the automatic remediation, columns included.

`0011` added a per-child setting and a column saying whether an assignment came
from the parent or from the platform. The owner has since decided that this
version assigns nothing by itself, so the setting configures a mode that no
longer exists and `origin` can only ever hold one value.

Both are dropped rather than left in place "for later". A column with a single
possible value is read by the next person as a distinction the code makes, and
it does not; keeping it would cost a misunderstanding every time it is met, and
bringing it back is one migration.

What is kept from `0011` is what the owner asked for and did not take back: a
competency whose prerequisite is in gap is not proposed at all, the score is
weighted by attempts, and a parent can give the proposals in one call. None of
those needed a column.

Revision ID: 0012_drop_automatic_remediation
Revises: 0011_remediation_settings
Create Date: 2026-08-16
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_drop_automatic_remediation"
down_revision: str | None = "0011_remediation_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_assignments_origin", "assignments", type_="check")
    op.drop_column("assignments", "origin")
    op.drop_constraint(
        "ck_auth_children_remediation_mode", "auth_children", type_="check"
    )
    op.drop_column("auth_children", "remediation_mode")


def downgrade() -> None:
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
