"""How responses become a reading, by rules that can be shown.

Everything here is deliberately dull arithmetic on counts, and that is the
requirement rather than a limitation. Two project rules meet in this file:

- *a mark never replaces a competency*, so nothing produces a number to be read
  as a grade; the conclusion is one of three words, and the counts that led to
  it are kept beside it;
- *an automatic gap is an explainable candidate*, so every conclusion names the
  rule that produced it. A conclusion nobody can trace back is not a candidate,
  it is a verdict.

There is no model here, opaque or otherwise. A parent must be able to be told:
"she answered four questions on this competency, three were right, and the rule
that asks for everything to be right concluded that it is not yet mastered".
That sentence is the whole design.

The rules apply to **every competency the activity works on**, because H5P does
not say which question belongs to which competency. That is a real limitation
and it is written down rather than hidden: an activity attached to two
competencies produces the same reading for both.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.models.attempt import OUTCOME_MASTERED, OUTCOME_NOT_MASTERED, OUTCOME_PARTIAL

# Named so that a report can quote them and a test can pin them.
RULE_ALL_CORRECT: Final = "all-correct"
RULE_MAJORITY_CORRECT: Final = "majority-correct"
RULE_TOO_FEW_CORRECT: Final = "too-few-correct"

# Mastery asks for everything, because these are short activities on one point:
# getting most of a three-question exercise right is not mastering it. The
# middle band exists so that "nearly" is not filed with "not at all", which
# would tell a parent something false.
MASTERY_THRESHOLD: Final = 1.0
PARTIAL_THRESHOLD: Final = 0.5


@dataclass(frozen=True)
class Reading:
    """A conclusion, the counts behind it, and the rule that drew it."""

    outcome: str
    answered: int
    correct: int
    rule_code: str


def read_counts(answered: int, correct: int) -> Reading | None:
    """Conclude from two counts, and say by which rule — or conclude nothing.

    `answered` counts only the responses the content actually judged. A content
    that does not say whether an answer was right is not made to say it.

    **No evidence yields no reading at all**, and `None` says so. There is no
    outcome for it, deliberately: filing a silence under `not_mastered` would
    turn it into an accusation, and under `partial` into a claim that something
    was half done. Nothing was observed, so nothing is recorded, and the absence
    of a result is itself the honest answer.
    """
    if answered <= 0:
        return None

    ratio = correct / answered
    if ratio >= MASTERY_THRESHOLD:
        return Reading(OUTCOME_MASTERED, answered, correct, RULE_ALL_CORRECT)
    if ratio >= PARTIAL_THRESHOLD:
        return Reading(OUTCOME_PARTIAL, answered, correct, RULE_MAJORITY_CORRECT)
    return Reading(OUTCOME_NOT_MASTERED, answered, correct, RULE_TOO_FEW_CORRECT)


def explain(reading: Reading) -> str:
    """The sentence a parent should be able to be shown.

    It is built here, from the same values that were stored, so that the
    explanation cannot drift from the conclusion it explains.
    """
    answers = "réponse évaluée" if reading.answered == 1 else "réponses évaluées"
    correct = "juste" if reading.correct == 1 else "justes"
    counted = f"{reading.answered} {answers}, dont {reading.correct} {correct}"

    if reading.rule_code == RULE_ALL_CORRECT:
        return f"{counted} : tout est juste, la compétence est considérée acquise."
    if reading.rule_code == RULE_MAJORITY_CORRECT:
        return (
            f"{counted} : la majorité est juste, la compétence est considérée en "
            "cours d’acquisition."
        )
    return (
        f"{counted} : moins de la moitié est juste, la compétence est considérée "
        "non acquise."
    )
