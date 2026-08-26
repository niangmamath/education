"""Giving a child the course behind the palier she is about to sit.

An assessment measures a competency; a remediation sheet repairs one already
found in gap. Neither teaches beforehand — until this module, a child was
tested cold on whatever her prerequisites unlocked, on the standing
assumption that she had learned it somewhere off the platform.

A course closes that gap the same way the assessment itself is given: the
platform assigns it, rather than waiting for a parent to think of it
(décision du propriétaire, 26 août 2026, extending the exception ADR-014
first opened and ADR-021 already extended once). It is **not** a gate: the
assessment behind the same competency is given exactly as before, at the
same moment, whether or not its course was ever opened. A child confident in
the material is free to sit straight for the exam.

Nothing here decides *which* competencies are next — that stays
`app.assessment.tiers.next_sitting`'s question, computed once by the caller
and passed in, so this module never re-reads the prerequisite graph or the
child's progress on its own.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import ASSIGNMENT_OPEN_STATUSES, Assignment
from app.models.catalog import (
    ACTIVITY_KIND_COURSE,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.models.identity import Child

COURSE_NOTE = (
    "Une leçon pour découvrir cette compétence avant l’examen. Tu peux aussi "
    "passer l’examen directement si tu penses déjà savoir."
)


async def course_for(db: AsyncSession, competency_code: str) -> Activity | None:
    """The published course working on this competency, if one exists.

    The most recently created one, in the unlikely event two match — the
    same tie-break `assessment_for` uses, for the same reason: replacing a
    course is publishing a new one, and nothing here needs to choose among
    several at once.
    """
    return await db.scalar(
        select(Activity)
        .join(ActivityCompetency, ActivityCompetency.activity_id == Activity.id)
        .where(
            ActivityCompetency.competency_code == competency_code,
            Activity.kind == ACTIVITY_KIND_COURSE,
            Activity.status == ACTIVITY_STATUS_PUBLISHED,
        )
        .order_by(Activity.created_at.desc())
        .limit(1)
    )


async def give_to(db: AsyncSession, child: Child, due: Sequence[str]) -> None:
    """Give a child the courses behind the competencies due for her next sitting.

    `due` is `next_sitting`'s own output, already computed by the caller —
    this function never asks the graph or the progress reading again.

    Silent wherever there is nothing to give: no published course for a
    competency, or one already open for her. That last check is the same
    open-assignment idempotence `assessment.service.give_to` already uses,
    and for the same reason: this is the platform giving something to
    itself, so it must not pile up a second course while the first is still
    sitting there unopened.

    A course is assigned directly, bypassing `assign_activity`'s ceiling on
    open assignments — the same bargain the assessment already makes. It is
    not a parent's request that could reasonably be refused; it is the
    platform's own act, and skipping it silently because a family's list was
    already full would make the exception inconsistent with itself.
    """
    for competency_code in due:
        course = await course_for(db, competency_code)
        if course is None:
            continue

        already_open = await db.scalar(
            select(Assignment.id).where(
                Assignment.child_id == child.id,
                Assignment.activity_id == course.id,
                Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
            )
        )
        if already_open is not None:
            continue

        db.add(
            Assignment(
                child_id=child.id,
                assigned_by_parent_id=child.parent_id,
                activity_id=course.id,
                note=COURSE_NOTE,
            )
        )
    await db.flush()
