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

# Sessions are keyed by the digest of a token nobody but their holder knows, so
# nothing lets the server find the sessions of a given account. This index does:
# it is what makes revoking every session of one child possible when its PIN
# changes or its profile is turned off.
USER_SESSIONS_KEY_PREFIX: Final = "user-sessions:"

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


def user_sessions_key(user_id: uuid.UUID) -> str:
    """Return the Redis key indexing every session key of one account."""
    return f"{USER_SESSIONS_KEY_PREFIX}{user_id}"


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

    # The index outlives no session it points to: its own expiry is pushed to the
    # newest one, and a member whose session has expired is a key that no longer
    # exists, which deleting simply ignores.
    index = user_sessions_key(user_id)
    await client.sadd(index, key)  # type: ignore[misc]
    await client.expire(index, ttl_seconds)

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
    key = session_key(token)
    session = await read_session(client, token)

    await client.delete(key)
    if session is not None:
        await client.srem(user_sessions_key(session.user_id), key)  # type: ignore[misc]


async def revoke_user_sessions(
    client: redis.Redis, user_id: uuid.UUID, except_token: str | None = None
) -> int:
    """Revoke every session of an account and return how many were dropped.

    `except_token` spares the caller's own session, which is what a child
    changing its own PIN expects: the other devices are logged out, not the one
    in its hands.
    """
    index = user_sessions_key(user_id)
    spared = session_key(except_token) if except_token is not None else None

    keys = {key for key in await client.smembers(index) if key != spared}  # type: ignore[misc]
    if keys:
        await client.delete(*keys)
        await client.srem(index, *keys)  # type: ignore[misc]

    return len(keys)
