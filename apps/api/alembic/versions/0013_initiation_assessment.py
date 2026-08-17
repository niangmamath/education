"""The first step of the MVP loop, which had never been built.

The project's own definition of the MVP reads: *Parent crée un enfant → **enfant
réalise un diagnostic** → compétences mises à jour → lacune détectée → Quick
Repair recommandé*. Every arrow after the second exists. The second did not, so a
child registered on Monday had no observed competency, therefore no diagnostic,
therefore no recommendation: the journey started empty and stayed empty until a
parent thought of assigning something.

An initiation assessment is a fourth kind of activity. It is **not H5P**, and
that is a decision rather than a shortcut: each of its questions has to be tied
to a competency of *our* referential, and no external bank can supply that tie —
it exists nowhere but here. Authoring it natively also costs nothing in the
places H5P costs a great deal: no library to freeze, no type to admit into
ADR-012's allow-list, and no shared content volume to arrange.

`assessment_questions` holds the wording; `catalog_activity_questions`, which
already existed, keeps holding the attribution. Two tables, one writer, and the
engine that reads a result never learns that this activity was authored here
rather than imported.

Revision ID: 0013_initiation_assessment
Revises: 0012_drop_automatic_remediation
Create Date: 2026-08-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013_initiation_assessment"
down_revision: str | None = "0012_drop_automatic_remediation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_catalog_activities_kind", "catalog_activities", type_="check"
    )
    op.create_check_constraint(
        "ck_catalog_activities_kind",
        "catalog_activities",
        "kind IN ('h5p', 'phet', 'video', 'assessment')",
    )

    op.create_table(
        "assessment_questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("activity_id", sa.UUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        # The same identifier the responses carry, so a question's reading joins
        # to its wording without a second convention.
        sa.Column("question_ref", sa.String(length=200), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(), nullable=False),
        sa.Column("correct_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["catalog_activities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "activity_id", "question_ref", name="uq_assessment_questions_ref"
        ),
        sa.CheckConstraint(
            "correct_index >= 0", name="ck_assessment_questions_correct"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(choices) >= 2", name="ck_assessment_questions_choices"
        ),
    )
    op.create_index(
        "ix_assessment_questions_activity", "assessment_questions", ["activity_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_questions_activity", table_name="assessment_questions")
    op.drop_table("assessment_questions")
    # What the assessments produced goes with them, and the order is forced by
    # the schema rather than chosen: `assignments.activity_id` restricts on
    # delete, deliberately — an activity given to a child is part of her history
    # and may not be removed under her. So the assignments go first, taking their
    # attempts, responses and readings by cascade, and the activities follow.
    #
    # This is the one place that rule is set aside, and only for rows the target
    # schema cannot represent at all: under it, `assessment` is not a kind an
    # activity may have. Reverting a migration gives up what the migration made
    # possible — the same bargain as dropping a column with its data — and
    # nothing that predates it is touched.
    op.execute(
        "DELETE FROM assignments WHERE activity_id IN "
        "(SELECT id FROM catalog_activities WHERE kind = 'assessment')"
    )
    op.execute("DELETE FROM catalog_activities WHERE kind = 'assessment'")
    op.drop_constraint(
        "ck_catalog_activities_kind", "catalog_activities", type_="check"
    )
    op.create_check_constraint(
        "ck_catalog_activities_kind",
        "catalog_activities",
        "kind IN ('h5p', 'phet', 'video')",
    )
