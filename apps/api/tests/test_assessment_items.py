"""What an assessment item is allowed to be.

The first draft of the initiation assessment failed the most basic of these:
"quelle lettre fait le son « mmm » ?" spelled its answer three times in the
prompt, "dans quel mot entends-tu le son « ou » ?" offered *loup* with the
letters plainly visible, and the spelling item quoted the word already spelled
correctly.

Those measure the ability to copy, and that is worse than asking nothing: the
reading they produce looks exactly like a real one, so a child is told she has
acquired something on the strength of a question that gave itself away.

These are cheap properties and none of them catches a bad question on its
merits. They catch the mechanical failures, which are the ones that slip through
when somebody writes twelve items in one sitting.
"""

from __future__ import annotations

import pytest

from app.demo.dataset import ASSESSMENT, ExamQuestion, referential


def answer_of(question: ExamQuestion) -> str:
    return question["choices"][question["correct"]]


@pytest.mark.parametrize("question", ASSESSMENT, ids=lambda q: q["ref"])
class TestEveryItem:
    def test_does_not_contain_its_own_answer(self, question: ExamQuestion) -> None:
        """The failure that made the first draft worthless."""
        answer = answer_of(question).lower().strip(".")

        assert len(answer) < 2 or answer not in question["prompt"].lower()

    def test_offers_at_least_three_choices(self, question: ExamQuestion) -> None:
        """Two choices make a coin toss look like a competency."""
        assert len(question["choices"]) >= 3

    def test_offers_no_two_identical_choices(self, question: ExamQuestion) -> None:
        assert len(set(question["choices"])) == len(question["choices"])

    def test_points_at_one_of_its_choices(self, question: ExamQuestion) -> None:
        assert 0 <= question["correct"] < len(question["choices"])

    def test_asks_something(self, question: ExamQuestion) -> None:
        """A question mark somewhere, not necessarily at the end: a prompt may
        carry what it asks about after the question — seven stars to count, for
        instance — and reading better that way is not a defect."""
        assert "?" in question["prompt"]


class TestTheAssessmentAsAWhole:
    def test_every_competency_of_the_referential_is_asked_about(self) -> None:
        """A competency nobody asks about gets no reading, which is honest but
        useless in an assessment whose whole job is to start the journey."""
        asked = {question["competency"] for question in ASSESSMENT}
        declared = {row["code"] for row in referential()["competencies"]}

        assert declared == asked

    def test_no_question_reference_is_used_twice(self) -> None:
        """Two questions under one reference would be one answer overwriting
        another when the reading picks the last per question."""
        refs = [question["ref"] for question in ASSESSMENT]

        assert len(set(refs)) == len(refs)
