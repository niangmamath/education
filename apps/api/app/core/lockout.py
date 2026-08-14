"""Attempt lockout for the child PIN, counted in Redis.

A six-digit PIN is a million combinations, which a script exhausts in hours if
nothing caps the attempts. Counting failures per child and refusing the login
once the cap is reached turns that exhaustive search into something no online
attacker can finish.

The counter deliberately lives next to the sessions rather than in PostgreSQL:
it is short-lived state that must expire on its own, exactly what a Redis key
with a TTL already does.
"""

from __future__ import annotations

import uuid
from typing import Final

import redis.asyncio as redis

FAILURE_KEY_PREFIX: Final = "child-pin-failures:"


def failure_key(child_id: uuid.UUID) -> str:
    """Return the Redis key counting failed PIN attempts for this child."""
    return f"{FAILURE_KEY_PREFIX}{child_id}"


async def failure_count(client: redis.Redis, child_id: uuid.UUID) -> int:
    """Return how many failed attempts are currently held against this child."""
    stored = await client.get(failure_key(child_id))
    if stored is None:
        return 0
    try:
        return int(stored)
    except ValueError:
        return 0


async def is_locked(
    client: redis.Redis, child_id: uuid.UUID, max_attempts: int
) -> bool:
    """Return whether this child has spent its allowance of failed attempts."""
    return await failure_count(client, child_id) >= max_attempts


async def register_failure(
    client: redis.Redis, child_id: uuid.UUID, lockout_seconds: int
) -> int:
    """Count one failed attempt and return the new total.

    Every failure pushes the expiry back, so the window slides: an attacker who
    keeps guessing keeps the lock alive instead of waiting it out while probing.
    """
    key = failure_key(child_id)
    count = int(await client.incr(key))
    await client.expire(key, lockout_seconds)
    return count


async def clear_failures(client: redis.Redis, child_id: uuid.UUID) -> None:
    """Drop the failure count, as a successful login must."""
    await client.delete(failure_key(child_id))
