"""Add the parent family code and turn the child flag into a status.

Pseudonym uniqueness moves from global to familial: a child is reached through
its parent's family code, so two families may each hold the same pseudonym.

Revision ID: 0003_family_code_child_status
Revises: 0002_identity_family_models
Create Date: 2026-08-14
"""

import logging
import secrets
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

logger = logging.getLogger("alembic.runtime.migration")

revision: str = "0003_family_code_child_status"
down_revision: str | None = "0002_identity_family_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Repeated from `app.core.security` on purpose: a migration must keep producing
# the same result years later, even once the application constant has moved on.
FAMILY_CODE_LENGTH = 6
FAMILY_CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"

# Used only by the downgrade, to rename the pseudonyms two families ended up
# sharing once this revision allowed it.
PSEUDONYM_MAX_LENGTH = 50
SUFFIX_LENGTH = 6


def _mint_family_code(taken: set[str]) -> str:
    while True:
        code = "".join(
            secrets.choice(FAMILY_CODE_ALPHABET) for _ in range(FAMILY_CODE_LENGTH)
        )
        if code not in taken:
            taken.add(code)
            return code


def _variant(pseudonym: str, child_id: str, taken: set[str]) -> str:
    """Return a free pseudonym derived from this one and the profile identifier.

    The suffix grows only if the short form is already taken, so the renamed
    pseudonym stays as close as possible to the one the family chose.
    """
    marker = str(child_id).replace("-", "")
    for length in range(SUFFIX_LENGTH, len(marker) + 1):
        suffix = f"-{marker[:length]}"
        candidate = f"{pseudonym[: PSEUDONYM_MAX_LENGTH - len(suffix)]}{suffix}"
        if candidate not in taken:
            return candidate

    raise RuntimeError(f"aucun pseudonyme libre dérivable de « {pseudonym} »")


def _free_the_shared_pseudonyms() -> None:
    """Make pseudonyms globally unique again, renaming as few profiles as possible.

    This revision let two families each hold a `lea`, so the global constraint
    this downgrade restores no longer fits the data. Refusing to run would leave
    an operator stuck mid-rollback, so the conflicts are settled by a rule rather
    than by hand: within a shared pseudonym, the oldest profile keeps it and the
    others take a suffix drawn from their own identifier.

    Every rename is logged, because a child's pseudonym is what that child types
    to log in: whoever runs this downgrade has to know which ones changed.
    """
    connection = op.get_bind()
    shared = connection.execute(
        sa.text(
            "SELECT id, pseudonym FROM auth_children WHERE pseudonym IN ("
            "  SELECT pseudonym FROM auth_children"
            "  GROUP BY pseudonym HAVING count(*) > 1"
            ") ORDER BY pseudonym, created_at, id"
        )
    ).fetchall()
    if not shared:
        return

    taken = {
        row[0]
        for row in connection.execute(sa.text("SELECT pseudonym FROM auth_children"))
    }
    kept: set[str] = set()

    for child_id, pseudonym in shared:
        if pseudonym not in kept:
            kept.add(pseudonym)
            continue

        renamed = _variant(pseudonym, child_id, taken)
        taken.add(renamed)
        connection.execute(
            sa.text("UPDATE auth_children SET pseudonym = :renamed WHERE id = :id"),
            {"renamed": renamed, "id": child_id},
        )
        logger.warning(
            "Pseudonyme « %s » partagé entre familles, profil %s renommé en « %s »",
            pseudonym,
            child_id,
            renamed,
        )


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
    _free_the_shared_pseudonyms()
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
