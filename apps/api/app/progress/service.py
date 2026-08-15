"""Gathering what many attempts said about one child.

Four decisions shape this file, and each is a choice that could have gone the
other way.

**Nothing is stored.** There is no aggregate table. Progress is computed from
the results and the events every time it is asked for, which is what makes it
*reproducible* in the sense the step asks: the same facts give the same answer,
and there is no fourth thing able to disagree with the three it was built from.
The cost is a few queries per read, on a family's worth of rows. If the
dashboards of step 13 ever need it cached, that will be a caching decision taken
in the open, not a silent duplication of the truth.

**Results are read, never recomputed.** The reading of an attempt was done when
it was completed, with the question-to-competency attribution as it stood then.
Recomputing here would apply today's attribution to yesterday's answers and
quietly change a conclusion a parent may already have been shown. So this file
sums results; it never touches the rules.

**Only completed attempts count.** An attempt under way has concluded nothing —
by construction, since results are written when it is completed — and an
abandoned one was called off. Counting either would report as progress something
that never happened.

**Nothing here diagnoses.** No gap is proposed, no remediation suggested, no
trend named. Those belong to step 12, and putting a first version of them here
would mean two places deciding what a difficulty is. What this returns is
description: the latest word, how often each was reached, and the counts behind
them.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.attempt import (
    ATTEMPT_STATUS_COMPLETED,
    OUTCOME_MASTERED,
    OUTCOME_NOT_MASTERED,
    OUTCOME_PARTIAL,
    RESPONSE_SOURCE_DECLARED,
    RESPONSE_SOURCE_XAPI,
    Attempt,
    AttemptResponse,
    AttemptResult,
)
from app.models.xapi import XapiStatement
from app.schemas.progress import (
    ChildProgress,
    CompetencyProgress,
    OutcomeCounts,
    ProgressEvidence,
)

_OUTCOME_WORDS = {
    OUTCOME_MASTERED: "acquise",
    OUTCOME_PARTIAL: "en cours d’acquisition",
    OUTCOME_NOT_MASTERED: "non acquise",
}


async def child_progress(db: AsyncSession, child_id: uuid.UUID) -> ChildProgress:
    """Everything the child's completed attempts say, competency by competency."""
    rows = (
        await db.scalars(
            select(AttemptResult)
            .join(Attempt, Attempt.id == AttemptResult.attempt_id)
            .join(Assignment, Assignment.id == Attempt.assignment_id)
            .where(
                Assignment.child_id == child_id,
                Attempt.status == ATTEMPT_STATUS_COMPLETED,
            )
            .order_by(AttemptResult.computed_at, AttemptResult.id)
        )
    ).all()

    grouped: dict[str, list[AttemptResult]] = {}
    for row in rows:
        grouped.setdefault(row.competency_code, []).append(row)

    competencies = [
        _competency(code, grouped[code]) for code in sorted(grouped, key=str.casefold)
    ]

    return ChildProgress(
        child_id=child_id,
        attempts_completed=await _completed_attempts(db, child_id),
        competencies=competencies,
        evidence=await _evidence(db, child_id),
        computed_at=datetime.now(timezone.utc),
    )


def _competency(code: str, results: list[AttemptResult]) -> CompetencyProgress:
    """One competency, read from the results already written about it.

    `results` arrives oldest first, so the last of them is the latest word.
    """
    counts = OutcomeCounts(
        mastered=sum(1 for row in results if row.outcome == OUTCOME_MASTERED),
        partial=sum(1 for row in results if row.outcome == OUTCOME_PARTIAL),
        not_mastered=sum(1 for row in results if row.outcome == OUTCOME_NOT_MASTERED),
    )
    latest = results[-1]
    answered = sum(row.answered for row in results)
    correct = sum(row.correct for row in results)

    return CompetencyProgress(
        competency_code=code,
        latest_outcome=latest.outcome,
        latest_at=latest.computed_at,
        first_at=results[0].computed_at,
        attempts_counted=len(results),
        outcomes=counts,
        answered_total=answered,
        correct_total=correct,
        explanation=_explain(len(results), answered, correct, latest.outcome),
    )


def _explain(attempts: int, answered: int, correct: int, outcome: str) -> str:
    """The sentence a parent should be able to be shown about a competency.

    Built from the same values that travel beside it, so it cannot say something
    the counts contradict. It reports and does not advise: what to do about a
    competency is step 12's subject, not this one's.
    """
    tries = "tentative" if attempts == 1 else "tentatives"
    answers = "réponse évaluée" if answered == 1 else "réponses évaluées"
    justes = "juste" if correct == 1 else "justes"
    return (
        f"{attempts} {tries} terminée{'s' if attempts > 1 else ''} sur cette "
        f"compétence, {answered} {answers} dont {correct} {justes} ; la dernière "
        f"lecture la considère {_OUTCOME_WORDS[outcome]}."
    )


async def _completed_attempts(db: AsyncSession, child_id: uuid.UUID) -> int:
    total = await db.scalar(
        select(func.count(Attempt.id))
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(
            Assignment.child_id == child_id,
            Attempt.status == ATTEMPT_STATUS_COMPLETED,
        )
    )
    return int(total or 0)


async def _evidence(db: AsyncSession, child_id: uuid.UUID) -> ProgressEvidence:
    """What arrived, and by which door.

    Counted over every attempt of the child and not only the completed ones:
    this describes what the platform received, which is true whether or not an
    attempt was ever finished.
    """
    by_source = await db.execute(
        select(AttemptResponse.source, func.count(AttemptResponse.id))
        .join(Attempt, Attempt.id == AttemptResponse.attempt_id)
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(Assignment.child_id == child_id)
        .group_by(AttemptResponse.source)
    )
    counts = {source: int(total) for source, total in by_source}

    statements = await db.scalar(
        select(func.count(XapiStatement.id))
        .join(Attempt, Attempt.id == XapiStatement.attempt_id)
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(Assignment.child_id == child_id)
    )

    return ProgressEvidence(
        statements_received=int(statements or 0),
        responses_declared=counts.get(RESPONSE_SOURCE_DECLARED, 0),
        responses_from_runtime=counts.get(RESPONSE_SOURCE_XAPI, 0),
    )
