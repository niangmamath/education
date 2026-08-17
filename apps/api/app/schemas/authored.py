"""What an activity written by this platform looks like on the wire.

The correct answer is absent **by construction** rather than by filtering: there
is no field for it on the public question model, so no later edit can leak one
through this schema. The same trick the parent and child schemas already use for
password and PIN hashes.

The asymmetry between the two authored kinds lives here, and it is the whole
point of having two response shapes. A remediation sheet answers back — right or
wrong, and why — because that is what makes it teaching. The initiation
assessment does not, because telling a child the answer to a question that is
measuring her corrupts the reading being taken, and would let the exam be walked
through one question at a time.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class AuthoredQuestionPublic(BaseModel):
    """One question, as it is asked."""

    question_ref: str
    prompt: str
    choices: list[str]


class AuthoredAnswerRequest(BaseModel):
    """One answer: which question, and which choice.

    Never whether it was right. That is the server's to say, and a payload that
    offered to say it would be one forgotten check away from being believed.
    """

    model_config = ConfigDict(extra="forbid")

    question_ref: str = Field(min_length=1, max_length=200)
    chosen_index: int = Field(ge=0)


class FichePublic(BaseModel):
    """A remediation sheet, as a child meets it.

    `guidance` is what the sheet teaches before it asks anything. It comes first
    on purpose: a repair that opens with questions is a second test, and a child
    who has just been told she has a difficulty has no reason to sit another one.
    """

    assignment_id: uuid.UUID
    activity_code: str
    title: str
    guidance: str | None
    duration_minutes: int
    questions: list[AuthoredQuestionPublic] = Field(default_factory=list)


class AnswerFeedback(BaseModel):
    """What a sheet says back once a question has been answered.

    `explanation` is the question's own and does not change with what was
    answered: a sheet explains what is true, it does not comment on the child.
    """

    question_ref: str
    correct: bool
    explanation: str | None
