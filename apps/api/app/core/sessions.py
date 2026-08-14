"""Opaque server-side sessions backed by Redis.

ADR-005 rules out any SQL session table: a session exists only as a Redis entry
whose expiry is enforced by Redis itself, so revoking one is a single delete.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import redis.asyncio as redis

from app.core.security import generate_session_token, hash_session_token

SESSION_KEY_PREFIX: Final = "session:"
PARENT_USER_TYPE: Final = "parent"
CHILD_USER_TYPE: Final = "child"


@dataclass(frozen=True)
class SessionData:
    """Server-side state attached to a session token."""

    user_id: uuid.UUID
    user_type: str
    expires_at: datetime


def session_key(token: str) -> str:
    """Return the Redis key holding the session for this token."""
    return f"{SESSION_KEY_PREFIX}{hash_session_token(token)}"


async def create_session(
    client: redis.Redis,
    user_id: uuid.UUID,
    user_type: str,
    ttl_seconds: int,
) -> tuple[str, SessionData]:
    """Store a new session and return its token alongside its content.

    A fresh token is minted on every call, which is what keeps a login from
    reusing an identifier an attacker may already hold.
    """
    token = generate_session_token()
    expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    key = session_key(token)

    await client.hset(  # type: ignore[misc]
        key,
        mapping={
            "user_id": str(user_id),
            "user_type": user_type,
            "expires_at": expires_at.isoformat(),
        },
    )
    await client.expire(key, ttl_seconds)

    return token, SessionData(
        user_id=user_id, user_type=user_type, expires_at=expires_at
    )


async def read_session(client: redis.Redis, token: str) -> SessionData | None:
    """Return the session for this token, or None when it is absent or unusable."""
    stored = await client.hgetall(session_key(token))  # type: ignore[misc]
    if not stored:
        return None

    try:
        return SessionData(
            user_id=uuid.UUID(stored["user_id"]),
            user_type=stored["user_type"],
            expires_at=datetime.fromisoformat(stored["expires_at"]),
        )
    except (KeyError, ValueError):
        return None


async def delete_session(client: redis.Redis, token: str) -> None:
    """Revoke the session for this token. Deleting an absent session is a no-op."""
    await client.delete(session_key(token))
