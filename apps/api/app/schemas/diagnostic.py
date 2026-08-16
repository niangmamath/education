"""What a diagnostic and its recommendations look like on the wire.

Every conclusion travels with the rule that produced it and the counts it was
read from. A gap that arrived without them would be a verdict; with them it is
what the project asks for — an explainable candidate.

Two shapes leave this module, and they are deliberately not the same. The Parent
gets the diagnostic. The Élève gets actions, and no diagnostic vocabulary at
all: nothing here tells a child she has a gap.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LocalizedGap(BaseModel):
    """One competency proposed as a difficulty, and why."""

    competency_code: str
    # Filled from the edition in force when there is one. A gap is reported even
    # without it: the reading does not depend on the tree, only the grouping does.
    competency_label: str | None = None
    domain_code: str | None = None
    domain_label: str | None = None
    outcome: str
    attempts_counted: int
    answered: int
    correct: int
    rule_code: str
    explanation: str
    last_seen_at: datetime


class GeneralGap(BaseModel):
    """Several localized gaps in one domain, read together.

    The competencies it names are **also** in the localized list. A project rule
    asks that a general gap group them without removing them, and the two lists
    are returned side by side for that reason.
    """

    domain_code: str
    domain_label: str
    competency_codes: list[str]
    rule_code: str
    explanation: str


class RootCauseHypothesis(BaseModel):
    """One gap that may sit underneath others. Never more than a hypothesis."""

    competency_code: str
    # The gaps this one is a prerequisite of, and which it may explain.
    explains_codes: list[str]
    rule_code: str
    explanation: str
    # Always false. It is a field rather than an implication so that a client
    # cannot display the hypothesis as an established cause by omission.
    confirmed: bool = False


class Health(BaseModel):
    """The academic health score, and every term it was made of."""

    score: int
    rule_code: str
    observed: int
    mastered: int
    partial: int
    not_mastered: int
    explanation: str


class Recommendation(BaseModel):
    """One Quick Repair proposed for one competency."""

    competency_code: str
    activity_code: str
    title: str
    kind: str
    duration_minutes: int
    # True when this child has already completed this activity before. Proposed
    # anyway when nothing else fits, and said rather than hidden.
    already_done: bool
    # Why this one, in French, naming the competency it targets.
    reason: str
    # How the remediation will be proved. A project rule says every remediation
    # has a final proof, and this names it rather than assuming it.
    proof: str


class ChildDiagnostic(BaseModel):
    """What the platform proposes about one child, for her parent."""

    child_id: uuid.UUID
    # Absent when nothing has been observed. There is no zero for it: zero would
    # say the work went badly, and nothing went at all.
    health: Health | None = None
    localized_gaps: list[LocalizedGap] = Field(default_factory=list)
    general_gaps: list[GeneralGap] = Field(default_factory=list)
    root_causes: list[RootCauseHypothesis] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    # False when no edition of the referential is in force. Grouping and root
    # causes need the competency tree; the gaps themselves do not, and are
    # reported either way. Said explicitly so a short answer is not read as "no
    # difficulty".
    tree_available: bool = True
    computed_at: datetime


class NextStep(BaseModel):
    """One thing a child can do now.

    No gap, no score, no rule code. What a child is shown is an activity and how
    long it takes.
    """

    activity_code: str
    title: str
    kind: str
    duration_minutes: int


class NextSteps(BaseModel):
    """What the Élève space shows: things to do, not things to fix."""

    steps: list[NextStep] = Field(default_factory=list)
    computed_at: datetime


class DiagnosticRulePublic(BaseModel):
    """One diagnostic rule, stated so it can be quoted rather than guessed."""

    code: str
    condition: str
    produces: str
    description: str
