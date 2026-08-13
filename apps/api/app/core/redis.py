"""Redis client wiring for request-scoped access."""

from __future__ import annotations

from collections.abc import AsyncIterator

import redis.asyncio as redis

from app.core.config import settings


async def get_redis_client() -> AsyncIterator[redis.Redis]:
    """Yield a Redis client for the duration of a request.

    The client is built per request rather than shared at module scope because a
    pooled asyncio client binds to the event loop that first used it, which
    breaks as soon as another loop takes over, as the synchronous test client
    does. Connection pooling belongs to the later operations step.
    """
    client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
