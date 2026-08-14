"""Shared FastAPI dependencies for authenticated routes."""

from __future__ import annotations

from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db_session
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.redis import get_redis_client
from app.core.sessions import (
    CHILD_USER_TYPE,
    PARENT_USER_TYPE,
    SessionData,
    read_session,
)
from app.models import Child, Parent
from app.models.identity import CHILD_STATUS_ACTIVE

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
RedisClient = Annotated[redis.Redis, Depends(get_redis_client)]

INVALID_SESSION_MESSAGE = "Session invalide ou expirée"


def get_session_token(request: Request) -> str:
    """Return the session token carried by the request cookie."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise AuthenticationException(message="Session absente")
    return token


SessionToken = Annotated[str, Depends(get_session_token)]


async def get_current_session(token: SessionToken, client: RedisClient) -> SessionData:
    """Resolve the caller's session, rejecting anything Redis no longer holds."""
    session = await read_session(client, token)
    if session is None:
        raise AuthenticationException(message=INVALID_SESSION_MESSAGE)
    return session


CurrentSession = Annotated[SessionData, Depends(get_current_session)]


async def get_current_parent(session: CurrentSession, db: DbSession) -> Parent:
    """Return the parent behind the current session.

    A deactivated account is treated as an invalid session rather than as a
    forbidden one, so the response says nothing about the account's existence.
    """
    if session.user_type != PARENT_USER_TYPE:
        raise AuthorizationException(
            message="Cette ressource est réservée aux comptes Parent"
        )

    parent = await db.get(Parent, session.user_id)
    if parent is None or not parent.is_active:
        raise AuthenticationException(message=INVALID_SESSION_MESSAGE)

    return parent


CurrentParent = Annotated[Parent, Depends(get_current_parent)]


async def get_current_child(session: CurrentSession, db: DbSession) -> Child:
    """Return the child behind the current session.

    A parent session is refused here rather than silently accepted: the two
    spaces show different data, and a route that takes either would be one
    forgotten check away from showing a child the parent dashboard.
    """
    if session.user_type != CHILD_USER_TYPE:
        raise AuthorizationException(
            message="Cette ressource est réservée aux profils Enfant"
        )

    child = await db.get(Child, session.user_id)
    if child is None or child.status != CHILD_STATUS_ACTIVE:
        raise AuthenticationException(message=INVALID_SESSION_MESSAGE)

    return child


CurrentChild = Annotated[Child, Depends(get_current_child)]
