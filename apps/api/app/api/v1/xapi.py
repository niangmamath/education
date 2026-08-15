"""The endpoint the content runtime's statements reach, through the page above.

`play.html` cannot call this route and is not meant to: it lives on another
origin, holds no session, and posts its statements up to the application page
with `postMessage`. That page — same origin as the API, carrying the session
cookie — is what forwards them here, together with the ticket it already holds
from having opened the activity.

That indirection is the design and not an inconvenience. The runtime is never
given a credential, so a content that misbehaves has nothing to misuse; and the
statement still arrives with something the server minted itself, so it cannot be
sent from nowhere.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Header, Response, status

from app.api.deps import CurrentChild, DbSession, RedisClient
from app.schemas.xapi import StatementPublic
from app.xapi import service

router = APIRouter()

# The ticket travels in a header, not in the body: it is not part of the
# statement, and a statement that could carry its own authorisation would be one
# forgery away from being its own permission.
ContentTicket = Annotated[str | None, Header(alias="X-Content-Ticket")]


@router.post("/me/xapi/statements", response_model=StatementPublic)
async def receive_statement(
    payload: dict[str, Any],
    child: CurrentChild,
    db: DbSession,
    client: RedisClient,
    response: Response,
    x_content_ticket: ContentTicket = None,
) -> Any:
    """Take in one statement from the activity currently open.

    Answers `201` when the statement was new and `200` when the same one had
    already been received for this attempt. Neither is an error: a retry over a
    flaky connection is the same event, and the client is told which happened
    rather than shown a conflict.
    """
    record, created = await service.ingest(db, client, child, x_content_ticket, payload)
    await db.commit()
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return record


@router.get(
    "/me/attempts/{attempt_id}/xapi/statements", response_model=list[StatementPublic]
)
async def list_statements(
    attempt_id: uuid.UUID, child: CurrentChild, db: DbSession
) -> Any:
    """What was received for one of this child's attempts, oldest first.

    Reserved to the child whose attempt it is, like every other route that
    touches an attempt. What a parent is shown is the reading, through the
    progress of this step and the dashboards of step 13 — not the raw traffic of
    a content her child was using.
    """
    return await service.list_for_attempt(db, child, attempt_id)
