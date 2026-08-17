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
from app.assessment import service as assessment
from app.api.deps import (
    CurrentChild,
    CurrentParent,
    DbSession,
    RedisClient,
    SessionToken,
)
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
from app.core.sessions import CHILD_USER_TYPE, create_session, revoke_user_sessions
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
    ChildPinChangeRequest,
    ChildPinResetRequest,
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
PROFILE_NOT_FOUND_MESSAGE = "Profil introuvable"


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


async def _own_child(db: DbSession, parent_id: uuid.UUID, child_id: uuid.UUID) -> Child:
    """Return one child of this family, or refuse without saying more.

    A profile belonging to another family answers exactly like one that does not
    exist, so these routes cannot be used to probe the other families.
    """
    child = await db.scalar(
        select(Child).where(Child.id == child_id, Child.parent_id == parent_id)
    )
    if child is None:
        raise NotFoundException(message=PROFILE_NOT_FOUND_MESSAGE)
    return child


@router.post("/children/{child_id}/activate", response_model=ChildPublic)
async def activate_child(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Child:
    """Open access to a profile, whether it was pending or turned off.

    Activation is also where the initiation assessment is given. It is the one
    place the platform assigns anything, and the exception is argued rather than
    assumed: a diagnostic that waits for a parent to think of it is a diagnostic
    that does not happen, and everything downstream has nothing to work from
    until it does. Remediation stays what it was — proposed, never given.
    """
    child = await _own_child(db, parent.id, child_id)

    if child.status != CHILD_STATUS_ACTIVE:
        child.status = CHILD_STATUS_ACTIVE

    await assessment.give_to(db, parent.id, child)
    await db.commit()
    await db.refresh(child)

    return child


@router.post("/children/{child_id}/deactivate", response_model=ChildPublic)
async def deactivate_child(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession, client: RedisClient
) -> Child:
    """Close access to a profile without losing anything it holds.

    Sessions open on the child's devices are revoked on the spot rather than
    left to expire: turning a profile off has to mean it, including on the
    tablet already logged in.
    """
    child = await _own_child(db, parent.id, child_id)

    if child.status == CHILD_STATUS_PENDING:
        raise ConflictException(
            message="Profil en attente, écartez-le plutôt que de le désactiver"
        )

    if child.status != CHILD_STATUS_DISABLED:
        child.status = CHILD_STATUS_DISABLED
        await db.commit()
        await db.refresh(child)

    await revoke_user_sessions(client, child.id)
    return child


@router.put("/children/{child_id}/pin", response_model=ChildPublic)
async def reset_child_pin(
    child_id: uuid.UUID,
    payload: ChildPinResetRequest,
    parent: CurrentParent,
    db: DbSession,
    client: RedisClient,
) -> Child:
    """Set a new PIN for a child, for the day nobody remembers the old one.

    Two things follow, and both are the point of the route: the failed-attempt
    lockout is cleared, since a child locked out of a PIN that no longer exists
    would stay locked out for nothing, and the sessions opened with the previous
    PIN are revoked.
    """
    child = await _own_child(db, parent.id, child_id)

    child.pin_hash = hash_pin(payload.pin.get_secret_value())
    await db.commit()
    await db.refresh(child)

    await clear_failures(client, child.id)
    await revoke_user_sessions(client, child.id)

    return child


@router.put("/child/pin", response_model=ChildPublic)
async def change_own_pin(
    payload: ChildPinChangeRequest,
    child: CurrentChild,
    token: SessionToken,
    db: DbSession,
    client: RedisClient,
) -> Child:
    """Let a child replace its own PIN, against the current one.

    The child's own session survives, the others do not: whoever else was logged
    in with the old PIN loses access, which is the whole reason a child changes
    a PIN it thinks someone has seen.
    """
    if not verify_pin(payload.current_pin.get_secret_value(), child.pin_hash):
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    child.pin_hash = hash_pin(payload.new_pin.get_secret_value())
    await db.commit()
    await db.refresh(child)

    await revoke_user_sessions(client, child.id, except_token=token)

    return child


@router.delete(
    "/children/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    # A bare `-> None` annotation would be read as a response model, which a 204
    # is not allowed to carry.
    response_model=None,
)
async def delete_child(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession, client: RedisClient
) -> None:
    """Remove a profile, with everything the family cascade carries with it.

    A pending profile goes straight away: that is the other half of the answer to
    a family code that has got around, since regenerating the code closes the
    door and this clears what came through before.

    An active profile does not. It holds a history a child built, and the results
    of the later steps will hang from it, so it must be deactivated first: two
    deliberate steps, and a window during which the parent can still change their
    mind, instead of one call that empties a child's year.
    """
    child = await _own_child(db, parent.id, child_id)

    if child.status == CHILD_STATUS_ACTIVE:
        raise ConflictException(
            message="Profil actif, désactivez-le avant de le supprimer"
        )

    await db.delete(child)
    await db.commit()

    await revoke_user_sessions(client, child.id)
    await clear_failures(client, child.id)


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
