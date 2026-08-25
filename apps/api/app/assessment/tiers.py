"""Which competencies a child's next sitting should test.

An enfant is never tested on a whole class at once: she is tested palier by
palier, gagné un à un (décision du propriétaire, 25 août 2026). This module
is the one place that decides what "the current palier" is, so `give_to` and
`is_done` in `app.assessment.service` can stay policy about *when* a sitting
is due, never about *which competencies* it covers.

A palier is not stored. It is read from the same three sources every other
derived state in this project reads from: the published referential's
prerequisite graph, and the child's own progress — recomputed at every call,
never persisted, for the same reason ADR-015 gives for the diagnostic.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import OUTCOME_MASTERED
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.models.identity import Child
from app.progress import service as progress_service
from app.referential import graph as referential_graph


async def next_sitting(db: AsyncSession, child: Child) -> list[str]:
    """Competency codes due for this child's next sitting in her own class.

    Empty when nothing is due — no class declared, no assessment published for
    it, every competency it names already tested, or what remains untested is
    still waiting on a prerequisite of its own. That last case is not a
    sitting to prepare: a competency whose prerequisite is itself unmastered
    is the diagnostic and remediation's business, exactly as
    `defer-behind-prerequisite` already keeps it out of a recommendation.

    The candidate competencies come from the assessment's own
    `catalog_activity_competencies` — what the catalogue says this class's
    paper actually asks — not from the referential graph, which only refines
    the order and the prerequisite gating among them (ADR-013).
    """
    if child.level_code is None:
        return []

    assessment = await db.scalar(
        select(Activity).where(
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Activity.status == ACTIVITY_STATUS_PUBLISHED,
            Activity.level_code == child.level_code,
        )
    )
    if assessment is None:
        return []

    codes = (
        await db.scalars(
            select(ActivityCompetency.competency_code).where(
                ActivityCompetency.activity_id == assessment.id
            )
        )
    ).all()
    if not codes:
        return []

    competency_graph = await referential_graph.load(db, level_code=child.level_code)
    progress = await progress_service.child_progress(db, child.id)
    tested = {row.competency_code for row in progress.competencies}
    mastered = {
        row.competency_code
        for row in progress.competencies
        if row.latest_outcome == OUTCOME_MASTERED
    }
    return competency_graph.frontier(codes, mastered=mastered, tested=tested)
