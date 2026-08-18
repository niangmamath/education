"""The initiation assessment, as a child meets it.

Two routes and no more: read the questions, answer one. Starting the attempt and
finishing it go through the attempt routes that already exist — an assessment is
an activity, and the platform must not grow a second way of doing an activity
just because this one was written here.

Nothing on this side of the wire carries a correct answer.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentChild, DbSession
from app.assessment import service
from app.attempts import service as attempts
from app.authored import service as authored
from app.core.exceptions import NotFoundException
from app.schemas.assessment import (
    AssessmentAnswerRequest,
    AssessmentPublic,
    AuthoredQuestionPublic,
)
from app.schemas.attempt import ResponsePublic

router = APIRouter()


@router.get("/me/assessment", response_model=AssessmentPublic)
async def read_my_assessment(child: CurrentChild, db: DbSession) -> Any:
    """The assessment waiting for this child, with its questions.

    `done` says she has already been through the one for her class, which is what
    a client needs to know whether to invite her in or leave her alone. There is
    no way here to ask for a second one: an assessment opens a class, it is not a
    habit — the next one comes when she is promoted, and it is a different paper.
    """
    done = await service.is_done(db, child)
    pending = await service.pending_for(db, child.id)

    if pending is None:
        return AssessmentPublic(done=done, assignment_id=None, title=None, questions=[])

    assessment = await service.assessment_for(db, child.level_code)
    if assessment is None:
        raise NotFoundException(message=service.NO_ASSESSMENT_MESSAGE)

    questions = await authored.questions_of(db, assessment.id)
    return AssessmentPublic(
        done=done,
        assignment_id=pending.id,
        title=assessment.title,
        questions=[
            AuthoredQuestionPublic(
                question_ref=row.question_ref,
                prompt=row.prompt,
                # The correct index is not in this model, and cannot be added to
                # it by accident: it is not a field that exists.
                choices=list(row.choices),
            )
            for row in questions
        ],
    )


@router.post(
    "/me/assessment/attempts/{attempt_id}/answers",
    response_model=ResponsePublic,
    status_code=status.HTTP_201_CREATED,
)
async def answer_question(
    attempt_id: str,
    payload: AssessmentAnswerRequest,
    child: CurrentChild,
    db: DbSession,
) -> Any:
    """Answer one question, and let the server say whether it was right.

    The client sends a position in the list of choices. It never sends whether
    it was correct, and it could not be believed if it did — which is the whole
    reason the assessment is graded on this side.
    """
    import uuid as _uuid

    attempt = await attempts.own_attempt(db, child, _uuid.UUID(attempt_id))
    # The explanation is deliberately dropped: an assessment does not teach as
    # it measures, and a route that returned one would make the exam walkable.
    answer, correct, _ = await authored.grade(
        db, attempt, payload.question_ref, payload.chosen_index
    )
    recorded = await attempts.record_response(
        db,
        child,
        attempt.id,
        question_ref=payload.question_ref,
        response=answer,
        is_correct=correct,
    )
    await db.commit()
    return recorded
