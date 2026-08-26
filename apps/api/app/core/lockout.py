"""Attempt lockout for a login, counted in Redis.

A six-digit PIN is a million combinations, which a script exhausts in hours if
nothing caps the attempts; a password is stronger, but nothing else in front
of a login endpoint caps repeated guesses either. Counting failures per
identity and refusing the login once the cap is reached turns an exhaustive
or a patient online search into something an attacker cannot finish.

The counter deliberately lives next to the sessions rather than in PostgreSQL:
it is short-lived state that must expire on its own, exactly what a Redis key
with a TTL already does.

`scope` keeps the child-PIN and parent-login counters in separate namespaces
so the same identifier could never collide between the two call sites.
"""

from __future__ import annotations

import uuid
from typing import Final

import redis.asyncio as redis

DEFAULT_SCOPE: Final = "child-pin"
LOCKED_MESSAGE: Final = "Trop de tentatives, réessayez dans quelques minutes"


def failure_key(identity_id: uuid.UUID, scope: str = DEFAULT_SCOPE) -> str:
    """Return the Redis key counting failed attempts for this identity."""
    return f"{scope}-failures:{identity_id}"


async def failure_count(
    client: redis.Redis, identity_id: uuid.UUID, scope: str = DEFAULT_SCOPE
) -> int:
    """Return how many failed attempts are currently held against this identity."""
    stored = await client.get(failure_key(identity_id, scope))
    if stored is None:
        return 0
    try:
        return int(stored)
    except ValueError:
        return 0


async def is_locked(
    client: redis.Redis,
    identity_id: uuid.UUID,
    max_attempts: int,
    scope: str = DEFAULT_SCOPE,
) -> bool:
    """Return whether this identity has spent its allowance of failed attempts."""
    return await failure_count(client, identity_id, scope) >= max_attempts


async def register_failure(
    client: redis.Redis,
    identity_id: uuid.UUID,
    lockout_seconds: int,
    scope: str = DEFAULT_SCOPE,
) -> int:
    """Count one failed attempt and return the new total.

    Every failure pushes the expiry back, so the window slides: an attacker who
    keeps guessing keeps the lock alive instead of waiting it out while probing.
    """
    key = failure_key(identity_id, scope)
    count = int(await client.incr(key))
    await client.expire(key, lockout_seconds)
    return count


async def clear_failures(
    client: redis.Redis, identity_id: uuid.UUID, scope: str = DEFAULT_SCOPE
) -> None:
    """Drop the failure count, as a successful login must."""
    await client.delete(failure_key(identity_id, scope))
