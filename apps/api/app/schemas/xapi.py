"""What a stored statement looks like on the wire.

There is deliberately no request model. An xAPI statement is an open,
extensible structure defined elsewhere, and pinning it to a Pydantic model would
either refuse valid statements or quietly drop the parts of them we chose not to
name. `app/xapi/statements.py` reads what it needs and keeps the rest as it
arrived, which is both more faithful and easier to argue with later.

The reply names the pseudonymous actor the server substituted. Showing it is the
point: the sender can see that what it claimed was replaced.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StatementPublic(BaseModel):
    """One statement as the server holds it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    attempt_id: uuid.UUID
    statement_id: str
    # The server's pseudonym, never the one the statement carried.
    actor_key: str
    verb_id: str
    object_id: str
    result_success: bool | None
    result_response: str | None
    # What the source claims, and what the server observed. Two clocks, kept
    # apart, as ADR-012's seventh condition asks.
    issued_at: datetime | None
    received_at: datetime
    # The response this statement produced, when it was an answer.
    response_id: uuid.UUID | None
