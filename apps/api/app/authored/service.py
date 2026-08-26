"""Reading and grading the activities this platform wrote itself.

Two kinds are authored here — the initiation assessment and the remediation
sheets — and they ask a question the same way: a prompt, a list of choices, and
a correct index the client is never shown. What separates them is policy, which
lives elsewhere: the assessment is given once at activation and says nothing back,
a sheet is proposed by a parent and explains itself as it goes.

Everything in this module is therefore about the **question**, never about which
kind asked it. That is deliberate. The moment grading has to know what sort of
activity it is grading, the two kinds start drifting apart, and the reading engine
downstream — which must go on seeing one shape — inherits the difference.

The correct answer never leaves the server. A client sends a position in the list
of choices; it never sends whether it was right, and it would not be believed if
it did.
"""

from __future__ import annotations

import random
import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import ASSIGNMENT_OPEN_STATUSES, Assignment
from app.models.catalog import (
    AUTHORED_KINDS,
    Activity,
    ActivityQuestion,
    AuthoredQuestion,
)
from app.models.identity import Child

QUESTION_UNKNOWN_MESSAGE = "Cette question n’appartient pas à cette activité"
ANSWER_UNKNOWN_MESSAGE = "Cette réponse n’est pas proposée"
AUTHORED_ACTIVITY_UNKNOWN_MESSAGE = "Cette activité n’est pas la tienne"


async def questions_of(
    db: AsyncSession,
    activity_id: uuid.UUID,
    *,
    draw: int | None = None,
    seed: str | None = None,
    competency_codes: Sequence[str] | None = None,
) -> Sequence[AuthoredQuestion]:
    """Every question of an authored activity, or a stable subset of them.

    Left at its default, `draw` returns the whole bank in a fixed order — the
    assessment's own use, unchanged since ADR-019 tripled its bank per
    competency without this parameter needing to exist. A sheet asks for a
    subset instead (HORS-10): fewer questions served than the bank holds, so a
    child who repeats a sheet is not shown the same four in the same order
    every time. `seed` is what makes one draw reproducible — the caller passes
    the running attempt's id, so every read during that attempt draws the same
    subset, and a new attempt draws again. Which policy applies is not this
    module's decision; it stays with whoever calls it, exactly as the module
    docstring says of everything else that separates a sheet from the
    assessment.

    `competency_codes`, left at its default, leaves the bank untouched — every
    caller but one. The assessment (étape 14) passes the codes of the palier
    due right now, through the same attribution `catalog_activity_questions`
    already carries per question (ADR-019). A sitting therefore serves only
    the questions of the competencies actually due, out of the one bank
    authored for the whole class.
    """
    query = select(AuthoredQuestion).where(AuthoredQuestion.activity_id == activity_id)
    if competency_codes is not None:
        query = (
            query.join(
                ActivityQuestion,
                (ActivityQuestion.activity_id == AuthoredQuestion.activity_id)
                & (ActivityQuestion.question_ref == AuthoredQuestion.question_ref),
            )
            .where(ActivityQuestion.competency_code.in_(competency_codes))
            .distinct()
        )
    rows = await db.scalars(
        query.order_by(AuthoredQuestion.position, AuthoredQuestion.question_ref)
    )
    bank = rows.all()
    if draw is None or draw >= len(bank):
        return bank
    return random.Random(seed).sample(bank, draw)


async def open_authored_activity_for(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> tuple[Assignment, Activity] | None:
    """The authored activity behind an assignment, if it is this child's and open.

    Shared by both routes this platform writes questions for — the sheet's and,
    since étape 15, the course's — because the check is the same either way:
    does this assignment belong to this child, is it open, and does it point at
    something written here at all. Which of the authored kinds it actually is
    stays for the caller to check against its own.

    Returns nothing rather than raising when the assignment belongs to someone
    else, does not exist, or points at an activity the platform did not write.
    All three are the same answer to the caller — there is nothing to read here
    — and telling them apart in a response would say whether somebody else's
    assignment exists.
    """
    assignment = await db.scalar(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.child_id == child.id,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
    )
    if assignment is None:
        return None

    activity = await db.get(Activity, assignment.activity_id)
    if activity is None or activity.kind not in AUTHORED_KINDS:
        return None

    return assignment, activity


async def grade(
    db: AsyncSession, assignment_id: uuid.UUID, question_ref: str, chosen: int
) -> tuple[str, bool, str | None]:
    """Say what was answered, whether it was right, and what to tell her.

    Returns the text of the chosen answer, its correctness, and the question's
    explanation if it has one — so a sheet's caller can record something a
    parent can read rather than an index only this table can interpret, and
    the child gets the sentence that turns a repair into teaching.

    The explanation is the question's own and is the same whatever was answered:
    a sheet explains what is true, it does not comment on the child.

    Takes the assignment directly rather than an attempt: a sheet's answer is
    recorded against one (its attempt exists to produce the reading that
    closes the repair), but a course's on-the-fly check (étape 15) is
    deliberately not — nothing here needs to know which of the two is
    calling, or whether an attempt exists at all.

    A question that does not belong to the activity behind this assignment is
    refused. An answer has to be an answer to something.
    """
    assignment = await db.get(Assignment, assignment_id)
    if assignment is None:
        raise NotFoundException(message=QUESTION_UNKNOWN_MESSAGE)

    question = await db.scalar(
        select(AuthoredQuestion).where(
            AuthoredQuestion.activity_id == assignment.activity_id,
            AuthoredQuestion.question_ref == question_ref,
        )
    )
    if question is None:
        raise NotFoundException(message=QUESTION_UNKNOWN_MESSAGE)

    if chosen < 0 or chosen >= len(question.choices):
        raise ConflictException(message=ANSWER_UNKNOWN_MESSAGE)

    return (
        question.choices[chosen],
        chosen == question.correct_index,
        question.explanation,
    )
