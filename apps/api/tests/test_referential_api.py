"""Integration tests for the referential read routes.

These go through the real API with real sessions: authorisation is only real
once a request without a cookie is actually refused, and the edition served is
only real once PostgreSQL holds a published one.

The edition already in force on the machine, if any, is stepped aside for the
duration and put back afterwards, so the suite neither depends on the local
state nor destroys it. Every address belongs to `example.com`, reserved by
RFC 2606.
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
from app.models.referential import VERSION_STATUS_DRAFT
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.referential.publication import publish, published_version
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-api-"
TEST_EMAIL_DOMAIN = "example.com"
PASSWORD = "correct-horse-battery"
PIN = "428173"

EDITION_URL = "/api/v1/referential/edition"
LEVELS_URL = "/api/v1/referential/levels"
SUBJECTS_URL = "/api/v1/referential/subjects"
COMPETENCIES_URL = "/api/v1/referential/competencies"


def document(code: str) -> dict[str, Any]:
    """Two levels, two subjects, three domains, five competencies."""
    return {
        "version": {"code": code, "label": "Édition servie par l’API"},
        "levels": [
            {"code": "cp", "label": "Cours préparatoire", "position": 1},
            {"code": "ce1", "label": "Cours élémentaire", "position": 2},
        ],
        "subjects": [
            {
                "code": "math",
                "label": "Mathématiques",
                "position": 1,
                "domains": [
                    {"code": "math-num", "label": "Nombres et calcul", "position": 1},
                    {"code": "math-geo", "label": "Espace et géométrie", "position": 2},
                ],
            },
            {
                "code": "fr",
                "label": "Français",
                "position": 2,
                "domains": [
                    {"code": "fr-lec", "label": "Lecture", "position": 1},
                ],
            },
        ],
        "competencies": [
            _competency("cp-math-num-01", position=1),
            _competency("cp-math-num-02", position=2),
            _competency("ce1-math-num-01", level="ce1", position=1),
            _competency("cp-math-geo-01", domain="math-geo", position=1),
            _competency("cp-fr-lec-01", domain="fr-lec", position=1),
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
def edition_code(engine: Engine) -> Iterator[str]:
    """Put a known edition in force, and give the machine its own one back."""
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"

    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            reconcile(session, ReferentialDocument.model_validate(document(code)))
            publish(session, code)
            session.commit()

        yield code


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def parent(client: TestClient) -> dict[str, str]:
    """A registered, logged-in parent; the client keeps the session cookie."""
    email = f"ref-{uuid.uuid4().hex}@{TEST_EMAIL_DOMAIN}"
    created = client.post(
        "/api/v1/auth/parent/register",
        json={"email": email, "password": PASSWORD, "display_name": "Parent Lecture"},
    )
    assert created.status_code == 201

    # Registering does not open a session; logging in is what hands the cookie.
    logged_in = client.post(
        "/api/v1/auth/parent/login", json={"email": email, "password": PASSWORD}
    )
    assert logged_in.status_code == 200

    return {"email": email, "family_code": created.json()["family_code"]}


@pytest.fixture
def child_client(client: TestClient, parent: dict[str, str]) -> TestClient:
    """The same client, its parent session traded for an active child's.

    One client and not two: each `TestClient` runs its own event loop, and the
    application's async engine pools connections against the loop that opened
    them. A second client nested inside the first leaves asyncpg holding sockets
    bound to a loop that is gone.
    """
    pseudonym = f"lea{uuid.uuid4().hex[:6]}"
    created = client.post(
        "/api/v1/auth/children",
        json={"pseudonym": pseudonym, "pin": PIN, "display_name": "Léa"},
    )
    assert created.status_code == 201
    activated = client.post(f"/api/v1/auth/children/{created.json()['id']}/activate")
    assert activated.status_code == 200

    # The login cookie has the same name, so this replaces the parent's session.
    logged_in = client.post(
        "/api/v1/auth/child/login",
        json={
            "family_code": parent["family_code"],
            "pseudonym": pseudonym,
            "pin": PIN,
        },
    )
    assert logged_in.status_code == 200
    return client


class TestAuthorisation:
    @pytest.mark.parametrize(
        "url", [EDITION_URL, LEVELS_URL, SUBJECTS_URL, COMPETENCIES_URL]
    )
    def test_a_request_without_a_session_is_refused(
        self, client: TestClient, edition_code: str, url: str
    ) -> None:
        assert client.get(url).status_code == 401

    def test_a_parent_may_read(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        assert client.get(LEVELS_URL).status_code == 200

    def test_a_child_may_read_the_same_routes(
        self, child_client: TestClient, edition_code: str
    ) -> None:
        """The referential is not personal data, and the Élève space needs it."""
        response = child_client.get(COMPETENCIES_URL)

        assert response.status_code == 200
        assert response.json()["total"] == 5


class TestEditionServed:
    def test_the_edition_in_force_is_named(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        response = client.get(EDITION_URL)

        assert response.status_code == 200
        assert response.json()["code"] == edition_code

    def test_every_listing_says_which_edition_it_read(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        """A client holding a list can tell whether it is still the current one."""
        for url in (LEVELS_URL, SUBJECTS_URL, COMPETENCIES_URL):
            assert client.get(url).json()["edition"]["code"] == edition_code

    def test_a_draft_is_never_served(
        self,
        client: TestClient,
        parent: dict[str, str],
        edition_code: str,
        engine: Engine,
    ) -> None:
        """Work in progress stays out of HTTP, whatever it holds."""
        draft_code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"
        with Session(engine) as session:
            payload = document(draft_code)
            payload["competencies"].append(_competency("cp-math-num-99", position=9))
            reconcile(session, ReferentialDocument.model_validate(payload))
            session.commit()

        response = client.get(COMPETENCIES_URL)

        assert response.json()["edition"]["code"] == edition_code
        assert response.json()["total"] == 5
        codes = {item["code"] for item in response.json()["items"]}
        assert "cp-math-num-99" not in codes


class TestListings:
    def test_levels_come_in_school_order(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        body = client.get(LEVELS_URL).json()

        assert [item["code"] for item in body["items"]] == ["cp", "ce1"]
        assert body["total"] == 2

    def test_a_subject_carries_its_domains(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        body = client.get(SUBJECTS_URL).json()

        maths = body["items"][0]
        assert maths["code"] == "math"
        assert [domain["code"] for domain in maths["domains"]] == [
            "math-num",
            "math-geo",
        ]

    def test_a_competency_names_its_level_domain_and_subject(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        body = client.get(COMPETENCIES_URL, params={"domain": "fr-lec"}).json()

        assert body["items"] == [
            {
                "code": "cp-fr-lec-01",
                "label": "Compétence cp-fr-lec-01",
                "description": None,
                "position": 1,
                "level": "cp",
                "domain": "fr-lec",
                "subject": "fr",
            }
        ]

    def test_the_prerequisite_tree_is_not_exposed(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        """Modelled since 07.1, it belongs to the remediation of step 12."""
        item = client.get(COMPETENCIES_URL).json()["items"][0]

        assert "prerequisites" not in item


class TestFilters:
    @pytest.mark.parametrize(
        ("filters", "expected"),
        [
            ({"level": "cp"}, 4),
            ({"level": "ce1"}, 1),
            ({"subject": "math"}, 4),
            ({"subject": "fr"}, 1),
            ({"domain": "math-num"}, 3),
            ({"level": "cp", "domain": "math-num"}, 2),
            ({"level": "ce1", "subject": "fr"}, 0),
        ],
    )
    def test_filters_narrow_the_listing(
        self,
        client: TestClient,
        parent: dict[str, str],
        edition_code: str,
        filters: dict[str, str],
        expected: int,
    ) -> None:
        body = client.get(COMPETENCIES_URL, params=filters).json()

        assert body["total"] == expected
        assert len(body["items"]) == expected

    def test_an_unknown_code_narrows_to_nothing_rather_than_failing(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        response = client.get(COMPETENCIES_URL, params={"level": "cm2"})

        assert response.status_code == 200
        assert response.json()["total"] == 0


class TestPagination:
    def test_a_page_holds_what_it_was_asked_for(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        body = client.get(COMPETENCIES_URL, params={"page_size": 2}).json()

        assert len(body["items"]) == 2
        assert body["total"] == 5
        assert body["page"] == 1

    def test_the_pages_together_hold_everything_exactly_once(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        """Ordering must be total, or a row would be seen twice or not at all."""
        seen: list[str] = []
        for page in (1, 2, 3):
            body = client.get(
                COMPETENCIES_URL, params={"page": page, "page_size": 2}
            ).json()
            seen += [item["code"] for item in body["items"]]

        assert len(seen) == 5
        assert len(set(seen)) == 5

    def test_a_page_beyond_the_last_is_empty_and_still_counts(
        self, client: TestClient, parent: dict[str, str], edition_code: str
    ) -> None:
        body = client.get(COMPETENCIES_URL, params={"page": 9}).json()

        assert body["items"] == []
        assert body["total"] == 5

    @pytest.mark.parametrize(
        "params", [{"page": 0}, {"page": -1}, {"page_size": 0}, {"page_size": 101}]
    )
    def test_a_page_outside_the_bounds_is_refused(
        self,
        client: TestClient,
        parent: dict[str, str],
        edition_code: str,
        params: dict[str, int],
    ) -> None:
        assert client.get(COMPETENCIES_URL, params=params).status_code == 422


class TestNoEditionInForce:
    def test_listings_answer_empty_and_say_so(
        self, client: TestClient, parent: dict[str, str], engine: Engine
    ) -> None:
        """No published edition is not an error: there simply is none yet."""
        with Session(engine) as session:
            incumbent = published_version(session)
            incumbent_code = incumbent.code if incumbent is not None else None
            if incumbent is not None:
                incumbent.status = VERSION_STATUS_DRAFT
                session.commit()

        try:
            body = client.get(LEVELS_URL).json()
            assert body["edition"] is None
            assert body["items"] == []
            assert body["total"] == 0
            assert client.get(EDITION_URL).status_code == 404
        finally:
            if incumbent_code is not None:
                with engine.begin() as connection:
                    connection.execute(
                        text(
                            "UPDATE ref_versions SET status = 'published' "
                            "WHERE code = :code"
                        ),
                        {"code": incumbent_code},
                    )
