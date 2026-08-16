"""Diagnostic and remediation, through the real API.

The competency tree is real here: an edition is put in force for the duration,
with two domains and a prerequisite between two competencies, because grouping
gaps and proposing which one sits underneath another are exactly what a tree is
for. The edition already on the machine is stepped aside and put back, as
elsewhere.

Gaps are produced the long way round — an activity is given, started, answered
wrongly and finished — so that what is diagnosed is what the platform actually
recorded, and not a row inserted to make a test pass.
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
)
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.referential.publication import publish
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-dia-"
RUN = uuid.uuid4().hex[:8]

# Two competencies in one domain, one in another, and B requires A. That shape
# is what makes a general gap and a root-cause hypothesis possible at all.
COMP_A = f"{RUN}-num-a"
COMP_B = f"{RUN}-num-b"
COMP_C = f"{RUN}-lec-c"

PASSWORD = "correct-horse-battery"
PIN = "428173"

ASSIGNMENTS_URL = "/api/v1/assignments"
MY_ACTIVITIES_URL = "/api/v1/me/activities"
MY_ATTEMPTS_URL = "/api/v1/me/attempts"
NEXT_STEPS_URL = "/api/v1/me/next-steps"
RULES_URL = "/api/v1/diagnostic/rules"

# Long enough not to be a Quick Repair: these create the gaps, they do not fix
# them. The repairs are the short ones.
LONG = 20
SHORT_A = 5
SHORT_B = 4


def document(code: str) -> dict[str, Any]:
    return {
        "version": {"code": code, "label": "Édition du diagnostic"},
        "levels": [{"code": "cp", "label": "Cours préparatoire", "position": 1}],
        "subjects": [
            {
                "code": "math",
                "label": "Mathématiques",
                "position": 1,
                "domains": [
                    {"code": "math-num", "label": "Nombres et calcul", "position": 1}
                ],
            },
            {
                "code": "fr",
                "label": "Français",
                "position": 2,
                "domains": [{"code": "fr-lec", "label": "Lecture", "position": 1}],
            },
        ],
        "competencies": [
            _competency(COMP_A, position=1),
            _competency(COMP_B, position=2, prerequisites=[COMP_A]),
            _competency(COMP_C, position=1, domain="fr-lec"),
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
def catalogue(engine: Engine) -> Iterator[dict[str, str]]:
    """An edition in force, and five activities: three long, two short."""
    edition = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"
    codes = {
        "a_source": f"{TEST_CODE_PREFIX}a-src-{RUN}",
        "a_repair": f"{TEST_CODE_PREFIX}a-fix-{RUN}",
        "b_source": f"{TEST_CODE_PREFIX}b-src-{RUN}",
        "b_repair": f"{TEST_CODE_PREFIX}b-fix-{RUN}",
        "c_source": f"{TEST_CODE_PREFIX}c-src-{RUN}",
    }
    plan = [
        (codes["a_source"], COMP_A, LONG),
        (codes["a_repair"], COMP_A, SHORT_A),
        (codes["b_source"], COMP_B, LONG),
        (codes["b_repair"], COMP_B, SHORT_B),
        # Deliberately no short activity for C: a competency the catalogue
        # cannot repair must produce a gap and no recommendation.
        (codes["c_source"], COMP_C, LONG),
    ]

    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            reconcile(session, ReferentialDocument.model_validate(document(edition)))
            publish(session, edition)
            for code, competency, minutes in plan:
                row = Activity(
                    code=code,
                    title=f"Activité {code}",
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=minutes,
                )
                session.add(row)
                session.flush()
                session.add(
                    ActivityCompetency(activity_id=row.id, competency_code=competency)
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
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


class Family:
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"dia-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Diagnostic",
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

    @property
    def diagnostic_url(self) -> str:
        return f"/api/v1/children/{self.child_id}/diagnostic"


@pytest.fixture
def family(client: TestClient) -> Family:
    return Family(client)


def work_through(family: Family, activity_code: str, correct: bool) -> None:
    """Give an activity, do it, answer once and finish it.

    One evaluated answer is enough: all-correct reads as mastered, all-wrong as
    not mastered, and both are what the rules of step 10 already guarantee.
    """
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
    attempt_id = attempt.json()["id"]
    posted = child.post(
        f"{MY_ATTEMPTS_URL}/{attempt_id}/responses",
        json={"question_ref": "q1", "response": "vrai", "is_correct": correct},
    )
    assert posted.status_code == 201, posted.text
    assert child.post(f"{MY_ATTEMPTS_URL}/{attempt_id}/complete").status_code == 200


def gap_for(body: dict[str, Any], code: str) -> dict[str, Any] | None:
    return next(
        (row for row in body["localized_gaps"] if row["competency_code"] == code), None
    )


class TestALocalizedGapIsACandidate:
    def test_a_competency_read_as_not_mastered_becomes_a_gap(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        gap = gap_for(body, COMP_A)
        assert gap is not None
        assert gap["rule_code"] == "gap-not-mastered"

    def test_a_mastered_competency_is_not_a_gap(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=True)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert gap_for(body, COMP_A) is None

    def test_a_competency_nobody_worked_on_is_not_a_gap(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """Filing a silence under difficulty would turn an absence into a charge."""
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert gap_for(body, COMP_C) is None

    def test_a_gap_carries_the_rule_the_counts_and_a_sentence(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        gap = gap_for(family.as_parent().get(family.diagnostic_url).json(), COMP_A)

        assert gap is not None
        assert gap["answered"] == 1 and gap["correct"] == 0
        assert COMP_A in gap["explanation"]
        assert "à confirmer" in gap["explanation"]

    def test_the_gap_is_placed_in_the_edition_in_force(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        gap = gap_for(family.as_parent().get(family.diagnostic_url).json(), COMP_A)

        assert gap is not None
        assert gap["domain_code"] == "math-num"
        assert gap["domain_label"] == "Nombres et calcul"


class TestAGeneralGapGroupsWithoutRemoving:
    def test_two_gaps_in_one_domain_are_also_read_together(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)
        work_through(family, catalogue["b_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        general = [
            row for row in body["general_gaps"] if row["domain_code"] == "math-num"
        ]
        assert len(general) == 1
        assert sorted(general[0]["competency_codes"]) == sorted([COMP_A, COMP_B])

    def test_the_localized_gaps_are_still_listed_one_by_one(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """The project rule is that grouping never removes what it groups."""
        work_through(family, catalogue["a_source"], correct=False)
        work_through(family, catalogue["b_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert gap_for(body, COMP_A) is not None
        assert gap_for(body, COMP_B) is not None

    def test_one_gap_alone_is_not_a_pattern(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert body["general_gaps"] == []


class TestARootCauseStaysAHypothesis:
    def test_a_prerequisite_in_difficulty_is_proposed_as_the_cause(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)
        work_through(family, catalogue["b_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert len(body["root_causes"]) == 1
        cause = body["root_causes"][0]
        assert cause["competency_code"] == COMP_A
        assert cause["explains_codes"] == [COMP_B]

    def test_it_is_never_marked_as_established(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)
        work_through(family, catalogue["b_source"], correct=False)

        cause = family.as_parent().get(family.diagnostic_url).json()["root_causes"][0]

        assert cause["confirmed"] is False
        assert "hypothèse" in cause["explanation"]
        assert "réévaluation" in cause["explanation"]

    def test_a_mastered_prerequisite_explains_nothing(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """Evidence against the hypothesis is not evidence for it."""
        work_through(family, catalogue["a_source"], correct=True)
        work_through(family, catalogue["b_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert body["root_causes"] == []
        assert gap_for(body, COMP_B) is not None


class TestQuickRepairsAreShortAndProvable:
    def test_a_repair_is_proposed_for_a_gap(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        proposed = [row["activity_code"] for row in body["recommendations"]]
        assert proposed == [catalogue["a_repair"]]

    def test_an_activity_outside_the_band_is_never_a_quick_repair(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """C has a gap and only a twenty-minute activity; nothing is proposed."""
        work_through(family, catalogue["c_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert gap_for(body, COMP_C) is not None
        assert body["recommendations"] == []

    def test_every_recommendation_names_its_proof(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        recommendation = (
            family.as_parent().get(family.diagnostic_url).json()["recommendations"][0]
        )

        assert "preuve finale" in recommendation["proof"]
        assert recommendation["duration_minutes"] == SHORT_A
        assert recommendation["already_done"] is False

    def test_the_root_cause_is_proposed_first(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """Starting underneath is the whole point of having looked."""
        work_through(family, catalogue["b_source"], correct=False)
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert [row["competency_code"] for row in body["recommendations"]] == [
            COMP_A,
            COMP_B,
        ]

    def test_an_activity_already_waiting_is_not_proposed_again(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)
        given = family.as_parent().post(
            ASSIGNMENTS_URL,
            json={
                "child_id": family.child_id,
                "activity_code": catalogue["a_repair"],
            },
        )
        assert given.status_code == 201

        body = family.as_parent().get(family.diagnostic_url).json()

        assert body["recommendations"] == []

    def test_an_activity_already_done_is_proposed_again_but_flagged(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_repair"], correct=False)

        body = family.as_parent().get(family.diagnostic_url).json()

        recommendation = body["recommendations"][0]
        assert recommendation["activity_code"] == catalogue["a_repair"]
        assert recommendation["already_done"] is True
        assert "seconde passe" in recommendation["reason"]


class TestTheHealthScoreIsShownWithItsTerms:
    def test_nothing_observed_yields_no_score_at_all(self, family: Family) -> None:
        body = family.as_parent().get(family.diagnostic_url).json()

        assert body["health"] is None

    def test_the_score_carries_every_term_it_was_made_of(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=True)
        work_through(family, catalogue["b_source"], correct=False)

        health = family.as_parent().get(family.diagnostic_url).json()["health"]

        assert health["observed"] == 2
        assert health["mastered"] == 1 and health["not_mastered"] == 1
        assert health["score"] == 50
        assert health["rule_code"] == "health-weighted-outcomes"

    def test_it_compares_this_child_to_nobody(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=True)

        body = family.as_parent().get(family.diagnostic_url).json()

        assert "ne compare cet enfant à personne" in body["health"]["explanation"]
        forbidden = {"rank", "percentile", "average", "moyenne", "classement", "cohort"}
        assert not forbidden & set(body["health"])


class TestWhatEachSideIsShown:
    def test_a_child_is_shown_actions_and_no_diagnosis(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)

        body = family.as_child().get(NEXT_STEPS_URL).json()

        assert [row["activity_code"] for row in body["steps"]] == [
            catalogue["a_repair"]
        ]
        assert "health" not in body
        assert "localized_gaps" not in body
        assert "rule_code" not in body["steps"][0]
        assert COMP_A not in str(body)

    def test_a_child_may_not_read_the_diagnostic(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        assert family.as_child().get(family.diagnostic_url).status_code == 403

    def test_a_parent_may_not_read_the_child_route(self, family: Family) -> None:
        assert family.as_parent().get(NEXT_STEPS_URL).status_code == 403

    def test_another_familys_child_does_not_exist(
        self, client: TestClient, catalogue: dict[str, str]
    ) -> None:
        first = Family(client)
        second = Family(client)

        refused = second.as_parent().get(first.diagnostic_url)

        assert refused.status_code == 404


class TestTheRulesArePublished:
    def test_a_parent_may_read_them(self, family: Family) -> None:
        published = family.as_parent().get(RULES_URL)

        assert published.status_code == 200
        assert len(published.json()) == 5

    def test_a_child_may_read_them_too(self, family: Family) -> None:
        """Published behind a door only one side opens would publish to nobody."""
        assert family.as_child().get(RULES_URL).status_code == 200

    def test_they_are_refused_without_a_session(self, client: TestClient) -> None:
        assert client.get(RULES_URL).status_code == 401


class TestTheDiagnosticIsRecomputedAtEveryRead:
    def test_reading_twice_gives_the_same_answer(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        work_through(family, catalogue["a_source"], correct=False)
        parent = family.as_parent()

        first = parent.get(family.diagnostic_url).json()
        again = parent.get(family.diagnostic_url).json()

        first.pop("computed_at")
        again.pop("computed_at")
        assert first == again

    def test_new_evidence_changes_it_without_anything_being_refreshed(
        self, family: Family, catalogue: dict[str, str]
    ) -> None:
        """A root cause is a hypothesis until re-evaluation; this is what that means."""
        work_through(family, catalogue["a_source"], correct=False)
        work_through(family, catalogue["b_source"], correct=False)
        assert (
            len(family.as_parent().get(family.diagnostic_url).json()["root_causes"])
            == 1
        )

        work_through(family, catalogue["a_repair"], correct=True)

        body = family.as_parent().get(family.diagnostic_url).json()
        assert body["root_causes"] == []
        assert gap_for(body, COMP_A) is None
