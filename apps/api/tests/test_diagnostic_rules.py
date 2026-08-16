"""What the diagnostic rules are allowed to say, off the database.

These pin the decisions of 12.1 where they are made: what counts as a candidate
gap, what does not, and what the health score is and is not.
"""

from __future__ import annotations

from app.diagnostic import rules


class TestWhatIsACandidateGap:
    def test_not_mastered_is_one(self) -> None:
        reading = rules.read_gap(
            "not_mastered", attempts_counted=1, answered=4, correct=1
        )

        assert reading is not None
        assert reading.rule_code == rules.RULE_GAP_NOT_MASTERED

    def test_mastered_is_not_one(self) -> None:
        assert rules.read_gap("mastered", 3, 9, 9) is None

    def test_one_partial_is_not_one(self) -> None:
        """Halfway through learning something is not a difficulty."""
        assert (
            rules.read_gap("partial", attempts_counted=1, answered=4, correct=2) is None
        )

    def test_a_partial_that_survives_a_second_attempt_is_one(self) -> None:
        reading = rules.read_gap("partial", attempts_counted=2, answered=8, correct=4)

        assert reading is not None
        assert reading.rule_code == rules.RULE_GAP_PARTIAL_PERSISTS

    def test_a_gap_carries_the_counts_it_was_read_from(self) -> None:
        """A conclusion nobody can trace back is a verdict, not a candidate."""
        reading = rules.read_gap("not_mastered", 2, 8, 1)

        assert reading is not None
        assert (reading.attempts_counted, reading.answered, reading.correct) == (
            2,
            8,
            1,
        )


class TestTheSentencesSayWhatTheCountsSay:
    def test_a_gap_is_worded_as_a_candidate(self) -> None:
        reading = rules.read_gap("not_mastered", 1, 4, 1)

        assert reading is not None
        sentence = rules.explain_gap(reading, "cp-math-num-01")
        assert "cp-math-num-01" in sentence
        assert "4 réponses évaluées dont 1 juste" in sentence
        assert "à confirmer" in sentence

    def test_a_general_gap_says_the_localized_ones_remain(self) -> None:
        sentence = rules.explain_general_gap("Nombres et calcul", 3)

        assert "restent listées une par une" in sentence

    def test_a_root_cause_says_it_is_a_hypothesis(self) -> None:
        sentence = rules.explain_root_cause("cp-a", ["cp-b", "cp-c"])

        assert "hypothèse" in sentence
        assert "réévaluation" in sentence


class TestTheHealthScore:
    def test_nothing_observed_yields_no_score(self) -> None:
        """Zero would say the work went badly; nothing went at all."""
        assert rules.health(0, 0, 0) is None

    def test_everything_mastered_is_a_hundred(self) -> None:
        reading = rules.health(mastered=4, partial=0, not_mastered=0)

        assert reading is not None and reading.score == 100

    def test_nothing_mastered_is_zero(self) -> None:
        reading = rules.health(mastered=0, partial=0, not_mastered=3)

        assert reading is not None and reading.score == 0

    def test_in_progress_counts_half(self) -> None:
        reading = rules.health(mastered=1, partial=2, not_mastered=1)

        # (1 + 1 + 0) / 4
        assert reading is not None and reading.score == 50

    def test_every_term_travels_with_the_score(self) -> None:
        reading = rules.health(mastered=2, partial=1, not_mastered=1)

        assert reading is not None
        assert (
            reading.observed,
            reading.mastered,
            reading.partial,
            reading.not_mastered,
        ) == (
            4,
            2,
            1,
            1,
        )

    def test_the_sentence_refuses_comparison(self) -> None:
        reading = rules.health(1, 1, 1)

        assert reading is not None
        assert "ne compare cet enfant à personne" in rules.explain_health(reading)


class TestThePublishedRules:
    def test_every_rule_the_code_can_produce_is_published(self) -> None:
        """A rule a report cannot quote is a rule nobody can argue with."""
        published = {rule["code"] for rule in rules.published_rules()}

        assert published == {
            rules.RULE_GAP_NOT_MASTERED,
            rules.RULE_GAP_PARTIAL_PERSISTS,
            rules.RULE_GENERAL_GAP_SAME_DOMAIN,
            rules.RULE_ROOT_CAUSE_PREREQUISITE,
            rules.RULE_HEALTH_WEIGHTED,
        }

    def test_each_one_states_its_condition_and_what_it_produces(self) -> None:
        for rule in rules.published_rules():
            assert rule["condition"] and rule["produces"] and rule["description"]
