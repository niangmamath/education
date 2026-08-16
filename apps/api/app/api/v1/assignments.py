"""Giving activities, from the Parent side and from the Élève side.

Two spaces act on the same rows, and the dependency is what keeps them apart: a
parent route takes `CurrentParent`, a child route takes `CurrentChild`, and
neither accepts the other. A route that took either would be one forgotten check
away from letting a child hand herself work, or a parent finish it in her place.

Every rule lives in `app.assignments.service`; the routes are the shape of the
request and nothing else.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentChild, CurrentParent, DbSession, RedisClient
from app.assignments import service
from app.models.assignment import ASSIGNMENT_STATUSES
from app.content.tokens import CONTENT_TICKET_TTL_SECONDS, mint_ticket
from app.core.config import settings
from app.schemas.assignment import (
    ActivityContent,
    AssignmentCreateRequest,
    AssignmentPublic,
    ChildAssignmentPublic,
)


router = APIRouter()

StatusFilter = Annotated[
    str | None, Query(pattern="^(assigned|in_progress|completed|cancelled)$")
]


@router.post(
    "/assignments",
    response_model=AssignmentPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    payload: AssignmentCreateRequest, parent: CurrentParent, db: DbSession
) -> Any:
    """Give one published activity to one of this parent's children."""
    assignment = await service.assign_activity(
        db,
        parent,
        child_id=payload.child_id,
        activity_code=payload.activity_code,
        note=payload.note,
        due_on=payload.due_on,
    )
    await db.commit()
    return _parent_view(assignment)


@router.get("/assignments", response_model=list[AssignmentPublic])
async def list_assignments(
    parent: CurrentParent,
    db: DbSession,
    child_id: uuid.UUID | None = None,
    assignment_status: StatusFilter = None,
) -> list[AssignmentPublic]:
    """Everything given inside this family, newest first."""
    rows = await service.list_for_parent(
        db, parent, child_id=child_id, status=assignment_status
    )
    return [_parent_view(row) for row in rows]


@router.post("/assignments/{assignment_id}/cancel", response_model=AssignmentPublic)
async def cancel_assignment(
    assignment_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Any:
    """Call off an assignment that is still owed, without erasing it."""
    assignment = await service.cancel_assignment(db, parent, assignment_id)
    await db.commit()
    return _parent_view(assignment)


@router.get("/me/activities", response_model=list[ChildAssignmentPublic])
async def list_my_activities(
    child: CurrentChild, db: DbSession, assignment_status: StatusFilter = None
) -> list[ChildAssignmentPublic]:
    """What this child has been given: to do, under way, or finished."""
    rows = await service.list_for_child(db, child, status=assignment_status)
    return [_child_view(row) for row in rows]


@router.post(
    "/me/activities/{assignment_id}/start", response_model=ChildAssignmentPublic
)
async def start_my_activity(
    assignment_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """Take up an activity that was given."""
    assignment = await service.start_assignment(db, child, assignment_id)
    await db.commit()
    return _child_view(assignment)


@router.post(
    "/me/activities/{assignment_id}/complete", response_model=ChildAssignmentPublic
)
async def complete_my_activity(
    assignment_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """Reach the end of an activity.

    Finishing is not passing: nothing here touches a competency, and the
    evidence belongs to the attempts of step 10.
    """
    assignment = await service.complete_assignment(db, child, assignment_id)
    await db.commit()
    return _child_view(assignment)


@router.get("/me/activities/{assignment_id}/content", response_model=ActivityContent)
async def read_my_activity_content(
    assignment_id: uuid.UUID,
    child: CurrentChild,
    db: DbSession,
    client: RedisClient,
) -> ActivityContent:
    """Where to play an activity under way, and the ticket that opens it.

    The URL points at the content origin, which will check the ticket on every
    asset it serves. Access follows the assignment, so a child who has not
    started, or has finished, gets nothing at all.
    """
    assignment, package = await service.content_for(db, child, assignment_id)
    ticket = await mint_ticket(client, assignment.id, package.sha256)
    return ActivityContent(
        library_name=package.library_name,
        library_version=package.library_version,
        play_url=(
            f"{settings.CONTENT_ORIGIN_URL}/player/play.html"
            f"?c={package.sha256}&t={ticket}"
        ),
        expires_in=CONTENT_TICKET_TTL_SECONDS,
    )


@router.get("/assignments/statuses", response_model=list[str])
async def list_statuses(parent: CurrentParent) -> list[str]:
    """The statuses an assignment may have, so a client need not hard-code them."""
    return list(ASSIGNMENT_STATUSES)


def _parent_view(assignment: Any) -> AssignmentPublic:
    return AssignmentPublic(
        id=assignment.id,
        child_id=assignment.child_id,
        child_pseudonym=assignment.child.pseudonym,
        status=assignment.status,
        origin=assignment.origin,
        note=assignment.note,
        due_on=assignment.due_on,
        activity=assignment.activity,
        assigned_at=assignment.assigned_at,
        started_at=assignment.started_at,
        completed_at=assignment.completed_at,
        cancelled_at=assignment.cancelled_at,
    )


def _child_view(assignment: Any) -> ChildAssignmentPublic:
    return ChildAssignmentPublic(
        id=assignment.id,
        status=assignment.status,
        note=assignment.note,
        due_on=assignment.due_on,
        activity=assignment.activity,
        assigned_at=assignment.assigned_at,
        started_at=assignment.started_at,
        completed_at=assignment.completed_at,
    )
