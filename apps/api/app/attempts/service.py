"""Starting, resuming, recording and finishing an attempt.

Three properties are carried here, and each is worth naming.

**Starting is idempotent.** A child who reloads the page, or whose network
hiccups, must not end up with two attempts. Asking to start when one is already
running returns that one. The database guarantees it rather than the code: a
partial unique index allows a single attempt in progress per assignment, so two
requests arriving together cannot both win, and the loser is told about the
winner instead of failing.

**Recording never overwrites.** Every response is appended. A child who answers,
changes her mind and answers again has done two things; the reading takes her
last answer per question, the history keeps both.

**Where an answer came from outranks when it arrived.** Since step 11 the same
question may be described twice: once by the browser, which reports its own
conclusion, and once by the runtime, whose statement the server read itself.
Those are two accounts of one fact, not two facts, and the reading keeps the one
the server interpreted. Between two accounts of the same kind, the later still
wins — answering twice really is two answers.

**Finishing computes, it does not judge.** The rules of `rules.py` read counts
and name themselves. Nothing here decides anything a parent could not be shown.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.attempts import rules
from app.core.exceptions import ConflictException, NotFoundException
from app.models.assignment import (
    ASSIGNMENT_STATUS_COMPLETED,
    ASSIGNMENT_STATUS_IN_PROGRESS,
    Assignment,
)
from app.models.attempt import (
    ATTEMPT_STATUS_ABANDONED,
    ATTEMPT_STATUS_COMPLETED,
    ATTEMPT_STATUS_IN_PROGRESS,
    RESPONSE_SOURCE_DECLARED,
    RESPONSE_SOURCE_XAPI,
    Attempt,
    AttemptResponse,
    AttemptResult,
)
from app.models.catalog import Activity, ActivityCompetency, ActivityQuestion
from app.models.identity import Child

ATTEMPT_NOT_FOUND_MESSAGE = "Cette tentative n’existe pas"
ASSIGNMENT_NOT_OPEN_MESSAGE = (
    "Commencez l’activité avant d’en faire une tentative ; une activité terminée "
    "ou annulée n’en accepte plus"
)
ATTEMPT_CLOSED_MESSAGE = "Cette tentative est terminée"

_LOADED = (selectinload(Attempt.responses), selectinload(Attempt.results))


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def start_or_resume(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> tuple[Attempt, bool]:
    """The attempt under way for that assignment, starting one if there is none.

    Returns the attempt and whether it was created. Idempotent by design: a
    reload, a retry, a flaky connection must not leave two attempts behind.
    """
    assignment = await _own_assignment(db, child, assignment_id)
    if assignment.status != ASSIGNMENT_STATUS_IN_PROGRESS:
        raise ConflictException(message=ASSIGNMENT_NOT_OPEN_MESSAGE)

    running = await _running_attempt(db, assignment_id)
    if running is not None:
        return running, False

    attempt = Attempt(assignment_id=assignment.id)
    db.add(attempt)
    try:
        await db.flush()
    except IntegrityError:
        # Two requests arrived together and the index refused the second. The
        # loser is told about the winner rather than shown an error: from the
        # child's side, both asked the same thing and both get the same answer.
        await db.rollback()
        existing = await _running_attempt(db, assignment_id)
        if existing is None:
            raise
        return existing, False

    await db.refresh(attempt, ["responses", "results"])
    return attempt, True


async def record_response(
    db: AsyncSession,
    child: Child,
    attempt_id: uuid.UUID,
    question_ref: str,
    response: str | None,
    is_correct: bool | None,
) -> AttemptResponse:
    """Append one answer, marked as declared by the client.

    `source` says where it came from, and here it is always the browser: the
    client reports its own conclusion about what happened in the content. The
    runtime's own statements arrive by the xAPI route instead, and when the two
    describe the same question, `_prevailing` keeps the one the server read.
    """
    attempt = await own_attempt(db, child, attempt_id)
    if attempt.status != ATTEMPT_STATUS_IN_PROGRESS:
        raise ConflictException(message=ATTEMPT_CLOSED_MESSAGE)

    recorded = AttemptResponse(
        attempt_id=attempt.id,
        question_ref=question_ref,
        response=response,
        is_correct=is_correct,
        source=RESPONSE_SOURCE_DECLARED,
    )
    db.add(recorded)
    await db.flush()
    return recorded


async def complete(
    db: AsyncSession, child: Child, attempt_id: uuid.UUID
) -> tuple[Attempt, list[AttemptResult]]:
    """Close the attempt, read what it holds, and finish the assignment.

    Completing twice returns the same attempt and the same results rather than
    computing them again: an attempt is finished once, and a second request is
    the same request.
    """
    attempt = await own_attempt(db, child, attempt_id)
    if attempt.status == ATTEMPT_STATUS_COMPLETED:
        return attempt, list(attempt.results)
    if attempt.status == ATTEMPT_STATUS_ABANDONED:
        raise ConflictException(message=ATTEMPT_CLOSED_MESSAGE)

    results = await _compute_results(db, attempt)
    attempt.status = ATTEMPT_STATUS_COMPLETED
    attempt.completed_at = _now()

    assignment = await db.get(Assignment, attempt.assignment_id)
    if assignment is not None and assignment.status == ASSIGNMENT_STATUS_IN_PROGRESS:
        # Finishing the attempt is what finishes the assignment: the two would
        # otherwise be able to disagree about whether the work was done.
        assignment.status = ASSIGNMENT_STATUS_COMPLETED
        assignment.completed_at = attempt.completed_at

    await db.flush()
    return attempt, results


async def abandon_running_attempt(db: AsyncSession, assignment_id: uuid.UUID) -> None:
    """Close whatever was under way when an assignment is called off.

    The attempt is not deleted: she did start, and that stays true.
    """
    running = await _running_attempt(db, assignment_id)
    if running is not None:
        running.status = ATTEMPT_STATUS_ABANDONED
        await db.flush()


async def list_for_child(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID | None = None
) -> Sequence[Attempt]:
    statement = (
        select(Attempt)
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(Assignment.child_id == child.id)
        .order_by(Attempt.started_at.desc(), Attempt.id)
        .options(*_LOADED)
    )
    if assignment_id is not None:
        statement = statement.where(Attempt.assignment_id == assignment_id)
    rows = await db.scalars(statement)
    return rows.all()


async def _compute_results(db: AsyncSession, attempt: Attempt) -> list[AttemptResult]:
    """Read the responses through the rules, competency by competency.

    One answer per question is what counts, chosen by `_prevailing`, and only
    answers the content actually judged are counted at all: a content that says
    nothing about an answer is not made to say something.

    **How answers are attributed depends on what the activity declares.** If it
    maps its questions to competencies, each question counts only towards what it
    works on, and a competency with no question of its own gets no result rather
    than a borrowed one. If it declares no mapping — the ordinary case, since H5P
    itself says nothing about it — every competency of the activity gets the same
    reading, which is coarse but honest and is written down as such.
    """
    latest = _prevailing(attempt.responses)

    assignment = await db.get(Assignment, attempt.assignment_id)
    if assignment is None:
        return []

    codes = list(
        (
            await db.scalars(
                select(ActivityCompetency.competency_code)
                .join(Activity, Activity.id == ActivityCompetency.activity_id)
                .where(Activity.id == assignment.activity_id)
                .order_by(ActivityCompetency.competency_code)
            )
        ).all()
    )
    attribution = await _question_attribution(db, assignment.activity_id)

    results = []
    for code in codes:
        if attribution:
            judged = [
                row
                for ref, row in latest.items()
                if row.is_correct is not None and code in attribution.get(ref, ())
            ]
        else:
            judged = [row for row in latest.values() if row.is_correct is not None]

        reading = rules.read_counts(
            len(judged), sum(1 for row in judged if row.is_correct)
        )
        if reading is None:
            # No evidence for this competency yields no result for it. The
            # absence is the honest answer, and it is now per competency.
            continue

        result = AttemptResult(
            competency_code=code,
            outcome=reading.outcome,
            answered=reading.answered,
            correct=reading.correct,
            rule_code=reading.rule_code,
        )
        # Appended through the relationship rather than added with a foreign
        # key: the collection was loaded before this ran, and a row inserted
        # behind its back would leave the attempt in hand still showing none.
        attempt.results.append(result)
        results.append(result)
    await db.flush()
    return results


def _prevailing(responses: Sequence[AttemptResponse]) -> dict[str, AttemptResponse]:
    """The one answer per question the reading is entitled to use.

    Two rules, and the order between them is the decision of step 11.

    **A runtime statement outranks a declared answer**, whenever either arrived.
    Both reach the server through the same browser, so this is not a claim that
    one is harder to forge than the other; it is about who did the interpreting.
    A declared response is the client's own conclusion about what happened; an
    `xapi` response is the runtime's account, relayed as it stood and read by the
    server. When both describe the same question they are two accounts of one
    fact, and the one the server read itself is the one it keeps. Ordering it the
    other way round would let a client undo a runtime statement simply by posting
    its own afterwards.

    **Within one source, the later answer wins**, as before: a child who changes
    her mind has answered twice, and the second answer is the one that stands.
    """
    chosen: dict[str, AttemptResponse] = {}
    for row in sorted(responses, key=lambda item: item.recorded_at):
        held = chosen.get(row.question_ref)
        if held is None or _rank(row) >= _rank(held):
            chosen[row.question_ref] = row
    return chosen


def _rank(response: AttemptResponse) -> int:
    return 1 if response.source == RESPONSE_SOURCE_XAPI else 0


async def _question_attribution(
    db: AsyncSession, activity_id: uuid.UUID
) -> dict[str, set[str]]:
    """Which competencies each question of this activity works on, if declared."""
    rows = await db.execute(
        select(ActivityQuestion.question_ref, ActivityQuestion.competency_code).where(
            ActivityQuestion.activity_id == activity_id
        )
    )
    attribution: dict[str, set[str]] = {}
    for question_ref, competency_code in rows:
        attribution.setdefault(question_ref, set()).add(competency_code)
    return attribution


async def _running_attempt(
    db: AsyncSession, assignment_id: uuid.UUID
) -> Attempt | None:
    return await db.scalar(
        select(Attempt)
        .where(
            Attempt.assignment_id == assignment_id,
            Attempt.status == ATTEMPT_STATUS_IN_PROGRESS,
        )
        .options(*_LOADED)
    )


async def _own_assignment(
    db: AsyncSession, child: Child, assignment_id: uuid.UUID
) -> Assignment:
    assignment = await db.scalar(
        select(Assignment).where(
            Assignment.id == assignment_id, Assignment.child_id == child.id
        )
    )
    if assignment is None:
        raise NotFoundException(message=ATTEMPT_NOT_FOUND_MESSAGE)
    return assignment


async def running_attempt(db: AsyncSession, assignment_id: uuid.UUID) -> Attempt | None:
    """The attempt currently in progress for this assignment, if there is one.

    Public because a sheet reader needs to know whether one exists before it can
    draw a stable subset of questions for it — the same reason `own_attempt` is
    public: a second, private-only implementation of "which attempt is this"
    is a second chance to get it wrong.
    """
    return await _running_attempt(db, assignment_id)


async def own_attempt(db: AsyncSession, child: Child, attempt_id: uuid.UUID) -> Attempt:
    """One attempt of this child, or a refusal that says nothing more.

    Public because the initiation assessment needs the same check before it
    grades an answer, and a second implementation of "is this hers" is a second
    chance to get it wrong.
    """
    attempt = await db.scalar(
        select(Attempt)
        .join(Assignment, Assignment.id == Attempt.assignment_id)
        .where(Attempt.id == attempt_id, Assignment.child_id == child.id)
        .options(*_LOADED)
    )
    if attempt is None:
        raise NotFoundException(message=ATTEMPT_NOT_FOUND_MESSAGE)
    return attempt
