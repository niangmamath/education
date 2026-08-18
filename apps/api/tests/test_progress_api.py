"""Progress, read across attempts, by the child and by her parent.

What is pinned here is what the aggregation is allowed to be: a sum of readings
already written, never a fresh judgement; the latest word rather than an average;
no ratio anywhere; and the same shape on both sides of the family, with each side
able to reach only its own.

The prevalence between a declared answer and a runtime statement is tested here
too, because that decision is only visible once both have described the same
question.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.content.tokens import mint_ticket
from app.core.config import settings
from app.core.db import sync_database_url
from app.main import app
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.models.xapi import VERB_ANSWERED

TEST_CODE_PREFIX = "test-prog-"
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"
DIGEST = uuid.uuid4().hex + uuid.uuid4().hex

ASSIGNMENTS_URL = "/api/v1/assignments"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"
MY_PROGRESS_URL = "/api/v1/me/progress"
STATEMENTS_URL = "/api/v1/me/xapi/statements"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def activity(engine: Engine) -> Iterator[str]:
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}"
    with Session(engine) as session:
        row = Activity(
            code=code,
            title="Vrai ou faux",
            kind=ACTIVITY_KIND_H5P,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=4,
        )
        session.add(row)
        session.flush()
        session.add(ActivityCompetency(activity_id=row.id, competency_code=COMPETENCY))
        session.commit()

    yield code

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


@pytest.fixture
async def store() -> Any:
    connection = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield connection
    await connection.aclose()


class Family:
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"prog-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Progrès",
            },
        )
        assert created.status_code == 201
        self.family_code = created.json()["family_code"]
        self.as_parent()

        self.pseudonym = f"lea{uuid.uuid4().hex[:6]}"
        child = client.post(
            "/api/v1/auth/children",
            json={
                "pseudonym": self.pseudonym,
                "pin": PIN,
                "display_name": "Léa",
                "level_code": "cp",
            },
        )
        assert child.status_code == 201
        self.child_id = child.json()["id"]
        assert (
            client.post(f"/api/v1/auth/children/{self.child_id}/activate").status_code
            == 200
        )

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


@pytest.fixture
def family(client: TestClient) -> Family:
    return Family(client)


def new_attempt(family: Family, activity_code: str) -> tuple[str, str]:
    given = family.as_parent().post(
        ASSIGNMENTS_URL,
        json={"child_id": family.child_id, "activity_code": activity_code},
    )
    assert given.status_code == 201, given.text
    assignment_id = given.json()["id"]
    child = family.as_child()
    assert child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/start").status_code == 200
    attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
    assert attempt.status_code == 201, attempt.text
    return assignment_id, attempt.json()["id"]


def declare(
    client: TestClient, attempt_id: str, ref: str, correct: bool | None
) -> None:
    posted = client.post(
        f"{MY_ATTEMPTS_URL}/{attempt_id}/responses",
        json={"question_ref": ref, "response": "vrai", "is_correct": correct},
    )
    assert posted.status_code == 201, posted.text


def emit(client: TestClient, ticket: str, ref: str, success: bool) -> Any:
    return client.post(
        STATEMENTS_URL,
        json={
            "id": str(uuid.uuid4()),
            "verb": {"id": VERB_ANSWERED},
            "object": {"id": ref},
            "result": {"success": success, "response": "vrai"},
        },
        headers={"X-Content-Ticket": ticket},
    )


def finish(client: TestClient, attempt_id: str) -> Any:
    done = client.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete")
    assert done.status_code == 200, done.text
    return done.json()


def only(progress: dict[str, Any]) -> dict[str, Any]:
    """The one competency these tests work on, among whatever else exists."""
    matching = [
        row for row in progress["competencies"] if row["competency_code"] == COMPETENCY
    ]
    assert len(matching) == 1, progress["competencies"]
    return matching[0]


class TestARuntimeStatementOutranksADeclaredAnswer:
    async def test_the_runtime_wins_even_when_it_spoke_first(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = new_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        emit(child, ticket, "q1", success=False)
        declare(child, attempt_id, "q1", True)

        result = finish(child, attempt_id)["results"][0]
        assert result["correct"] == 0
        assert result["outcome"] == "not_mastered"

    async def test_the_runtime_wins_when_it_spoke_last_too(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = new_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        declare(child, attempt_id, "q1", False)
        emit(child, ticket, "q1", success=True)

        result = finish(child, attempt_id)["results"][0]
        assert result["correct"] == 1
        assert result["outcome"] == "mastered"

    async def test_both_answers_are_still_kept(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """One of them is not read; neither is erased."""
        assignment_id, attempt_id = new_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        emit(child, ticket, "q1", success=False)
        declare(child, attempt_id, "q1", True)

        assert len(finish(child, attempt_id)["responses"]) == 2

    def test_between_two_declared_answers_the_later_still_wins(
        self, family: Family, activity: str
    ) -> None:
        _, attempt_id = new_attempt(family, activity)
        child = family.as_child()

        declare(child, attempt_id, "q1", False)
        declare(child, attempt_id, "q1", True)

        assert finish(child, attempt_id)["results"][0]["correct"] == 1

    async def test_between_two_runtime_statements_the_later_wins(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = new_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        emit(child, ticket, "q1", success=False)
        emit(child, ticket, "q1", success=True)

        assert finish(child, attempt_id)["results"][0]["correct"] == 1


class TestProgressSumsWhatWasAlreadyRead:
    def test_a_child_with_no_finished_attempt_has_no_progress(
        self, family: Family, activity: str
    ) -> None:
        new_attempt(family, activity)

        body = family.as_child().get(MY_PROGRESS_URL).json()

        assert body["attempts_completed"] == 0
        assert not [
            row for row in body["competencies"] if row["competency_code"] == COMPETENCY
        ]

    def test_an_unfinished_attempt_never_counts(
        self, family: Family, activity: str
    ) -> None:
        """An attempt under way has concluded nothing, by construction."""
        _, first = new_attempt(family, activity)
        child = family.as_child()
        declare(child, first, "q1", True)
        finish(child, first)
        _, second = new_attempt(family, activity)
        declare(child, second, "q1", False)

        assert only(child.get(MY_PROGRESS_URL).json())["attempts_counted"] == 1

    def test_each_finished_attempt_adds_to_the_reading(
        self, family: Family, activity: str
    ) -> None:
        child = family.as_child()
        for correct in (False, True):
            _, attempt_id = new_attempt(family, activity)
            declare(family.as_child(), attempt_id, "q1", correct)
            finish(family.as_child(), attempt_id)

        row = only(child.get(MY_PROGRESS_URL).json())
        assert row["attempts_counted"] == 2
        assert row["outcomes"] == {"mastered": 1, "partial": 0, "not_mastered": 1}
        assert row["answered_total"] == 2
        assert row["correct_total"] == 1

    def test_the_latest_word_is_the_latest_and_not_an_average(
        self, family: Family, activity: str
    ) -> None:
        for correct in (False, True):
            _, attempt_id = new_attempt(family, activity)
            declare(family.as_child(), attempt_id, "q1", correct)
            finish(family.as_child(), attempt_id)

        row = only(family.as_child().get(MY_PROGRESS_URL).json())
        assert row["latest_outcome"] == "mastered"

    def test_no_ratio_travels_anywhere(self, family: Family, activity: str) -> None:
        """A mark never replaces a competency, so no number reads as one."""
        _, attempt_id = new_attempt(family, activity)
        declare(family.as_child(), attempt_id, "q1", True)
        finish(family.as_child(), attempt_id)

        row = only(family.as_child().get(MY_PROGRESS_URL).json())
        forbidden = {"score", "percentage", "ratio", "average", "moyenne", "note"}
        assert not forbidden & set(row)

    def test_the_explanation_says_what_the_counts_say(
        self, family: Family, activity: str
    ) -> None:
        _, attempt_id = new_attempt(family, activity)
        declare(family.as_child(), attempt_id, "q1", True)
        finish(family.as_child(), attempt_id)

        row = only(family.as_child().get(MY_PROGRESS_URL).json())
        assert "1 réponse évaluée dont 1 juste" in row["explanation"]
        assert "acquise" in row["explanation"]

    def test_reading_twice_gives_the_same_answer(
        self, family: Family, activity: str
    ) -> None:
        """Nothing is stored, so nothing can go stale or diverge."""
        _, attempt_id = new_attempt(family, activity)
        declare(family.as_child(), attempt_id, "q1", True)
        finish(family.as_child(), attempt_id)
        child = family.as_child()

        first = only(child.get(MY_PROGRESS_URL).json())
        again = only(child.get(MY_PROGRESS_URL).json())

        assert first == again


class TestProgressCountsWhereTheEvidenceCameFrom:
    async def test_both_doors_are_counted_apart(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = new_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()
        declare(child, attempt_id, "q1", True)
        emit(child, ticket, "q2", success=True)
        finish(child, attempt_id)

        evidence = child.get(MY_PROGRESS_URL).json()["evidence"]
        assert evidence["responses_declared"] == 1
        assert evidence["responses_from_runtime"] == 1
        assert evidence["statements_received"] == 1


class TestEachSideReachesOnlyItsOwn:
    def test_a_parent_reads_her_own_childs_progress(
        self, family: Family, activity: str
    ) -> None:
        _, attempt_id = new_attempt(family, activity)
        declare(family.as_child(), attempt_id, "q1", True)
        finish(family.as_child(), attempt_id)

        body = family.as_parent().get(f"/api/v1/children/{family.child_id}/progress")

        assert body.status_code == 200
        assert only(body.json())["latest_outcome"] == "mastered"

    def test_another_familys_child_does_not_exist(
        self, client: TestClient, activity: str
    ) -> None:
        first = Family(client)
        second = Family(client)

        refused = second.as_parent().get(f"/api/v1/children/{first.child_id}/progress")

        assert refused.status_code == 404

    def test_a_child_may_not_read_through_the_parent_route(
        self, family: Family, activity: str
    ) -> None:
        refused = family.as_child().get(f"/api/v1/children/{family.child_id}/progress")

        assert refused.status_code == 403

    def test_a_parent_may_not_read_through_the_child_route(
        self, family: Family, activity: str
    ) -> None:
        assert family.as_parent().get(MY_PROGRESS_URL).status_code == 403
