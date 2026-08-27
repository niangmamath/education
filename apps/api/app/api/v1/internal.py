"""What the content origin asks before it serves a byte.

The runtime sits on its own origin, so no session cookie reaches it. nginx
therefore asks this route, through `auth_request`, whether the ticket in the
request opens the content being fetched — and, since the runtime stopped
living on a disk nginx can read directly, **where to fetch it from**.

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

**Answering used to be enough on its own**, because the byte lived beside
nginx. It no longer does: two services on a platform like Render cannot share a
disk, so the deployed content lives in a private bucket instead, and this route
now hands back a URL signed for exactly the object being asked for, valid for a
minute. nginx proxies to it and never sees the bucket's credentials; the
browser never sees the bucket at all. The route still says nothing about who
the ticket belongs to and nothing about why a refusal happened — the one thing
it now adds is where, and only for a request it has already decided to allow.
"""

from __future__ import annotations

import re
from typing import Annotated
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends, Header, Response, status

from app.api.deps import RedisClient
from app.catalog.storage import ObjectStore
from app.content.deploy import content_store
from app.content.tokens import read_ticket

router = APIRouter()

ContentStore = Annotated[ObjectStore, Depends(content_store)]

# `/t/<ticket>/content/<digest>/<reste>` or `/t/<ticket>/libraries/<reste>`. The
# digest is only present on the first form, and only that form is checked
# against the ticket: libraries are shared by every content, so holding a valid
# ticket is the whole of what may be asked of a request for one. The trailing
# group is required rather than optional because it is what gets signed — a
# request for a bare digest or a bare `libraries/` names no object to fetch.
TICKETED_PATH = re.compile(
    r"^/t/(?P<ticket>[^/]+)/"
    r"(?:content/(?P<digest>[^/]+)/(?P<content_rest>.+)"
    r"|libraries/(?P<library_rest>.+))$"
)

# Long enough to survive the round trip through nginx's own proxy, short enough
# that a URL copied out of this response is worthless once the byte is served.
SIGNED_URL_TTL_SECONDS = 60


@router.get(
    "/internal/content-access",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def check_content_access(
    client: RedisClient,
    store: ContentStore,
    x_original_uri: str | None = Header(default=None),
) -> Response:
    """Say whether the ticket in that path opens what it asks for, and where.

    The whole original URI is read here rather than pieces filled in by nginx:
    an `auth_request` subrequest has its own variable cache, so anything the
    protected location computed would arrive empty. Parsing the URI is one place
    instead of two, and it cannot be got subtly wrong in a configuration file.
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
    if digest is not None:
        # A ticket for another content is refused exactly like no ticket at
        # all: one ticket opens one content, and nothing here helps guess a
        # second.
        if ticket.content_digest != unquote(digest):
            return Response(status_code=status.HTTP_403_FORBIDDEN)
        key = f"content/{unquote(digest)}/{unquote(match.group('content_rest'))}"
    else:
        key = f"libraries/{unquote(match.group('library_rest'))}"

    # `internal=True`: nginx fetches this URL from inside the same private
    # network the API is on, never from a browser — signing it against the
    # public endpoint would hand it an address it cannot resolve.
    url = store.presign(key, expires_in=SIGNED_URL_TTL_SECONDS, internal=True)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT, headers={"X-Content-Url": url}
    )
