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

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import ASSIGNMENT_OPEN_STATUSES, Assignment
from app.models.attempt import Attempt
from app.models.catalog import AUTHORED_KINDS, Activity, AuthoredQuestion
from app.models.identity import Child

QUESTION_UNKNOWN_MESSAGE = "Cette question n’appartient pas à cette activité"
ANSWER_UNKNOWN_MESSAGE = "Cette réponse n’est pas proposée"
SHEET_UNKNOWN_MESSAGE = "Cette activité n’est pas la tienne"


async def questions_of(
    db: AsyncSession, activity_id: uuid.UUID
) -> Sequence[AuthoredQuestion]:
    """Every question of an authored activity, in the order it is asked."""
    rows = await db.scalars(
        select(AuthoredQuestion)
        .where(AuthoredQuestion.activity_id == activity_id)
        .order_by(AuthoredQuestion.position, AuthoredQuestion.question_ref)
    )
    return rows.all()


async def open_sheet_for(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> tuple[Assignment, Activity] | None:
    """The authored activity behind an assignment, if it is this child's and open.

    Returns nothing rather than raising when the assignment belongs to someone
    else, does not exist, or points at an activity the platform did not write.
    All three are the same answer to the caller — there is no sheet here — and
    telling them apart in a response would say whether somebody else's assignment
    exists.
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
    db: AsyncSession, attempt: Attempt, question_ref: str, chosen: int
) -> tuple[str, bool, str | None]:
    """Say what was answered, whether it was right, and what to tell her.

    Returns the text of the chosen answer, its correctness, and the question's
    explanation if it has one — so the response recorded afterwards holds
    something a parent can read rather than an index only this table can
    interpret, and the child gets the sentence that turns a repair into teaching.

    The explanation is the question's own and is the same whatever was answered:
    a sheet explains what is true, it does not comment on the child.

    A question that does not belong to the activity behind this attempt is
    refused. An answer has to be an answer to something.
    """
    assignment = await db.get(Assignment, attempt.assignment_id)
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
