"""Assigning activities, through the real API and two real sessions.

Isolation is the point of this step, so most of what follows is about what a
family cannot see or do to another. A second family is built in full and used to
knock on every door.

Every address belongs to `example.com`, reserved by RFC 2606; every activity and
profile carries a test prefix and is removed afterwards.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import sync_database_url
from app.main import app
from app.models.assignment import MAX_OPEN_ASSIGNMENTS
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_STATUS_DRAFT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    H5PPackage,
)

TEST_CODE_PREFIX = "test-asg-"
PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSIGNMENTS_URL = "/api/v1/assignments"
MY_ACTIVITIES_URL = "/api/v1/me/activities"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def activities(engine: Engine) -> Iterator[dict[str, str]]:
    """Two published activities and one draft."""
    codes = {name: f"{TEST_CODE_PREFIX}{name}" for name in ("un", "deux", "brouillon")}
    with Session(engine) as session:
        session.add_all(
            [
                Activity(
                    code=codes["un"],
                    title="Addition posée",
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=4,
                ),
                Activity(
                    code=codes["deux"],
                    title="Soustraction posée",
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=6,
                ),
                Activity(
                    code=codes["brouillon"],
                    title="En préparation",
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_DRAFT,
                    duration_minutes=5,
                ),
            ]
        )
        session.commit()

    yield codes

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
def package_activity(engine: Engine, activities: dict[str, str]) -> str:
    """A published activity that really has a vetted package behind it."""
    code = f"{TEST_CODE_PREFIX}avecpaquet"
    with Session(engine) as session:
        activity = Activity(
            code=code,
            title="Vrai ou faux",
            kind=ACTIVITY_KIND_H5P,
            status=ACTIVITY_STATUS_PUBLISHED,
            duration_minutes=4,
        )
        session.add(activity)
        session.flush()
        session.add(
            H5PPackage(
                activity_id=activity.id,
                library_name="H5P.TrueFalse",
                library_version="1.8",
                object_key="packages/essai-affectation.h5p",
                sha256=uuid.uuid4().hex + uuid.uuid4().hex,
                size_bytes=4096,
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )
        )
        session.commit()
    return code


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


class Family:
    """A parent, one active child, and the client holding a session."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"asg-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Affectation",
            },
        )
        assert created.status_code == 201
        self.family_code = created.json()["family_code"]

        assert (
            client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )

        self.pseudonym = f"lea{uuid.uuid4().hex[:6]}"
        child = client.post(
            "/api/v1/auth/children",
            json={"pseudonym": self.pseudonym, "pin": PIN, "display_name": "Léa"},
        )
        assert child.status_code == 201
        self.child_id = child.json()["id"]
        assert (
            client.post(f"/api/v1/auth/children/{self.child_id}/activate").status_code
            == 200
        )

    def as_parent(self) -> TestClient:
        """Trade whatever session is held for this parent's."""
        assert (
            self.client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )
        return self.client

    def as_child(self) -> TestClient:
        """Trade whatever session is held for this child's.

        One client throughout: each `TestClient` runs its own event loop, and a
        second one nested inside the first leaves asyncpg holding sockets bound
        to a loop that is gone.
        """
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


def assign(family: Family, activity_code: str, **extra: object) -> dict:
    payload = {"child_id": family.child_id, "activity_code": activity_code}
    payload.update(extra)
    response = family.as_parent().post(ASSIGNMENTS_URL, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


class TestGivingAnActivity:
    def test_a_parent_gives_an_activity_to_their_child(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        body = assign(family, activities["un"], note="Trois minutes avant le dîner")

        assert body["status"] == "assigned"
        assert body["activity"]["code"] == activities["un"]
        assert body["child_pseudonym"] == family.pseudonym
        assert body["note"] == "Trois minutes avant le dîner"
        assert body["started_at"] is None

    def test_a_draft_activity_cannot_be_given(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """What is being prepared is not a parent's business either."""
        prepared = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={
                "child_id": family.child_id,
                "activity_code": activities["brouillon"],
            },
        )
        absent = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": "jamais-vue"},
        )

        assert prepared.status_code == absent.status_code == 404

    def test_the_same_activity_cannot_be_owed_twice_at_once(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        assign(family, activities["un"])

        again = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": activities["un"]},
        )

        assert again.status_code == 409

    def test_it_may_be_given_again_once_it_is_finished(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """Twice done and once done are different facts, so this is a second row."""
        first = assign(family, activities["un"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{first['id']}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{first['id']}/complete")

        second = assign(family, activities["un"])

        assert second["id"] != first["id"]
        # Two rows for the same activity: that is the claim. What else the child
        # holds is not part of it.
        assert set(
            only_ours(family.as_parent().get(ASSIGNMENTS_URL).json(), first, second)
        ) == {first["id"], second["id"]}


class TestFamilyIsolation:
    def test_a_parent_cannot_give_to_another_family_s_child(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        theirs = Family(client)
        ours = Family(client)

        refused = ours.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": theirs.child_id, "activity_code": activities["un"]},
        )

        assert refused.status_code == 404

    def test_a_parent_sees_only_their_own_assignments(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        theirs = Family(client)
        hers = assign(theirs, activities["un"])
        ours = Family(client)
        mine = assign(ours, activities["deux"])

        listed = [row["id"] for row in ours.as_parent().get(ASSIGNMENTS_URL).json()]

        # What isolation claims is that the other family is absent, not that the
        # list holds one row: her own child may also have what the platform gave.
        assert hers["id"] not in listed
        assert mine["id"] in listed

    def test_a_parent_cannot_cancel_another_family_s_assignment(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        """Refused exactly like one that does not exist, so nothing is revealed."""
        theirs = Family(client)
        stranger = assign(theirs, activities["un"])
        ours = Family(client)

        refused = ours.as_parent().post(f"{ASSIGNMENTS_URL}/{stranger['id']}/cancel")
        absent = ours.as_parent().post(f"{ASSIGNMENTS_URL}/{uuid.uuid4()}/cancel")

        assert refused.status_code == absent.status_code == 404

    def test_a_child_sees_only_what_she_was_given(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        theirs = Family(client)
        hers = assign(theirs, activities["un"])
        ours = Family(client)
        mine = assign(ours, activities["deux"])

        listed = [row["id"] for row in ours.as_child().get(MY_ACTIVITIES_URL).json()]

        assert hers["id"] not in listed
        assert mine["id"] in listed

    def test_a_child_cannot_start_another_child_s_activity(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        theirs = Family(client)
        stranger = assign(theirs, activities["un"])
        ours = Family(client)

        refused = ours.as_child().post(f"{MY_ACTIVITIES_URL}/{stranger['id']}/start")

        assert refused.status_code == 404


class TestSpacesDoNotMix:
    def test_a_child_cannot_give_herself_work(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        refused = family.as_child().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": activities["un"]},
        )

        assert refused.status_code == 403

    def test_a_parent_cannot_finish_the_activity_in_her_place(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])

        refused = family.as_parent().post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete")

        assert refused.status_code == 403

    def test_a_child_cannot_cancel_what_she_was_given(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])

        refused = family.as_child().post(f"{ASSIGNMENTS_URL}/{given['id']}/cancel")

        assert refused.status_code == 403

    def test_the_routes_refuse_a_request_without_a_session(
        self, client: TestClient, activities: dict[str, str]
    ) -> None:
        assert client.get(ASSIGNMENTS_URL).status_code == 401
        assert client.get(MY_ACTIVITIES_URL).status_code == 401


class TestNothingGoesBackwards:
    def test_an_activity_is_given_taken_up_then_finished(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        child = family.as_child()

        started = child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start").json()
        finished = child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete").json()

        assert started["status"] == "in_progress"
        assert started["started_at"] is not None
        assert finished["status"] == "completed"
        assert finished["completed_at"] is not None

    def test_it_cannot_be_finished_before_it_is_taken_up(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])

        refused = family.as_child().post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete")

        assert refused.status_code == 409

    def test_it_cannot_be_taken_up_twice(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        again = child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        assert again.status_code == 409

    def test_a_finished_activity_does_not_reopen(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete")

        assert child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start").status_code == 409

    def test_a_cancelled_activity_does_not_resume(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        family.as_parent().post(f"{ASSIGNMENTS_URL}/{given['id']}/cancel")

        assert child_start(family, given["id"]) == 409

    def test_a_finished_assignment_cannot_be_cancelled(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete")

        refused = family.as_parent().post(f"{ASSIGNMENTS_URL}/{given['id']}/cancel")

        assert refused.status_code == 409


class TestCancelling:
    def test_cancelling_keeps_the_row_and_dates_it(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """Given and withdrawn is a different history from never given."""
        given = assign(family, activities["un"])

        cancelled = (
            family.as_parent().post(f"{ASSIGNMENTS_URL}/{given['id']}/cancel").json()
        )

        assert cancelled["status"] == "cancelled"
        assert cancelled["cancelled_at"] is not None
        # The row stays, cancelled: that is the whole claim. Counting the list
        # would count whatever else the child holds as well.
        assert only_ours(family.as_parent().get(ASSIGNMENTS_URL).json(), given) == [
            given["id"]
        ]

    def test_an_activity_under_way_may_still_be_called_off(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        given = assign(family, activities["un"])
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        cancelled = family.as_parent().post(f"{ASSIGNMENTS_URL}/{given['id']}/cancel")

        assert cancelled.status_code == 200
        assert cancelled.json()["started_at"] is not None


class TestListings:
    def test_a_parent_may_narrow_by_child_and_by_status(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        first = assign(family, activities["un"])
        second = assign(family, activities["deux"])
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{first['id']}/start")

        parent = family.as_parent()
        by_child = parent.get(
            ASSIGNMENTS_URL, params={"child_id": family.child_id}
        ).json()
        under_way = parent.get(
            ASSIGNMENTS_URL, params={"assignment_status": "in_progress"}
        ).json()

        assert set(only_ours(by_child, first, second)) == {first["id"], second["id"]}
        assert only_ours(under_way, first, second) == [first["id"]]

    def test_a_child_may_narrow_by_status(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        first = assign(family, activities["un"])
        second = assign(family, activities["deux"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{first['id']}/start")

        to_do = child.get(MY_ACTIVITIES_URL, params={"assignment_status": "assigned"})

        assert only_ours(to_do.json(), first, second) == [second["id"]]

    def test_a_child_is_not_told_which_child_she_is(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """Every row she sees is hers; saying so on each one would be noise."""
        given = assign(family, activities["un"])

        rows = family.as_child().get(MY_ACTIVITIES_URL).json()
        row = next(item for item in rows if item["id"] == given["id"])

        assert "child_id" not in row
        assert "child_pseudonym" not in row

    def test_an_unknown_status_is_refused(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        response = family.as_parent().get(
            ASSIGNMENTS_URL, params={"assignment_status": "peut-etre"}
        )

        assert response.status_code == 422


def child_start(family: Family, assignment_id: str) -> int:
    return (
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{assignment_id}/start").status_code
    )


class TestDueDateAndCourseOrder:
    """The debt of step 09: an assignment could be given but never expected."""

    def test_an_activity_may_be_expected_by_a_day(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        due = (date.today() + timedelta(days=3)).isoformat()

        body = assign(family, activities["un"], due_on=due)

        assert body["due_on"] == due

    def test_an_activity_may_still_be_given_without_a_date(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """Most activities are simply given, not expected by any particular day."""
        assert assign(family, activities["un"])["due_on"] is None

    def test_a_date_already_past_is_refused(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """Nobody means to give a child something that was due yesterday."""
        refused = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={
                "child_id": family.child_id,
                "activity_code": activities["un"],
                "due_on": (date.today() - timedelta(days=1)).isoformat(),
            },
        )

        assert refused.status_code == 409

    def test_what_is_expected_soonest_comes_first(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """The whole of the course order: a consequence of the dates, not a list
        to be dragged around."""
        later = assign(
            family,
            activities["un"],
            due_on=(date.today() + timedelta(days=9)).isoformat(),
        )
        soon = assign(
            family,
            activities["deux"],
            due_on=(date.today() + timedelta(days=1)).isoformat(),
        )

        # Among the rows this test created: a child's list also holds whatever
        # the platform has given her, and the order promised is between these two.
        listed = [
            row["id"]
            for row in family.as_child().get(MY_ACTIVITIES_URL).json()
            if row["id"] in {soon["id"], later["id"]}
        ]

        assert listed == [soon["id"], later["id"]]

    def test_what_is_expected_on_no_day_comes_after_what_is(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        undated = assign(family, activities["un"])
        dated = assign(
            family,
            activities["deux"],
            due_on=(date.today() + timedelta(days=30)).isoformat(),
        )

        listed = [row["id"] for row in family.as_child().get(MY_ACTIVITIES_URL).json()]

        assert listed.index(dated["id"]) < listed.index(undated["id"])


class TestCeilingOnOpenWork:
    """The other debt: nothing stopped a child being buried in work.

    These count from what the child already owes rather than from zero. A
    profile may arrive with something the platform gave it — the initiation
    assessment, when one is published — and a test that assumes an empty slate
    passes or fails depending on which database it meets. That has happened
    often enough on this project to be worth spelling out.
    """

    def test_a_child_cannot_be_given_more_than_the_ceiling(
        self, family: Family, engine: Engine, activities: dict[str, str]
    ) -> None:
        free = MAX_OPEN_ASSIGNMENTS - _owed(family)
        codes = _many_activities(engine, free + 1)

        for code in codes[:free]:
            assign(family, code)
        refused = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": codes[-1]},
        )

        assert refused.status_code == 409
        assert "attente" in refused.json()["error"]["message"]

    def test_finishing_one_frees_a_slot(
        self, family: Family, engine: Engine, activities: dict[str, str]
    ) -> None:
        """The ceiling counts what is owed, not what has ever been given."""
        free = MAX_OPEN_ASSIGNMENTS - _owed(family)
        codes = _many_activities(engine, free + 1)
        given = [assign(family, code) for code in codes[:free]]

        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given[0]['id']}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{given[0]['id']}/complete")

        accepted = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": codes[-1]},
        )

        assert accepted.status_code == 201

    def test_cancelling_one_frees_a_slot_too(
        self, family: Family, engine: Engine, activities: dict[str, str]
    ) -> None:
        free = MAX_OPEN_ASSIGNMENTS - _owed(family)
        codes = _many_activities(engine, free + 1)
        given = [assign(family, code) for code in codes[:free]]
        family.as_parent().post(f"{ASSIGNMENTS_URL}/{given[0]['id']}/cancel")

        accepted = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={"child_id": family.child_id, "activity_code": codes[-1]},
        )

        assert accepted.status_code == 201


class TestOpeningTheContent:
    """The third debt: an activity could be started with nothing to play."""

    def test_a_child_doing_an_activity_is_sent_to_the_content_origin(
        self, family: Family, package_activity: str
    ) -> None:
        """Not to the API: the runtime is isolated behind its own origin, which
        is the whole of ADR-012's fifth condition."""
        given = assign(family, package_activity)
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        body = child.get(f"{MY_ACTIVITIES_URL}/{given['id']}/content").json()

        assert body["library_name"] == "H5P.TrueFalse"
        assert body["play_url"].startswith(settings.CONTENT_ORIGIN_URL)
        # A ticket, and the content it opens; nothing else travels in the URL.
        assert "c=" in body["play_url"] and "t=" in body["play_url"]
        assert body["expires_in"] > 0

    def test_nothing_opens_before_the_activity_is_started(
        self, family: Family, package_activity: str
    ) -> None:
        """Access follows the assignment, not the content."""
        given = assign(family, package_activity)

        refused = family.as_child().get(f"{MY_ACTIVITIES_URL}/{given['id']}/content")

        assert refused.status_code == 409

    def test_nothing_opens_once_it_is_finished(
        self, family: Family, package_activity: str
    ) -> None:
        given = assign(family, package_activity)
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/complete")

        assert (
            child.get(f"{MY_ACTIVITIES_URL}/{given['id']}/content").status_code == 409
        )

    def test_another_child_cannot_open_it(
        self, client: TestClient, package_activity: str
    ) -> None:
        theirs = Family(client)
        given = assign(theirs, package_activity)
        theirs.as_child().post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")
        ours = Family(client)

        refused = ours.as_child().get(f"{MY_ACTIVITIES_URL}/{given['id']}/content")

        assert refused.status_code == 404

    def test_a_parent_cannot_open_it_either(
        self, family: Family, package_activity: str
    ) -> None:
        given = assign(family, package_activity)
        family.as_child().post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        refused = family.as_parent().get(f"{MY_ACTIVITIES_URL}/{given['id']}/content")

        assert refused.status_code == 403

    def test_an_activity_without_a_package_says_so(
        self, family: Family, activities: dict[str, str]
    ) -> None:
        """A PhET simulation or a video is another kind of activity, not a failure."""
        given = assign(family, activities["un"])
        child = family.as_child()
        child.post(f"{MY_ACTIVITIES_URL}/{given['id']}/start")

        refused = child.get(f"{MY_ACTIVITIES_URL}/{given['id']}/content")

        assert refused.status_code == 409
        assert "H5P" in refused.json()["error"]["message"]


def only_ours(rows: list[dict[str, Any]], *given: dict[str, Any]) -> list[str]:
    """The identifiers of the rows this test created, in the order served.

    A child's list also holds what the platform gave her — the initiation
    assessment, when one is published — and a test that counts the whole list is
    measuring the database it happened to meet. Filtering to what the test
    created is what makes the assertion mean the same thing everywhere.
    """
    wanted = {row["id"] for row in given}
    return [row["id"] for row in rows if row["id"] in wanted]


def _owed(family: Family) -> int:
    """How many activities this child already has waiting.

    The platform may have given her one of its own — the initiation assessment —
    and the ceiling counts it like any other. Reading it rather than assuming
    zero is what makes these tests true on an empty database and on a seeded one.
    """
    rows = family.as_child().get(MY_ACTIVITIES_URL).json()
    return len([row for row in rows if row["status"] in ("assigned", "in_progress")])


def _many_activities(engine: Engine, count: int) -> list[str]:
    """More published activities than a child may be given at once.

    They carry the test prefix, so the `activities` fixture removes them: any
    test calling this must depend on that fixture for its teardown.
    """
    codes = [f"{TEST_CODE_PREFIX}m{index:03d}" for index in range(count)]
    with Session(engine) as session:
        session.add_all(
            [
                Activity(
                    code=code,
                    title=f"Activité {code}",
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=5,
                )
                for code in codes
            ]
        )
        session.commit()
    return codes
