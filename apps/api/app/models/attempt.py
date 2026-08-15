"""What a child actually did, and what was made of it.

Three tables, and the line between them is the point of the step.

An **attempt** is a fact: this child opened this activity at this moment and
later stopped. A **response** is a fact too: this answer was given to this
question at this moment. Neither says anything about mastery.

A **result** is an interpretation, and it is kept apart precisely because it is
one. It records which rule produced it and the counts it was produced from, so
that anyone can be shown why. A project rule says a mark never replaces a
competency and that an automatic gap is an explainable candidate; keeping the
facts and the reading of them in separate tables is what makes that possible
rather than merely stated.

Responses are **append-only**. A child who answers, changes her mind and answers
again has done two things, and the second does not erase the first: another
project rule says a new observation must never overwrite the history. The result
reads the last answer per question; the history keeps all of them.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Final

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.assignment import Assignment
from app.models.referential import CODE_LENGTH

ATTEMPT_STATUS_IN_PROGRESS: Final = "in_progress"
ATTEMPT_STATUS_COMPLETED: Final = "completed"
# Set when the assignment is called off under the child's feet. The attempt is
# not deleted: she did start, and that stays true.
ATTEMPT_STATUS_ABANDONED: Final = "abandoned"
ATTEMPT_STATUSES: Final = (
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_COMPLETED,
    ATTEMPT_STATUS_ABANDONED,
)

# What a rule concluded about one competency. Deliberately three words and not a
# number: a mark never replaces a competency.
OUTCOME_MASTERED: Final = "mastered"
OUTCOME_PARTIAL: Final = "partial"
OUTCOME_NOT_MASTERED: Final = "not_mastered"
OUTCOMES: Final = (OUTCOME_MASTERED, OUTCOME_PARTIAL, OUTCOME_NOT_MASTERED)

MAX_QUESTION_REF_LENGTH: Final = 200
MAX_RESPONSE_LENGTH: Final = 2000


class Attempt(Base):
    """One go at an assigned activity."""

    __tablename__ = "attempts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned')",
            name="ck_attempts_status",
        ),
        CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_attempts_completed_at",
        ),
        # One go at a time, and the database is what says so. Two requests to
        # start arriving together cannot both win: the second is refused by the
        # index rather than by a check that read the table a moment earlier.
        Index(
            "uq_attempts_one_in_progress",
            "assignment_id",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
        ),
        Index("ix_attempts_assignment", "assignment_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ATTEMPT_STATUS_IN_PROGRESS,
        server_default=ATTEMPT_STATUS_IN_PROGRESS,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    assignment: Mapped[Assignment] = relationship()
    responses: Mapped[list[AttemptResponse]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AttemptResponse.recorded_at",
    )
    results: Mapped[list[AttemptResult]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", passive_deletes=True
    )


class AttemptResponse(Base):
    """One answer, at one moment, to one question of the content.

    There is no unique key on the question: answering twice is two facts, and
    the later one does not replace the earlier. What the result reads is the
    last answer per question; what the history keeps is all of them.
    """

    __tablename__ = "attempt_responses"
    __table_args__ = (Index("ix_attempt_responses_attempt", "attempt_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    # How the content names the question. It comes from the content, so it is
    # stored as it arrives and never parsed for meaning.
    question_ref: Mapped[str] = mapped_column(
        String(MAX_QUESTION_REF_LENGTH), nullable=False
    )
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Nullable on purpose: a content that does not say whether an answer was
    # right must not be made to say it. An unknown is recorded as unknown.
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    attempt: Mapped[Attempt] = relationship(back_populates="responses")


class AttemptResult(Base):
    """What a rule concluded about one competency, and from what.

    The rule that produced it and the counts it read are stored beside the
    conclusion. Without them the conclusion would be an assertion; with them it
    can be shown, argued with, and recomputed.
    """

    __tablename__ = "attempt_results"
    __table_args__ = (
        CheckConstraint(
            "outcome IN ('mastered', 'partial', 'not_mastered')",
            name="ck_attempt_results_outcome",
        ),
        CheckConstraint(
            "answered >= 0 AND correct >= 0 AND correct <= answered",
            name="ck_attempt_results_counts",
        ),
        # One conclusion per competency per attempt: a second would be a
        # contradiction with no way to choose between them.
        Index(
            "uq_attempt_results_competency",
            "attempt_id",
            "competency_code",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    # By code, as everywhere the catalogue meets the referential: ADR-013.
    competency_code: Mapped[str] = mapped_column(String(CODE_LENGTH), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    # The evidence, as plain counts. No ratio is stored: a ratio is what someone
    # else may compute, not what was observed.
    answered: Mapped[int] = mapped_column(Integer, nullable=False)
    correct: Mapped[int] = mapped_column(Integer, nullable=False)
    # Which named rule concluded this, so that "why" has an answer.
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    attempt: Mapped[Attempt] = relationship(back_populates="results")
