"""What a remediation sheet is allowed to be.

The assessment's items already have properties of this kind, and for a reason
worth repeating: its first draft asked "quelle lettre fait le son « mmm » ?",
spelling the answer three times in the prompt. A question that gives itself away
measures the ability to copy, and the reading it produces looks exactly like a
real one — so a child is told she has acquired something on the strength of
nothing.

A sheet can fail in every way the assessment can, plus two of its own.

**It can fail to teach.** A sheet with no lesson and no explanations is a second
test, handed to a child who has just been told she has a difficulty. That is the
one thing a repair must not be, so both are required here.

**It can fail to repair anything.** The diagnostic proposes a repair by looking
for an activity that works on the competency it wants repaired. A competency with
no sheet is a difficulty the platform can name and then do nothing about, which is
worse than not naming it.

None of these catches a bad question on its merits. They catch the mechanical
failures — the ones that slip through when somebody writes forty-eight items in
one sitting.
"""

from __future__ import annotations

import pytest

from app.demo.referentiel import COMPETENCIES
from app.demo.fiches import FICHES, Sheet, SheetQuestion
from app.models.catalog import MAX_DURATION_MINUTES, MIN_DURATION_MINUTES

QUESTIONS: list[tuple[str, SheetQuestion]] = [
    (sheet["code"], question) for sheet in FICHES for question in sheet["questions"]
]

# A Quick Repair lasts three to seven minutes. That is a product rule, narrower
# than what the catalogue's own constraint allows.
QUICK_REPAIR_MINUTES = range(3, 8)


def answer_of(question: SheetQuestion) -> str:
    return question["choices"][question["correct"]]


@pytest.mark.parametrize(
    ("code", "question"), QUESTIONS, ids=[f"{c}:{q['ref']}" for c, q in QUESTIONS]
)
class TestEveryQuestion:
    def test_does_not_contain_its_own_answer(
        self, code: str, question: SheetQuestion
    ) -> None:
        """The failure that made the assessment's first draft worthless.

        Single-character answers are skipped: a question about the letter S
        cannot avoid the letter s appearing somewhere, and refusing them would
        forbid asking about letters at all.
        """
        answer = answer_of(question).lower().strip(".")

        assert len(answer) < 2 or answer not in question["prompt"].lower()

    def test_offers_at_least_three_choices(
        self, code: str, question: SheetQuestion
    ) -> None:
        """Two choices make a coin toss look like a competency."""
        assert len(question["choices"]) >= 3

    def test_offers_no_two_identical_choices(
        self, code: str, question: SheetQuestion
    ) -> None:
        assert len(set(question["choices"])) == len(question["choices"])

    def test_points_at_one_of_its_choices(
        self, code: str, question: SheetQuestion
    ) -> None:
        assert 0 <= question["correct"] < len(question["choices"])

    def test_asks_something(self, code: str, question: SheetQuestion) -> None:
        assert "?" in question["prompt"]

    def test_explains_itself_afterwards(
        self, code: str, question: SheetQuestion
    ) -> None:
        """Without this, the sheet is a test wearing a repair's name."""
        assert question["explanation"].strip()

    def test_its_explanation_says_more_than_the_prompt(
        self, code: str, question: SheetQuestion
    ) -> None:
        """An explanation that repeats the question teaches nothing.

        The threshold is crude on purpose: it catches a placeholder left behind,
        not a weak sentence, and no cheap property could tell the difference.
        """
        assert len(question["explanation"]) > 40

    def test_its_explanation_does_not_address_the_child(
        self, code: str, question: SheetQuestion
    ) -> None:
        """A sheet explains what is true; it does not comment on her.

        The same sentence is shown whether she was right or wrong, so anything
        congratulating or consoling would be wrong half the time.
        """
        said = question["explanation"].lower()

        for judgement in ("bravo", "dommage", "tu t’es trompé", "bien joué", "raté"):
            assert judgement not in said


@pytest.mark.parametrize("sheet", FICHES, ids=lambda s: s["code"])
class TestEverySheet:
    def test_teaches_before_it_asks(self, sheet: Sheet) -> None:
        """The lesson is the difference between a repair and a second test."""
        assert len(sheet["guidance"].strip()) > 120

    def test_lasts_between_three_and_seven_minutes(self, sheet: Sheet) -> None:
        """A Quick Repair that runs long stops being one, and a child asked to
        sit down again after a difficulty will not sit for a quarter of an hour."""
        assert sheet["minutes"] in QUICK_REPAIR_MINUTES
        assert MIN_DURATION_MINUTES <= sheet["minutes"] <= MAX_DURATION_MINUTES

    def test_asks_at_least_three_questions(self, sheet: Sheet) -> None:
        """One right answer out of one is luck; the proof has to be worth something."""
        assert len(sheet["questions"]) >= 3

    def test_uses_each_question_reference_once(self, sheet: Sheet) -> None:
        """Two questions under one reference would be one answer overwriting the
        other, since a reading keeps the last response per question."""
        refs = [question["ref"] for question in sheet["questions"]]

        assert len(set(refs)) == len(refs)


class TestTheSheetsAsAWhole:
    def test_every_sheet_repairs_a_competency_the_referential_declares(self) -> None:
        """Une fiche qui vise un code inexistant ne réparerait rien du tout, et
        le diagnostic ne la proposerait jamais — une activité morte que personne
        ne verrait mourir."""
        declared = {row["code"] for row in COMPETENCIES}

        assert {sheet["competency"] for sheet in FICHES} <= declared

    def test_the_sheets_cover_the_competencies_they_are_written_for(self) -> None:
        """La couverture actuelle, épinglée pour qu'elle ne régresse pas en silence.

        Le référentiel couvre six classes et trois matières ; ces fiches-là
        couvrent les douze compétences que la première version du produit avait
        écrites, du CI au CE1, en français et en mathématiques seulement.
        **Les quarante-deux autres — dont les dix-huit d'anglais — n'ont pas
        encore de réparation**, et c'est la dette la mieux mesurée du projet :
        une lacune que la plateforme sait nommer et ne sait pas réparer est pire
        qu'une lacune dont elle ne parle pas, parce que le parent agit et il ne
        se passe rien.

        Ce test échoue dans les deux sens. Il échoue si une fiche disparaît, et
        il échoue quand de nouvelles fiches arrivent — auquel cas on relève le
        compte ici, délibérément, plutôt que de laisser la dette s'effacer sans
        que personne ne la voie diminuer.
        """
        repaired = {sheet["competency"] for sheet in FICHES}
        declared = {row["code"] for row in COMPETENCIES}

        assert len(repaired) == 12
        assert len(declared - repaired) == 42

    def test_no_competency_has_two_sheets(self) -> None:
        """The recommender proposes one repair per competency; a second sheet
        would make which one it picks depend on row order."""
        repaired = [sheet["competency"] for sheet in FICHES]

        assert len(set(repaired)) == len(repaired)

    def test_no_activity_code_is_used_twice(self) -> None:
        codes = [sheet["code"] for sheet in FICHES]

        assert len(set(codes)) == len(codes)

    def test_no_question_reference_is_shared_between_sheets(self) -> None:
        """Not required by the schema, which scopes a reference to its activity,
        but a shared reference makes a response ambiguous to read by eye."""
        refs = [ref for _, question in QUESTIONS for ref in (question["ref"],)]

        assert len(set(refs)) == len(refs)
