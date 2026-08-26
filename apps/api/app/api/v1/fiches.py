"""Remediation sheets, as a child meets them.

Two routes: read the sheet, answer one of its questions. Opening the attempt and
finishing it go through the attempt routes that already exist — a sheet is an
activity, and the platform must not grow a second way of doing an activity just
because this one was written here.

**Why a sheet answers back and the assessment does not.** Both are graded by the
same code, but this route returns the explanation and the assessment's does not.
A repair that says nothing is a second test, and a child who has just been told
she has a difficulty has no reason to sit one. An assessment that says something
stops measuring: it could be walked through one question at a time.

That asymmetry is why this route refuses an attempt that is not a sheet's. Without
the check, an assessment attempt posted here would be graded and answered — the
exam, made walkable, through the door left open by the repair.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentChild, DbSession
from app.attempts import service as attempts
from app.authored import service
from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import Assignment
from app.models.catalog import ACTIVITY_KIND_REMEDIATION, Activity
from app.schemas.authored import (
    AnswerFeedback,
    AuthoredAnswerRequest,
    AuthoredQuestionPublic,
    FichePublic,
)

router = APIRouter()

NOT_A_SHEET_MESSAGE = "Cette activité ne se fait pas ici"

# HORS-10 : quatre questions servies par lecture, tirées d'une réserve d'environ
# huit, pour qu'une fiche reprise ne montre plus systématiquement les mêmes
# quatre dans le même ordre. L'examen n'est pas concerné — ADR-020.
FICHE_QUESTIONS_SERVED = 4


@router.get("/me/activities/{assignment_id}/fiche", response_model=FichePublic)
async def read_my_fiche(
    assignment_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """The sheet behind one of this child's open assignments.

    Nothing here carries a correct answer, and nothing here carries an
    explanation either: an explanation given before the question is asked is the
    answer, written out.
    """
    found = await service.open_authored_activity_for(db, child, assignment_id)
    if found is None:
        raise NotFoundException(message=service.AUTHORED_ACTIVITY_UNKNOWN_MESSAGE)

    assignment, activity = found
    if activity.kind != ACTIVITY_KIND_REMEDIATION:
        raise NotFoundException(message=NOT_A_SHEET_MESSAGE)

    running = await attempts.running_attempt(db, assignment.id)
    questions = await service.questions_of(
        db,
        activity.id,
        draw=FICHE_QUESTIONS_SERVED,
        seed=str(running.id) if running is not None else None,
    )
    return FichePublic(
        assignment_id=assignment.id,
        activity_code=activity.code,
        title=activity.title,
        guidance=activity.guidance,
        duration_minutes=activity.duration_minutes,
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
    "/me/fiches/attempts/{attempt_id}/answers",
    response_model=AnswerFeedback,
    status_code=status.HTTP_201_CREATED,
)
async def answer_sheet_question(
    attempt_id: uuid.UUID,
    payload: AuthoredAnswerRequest,
    child: CurrentChild,
    db: DbSession,
) -> Any:
    """Answer one question of a sheet, and be told what is true.

    The answer is recorded exactly as any other response is, so the reading
    engine sees one shape and never learns that this activity was written here.
    """
    attempt = await attempts.own_attempt(db, child, attempt_id)

    assignment = await db.get(Assignment, attempt.assignment_id)
    activity = (
        await db.get(Activity, assignment.activity_id)
        if assignment is not None
        else None
    )
    if activity is None or activity.kind != ACTIVITY_KIND_REMEDIATION:
        raise ConflictException(message=NOT_A_SHEET_MESSAGE)

    answer, correct, explanation = await service.grade(
        db, attempt.assignment_id, payload.question_ref, payload.chosen_index
    )
    await attempts.record_response(
        db,
        child,
        attempt.id,
        question_ref=payload.question_ref,
        response=answer,
        is_correct=correct,
    )
    await db.commit()

    return AnswerFeedback(
        question_ref=payload.question_ref, correct=correct, explanation=explanation
    )
