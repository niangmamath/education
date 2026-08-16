"""How a reading becomes a candidate gap, and how health is stated.

Dull arithmetic on counts, again, and again that is the requirement. Four
project rules meet in this file:

- *an automatic gap is an explainable candidate*, so nothing here concludes; it
  proposes, names the rule that proposed, and carries the counts it read;
- *a general gap groups localized gaps without removing them*, so grouping adds
  a second reading and never replaces the first;
- *a root cause stays a hypothesis until re-evaluation*, so nothing here is ever
  marked as established;
- *the academic health score must be explainable and non comparative*, so it is
  computed from published terms and compared to nothing.

There is no model here, opaque or otherwise, and no threshold anybody may turn.
As in `attempts/rules.py`, the rules are **published rather than configured**:
making them adjustable would mean deciding who may change what a difficulty is,
which is a decision and not a setting.

Nothing in this file decides **which** competencies a count covers, nor what a
gap should lead to. Those belong to `service.py` and `remediation.py`; keeping
them out is what lets these rules stay quotable as they are.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.models.attempt import OUTCOME_MASTERED, OUTCOME_NOT_MASTERED, OUTCOME_PARTIAL

# Named so a report can quote them and a test can pin them.
RULE_GAP_NOT_MASTERED: Final = "gap-not-mastered"
RULE_GAP_PARTIAL_PERSISTS: Final = "gap-partial-persists"
RULE_GENERAL_GAP_SAME_DOMAIN: Final = "general-gap-same-domain"
RULE_ROOT_CAUSE_PREREQUISITE: Final = "root-cause-prerequisite"
RULE_HEALTH_WEIGHTED: Final = "health-weighted-outcomes"

# One `partial` is not a difficulty: it is what learning something looks like on
# the way. It becomes a candidate gap when it survives a second attempt — the
# child came back to the same competency and it did not settle.
ATTEMPTS_BEFORE_PARTIAL_IS_A_GAP: Final = 2

# A general gap needs at least two localized ones to group. One gap in a domain
# is that gap, and calling it a pattern would be inventing one.
LOCALIZED_GAPS_FOR_A_GENERAL_GAP: Final = 2

# The terms of the health score, published so the number can be taken apart.
# A mastered competency counts whole, one in progress counts half, one not
# mastered counts nothing. There is no fourth weight: what was never observed is
# not in the score at all.
HEALTH_WEIGHTS: Final = {
    OUTCOME_MASTERED: 1.0,
    OUTCOME_PARTIAL: 0.5,
    OUTCOME_NOT_MASTERED: 0.0,
}


@dataclass(frozen=True)
class GapReading:
    """A candidate gap, the counts behind it, and the rule that proposed it."""

    rule_code: str
    outcome: str
    attempts_counted: int
    answered: int
    correct: int


@dataclass(frozen=True)
class HealthReading:
    """A health score and every term it was made of."""

    score: int
    rule_code: str
    observed: int
    mastered: int
    partial: int
    not_mastered: int


def read_gap(
    outcome: str, attempts_counted: int, answered: int, correct: int
) -> GapReading | None:
    """Propose a gap from what the completed attempts concluded, or propose none.

    `None` is a real answer and not a failure to decide. A mastered competency
    is not a gap; neither is a single `partial`, which is what progress looks
    like halfway. And a competency nobody has ever worked on does not reach this
    function at all — there is no reading to read, and filing a silence under
    "difficulty" would turn an absence into an accusation.
    """
    if outcome == OUTCOME_NOT_MASTERED:
        return GapReading(
            RULE_GAP_NOT_MASTERED, outcome, attempts_counted, answered, correct
        )
    if (
        outcome == OUTCOME_PARTIAL
        and attempts_counted >= ATTEMPTS_BEFORE_PARTIAL_IS_A_GAP
    ):
        return GapReading(
            RULE_GAP_PARTIAL_PERSISTS, outcome, attempts_counted, answered, correct
        )
    return None


def explain_gap(reading: GapReading, competency_code: str) -> str:
    """The sentence a parent should be able to be shown about a candidate gap."""
    tries = "tentative" if reading.attempts_counted == 1 else "tentatives"
    answers = "réponse évaluée" if reading.answered == 1 else "réponses évaluées"
    justes = "juste" if reading.correct == 1 else "justes"
    counted = (
        f"{reading.attempts_counted} {tries} terminée"
        f"{'s' if reading.attempts_counted > 1 else ''} sur « {competency_code} », "
        f"{reading.answered} {answers} dont {reading.correct} {justes}"
    )

    if reading.rule_code == RULE_GAP_NOT_MASTERED:
        return (
            f"{counted} : la dernière lecture la considère non acquise, "
            "c’est une lacune à confirmer."
        )
    return (
        f"{counted} : elle reste en cours d’acquisition après plusieurs "
        "tentatives, c’est une lacune à confirmer."
    )


def explain_general_gap(domain_label: str, count: int) -> str:
    """Why several localized gaps are also read together.

    The localized ones are not replaced by this reading. A project rule asks
    that a general gap group them **without removing them**, and both lists are
    returned side by side for exactly that reason.
    """
    return (
        f"{count} compétences de « {domain_label} » sont des lacunes à confirmer : "
        "elles sont regroupées ici parce qu’elles portent sur le même domaine, "
        "et elles restent listées une par une."
    )


def explain_root_cause(cause_code: str, dependent_codes: list[str]) -> str:
    """Why one gap may be underneath another, and why it stays a hypothesis."""
    dependents = ", ".join(f"« {code} »" for code in dependent_codes)
    plural = "elles" if len(dependent_codes) > 1 else "elle"
    return (
        f"« {cause_code} » est un prérequis de {dependents}, et {plural} "
        "présente aussi une lacune. Travailler le prérequis d’abord est une "
        "hypothèse, qui ne sera confirmée que par une réévaluation."
    )


def health(mastered: int, partial: int, not_mastered: int) -> HealthReading | None:
    """State academic health from the competencies actually observed.

    **Explainable**: the score is a weighted count divided by the number of
    observed competencies, and every term travels beside it. Anyone can redo the
    arithmetic.

    **Non comparative**: it is computed over what this child has worked on and
    nothing else. Not over the programme, which would read as "how far behind",
    and not against other children, which the platform never computes at all.

    **Not a mark on a competency**: it appears once, for a child, next to the
    full per-competency reading it summarises — never in place of one. A project
    rule says a mark never replaces a competency, and this is what keeps that
    true while still giving the parent the single view the product asks for.

    Nothing observed yields no score. There is deliberately no zero for it: zero
    would say the work went badly, and nothing went at all.
    """
    observed = mastered + partial + not_mastered
    if observed <= 0:
        return None

    weighted = (
        mastered * HEALTH_WEIGHTS[OUTCOME_MASTERED]
        + partial * HEALTH_WEIGHTS[OUTCOME_PARTIAL]
        + not_mastered * HEALTH_WEIGHTS[OUTCOME_NOT_MASTERED]
    )
    return HealthReading(
        score=round(weighted / observed * 100),
        rule_code=RULE_HEALTH_WEIGHTED,
        observed=observed,
        mastered=mastered,
        partial=partial,
        not_mastered=not_mastered,
    )


def explain_health(reading: HealthReading) -> str:
    """The sentence that takes the score apart, so it is never read alone."""
    observed = (
        "compétence observée" if reading.observed == 1 else "compétences observées"
    )
    return (
        f"{reading.observed} {observed} : {reading.mastered} acquise"
        f"{'s' if reading.mastered > 1 else ''}, {reading.partial} en cours "
        f"d’acquisition, {reading.not_mastered} non acquise"
        f"{'s' if reading.not_mastered > 1 else ''}. Le score résume ces comptes "
        "et ne compare cet enfant à personne."
    )


def published_rules() -> list[dict[str, str]]:
    """The rules, as they are meant to be shown and quoted.

    Exposed rather than made configurable, for the same reason as the reading
    rules of step 10: choosing the threshold at which a difficulty is named is a
    decision about what the platform says of a child, not a setting.
    """
    return [
        {
            "code": RULE_GAP_NOT_MASTERED,
            "condition": "la dernière lecture terminée conclut « non acquise »",
            "produces": "lacune localisée",
            "description": (
                "Une compétence lue comme non acquise est une lacune à "
                "confirmer, jamais un constat définitif."
            ),
        },
        {
            "code": RULE_GAP_PARTIAL_PERSISTS,
            "condition": (
                "la dernière lecture conclut « en cours d’acquisition » après au "
                f"moins {ATTEMPTS_BEFORE_PARTIAL_IS_A_GAP} tentatives terminées"
            ),
            "produces": "lacune localisée",
            "description": (
                "Une seule lecture intermédiaire n’est pas une difficulté : "
                "c’est ce à quoi ressemble un apprentissage en chemin. Elle le "
                "devient si elle ne se règle pas d’une tentative à l’autre."
            ),
        },
        {
            "code": RULE_GENERAL_GAP_SAME_DOMAIN,
            "condition": (
                f"au moins {LOCALIZED_GAPS_FOR_A_GENERAL_GAP} lacunes localisées "
                "portent sur le même domaine du référentiel"
            ),
            "produces": "lacune générale",
            "description": (
                "Le regroupement ajoute une lecture et n’en retire aucune : les "
                "lacunes localisées restent listées une par une."
            ),
        },
        {
            "code": RULE_ROOT_CAUSE_PREREQUISITE,
            "condition": (
                "une compétence en lacune est prérequis d’une autre compétence "
                "en lacune, dans l’édition du référentiel en vigueur"
            ),
            "produces": "hypothèse de cause racine",
            "description": (
                "Une cause racine reste une hypothèse jusqu’à la réévaluation. "
                "Elle propose par quoi commencer, elle n’explique rien de façon "
                "établie."
            ),
        },
        {
            "code": RULE_HEALTH_WEIGHTED,
            "condition": (
                "moyenne pondérée des compétences observées, une acquise comptant "
                "1, une en cours 0,5, une non acquise 0"
            ),
            "produces": "score de santé académique",
            "description": (
                "Calculé sur ce que l’enfant a travaillé, et sur rien d’autre : "
                "ni sur le programme, ni contre d’autres enfants. Il résume les "
                "lectures par compétence, il ne les remplace pas."
            ),
        },
    ]
