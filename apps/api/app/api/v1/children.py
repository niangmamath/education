"""Child profile creation and child access endpoints.

A child is always attached to one parent, and it is the parent's family code
that carries that attachment wherever no parent session exists. The pseudonym is
unique inside a family only, so it never designates a child on its own: every
child route starts from a family, either the one behind the caller's session or
the one behind the code they typed.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.cookies import set_session_cookie
from app.api.deps import CurrentChild, CurrentParent, DbSession, RedisClient
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    NotFoundException,
    RateLimitException,
)
from app.core.lockout import clear_failures, is_locked, register_failure
from app.core.security import (
    hash_pin,
    needs_rehash,
    spend_dummy_verification,
    verify_pin,
)
from app.core.sessions import CHILD_USER_TYPE, create_session
from app.models import Parent
from app.models.identity import (
    CHILD_STATUS_ACTIVE,
    CHILD_STATUS_DISABLED,
    CHILD_STATUS_PENDING,
    Child,
)
from app.schemas.auth import (
    ChildCreateRequest,
    ChildLoginRequest,
    ChildPublic,
    ChildSelfRegisterRequest,
)

router = APIRouter()

# One message for every failed child login, for the same reason as the parent
# one: a different answer per cause would tell an attacker which pseudonyms
# exist behind a family code.
INVALID_CREDENTIALS_MESSAGE = "Identifiants invalides"
LOCKED_MESSAGE = "Trop de tentatives, réessayez dans quelques minutes"
PSEUDONYM_TAKEN_MESSAGE = "Ce pseudonyme est déjà utilisé dans cette famille"
UNKNOWN_FAMILY_CODE_MESSAGE = "Code famille inconnu"
PENDING_MESSAGE = "Profil en attente d'activation par le parent"


async def _find_child(
    db: DbSession, parent_id: uuid.UUID, pseudonym: str
) -> Child | None:
    """Return the child holding this pseudonym inside this family, if any."""
    return await db.scalar(
        select(Child).where(Child.parent_id == parent_id, Child.pseudonym == pseudonym)
    )


async def _add_child(
    db: DbSession,
    parent_id: uuid.UUID,
    payload: ChildCreateRequest,
    child_status: str,
) -> Child:
    """Attach a child profile to a family, in the state its creator earns it."""
    existing = await _find_child(db, parent_id, payload.pseudonym)
    if existing is not None:
        raise ConflictException(message=PSEUDONYM_TAKEN_MESSAGE)

    child = Child(
        parent_id=parent_id,
        pseudonym=payload.pseudonym,
        pin_hash=hash_pin(payload.pin.get_secret_value()),
        display_name=payload.display_name,
        date_of_birth=payload.date_of_birth,
        status=child_status,
    )
    db.add(child)

    try:
        await db.commit()
    except IntegrityError as exc:
        # Two creations claiming the same pseudonym in the same family at once
        # both pass the check above; the unique constraint settles the race.
        await db.rollback()
        raise ConflictException(message=PSEUDONYM_TAKEN_MESSAGE) from exc

    await db.refresh(child)
    return child


@router.post(
    "/children",
    response_model=ChildPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_child(
    payload: ChildCreateRequest, parent: CurrentParent, db: DbSession
) -> Child:
    """Open a child profile from the parent's own space, usable straight away."""
    return await _add_child(db, parent.id, payload, CHILD_STATUS_ACTIVE)


@router.post(
    "/child/register",
    response_model=ChildPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register_child(payload: ChildSelfRegisterRequest, db: DbSession) -> Child:
    """Open a child profile from the family code, pending the parent's approval.

    No session is created and the profile cannot log in yet: a family code alone
    must never be enough to join a family, only to ask to.
    """
    parent_id = await db.scalar(
        select(Parent.id).where(Parent.family_code == payload.family_code)
    )
    if parent_id is None:
        raise NotFoundException(message=UNKNOWN_FAMILY_CODE_MESSAGE)

    return await _add_child(db, parent_id, payload, CHILD_STATUS_PENDING)


@router.get("/children", response_model=list[ChildPublic])
async def list_children(parent: CurrentParent, db: DbSession) -> Sequence[Child]:
    """List the children of the authenticated parent, pending ones included."""
    result = await db.scalars(
        select(Child)
        .where(Child.parent_id == parent.id)
        .order_by(Child.created_at, Child.id)
    )
    return result.all()


@router.post("/children/{child_id}/activate", response_model=ChildPublic)
async def activate_child(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Child:
    """Let a parent activate a profile a child opened with the family code."""
    child = await db.scalar(
        select(Child).where(Child.id == child_id, Child.parent_id == parent.id)
    )
    if child is None:
        # A profile in another family answers exactly like one that does not
        # exist, so the route cannot be used to probe other families.
        raise NotFoundException(message="Profil introuvable")

    if child.status == CHILD_STATUS_DISABLED:
        raise ConflictException(message="Profil désactivé, activation impossible")

    if child.status != CHILD_STATUS_ACTIVE:
        child.status = CHILD_STATUS_ACTIVE
        await db.commit()
        await db.refresh(child)

    return child


@router.post("/child/login", response_model=ChildPublic)
async def login_child(
    payload: ChildLoginRequest,
    response: Response,
    db: DbSession,
    client: RedisClient,
) -> Child:
    """Authenticate a child inside its family and open a short session."""
    pin = payload.pin.get_secret_value()
    parent_id = await db.scalar(
        select(Parent.id).where(Parent.family_code == payload.family_code)
    )
    child = (
        None
        if parent_id is None
        else await _find_child(db, parent_id, payload.pseudonym)
    )

    if child is None:
        # An unknown code and an unknown pseudonym cost the same as a real
        # attempt, so neither can be told apart by timing.
        spend_dummy_verification(pin)
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    # Checked before the PIN is verified: once the allowance is spent, even the
    # right PIN must wait, otherwise the lockout would only slow an attacker
    # down rather than stop them.
    if await is_locked(client, child.id, settings.CHILD_PIN_MAX_ATTEMPTS):
        raise RateLimitException(message=LOCKED_MESSAGE)

    if not verify_pin(pin, child.pin_hash):
        await register_failure(client, child.id, settings.CHILD_PIN_LOCKOUT_SECONDS)
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    await clear_failures(client, child.id)

    if child.status == CHILD_STATUS_PENDING:
        # Said plainly, but only to someone who already proved the credentials:
        # a child waiting for its parent needs to know why it cannot get in.
        raise AuthorizationException(message=PENDING_MESSAGE)

    if child.status != CHILD_STATUS_ACTIVE:
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    if needs_rehash(child.pin_hash):
        # The only moment the plain PIN is available to re-hash it under current
        # Argon2 parameters.
        child.pin_hash = hash_pin(pin)
        await db.commit()
        await db.refresh(child)

    token, _ = await create_session(
        client,
        user_id=child.id,
        user_type=CHILD_USER_TYPE,
        ttl_seconds=settings.CHILD_SESSION_TTL_SECONDS,
    )
    set_session_cookie(response, token, max_age=settings.CHILD_SESSION_TTL_SECONDS)

    return child


@router.get("/child/me", response_model=ChildPublic)
async def read_current_child(child: CurrentChild) -> Child:
    """Return the child behind the current session."""
    return child
