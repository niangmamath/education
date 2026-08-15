"""What the content origin asks before it serves a byte.

The runtime sits on its own origin, so no session cookie reaches it. nginx
therefore asks this route, through `auth_request`, whether the ticket in the
request opens the content being fetched.

The route answers `204` or `403` and nothing else. It says nothing about who the
ticket belongs to, nothing about whether the content exists, and nothing about
why a refusal happened: nginx has no use for any of it, and an answer that
explained itself would explain itself to whoever asked.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, Header, Response, status

from app.api.deps import RedisClient
from app.content.tokens import read_ticket

router = APIRouter()


@router.get(
    "/internal/content-access",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def check_content_access(
    client: RedisClient,
    x_original_uri: str | None = Header(default=None),
) -> Response:
    """Say only whether the ticket in that URL opens the content it asks for.

    The whole original URI is read here rather than two headers filled in by
    nginx: an `auth_request` subrequest has its own variable cache, so anything
    the protected location computed would arrive empty. Parsing the URI is one
    place instead of two, and it cannot be got subtly wrong in a config file.
    """
    if not x_original_uri:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    arguments = parse_qs(urlparse(x_original_uri).query)
    digest = next(iter(arguments.get("c", [])), None)
    token = next(iter(arguments.get("t", [])), None)
    if not digest or not token:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    ticket = await read_ticket(client, token)
    if ticket is None or ticket.content_digest != digest:
        # A ticket for another content is refused exactly like no ticket at all:
        # one ticket opens one content, and nothing here helps guess a second.
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
