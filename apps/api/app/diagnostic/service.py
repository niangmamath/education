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

from sqlalchemy.ext.asyncio import AsyncSession

from app.assignments import service as assignments_service
from app.core.exceptions import ConflictException
from app.diagnostic import remediation, rules
from app.models.identity import Parent
from app.progress import service as progress_service
from app.referential import graph as referential_graph
from app.schemas.diagnostic import (
    AppliedRemediation,
    ChildDiagnostic,
    GeneralGap,
    Health,
    LocalizedGap,
    NextStep,
    NextSteps,
    Recommendation,
    RootCauseHypothesis,
)
from app.schemas.progress import CompetencyProgress

CHILD_NOT_FOUND_MESSAGE = "Ce profil enfant n’existe pas"

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
                # Named as a parent knows it when the edition in force can say
                # so. A sentence that reads "demo-num-compter" is addressed to
                # whoever wrote the catalogue, not to the person being shown it.
                explanation=rules.explain_gap(
                    reading, placed.label if placed else row.competency_code
                ),
                last_seen_at=row.latest_at,
            )
        )

    general = _general_gaps(gaps)
    observed = {row.competency_code for row in progress.competencies}
    root_causes = _root_causes(gaps, tree) + _unobserved_causes(gaps, tree, observed)
    _defer_behind_prerequisites(gaps, root_causes)

    return ChildDiagnostic(
        child_id=child_id,
        health=_health(progress.competencies),
        localized_gaps=gaps,
        general_gaps=general,
        root_causes=root_causes,
        recommendations=await remediation.quick_repairs(
            db, child_id, _targets(gaps, root_causes, observed)
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


async def apply_recommendations(
    db: AsyncSession, parent: Parent, child_id: uuid.UUID, limit: int | None = None
) -> AppliedRemediation:
    """Give the activities the platform proposes, on the parent's word.

    This is the "make it easier" half of the setting: a parent who agrees with
    the proposals should not have to retype them into the assignment form. It is
    still her act — she called this route — and it works in either mode.

    Refusals are collected rather than raised. A proposal already waiting for the
    child, or one over the ceiling of open assignments, is skipped and named; the
    others still go through. Failing the whole call because one of five was
    already given would be worse than useless.
    """
    diagnostic = await child_diagnostic(db, child_id)
    proposals = (
        diagnostic.recommendations[:limit] if limit else diagnostic.recommendations
    )

    assigned, skipped = await _give(db, parent, child_id, proposals)
    return AppliedRemediation(
        assigned=assigned, skipped=skipped, reason=_applied_reason(assigned, skipped)
    )


async def _give(
    db: AsyncSession,
    parent: Parent,
    child_id: uuid.UUID,
    proposals: Sequence[Recommendation],
) -> tuple[list[str], list[str]]:
    """Turn proposals into assignments, skipping the ones already refused."""
    assigned: list[str] = []
    skipped: list[str] = []
    for proposal in proposals:
        try:
            await assignments_service.assign_activity(
                db,
                parent,
                child_id,
                proposal.activity_code,
                note=_note(proposal),
            )
        except ConflictException:
            # Already waiting for her, or the ceiling of open assignments is
            # reached. Both are the platform being told no by rules that exist to
            # protect the child, and both are reported rather than forced.
            skipped.append(proposal.activity_code)
            continue
        assigned.append(proposal.activity_code)
    return assigned, skipped


def _note(proposal: Recommendation) -> str:
    """What the child is told about an activity her parent has just given her.

    A note in a child's own space should say something to her, not report a
    diagnosis: it names the work, never the difficulty behind it, for the same
    reason `child_next_steps` shows no gap.
    """
    return f"À faire quand tu veux, {proposal.duration_minutes} minutes."


def _applied_reason(assigned: list[str], skipped: list[str]) -> str:
    if not assigned and not skipped:
        return "Aucune remédiation à proposer pour l’instant."
    given = "activité donnée" if len(assigned) == 1 else "activités données"
    if not skipped:
        return f"{len(assigned)} {given}."
    return (
        f"{len(assigned)} {given}, {len(skipped)} écartée"
        f"{'s' if len(skipped) > 1 else ''} : déjà en attente, ou plafond "
        "d’activités en cours atteint."
    )


def _defer_behind_prerequisites(
    gaps: list[LocalizedGap], root_causes: list[RootCauseHypothesis]
) -> None:
    """Mark every gap that is waiting on a prerequisite gap of its own.

    This is the point of having a competency tree at all. Asking a child to
    secure her operations when the real trouble is counting, or to conjugate when
    she cannot yet tell the verb groups apart, makes her work on what buts rather
    than on what blocks — and settles neither. So while a prerequisite is itself
    a gap, the competency that depends on it is **not proposed at all**, not
    merely proposed second.

    The gap stays listed, with `blocked_by` and a sentence saying what it waits
    on. A parent who sees a difficulty with no repair beside it must be told the
    silence is deliberate.

    Chains fall out of this on their own: with A required by B required by C, all
    three in gap, B is deferred behind A and C behind B, so only A is worked on.
    """
    blocking = {
        dependent: cause.competency_code
        for cause in root_causes
        for dependent in cause.explains_codes
    }
    # Labels where the edition in force knows them, codes otherwise. `blocked_by`
    # keeps the code either way: it is an identifier a client joins on, and the
    # sentence beside it is what a person reads.
    named = {
        row.competency_code: row.competency_label or row.competency_code for row in gaps
    }
    for row in gaps:
        prerequisite = blocking.get(row.competency_code)
        if prerequisite is None:
            continue
        row.blocked_by = prerequisite
        row.deferral = rules.explain_deferral(
            named[row.competency_code], named.get(prerequisite, prerequisite)
        )


def _targets(
    gaps: list[LocalizedGap],
    causes: list[RootCauseHypothesis],
    observed: set[str],
) -> list[str]:
    """Quelles compétences proposer de travailler, et dans quel ordre.

    Deux sources, et la seconde est ce qui fait descendre la plateforme.

    Les lacunes que rien n'attend, d'abord : une lacune reportée n'apporte rien
    ici, c'est le sens même du report.

    Puis les **prérequis jamais observés**, qui ne sont pas des lacunes puisqu'ils
    n'ont aucune lecture, mais qui sont précisément là qu'il faut regarder. Ils
    passent devant : un prérequis de classe antérieure explique plus souvent la
    difficulté que la compétence où elle s'est manifestée.
    """
    unobserved = [
        cause.competency_code
        for cause in causes
        if cause.rule_code == rules.RULE_UNOBSERVED_PREREQUISITE
        and cause.competency_code not in observed
    ]
    return unobserved + [row.competency_code for row in gaps if row.blocked_by is None]


def _health(competencies: Sequence[CompetencyProgress]) -> Health | None:
    """The score, from the same readings the gaps were proposed from.

    Each competency is passed with the number of completed attempts it was read
    from, because that is what weights it.
    """
    reading = rules.health(
        [(row.latest_outcome, row.attempts_counted) for row in competencies]
    )
    if reading is None:
        return None
    return Health(
        score=reading.score,
        rule_code=reading.rule_code,
        observed=reading.observed,
        attempts=reading.attempts,
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


def _root_causes(gaps: list[LocalizedGap], tree: _Tree) -> list[RootCauseHypothesis]:
    """Which gaps are prerequisites of which other gaps.

    Only edges between two gaps count. A prerequisite that is mastered, or that
    nobody has worked on, explains nothing: the first is evidence against the
    hypothesis, and the second is no evidence at all.
    """
    named = {
        row.competency_code: row.competency_label or row.competency_code for row in gaps
    }
    in_gap = set(named)
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
            explanation=rules.explain_root_cause(
                named.get(cause, cause),
                [named.get(code, code) for code in sorted(dependents)],
            ),
        )
        for cause, dependents in sorted(explains.items())
    ]


def _unobserved_causes(
    gaps: list[LocalizedGap], tree: _Tree, observed: set[str]
) -> list[RootCauseHypothesis]:
    """Les prérequis dont la plateforme n'a aucune lecture, et qu'il faut regarder.

    C'est la descente vers les classes antérieures, et elle n'existait pas tant
    qu'il n'y avait qu'un seul examen. Un examen d'entrée ne porte que sur la
    classe déclarée ; un CM1 qui échoue en division n'a donc **aucune lecture**
    sur la multiplication du CE2, ni sur l'addition du CP. Sans cette règle, la
    plateforme constaterait l'échec et n'aurait rien à remonter.

    Ce n'est pas un constat de lacune, et la phrase produite le dit : rien n'a été
    observé, donc rien ne peut être affirmé. C'est une hypothèse sur l'endroit où
    chercher — et travailler ce prérequis produira la lecture qui manque, ce qui
    confirmera ou infirmera l'hypothèse. Une cause racine reste une hypothèse
    jusqu'à la réévaluation, exactement comme l'autre règle.
    """
    named = {
        row.competency_code: row.competency_label or row.competency_code for row in gaps
    }
    explains: dict[str, list[str]] = {}
    for row in gaps:
        for prerequisite in tree.prerequisites.get(row.competency_code, ()):
            if prerequisite not in observed:
                explains.setdefault(prerequisite, []).append(row.competency_code)

    return [
        RootCauseHypothesis(
            competency_code=cause,
            explains_codes=sorted(dependents),
            rule_code=rules.RULE_UNOBSERVED_PREREQUISITE,
            explanation=rules.explain_unobserved_prerequisite(
                tree.competencies[cause].label if cause in tree.competencies else cause,
                [named.get(code, code) for code in sorted(dependents)],
            ),
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

    Read through `app.referential.graph`, unscoped by class: a prerequisite of
    a localized gap can sit in any class, any subject — the seed data already
    has edges crossing both (ADR-019) — and the diagnostic must be able to
    name it wherever it is. Loading the whole graph rather than only `codes`
    and their immediate prerequisites is a superset of what the old, hand-rolled
    two-query version placed, and costs nothing worth avoiding at this scale:
    a school referential is dozens of rows, not thousands.
    """
    if not codes:
        return _Tree(True, {}, {})

    competency_graph = await referential_graph.load(db)
    if not competency_graph.nodes:
        return _Tree(False, {}, {})

    placed = {
        code: _Placed(node.label, node.domain_code, node.domain_label)
        for code, node in competency_graph.nodes.items()
    }
    return _Tree(True, placed, competency_graph.prerequisites)
