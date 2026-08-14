"""Integration tests for child creation, child login and family isolation.

Like the parent suite, these tests run against the real PostgreSQL and Redis
services: the familial uniqueness of a pseudonym and the attempt lockout only
exist once those two enforce them. Parent addresses stay in `example.com`,
reserved by RFC 2606, and every child is fictional.

A single test client serves every identity. A second client would open a second
event loop, and the application engine binds to the first loop that uses it, so
sessions are switched by swapping the cookie rather than by adding a client.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import NamedTuple

import pytest
import redis as sync_redis
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text

from app.core.config import settings
from app.core.db import DATABASE_URL
from app.core.lockout import failure_key
from app.core.security import (
    FAMILY_CODE_ALPHABET,
    FAMILY_CODE_LENGTH,
    hash_session_token,
)
from app.main import app

TEST_EMAIL_DOMAIN = "example.com"
TEST_EMAIL_PREFIX = "parent-enfant-"
PARENT_PASSWORD = "correct-horse-battery"
VALID_PIN = "428173"
OTHER_PIN = "618294"
WRONG_PIN = "999182"

REGISTER_URL = "/api/v1/auth/parent/register"
LOGIN_URL = "/api/v1/auth/parent/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"
CHILDREN_URL = "/api/v1/auth/children"
CHILD_REGISTER_URL = "/api/v1/auth/child/register"
REGENERATE_CODE_URL = "/api/v1/auth/parent/family-code/regenerate"
CHILD_LOGIN_URL = "/api/v1/auth/child/login"
CHILD_ME_URL = "/api/v1/auth/child/me"


class ParentAccount(NamedTuple):
    """What a test needs to speak as a parent, or to reach their family."""

    token: str
    family_code: str


@pytest.fixture(scope="module")
def sync_engine() -> Iterator[Engine]:
    engine = create_engine(
        DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    )
    yield engine
    engine.dispose()


@pytest.fixture
def redis_client() -> Iterator[sync_redis.Redis]:
    client = sync_redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield client
    client.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_test_parents(sync_engine: Engine) -> Iterator[None]:
    """Remove the parents a test created; their children go with the cascade."""
    yield
    with sync_engine.begin() as connection:
        connection.execute(
            text("DELETE FROM auth_parents WHERE email LIKE :pattern"),
            {"pattern": f"{TEST_EMAIL_PREFIX}%@{TEST_EMAIL_DOMAIN}"},
        )


def pseudonym() -> str:
    return f"enfant-{uuid.uuid4().hex}"


def session_key(token: str) -> str:
    return f"session:{hash_session_token(token)}"


def use_session(client: TestClient, token: str) -> None:
    """Make the client speak as the holder of this session token."""
    client.cookies.clear()
    client.cookies.set(settings.SESSION_COOKIE_NAME, token)


def sign_in_parent(client: TestClient) -> ParentAccount:
    """Register a parent, log the client in as that parent, return its handles."""
    email = f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}"
    client.cookies.clear()
    created = client.post(
        REGISTER_URL,
        json={
            "email": email,
            "password": PARENT_PASSWORD,
            "display_name": "Parent de test",
        },
    ).json()
    response = client.post(
        LOGIN_URL, json={"email": email, "password": PARENT_PASSWORD}
    )
    return ParentAccount(
        token=str(response.cookies[settings.SESSION_COOKIE_NAME]),
        family_code=str(created["family_code"]),
    )


def child_payload(
    child_pseudonym: str | None,
    pin: str,
    display_name: str,
    date_of_birth: str | None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "pseudonym": child_pseudonym if child_pseudonym is not None else pseudonym(),
        "pin": pin,
        "display_name": display_name,
    }
    if date_of_birth is not None:
        payload["date_of_birth"] = date_of_birth
    return payload


def create_child(
    client: TestClient,
    child_pseudonym: str | None = None,
    pin: str = VALID_PIN,
    display_name: str = "Enfant de test",
    date_of_birth: str | None = None,
):
    """Create a child from the parent space, which needs no family code."""
    return client.post(
        CHILDREN_URL,
        json=child_payload(child_pseudonym, pin, display_name, date_of_birth),
    )


def register_child(
    client: TestClient,
    family_code: str,
    child_pseudonym: str | None = None,
    pin: str = VALID_PIN,
    display_name: str = "Enfant de test",
):
    """Create a child from the family code, without any session."""
    client.cookies.clear()
    payload = child_payload(child_pseudonym, pin, display_name, None)
    payload["family_code"] = family_code
    return client.post(CHILD_REGISTER_URL, json=payload)


def child_login(
    client: TestClient,
    family_code: str,
    child_pseudonym: str,
    pin: str = VALID_PIN,
):
    """Log in as a child, which replaces whatever session the client held."""
    client.cookies.clear()
    return client.post(
        CHILD_LOGIN_URL,
        json={
            "family_code": family_code,
            "pseudonym": child_pseudonym,
            "pin": pin,
        },
    )


def activate_url(child_id: str) -> str:
    return f"{CHILDREN_URL}/{child_id}/activate"


class TestChildCreation:
    def test_create_returns_an_active_profile_without_the_pin(
        self, client: TestClient
    ) -> None:
        sign_in_parent(client)
        chosen = pseudonym()

        response = create_child(client, chosen, date_of_birth="2017-05-04")

        assert response.status_code == 201
        body = response.json()
        assert body["pseudonym"] == chosen
        assert body["display_name"] == "Enfant de test"
        assert body["date_of_birth"] == "2017-05-04"
        assert body["status"] == "active"
        assert "pin" not in body
        assert "pin_hash" not in body
        assert VALID_PIN not in repr(body)

    def test_create_requires_a_parent_session(self, client: TestClient) -> None:
        assert create_child(client).status_code == 401

    def test_a_child_session_cannot_create_a_child(self, client: TestClient) -> None:
        """Only an adult account opens profiles, whatever the child's session."""
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)
        child_login(client, parent.family_code, chosen)

        response = create_child(client)

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"

    def test_create_refuses_a_pseudonym_taken_in_the_same_family(
        self, client: TestClient
    ) -> None:
        sign_in_parent(client)
        chosen = pseudonym()
        assert create_child(client, chosen).status_code == 201

        response = create_child(client, chosen)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"

    def test_two_families_may_hold_the_same_pseudonym(self, client: TestClient) -> None:
        """Uniqueness is familial: the family code tells the two apart at login."""
        first = sign_in_parent(client)
        shared = pseudonym()
        assert create_child(client, shared).status_code == 201

        second = sign_in_parent(client)
        assert create_child(client, shared, pin=OTHER_PIN).status_code == 201

        as_first = child_login(client, first.family_code, shared)
        as_second = child_login(client, second.family_code, shared, pin=OTHER_PIN)

        assert as_first.status_code == 200
        assert as_second.status_code == 200
        assert as_first.json()["id"] != as_second.json()["id"]

    def test_create_normalises_the_pseudonym_case(self, client: TestClient) -> None:
        sign_in_parent(client)
        chosen = pseudonym()

        created = create_child(client, chosen.upper())

        assert created.status_code == 201
        assert created.json()["pseudonym"] == chosen
        assert create_child(client, chosen).status_code == 409

    @pytest.mark.parametrize(
        "pin",
        ["12345", "1234567", "12a456", "12 456", "111111", "123456", "654321", ""],
    )
    def test_create_refuses_a_weak_or_malformed_pin(
        self, client: TestClient, pin: str
    ) -> None:
        sign_in_parent(client)

        assert create_child(client, pin=pin).status_code == 422

    @pytest.mark.parametrize(
        "bad_pseudonym", ["ab", "-lea", "lea-", "lea!", "élise", "lea lou", "a" * 51]
    )
    def test_create_refuses_an_invalid_pseudonym(
        self, client: TestClient, bad_pseudonym: str
    ) -> None:
        sign_in_parent(client)

        assert create_child(client, bad_pseudonym).status_code == 422

    def test_create_refuses_a_blank_display_name(self, client: TestClient) -> None:
        sign_in_parent(client)

        assert create_child(client, display_name="   ").status_code == 422

    def test_create_refuses_a_future_birth_date(self, client: TestClient) -> None:
        sign_in_parent(client)

        assert create_child(client, date_of_birth="2999-01-01").status_code == 422


class TestChildSelfRegistration:
    """A child may open its own profile, but never let itself in."""

    def test_the_family_code_creates_a_pending_profile(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()

        response = register_child(client, parent.family_code, chosen)

        assert response.status_code == 201
        assert response.json()["status"] == "pending"
        assert response.json()["pseudonym"] == chosen
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_the_family_code_is_case_insensitive(self, client: TestClient) -> None:
        """A child reads the code off a sheet of paper, not off a keyboard."""
        parent = sign_in_parent(client)

        response = register_child(client, parent.family_code.lower())

        assert response.status_code == 201

    def test_an_unknown_family_code_creates_nothing(self, client: TestClient) -> None:
        response = register_child(client, "ZZZZZZ")

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_a_pending_profile_cannot_log_in_even_with_the_right_pin(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        register_child(client, parent.family_code, chosen)

        response = child_login(client, parent.family_code, chosen)

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_self_registration_refuses_a_pseudonym_taken_in_that_family(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        assert register_child(client, parent.family_code, chosen).status_code == 409

    def test_self_registration_applies_the_same_pin_rules(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)

        assert register_child(client, parent.family_code, pin="111111").status_code == (
            422
        )

    def test_the_parent_sees_the_pending_profile(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]

        use_session(client, parent.token)
        listed = client.get(CHILDREN_URL).json()

        assert [child["id"] for child in listed] == [pending_id]
        assert listed[0]["status"] == "pending"


class TestTurningDownAPendingProfile:
    """Regenerating the code closes the door; this clears what came through."""

    def test_the_parent_drops_a_pending_profile(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]

        use_session(client, parent.token)
        response = client.delete(f"{CHILDREN_URL}/{pending_id}")

        assert response.status_code == 204
        assert client.get(CHILDREN_URL).json() == []

    def test_the_pseudonym_is_free_again_afterwards(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]

        use_session(client, parent.token)
        client.delete(f"{CHILDREN_URL}/{pending_id}")

        assert create_child(client, chosen).status_code == 201

    def test_an_active_profile_is_not_dropped_this_way(
        self, client: TestClient
    ) -> None:
        """An active profile holds a history; removing it is its own decision."""
        sign_in_parent(client)
        child_id = create_child(client).json()["id"]

        response = client.delete(f"{CHILDREN_URL}/{child_id}")

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"
        assert len(client.get(CHILDREN_URL).json()) == 1

    def test_a_parent_cannot_drop_another_familys_profile(
        self, client: TestClient
    ) -> None:
        first = sign_in_parent(client)
        foreign_id = register_child(client, first.family_code).json()["id"]

        other = sign_in_parent(client)
        use_session(client, other.token)

        assert client.delete(f"{CHILDREN_URL}/{foreign_id}").status_code == 404
        assert client.delete(f"{CHILDREN_URL}/{uuid.uuid4()}").status_code == 404

    def test_dropping_requires_a_parent_session(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]

        assert client.delete(f"{CHILDREN_URL}/{pending_id}").status_code == 401

    def test_a_child_cannot_drop_a_pending_profile(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        pending_id = register_child(client, parent.family_code).json()["id"]
        sibling = pseudonym()
        use_session(client, parent.token)
        create_child(client, sibling)
        child_login(client, parent.family_code, sibling)

        assert client.delete(f"{CHILDREN_URL}/{pending_id}").status_code == 403


class TestFamilyCodeRegeneration:
    """A code that has got around must be replaceable by the parent alone."""

    def test_regeneration_returns_a_different_valid_code(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)

        response = client.post(REGENERATE_CODE_URL)

        assert response.status_code == 200
        new_code = response.json()["family_code"]
        assert new_code != parent.family_code
        assert len(new_code) == FAMILY_CODE_LENGTH
        assert set(new_code) <= set(FAMILY_CODE_ALPHABET)
        assert client.get(ME_URL).json()["family_code"] == new_code

    def test_the_old_code_stops_working_everywhere(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        use_session(client, parent.token)
        new_code = client.post(REGENERATE_CODE_URL).json()["family_code"]

        assert child_login(client, parent.family_code, chosen).status_code == 401
        assert register_child(client, parent.family_code).status_code == 404
        assert child_login(client, new_code, chosen).status_code == 200
        assert register_child(client, new_code).status_code == 201

    def test_regeneration_leaves_open_sessions_alone(self, client: TestClient) -> None:
        """The child on the family tablet is not the reason the code leaked."""
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)
        child_token = child_login(client, parent.family_code, chosen).cookies[
            settings.SESSION_COOKIE_NAME
        ]

        use_session(client, parent.token)
        assert client.post(REGENERATE_CODE_URL).status_code == 200

        use_session(client, child_token)
        assert client.get(CHILD_ME_URL).status_code == 200

    def test_profiles_created_under_the_old_code_remain(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        pending_id = register_child(client, parent.family_code).json()["id"]

        use_session(client, parent.token)
        client.post(REGENERATE_CODE_URL)

        listed = client.get(CHILDREN_URL).json()
        assert [child["id"] for child in listed] == [pending_id]

    def test_regeneration_requires_a_parent_session(self, client: TestClient) -> None:
        assert client.post(REGENERATE_CODE_URL).status_code == 401

    def test_a_child_cannot_regenerate_the_family_code(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)
        child_login(client, parent.family_code, chosen)

        assert client.post(REGENERATE_CODE_URL).status_code == 403


class TestActivation:
    def test_the_parent_activates_a_pending_profile(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]

        use_session(client, parent.token)
        activated = client.post(activate_url(pending_id))

        assert activated.status_code == 200
        assert activated.json()["status"] == "active"
        assert child_login(client, parent.family_code, chosen).status_code == 200

    def test_activation_is_idempotent(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        child_id = create_child(client).json()["id"]

        use_session(client, parent.token)
        response = client.post(activate_url(child_id))

        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_a_parent_cannot_activate_another_familys_child(
        self, client: TestClient
    ) -> None:
        """The answer is the same as for a profile that does not exist at all."""
        sign_in_parent(client)
        foreign_id = create_child(client).json()["id"]

        other = sign_in_parent(client)
        use_session(client, other.token)
        response = client.post(activate_url(foreign_id))

        assert response.status_code == 404
        assert client.post(activate_url(str(uuid.uuid4()))).status_code == 404

    def test_activation_requires_a_session(self, client: TestClient) -> None:
        sign_in_parent(client)
        child_id = create_child(client).json()["id"]

        client.cookies.clear()

        assert client.post(activate_url(child_id)).status_code == 401

    def test_a_child_cannot_activate_itself(self, client: TestClient) -> None:
        """Otherwise the parent's approval would be a formality the child skips."""
        parent = sign_in_parent(client)
        chosen = pseudonym()
        pending_id = register_child(client, parent.family_code, chosen).json()["id"]
        sibling = pseudonym()
        use_session(client, parent.token)
        create_child(client, sibling)
        child_login(client, parent.family_code, sibling)

        assert client.post(activate_url(pending_id)).status_code == 403


class TestFamilyIsolation:
    def test_list_returns_only_the_callers_children(self, client: TestClient) -> None:
        first = sign_in_parent(client)
        mine = create_child(client).json()["id"]
        sign_in_parent(client)
        theirs = create_child(client).json()["id"]

        use_session(client, first.token)
        listed = client.get(CHILDREN_URL)

        assert listed.status_code == 200
        identifiers = [child["id"] for child in listed.json()]
        assert identifiers == [mine]
        assert theirs not in identifiers

    def test_list_requires_a_parent_session(self, client: TestClient) -> None:
        assert client.get(CHILDREN_URL).status_code == 401

    def test_a_parent_session_cannot_read_the_child_space(
        self, client: TestClient
    ) -> None:
        sign_in_parent(client)

        assert client.get(CHILD_ME_URL).status_code == 403

    def test_a_child_session_cannot_read_the_parent_space(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)
        child_login(client, parent.family_code, chosen)

        assert client.get(ME_URL).status_code == 403


class TestChildLogin:
    def test_login_opens_a_child_session_shorter_than_a_parents(
        self, client: TestClient, redis_client: sync_redis.Redis
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        child_id = create_child(client, chosen).json()["id"]

        response = child_login(client, parent.family_code, chosen)

        assert response.status_code == 200
        assert response.json()["id"] == child_id

        set_cookie = response.headers["set-cookie"].lower()
        assert "httponly" in set_cookie
        assert "samesite=lax" in set_cookie

        token = response.cookies[settings.SESSION_COOKIE_NAME]
        stored = redis_client.hgetall(session_key(token))
        assert stored["user_id"] == child_id
        assert stored["user_type"] == "child"

        ttl = redis_client.ttl(session_key(token))
        assert 0 < ttl <= settings.CHILD_SESSION_TTL_SECONDS
        assert ttl < settings.SESSION_TTL_SECONDS

    def test_each_login_mints_a_new_session(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        first = child_login(client, parent.family_code, chosen).cookies[
            settings.SESSION_COOKIE_NAME
        ]
        second = child_login(client, parent.family_code, chosen).cookies[
            settings.SESSION_COOKIE_NAME
        ]

        assert first != second

    def test_login_refuses_a_wrong_pin(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        response = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)

        assert response.status_code == 401
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_a_wrong_family_code_answers_exactly_like_a_wrong_pin(
        self, client: TestClient
    ) -> None:
        """The code must not become an oracle telling which families exist."""
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        wrong_pin = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)
        wrong_code = child_login(client, "ZZZZZZ", chosen)

        assert wrong_pin.status_code == 401
        assert wrong_code.status_code == 401
        assert wrong_pin.json() == wrong_code.json()

    def test_an_unknown_pseudonym_answers_exactly_like_a_wrong_pin(
        self, client: TestClient
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        wrong_pin = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)
        unknown = child_login(client, parent.family_code, pseudonym(), pin=WRONG_PIN)

        assert wrong_pin.status_code == 401
        assert unknown.status_code == 401
        assert wrong_pin.json() == unknown.json()

    def test_a_pseudonym_of_another_family_is_not_reachable(
        self, client: TestClient
    ) -> None:
        sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)

        other = sign_in_parent(client)

        assert child_login(client, other.family_code, chosen).status_code == 401

    def test_child_me_returns_the_authenticated_child(self, client: TestClient) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        child_id = create_child(client, chosen).json()["id"]
        child_login(client, parent.family_code, chosen)

        response = client.get(CHILD_ME_URL)

        assert response.status_code == 200
        assert response.json()["id"] == child_id
        assert "pin_hash" not in response.json()

    def test_logout_revokes_the_child_session(
        self, client: TestClient, redis_client: sync_redis.Redis
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        create_child(client, chosen)
        token = child_login(client, parent.family_code, chosen).cookies[
            settings.SESSION_COOKIE_NAME
        ]

        response = client.delete(LOGOUT_URL)

        assert response.status_code == 204
        assert redis_client.exists(session_key(token)) == 0
        assert client.get(CHILD_ME_URL).status_code == 401


class TestPinLockout:
    """Six digits only hold if the attempts are capped."""

    @pytest.fixture
    def locked_child(
        self, client: TestClient, redis_client: sync_redis.Redis
    ) -> Iterator[tuple[ParentAccount, str, str]]:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        child_id = create_child(client, chosen).json()["id"]

        for _ in range(settings.CHILD_PIN_MAX_ATTEMPTS):
            attempt = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)
            assert attempt.status_code == 401

        yield parent, chosen, child_id
        redis_client.delete(failure_key(uuid.UUID(child_id)))

    def test_the_allowance_spent_the_login_is_refused(
        self, client: TestClient, locked_child: tuple[ParentAccount, str, str]
    ) -> None:
        parent, chosen, _ = locked_child

        response = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)

        assert response.status_code == 429
        assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_the_lockout_holds_against_the_right_pin(
        self, client: TestClient, locked_child: tuple[ParentAccount, str, str]
    ) -> None:
        """Otherwise the cap would only slow an attacker instead of stopping them."""
        parent, chosen, _ = locked_child

        response = child_login(client, parent.family_code, chosen)

        assert response.status_code == 429
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_the_counter_expires_on_its_own(
        self,
        redis_client: sync_redis.Redis,
        locked_child: tuple[ParentAccount, str, str],
    ) -> None:
        _, _, child_id = locked_child

        ttl = redis_client.ttl(failure_key(uuid.UUID(child_id)))

        assert 0 < ttl <= settings.CHILD_PIN_LOCKOUT_SECONDS

    def test_a_successful_login_clears_the_counter(
        self, client: TestClient, redis_client: sync_redis.Redis
    ) -> None:
        parent = sign_in_parent(client)
        chosen = pseudonym()
        child_id = create_child(client, chosen).json()["id"]
        failed = child_login(client, parent.family_code, chosen, pin=WRONG_PIN)
        assert failed.status_code == 401

        assert child_login(client, parent.family_code, chosen).status_code == 200

        assert redis_client.exists(failure_key(uuid.UUID(child_id))) == 0
