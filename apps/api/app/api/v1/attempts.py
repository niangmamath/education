"""Doing an activity: starting, answering, finishing.

Every route that **acts on** an attempt — opening one, answering, finishing —
belongs to the Élève space and takes `CurrentChild`. A parent has nothing to do
there — not out of secrecy, but because an attempt is something a child does,
and a route that accepted either would be one forgotten check away from letting
a parent answer in her place.

`GET /attempts/rules` was always the exception: it touches no attempt and names
no child, so any authenticated session may read it.

`GET /children/{child_id}/attempts` is a second, narrower exception, added once
the dashboards of step 13 had shipped without it: a parent could see an
activity was `completed` on the assignment listing, but nothing said what it
showed. This route only **reads** — the same `list_for_child` the child's own
`GET /me/attempts` calls, given the child the parent owns instead of the one in
session — so the rule above still holds for every route that writes.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status
from sqlalchemy import select

from app.api.deps import CurrentChild, CurrentParent, CurrentSession, DbSession
from app.attempts import rules, service
from app.core.exceptions import NotFoundException
from app.models.attempt import Attempt, AttemptResult
from app.models.identity import Child
from app.schemas.attempt import (
    AttemptPublic,
    ResponsePublic,
    ResponseRequest,
    ResultPublic,
    RulePublic,
)

router = APIRouter()

CHILD_NOT_FOUND_MESSAGE = "Ce profil enfant n’existe pas"

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

    Nothing is assigned here. Finishing an activity is the moment the reading
    changes, and it would be the natural place to hand out a repair — but the
    platform does not assign for anyone: it proposes, and a parent gives.
    """
    attempt, _ = await service.complete(db, child, attempt_id)
    await db.commit()
    return _public(attempt)


@router.get("/attempts/rules", response_model=list[RulePublic])
async def list_rules(session: CurrentSession) -> list[RulePublic]:
    """The rules that read an attempt, stated so they can be shown.

    Published rather than made configurable: configuring them would mean
    deciding who may change what a mastered competency means, which is a
    decision and not a setting, and one with nobody to make it yet.

    Readable by **any authenticated session**, Parent as well as Élève. Rules
    published so that a parent can be shown them, behind a door only a child may
    open, would be published to nobody who needs them.
    """
    return [RulePublic(**rule) for rule in rules.published_rules()]


@router.get("/me/attempts", response_model=list[AttemptPublic])
async def list_attempts(
    child: CurrentChild, db: DbSession, assignment_id: AssignmentFilter = None
) -> list[AttemptPublic]:
    """This child's attempts, newest first, and nobody else's."""
    rows = await service.list_for_child(db, child, assignment_id=assignment_id)
    return [_public(row) for row in rows]


@router.get("/children/{child_id}/attempts", response_model=list[AttemptPublic])
async def list_attempts_for_parent(
    child_id: uuid.UUID,
    parent: CurrentParent,
    db: DbSession,
    assignment_id: AssignmentFilter = None,
) -> list[AttemptPublic]:
    """One child's attempts, read by the parent who owns her, nobody else's.

    A child of another family is refused as one that does not exist, the same
    posture the diagnostic route already takes.
    """
    owned = await db.scalar(
        select(Child).where(Child.id == child_id, Child.parent_id == parent.id)
    )
    if owned is None:
        raise NotFoundException(message=CHILD_NOT_FOUND_MESSAGE)

    rows = await service.list_for_child(db, owned, assignment_id=assignment_id)
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
