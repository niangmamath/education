"""The initiation assessment, and the promise it has to keep.

One rule holds this together: **a child who can sign in has an assessment
waiting.** It is worth a test of its own because the first version broke it in
the least visible way — the assessment was given when a profile was *activated*,
which never happens for a profile a parent creates from her own space, since it
comes out usable. The path a parent is most likely to take was the one that led
to an empty dashboard.
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
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    ActivityQuestion,
    AuthoredQuestion,
)

TEST_CODE_PREFIX = "test-exam-"
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSESSMENT_URL = "/api/v1/me/assessment"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def assessment(engine: Engine) -> Iterator[str]:
    """One published assessment, two questions on one competency."""
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}"
    with Session(engine) as session:
        row = Activity(
            code=code,
            title="Pour faire connaissance",
            kind=ACTIVITY_KIND_ASSESSMENT,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=5,
        )
        session.add(row)
        session.flush()
        session.add(ActivityCompetency(activity_id=row.id, competency_code=COMPETENCY))
        for position, (ref, prompt, choices, correct) in enumerate(
            [
                ("q1", "Combien font 2 + 2 ?", ["3", "4", "5"], 1),
                ("q2", "Combien font 3 + 3 ?", ["6", "7"], 0),
            ],
            start=1,
        ):
            session.add(
                AuthoredQuestion(
                    activity_id=row.id,
                    position=position,
                    question_ref=ref,
                    prompt=prompt,
                    choices=choices,
                    correct_index=correct,
                )
            )
            session.add(
                ActivityQuestion(
                    activity_id=row.id, question_ref=ref, competency_code=COMPETENCY
                )
            )
        session.commit()

    yield code

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
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"exam-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Examen",
            },
        )
        assert created.status_code == 201
        self.family_code = created.json()["family_code"]
        self.as_parent()

    def as_parent(self) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )
        return self.client

    def add_child(self, pseudonym: str) -> dict[str, Any]:
        """A profile the parent opens herself: usable straight away."""
        created = self.as_parent().post(
            "/api/v1/auth/children",
            json={"pseudonym": pseudonym, "pin": PIN, "display_name": "Léa"},
        )
        assert created.status_code == 201, created.text
        return dict(created.json())

    def child_joins(self, pseudonym: str) -> dict[str, Any]:
        """A profile the child opens with the family code: it waits."""
        created = self.client.post(
            "/api/v1/auth/child/register",
            json={
                "family_code": self.family_code,
                "pseudonym": pseudonym,
                "pin": PIN,
                "display_name": "Tom",
            },
        )
        assert created.status_code == 201, created.text
        return dict(created.json())

    def as_child(self, pseudonym: str) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/child/login",
                json={
                    "family_code": self.family_code,
                    "pseudonym": pseudonym,
                    "pin": PIN,
                },
            ).status_code
            == 200
        )
        return self.client


@pytest.fixture
def family(client: TestClient) -> Family:
    return Family(client)


class TestEveryUsableProfileHasOneWaiting:
    """The rule, tested by both doors a profile can come through."""

    def test_a_profile_the_parent_opens_has_it(
        self, family: Family, assessment: str
    ) -> None:
        """The path that was broken: nothing is activated, so nothing gave it."""
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()

        assert body["assignment_id"] is not None
        assert body["done"] is False
        assert len(body["questions"]) == 2

    def test_a_profile_the_child_opens_has_it_once_accepted(
        self, family: Family, assessment: str
    ) -> None:
        child = family.child_joins(f"tom{uuid.uuid4().hex[:6]}")
        assert child["status"] == "pending"

        family.as_parent().post(f"/api/v1/auth/children/{child['id']}/activate")

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()
        assert body["assignment_id"] is not None

    def test_it_is_given_once_and_not_again(
        self, family: Family, assessment: str
    ) -> None:
        """Activating twice must not hand her a second copy."""
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        parent = family.as_parent()
        parent.post(f"/api/v1/auth/children/{child['id']}/deactivate")
        parent.post(f"/api/v1/auth/children/{child['id']}/activate")

        listed = family.as_child(child["pseudonym"]).get(MY_ACTIVITIES_URL).json()

        assert (
            len([row for row in listed if row["activity"]["kind"] == "assessment"]) == 1
        )


class TestTheAnswersStayOnTheServer:
    def test_a_question_travels_without_its_answer(
        self, family: Family, assessment: str
    ) -> None:
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()

        for question in body["questions"]:
            assert set(question) == {"question_ref", "prompt", "choices"}
        assert "correct" not in str(body)

    def test_the_server_decides_whether_an_answer_is_right(
        self, family: Family, assessment: str
    ) -> None:
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        session = family.as_child(child["pseudonym"])
        body = session.get(ASSESSMENT_URL).json()
        session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
        attempt = session.post(
            f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
        ).json()

        right = session.post(
            f"/api/v1/me/assessment/attempts/{attempt['id']}/answers",
            json={"question_ref": "q1", "chosen_index": 1},
        )
        wrong = session.post(
            f"/api/v1/me/assessment/attempts/{attempt['id']}/answers",
            json={"question_ref": "q2", "chosen_index": 1},
        )

        assert right.json()["is_correct"] is True
        assert wrong.json()["is_correct"] is False

    def test_a_question_from_elsewhere_is_refused(
        self, family: Family, assessment: str
    ) -> None:
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        session = family.as_child(child["pseudonym"])
        body = session.get(ASSESSMENT_URL).json()
        session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
        attempt = session.post(
            f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
        ).json()

        refused = session.post(
            f"/api/v1/me/assessment/attempts/{attempt['id']}/answers",
            json={"question_ref": "q-inventee", "chosen_index": 0},
        )

        assert refused.status_code == 404

    def test_a_choice_that_is_not_proposed_is_refused(
        self, family: Family, assessment: str
    ) -> None:
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        session = family.as_child(child["pseudonym"])
        body = session.get(ASSESSMENT_URL).json()
        session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
        attempt = session.post(
            f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
        ).json()

        refused = session.post(
            f"/api/v1/me/assessment/attempts/{attempt['id']}/answers",
            json={"question_ref": "q1", "chosen_index": 99},
        )

        assert refused.status_code == 409


class TestWhatItProduces:
    def test_finishing_it_reads_the_competency(
        self, family: Family, assessment: str
    ) -> None:
        """The whole point: a profile that started empty has a reading."""
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        session = family.as_child(child["pseudonym"])
        body = session.get(ASSESSMENT_URL).json()
        session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
        attempt = session.post(
            f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
        ).json()
        for ref, chosen in (("q1", 1), ("q2", 0)):
            session.post(
                f"/api/v1/me/assessment/attempts/{attempt['id']}/answers",
                json={"question_ref": ref, "chosen_index": chosen},
            )

        finished = session.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()

        reading = [
            row for row in finished["results"] if row["competency_code"] == COMPETENCY
        ]
        assert reading and reading[0]["outcome"] == "mastered"

    def test_once_done_it_is_not_offered_again(
        self, family: Family, assessment: str
    ) -> None:
        child = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        session = family.as_child(child["pseudonym"])
        body = session.get(ASSESSMENT_URL).json()
        session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
        attempt = session.post(
            f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
        ).json()
        session.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")

        again = session.get(ASSESSMENT_URL).json()

        assert again["done"] is True
        assert again["assignment_id"] is None
