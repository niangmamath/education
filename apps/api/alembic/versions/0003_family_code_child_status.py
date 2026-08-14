"""Add the parent family code and turn the child flag into a status.

Pseudonym uniqueness moves from global to familial: a child is reached through
its parent's family code, so two families may each hold the same pseudonym.

Revision ID: 0003_family_code_child_status
Revises: 0002_identity_family_models
Create Date: 2026-08-14
"""

import secrets
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_family_code_child_status"
down_revision: str | None = "0002_identity_family_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Repeated from `app.core.security` on purpose: a migration must keep producing
# the same result years later, even once the application constant has moved on.
FAMILY_CODE_LENGTH = 6
FAMILY_CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def _mint_family_code(taken: set[str]) -> str:
    while True:
        code = "".join(
            secrets.choice(FAMILY_CODE_ALPHABET) for _ in range(FAMILY_CODE_LENGTH)
        )
        if code not in taken:
            taken.add(code)
            return code


def upgrade() -> None:
    op.add_column(
        "auth_parents",
        sa.Column("family_code", sa.String(length=FAMILY_CODE_LENGTH), nullable=True),
    )

    # Existing accounts predate the code, so each one is given its own before the
    # column is closed to nulls.
    connection = op.get_bind()
    taken: set[str] = set()
    for row in connection.execute(sa.text("SELECT id FROM auth_parents")).fetchall():
        connection.execute(
            sa.text("UPDATE auth_parents SET family_code = :code WHERE id = :id"),
            {"code": _mint_family_code(taken), "id": row[0]},
        )

    op.alter_column("auth_parents", "family_code", nullable=False)
    op.create_unique_constraint(
        "uq_auth_parents_family_code", "auth_parents", ["family_code"]
    )

    op.add_column(
        "auth_children",
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="active",
        ),
    )
    op.execute(
        "UPDATE auth_children SET status = CASE WHEN is_active "
        "THEN 'active' ELSE 'disabled' END"
    )
    op.create_check_constraint(
        "ck_auth_children_status",
        "auth_children",
        "status IN ('pending', 'active', 'disabled')",
    )
    op.drop_column("auth_children", "is_active")

    op.drop_constraint("uq_auth_children_pseudonym", "auth_children", type_="unique")
    op.create_unique_constraint(
        "uq_auth_children_parent_pseudonym", "auth_children", ["parent_id", "pseudonym"]
    )
    # The composite unique index above starts with `parent_id`, so the standalone
    # index on that column would only duplicate it.
    op.drop_index("ix_auth_children_parent_id", table_name="auth_children")


def downgrade() -> None:
    op.create_index(
        "ix_auth_children_parent_id", "auth_children", ["parent_id"], unique=False
    )
    op.drop_constraint(
        "uq_auth_children_parent_pseudonym", "auth_children", type_="unique"
    )
    # Restoring global uniqueness is impossible over data this revision allowed:
    # two families each holding a `lea` cannot both keep it. The check turns a raw
    # constraint violation into a sentence saying what has to be arbitrated, and
    # no pseudonym is ever rewritten behind the owner's back.
    duplicates = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT count(*) FROM (SELECT pseudonym FROM auth_children "
                "GROUP BY pseudonym HAVING count(*) > 1) AS shared"
            )
        )
        .scalar_one()
    )
    if duplicates:
        raise RuntimeError(
            f"{duplicates} pseudonyme(s) partagé(s) par plusieurs familles. "
            "Le retour à une unicité globale demande de les arbitrer à la main "
            "avant de rejouer ce downgrade."
        )

    op.create_unique_constraint(
        "uq_auth_children_pseudonym", "auth_children", ["pseudonym"]
    )

    op.add_column(
        "auth_children",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute("UPDATE auth_children SET is_active = (status = 'active')")
    op.drop_constraint("ck_auth_children_status", "auth_children", type_="check")
    op.drop_column("auth_children", "status")

    op.drop_constraint("uq_auth_parents_family_code", "auth_parents", type_="unique")
    op.drop_column("auth_parents", "family_code")
