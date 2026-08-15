"""Doing an activity: starting, answering, finishing.

Every route belongs to the Élève space and takes `CurrentChild`. A parent has
nothing to do here — not out of secrecy, but because an attempt is something a
child does, and a route that accepted either would be one forgotten check away
from letting a parent answer in her place.

The Parent side reads the results through the assignment listing of step 09 and,
later, through the dashboards of step 13.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentChild, DbSession
from app.attempts import rules, service
from app.models.attempt import Attempt, AttemptResult
from app.schemas.attempt import (
    AttemptPublic,
    ResponsePublic,
    ResponseRequest,
    ResultPublic,
)

router = APIRouter()

AssignmentFilter = Annotated[uuid.UUID | None, Query()]


@router.post("/me/activities/{assignment_id}/attempts", response_model=AttemptPublic)
async def start_attempt(
    assignment_id: uuid.UUID,
    child: CurrentChild,
    db: DbSession,
    response: Response,
) -> Any:
    """Start an attempt, or return the one already under way.

    Answers `201` when it created one and `200` when it handed back an existing
    one, so a client can tell without either being an error. A reload must not
    leave two attempts behind.
    """
    attempt, created = await service.start_or_resume(db, child, assignment_id)
    await db.commit()
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return _public(attempt)


@router.post(
    "/me/attempts/{attempt_id}/responses",
    response_model=ResponsePublic,
    status_code=status.HTTP_201_CREATED,
)
async def add_response(
    attempt_id: uuid.UUID,
    payload: ResponseRequest,
    child: CurrentChild,
    db: DbSession,
) -> Any:
    """Append one answer to the attempt under way."""
    recorded = await service.record_response(
        db,
        child,
        attempt_id,
        question_ref=payload.question_ref,
        response=payload.response,
        is_correct=payload.is_correct,
    )
    await db.commit()
    return recorded


@router.post("/me/attempts/{attempt_id}/complete", response_model=AttemptPublic)
async def complete_attempt(
    attempt_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """Finish the attempt and read what it holds.

    Completing twice returns the same results rather than computing them again.
    """
    attempt, _ = await service.complete(db, child, attempt_id)
    await db.commit()
    return _public(attempt)


@router.get("/me/attempts", response_model=list[AttemptPublic])
async def list_attempts(
    child: CurrentChild, db: DbSession, assignment_id: AssignmentFilter = None
) -> list[AttemptPublic]:
    """This child's attempts, newest first, and nobody else's."""
    rows = await service.list_for_child(db, child, assignment_id=assignment_id)
    return [_public(row) for row in rows]


def _public(attempt: Attempt) -> AttemptPublic:
    return AttemptPublic(
        id=attempt.id,
        assignment_id=attempt.assignment_id,
        status=attempt.status,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        responses=[ResponsePublic.model_validate(row) for row in attempt.responses],
        results=[_result(row) for row in attempt.results],
    )


def _result(result: AttemptResult) -> ResultPublic:
    """The stored conclusion, with the sentence that explains it.

    The explanation is built from the same values that were stored, so it cannot
    drift from what it explains.
    """
    reading = rules.Reading(
        outcome=result.outcome,
        answered=result.answered,
        correct=result.correct,
        rule_code=result.rule_code,
    )
    return ResultPublic(
        competency_code=result.competency_code,
        outcome=result.outcome,
        answered=result.answered,
        correct=result.correct,
        rule_code=result.rule_code,
        explanation=rules.explain(reading),
    )
