"""A course, as a child meets it (étape 15).

Two routes, on the model of `fiches.py`: read the lesson and its questions,
answer one of them. The difference from a sheet is what does **not** happen
here — there is no attempt behind a course, and answering one of its
questions is graded and explained on the spot without ever being recorded.
A course teaches before the palier it precedes is tested; the reading that
decides mastery stays entirely the assessment's, exactly as before étape 15.

That is also why this route refuses an assignment that is not a course's,
the same way `fiches.py` refuses one that is not a sheet's: both share the
same grading engine, and without the check an assessment's or a sheet's
assignment could be answered here just as walkably.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentChild, DbSession
from app.authored import service
from app.core.exceptions import ConflictException, NotFoundException
from app.models.catalog import ACTIVITY_KIND_COURSE
from app.schemas.authored import (
    AnswerFeedback,
    AuthoredAnswerRequest,
    AuthoredQuestionPublic,
    CoursePublic,
)

router = APIRouter()

NOT_A_COURSE_MESSAGE = "Cette activité ne se fait pas ici"


@router.get("/me/activities/{assignment_id}/cours", response_model=CoursePublic)
async def read_my_course(
    assignment_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """The course behind one of this child's open assignments.

    Every question of its bank is served, unlike a sheet: a course is not
    repeated the way a Quick Repair may be, so there is no reserve to draw a
    subset from (HORS-10 stays a sheet-only concern).
    """
    found = await service.open_authored_activity_for(db, child, assignment_id)
    if found is None:
        raise NotFoundException(message=service.AUTHORED_ACTIVITY_UNKNOWN_MESSAGE)

    assignment, activity = found
    if activity.kind != ACTIVITY_KIND_COURSE:
        raise NotFoundException(message=NOT_A_COURSE_MESSAGE)

    questions = await service.questions_of(db, activity.id)
    return CoursePublic(
        assignment_id=assignment.id,
        activity_code=activity.code,
        title=activity.title,
        guidance=activity.guidance,
        duration_minutes=activity.duration_minutes,
        questions=[
            AuthoredQuestionPublic(
                question_ref=row.question_ref,
                prompt=row.prompt,
                choices=list(row.choices),
            )
            for row in questions
        ],
    )


@router.post(
    "/me/cours/{assignment_id}/answers",
    response_model=AnswerFeedback,
    status_code=status.HTTP_201_CREATED,
)
async def answer_course_question(
    assignment_id: uuid.UUID,
    payload: AuthoredAnswerRequest,
    child: CurrentChild,
    db: DbSession,
) -> Any:
    """Answer one question of a course, and be told what is true.

    Nothing is written here — no attempt, no response, no competency
    reading. That is deliberate rather than an omission: a course checks
    understanding on the fly, and the platform's rule that opening a content
    never validates a competency on its own would be contradicted the moment
    this route touched `attempts`.
    """
    found = await service.open_authored_activity_for(db, child, assignment_id)
    if found is None or found[1].kind != ACTIVITY_KIND_COURSE:
        raise ConflictException(message=NOT_A_COURSE_MESSAGE)

    _, correct, explanation = await service.grade(
        db, assignment_id, payload.question_ref, payload.chosen_index
    )

    return AnswerFeedback(
        question_ref=payload.question_ref, correct=correct, explanation=explanation
    )
