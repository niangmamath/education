"""Handing a new child her initiation assessment, and reading what it says.

A child who has just been activated has done nothing, so the platform knows
nothing about her: no competency observed, no difficulty to propose, no
remediation. The dashboards are honest about it and completely empty, and they
stay that way until an adult happens to assign something. The project's own MVP
definition never intended that — it puts a diagnostic immediately after the
child is created.

So the assessment is **given by the platform**, once, at activation. That is the
single place where the platform assigns anything, and the exception is argued
rather than assumed: a diagnostic that requires a parent to think of it is a
diagnostic that does not happen, and everything downstream — the reading, the
gaps, the repairs — has nothing to work from until it does. Remediation stays
what it was: proposed, never given.

**Answers are graded here, never in the browser.** The questions travel without
their correct index; an answer comes back as a position in the list, and the
server compares. Shipping the answers with the questions would make the
assessment a questionnaire.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import (
    ASSIGNMENT_OPEN_STATUSES,
    ASSIGNMENT_STATUS_COMPLETED,
    Assignment,
)
from app.models.attempt import Attempt
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    AssessmentQuestion,
)
from app.models.identity import Child

NO_ASSESSMENT_MESSAGE = "Aucun examen d’initiation n’est publié"
QUESTION_UNKNOWN_MESSAGE = "Cette question n’appartient pas à cet examen"


async def published_assessment(db: AsyncSession) -> Activity | None:
    """The initiation assessment in force, if one is published.

    One at a time, by taking the most recently created: replacing an assessment
    is publishing a new one, and the old one keeps every reading it produced.
    Nothing here rewrites what a previous assessment concluded.
    """
    return await db.scalar(
        select(Activity)
        .where(
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Activity.status == ACTIVITY_STATUS_PUBLISHED,
        )
        .order_by(Activity.created_at.desc())
        .limit(1)
    )


async def questions_of(
    db: AsyncSession, activity_id: uuid.UUID
) -> Sequence[AssessmentQuestion]:
    rows = await db.scalars(
        select(AssessmentQuestion)
        .where(AssessmentQuestion.activity_id == activity_id)
        .order_by(AssessmentQuestion.position, AssessmentQuestion.question_ref)
    )
    return rows.all()


async def give_to(db: AsyncSession, parent_id: uuid.UUID, child: Child) -> None:
    """Give the assessment to a child who has never been given it.

    Silent when there is nothing to give, when she already has it, or when she
    has already done it. Activating a profile must not fail because the platform
    has no assessment published — the activation is the parent's act and the
    assessment is ours.
    """
    assessment = await published_assessment(db)
    if assessment is None:
        return

    already = await db.scalar(
        select(Assignment.id).where(
            Assignment.child_id == child.id,
            Assignment.activity_id == assessment.id,
        )
    )
    if already is not None:
        return

    db.add(
        Assignment(
            child_id=child.id,
            assigned_by_parent_id=parent_id,
            activity_id=assessment.id,
            note="Un petit test pour savoir par où commencer. Il n’y a pas de note.",
        )
    )
    await db.flush()


async def is_done(db: AsyncSession, child_id: uuid.UUID) -> bool:
    """Whether this child has finished an initiation assessment."""
    done = await db.scalar(
        select(Assignment.id)
        .join(Activity, Activity.id == Assignment.activity_id)
        .where(
            Assignment.child_id == child_id,
            Activity.kind == ACTIVITY_KIND_ASSESSMENT,
            Assignment.status == ASSIGNMENT_STATUS_COMPLETED,
        )
        .limit(1)
    )
    return done is not None


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


async def grade(
    db: AsyncSession, attempt: Attempt, question_ref: str, chosen: int
) -> tuple[str, bool]:
    """Say what was answered and whether it was right, from the server's copy.

    Returns the text of the chosen answer and its correctness, so the response
    recorded afterwards holds something a parent can read rather than an index
    only this table can interpret.

    A question that does not belong to the assessment behind this attempt is
    refused: an answer has to be an answer to something.
    """
    assignment = await db.get(Assignment, attempt.assignment_id)
    if assignment is None:
        raise NotFoundException(message=QUESTION_UNKNOWN_MESSAGE)

    question = await db.scalar(
        select(AssessmentQuestion).where(
            AssessmentQuestion.activity_id == assignment.activity_id,
            AssessmentQuestion.question_ref == question_ref,
        )
    )
    if question is None:
        raise NotFoundException(message=QUESTION_UNKNOWN_MESSAGE)

    if chosen < 0 or chosen >= len(question.choices):
        raise ConflictException(message="Cette réponse n’est pas proposée")

    return question.choices[chosen], chosen == question.correct_index
