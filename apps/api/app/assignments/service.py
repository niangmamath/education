"""Giving an activity, taking it up, finishing it, calling it off.

Every rule of the step lives here rather than in the routes, because the Parent
space and the Élève space act on the same rows from opposite sides and must not
drift apart.

Two rules are worth naming.

**Isolation is carried by the query, not by a check afterwards.** A parent asks
for one of *their* children, and an assignment of another family answers exactly
like one that does not exist. Nothing here can be used to find out whether a row
belongs to somebody else.

**Nothing goes backwards.** An assignment is given, taken up, finished — or
called off. A finished assignment does not reopen and a cancelled one does not
resume; giving the activity again is a new row. The project rule that an
observation must never overwrite the history begins to cost something here, and
this is where it is paid.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.attempts.service import abandon_running_attempt
from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import (
    ASSIGNMENT_OPEN_STATUSES,
    MAX_OPEN_ASSIGNMENTS,
    ASSIGNMENT_STATUS_ASSIGNED,
    ASSIGNMENT_STATUS_CANCELLED,
    ASSIGNMENT_STATUS_COMPLETED,
    ASSIGNMENT_STATUS_IN_PROGRESS,
    Assignment,
)
from app.models.catalog import ACTIVITY_STATUS_PUBLISHED, Activity, H5PPackage
from app.models.identity import CHILD_STATUS_ACTIVE, Child, Parent

# One message for "not yours" and for "does not exist", so the two cannot be
# told apart from outside.
ASSIGNMENT_NOT_FOUND_MESSAGE = "Cette affectation n’existe pas"
CHILD_NOT_FOUND_MESSAGE = "Ce profil n’existe pas"
ACTIVITY_NOT_FOUND_MESSAGE = "Cette activité n’existe pas ou n’est pas publiée"

ALREADY_ASSIGNED_MESSAGE = "Cette activité est déjà proposée à cet enfant"
TOO_MANY_OPEN_MESSAGE = (
    f"Cet enfant a déjà {MAX_OPEN_ASSIGNMENTS} activités en attente ; "
    "attendez qu'il en termine avant d'en proposer d'autres"
)
DUE_DATE_IN_THE_PAST_MESSAGE = "Une échéance ne peut pas être déjà passée"
CONTENT_NOT_OPEN_MESSAGE = (
    "Commencez l’activité pour ouvrir son contenu ; une activité terminée ou "
    "annulée n’en donne plus"
)
NO_CONTENT_MESSAGE = "Cette activité n’a pas de contenu H5P à jouer"
ALREADY_CLOSED_MESSAGE = "Cette affectation est terminée ou annulée"
NOT_YET_STARTED_MESSAGE = "Cette activité n’a pas été commencée"
ALREADY_STARTED_MESSAGE = "Cette activité est déjà commencée"

_LOADED = (
    selectinload(Assignment.activity),
    selectinload(Assignment.child),
)


def _in_course_order() -> tuple[Any, ...]:
    """The order a child is meant to work through, and a parent to read.

    What is expected soonest comes first; what is expected on no particular day
    comes after all of it, oldest first. This is the whole of the "parcours":
    the order is a consequence of the dates a parent sets, not a list to be
    dragged around. Reordering by hand would need a rank to maintain, and a rank
    that nobody updates is worse than no rank at all.
    """
    return (
        Assignment.due_on.asc().nulls_last(),
        Assignment.assigned_at.asc(),
        Assignment.id,
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def assign_activity(
    db: AsyncSession,
    parent: Parent,
    child_id: uuid.UUID,
    activity_code: str,
    note: str | None = None,
    due_on: date | None = None,
) -> Assignment:
    """Give one published activity to one of this parent's children."""
    if due_on is not None and due_on < date.today():
        # Refused rather than accepted and shown as already late: nobody means
        # to give a child something that was due yesterday.
        raise ConflictException(message=DUE_DATE_IN_THE_PAST_MESSAGE)

    child = await _own_child(db, parent, child_id)

    activity = await db.scalar(
        select(Activity).where(
            Activity.code == activity_code,
            Activity.status == ACTIVITY_STATUS_PUBLISHED,
        )
    )
    if activity is None:
        # A draft is refused exactly like an activity that does not exist: what
        # is being prepared is not a parent's business either.
        raise NotFoundException(message=ACTIVITY_NOT_FOUND_MESSAGE)

    open_already = await db.scalar(
        select(Assignment).where(
            Assignment.child_id == child.id,
            Assignment.activity_id == activity.id,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
    )
    if open_already is not None:
        # The partial unique index would refuse this too; asking first is what
        # turns a database error into an answer the parent can act on.
        raise ConflictException(message=ALREADY_ASSIGNED_MESSAGE)

    owed = await db.scalar(
        select(func.count())
        .select_from(Assignment)
        .where(
            Assignment.child_id == child.id,
            Assignment.status.in_(ASSIGNMENT_OPEN_STATUSES),
        )
    )
    if (owed or 0) >= MAX_OPEN_ASSIGNMENTS:
        # The ceiling counts only what is still owed, so finishing frees a slot.
        raise ConflictException(message=TOO_MANY_OPEN_MESSAGE)

    assignment = Assignment(
        child_id=child.id,
        assigned_by_parent_id=parent.id,
        activity_id=activity.id,
        note=note,
        due_on=due_on,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment, ["activity", "child"])
    return assignment


async def cancel_assignment(
    db: AsyncSession, parent: Parent, assignment_id: uuid.UUID
) -> Assignment:
    """Call off an assignment that is still owed.

    Cancelling is not deleting. The row stays, dated, because a child who was
    given something and then had it withdrawn is a different history from a
    child who was never given it.
    """
    assignment = await _own_assignment(db, parent, assignment_id)
    if assignment.status not in ASSIGNMENT_OPEN_STATUSES:
        raise ConflictException(message=ALREADY_CLOSED_MESSAGE)

    assignment.status = ASSIGNMENT_STATUS_CANCELLED
    assignment.cancelled_at = _now()
    # Whatever she had under way stops with it, without being erased: she did
    # start, and that stays true.
    await abandon_running_attempt(db, assignment.id)
    await db.flush()
    return assignment


async def start_assignment(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> Assignment:
    """The child takes up an activity they were given."""
    assignment = await _child_assignment(db, child, assignment_id)
    if assignment.status == ASSIGNMENT_STATUS_IN_PROGRESS:
        raise ConflictException(message=ALREADY_STARTED_MESSAGE)
    if assignment.status != ASSIGNMENT_STATUS_ASSIGNED:
        raise ConflictException(message=ALREADY_CLOSED_MESSAGE)

    assignment.status = ASSIGNMENT_STATUS_IN_PROGRESS
    assignment.started_at = _now()
    await db.flush()
    return assignment


async def complete_assignment(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> Assignment:
    """The child reaches the end of the activity.

    Finishing an activity is not passing a competency. Nothing here touches a
    competency, and a project rule says that opening a content never validates
    one on its own: the evidence belongs to the attempts of step 10.
    """
    assignment = await _child_assignment(db, child, assignment_id)
    if assignment.status != ASSIGNMENT_STATUS_IN_PROGRESS:
        raise ConflictException(
            message=(
                ALREADY_CLOSED_MESSAGE
                if assignment.status
                in (ASSIGNMENT_STATUS_COMPLETED, ASSIGNMENT_STATUS_CANCELLED)
                else NOT_YET_STARTED_MESSAGE
            )
        )

    assignment.status = ASSIGNMENT_STATUS_COMPLETED
    assignment.completed_at = _now()
    await db.flush()
    return assignment


async def list_for_parent(
    db: AsyncSession,
    parent: Parent,
    child_id: uuid.UUID | None = None,
    status: str | None = None,
) -> Sequence[Assignment]:
    """Every assignment of this parent's family, in the order it is expected."""
    statement = (
        select(Assignment)
        .join(Child, Child.id == Assignment.child_id)
        .where(Child.parent_id == parent.id)
        .order_by(*_in_course_order())
        .options(*_LOADED)
    )
    if child_id is not None:
        statement = statement.where(Assignment.child_id == child_id)
    if status is not None:
        statement = statement.where(Assignment.status == status)

    rows = await db.scalars(statement)
    return rows.all()


async def list_for_child(
    db: AsyncSession, child: Child, status: str | None = None
) -> Sequence[Assignment]:
    """What this child has been given, and nothing anyone else was given."""
    statement = (
        select(Assignment)
        .where(Assignment.child_id == child.id)
        .order_by(*_in_course_order())
        .options(*_LOADED)
    )
    if status is not None:
        statement = statement.where(Assignment.status == status)

    rows = await db.scalars(statement)
    return rows.all()


async def _own_child(db: AsyncSession, parent: Parent, child_id: uuid.UUID) -> Child:
    """One active child of this family, or a refusal that says nothing more."""
    child = await db.scalar(
        select(Child).where(
            Child.id == child_id,
            Child.parent_id == parent.id,
            Child.status == CHILD_STATUS_ACTIVE,
        )
    )
    if child is None:
        raise NotFoundException(message=CHILD_NOT_FOUND_MESSAGE)
    return child


async def _own_assignment(
    db: AsyncSession, parent: Parent, assignment_id: uuid.UUID
) -> Assignment:
    assignment = await db.scalar(
        select(Assignment)
        .join(Child, Child.id == Assignment.child_id)
        .where(Assignment.id == assignment_id, Child.parent_id == parent.id)
        .options(*_LOADED)
    )
    if assignment is None:
        raise NotFoundException(message=ASSIGNMENT_NOT_FOUND_MESSAGE)
    return assignment


async def _child_assignment(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> Assignment:
    assignment = await db.scalar(
        select(Assignment)
        .where(Assignment.id == assignment_id, Assignment.child_id == child.id)
        .options(*_LOADED)
    )
    if assignment is None:
        raise NotFoundException(message=ASSIGNMENT_NOT_FOUND_MESSAGE)
    return assignment


async def content_for(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> tuple[Assignment, H5PPackage]:
    """The package this child may open right now, and the reasons she may not.

    Access to a content is not a property of the content: it is a property of
    the assignment. The package is handed over only to the child it was given
    to, and only while she is actually doing it — a link obtained before
    starting, or kept after finishing, opens nothing.
    """
    assignment = await _child_assignment(db, child, assignment_id)
    if assignment.status != ASSIGNMENT_STATUS_IN_PROGRESS:
        raise ConflictException(message=CONTENT_NOT_OPEN_MESSAGE)

    activity = await db.scalar(
        select(Activity)
        .where(Activity.id == assignment.activity_id)
        .options(selectinload(Activity.h5p_package))
    )
    if activity is None or activity.h5p_package is None:
        # A PhET simulation or a video has no package to hand over; that is not
        # a failure, it is another kind of activity.
        raise ConflictException(message=NO_CONTENT_MESSAGE)

    return assignment, activity.h5p_package
