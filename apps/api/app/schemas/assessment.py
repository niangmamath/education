"""What an initiation assessment looks like on the wire.

The question and answer shapes are shared with the remediation sheets and live
in `app.schemas.authored`; what remains here is the one thing specific to the
assessment — whether a child has one waiting, and whether she has already been
through it.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.schemas.authored import AuthoredQuestionPublic

# Kept so callers may go on importing the request model from here; the assessment
# and the sheets send exactly the same payload to answer a question.
from app.schemas.authored import AuthoredAnswerRequest as AssessmentAnswerRequest

__all__ = ["AssessmentAnswerRequest", "AssessmentPublic", "AuthoredQuestionPublic"]


class AssessmentPublic(BaseModel):
    """The assessment waiting for a child, or the fact that none is.

    `done` and an empty list are not the same answer as `done: false` and an
    empty list: the first means she has been through it, the second that the
    platform has nothing published. A client shows different things for each.
    """

    done: bool
    assignment_id: uuid.UUID | None
    title: str | None
    questions: list[AuthoredQuestionPublic] = Field(default_factory=list)
