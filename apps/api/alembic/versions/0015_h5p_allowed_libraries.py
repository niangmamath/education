"""ADR-012 amended: eight H5P libraries instead of one.

The pilot admitted `H5P.TrueFalse 1.8` and refused everything else. One type
cannot carry a subject: a dictation has to be heard, an ordering has to be
dragged, and a true-or-false question expresses neither. The owner amended the
decision on 17 August 2026 and validated the list.

The constraint stays a constraint — that is the point of ADR-012. Adding a type
still costs a migration and an amendment, so nothing can be smuggled into the
catalogue by an application-level edit.

**The version stops being pinned**, and that is a deliberate loosening. Freezing
is done by `sha256`, which says "these are the bytes that were vetted"; two
builds of one library version are not the same file, and the version string
cannot tell them apart. Pinning it here only ever refused a package for being
newer than a constant nobody remembered to raise.

Revision ID: 0015_h5p_allowed_libraries
Revises: 0014_remediation_sheets
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0015_h5p_allowed_libraries"
down_revision: str | None = "0014_remediation_sheets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CONSTRAINT = "ck_catalog_h5p_packages_allowed_library"
_TABLE = "catalog_h5p_packages"

_BEFORE = "library_name = 'H5P.TrueFalse' AND library_version = '1.8'"
_AFTER = (
    "library_name IN ("
    "'H5P.TrueFalse', 'H5P.MultiChoice', 'H5P.SingleChoiceSet', "
    "'H5P.Blanks', 'H5P.MarkTheWords', 'H5P.DragText', "
    "'H5P.DragQuestion', 'H5P.Dictation')"
)


def upgrade() -> None:
    op.drop_constraint(_CONSTRAINT, _TABLE)
    op.create_check_constraint(_CONSTRAINT, _TABLE, _AFTER)


def downgrade() -> None:
    # Packages of the newly admitted types would violate the old constraint, and
    # they are files somebody vetted rather than rows to keep at any cost: the
    # activity survives, only its package goes.
    op.execute(
        f"DELETE FROM {_TABLE} WHERE NOT "
        "(library_name = 'H5P.TrueFalse' AND library_version = '1.8')"
    )
    op.drop_constraint(_CONSTRAINT, _TABLE)
    op.create_check_constraint(_CONSTRAINT, _TABLE, _BEFORE)
