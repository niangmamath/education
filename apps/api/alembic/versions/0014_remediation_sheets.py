"""Remediation sheets: a second kind of activity written here.

Three changes, and each one answers a question the initiation assessment left
open.

**`assessment_questions` becomes `authored_questions`.** The table was named
after the only thing that used it. A remediation sheet asks a question exactly
the way the assessment does — a prompt, a list of choices, an index the client
never sees — so it holds its questions here rather than in a second table with
the same four columns. Two tables would drift, and the grading code would have to
learn which one to look in.

**`authored_questions.explanation`** is what a child is told once she has
answered. It is the difference between a repair and a second test: the assessment
leaves it empty on purpose, because telling a child the answer to a question that
is measuring her corrupts the reading being taken.

**`catalog_activities.guidance`** is what the sheet teaches before it asks. It is
addressed to the child, unlike `summary`, which describes the activity to adults.

The `remediation` kind joins the check constraint. That constraint is the point:
adding a kind takes a migration, which is the friction ADR-012 asked for and the
reason nothing can be smuggled into the catalogue by an application-level edit.

Revision ID: 0014_remediation_sheets
Revises: 0013_initiation_assessment
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014_remediation_sheets"
down_revision: str | None = "0013_initiation_assessment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_KINDS_BEFORE = "kind IN ('h5p', 'phet', 'video', 'assessment')"
_KINDS_AFTER = "kind IN ('h5p', 'phet', 'video', 'assessment', 'remediation')"


def upgrade() -> None:
    op.rename_table("assessment_questions", "authored_questions")

    # A rename carries the constraints under their old names; renaming them too
    # keeps `\d authored_questions` readable and keeps the model's declared names
    # true, which is what a later autogenerate compares against.
    op.execute(
        "ALTER INDEX uq_assessment_questions_ref RENAME TO uq_authored_questions_ref"
    )
    op.execute(
        "ALTER INDEX ix_assessment_questions_activity "
        "RENAME TO ix_authored_questions_activity"
    )
    op.execute(
        "ALTER TABLE authored_questions RENAME CONSTRAINT "
        "ck_assessment_questions_correct TO ck_authored_questions_correct"
    )
    op.execute(
        "ALTER TABLE authored_questions RENAME CONSTRAINT "
        "ck_assessment_questions_choices TO ck_authored_questions_choices"
    )

    op.add_column(
        "authored_questions", sa.Column("explanation", sa.Text(), nullable=True)
    )
    op.add_column("catalog_activities", sa.Column("guidance", sa.Text(), nullable=True))

    op.drop_constraint("ck_catalog_activities_kind", "catalog_activities")
    op.create_check_constraint(
        "ck_catalog_activities_kind", "catalog_activities", _KINDS_AFTER
    )


def downgrade() -> None:
    # Sheets have to go before the kind stops being legal, and their assignments
    # before them: `catalog_activities` is referenced with RESTRICT, so deleting
    # an activity somebody was given fails rather than cascading. The initiation
    # assessment's migration learnt this the same way.
    op.execute(
        "DELETE FROM assignments WHERE activity_id IN "
        "(SELECT id FROM catalog_activities WHERE kind = 'remediation')"
    )
    op.execute("DELETE FROM catalog_activities WHERE kind = 'remediation'")

    op.drop_constraint("ck_catalog_activities_kind", "catalog_activities")
    op.create_check_constraint(
        "ck_catalog_activities_kind", "catalog_activities", _KINDS_BEFORE
    )

    op.drop_column("catalog_activities", "guidance")
    op.drop_column("authored_questions", "explanation")

    op.execute(
        "ALTER TABLE authored_questions RENAME CONSTRAINT "
        "ck_authored_questions_choices TO ck_assessment_questions_choices"
    )
    op.execute(
        "ALTER TABLE authored_questions RENAME CONSTRAINT "
        "ck_authored_questions_correct TO ck_assessment_questions_correct"
    )
    op.execute(
        "ALTER INDEX ix_authored_questions_activity "
        "RENAME TO ix_assessment_questions_activity"
    )
    op.execute(
        "ALTER INDEX uq_authored_questions_ref RENAME TO uq_assessment_questions_ref"
    )
    op.rename_table("authored_questions", "assessment_questions")
