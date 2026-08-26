"""Parent authentication and session endpoints.

Routes follow the parent flow of ADR-005: register, then log in against an
opaque session stored in Redis and carried by an HttpOnly cookie, then log out
by revoking that session server-side.

Registration also mints the family code, the handle a parent gives their
children; the child side of it lives in `children.py`.
"""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cookies import clear_session_cookie, set_session_cookie
from app.api.deps import (
    INVALID_SESSION_MESSAGE,
    CurrentParent,
    CurrentSession,
    DbSession,
    RedisClient,
    SessionToken,
)
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ConflictException
from app.core.lockout import clear_failures, is_locked, register_failure
from app.core.security import (
    generate_family_code,
    hash_password,
    needs_rehash,
    spend_dummy_verification,
    verify_password,
)
from app.core.sessions import (
    CHILD_USER_TYPE,
    PARENT_USER_TYPE,
    create_session,
    delete_session,
    revoke_user_sessions,
)
from app.models import Child, Parent
from app.models.identity import CHILD_STATUS_ACTIVE
from app.schemas.auth import (
    ParentLoginRequest,
    ParentPasswordChangeRequest,
    ParentPublic,
    ParentRegisterRequest,
    ParentUpdateRequest,
    SessionPublic,
)

router = APIRouter()

# A single message for every failed login: distinct wording would turn the
# endpoint into an oracle telling an attacker which emails hold an account.
INVALID_CREDENTIALS_MESSAGE = "Identifiants invalides"
EMAIL_TAKEN_MESSAGE = "Un compte existe déjà pour cette adresse email"

# Draws are checked against the accounts already held, so this only bounds an
# absurd run of bad luck rather than an expected retry.
FAMILY_CODE_ATTEMPTS = 3


async def _draw_unused_family_code(db: AsyncSession) -> str:
    """Return a family code no account holds yet."""
    for _ in range(FAMILY_CODE_ATTEMPTS):
        code = generate_family_code()
        if await db.scalar(select(Parent.id).where(Parent.family_code == code)) is None:
            return code

    raise ConflictException(message="Tirage du code famille impossible, réessayez")


@router.post(
    "/parent/register",
    response_model=ParentPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register_parent(payload: ParentRegisterRequest, db: DbSession) -> Parent:
    """Create a parent account, and with it the family code, without a session.

    Registration deliberately does not log the caller in: ADR-005 places email
    verification between the two, and that flow is not implemented yet.
    """
    existing = await db.scalar(select(Parent).where(Parent.email == payload.email))
    if existing is not None:
        raise ConflictException(message=EMAIL_TAKEN_MESSAGE)

    parent = Parent(
        email=payload.email,
        family_code=await _draw_unused_family_code(db),
        password_hash=hash_password(payload.password.get_secret_value()),
        display_name=payload.display_name,
    )
    db.add(parent)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Two concurrent registrations reach the check above together; the unique
        # constraints are what actually settle the race. Only the email can
        # realistically clash: the code was just verified free, and two identical
        # draws out of eight hundred million in the same instant is not a case
        # worth carrying a retry loop for.
        taken = await db.scalar(select(Parent.id).where(Parent.email == payload.email))
        if taken is not None:
            raise ConflictException(message=EMAIL_TAKEN_MESSAGE) from exc
        raise

    await db.refresh(parent)
    return parent


@router.post("/parent/family-code/regenerate", response_model=ParentPublic)
async def regenerate_family_code(parent: CurrentParent, db: DbSession) -> Parent:
    """Replace the family code, for a parent whose code has got around.

    The old code stops working at once, for logging in as well as for opening a
    profile. Sessions already opened are untouched: a child logged in on the
    family tablet is not the reason the code leaked, and throwing it out would
    turn a precaution into a punishment.

    Profiles already created under the old code remain, pending ones included:
    deleting a child profile is never a side effect of another action.
    """
    parent.family_code = await _draw_unused_family_code(db)
    await db.commit()
    await db.refresh(parent)
    return parent


@router.post("/parent/login", response_model=ParentPublic)
async def login_parent(
    payload: ParentLoginRequest,
    response: Response,
    db: DbSession,
    client: RedisClient,
) -> Parent:
    """Authenticate a parent and open a session."""
    password = payload.password.get_secret_value()
    parent = await db.scalar(select(Parent).where(Parent.email == payload.email))

    if parent is None:
        spend_dummy_verification(password)
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    # Checked before the password is verified: once the allowance is spent,
    # even the right password must wait, otherwise the lockout would only
    # slow an attacker down rather than stop them (mirrors the child PIN
    # login in `children.py`, the only other thing guarding a login here).
    #
    # Raised as the same exception as a wrong password, not as a distinct
    # `RateLimitException`: an unknown email never locks (it always takes the
    # `parent is None` branch above), so a distinct status/message here would
    # let an attacker tell a registered email apart from one that doesn't
    # exist just by submitting enough wrong passwords and watching for the
    # response to change — exactly the oracle `INVALID_CREDENTIALS_MESSAGE`
    # exists to deny them.
    if await is_locked(
        client, parent.id, settings.PARENT_LOGIN_MAX_ATTEMPTS, scope="parent-login"
    ):
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    if not verify_password(password, parent.password_hash):
        await register_failure(
            client,
            parent.id,
            settings.PARENT_LOGIN_LOCKOUT_SECONDS,
            scope="parent-login",
        )
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    await clear_failures(client, parent.id, scope="parent-login")

    if not parent.is_active:
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    if needs_rehash(parent.password_hash):
        # The only moment the plain password is available to re-hash it under
        # current parameters.
        parent.password_hash = hash_password(password)
        await db.commit()
        await db.refresh(parent)

    token, _ = await create_session(
        client,
        user_id=parent.id,
        user_type=PARENT_USER_TYPE,
        ttl_seconds=settings.SESSION_TTL_SECONDS,
    )
    set_session_cookie(response, token, max_age=settings.SESSION_TTL_SECONDS)

    return parent


@router.delete(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    # A bare `-> None` annotation would be read as a response model, which a 204
    # is not allowed to carry.
    response_model=None,
)
async def logout(
    response: Response,
    token: SessionToken,
    client: RedisClient,
) -> None:
    """Revoke the current session and clear the cookie.

    The route serves parent and child sessions alike: it only needs the token,
    never the identity behind it. Revoking a session Redis has already expired
    is a no-op, so a stale cookie still gets cleared instead of trapping the
    caller in a failing request.
    """
    await delete_session(client, token)
    clear_session_cookie(response)


@router.get("/me", response_model=ParentPublic)
async def read_current_parent(parent: CurrentParent) -> Parent:
    """Return the parent behind the current session."""
    return parent


@router.put("/me", response_model=ParentPublic)
async def update_parent(
    payload: ParentUpdateRequest, parent: CurrentParent, db: DbSession
) -> Parent:
    """Rename a parent's own profile. See `ParentUpdateRequest` for why this
    route touches nothing else."""
    parent.display_name = payload.display_name
    await db.commit()
    await db.refresh(parent)
    return parent


@router.put("/me/password", response_model=ParentPublic)
async def change_parent_password(
    payload: ParentPasswordChangeRequest,
    parent: CurrentParent,
    db: DbSession,
    client: RedisClient,
    token: SessionToken,
) -> Parent:
    """Change a password, never without the one it replaces.

    Every other session this parent holds is revoked once the new password is
    set — a laptop left signed in elsewhere should not outlive the password
    that opened it — except the one making this request, which just proved
    itself with the current password and needs no second proof.
    """
    if not verify_password(
        payload.current_password.get_secret_value(), parent.password_hash
    ):
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

    parent.password_hash = hash_password(payload.new_password.get_secret_value())
    await db.commit()
    await db.refresh(parent)

    await revoke_user_sessions(client, parent.id, except_token=token)
    return parent


@router.get("/session", response_model=SessionPublic)
async def read_current_session(session: CurrentSession, db: DbSession) -> SessionPublic:
    """Say which space the caller is in, and under what name.

    Open to either role, because the question is the same for both and a client
    has to answer it before it can ask anything else. It says nothing a session
    does not already establish: the holder of the cookie learns who they are.

    An account deactivated or removed since the cookie was minted is treated as
    an invalid session rather than as a name that no longer resolves — the same
    rule the two `me` routes follow.
    """
    if session.user_type == PARENT_USER_TYPE:
        parent = await db.get(Parent, session.user_id)
        if parent is None or not parent.is_active:
            raise AuthenticationException(message=INVALID_SESSION_MESSAGE)
        return SessionPublic(
            user_type=PARENT_USER_TYPE, id=parent.id, display_name=parent.display_name
        )

    child = await db.get(Child, session.user_id)
    if child is None or child.status != CHILD_STATUS_ACTIVE:
        raise AuthenticationException(message=INVALID_SESSION_MESSAGE)
    return SessionPublic(
        user_type=CHILD_USER_TYPE, id=child.id, display_name=child.display_name
    )
