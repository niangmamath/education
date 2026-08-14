"""Integration tests for the reconciling import, against real PostgreSQL.

Idempotence is a claim about what the database holds after a second run, so
these tests run the import twice for real rather than inspecting a plan. Every
edition built here carries a test prefix and is deleted afterwards; every label
is fictional.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine, select, text
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.models.referential import (
    VERSION_STATUS_ARCHIVED,
    VERSION_STATUS_DRAFT,
    VERSION_STATUS_PUBLISHED,
    Competency,
    CompetencyPrerequisite,
    Domain,
    Level,
    ReferentialVersion,
    Subject,
)
from app.referential.document import ReferentialDocument, read_json
from app.referential.importer import (
    COMPETENCIES,
    DOMAINS,
    LEVELS,
    PREREQUISITES,
    SUBJECTS,
    ImportRefused,
    ImportReport,
    reconcile,
)
from app.referential.validation import validate_document

TEST_CODE_PREFIX = "test-import-"
SHIPPED_FILE = (
    Path(__file__).resolve().parents[1]
    / "seeds"
    / "referential"
    / "fictif-2026-01.json"
)


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session
        session.rollback()
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM ref_versions WHERE code LIKE :pattern"),
            {"pattern": f"{TEST_CODE_PREFIX}%"},
        )


@pytest.fixture
def version_code() -> str:
    return f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"


def competency(code: str, **overrides: Any) -> dict[str, Any]:
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


def edition(code: str) -> dict[str, Any]:
    """Two levels, one subject, two domains, three competencies, one edge."""
    return {
        "version": {"code": code, "label": "Édition d’essai"},
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
            }
        ],
        "competencies": [
            competency("cp-math-num-01"),
            competency("cp-math-num-02", position=2, prerequisites=["cp-math-num-01"]),
            competency("cp-math-geo-01", domain="math-geo"),
        ],
    }


def run(session: Session, payload: dict[str, Any]) -> ImportReport:
    """Import a payload the way the command does: validated first, then applied."""
    document = ReferentialDocument.model_validate(payload)
    assert validate_document(document) == []
    return reconcile(session, document)


def stored(session: Session, code: str) -> ReferentialVersion:
    version = session.scalars(
        select(ReferentialVersion).where(ReferentialVersion.code == code)
    ).one()
    return version


def codes_of(session: Session, model: Any, version: ReferentialVersion) -> set[str]:
    return {
        row.code
        for row in session.scalars(select(model).where(model.version_id == version.id))
    }


class TestFirstImport:
    def test_it_creates_the_whole_edition(
        self, session: Session, version_code: str
    ) -> None:
        report = run(session, edition(version_code))
        session.commit()

        assert report.version_created is True
        assert report.version_status == VERSION_STATUS_DRAFT
        assert report.counts[LEVELS].created == 2
        assert report.counts[SUBJECTS].created == 1
        assert report.counts[DOMAINS].created == 2
        assert report.counts[COMPETENCIES].created == 3
        assert report.counts[PREREQUISITES].created == 1

    def test_the_rows_land_inside_that_version_only(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        version = stored(session, version_code)
        assert codes_of(session, Level, version) == {"cp", "ce1"}
        assert codes_of(session, Domain, version) == {"math-num", "math-geo"}
        assert codes_of(session, Competency, version) == {
            "cp-math-num-01",
            "cp-math-num-02",
            "cp-math-geo-01",
        }

    def test_an_edition_starts_as_a_draft(
        self, session: Session, version_code: str
    ) -> None:
        """Importing never puts a referential in force; publishing is another act."""
        run(session, edition(version_code))
        session.commit()

        assert stored(session, version_code).status == VERSION_STATUS_DRAFT

    def test_two_editions_may_carry_the_same_codes(self, session: Session) -> None:
        first_code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"
        second_code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"

        run(session, edition(first_code))
        run(session, edition(second_code))
        session.commit()

        first = stored(session, first_code)
        second = stored(session, second_code)
        assert codes_of(session, Competency, first) == codes_of(
            session, Competency, second
        )
        assert first.id != second.id


class TestIdempotence:
    def test_replaying_the_same_file_changes_nothing(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        report = run(session, edition(version_code))
        session.commit()

        assert report.changed is False
        assert report.version_created is False
        assert all(not counts.touched for counts in report.counts.values())

    def test_replaying_leaves_the_same_rows_in_place(
        self, session: Session, version_code: str
    ) -> None:
        """Not merely the same count: the same identifiers, untouched."""
        run(session, edition(version_code))
        session.commit()
        version = stored(session, version_code)
        before = {
            row.code: row.id
            for row in session.scalars(
                select(Competency).where(Competency.version_id == version.id)
            )
        }

        run(session, edition(version_code))
        session.commit()

        after = {
            row.code: row.id
            for row in session.scalars(
                select(Competency).where(Competency.version_id == version.id)
            )
        }
        assert after == before


class TestReconciliation:
    def test_a_new_competency_is_created_and_the_others_are_left_alone(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"].append(
            competency("cp-math-geo-02", domain="math-geo", position=2)
        )
        report = run(session, payload)
        session.commit()

        assert report.counts[COMPETENCIES].created == 1
        assert report.counts[COMPETENCIES].updated == 0
        assert report.counts[COMPETENCIES].deleted == 0

    def test_a_changed_label_is_an_update(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"][0]["label"] = "Intitulé corrigé"
        report = run(session, payload)
        session.commit()

        assert report.counts[COMPETENCIES].updated == 1
        version = stored(session, version_code)
        labels = {
            row.code: row.label
            for row in session.scalars(
                select(Competency).where(Competency.version_id == version.id)
            )
        }
        assert labels["cp-math-num-01"] == "Intitulé corrigé"

    def test_a_competency_absent_from_the_file_is_deleted(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"] = [
            entry
            for entry in payload["competencies"]
            if entry["code"] != "cp-math-geo-01"
        ]
        report = run(session, payload)
        session.commit()

        assert report.counts[COMPETENCIES].deleted == 1
        version = stored(session, version_code)
        assert "cp-math-geo-01" not in codes_of(session, Competency, version)

    def test_a_domain_leaves_with_the_competencies_it_held(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["subjects"][0]["domains"] = [
            entry
            for entry in payload["subjects"][0]["domains"]
            if entry["code"] != "math-geo"
        ]
        payload["competencies"] = [
            entry for entry in payload["competencies"] if entry["domain"] != "math-geo"
        ]
        report = run(session, payload)
        session.commit()

        assert report.counts[DOMAINS].deleted == 1
        assert report.counts[COMPETENCIES].deleted == 1
        version = stored(session, version_code)
        assert codes_of(session, Domain, version) == {"math-num"}

    def test_a_competency_may_move_to_another_domain(
        self, session: Session, version_code: str
    ) -> None:
        """Its code is its identity, so moving it keeps the same row."""
        run(session, edition(version_code))
        session.commit()
        version = stored(session, version_code)
        before = session.scalars(
            select(Competency).where(
                Competency.version_id == version.id,
                Competency.code == "cp-math-num-01",
            )
        ).one()
        original_id = before.id

        payload = edition(version_code)
        payload["competencies"][0]["domain"] = "math-geo"
        payload["competencies"][0]["position"] = 2
        report = run(session, payload)
        session.commit()

        assert report.counts[COMPETENCIES].updated == 1
        assert report.counts[COMPETENCIES].created == 0
        moved = session.scalars(
            select(Competency).where(
                Competency.version_id == version.id,
                Competency.code == "cp-math-num-01",
            )
        ).one()
        assert moved.id == original_id
        assert moved.domain.code == "math-geo"

    def test_a_level_that_is_no_longer_covered_is_deleted(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["levels"] = [
            entry for entry in payload["levels"] if entry["code"] != "ce1"
        ]
        report = run(session, payload)
        session.commit()

        assert report.counts[LEVELS].deleted == 1
        version = stored(session, version_code)
        assert codes_of(session, Level, version) == {"cp"}

    def test_the_version_label_may_be_corrected(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["version"]["label"] = "Édition d’essai, deuxième relecture"
        report = run(session, payload)
        session.commit()

        assert report.version_updated is True
        assert (
            stored(session, version_code).label == "Édition d’essai, deuxième relecture"
        )


class TestPrerequisiteEdges:
    def test_an_edge_is_added(self, session: Session, version_code: str) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"][2]["prerequisites"] = ["cp-math-num-02"]
        report = run(session, payload)
        session.commit()

        assert report.counts[PREREQUISITES].created == 1

    def test_an_edge_the_file_dropped_is_removed(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"][1]["prerequisites"] = []
        report = run(session, payload)
        session.commit()

        assert report.counts[PREREQUISITES].deleted == 1
        version = stored(session, version_code)
        remaining = session.scalars(
            select(CompetencyPrerequisite).where(
                CompetencyPrerequisite.version_id == version.id
            )
        ).all()
        assert remaining == []

    def test_removing_a_competency_removes_the_edges_that_named_it(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()

        payload = edition(version_code)
        payload["competencies"] = [
            entry
            for entry in payload["competencies"]
            if entry["code"] != "cp-math-num-02"
        ]
        report = run(session, payload)
        session.commit()

        assert report.counts[COMPETENCIES].deleted == 1
        assert report.counts[PREREQUISITES].deleted == 1


class TestImmutability:
    @pytest.mark.parametrize(
        "status", [VERSION_STATUS_PUBLISHED, VERSION_STATUS_ARCHIVED]
    )
    def test_a_version_in_force_or_retired_is_refused(
        self, session: Session, version_code: str, status: str
    ) -> None:
        """Traces of later steps point at these competencies; they stay put."""
        run(session, edition(version_code))
        session.commit()
        stored(session, version_code).status = status
        session.commit()

        payload = edition(version_code)
        payload["competencies"][0]["label"] = "Tentative de correction"
        with pytest.raises(ImportRefused) as refusal:
            run(session, payload)
        session.rollback()

        assert refusal.value.status == status
        assert version_code in str(refusal.value)

    def test_the_refused_edition_is_left_untouched(
        self, session: Session, version_code: str
    ) -> None:
        run(session, edition(version_code))
        session.commit()
        stored(session, version_code).status = VERSION_STATUS_PUBLISHED
        session.commit()

        payload = edition(version_code)
        payload["competencies"][0]["label"] = "Tentative de correction"
        with pytest.raises(ImportRefused):
            run(session, payload)
        session.rollback()

        version = stored(session, version_code)
        labels = {
            row.code: row.label
            for row in session.scalars(
                select(Competency).where(Competency.version_id == version.id)
            )
        }
        assert labels["cp-math-num-01"] == "Compétence cp-math-num-01"


class TestDryRun:
    def test_a_rolled_back_import_writes_nothing(
        self, session: Session, engine: Engine, version_code: str
    ) -> None:
        """This is what the command does without `--apply`."""
        report = run(session, edition(version_code))
        session.rollback()

        assert report.counts[COMPETENCIES].created == 3
        with Session(engine) as other:
            assert (
                other.scalars(
                    select(ReferentialVersion).where(
                        ReferentialVersion.code == version_code
                    )
                ).one_or_none()
                is None
            )

    def test_a_dry_run_reports_what_the_real_run_then_does(
        self, session: Session, engine: Engine, version_code: str
    ) -> None:
        dry = run(session, edition(version_code))
        session.rollback()

        applied = run(session, edition(version_code))
        session.commit()

        assert applied.counts[COMPETENCIES].created == dry.counts[COMPETENCIES].created
        assert (
            applied.counts[PREREQUISITES].created == dry.counts[PREREQUISITES].created
        )
        assert applied.version_created == dry.version_created


class TestShippedReferential:
    def test_it_imports_and_replays_without_a_change(self, session: Session) -> None:
        """The file the project ships is exercised, not merely parsed."""
        payload = read_json(SHIPPED_FILE)
        payload["version"]["code"] = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"

        first = run(session, payload)
        session.commit()
        second = run(session, payload)
        session.commit()

        assert first.counts[COMPETENCIES].created == len(payload["competencies"])
        assert second.changed is False

        version = stored(session, payload["version"]["code"])
        assert len(codes_of(session, Subject, version)) == 2
        assert len(codes_of(session, Level, version)) == 5
