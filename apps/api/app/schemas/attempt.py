"""What an attempt and its reading look like on the wire.

A result never travels as a number. It carries the three-word outcome, the
counts it was read from, the rule that read them, and the sentence that says so
in French: a project rule asks that an automatic gap be an explainable
candidate, and an explanation computed at the moment of reading cannot drift
from the conclusion it explains.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.attempt import MAX_QUESTION_REF_LENGTH, MAX_RESPONSE_LENGTH


class ResponseRequest(BaseModel):
    """One answer as the client reports it."""

    model_config = ConfigDict(extra="forbid")

    question_ref: str = Field(min_length=1, max_length=MAX_QUESTION_REF_LENGTH)
    response: str | None = Field(default=None, max_length=MAX_RESPONSE_LENGTH)
    # Nullable on purpose: a content that does not judge an answer must not be
    # made to judge it.
    is_correct: bool | None = None


class ResponsePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_ref: str
    response: str | None
    is_correct: bool | None
    # Where it came from. `declared` means the browser reported its conclusion,
    # `xapi` that the server read the runtime's statement; it travels rather
    # than being hidden, because it is what decides between two accounts.
    source: str
    recorded_at: datetime


class ResultPublic(BaseModel):
    """A conclusion that can be shown, not merely asserted."""

    competency_code: str
    outcome: str
    answered: int
    correct: int
    rule_code: str
    explanation: str


class AttemptPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assignment_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: datetime | None
    responses: list[ResponsePublic] = Field(default_factory=list)
    results: list[ResultPublic] = Field(default_factory=list)


class RulePublic(BaseModel):
    """One reading rule, stated so it can be quoted rather than guessed."""

    code: str
    condition: str
    outcome: str
    description: str
