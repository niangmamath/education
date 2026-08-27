"""Serving a content's bytes to the origin that plays it.

The runtime sits on its own origin, so no session cookie reaches it. What a
ticket replaces the cookie with is checked here, on every single file a
content or a library needs.

**This used to hand nginx a signed URL and let it fetch the bucket directly.**
That works when nginx can resolve the bucket's address — it could not on
Render: MinIO's private hostname exists only as an `/etc/hosts` entry there,
and nginx's `resolver` directive (the only way to resolve a host held in a
variable, which a per-request signed URL always is) never consults that file,
by design, on any platform. The API reaching the same bucket has never had
that problem — it resolves the same private name through the ordinary libc
path `/etc/hosts` is part of. So the API fetches the bytes itself now, and
nginx talks only to the API, an address it has always been able to reach.
The cost is bandwidth through one more hop; the benefit is that every leg of
the trip is one this platform has actually proven to work.

The path itself is what nginx already computed: `/t/<ticket>/content/<empreinte>/…`
or `/t/<ticket>/libraries/…`. Proxied here unprefixed and unchanged, so this
router's job is exactly parsing that shape once, in one language, instead of
splitting it between a path regex in a configuration file and a second regex
here.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from app.api.deps import RedisClient
from app.catalog.storage import ObjectStore
from app.content.deploy import content_store
from app.content.tokens import read_ticket

router = APIRouter()

ContentStore = Annotated[ObjectStore, Depends(content_store)]

# Read in chunks rather than all at once: a content's own asset (an image, a
# sound file) is small, but nothing here should hold a whole object in memory
# to serve one request.
CHUNK_SIZE = 256 * 1024


def _stream(body: object) -> Iterator[bytes]:
    try:
        while True:
            chunk = body.read(CHUNK_SIZE)  # type: ignore[attr-defined]
            if not chunk:
                return
            yield chunk
    finally:
        body.close()  # type: ignore[attr-defined]


async def _serve(store: ObjectStore, key: str) -> StreamingResponse:
    try:
        content_type, body = store.get_object(key)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return StreamingResponse(_stream(body), media_type=content_type)


@router.get("/t/{ticket}/content/{digest}/{path:path}", include_in_schema=False)
async def serve_content(
    ticket: str, digest: str, path: str, client: RedisClient, store: ContentStore
) -> Response:
    """One file of one deployed content, for the ticket that names it.

    A ticket for another content is refused exactly like no ticket at all:
    one ticket opens one content, and nothing here helps guess a second.
    """
    resolved = await read_ticket(client, ticket)
    if resolved is None or resolved.content_digest != digest:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    return await _serve(store, f"content/{digest}/{path}")


@router.get("/t/{ticket}/libraries/{path:path}", include_in_schema=False)
async def serve_library(
    ticket: str, path: str, client: RedisClient, store: ContentStore
) -> Response:
    """One file of the shared libraries, for any valid ticket.

    Libraries are shared by every content, so holding a valid ticket — for
    any content — is the whole of what may be asked of a request for one.
    """
    resolved = await read_ticket(client, ticket)
    if resolved is None:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    return await _serve(store, f"libraries/{path}")
