"""A course given alongside the palier it teaches, through the real API.

Étape 15, décisions du propriétaire du 26 août 2026: a course is given by the
platform at the same moment as the assessment behind the same competency,
never as a gate in front of it, and answering its questions must never touch
a competency reading — mastery stays entirely the assessment's to decide.

Same shape as `test_assessment_tiers.py`: B requires A, both in the same
class, so mastering the first palier is what makes the second one — and its
course — due.
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
    ACTIVITY_KIND_COURSE,
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

TEST_CODE_PREFIX = "test-course-tiers-"
RUN = uuid.uuid4().hex[:8]

COMP_A = f"{RUN}-num-a"
COMP_B = f"{RUN}-num-b"

PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSESSMENT_URL = "/api/v1/me/assessment"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"
NEXT_STEPS_URL = "/api/v1/me/next-steps"
PROGRESS_URL = "/api/v1/me/progress"


def document(code: str) -> dict[str, Any]:
    return {
        "version": {"code": code, "label": "Édition des cours"},
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


def _add_assessment(session: Session, run_id: str) -> None:
    row = Activity(
        code=f"{TEST_CODE_PREFIX}exam-{run_id}",
        title="Pour faire connaissance",
        kind=ACTIVITY_KIND_ASSESSMENT,
        status=ACTIVITY_STATUS_PUBLISHED,
        duration_minutes=5,
        level_code="cp",
    )
    session.add(row)
    session.flush()
    for competency in (COMP_A, COMP_B):
        session.add(ActivityCompetency(activity_id=row.id, competency_code=competency))
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


def _add_course(session: Session, competency: str) -> Activity:
    row = Activity(
        code=f"{TEST_CODE_PREFIX}cours-{competency}-{RUN}",
        title=f"Découvrir {competency}",
        kind=ACTIVITY_KIND_COURSE,
        status=ACTIVITY_STATUS_PUBLISHED,
        duration_minutes=10,
        guidance="Une leçon avant l’examen.",
    )
    session.add(row)
    session.flush()
    session.add(ActivityCompetency(activity_id=row.id, competency_code=competency))
    session.add(
        AuthoredQuestion(
            activity_id=row.id,
            position=1,
            question_ref=f"{competency}-check",
            prompt="As-tu compris la leçon ?",
            choices=["Oui", "Non"],
            correct_index=0,
            explanation="C’était bien ça.",
        )
    )
    return row


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def edition(engine: Engine) -> Iterator[None]:
    """An edition in force, an assessment, and a course for each competency."""
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"
    run_id = uuid.uuid4().hex[:8]

    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            reconcile(session, ReferentialDocument.model_validate(document(code)))
            publish(session, code)

            _add_assessment(session, run_id)
            _add_course(session, COMP_A)
            _add_course(session, COMP_B)
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
        self.email = f"course-tiers-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Cours",
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


def course_assignment(session: TestClient, competency: str) -> dict[str, Any] | None:
    """This child's open assignment for the course of one competency, if any."""
    for row in session.get(MY_ACTIVITIES_URL).json():
        if row["activity"]["kind"] != "course":
            continue
        if row["activity"]["code"] == f"{TEST_CODE_PREFIX}cours-{competency}-{RUN}":
            return row
    return None


class TestACourseIsGivenAlongsideItsPalier:
    def test_the_first_palier_s_course_is_given_at_the_same_time_as_its_exam(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")

        exam = sit(session)
        course = course_assignment(session, COMP_A)

        assert exam["competency_codes"] == [COMP_A]
        assert course is not None
        assert course["status"] == "assigned"

    def test_the_exam_is_sittable_without_ever_opening_the_course(
        self, family: Family, edition: None
    ) -> None:
        """Décision du propriétaire : le cours n'est pas une porte."""
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")

        answer(session, COMP_A, correct=True)

        assert sit(session)["competency_codes"] == [COMP_B]

    def test_the_second_palier_s_course_arrives_once_the_first_is_mastered(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        assert course_assignment(session, COMP_B) is None

        answer(session, COMP_A, correct=True)
        sit(session)

        course = course_assignment(session, COMP_B)
        assert course is not None
        assert course["status"] == "assigned"

    def test_a_competency_once_tested_is_not_given_a_course_again(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        answer(session, COMP_A, correct=True)
        answer(session, COMP_B, correct=True)

        sit(session)

        assert course_assignment(session, COMP_A) is not None
        assert course_assignment(session, COMP_B) is not None
        # Neither is re-given a second time: one row each.
        rows = [
            row
            for row in session.get(MY_ACTIVITIES_URL).json()
            if row["activity"]["kind"] == "course"
        ]
        assert len(rows) == 2


class TestACourseNeverAffectsMastery:
    def test_reading_and_answering_a_course_leaves_progress_untouched(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        sit(session)
        course = course_assignment(session, COMP_A)
        assert course is not None

        before = session.get(PROGRESS_URL).json()

        read = session.get(f"{MY_ACTIVITIES_URL}/{course['id']}/cours")
        assert read.status_code == 200
        assert read.json()["questions"], "a course must carry at least one check"

        session.post(f"{MY_ACTIVITIES_URL}/{course['id']}/start")
        feedback = session.post(
            f"/api/v1/me/cours/{course['id']}/answers",
            json={"question_ref": f"{COMP_A}-check", "chosen_index": 0},
        )
        assert feedback.status_code == 201
        assert feedback.json()["correct"] is True
        assert feedback.json()["explanation"]

        session.post(f"{MY_ACTIVITIES_URL}/{course['id']}/complete")

        after = session.get(PROGRESS_URL).json()
        # `computed_at` is a read-time timestamp and differs on every call by
        # construction; everything else must not have moved.
        assert {k: v for k, v in after.items() if k != "computed_at"} == {
            k: v for k, v in before.items() if k != "computed_at"
        }

    def test_a_course_is_never_proposed_as_a_quick_repair(
        self, family: Family, edition: None
    ) -> None:
        session = family.add_child(f"lea{uuid.uuid4().hex[:6]}")
        answer(session, COMP_A, correct=False)

        steps = session.get(NEXT_STEPS_URL).json()["steps"]

        assert all(step["kind"] != "course" for step in steps)
