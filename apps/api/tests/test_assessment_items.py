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

from app.demo.examens import EXAMS, ExamQuestion
from app.demo.referentiel import COMPETENCIES_BY_LEVEL, LEVEL_CODES

# Toutes les questions des six examens, chacune sachant de quel examen elle vient.
ASSESSMENT: list[ExamQuestion] = [q for exam in EXAMS for q in exam["questions"]]


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


class TestTheAssessmentsAsAWhole:
    @pytest.mark.parametrize("exam", EXAMS, ids=lambda e: e["level"])
    def test_an_exam_asks_about_every_competency_of_its_class_and_no_other(
        self, exam: dict[str, object]
    ) -> None:
        """Un examen d'entrée porte sur la classe déclarée, exactement.

        Une compétence de la classe que personne n'interroge ne reçoit aucune
        lecture — inutile pour un examen dont tout le rôle est de commencer le
        parcours. Une question qui porterait sur une autre classe, à l'inverse,
        produirait une lecture que l'élève n'avait aucune raison de subir.
        """
        questions = exam["questions"]
        assert isinstance(questions, list)
        asked = {question["competency"] for question in questions}
        declared = {row["code"] for row in COMPETENCIES_BY_LEVEL[str(exam["level"])]}

        assert asked == declared

    def test_there_is_exactly_one_exam_per_class(self) -> None:
        """Sans examen pour sa classe, un élève inscrit ne reçoit rien du tout."""
        assert [exam["level"] for exam in EXAMS] == list(LEVEL_CODES)

    def test_no_question_reference_is_used_twice(self) -> None:
        """Two questions under one reference would be one answer overwriting
        another when the reading picks the last per question."""
        refs = [question["ref"] for question in ASSESSMENT]

        assert len(set(refs)) == len(refs)

    @pytest.mark.parametrize("exam", EXAMS, ids=lambda e: e["level"])
    def test_an_exam_asks_exactly_three_questions_per_competency(
        self, exam: dict[str, object]
    ) -> None:
        """Une seule question par compétence ne rend qu'un verdict binaire.

        Avec trois lectures, `read_counts` peut rendre une compétence
        « partielle » (deux réponses sur trois) plutôt que de trancher entre
        acquis et non acquis sur un seul coup de dé.
        """
        questions = exam["questions"]
        assert isinstance(questions, list)
        counts: dict[str, int] = {}
        for question in questions:
            counts[question["competency"]] = counts.get(question["competency"], 0) + 1

        assert all(count == 3 for count in counts.values())
