"""What the content origin asks before it serves a byte.

The runtime sits on its own origin, so no session cookie reaches it. nginx
therefore asks this route, through `auth_request`, whether the ticket in the
request opens the content being fetched.

**The ticket travels in the path, and that is a correction.** The first design
put it in the query string and expected the H5P player to carry it on every
asset it fetched. It does not: a player composes an asset URL by joining path
segments, and a query string is not a path segment, so it was dropped the moment
the player asked for anything of its own. Nothing caught it because no content
had ever been played end to end — a receiver with no producer only gets
exercised by requests made up by hand.

A path prefix survives that joining by construction, which is the whole reason
for the change: the platform no longer has to control every URL the player
invents. A cookie would have been the other candidate and is worse here — the
runtime is embedded cross-site, so its cookie would have to be a third-party
one, exactly the thing browsers are removing.

The route answers `204` or `403` and nothing else. It says nothing about who the
ticket belongs to, nothing about whether the content exists, and nothing about
why a refusal happened: nginx has no use for any of it, and an answer that
explained itself would explain itself to whoever asked.
"""

from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Header, Response, status

from app.api.deps import RedisClient
from app.content.tokens import read_ticket

router = APIRouter()

# `/t/<ticket>/content/<digest>/…` or `/t/<ticket>/libraries/…`. The digest is
# only present on the first form, and only that form is checked against the
# ticket: libraries are shared by every content, so holding a valid ticket is the
# whole of what may be asked of a request for one.
TICKETED_PATH = re.compile(
    r"^/t/(?P<ticket>[^/]+)/(?:content/(?P<digest>[^/]+)|libraries)(?:/|$)"
)


@router.get(
    "/internal/content-access",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def check_content_access(
    client: RedisClient,
    x_original_uri: str | None = Header(default=None),
) -> Response:
    """Say only whether the ticket in that path opens what it asks for.

    The whole original URI is read here rather than pieces filled in by nginx:
    an `auth_request` subrequest has its own variable cache, so anything the
    protected location computed would arrive empty. Parsing the URI is one place
    instead of two, and it cannot be got subtly wrong in a config file.
    """
    if not x_original_uri:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    match = TICKETED_PATH.match(urlparse(x_original_uri).path)
    if match is None:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    ticket = await read_ticket(client, unquote(match.group("ticket")))
    if ticket is None:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    digest = match.group("digest")
    if digest is not None and ticket.content_digest != unquote(digest):
        # A ticket for another content is refused exactly like no ticket at all:
        # one ticket opens one content, and nothing here helps guess a second.
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
