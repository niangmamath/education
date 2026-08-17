"""What an initiation assessment looks like on the wire.

The correct answer is absent **by construction** rather than by filtering: there
is no field for it on the public model, so no later edit can leak one through
this schema. The same trick the parent and child schemas already use for
password and PIN hashes.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class AssessmentQuestionPublic(BaseModel):
    """One question, as it is asked."""

    question_ref: str
    prompt: str
    choices: list[str]


class AssessmentPublic(BaseModel):
    """The assessment waiting for a child, or the fact that none is.

    `done` and an empty list are not the same answer as `done: false` and an
    empty list: the first means she has been through it, the second that the
    platform has nothing published. A client shows different things for each.
    """

    done: bool
    assignment_id: uuid.UUID | None
    title: str | None
    questions: list[AssessmentQuestionPublic] = Field(default_factory=list)


class AssessmentAnswerRequest(BaseModel):
    """One answer: which question, and which choice.

    Never whether it was right. That is the server's to say, and a payload that
    offered to say it would be one forgotten check away from being believed.
    """

    model_config = ConfigDict(extra="forbid")

    question_ref: str = Field(min_length=1, max_length=200)
    chosen_index: int = Field(ge=0)
