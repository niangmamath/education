"""Taking in a statement: who may send one, for what, and what it becomes.

The chain of trust is worth stating in full, because it is the whole of what
ADR-012's sixth condition asks for — an xAPI endpoint that is *authenticated*
and *authorised*.

1. **Authenticated by the session cookie.** The sender is a child, signed in on
   the application origin. The runtime itself never calls this route and holds
   nothing that would let it: it has no cookie, no key, no address for the API.
2. **Authorised by the ticket.** The same opaque ticket that opens the content
   must be presented, in a header rather than in the body — it is not part of
   the statement and must not look like one. A ticket names an assignment and a
   content; it was minted by the server when this child opened this activity,
   and it expires. So a statement can only be sent while a content is genuinely
   open, and only for the activity it was opened for.
3. **Bound to the attempt by the server.** The client never names an attempt.
   The ticket gives the assignment, and the attempt is the one running for it.
   A client that could name the attempt could file an observation against a
   different piece of work.

The child's own session and the ticket are checked against each other: a ticket
belonging to another family's assignment is refused exactly as an expired one
is. Tickets are opaque and unguessable, so this is defence in depth rather than
a hole being closed — but it is the check that makes the guarantee true by
construction instead of by argument.

**What the identity crosses, and what does not.** The runtime is given the
content digest and the ticket. Not the child, not the pseudonym, not the
assignment. Coming back, the statement's claimed actor is discarded and the
server writes its own pseudonym. So the link between a statement and a child is
made *here*, on the server, from a session — and it exists nowhere else.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.tokens import read_ticket
from app.core.exceptions import AuthorizationException, ConflictException
from app.models.assignment import Assignment
from app.models.attempt import (
    ATTEMPT_STATUS_IN_PROGRESS,
    RESPONSE_SOURCE_XAPI,
    Attempt,
    AttemptResponse,
)
from app.models.identity import Child
from app.models.xapi import XapiStatement
from app.xapi import statements as parsing

TICKET_REQUIRED_MESSAGE = (
    "Un événement xAPI ne peut être envoyé que depuis une activité ouverte"
)
NO_ATTEMPT_MESSAGE = (
    "Commencez une tentative avant d’envoyer les événements de l’activité"
)


async def ingest(
    db: AsyncSession,
    client: redis.Redis,
    child: Child,
    ticket_token: str | None,
    payload: Any,
) -> tuple[XapiStatement, bool]:
    """Record one statement, and return it with whether it was new.

    A statement already held for this attempt is handed back untouched rather
    than written again: a retransmission is the same event, and the caller is
    told so by the `False` instead of by an error.
    """
    attempt = await _attempt_behind_ticket(db, client, child, ticket_token)
    key = parsing.actor_key(child.id)
    parsed = parsing.parse(payload, key)

    existing = await db.scalar(
        select(XapiStatement).where(
            XapiStatement.attempt_id == attempt.id,
            XapiStatement.statement_id == parsed.statement_id,
        )
    )
    if existing is not None:
        return existing, False

    response = None
    if parsed.is_answer:
        # An answer becomes a response marked `xapi`, and `source` is set here
        # rather than read from anywhere: a client able to declare where its own
        # data came from would erase the distinction the column exists for.
        response = AttemptResponse(
            attempt_id=attempt.id,
            question_ref=parsed.object_id,
            response=parsed.result_response,
            is_correct=parsed.result_success,
            source=RESPONSE_SOURCE_XAPI,
        )
        db.add(response)
        await db.flush()

    record = XapiStatement(
        attempt_id=attempt.id,
        statement_id=parsed.statement_id,
        actor_key=key,
        verb_id=parsed.verb_id,
        object_id=parsed.object_id,
        result_success=parsed.result_success,
        result_response=parsed.result_response,
        statement=parsed.statement,
        issued_at=parsed.issued_at,
        response_id=response.id if response is not None else None,
    )
    db.add(record)
    await db.flush()
    return record, True


async def list_for_attempt(
    db: AsyncSession, child: Child, attempt_id: uuid.UUID
) -> Sequence[XapiStatement]:
    """The statements held for one attempt of this child, oldest first."""
    rows = await db.scalars(
        select(XapiStatement)
        .join(Attempt, Attempt.id == XapiStatement.attempt_id)
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(XapiStatement.attempt_id == attempt_id, Assignment.child_id == child.id)
        .order_by(XapiStatement.received_at, XapiStatement.statement_id)
    )
    return rows.all()


async def _attempt_behind_ticket(
    db: AsyncSession,
    client: redis.Redis,
    child: Child,
    ticket_token: str | None,
) -> Attempt:
    """The attempt this ticket allows statements about, or a flat refusal.

    Every refusal here says the same thing. A missing ticket, an expired one,
    one minted for another family: nothing in the answer helps tell them apart,
    because the difference is only useful to someone trying them in turn.
    """
    if not ticket_token:
        raise AuthorizationException(message=TICKET_REQUIRED_MESSAGE)

    ticket = await read_ticket(client, ticket_token)
    if ticket is None:
        raise AuthorizationException(message=TICKET_REQUIRED_MESSAGE)

    assignment = await db.scalar(
        select(Assignment).where(
            Assignment.id == ticket.assignment_id, Assignment.child_id == child.id
        )
    )
    if assignment is None:
        raise AuthorizationException(message=TICKET_REQUIRED_MESSAGE)

    attempt = await db.scalar(
        select(Attempt).where(
            Attempt.assignment_id == assignment.id,
            Attempt.status == ATTEMPT_STATUS_IN_PROGRESS,
        )
    )
    if attempt is None:
        # A distinct answer, because this one is the sender's to fix: the
        # activity is open but no attempt is running behind it.
        raise ConflictException(message=NO_ATTEMPT_MESSAGE)
    return attempt
