"""Short-lived tickets that let one content be fetched from the other origin.

The runtime lives on its own origin, which is the whole point of ADR-012's fifth
condition: a content that misbehaves must not be able to read the application's
cookies, because it is not the same site. The consequence is that the session
cookie cannot travel with the request either — so something else has to say that
this fetch is allowed.

That something is a **ticket**: an opaque value minted by the API when a child
opens an activity she is doing, held in Redis for a few minutes, and checked by
the content origin on every request through `auth_request`. It carries no
identity of its own; it names an assignment and the content it unlocks, and
nothing else.

The token is stored under its digest, exactly as sessions are: whoever reads the
store learns which contents are open, never the tickets that open them.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Final

import redis.asyncio as redis

from app.core.security import generate_session_token, hash_session_token

CONTENT_TICKET_PREFIX: Final = "content-ticket:"

# Long enough to open an activity and work through it, short enough that a link
# copied out of a browser is worthless by the time it is used elsewhere.
CONTENT_TICKET_TTL_SECONDS: Final = 30 * 60


@dataclass(frozen=True)
class ContentTicket:
    """What a ticket unlocks: one deployed content, for one assignment."""

    assignment_id: uuid.UUID
    content_digest: str


def ticket_key(token: str) -> str:
    return f"{CONTENT_TICKET_PREFIX}{hash_session_token(token)}"


async def mint_ticket(
    client: redis.Redis, assignment_id: uuid.UUID, content_digest: str
) -> str:
    """Hand out a ticket for one content, and return the value to put in the URL."""
    token = generate_session_token()
    await client.hset(  # type: ignore[misc]
        ticket_key(token),
        mapping={
            "assignment_id": str(assignment_id),
            "content_digest": content_digest,
        },
    )
    await client.expire(ticket_key(token), CONTENT_TICKET_TTL_SECONDS)
    return token


async def read_ticket(client: redis.Redis, token: str) -> ContentTicket | None:
    """The ticket behind that value, or nothing at all."""
    stored = await client.hgetall(ticket_key(token))  # type: ignore[misc]
    if not stored:
        return None
    try:
        return ContentTicket(
            assignment_id=uuid.UUID(stored["assignment_id"]),
            content_digest=stored["content_digest"],
        )
    except (KeyError, ValueError):
        return None


async def revoke_ticket(client: redis.Redis, token: str) -> None:
    """Give the ticket back before its time, when an activity is finished."""
    await client.delete(ticket_key(token))
