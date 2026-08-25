"""The assessment served palier by palier, through the real API.

ADR-021: an enfant is tested only on the competencies of her class whose
prerequisites, inside that same class, are already mastered. This is the one
place a real published referential and a real assessment `Activity` are put
together on purpose — every other assessment test uses a single, prerequisite-
free competency, which cannot exercise the gating this étape adds.

The edition already on the machine is stepped aside and put back, as
`test_diagnostic_api.py` already does; the assessment activity this module
creates is its own, torn down after.
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
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.referential.publication import publish
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-tiers-"
RUN = uuid.uuid4().hex[:8]

# B requires A, both in the same class: exactly the shape ADR-021 gates on.
COMP_A = f"{RUN}-num-a"
COMP_B = f"{RUN}-num-b"

PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSESSMENT_URL = "/api/v1/me/assessment"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"


def document(code: str) -> dict[str, Any]:
    return {
        "version": {"code": code, "label": "Édition des paliers"},
        "levels": [{"code": "cp", "label": "Cours préparatoire", "position": 1}],
        "subjects": [
            {
                "code": "math",
                "label": "Mathématiques",
                "position": 1,
                "domains": [
                    {"code": "math-num", "label": "Nombres et calcul", "position": 1}
                ],
            }
        ],
        "competencies": [
            _competency(COMP_A, position=1),
            _competency(COMP_B, position=2, prerequisites=[COMP_A]),
        ],
    }


def _competency(code: str, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "label": f"Compétence {code}",
        "description": None,
        "position": 1,
        "level": "cp",
        "domain": "math-num",
        "prerequisites": [],
    }
    payload.update(overrides)
    return payload


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def edition(engine: Engine) -> Iterator[None]:
    """An edition in force, and one assessment activity naming both A and B."""
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"

    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            reconcile(session, ReferentialDocument.model_validate(document(code)))
            publish(session, code)

            row = Activity(
                code=f"{TEST_CODE_PREFIX}exam-{uuid.uuid4().hex[:8]}",
                title="Pour faire connaissance",
                kind=ACTIVITY_KIND_ASSESSMENT,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=5,
                level_code="cp",
            )
            session.add(row)
            session.flush()
            for competency in (COMP_A, COMP_B):
                session.add(
                    ActivityCompetency(activity_id=row.id, competency_code=competency)
                )
                session.add(
                    AuthoredQuestion(
                        activity_id=row.id,
                        position=1,
                        question_ref=f"{competency}-q1",
                        prompt="Combien font 2 + 2 ?",
                        choices=["3", "4", "5"],
                        correct_index=1,
                    )
                )
                session.add(
                    ActivityQuestion(
                        activity_id=row.id,
                        question_ref=f"{competency}-q1",
                        competency_code=competency,
                    )
                )
            session.commit()

        yield

        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM assignments WHERE activity_id IN "
                    "(SELECT id FROM catalog_activities WHERE code LIKE :pattern)"
                ),
                {"pattern": f"{TEST_CODE_PREFIX}%"},
            )
            connection.execute(
                text("DELETE FROM catalog_activities WHERE code LIKE :pattern"),
                {"pattern": f"{TEST_CODE_PREFIX}%"},
            )


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


class Family:
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"tiers-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Paliers",
            },
        )
        assert created.status_code == 201
        self.family_code = created.json()["family_code"]

    def add_child(self, pseudonym: str) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )
        created = self.client.post(
            "/api/v1/auth/children",
            json={
                "pseudonym": pseudonym,
                "pin": PIN,
                "display_name": "Léa",
                "level_code": "cp",
            },
        )
        assert created.status_code == 201, created.text
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


def sit(session: TestClient) -> dict[str, Any]:
    return session.get(ASSESSMENT_URL).json()


def answer(session: TestClient, competency: str, *, correct: bool) -> None:
    body = sit(session)
    session.post(f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/start")
    attempt = session.post(
        f"{MY_ACTIVITIES_URL}/{body['assignment_id']}/attempts"
    ).json()
    session.post(
        f"{ASSESSMENT_URL}/attempts/{attempt['id']}/answers",
        json={
            "question_ref": f"{competency}-q1",
            "chosen_index": 1 if correct else 0,
        },
    )
    session.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")


class TestAPalierIsBoundedToWhatIsReady:
    def test_only_the_prerequisite_free_competency_is_served_first(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")

        body = sit(session)

        assert body["competency_codes"] == [COMP_A]
        refs = {row["question_ref"] for row in body["questions"]}
        assert refs == {f"{COMP_A}-q1"}

    def test_the_dependent_competency_is_served_once_the_prerequisite_is_mastered(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        answer(session, COMP_A, correct=True)

        body = sit(session)

        assert body["competency_codes"] == [COMP_B]
        refs = {row["question_ref"] for row in body["questions"]}
        assert refs == {f"{COMP_B}-q1"}

    def test_once_every_competency_is_tested_nothing_is_due(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        answer(session, COMP_A, correct=True)
        answer(session, COMP_B, correct=True)

        body = sit(session)

        assert body["done"] is True
        assert body["assignment_id"] is None
        assert body["questions"] == []

    def test_a_failed_prerequisite_leaves_the_dependent_out_of_any_sitting(
        self, family: Family, edition: None
    ) -> None:
        """A gap is remediation's business, not a fresh sitting to prepare."""
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        answer(session, COMP_A, correct=False)

        body = sit(session)

        assert body["done"] is True
        assert body["assignment_id"] is None
        assert body["questions"] == []
