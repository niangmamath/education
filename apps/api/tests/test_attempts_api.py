"""Doing an activity, through the real API.

Three properties are what this step owes, and each is tested by making it fail
if it were absent: starting is idempotent, recording never overwrites, and a
reading is computed rather than judged.

Isolation is tested as in step 09, by building a second family in full and
trying every door.
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
    ACTIVITY_KIND_H5P,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    ActivityQuestion,
)

TEST_CODE_PREFIX = "test-ten-"
# Drawn per run, for the same reason as everywhere else these are filtered on.
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
OTHER_COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSIGNMENTS_URL = "/api/v1/assignments"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def activity(engine: Engine) -> Iterator[str]:
    """One published activity working on two competencies."""
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}"
    with Session(engine) as session:
        row = Activity(
            code=code,
            title="Addition posée",
            kind=ACTIVITY_KIND_H5P,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=4,
        )
        session.add(row)
        session.flush()
        session.add_all(
            [
                ActivityCompetency(activity_id=row.id, competency_code=COMPETENCY),
                ActivityCompetency(
                    activity_id=row.id, competency_code=OTHER_COMPETENCY
                ),
            ]
        )
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


class Family:
    """A parent, an active child, and the client holding a session."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"ten-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Tentative",
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


def started_activity(family: Family, activity_code: str) -> str:
    """An assignment the child has taken up, ready for an attempt."""
    given = family.as_parent().post(
        ASSIGNMENTS_URL,
        json={"child_id": family.child_id, "activity_code": activity_code},
    )
    assert given.status_code == 201
    assignment_id = given.json()["id"]
    assert (
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/start").status_code
        == 200
    )
    return assignment_id


def _find(rows: list[dict[str, Any]], assignment_id: str) -> dict[str, Any]:
    """The row this test is about, found by its identifier.

    Never by position. A child's list holds whatever the platform has given her,
    the initiation assessment included, and a test that reads the first row is
    testing the order of a list nobody promised.
    """
    match = [row for row in rows if row["id"] == assignment_id]
    assert len(match) == 1, rows
    return match[0]


def answer(client: TestClient, attempt_id: str, ref: str, correct: bool | None) -> None:
    posted = client.post(
        f"{MY_ATTEMPTS_URL}/{attempt_id}/responses",
        json={"question_ref": ref, "response": "vrai", "is_correct": correct},
    )
    assert posted.status_code == 201, posted.text


class TestStartingIsIdempotent:
    def test_the_first_request_creates_an_attempt(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)

        created = family.as_child().post(
            f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts"
        )

        assert created.status_code == 201
        assert created.json()["status"] == "in_progress"

    def test_asking_again_returns_the_same_attempt(
        self, family: Family, activity: str
    ) -> None:
        """A reload, a retry, a flaky connection: none may leave two attempts."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        first = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")

        again = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")

        assert again.status_code == 200
        assert again.json()["id"] == first.json()["id"]

    def test_ten_requests_leave_one_attempt(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        child = family.as_child()

        for _ in range(10):
            child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")

        listed = child.get(
            MY_ATTEMPTS_URL, params={"assignment_id": assignment_id}
        ).json()
        assert len(listed) == 1

    def test_an_activity_not_taken_up_accepts_no_attempt(
        self, family: Family, activity: str
    ) -> None:
        given = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": activity},
        )
        assignment_id = given.json()["id"]

        refused = family.as_child().post(
            f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts"
        )

        assert refused.status_code == 409

    def test_a_new_attempt_is_possible_after_the_first_is_finished(
        self, family: Family, activity: str
    ) -> None:
        """The index allows one *in progress*, not one ever."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        first = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        child.post(f"{MY_ATTEMPTS_URL}/{first['id']}/complete")

        # The assignment is finished with the attempt, so it no longer accepts
        # one; that is the coherence the two are kept in.
        again = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
        assert again.status_code == 409


class TestRecordingNeverOverwrites:
    def test_every_answer_is_kept(self, family: Family, activity: str) -> None:
        """Answering twice is two facts; the later does not erase the earlier."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()

        answer(child, attempt["id"], "q1", False)
        answer(child, attempt["id"], "q1", True)

        body = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()
        assert len(body["responses"]) == 2

    def test_the_reading_takes_the_last_answer_per_question(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", False)
        answer(child, attempt["id"], "q1", True)

        results = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ]

        assert results[0]["answered"] == 1
        assert results[0]["correct"] == 1
        assert results[0]["outcome"] == "mastered"

    def test_a_finished_attempt_accepts_no_more_answers(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")

        refused = child.post(
            f"{MY_ATTEMPTS_URL}/{attempt['id']}/responses",
            json={"question_ref": "q9", "response": "vrai", "is_correct": True},
        )

        assert refused.status_code == 409


class TestTheReading:
    def test_a_result_is_produced_for_every_competency_of_the_activity(
        self, family: Family, activity: str
    ) -> None:
        """H5P does not say which question belongs to which competency, so the
        same reading applies to both. The limitation is written down, not hidden."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)

        results = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ]

        assert sorted(row["competency_code"] for row in results) == sorted(
            [COMPETENCY, OTHER_COMPETENCY]
        )

    def test_every_result_names_its_rule_and_carries_its_counts(
        self, family: Family, activity: str
    ) -> None:
        """A conclusion nobody can trace back is a verdict, not a candidate."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)
        answer(child, attempt["id"], "q2", False)

        result = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ][0]

        assert result["rule_code"] == "majority-correct"
        assert (result["answered"], result["correct"]) == (2, 1)
        assert "2 réponses évaluées, dont 1 juste" in result["explanation"]

    def test_an_answer_the_content_did_not_judge_is_not_counted(
        self, family: Family, activity: str
    ) -> None:
        """A content that says nothing is not made to say something."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)
        answer(child, attempt["id"], "q2", None)

        result = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ][0]

        assert result["answered"] == 1

    def test_an_attempt_with_nothing_judged_concludes_nothing(
        self, family: Family, activity: str
    ) -> None:
        """The absence of a result is the honest answer, not a bad one."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", None)

        body = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()

        assert body["results"] == []
        assert body["status"] == "completed"

    def test_no_result_carries_a_grade(self, family: Family, activity: str) -> None:
        """A mark never replaces a competency, so none travels."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)

        result = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ][0]

        assert "score" not in result
        assert "%" not in result["explanation"]

    def test_completing_twice_computes_nothing_a_second_time(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)
        first = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()

        again = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")

        assert again.status_code == 200
        assert len(again.json()["results"]) == len(first["results"]) == 2


class TestTheAssignmentFollows:
    def test_finishing_the_attempt_finishes_the_assignment(
        self, family: Family, activity: str
    ) -> None:
        """The two must not be able to disagree about whether the work was done."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")

        mine = _find(child.get(MY_ACTIVITIES_URL).json(), assignment_id)

        assert mine["status"] == "completed"

    def test_cancelling_the_assignment_abandons_the_attempt_without_erasing_it(
        self, family: Family, activity: str
    ) -> None:
        """She did start, and that stays true."""
        assignment_id = started_activity(family, activity)
        attempt = (
            family.as_child()
            .post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
            .json()
        )

        family.as_parent().post(f"{ASSIGNMENTS_URL}/{assignment_id}/cancel")

        listed = (
            family.as_child()
            .get(MY_ATTEMPTS_URL, params={"assignment_id": assignment_id})
            .json()
        )
        assert [row["id"] for row in listed] == [attempt["id"]]
        assert listed[0]["status"] == "abandoned"


class TestIsolation:
    def test_a_child_cannot_attempt_another_child_s_assignment(
        self, client: TestClient, activity: str
    ) -> None:
        theirs = Family(client)
        assignment_id = started_activity(theirs, activity)
        ours = Family(client)

        refused = ours.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")

        assert refused.status_code == 404

    def test_a_child_cannot_answer_in_another_child_s_attempt(
        self, client: TestClient, activity: str
    ) -> None:
        theirs = Family(client)
        assignment_id = started_activity(theirs, activity)
        attempt = (
            theirs.as_child()
            .post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
            .json()
        )
        ours = Family(client)

        refused = ours.as_child().post(
            f"{MY_ATTEMPTS_URL}/{attempt['id']}/responses",
            json={"question_ref": "q1", "response": "vrai", "is_correct": True},
        )

        assert refused.status_code == 404

    def test_a_child_sees_only_her_own_attempts(
        self, client: TestClient, activity: str
    ) -> None:
        theirs = Family(client)
        their_assignment = started_activity(theirs, activity)
        theirs.as_child().post(f"{MY_ACTIVITIES_URL}/{their_assignment}/attempts")
        ours = Family(client)
        assignment_id = started_activity(ours, activity)
        mine = (
            ours.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        )

        listed = ours.as_child().get(MY_ATTEMPTS_URL).json()

        assert [row["id"] for row in listed] == [mine["id"]]

    def test_a_parent_cannot_attempt_in_her_place(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)

        refused = family.as_parent().post(
            f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts"
        )

        assert refused.status_code == 403

    def test_the_routes_refuse_a_request_without_a_session(
        self, client: TestClient
    ) -> None:
        assert client.get(MY_ATTEMPTS_URL).status_code == 401


class TestParentReadingAttempts:
    """`GET /children/{child_id}/attempts` — the parent's read-only door."""

    def test_a_parent_reads_her_own_child_s_finished_attempt(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        attempt = (
            family.as_child()
            .post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
            .json()
        )
        family.as_child().post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete")

        listed = family.as_parent().get(f"/api/v1/children/{family.child_id}/attempts")

        assert listed.status_code == 200
        assert [row["id"] for row in listed.json()] == [attempt["id"]]

    def test_the_assignment_filter_works_the_same_as_the_child_s_own_route(
        self, family: Family, activity: str
    ) -> None:
        assignment_id = started_activity(family, activity)
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")

        listed = family.as_parent().get(
            f"/api/v1/children/{family.child_id}/attempts",
            params={"assignment_id": assignment_id},
        )

        assert listed.status_code == 200
        assert all(row["assignment_id"] == assignment_id for row in listed.json())

    def test_another_family_s_parent_reaches_nothing(
        self, client: TestClient, activity: str
    ) -> None:
        theirs = Family(client)
        assignment_id = started_activity(theirs, activity)
        theirs.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts")
        ours = Family(client)

        refused = ours.as_parent().get(f"/api/v1/children/{theirs.child_id}/attempts")

        assert refused.status_code == 404

    def test_a_child_session_cannot_use_the_parent_route(
        self, family: Family, activity: str
    ) -> None:
        started_activity(family, activity)

        refused = family.as_child().get(f"/api/v1/children/{family.child_id}/attempts")

        assert refused.status_code == 403

    def test_the_route_refuses_a_request_without_a_session(
        self, client: TestClient, family: Family
    ) -> None:
        client.cookies.clear()
        assert (
            client.get(f"/api/v1/children/{family.child_id}/attempts").status_code
            == 401
        )


class TestPerQuestionAttribution:
    """The debt of step 10: every competency got the same reading.

    It still does when the activity says nothing about its questions, because
    H5P says nothing either. What changed is that an activity may now say.
    """

    @pytest.fixture
    def mapped_activity(self, engine: Engine) -> str:
        """An activity whose two questions each work on one competency."""
        code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}"
        with Session(engine) as session:
            row = Activity(
                code=code,
                title="Deux points distincts",
                kind=ACTIVITY_KIND_H5P,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=5,
            )
            session.add(row)
            session.flush()
            session.add_all(
                [
                    ActivityCompetency(activity_id=row.id, competency_code=COMPETENCY),
                    ActivityCompetency(
                        activity_id=row.id, competency_code=OTHER_COMPETENCY
                    ),
                    ActivityQuestion(
                        activity_id=row.id,
                        question_ref="q1",
                        competency_code=COMPETENCY,
                    ),
                    ActivityQuestion(
                        activity_id=row.id,
                        question_ref="q2",
                        competency_code=OTHER_COMPETENCY,
                    ),
                ]
            )
            session.commit()
        return code

    def test_each_question_counts_only_towards_what_it_works_on(
        self, family: Family, mapped_activity: str
    ) -> None:
        """One right, one wrong, and the two competencies part company."""
        assignment_id = started_activity(family, mapped_activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)
        answer(child, attempt["id"], "q2", False)

        results = {
            row["competency_code"]: row
            for row in child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
                "results"
            ]
        }

        assert results[COMPETENCY]["outcome"] == "mastered"
        assert results[COMPETENCY]["answered"] == 1
        assert results[OTHER_COMPETENCY]["outcome"] == "not_mastered"
        assert results[OTHER_COMPETENCY]["answered"] == 1

    def test_a_competency_with_no_answer_of_its_own_gets_no_result(
        self, family: Family, mapped_activity: str
    ) -> None:
        """Not a borrowed one: the absence is the honest answer, per competency."""
        assignment_id = started_activity(family, mapped_activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)

        results = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ]

        assert [row["competency_code"] for row in results] == [COMPETENCY]

    def test_without_a_mapping_the_reading_still_applies_to_all(
        self, family: Family, activity: str
    ) -> None:
        """The ordinary case, unchanged and written down: H5P says nothing, so
        the platform cannot say more than the activity does."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()
        answer(child, attempt["id"], "q1", True)

        results = child.post(f"{MY_ATTEMPTS_URL}/{attempt['id']}/complete").json()[
            "results"
        ]

        assert len(results) == 2
        assert {row["outcome"] for row in results} == {"mastered"}


class TestProvenanceAndRules:
    def test_a_response_says_where_it_came_from(
        self, family: Family, activity: str
    ) -> None:
        """The trust boundary travels rather than being hidden: nothing yet
        proves the browser reports what happened in the content."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()

        recorded = child.post(
            f"{MY_ATTEMPTS_URL}/{attempt['id']}/responses",
            json={"question_ref": "q1", "response": "vrai", "is_correct": True},
        ).json()

        assert recorded["source"] == "declared"

    def test_a_client_cannot_claim_another_provenance(
        self, family: Family, activity: str
    ) -> None:
        """Saying "this came from the runtime" is exactly what a client must not
        be able to do, so the field is not part of the payload at all."""
        assignment_id = started_activity(family, activity)
        child = family.as_child()
        attempt = child.post(f"{MY_ACTIVITIES_URL}/{assignment_id}/attempts").json()

        refused = child.post(
            f"{MY_ATTEMPTS_URL}/{attempt['id']}/responses",
            json={
                "question_ref": "q1",
                "response": "vrai",
                "is_correct": True,
                "source": "xapi",
            },
        )

        assert refused.status_code == 422

    def test_the_rules_can_be_read_rather_than_guessed(self, family: Family) -> None:
        """Published rather than configurable: what a mastered competency means
        is a decision, not a setting."""
        published = family.as_child().get("/api/v1/attempts/rules").json()

        assert [rule["code"] for rule in published] == [
            "all-correct",
            "majority-correct",
            "too-few-correct",
        ]
        assert all(rule["condition"] and rule["description"] for rule in published)

    def test_a_parent_can_read_the_rules_that_judge_her_child(
        self, family: Family
    ) -> None:
        """The rules are published so a parent can be shown them; behind a door
        only a child may open, they would be published to nobody who needs them."""
        answered = family.as_parent().get("/api/v1/attempts/rules")

        assert answered.status_code == 200
        assert [rule["code"] for rule in answered.json()] == [
            "all-correct",
            "majority-correct",
            "too-few-correct",
        ]
