"""Integration tests for the public, unauthenticated stats route.

Counts only, across the whole database rather than one family's slice, so a
test cannot assert an exact number without owning every other row already
there. What it can assert: the route needs no session, the shape is right,
and registering a family moves the count that counts it.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text

from app.core.db import DATABASE_URL
from app.main import app

TEST_EMAIL_DOMAIN = "example.com"
TEST_EMAIL_PREFIX = "public-stats-"
STATS_URL = "/api/v1/public/stats"
REGISTER_URL = "/api/v1/auth/parent/register"


@pytest.fixture(scope="module")
def sync_engine() -> Iterator[Engine]:
    engine = create_engine(
        DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    )
    yield engine
    engine.dispose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_test_parents(sync_engine: Engine) -> Iterator[None]:
    yield
    with sync_engine.begin() as connection:
        connection.execute(
            text("DELETE FROM auth_parents WHERE email LIKE :pattern"),
            {"pattern": f"{TEST_EMAIL_PREFIX}%@{TEST_EMAIL_DOMAIN}"},
        )


class TestPublicStats:
    def test_no_session_is_needed(self, client: TestClient) -> None:
        assert client.get(STATS_URL).status_code == 200

    def test_the_shape_is_all_counts(self, client: TestClient) -> None:
        body = client.get(STATS_URL).json()

        assert set(body) == {
            "families",
            "children",
            "activities_completed",
            "competencies_covered",
            "competencies_total",
        }
        assert all(isinstance(value, int) and value >= 0 for value in body.values())

    def test_a_new_family_moves_the_family_count(self, client: TestClient) -> None:
        before = client.get(STATS_URL).json()["families"]

        client.post(
            REGISTER_URL,
            json={
                "email": f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}",
                "password": "correct-horse-battery",
                "display_name": "Parent de test",
            },
        )

        after = client.get(STATS_URL).json()["families"]
        assert after == before + 1
