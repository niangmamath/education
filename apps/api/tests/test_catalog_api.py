"""Integration tests for the catalogue read routes.

Through the real API with real sessions: authorisation is only real once a
request without a cookie is refused, and a draft is only hidden once the route
actually hides it.

Every activity built here carries a test prefix and is removed afterwards. Every
address belongs to `example.com`, reserved by RFC 2606.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.main import app
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_KIND_PHET,
    ACTIVITY_KIND_VIDEO,
    ACTIVITY_STATUS_ARCHIVED,
    ACTIVITY_STATUS_DRAFT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    H5PPackage,
)

TEST_CODE_PREFIX = "test-capi-"
# Drawn per run: a fixed code would be shared with whatever else the database
# happens to hold, and these tests filter on it.
COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
OTHER_COMPETENCY = f"test-comp-{uuid.uuid4().hex[:8]}"
PASSWORD = "correct-horse-battery"
PIN = "428173"

ACTIVITIES_URL = "/api/v1/catalog/activities"
KINDS_URL = "/api/v1/catalog/kinds"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def catalogue(engine: Engine) -> Iterator[dict[str, str]]:
    """A small catalogue: four published activities, one draft, one archived."""
    codes = {
        name: f"{TEST_CODE_PREFIX}{name}"
        for name in ("court", "long", "phet", "video", "brouillon", "archive")
    }

    with Session(engine) as session:
        rows = [
            Activity(
                code=codes["court"],
                title="Quick Repair, addition",
                summary="Trois minutes sur l’addition posée.",
                kind=ACTIVITY_KIND_H5P,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=3,
            ),
            Activity(
                code=codes["long"],
                title="Séance longue, numération",
                kind=ACTIVITY_KIND_H5P,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=25,
            ),
            Activity(
                code=codes["phet"],
                title="Simulation des fractions",
                kind=ACTIVITY_KIND_PHET,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=10,
            ),
            Activity(
                code=codes["video"],
                title="Vidéo, poser une division",
                kind=ACTIVITY_KIND_VIDEO,
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
            Activity(
                code=codes["archive"],
                title="Retirée du service",
                kind=ACTIVITY_KIND_H5P,
                status=ACTIVITY_STATUS_ARCHIVED,
                duration_minutes=5,
            ),
        ]
        session.add_all(rows)
        session.flush()

        by_code = {row.code: row for row in rows}
        session.add_all(
            [
                ActivityCompetency(
                    activity_id=by_code[codes["court"]].id,
                    competency_code=COMPETENCY,
                ),
                ActivityCompetency(
                    activity_id=by_code[codes["court"]].id,
                    competency_code=OTHER_COMPETENCY,
                ),
                ActivityCompetency(
                    activity_id=by_code[codes["long"]].id,
                    competency_code=COMPETENCY,
                ),
                ActivityCompetency(
                    activity_id=by_code[codes["brouillon"]].id,
                    competency_code=COMPETENCY,
                ),
            ]
        )
        session.add(
            H5PPackage(
                activity_id=by_code[codes["court"]].id,
                library_name="H5P.TrueFalse",
                library_version="1.8",
                object_key="packages/essai.h5p",
                sha256=uuid.uuid4().hex + uuid.uuid4().hex,
                size_bytes=4096,
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )
        )
        session.commit()

    yield codes

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM catalog_activities WHERE code LIKE :pattern"),
            {"pattern": f"{TEST_CODE_PREFIX}%"},
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def parent(client: TestClient) -> dict[str, str]:
    email = f"cat-{uuid.uuid4().hex}@example.com"
    created = client.post(
        "/api/v1/auth/parent/register",
        json={"email": email, "password": PASSWORD, "display_name": "Parent Catalogue"},
    )
    assert created.status_code == 201
    logged_in = client.post(
        "/api/v1/auth/parent/login", json={"email": email, "password": PASSWORD}
    )
    assert logged_in.status_code == 200
    return {"email": email, "family_code": created.json()["family_code"]}


@pytest.fixture
def child_client(client: TestClient, parent: dict[str, str]) -> TestClient:
    """The same client, its parent session traded for an active child's."""
    pseudonym = f"lea{uuid.uuid4().hex[:6]}"
    created = client.post(
        "/api/v1/auth/children",
        json={"pseudonym": pseudonym, "pin": PIN, "display_name": "Léa"},
    )
    assert created.status_code == 201
    assert (
        client.post(
            f"/api/v1/auth/children/{created.json()['id']}/activate"
        ).status_code
        == 200
    )
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


def codes_of(response_body: dict[str, object]) -> list[str]:
    items = response_body["items"]
    assert isinstance(items, list)
    return [item["code"] for item in items]


class TestAuthorisation:
    def test_a_request_without_a_session_is_refused(
        self, client: TestClient, catalogue: dict[str, str]
    ) -> None:
        for url in (ACTIVITIES_URL, KINDS_URL, f"{ACTIVITIES_URL}/whatever"):
            assert client.get(url).status_code == 401

    def test_a_parent_may_read(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        assert client.get(ACTIVITIES_URL).status_code == 200

    def test_a_child_may_read_the_same_routes(
        self, child_client: TestClient, catalogue: dict[str, str]
    ) -> None:
        """The Élève space needs the catalogue as much as the Parent space."""
        response = child_client.get(ACTIVITIES_URL)

        assert response.status_code == 200
        assert catalogue["court"] in codes_of(response.json())


class TestWhatIsServed:
    def test_only_published_activities_are_listed(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        listed = codes_of(client.get(ACTIVITIES_URL, params={"page_size": 100}).json())

        assert catalogue["court"] in listed
        assert catalogue["brouillon"] not in listed
        assert catalogue["archive"] not in listed

    @pytest.mark.parametrize("hidden", ["brouillon", "archive"])
    def test_an_unpublished_activity_answers_like_one_that_does_not_exist(
        self,
        client: TestClient,
        parent: dict[str, str],
        catalogue: dict[str, str],
        hidden: str,
    ) -> None:
        """Whether something is being prepared is not a client's business."""
        prepared = client.get(f"{ACTIVITIES_URL}/{catalogue[hidden]}")
        absent = client.get(f"{ACTIVITIES_URL}/{TEST_CODE_PREFIX}jamais-vue")

        assert prepared.status_code == absent.status_code == 404

    def test_an_activity_names_the_competencies_it_works_on(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(f"{ACTIVITIES_URL}/{catalogue['court']}").json()

        assert body["competencies"] == sorted([COMPETENCY, OTHER_COMPETENCY])
        assert body["duration_minutes"] == 3

    def test_an_h5p_activity_says_what_it_plays_and_not_where_it_lives(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        """No bucket path belongs in a client's hands, by ADR-008 and ADR-012."""
        body = client.get(f"{ACTIVITIES_URL}/{catalogue['court']}").json()

        assert body["h5p"] == {
            "library_name": "H5P.TrueFalse",
            "library_version": "1.8",
        }
        serialised = str(body)
        for leaked in ("object_key", "sha256", "packages/", "licence", "source"):
            assert leaked not in serialised

    def test_an_activity_without_a_package_says_so(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(f"{ACTIVITIES_URL}/{catalogue['phet']}").json()

        assert body["h5p"] is None
        assert body["kind"] == "phet"

    def test_the_kinds_are_served_so_a_client_need_not_hard_code_them(
        self, client: TestClient, parent: dict[str, str]
    ) -> None:
        """The initiation assessment is a kind, and deliberately not offered here:
        nobody browses for it and nobody gives it."""
        assert client.get(KINDS_URL).json() == ["h5p", "phet", "video"]


class TestFilters:
    def test_filtering_by_competency_finds_what_repairs_it(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        """The question step 12 will ask, and the reason for the index on the code."""
        body = client.get(ACTIVITIES_URL, params={"competency": COMPETENCY}).json()

        assert set(codes_of(body)) == {catalogue["court"], catalogue["long"]}
        assert body["total"] == 2

    def test_a_draft_is_not_found_by_a_competency_filter_either(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(ACTIVITIES_URL, params={"competency": COMPETENCY}).json()

        assert catalogue["brouillon"] not in codes_of(body)

    def test_an_activity_on_two_competencies_is_counted_once(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(ACTIVITIES_URL, params={"page_size": 100}).json()

        assert codes_of(body).count(catalogue["court"]) == 1

    def test_filtering_by_kind(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(
            ACTIVITIES_URL, params={"kind": "phet", "page_size": 100}
        ).json()

        assert codes_of(body) == [catalogue["phet"]]

    def test_a_quick_repair_filter_leaves_the_long_ones_out(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        """Three to seven minutes is a product rule, so it is a query parameter."""
        body = client.get(
            ACTIVITIES_URL, params={"max_duration": 7, "page_size": 100}
        ).json()

        listed = codes_of(body)
        assert catalogue["court"] in listed
        assert catalogue["video"] in listed
        assert catalogue["long"] not in listed

    def test_filters_combine(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(
            ACTIVITIES_URL,
            params={"competency": COMPETENCY, "max_duration": 7},
        ).json()

        assert codes_of(body) == [catalogue["court"]]

    def test_an_unknown_competency_narrows_to_nothing_rather_than_failing(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        response = client.get(ACTIVITIES_URL, params={"competency": "jamais-vue-01"})

        assert response.status_code == 200
        assert response.json()["total"] == 0

    @pytest.mark.parametrize(
        "params",
        [{"kind": "quiz"}, {"max_duration": 0}, {"max_duration": 61}, {"page": 0}],
    )
    def test_a_parameter_outside_the_bounds_is_refused(
        self,
        client: TestClient,
        parent: dict[str, str],
        catalogue: dict[str, str],
        params: dict[str, object],
    ) -> None:
        assert client.get(ACTIVITIES_URL, params=params).status_code == 422


class TestPagination:
    def test_the_pages_together_hold_everything_exactly_once(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        """Ordering is total — duration then code — so nothing shifts between pages."""
        seen: list[str] = []
        for page in (1, 2, 3, 4):
            body = client.get(
                ACTIVITIES_URL,
                params={"page": page, "page_size": 1, "competency": COMPETENCY},
            ).json()
            seen += codes_of(body)

        published = [code for code in seen if code.startswith(TEST_CODE_PREFIX)]
        assert len(published) == len(set(published)) == 2

    def test_a_page_beyond_the_last_is_empty_and_still_counts(
        self, client: TestClient, parent: dict[str, str], catalogue: dict[str, str]
    ) -> None:
        body = client.get(
            ACTIVITIES_URL, params={"page": 99, "competency": COMPETENCY}
        ).json()

        assert body["items"] == []
        assert body["total"] == 2
