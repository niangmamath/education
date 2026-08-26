"""A third authored kind: the course, given before a palier is tested.

Étape 15. An assessment measures and a remediation sheet repairs after a gap
is found; neither teaches before the fact. A course fills that gap: a native
lesson followed by a few explained questions, given automatically alongside
the next palier's assessment (never a gate in front of it — décision du
propriétaire, 26 août 2026) and read by the same authored engine the other
two kinds already share.

No new table. A course reuses `authored_questions` for its wording and
`catalog_activities.guidance` for its lesson, exactly as a remediation sheet
does; only the kind it may carry needs widening.

Revision ID: 0017_course_kind
Revises: 0016_classe_et_passage
Create Date: 2026-08-26
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0017_course_kind"
down_revision: str | None = "0016_classe_et_passage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_catalog_activities_kind", "catalog_activities", type_="check"
    )
    op.create_check_constraint(
        "ck_catalog_activities_kind",
        "catalog_activities",
        "kind IN ('h5p', 'phet', 'video', 'assessment', 'remediation', 'course')",
    )


def downgrade() -> None:
    # Same bargain 0013 and 0014 already took: reverting gives up what the
    # migration made possible. `assignments.activity_id` restricts on delete,
    # so a course's assignments (and, by cascade, their attempts, responses
    # and readings — a course has none by construction, but this stays
    # correct if one is ever added by mistake) go first.
    op.execute(
        "DELETE FROM assignments WHERE activity_id IN "
        "(SELECT id FROM catalog_activities WHERE kind = 'course')"
    )
    op.execute("DELETE FROM catalog_activities WHERE kind = 'course'")
    op.drop_constraint(
        "ck_catalog_activities_kind", "catalog_activities", type_="check"
    )
    op.create_check_constraint(
        "ck_catalog_activities_kind",
        "catalog_activities",
        "kind IN ('h5p', 'phet', 'video', 'assessment', 'remediation')",
    )
