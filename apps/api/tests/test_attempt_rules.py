"""The rules that turn counts into a reading.

No database and no API: these are the rules themselves, pinned. They are the
part of the platform a parent may one day argue with, so they must be readable
in isolation and impossible to change by accident.
"""

from __future__ import annotations

import pytest

from app.attempts.rules import (
    RULE_ALL_CORRECT,
    RULE_MAJORITY_CORRECT,
    RULE_TOO_FEW_CORRECT,
    Reading,
    explain,
    read_counts,
)
from app.models.attempt import (
    OUTCOME_MASTERED,
    OUTCOME_NOT_MASTERED,
    OUTCOME_PARTIAL,
)


class TestNoEvidence:
    def test_nothing_answered_yields_no_reading_at_all(self) -> None:
        """A silence is not a failure, and not a half-success either.

        Filing it under `not_mastered` would turn it into an accusation; under
        `partial`, into a claim that something was half done.
        """
        assert read_counts(answered=0, correct=0) is None


class TestConclusions:
    @pytest.mark.parametrize(
        ("answered", "correct", "outcome", "rule"),
        [
            (1, 1, OUTCOME_MASTERED, RULE_ALL_CORRECT),
            (4, 4, OUTCOME_MASTERED, RULE_ALL_CORRECT),
            (2, 1, OUTCOME_PARTIAL, RULE_MAJORITY_CORRECT),
            (4, 3, OUTCOME_PARTIAL, RULE_MAJORITY_CORRECT),
            (4, 2, OUTCOME_PARTIAL, RULE_MAJORITY_CORRECT),
            (4, 1, OUTCOME_NOT_MASTERED, RULE_TOO_FEW_CORRECT),
            (1, 0, OUTCOME_NOT_MASTERED, RULE_TOO_FEW_CORRECT),
            (3, 0, OUTCOME_NOT_MASTERED, RULE_TOO_FEW_CORRECT),
        ],
    )
    def test_the_bands_are_where_they_are_said_to_be(
        self, answered: int, correct: int, outcome: str, rule: str
    ) -> None:
        reading = read_counts(answered, correct)

        assert reading is not None
        assert reading.outcome == outcome
        assert reading.rule_code == rule

    def test_mastery_asks_for_everything(self) -> None:
        """These are short activities on one point: most of three is not mastery."""
        nearly = read_counts(answered=3, correct=2)

        assert nearly is not None
        assert nearly.outcome != OUTCOME_MASTERED

    def test_the_counts_are_carried_with_the_conclusion(self) -> None:
        """Without them the conclusion would be an assertion."""
        reading = read_counts(answered=4, correct=3)

        assert reading is not None
        assert (reading.answered, reading.correct) == (4, 3)


class TestExplanation:
    def test_every_conclusion_can_be_put_in_a_sentence(self) -> None:
        for answered, correct in ((1, 1), (4, 3), (4, 1)):
            reading = read_counts(answered, correct)
            assert reading is not None
            sentence = explain(reading)
            assert str(answered) in sentence
            assert str(correct) in sentence

    def test_the_sentence_agrees_with_the_conclusion(self) -> None:
        assert "acquise" in explain(Reading(OUTCOME_MASTERED, 2, 2, RULE_ALL_CORRECT))
        assert "en cours" in explain(
            Reading(OUTCOME_PARTIAL, 4, 3, RULE_MAJORITY_CORRECT)
        )
        assert "non acquise" in explain(
            Reading(OUTCOME_NOT_MASTERED, 4, 1, RULE_TOO_FEW_CORRECT)
        )

    def test_it_agrees_in_number(self) -> None:
        """Small thing, but it is shown to a parent."""
        one = explain(Reading(OUTCOME_MASTERED, 1, 1, RULE_ALL_CORRECT))
        many = explain(Reading(OUTCOME_MASTERED, 3, 3, RULE_ALL_CORRECT))

        assert "1 réponse évaluée, dont 1 juste" in one
        assert "3 réponses évaluées, dont 3 justes" in many

    def test_no_number_is_offered_as_a_grade(self) -> None:
        """A mark never replaces a competency, so none is produced."""
        reading = read_counts(answered=4, correct=3)

        assert reading is not None
        assert not hasattr(reading, "score")
        assert "75" not in explain(reading)
        assert "%" not in explain(reading)
