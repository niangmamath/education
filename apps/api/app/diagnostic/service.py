"""Building a diagnostic for one child, out of what is already recorded.

**Nothing new is measured here.** The diagnostic reads the progress of step 11,
which itself sums the results of step 10. Three layers, each reading the one
below and none re-deciding it: a gap proposed here can always be traced back to
an attempt, a rule and a set of counts. Recomputing the readings at this level
would let the same evidence say two different things depending on which route
was taken to it.

**Nothing is stored**, for the same reason as the progress of step 11: a stored
diagnostic is a fourth thing able to disagree with the three it came from, and
a stale gap is worse than no gap. It also makes *"a root cause stays a
hypothesis until re-evaluation"* true by construction — the hypothesis is
recomputed at every read, so a re-evaluation changes it the moment it lands.

**The competency tree is needed for grouping, not for gaps.** Localized gaps
only need competency codes, which the results carry. Grouping several gaps into
a general one, and proposing which gap sits underneath which, need the edition
in force. When there is none, the gaps are still reported and `tree_available`
says the rest is missing rather than absent — a short answer must not be read as
"no difficulty".
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.diagnostic import remediation, rules
from app.models.attempt import (
    OUTCOME_MASTERED,
    OUTCOME_NOT_MASTERED,
    OUTCOME_PARTIAL,
)
from app.models.referential import (
    VERSION_STATUS_PUBLISHED,
    Competency,
    CompetencyPrerequisite,
    Domain,
    ReferentialVersion,
)
from app.progress import service as progress_service
from app.schemas.diagnostic import (
    ChildDiagnostic,
    GeneralGap,
    Health,
    LocalizedGap,
    NextStep,
    NextSteps,
    RootCauseHypothesis,
)
from app.schemas.progress import CompetencyProgress

# How many things a child is shown at once. Enough to have a choice, few enough
# that the list is not a backlog: a screen of repairs reads as a punishment.
MAX_NEXT_STEPS = 3


async def child_diagnostic(db: AsyncSession, child_id: uuid.UUID) -> ChildDiagnostic:
    """Everything the platform proposes about one child, with its reasons."""
    progress = await progress_service.child_progress(db, child_id)

    tree = await _tree(db, [row.competency_code for row in progress.competencies])

    gaps = []
    for row in progress.competencies:
        reading = rules.read_gap(
            row.latest_outcome,
            row.attempts_counted,
            row.answered_total,
            row.correct_total,
        )
        if reading is None:
            continue
        placed = tree.competencies.get(row.competency_code)
        gaps.append(
            LocalizedGap(
                competency_code=row.competency_code,
                competency_label=placed.label if placed else None,
                domain_code=placed.domain_code if placed else None,
                domain_label=placed.domain_label if placed else None,
                outcome=reading.outcome,
                attempts_counted=reading.attempts_counted,
                answered=reading.answered,
                correct=reading.correct,
                rule_code=reading.rule_code,
                explanation=rules.explain_gap(reading, row.competency_code),
                last_seen_at=row.latest_at,
            )
        )

    general = _general_gaps(gaps)
    root_causes = _root_causes([row.competency_code for row in gaps], tree)

    return ChildDiagnostic(
        child_id=child_id,
        health=_health(progress.competencies),
        localized_gaps=gaps,
        general_gaps=general,
        root_causes=root_causes,
        recommendations=await remediation.quick_repairs(
            db, child_id, _targets(gaps, root_causes)
        ),
        tree_available=tree.available,
        computed_at=datetime.now(timezone.utc),
    )


async def child_next_steps(db: AsyncSession, child_id: uuid.UUID) -> NextSteps:
    """What the Élève space shows: things to do, never things to fix.

    The same engine produces both sides, and the difference is what crosses.
    A child is shown an activity and how long it takes. She is not shown that a
    competency was read as not acquired, nor a health score, nor the rule that
    named a difficulty — those are for the adult who can put them in context.
    That is not secrecy about her own work: her attempts and her progress remain
    hers to read. It is that a list of repairs, handed to a child as a diagnosis,
    is a judgement she has no way to answer.
    """
    diagnostic = await child_diagnostic(db, child_id)
    return NextSteps(
        steps=[
            NextStep(
                activity_code=row.activity_code,
                title=row.title,
                kind=row.kind,
                duration_minutes=row.duration_minutes,
            )
            for row in diagnostic.recommendations[:MAX_NEXT_STEPS]
        ],
        computed_at=diagnostic.computed_at,
    )


def _targets(
    gaps: list[LocalizedGap], root_causes: list[RootCauseHypothesis]
) -> list[str]:
    """Which competencies to propose work on, and in which order.

    Root-cause candidates first: if one gap may sit underneath another, starting
    with the one underneath is the whole point of having looked. The rest follow
    in the order they were read, which is the competency code order.
    """
    first = [row.competency_code for row in root_causes]
    return first + [
        row.competency_code for row in gaps if row.competency_code not in first
    ]


def _health(competencies: Sequence[CompetencyProgress]) -> Health | None:
    """The score, from the same readings the gaps were proposed from."""
    outcomes = [row.latest_outcome for row in competencies]
    reading = rules.health(
        mastered=sum(1 for row in outcomes if row == OUTCOME_MASTERED),
        partial=sum(1 for row in outcomes if row == OUTCOME_PARTIAL),
        not_mastered=sum(1 for row in outcomes if row == OUTCOME_NOT_MASTERED),
    )
    if reading is None:
        return None
    return Health(
        score=reading.score,
        rule_code=reading.rule_code,
        observed=reading.observed,
        mastered=reading.mastered,
        partial=reading.partial,
        not_mastered=reading.not_mastered,
        explanation=rules.explain_health(reading),
    )


def _general_gaps(gaps: list[LocalizedGap]) -> list[GeneralGap]:
    """Localized gaps read together when they share a domain.

    They are grouped, not consumed: every competency named here is also in the
    localized list, because a project rule asks that a general gap group them
    without removing them.
    """
    by_domain: dict[tuple[str, str], list[str]] = {}
    for row in gaps:
        if row.domain_code is None or row.domain_label is None:
            continue
        by_domain.setdefault((row.domain_code, row.domain_label), []).append(
            row.competency_code
        )

    grouped = []
    for (code, label), codes in sorted(by_domain.items()):
        if len(codes) < rules.LOCALIZED_GAPS_FOR_A_GENERAL_GAP:
            continue
        grouped.append(
            GeneralGap(
                domain_code=code,
                domain_label=label,
                competency_codes=sorted(codes),
                rule_code=rules.RULE_GENERAL_GAP_SAME_DOMAIN,
                explanation=rules.explain_general_gap(label, len(codes)),
            )
        )
    return grouped


def _root_causes(gap_codes: list[str], tree: _Tree) -> list[RootCauseHypothesis]:
    """Which gaps are prerequisites of which other gaps.

    Only edges between two gaps count. A prerequisite that is mastered, or that
    nobody has worked on, explains nothing: the first is evidence against the
    hypothesis, and the second is no evidence at all.
    """
    in_gap = set(gap_codes)
    explains: dict[str, list[str]] = {}
    for code in sorted(in_gap):
        for prerequisite in tree.prerequisites.get(code, ()):
            if prerequisite in in_gap:
                explains.setdefault(prerequisite, []).append(code)

    return [
        RootCauseHypothesis(
            competency_code=cause,
            explains_codes=sorted(dependents),
            rule_code=rules.RULE_ROOT_CAUSE_PREREQUISITE,
            explanation=rules.explain_root_cause(cause, sorted(dependents)),
        )
        for cause, dependents in sorted(explains.items())
    ]


class _Placed:
    """Where one competency sits in the edition in force."""

    __slots__ = ("label", "domain_code", "domain_label")

    def __init__(self, label: str, domain_code: str, domain_label: str) -> None:
        self.label = label
        self.domain_code = domain_code
        self.domain_label = domain_label


class _Tree:
    """The part of the competency tree these codes need, or nothing at all."""

    __slots__ = ("available", "competencies", "prerequisites")

    def __init__(
        self,
        available: bool,
        competencies: dict[str, _Placed],
        prerequisites: dict[str, list[str]],
    ) -> None:
        self.available = available
        self.competencies = competencies
        self.prerequisites = prerequisites


async def _tree(db: AsyncSession, codes: list[str]) -> _Tree:
    """Place these competency codes in the edition in force, if there is one.

    Read by code, as everywhere the rest of the platform meets the referential:
    ADR-013. A code the edition does not know is simply not placed — the
    catalogue may name a competency an older edition had, and losing the gap
    over it would be worse than reporting it unplaced.
    """
    if not codes:
        return _Tree(True, {}, {})

    version = await db.scalar(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    )
    if version is None:
        return _Tree(False, {}, {})

    rows = (
        await db.execute(
            select(
                Competency.id,
                Competency.code,
                Competency.label,
                Domain.code,
                Domain.label,
            )
            .join(Domain, Domain.id == Competency.domain_id)
            .where(
                Competency.version_id == version.id,
                Competency.code.in_(codes),
            )
        )
    ).all()

    placed = {
        code: _Placed(label, domain_code, domain_label)
        for _, code, label, domain_code, domain_label in rows
    }
    identifiers = {identifier: code for identifier, code, _, _, _ in rows}

    edges = (
        await db.execute(
            select(
                CompetencyPrerequisite.competency_id,
                CompetencyPrerequisite.prerequisite_id,
            ).where(
                CompetencyPrerequisite.version_id == version.id,
                CompetencyPrerequisite.competency_id.in_(list(identifiers)),
            )
        )
    ).all()

    prerequisites: dict[str, list[str]] = {}
    for competency_id, prerequisite_id in edges:
        # Only prerequisites that are themselves among the read competencies can
        # be named: the others carry no reading, so nothing could be said of them.
        code = identifiers.get(competency_id)
        required = identifiers.get(prerequisite_id)
        if code is not None and required is not None:
            prerequisites.setdefault(code, []).append(required)

    return _Tree(True, placed, prerequisites)
