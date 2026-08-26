"""Integration tests for parent registration, login, sessions and logout.

These tests deliberately exercise the real PostgreSQL and Redis services: email
uniqueness is only real once PostgreSQL enforces it, and a session is only real
once Redis holds it. Setup and teardown go through synchronous drivers so that
no connection outlives the event loop the test client owns.

Every address belongs to `example.com`, reserved by RFC 2606, so no test can
touch a real mailbox.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

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
TEST_EMAIL_PREFIX = "parent-"
VALID_PASSWORD = "correct-horse-battery"
WRONG_PASSWORD = "mauvais-mot-de-passe"

REGISTER_URL = "/api/v1/auth/parent/register"
LOGIN_URL = "/api/v1/auth/parent/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"


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


@pytest.fixture
def email() -> str:
    return f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}"


@pytest.fixture(autouse=True)
def clean_test_parents(sync_engine: Engine) -> Iterator[None]:
    """Remove the accounts a test created, children included through the cascade."""
    yield
    with sync_engine.begin() as connection:
        connection.execute(
            text("DELETE FROM auth_parents WHERE email LIKE :pattern"),
            {"pattern": f"{TEST_EMAIL_PREFIX}%@{TEST_EMAIL_DOMAIN}"},
        )


def register(
    client: TestClient,
    email: str,
    password: str = VALID_PASSWORD,
    display_name: str = "Parent de test",
):
    return client.post(
        REGISTER_URL,
        json={"email": email, "password": password, "display_name": display_name},
    )


def login(client: TestClient, email: str, password: str = VALID_PASSWORD):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


def session_key(token: str) -> str:
    return f"session:{hash_session_token(token)}"


class TestRegistration:
    def test_register_creates_an_unverified_parent(
        self, client: TestClient, email: str
    ) -> None:
        response = register(client, email)

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == email
        assert body["display_name"] == "Parent de test"
        assert body["is_verified"] is False

    def test_register_mints_a_family_code(self, client: TestClient) -> None:
        """The code is the parent's handle for their children, drawn at random."""
        first = register(client, f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex}@example.com")
        second = register(client, f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex}@example.com")

        code = first.json()["family_code"]
        assert len(code) == FAMILY_CODE_LENGTH
        assert set(code) <= set(FAMILY_CODE_ALPHABET)
        assert code != second.json()["family_code"]

    def test_register_never_returns_the_password(
        self, client: TestClient, email: str
    ) -> None:
        body = register(client, email).json()

        assert "password" not in body
        assert "password_hash" not in body
        assert VALID_PASSWORD not in repr(body)

    def test_register_does_not_open_a_session(
        self, client: TestClient, email: str
    ) -> None:
        """ADR-005 places email verification between registration and login."""
        response = register(client, email)

        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_register_refuses_a_duplicate_email(
        self, client: TestClient, email: str
    ) -> None:
        assert register(client, email).status_code == 201

        response = register(client, email)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"

    def test_register_normalises_the_email_case(self, client: TestClient) -> None:
        raw = f"{TEST_EMAIL_PREFIX.upper()}{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}"

        created = register(client, raw)

        assert created.status_code == 201
        assert created.json()["email"] == raw.lower()
        assert register(client, raw.lower()).status_code == 409

    @pytest.mark.parametrize("password", ["court", "a" * 11])
    def test_register_refuses_a_password_below_the_minimum(
        self, client: TestClient, email: str, password: str
    ) -> None:
        assert register(client, email, password=password).status_code == 422

    def test_register_refuses_an_invalid_email(self, client: TestClient) -> None:
        assert register(client, "pas-une-adresse").status_code == 422

    def test_register_refuses_a_blank_display_name(
        self, client: TestClient, email: str
    ) -> None:
        assert register(client, email, display_name="   ").status_code == 422


class TestLogin:
    def test_login_returns_the_parent_and_sets_a_hardened_cookie(
        self, client: TestClient, email: str
    ) -> None:
        register(client, email)

        response = login(client, email)

        assert response.status_code == 200
        assert response.json()["email"] == email

        set_cookie = response.headers["set-cookie"].lower()
        assert "httponly" in set_cookie
        assert "samesite=lax" in set_cookie
        assert "path=/" in set_cookie

    def test_login_stores_the_session_in_redis(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        parent_id = register(client, email).json()["id"]

        token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]

        stored = redis_client.hgetall(session_key(token))
        assert stored["user_id"] == parent_id
        assert stored["user_type"] == "parent"

    def test_session_is_keyed_by_a_digest_not_by_the_token(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        """A leaked Redis dump must not hand out replayable cookies."""
        register(client, email)

        token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]

        assert redis_client.exists(session_key(token)) == 1
        assert redis_client.exists(f"session:{token}") == 0

    def test_session_expires_on_its_own(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        register(client, email)

        token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]

        ttl = redis_client.ttl(session_key(token))
        assert 0 < ttl <= settings.SESSION_TTL_SECONDS

    def test_each_login_mints_a_new_session(
        self, client: TestClient, email: str
    ) -> None:
        """Regenerating the identifier is what closes session fixation."""
        register(client, email)

        first = login(client, email).cookies[settings.SESSION_COOKIE_NAME]
        second = login(client, email).cookies[settings.SESSION_COOKIE_NAME]

        assert first != second

    def test_login_refuses_a_wrong_password(
        self, client: TestClient, email: str
    ) -> None:
        register(client, email)

        response = login(client, email, password=WRONG_PASSWORD)

        assert response.status_code == 401
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_an_unknown_email_answers_exactly_like_a_wrong_password(
        self, client: TestClient, email: str
    ) -> None:
        """Distinct answers would tell an attacker which addresses are registered."""
        register(client, email)

        wrong_password = login(client, email, password=WRONG_PASSWORD)
        unknown_email = login(client, f"absent-{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}")

        assert wrong_password.status_code == 401
        assert unknown_email.status_code == 401
        assert wrong_password.json() == unknown_email.json()


class TestLoginLockout:
    """A password is stronger than a PIN, but nothing else caps repeated guesses."""

    @pytest.fixture
    def locked_parent(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> Iterator[str]:
        parent_id = register(client, email).json()["id"]

        for _ in range(settings.PARENT_LOGIN_MAX_ATTEMPTS):
            attempt = login(client, email, password=WRONG_PASSWORD)
            assert attempt.status_code == 401

        yield parent_id
        redis_client.delete(failure_key(uuid.UUID(parent_id), scope="parent-login"))

    def test_the_allowance_spent_the_login_is_refused(
        self, client: TestClient, email: str, locked_parent: str
    ) -> None:
        response = login(client, email, password=WRONG_PASSWORD)

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"

    def test_the_lockout_holds_against_the_right_password(
        self, client: TestClient, email: str, locked_parent: str
    ) -> None:
        """Otherwise the cap would only slow an attacker instead of stopping them."""
        response = login(client, email)

        assert response.status_code == 401
        assert settings.SESSION_COOKIE_NAME not in response.cookies

    def test_a_locked_account_answers_exactly_like_an_unknown_email(
        self, client: TestClient, email: str, locked_parent: str
    ) -> None:
        """A distinct status here would let an attacker confirm the email is
        registered just by exhausting the lockout — the same oracle
        `INVALID_CREDENTIALS_MESSAGE` already denies them on a plain wrong
        password."""
        locked = login(client, email, password=WRONG_PASSWORD)
        unknown_email = login(client, f"absent-{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}")

        assert locked.status_code == unknown_email.status_code == 401
        assert locked.json() == unknown_email.json()

    def test_the_counter_expires_on_its_own(
        self, redis_client: sync_redis.Redis, locked_parent: str
    ) -> None:
        ttl = redis_client.ttl(
            failure_key(uuid.UUID(locked_parent), scope="parent-login")
        )

        assert 0 < ttl <= settings.PARENT_LOGIN_LOCKOUT_SECONDS

    def test_a_successful_login_clears_the_counter(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        parent_id = register(client, email).json()["id"]
        failed = login(client, email, password=WRONG_PASSWORD)
        assert failed.status_code == 401

        assert login(client, email).status_code == 200

        key = failure_key(uuid.UUID(parent_id), scope="parent-login")
        assert redis_client.exists(key) == 0


class TestSessionAccess:
    def test_me_refuses_a_caller_without_a_cookie(self, client: TestClient) -> None:
        assert client.get(ME_URL).status_code == 401

    def test_me_refuses_a_forged_token(self, client: TestClient) -> None:
        client.cookies.set(settings.SESSION_COOKIE_NAME, "jeton-inexistant")

        assert client.get(ME_URL).status_code == 401

    def test_me_returns_the_authenticated_parent(
        self, client: TestClient, email: str
    ) -> None:
        created = register(client, email).json()
        login(client, email)

        response = client.get(ME_URL)

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
        assert "password_hash" not in response.json()


class TestProfileUpdate:
    def test_a_parent_renames_their_own_profile(
        self, client: TestClient, email: str
    ) -> None:
        register(client, email)
        login(client, email)

        response = client.put(ME_URL, json={"display_name": "Nouveau nom"})

        assert response.status_code == 200
        assert response.json()["display_name"] == "Nouveau nom"
        assert client.get(ME_URL).json()["display_name"] == "Nouveau nom"

    def test_renaming_refuses_a_caller_without_a_cookie(
        self, client: TestClient
    ) -> None:
        response = client.put(ME_URL, json={"display_name": "Nouveau nom"})
        assert response.status_code == 401

    def test_a_parent_changes_their_password(
        self, client: TestClient, email: str
    ) -> None:
        register(client, email)
        login(client, email)

        response = client.put(
            f"{ME_URL}/password",
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "un-autre-mot-de-passe",
            },
        )

        assert response.status_code == 200
        assert login(client, email, "un-autre-mot-de-passe").status_code == 200
        assert login(client, email, VALID_PASSWORD).status_code == 401

    def test_changing_password_refuses_the_wrong_current_one(
        self, client: TestClient, email: str
    ) -> None:
        register(client, email)
        login(client, email)

        response = client.put(
            f"{ME_URL}/password",
            json={
                "current_password": WRONG_PASSWORD,
                "new_password": "un-autre-mot-de-passe",
            },
        )

        assert response.status_code == 401
        assert login(client, email, VALID_PASSWORD).status_code == 200

    def test_changing_password_revokes_every_other_session(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        register(client, email)
        elsewhere_token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]
        here_token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]
        client.cookies.set(settings.SESSION_COOKIE_NAME, here_token)

        response = client.put(
            f"{ME_URL}/password",
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "un-autre-mot-de-passe",
            },
        )

        assert response.status_code == 200
        assert client.get(ME_URL).status_code == 200
        assert (
            redis_client.exists(f"session:{hash_session_token(elsewhere_token)}") == 0
        )


class TestLogout:
    def test_logout_revokes_the_session_everywhere(
        self, client: TestClient, email: str, redis_client: sync_redis.Redis
    ) -> None:
        register(client, email)
        token = login(client, email).cookies[settings.SESSION_COOKIE_NAME]

        response = client.delete(LOGOUT_URL)

        assert response.status_code == 204
        assert redis_client.exists(session_key(token)) == 0
        assert client.get(ME_URL).status_code == 401

    def test_logout_refuses_a_caller_without_a_cookie(self, client: TestClient) -> None:
        assert client.delete(LOGOUT_URL).status_code == 401


class TestWhichSpaceTheCallerIsIn:
    """`GET /auth/session` answers, in one call, a question every client asks first.

    Without it a client would try the Parent route, read a `403`, and try the
    Élève one — two round trips and a refusal in the logs to answer a question
    neither endpoint was asked.
    """

    def test_a_parent_session_says_parent(self, client: TestClient, email: str) -> None:
        client.post(
            REGISTER_URL,
            json={
                "email": email,
                "password": VALID_PASSWORD,
                "display_name": "Alex Martin",
            },
        )
        client.post(LOGIN_URL, json={"email": email, "password": VALID_PASSWORD})

        body = client.get("/api/v1/auth/session")

        assert body.status_code == 200
        assert body.json()["user_type"] == "parent"
        assert body.json()["display_name"] == "Alex Martin"

    def test_no_session_is_refused(self, client: TestClient) -> None:
        assert client.get("/api/v1/auth/session").status_code == 401

    def test_it_carries_no_secret(self, client: TestClient, email: str) -> None:
        """It names the caller; what an account holds is served elsewhere."""
        client.post(
            REGISTER_URL,
            json={
                "email": email,
                "password": VALID_PASSWORD,
                "display_name": "Alex Martin",
            },
        )
        client.post(LOGIN_URL, json={"email": email, "password": VALID_PASSWORD})

        body = client.get("/api/v1/auth/session").json()

        assert set(body) == {"user_type", "id", "display_name"}
        assert email not in str(body)
