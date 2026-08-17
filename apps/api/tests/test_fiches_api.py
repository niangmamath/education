"""Remediation sheets, through the real API.

The property tests next door check what the sheets *say*. These check what the
platform *does* with them, and one of them exists because of a door this feature
opened.

**The door.** A sheet and the assessment are graded by the same code, and a sheet
answers back with an explanation. If the sheet's route accepted any attempt, a
child could post her assessment answers to it and be told, one question at a
time, whether each was right — walking the exam that is supposed to measure her.
`test_an_assessment_attempt_is_refused_here` is the lock, and it is the reason
the route checks the activity's kind rather than trusting that clients call the
right endpoint.

Every address belongs to `example.com`, reserved by RFC 2606, and everything
built here carries a test prefix and is removed afterwards.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.main import app
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_KIND_REMEDIATION,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    ActivityQuestion,
    AuthoredQuestion,
)

TEST_CODE_PREFIX = "test-fiche-"
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"

GUIDANCE = (
    "Additionner, c’est avancer. Pour 8 + 5, pars de 8 et compte cinq pas de plus."
)
EXPLANATION = "Deux pas pour atteindre dix, puis il en reste quatre à ajouter."

MY_ACTIVITIES_URL = "/api/v1/me/activities"
FICHE_ANSWERS_URL = "/api/v1/me/fiches/attempts"
ASSESSMENT_ANSWERS_URL = "/api/v1/me/assessment/attempts"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


def _authored(session: Session, activity: Activity, questions: list[Any]) -> None:
    session.add(ActivityCompetency(activity_id=activity.id, competency_code=COMPETENCY))
    for position, (ref, prompt, choices, correct, explanation) in enumerate(
        questions, start=1
    ):
        session.add(
            AuthoredQuestion(
                activity_id=activity.id,
                position=position,
                question_ref=ref,
                prompt=prompt,
                choices=choices,
                correct_index=correct,
                explanation=explanation,
            )
        )
        session.add(
            ActivityQuestion(
                activity_id=activity.id, question_ref=ref, competency_code=COMPETENCY
            )
        )


@pytest.fixture
def catalogue(engine: Engine) -> Iterator[dict[str, str]]:
    """One sheet with a lesson and two questions, and one assessment beside it."""
    codes = {
        "fiche": f"{TEST_CODE_PREFIX}addition-{uuid.uuid4().hex[:8]}",
        "examen": f"{TEST_CODE_PREFIX}examen-{uuid.uuid4().hex[:8]}",
    }
    with Session(engine) as session:
        sheet = Activity(
            code=codes["fiche"],
            title="Additionner avec la bande numérique",
            kind=ACTIVITY_KIND_REMEDIATION,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=6,
            guidance=GUIDANCE,
        )
        exam = Activity(
            code=codes["examen"],
            title="Pour faire connaissance",
            kind=ACTIVITY_KIND_ASSESSMENT,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=5,
        )
        session.add_all([sheet, exam])
        session.flush()
        _authored(
            session,
            sheet,
            [
                ("fq1", "Combien font 8 + 6 ?", ["13", "14", "15"], 1, EXPLANATION),
                ("fq2", "Combien font 6 + 6 ?", ["11", "12", "13"], 1, "Un double."),
            ],
        )
        _authored(
            session,
            exam,
            [("eq1", "Combien font 2 + 2 ?", ["3", "4", "5"], 1, None)],
        )
        session.commit()

    yield codes

    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM assignments WHERE activity_id IN "
                "(SELECT id FROM catalog_activities WHERE code LIKE :p)"
            ),
            {"p": f"{TEST_CODE_PREFIX}%"},
        )
        connection.execute(
            text("DELETE FROM catalog_activities WHERE code LIKE :p"),
            {"p": f"{TEST_CODE_PREFIX}%"},
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


class Family:
    """A parent, one child, and the acts a sheet needs to be done."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"fiche-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Fiche",
            },
        )
        assert created.status_code == 201, created.text
        self.family_code = created.json()["family_code"]
        # Registering does not sign you in; creating a child needs a session.
        self.as_parent()
        self.pseudonym = f"lea{uuid.uuid4().hex[:6]}"
        child = client.post(
            "/api/v1/auth/children",
            json={"pseudonym": self.pseudonym, "pin": PIN, "display_name": "Léa"},
        )
        assert child.status_code == 201, child.text
        self.child_id = child.json()["id"]

    def as_parent(self) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )
        return self.client

    def as_child(self) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/child/login",
                json={
                    "family_code": self.family_code,
                    "pseudonym": self.pseudonym,
                    "pin": PIN,
                },
            ).status_code
            == 200
        )
        return self.client

    def give(self, activity_code: str) -> str:
        given = self.as_parent().post(
            "/api/v1/assignments",
            json={"child_id": self.child_id, "activity_code": activity_code},
        )
        assert given.status_code == 201, given.text
        return str(given.json()["id"])

    def open_attempt(self, assignment_id: str) -> str:
        child = self.as_child()
        assert (
            child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/start").status_code == 200
        )
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
        assert attempt.status_code == 201, attempt.text
        return str(attempt.json()["id"])


@pytest.fixture
def family(client: TestClient) -> Family:
    return Family(client)


class TestReadingASheet:
    def test_a_child_reads_the_sheet_she_was_given(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        assignment_id = family.give(catalogue["fiche"])

        body = (
            family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche").json()
        )

        assert body["title"] == "Additionner avec la bande numérique"
        assert len(body["questions"]) == 2

    def test_the_sheet_teaches_before_it_asks(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """The lesson is what separates a repair from a second test."""
        assignment_id = family.give(catalogue["fiche"])

        body = (
            family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche").json()
        )

        assert body["guidance"] == GUIDANCE

    def test_no_question_carries_its_answer(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """Absent by construction: the public model has no field for it."""
        assignment_id = family.give(catalogue["fiche"])

        body = (
            family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche").json()
        )

        for question in body["questions"]:
            assert set(question) == {"question_ref", "prompt", "choices"}

    def test_no_question_carries_its_explanation_either(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """An explanation handed over before the question is the answer, spelled
        out. It is said afterwards or not at all."""
        assignment_id = family.give(catalogue["fiche"])

        body = (
            family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche").json()
        )

        assert EXPLANATION not in str(body["questions"])

    def test_an_assessment_is_not_read_here(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """It is answered on its own route, which says nothing back."""
        assignment_id = family.give(catalogue["examen"])

        refused = family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche")

        assert refused.status_code == 404

    def test_another_family_sees_nothing(
        self, client: TestClient, catalogue: dict[str, str]
    ) -> None:
        theirs = Family(client)
        assignment_id = theirs.give(catalogue["fiche"])
        ours = Family(client)

        refused = ours.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche")

        assert refused.status_code == 404

    def test_a_parent_may_not_read_her_child_s_sheet(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """Not secrecy — the sheet is hers to see elsewhere — but this route
        answers for the child whose session made the request."""
        assignment_id = family.give(catalogue["fiche"])

        refused = family.as_parent().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche")

        assert refused.status_code in (401, 403)

    def test_a_sheet_already_finished_is_no_longer_open(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        assignment_id = family.give(catalogue["fiche"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/complete")

        refused = child.get(f"{MY_ACTIVITIES_URL}/{assignment_id}/fiche")

        assert refused.status_code == 404


class TestAnsweringASheet:
    def test_a_right_answer_is_said_to_be_right_and_explained(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        attempt_id = family.open_attempt(family.give(catalogue["fiche"]))

        body = family.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "fq1", "chosen_index": 1},
        )

        assert body.status_code == 201, body.text
        assert body.json() == {
            "question_ref": "fq1",
            "correct": True,
            "explanation": EXPLANATION,
        }

    def test_a_wrong_answer_gets_the_very_same_explanation(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """A sheet explains what is true; it does not comment on the child. Two
        sentences, one for success and one for failure, would make the wrong one
        a verdict."""
        attempt_id = family.open_attempt(family.give(catalogue["fiche"]))

        body = family.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "fq1", "chosen_index": 0},
        )

        assert body.status_code == 201, body.text
        assert body.json()["correct"] is False
        assert body.json()["explanation"] == EXPLANATION

    def test_the_answer_is_recorded_as_an_ordinary_response(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """The reading engine must see one shape and never learn that this
        activity was written here."""
        assignment_id = family.give(catalogue["fiche"])
        attempt_id = family.open_attempt(assignment_id)
        child = family.as_child()
        child.post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "fq1", "chosen_index": 1},
        )

        attempts = child.get(
            "/api/v1/me/attempts", params={"assignment_id": assignment_id}
        ).json()

        assert any(row["id"] == attempt_id for row in attempts)

    def test_a_choice_that_is_not_offered_is_refused(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        attempt_id = family.open_attempt(family.give(catalogue["fiche"]))

        refused = family.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "fq1", "chosen_index": 9},
        )

        assert refused.status_code == 409

    def test_a_question_from_another_activity_is_refused(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """An answer has to be an answer to something."""
        attempt_id = family.open_attempt(family.give(catalogue["fiche"]))

        refused = family.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "eq1", "chosen_index": 1},
        )

        assert refused.status_code == 404

    def test_an_assessment_attempt_is_refused_here(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """The door this feature opened, and the lock on it.

        Without the kind check, a child could post her assessment answers to the
        sheet's route and be told one at a time whether each was right — the exam
        walked through, by the endpoint that exists to help her.
        """
        attempt_id = family.open_attempt(family.give(catalogue["examen"]))

        refused = family.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "eq1", "chosen_index": 1},
        )

        assert refused.status_code == 409

    def test_the_assessment_route_still_says_nothing_back(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """The other half of the same rule: grading is shared, telling is not."""
        attempt_id = family.open_attempt(family.give(catalogue["examen"]))

        body = family.as_child().post(
            f"{ASSESSMENT_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "eq1", "chosen_index": 1},
        )

        assert body.status_code == 201, body.text
        assert "explanation" not in body.json()

    def test_a_stranger_cannot_answer(
        self, client: TestClient, catalogue: dict[str, str]
    ) -> None:
        theirs = Family(client)
        attempt_id = theirs.open_attempt(theirs.give(catalogue["fiche"]))
        ours = Family(client)

        refused = ours.as_child().post(
            f"{FICHE_ANSWERS_URL}/{attempt_id}/answers",
            json={"question_ref": "fq1", "chosen_index": 1},
        )

        assert refused.status_code == 404

    def test_a_request_without_a_session_is_refused(
        self, client: TestClient, catalogue: dict[str, str]
    ) -> None:
        assert (
            client.post(
                f"{FICHE_ANSWERS_URL}/{uuid.uuid4()}/answers",
                json={"question_ref": "fq1", "chosen_index": 1},
            ).status_code
            == 401
        )
