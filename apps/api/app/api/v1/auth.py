"""Parent authentication and session endpoints.

Routes follow the parent flow of ADR-005: register, then log in against an
opaque session stored in Redis and carried by an HttpOnly cookie, then log out
by revoking that session server-side.
"""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentParent, DbSession, RedisClient, SessionToken
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ConflictException
from app.core.security import (
    hash_password,
    needs_rehash,
    spend_dummy_verification,
    verify_password,
)
from app.core.sessions import PARENT_USER_TYPE, create_session, delete_session
from app.models import Parent
from app.schemas.auth import ParentLoginRequest, ParentPublic, ParentRegisterRequest

router = APIRouter()

# A single message for every failed login: distinct wording would turn the
# endpoint into an oracle telling an attacker which emails hold an account.
INVALID_CREDENTIALS_MESSAGE = "Identifiants invalides"


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )


@router.post(
    "/parent/register",
    response_model=ParentPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register_parent(payload: ParentRegisterRequest, db: DbSession) -> Parent:
    """Create a parent account without opening a session.

    Registration deliberately does not log the caller in: ADR-005 places email
    verification between the two, and that flow is not implemented yet.
    """
    existing = await db.scalar(select(Parent).where(Parent.email == payload.email))
    if existing is not None:
        raise ConflictException(
            message="Un compte existe déjà pour cette adresse email"
        )

    parent = Parent(
        email=payload.email,
        password_hash=hash_password(payload.password.get_secret_value()),
        display_name=payload.display_name,
    )
    db.add(parent)

    try:
        await db.commit()
    except IntegrityError as exc:
        # Two concurrent registrations reach the check above together; the
        # unique constraint is what actually settles the race.
        await db.rollback()
        raise ConflictException(
            message="Un compte existe déjà pour cette adresse email"
        ) from exc

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

    if not verify_password(password, parent.password_hash):
        raise AuthenticationException(message=INVALID_CREDENTIALS_MESSAGE)

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
    _set_session_cookie(response, token)

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

    Revoking a session Redis has already expired is a no-op, so a stale cookie
    still gets cleared instead of trapping the caller in a failing request.
    """
    await delete_session(client, token)
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")


@router.get("/me", response_model=ParentPublic)
async def read_current_parent(parent: CurrentParent) -> Parent:
    """Return the parent behind the current session."""
    return parent
