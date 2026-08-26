"""Handing a new child her initiation assessment, and reading what it says.

A child who has just been activated has done nothing, so the platform knows
nothing about her: no competency observed, no difficulty to propose, no
remediation. The dashboards are honest about it and completely empty, and they
stay that way until an adult happens to assign something. The project's own MVP
definition never intended that — it puts a diagnostic immediately after the
child is created.

So the assessment is **given by the platform**, at the moment a child enters a
class, and again every time she clears a palier — the same exception,
extended one notch rather than a new one created. That is the single place
where the platform assigns anything, and the exception is argued rather than
assumed: a diagnostic that requires a parent to think of it is a diagnostic
that does not happen, and everything downstream — the reading, the gaps, the
repairs — has nothing to work from until it does. Remediation stays what it
was: proposed, never given.

**One assessment per class, served palier by palier.** What you ask a CI and
what you ask a CM2 have nothing in common, so there is one activity per level
and the child's declared class decides which. But that one activity is no
longer served whole in one sitting: `app.assessment.tiers` decides which of
its competencies are due right now — the palier a child has not yet cleared —
and `give_to` only re-gives the same activity, as a fresh `Assignment`, when
that palier is non-empty. A child who is promoted enters a class she has
never been assessed on, and receives that class's first palier for the same
reason a new child receives hers: without it, the platform knows nothing
about the year she is starting.

A child whose class is not declared receives nothing, and that is deliberate. The
alternative — guessing a class — would put a CM2 assessment in front of a
six-year-old, or the reverse, and produce a reading that looks real.

What is left here is **policy**: which assessment is in force, who gets one, and
when. Reading its questions and grading an answer are the same for every activity
this platform writes, so they live in `app.authored.service` and are shared with
the remediation sheets.
"""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment import tiers
from app.course import service as course_service
from app.models.assignment import (
    ASSIGNMENT_OPEN_STATUSES,
    Assignment,
)
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
)
from app.models.identity import Child

NO_ASSESSMENT_MESSAGE = "Aucun examen d’entrée n’est publié pour cette classe"


async def assessment_for(db: AsyncSession, level_code: str | None) -> Activity | None:
    """The entry assessment in force for one class, if one is published.

    One at a time per class, by taking the most recently created: replacing an
    assessment is publishing a new one, and the old one keeps every reading it
    produced. Nothing here rewrites what a previous assessment concluded.

    No class, no assessment. Falling back to "any published assessment" would put
    a CM2 paper in front of a six-year-old and call the result a reading.
    """
    if level_code is None:
        return None

    return await db.scalar(
        select(Activity)
        .where(
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Activity.status == ACTIVITY_STATUS_PUBLISHED,
            Activity.level_code == level_code,
        )
        .order_by(Activity.created_at.desc())
        .limit(1)
    )


async def give_to(db: AsyncSession, child: Child) -> None:
    """Give a child the palier of her class's assessment that is due now,
    and the courses behind it (étape 15).

    Silent whenever there is nothing to give: no class declared, no
    assessment published for it, a palier already waiting for her, or every
    competency of her class already tested. Activating a profile, clearing a
    palier, or promoting her must not fail because the platform has nothing
    new to propose — those are the parent's or the child's acts, and the
    assessment is ours.

    `due` is computed once and shared with `course.service.give_to`, so a
    course reaches a child at the same moment as the assessment behind the
    same competency — never before, since nothing is due before it, and
    never as a gate in front of it, since giving one is unconditional on the
    other. Courses are given even when an assessment for this palier is
    already open: `due` reads the same either way, since nothing has been
    tested yet.

    The idempotence check for the assessment itself is deliberately about
    *open* assignments, the same shape `assignments.service.assign_activity`
    already uses, rather than "a row exists at all": the whole point of a
    palier is that this activity is re-given, as a new row, once its
    previous sitting is completed.
    """
    due = await tiers.next_sitting(db, child)
    await course_service.give_to(db, child, due)
    if not due:
        return

    assessment = await assessment_for(db, child.level_code)
    if assessment is None:
        return

    already_open = await db.scalar(
        select(Assignment.id).where(
            Assignment.child_id == child.id,
            Assignment.activity_id == assessment.id,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
    )
    if already_open is not None:
        return

    db.add(
        Assignment(
            child_id=child.id,
            assigned_by_parent_id=child.parent_id,
            activity_id=assessment.id,
            note="Un petit test pour savoir par où commencer. Il n’y a pas de note.",
        )
    )
    await db.flush()


async def is_done(db: AsyncSession, child: Child) -> bool:
    """Whether nothing is currently waiting to be sat, and nothing new is due.

    Scoped to her current class rather than to any assessment ever: a child
    promoted to CE2 owes CE2's first palier and has finished nothing about it
    yet, and an interface told otherwise would hide the one thing she still
    owes — deliberately its own query rather than `pending_for`, which is not
    scoped to a class and must stay that way for what it already serves. A
    gap already tested and not yet mastered does not make this `False`
    either — that gap is the diagnostic's to show a parent, not a fresh
    sitting to prepare for the child.
    """
    waiting = await db.scalar(
        select(Assignment.id)
        .join(Activity, Activity.id == Assignment.activity_id)
        .where(
            Assignment.child_id == child.id,
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Activity.level_code == child.level_code,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
        .limit(1)
    )
    if waiting is not None:
        return False
    return not await tiers.next_sitting(db, child)


async def pending_for(db: AsyncSession, child_id: uuid.UUID) -> Assignment | None:
    """The assessment waiting for this child, if one is."""
    return await db.scalar(
        select(Assignment)
        .join(Activity, Activity.id == Assignment.activity_id)
        .where(
            Assignment.child_id == child_id,
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
        .limit(1)
    )
