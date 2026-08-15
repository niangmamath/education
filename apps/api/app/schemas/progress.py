"""What progress looks like on the wire.

No ratio, no percentage, no score, anywhere. The counts travel and whoever
displays them may divide them; the platform does not, because a number presented
as a level of mastery is exactly what a project rule forbids.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OutcomeCounts(BaseModel):
    """How many attempts concluded each of the three words, for one competency."""

    mastered: int = 0
    partial: int = 0
    not_mastered: int = 0


class CompetencyProgress(BaseModel):
    """Everything the completed attempts say about one competency."""

    competency_code: str
    # What the most recent completed attempt concluded. Not a summary of all of
    # them: a competency worked on again is meant to be read at its latest state.
    latest_outcome: str
    latest_at: datetime
    first_at: datetime
    attempts_counted: int
    outcomes: OutcomeCounts
    # The evidence, summed from the results themselves, as plain counts.
    answered_total: int
    correct_total: int
    # The same values, said in French, so that a parent can be shown a sentence
    # rather than a table.
    explanation: str


class ProgressEvidence(BaseModel):
    """How much of what was read came from where.

    Kept at the level of the child rather than of a competency, deliberately.
    Splitting it per competency would mean re-attributing yesterday's answers
    with today's mapping of questions to competencies, and the whole point of
    reading stored results rather than recomputing them is to avoid that.
    """

    statements_received: int = 0
    responses_declared: int = 0
    responses_from_runtime: int = 0


class ChildProgress(BaseModel):
    """One child's progress, computed at the moment it was asked for."""

    child_id: uuid.UUID
    attempts_completed: int
    competencies: list[CompetencyProgress] = Field(default_factory=list)
    evidence: ProgressEvidence
    # Nothing is stored, so this is the time of the reading and not of a
    # refresh. Two readings of the same facts give the same answer.
    computed_at: datetime
