"""Reading a statement, and deciding what of it may be kept.

Everything here is about **not believing the sender more than necessary**. A
statement arrives through a browser: the runtime produced it, but the page that
relays it could have written anything. So this module never takes the sender's
word on the two things that would matter most if it were wrong.

- **The actor is thrown away.** The runtime is handed no identity — its URL
  carries a content digest and an opaque ticket, and nothing else — so whatever
  it names in `actor` is either a default of its own or something a client
  invented. The server puts its own pseudonym there instead, derived from the
  child behind the session. Keeping the claimed one would let a browser write a
  real name into the database through a field nobody reads.
- **The timestamp is kept as a claim, not as the time.** `issued_at` says what
  the source says; the moment that counts is the server's, and it is set by the
  database. ADR-012's seventh condition asks for that separation.

What is taken at face value is the description of the interaction itself — the
verb, the object, whether the answer was judged right — because that is the
content's own account and the whole reason for asking it. The verb must be one
we have seen H5P emit: a statement we have never met is refused rather than
stored as understood.

Nothing is truncated. An object identifier too long for the column is a refusal,
because shortening it would silently merge two questions into one.
"""

from __future__ import annotations

import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any, Final

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.models.attempt import MAX_QUESTION_REF_LENGTH, MAX_RESPONSE_LENGTH
from app.models.xapi import (
    ALLOWED_VERBS,
    MAX_OBJECT_ID_LENGTH,
    MAX_STATEMENT_BYTES,
    MAX_STATEMENT_ID_LENGTH,
    VERB_ANSWERED,
)

# The homepage of the pseudonymous account. It names the platform and nothing
# about the person: an xAPI agent needs a namespace, not an identity.
ACTOR_HOME_PAGE: Final = "https://studentconnect.local/pseudonymes"

_ACTOR_NAMESPACE: Final = b"xapi-actor:"


@dataclass(frozen=True)
class ParsedStatement:
    """A statement reduced to what the platform is willing to hold."""

    statement_id: str
    verb_id: str
    object_id: str
    result_success: bool | None
    result_response: str | None
    issued_at: datetime | None
    statement: dict[str, Any]

    @property
    def is_answer(self) -> bool:
        """Whether this statement reports an answer to a question.

        Only `answered` becomes a response. `completed`, `progressed` and the
        rest say something about the session, not about a question, and turning
        them into answers would invent evidence.
        """
        return self.verb_id == VERB_ANSWERED


def actor_key(child_id: uuid.UUID) -> str:
    """The pseudonym under which this child's statements are stored.

    Keyed with the application secret so that the pseudonym cannot be computed
    from a child identifier alone by anyone reading a database dump. Rotating
    the secret changes the pseudonym and breaks nothing: what links a statement
    to a child is the foreign key on the attempt, never this value.
    """
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        _ACTOR_NAMESPACE + str(child_id).encode("ascii"),
        sha256,
    ).hexdigest()


def pseudonymous_actor(key: str) -> dict[str, Any]:
    """The agent that replaces whatever the sender claimed."""
    return {
        "objectType": "Agent",
        "account": {"homePage": ACTOR_HOME_PAGE, "name": key},
    }


def parse(payload: Any, key: str) -> ParsedStatement:
    """Read an incoming statement, or refuse it and say why.

    The returned statement is the one that will be stored: same body, actor
    replaced. Refusals are `422` with a French message, as everywhere else.
    """
    if not isinstance(payload, dict):
        raise ValidationException(message="Un événement xAPI doit être un objet JSON")

    _refuse_if_too_large(payload)

    statement_id = _statement_id(payload)
    verb_id = _verb(payload)
    object_id = _object_id(payload)
    success, response = _result(payload)

    stored = dict(payload)
    # The claimed actor never survives this line, whatever it contained.
    stored["actor"] = pseudonymous_actor(key)

    return ParsedStatement(
        statement_id=statement_id,
        verb_id=verb_id,
        object_id=object_id,
        result_success=success,
        result_response=response,
        issued_at=_issued_at(payload),
        statement=stored,
    )


def _refuse_if_too_large(payload: dict[str, Any]) -> None:
    try:
        size = len(json.dumps(payload).encode("utf-8"))
    except (TypeError, ValueError) as error:
        raise ValidationException(
            message="Cet événement xAPI n’est pas sérialisable"
        ) from error
    if size > MAX_STATEMENT_BYTES:
        raise ValidationException(
            message=(
                "Cet événement xAPI est trop volumineux ; la limite est de "
                f"{MAX_STATEMENT_BYTES // 1024} kio"
            )
        )


def _statement_id(payload: dict[str, Any]) -> str:
    """The identifier that makes a replay recognisable.

    Required, and that is a deliberate demand on the sender. The alternative —
    minting one here — would make every retransmission a new event, and a child
    who answered once would be recorded as having answered twice. `play.html`
    stamps one when the content does not provide it.
    """
    raw = payload.get("id")
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationException(
            message="Cet événement xAPI n’a pas d’identifiant « id »"
        )
    value = raw.strip()
    if len(value) > MAX_STATEMENT_ID_LENGTH:
        raise ValidationException(
            message="L’identifiant de cet événement xAPI est trop long"
        )
    return value


def _verb(payload: dict[str, Any]) -> str:
    verb = payload.get("verb")
    raw = verb.get("id") if isinstance(verb, dict) else None
    if not isinstance(raw, str) or not raw:
        raise ValidationException(message="Cet événement xAPI n’a pas de verbe")
    if raw not in ALLOWED_VERBS:
        raise ValidationException(
            message="Ce verbe xAPI n’est pas accepté par la plateforme"
        )
    return raw


def _object_id(payload: dict[str, Any]) -> str:
    """How the content names what was interacted with.

    It becomes the `question_ref` of a response, so the two limits are checked
    together: an identifier the responses table could not hold would be stored
    in one place and lost in the other.
    """
    target = payload.get("object")
    raw = target.get("id") if isinstance(target, dict) else None
    if not isinstance(raw, str) or not raw:
        raise ValidationException(message="Cet événement xAPI ne nomme pas d’objet")
    if len(raw) > min(MAX_OBJECT_ID_LENGTH, MAX_QUESTION_REF_LENGTH):
        raise ValidationException(
            message="L’objet de cet événement xAPI porte un identifiant trop long"
        )
    return raw


def _result(payload: dict[str, Any]) -> tuple[bool | None, str | None]:
    """What the content concluded, if it concluded anything.

    `success` absent stays absent. A content that does not say whether an answer
    was right must not be made to say it — the same rule the declared path
    already follows, and the reason `is_correct` is nullable.
    """
    result = payload.get("result")
    if not isinstance(result, dict):
        return None, None

    success = result.get("success")
    if success is not None and not isinstance(success, bool):
        raise ValidationException(
            message="Le champ « result.success » doit être un booléen"
        )

    response = result.get("response")
    if response is not None and not isinstance(response, str):
        raise ValidationException(
            message="Le champ « result.response » doit être une chaîne"
        )
    if response is not None and len(response) > MAX_RESPONSE_LENGTH:
        raise ValidationException(
            message="La réponse portée par cet événement xAPI est trop longue"
        )

    return success, response


def _issued_at(payload: dict[str, Any]) -> datetime | None:
    """The moment the source claims, kept as a claim.

    An unreadable timestamp is dropped rather than refused: it is the sender's
    own account of time, it decides nothing here, and rejecting a whole
    observation over it would lose more than it protects.
    """
    raw = payload.get("timestamp")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
