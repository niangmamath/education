"""Sending statements through the real API, with the real doors in the way.

Three things are tested by making them fail if they were absent: only an open
activity may send statements, a retransmission is not a second answer, and no
identity of the child ever crosses to the content origin — in either direction.

Isolation is tested as in the steps before, by building a second family in full
and trying its ticket against the first.
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
    H5PPackage,
)
from app.models.xapi import VERB_ANSWERED, VERB_COMPLETED
from app.xapi.statements import actor_key

TEST_CODE_PREFIX = "test-xapi-"
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"
DIGEST = uuid.uuid4().hex + uuid.uuid4().hex

ASSIGNMENTS_URL = "/api/v1/assignments"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"
STATEMENTS_URL = "/api/v1/me/xapi/statements"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def activity(engine: Engine) -> Iterator[str]:
    """One published H5P activity, with a package so it can be opened."""
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
        session.add_all(
            [
                ActivityCompetency(activity_id=row.id, competency_code=COMPETENCY),
                H5PPackage(
                    activity_id=row.id,
                    library_name="H5P.TrueFalse",
                    library_version="1.8",
                    object_key=f"h5p/{code}.h5p",
                    sha256=DIGEST,
                    size_bytes=2048,
                    licence="CC BY 4.0",
                    source="https://h5p.org/true-false",
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


@pytest.fixture
async def store() -> Any:
    connection = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield connection
    await connection.aclose()


class Family:
    """A parent, an active child, and the client holding a session."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"xapi-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent xAPI",
            },
        )
        assert created.status_code == 201
        self.family_code = created.json()["family_code"]
        self.as_parent()

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


def open_attempt(family: Family, activity_code: str) -> tuple[str, str]:
    """An assignment taken up, with an attempt running. Returns both identifiers."""
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


def statement(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "actor": {"objectType": "Agent", "name": "Léa Dupont"},
        "verb": {"id": VERB_ANSWERED},
        "object": {"id": "q1"},
        "result": {"success": True, "response": "vrai"},
    }
    body.update(overrides)
    return body


def send(client: TestClient, ticket: str, body: dict[str, Any] | None = None) -> Any:
    return client.post(
        STATEMENTS_URL,
        json=body if body is not None else statement(),
        headers={"X-Content-Ticket": ticket},
    )


class TestOnlyAnOpenActivityMaySendStatements:
    async def test_a_statement_with_a_valid_ticket_is_taken_in(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, _ = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        sent = send(family.as_child(), ticket)

        assert sent.status_code == 201, sent.text

    def test_no_ticket_at_all_is_refused(self, family: Family, activity: str) -> None:
        open_attempt(family, activity)

        refused = family.as_child().post(STATEMENTS_URL, json=statement())

        assert refused.status_code == 403

    def test_an_unknown_ticket_is_refused(self, family: Family, activity: str) -> None:
        """An expired one looks exactly like this, and that is the point."""
        open_attempt(family, activity)

        refused = send(family.as_child(), "ticket-qui-nexiste-pas")

        assert refused.status_code == 403

    async def test_another_familys_ticket_is_refused(
        self, client: TestClient, activity: str, store: Any
    ) -> None:
        first = Family(client)
        assignment_id, _ = open_attempt(first, activity)
        stolen = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        second = Family(client)
        refused = send(second.as_child(), stolen)

        assert refused.status_code == 403

    async def test_a_parent_may_not_send_statements(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, _ = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        refused = send(family.as_parent(), ticket)

        assert refused.status_code == 403

    async def test_a_ticket_without_a_running_attempt_is_told_so(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        child = family.as_child()
        child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete")
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        refused = send(child, ticket)

        assert refused.status_code == 409

    async def test_the_client_never_names_the_attempt(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """The server derives it from the ticket, so it cannot be pointed elsewhere."""
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        sent = send(family.as_child(), ticket)

        assert sent.json()["attempt_id"] == attempt_id


class TestARetransmissionIsNotASecondAnswer:
    async def test_the_same_statement_twice_is_stored_once(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        body = statement()
        child = family.as_child()

        first = send(child, ticket, body)
        again = send(child, ticket, body)

        assert first.status_code == 201
        assert again.status_code == 200
        assert again.json()["id"] == first.json()["id"]

    async def test_a_replay_leaves_one_response_behind(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        body = statement()
        child = family.as_child()

        for _ in range(5):
            send(child, ticket, body)

        finished = child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").json()
        assert len(finished["responses"]) == 1

    async def test_two_different_statements_are_two_events(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """Answering twice really is two answers; only replays are collapsed."""
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        send(child, ticket, statement())
        send(child, ticket, statement())

        finished = child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").json()
        assert len(finished["responses"]) == 2


class TestWhatAStatementBecomes:
    async def test_an_answered_statement_becomes_a_response_marked_xapi(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        send(child, ticket)

        finished = child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").json()
        assert [row["source"] for row in finished["responses"]] == ["xapi"]

    async def test_the_client_cannot_declare_where_its_data_came_from(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """`source` is set by the route; a statement naming it changes nothing."""
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        send(child, ticket, statement(source="declared"))

        finished = child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").json()
        assert finished["responses"][0]["source"] == "xapi"

    async def test_a_completion_statement_produces_no_response(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """Only `answered` says something about a question."""
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        sent = send(child, ticket, statement(verb={"id": VERB_COMPLETED}, result={}))

        assert sent.status_code == 201
        assert sent.json()["response_id"] is None
        finished = child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").json()
        assert finished["responses"] == []

    async def test_a_statement_does_not_finish_the_attempt(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """Finishing is a deliberate act; an observation is not one."""
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        send(child, ticket, statement(verb={"id": VERB_COMPLETED}, result={}))

        listed = child.get(MY_ATTEMPTS_URL, params={"assignment_id": assignment_id})
        assert listed.json()[0]["status"] == "in_progress"

    async def test_a_refused_statement_leaves_nothing_behind(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        refused = send(child, ticket, statement(verb={"id": "http://x/verbs/bricoler"}))

        assert refused.status_code == 422
        held = child.get(f"{MY_ATTEMPTS_URL}/{attempt_id}/xapi/statements")
        assert held.json() == []


class TestTheChildIsNeverExposedToTheRuntime:
    def test_the_play_url_names_no_child(self, family: Family, activity: str) -> None:
        """Only a content digest and an opaque ticket cross to the other origin."""
        assignment_id, _ = open_attempt(family, activity)

        content = family.as_child().get(f"{MY_ACTIVITIES_URL}/{assignment_id}/content")

        url = content.json()["play_url"]
        assert family.child_id not in url
        assert family.pseudonym not in url
        assert family.family_code not in url
        assert assignment_id not in url

    async def test_the_stored_actor_is_the_servers_pseudonym(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        sent = send(child, ticket)

        assert sent.json()["actor_key"] == actor_key(uuid.UUID(family.child_id))
        assert sent.json()["actor_key"] != family.child_id

    async def test_the_claimed_actor_is_not_kept(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()

        send(child, ticket)

        held = child.get(f"{MY_ATTEMPTS_URL}/{attempt_id}/xapi/statements")
        assert "Léa Dupont" not in held.text

    async def test_the_two_clocks_are_kept_apart(
        self, family: Family, activity: str, store: Any
    ) -> None:
        """ADR-012 condition 7: what the source claims is not when we received it."""
        assignment_id, _ = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)

        sent = send(
            family.as_child(), ticket, statement(timestamp="2020-01-01T00:00:00Z")
        )

        body = sent.json()
        assert body["issued_at"].startswith("2020-01-01")
        assert not body["received_at"].startswith("2020-01-01")


class TestReadingBackWhatWasReceived:
    async def test_a_child_reads_her_own_statements(
        self, family: Family, activity: str, store: Any
    ) -> None:
        assignment_id, attempt_id = open_attempt(family, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        child = family.as_child()
        send(child, ticket)

        held = child.get(f"{MY_ATTEMPTS_URL}/{attempt_id}/xapi/statements")

        assert held.status_code == 200
        assert len(held.json()) == 1

    async def test_another_familys_attempt_shows_nothing(
        self, client: TestClient, activity: str, store: Any
    ) -> None:
        first = Family(client)
        assignment_id, attempt_id = open_attempt(first, activity)
        ticket = await mint_ticket(store, uuid.UUID(assignment_id), DIGEST)
        send(first.as_child(), ticket)

        second = Family(client)
        held = second.as_child().get(f"{MY_ATTEMPTS_URL}/{attempt_id}/xapi/statements")

        assert held.json() == []

    def test_a_parent_may_not_read_the_raw_traffic(
        self, family: Family, activity: str
    ) -> None:
        """What a parent is shown is the reading, not what a content emitted."""
        _, attempt_id = open_attempt(family, activity)

        refused = family.as_parent().get(
            f"{MY_ATTEMPTS_URL}/{attempt_id}/xapi/statements"
        )

        assert refused.status_code == 403
