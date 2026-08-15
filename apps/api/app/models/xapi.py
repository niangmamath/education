"""What the content runtime said happened, as the server received it.

A statement is an **observation**, kept beside the facts of step 10 rather than
mixed into them. The content says "this question was answered, and it was
right"; the server writes that down, notes when it received it, and only then
turns the ones it understands into an `AttemptResponse` marked `xapi`.

Three properties are carried by this table and are the reason it exists.

**The actor is never the one the statement claims.** Whatever identity the
runtime puts in `actor` is discarded before anything is stored, and replaced by
a pseudonym the server derives from the child. The runtime is given no identity
to begin with — it only ever sees a content digest and an opaque ticket — so
anything it names there is either a default of its own making or something a
client invented. Storing it would let a browser write a real name into our
database through a field nobody reads.

**A replay is not a second event.** Network retries are ordinary, and a
statement resent is the same statement. `(attempt_id, statement_id)` is unique,
so the second arrival is recognised rather than counted twice. The uniqueness is
scoped to the attempt on purpose: made global, one family could suppress
another's statement by claiming its identifier first.

**Two clocks, and they are not the same.** `issued_at` is what the source
claims; `received_at` is the server's own clock. ADR-012's seventh condition
asks for exactly that separation, and it exists here because the first is
evidence about the source and only the second is evidence about time.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Final

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.attempt import Attempt, AttemptResponse

# The verbs H5P actually emits, and the only ones accepted. An allow-list rather
# than an open door: the fiche asks for *authorised* events, and a statement
# whose verb we have never seen is one we cannot claim to have understood.
VERB_ANSWERED: Final = "http://adlnet.gov/expapi/verbs/answered"
VERB_ATTEMPTED: Final = "http://adlnet.gov/expapi/verbs/attempted"
VERB_COMPLETED: Final = "http://adlnet.gov/expapi/verbs/completed"
VERB_INTERACTED: Final = "http://adlnet.gov/expapi/verbs/interacted"
VERB_PROGRESSED: Final = "http://adlnet.gov/expapi/verbs/progressed"
VERB_MASTERED: Final = "http://adlnet.gov/expapi/verbs/mastered"
VERB_PASSED: Final = "http://adlnet.gov/expapi/verbs/passed"
VERB_FAILED: Final = "http://adlnet.gov/expapi/verbs/failed"

ALLOWED_VERBS: Final = (
    VERB_ANSWERED,
    VERB_ATTEMPTED,
    VERB_COMPLETED,
    VERB_INTERACTED,
    VERB_PROGRESSED,
    VERB_MASTERED,
    VERB_PASSED,
    VERB_FAILED,
)

MAX_STATEMENT_ID_LENGTH: Final = 64
MAX_VERB_LENGTH: Final = 255
MAX_OBJECT_ID_LENGTH: Final = 500
# A statement is a short record of one interaction. A cap keeps a content — or a
# client pretending to be one — from writing whatever it likes into the database.
MAX_STATEMENT_BYTES: Final = 16 * 1024

ACTOR_KEY_LENGTH: Final = 64


class XapiStatement(Base):
    """One statement received from the content runtime, as stored."""

    __tablename__ = "xapi_statements"
    __table_args__ = (
        Index(
            "uq_xapi_statements_attempt_statement",
            "attempt_id",
            "statement_id",
            unique=True,
        ),
        Index("ix_xapi_statements_attempt", "attempt_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    # The statement's own identifier, as the sender gave it. It is what makes a
    # replay recognisable, and nothing else is read from it.
    statement_id: Mapped[str] = mapped_column(
        String(MAX_STATEMENT_ID_LENGTH), nullable=False
    )
    # Derived by the server from the child, never taken from the statement.
    actor_key: Mapped[str] = mapped_column(String(ACTOR_KEY_LENGTH), nullable=False)
    verb_id: Mapped[str] = mapped_column(String(MAX_VERB_LENGTH), nullable=False)
    object_id: Mapped[str] = mapped_column(String(MAX_OBJECT_ID_LENGTH), nullable=False)
    result_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    result_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    # The whole statement, actor already replaced, kept so that a reading can be
    # argued with later against what it was read from.
    statement: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # What the source claims. Never used as the time of anything.
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # The response this statement produced, when it produced one. Nullable
    # because most verbs say something that is not an answer.
    response_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attempt_responses.id", ondelete="SET NULL"),
        nullable=True,
    )

    attempt: Mapped[Attempt] = relationship()
    response: Mapped[AttemptResponse | None] = relationship()
