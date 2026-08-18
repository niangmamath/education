"""Registering a package, and finding the links ADR-013 cannot protect.

Registration goes through real PostgreSQL, because what it must never leave
behind is a row without a file or a file without a row. Storage is a stand-in
that records what it was asked to do: the point is the order of operations, not
the bucket.
"""

from __future__ import annotations

import json
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.catalog.checks import check_catalogue
from app.catalog.h5p import PackageRefused
from app.catalog.registration import (
    RegistrationRefused,
    register_package,
    unregister_package,
)
from app.core.db import sync_database_url
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_KIND_PHET,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.referential.publication import publish
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-reg-"


class RecordingStore:
    """A stand-in bucket that remembers what it was asked to hold."""

    def __init__(self, fail_on_put: bool = False) -> None:
        self.objects: dict[str, int] = {}
        self.removed: list[str] = []
        self.fail_on_put = fail_on_put

    def put(self, key: str, path: Path) -> None:
        if self.fail_on_put:
            raise OSError("bucket injoignable")
        self.objects[key] = path.stat().st_size

    def remove(self, key: str) -> None:
        self.objects.pop(key, None)
        self.removed.append(key)


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            yield session
            session.rollback()
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM catalog_activities WHERE code LIKE :pattern"),
                {"pattern": f"{TEST_CODE_PREFIX}%"},
            )


@pytest.fixture
def store() -> RecordingStore:
    return RecordingStore()


def package_file(path: Path, library: str = "H5P.TrueFalse", minor: str = "8") -> Path:
    manifest: dict[str, Any] = {
        "title": "Question d’essai",
        "mainLibrary": library,
        "license": "U",
        "preloadedDependencies": [
            {"machineName": library, "majorVersion": "1", "minorVersion": minor}
        ],
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("h5p.json", json.dumps(manifest))
        archive.writestr("content/content.json", json.dumps({"correct": "true"}))
    return path


def build_activity(session: Session, **overrides: object) -> Activity:
    values: dict[str, object] = {
        "code": f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}",
        "title": "Activité d’essai",
        "kind": ACTIVITY_KIND_H5P,
        "duration_minutes": 5,
    }
    values.update(overrides)
    row = Activity(**values)
    session.add(row)
    session.flush()
    return row


class TestRegistration:
    def test_a_vetted_package_is_stored_then_recorded(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        activity = build_activity(session)
        session.commit()

        report = register_package(
            session,
            store,
            activity_code=activity.code,
            path=package_file(tmp_path / "ok.h5p"),
            licence="CC BY 4.0",
            source="https://example.com/essai",
        )
        session.commit()

        assert report.library == "H5P.TrueFalse 1.8"
        assert report.object_key in store.objects
        assert activity.h5p_package is not None
        assert activity.h5p_package.sha256 == report.sha256

    def test_the_object_is_named_after_its_digest(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        """The same bytes never sit in the bucket twice."""
        activity = build_activity(session)
        session.commit()

        report = register_package(
            session,
            store,
            activity_code=activity.code,
            path=package_file(tmp_path / "ok.h5p"),
            licence="CC BY 4.0",
            source="https://example.com/essai",
        )

        assert report.sha256 in report.object_key

    def test_a_refused_type_never_reaches_storage(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        """Inspection comes first, so the bucket never holds what ADR-012 refuses."""
        activity = build_activity(session)
        session.commit()

        with pytest.raises(PackageRefused):
            register_package(
                session,
                store,
                activity_code=activity.code,
                path=package_file(tmp_path / "autre.h5p", library="H5P.QuestionSet"),
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )

        assert store.objects == {}

    def test_a_failed_write_takes_the_object_back_out(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        """An object with no row is an orphan nobody inspects a second time.

        The row write is made to fail after the object has landed — a licence
        longer than its column does it — so the compensating removal is the only
        thing that can keep the bucket honest.
        """
        activity = build_activity(session)
        session.commit()

        with pytest.raises(SQLAlchemyError):
            register_package(
                session,
                store,
                activity_code=activity.code,
                path=package_file(tmp_path / "ok.h5p"),
                licence="C" * 200,
                source="https://example.com/essai",
            )
        session.rollback()

        assert store.objects == {}
        assert len(store.removed) == 1

    def test_an_unknown_activity_is_refused(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        with pytest.raises(RegistrationRefused):
            register_package(
                session,
                store,
                activity_code=f"{TEST_CODE_PREFIX}jamais-vue",
                path=package_file(tmp_path / "ok.h5p"),
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )

    def test_an_activity_of_another_kind_is_refused(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        activity = build_activity(session, kind=ACTIVITY_KIND_PHET)
        session.commit()

        with pytest.raises(RegistrationRefused) as refusal:
            register_package(
                session,
                store,
                activity_code=activity.code,
                path=package_file(tmp_path / "ok.h5p"),
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )

        assert "phet" in str(refusal.value)

    def test_a_second_package_on_the_same_activity_is_refused(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        activity = build_activity(session)
        session.commit()
        register_package(
            session,
            store,
            activity_code=activity.code,
            path=package_file(tmp_path / "un.h5p"),
            licence="CC BY 4.0",
            source="https://example.com/essai",
        )
        session.commit()

        with pytest.raises(RegistrationRefused):
            register_package(
                session,
                store,
                activity_code=activity.code,
                path=package_file(tmp_path / "deux.h5p", minor="8"),
                licence="CC BY 4.0",
                source="https://example.com/essai",
            )


class TestUnregistration:
    def test_removing_the_package_frees_the_slot_for_another(
        self, session: Session, store: RecordingStore, tmp_path: Path
    ) -> None:
        activity = build_activity(session)
        session.commit()
        register_package(
            session,
            store,
            activity_code=activity.code,
            path=package_file(tmp_path / "un.h5p"),
            licence="CC BY 4.0",
            source="https://example.com/essai",
        )
        session.commit()

        report = unregister_package(session, store, activity_code=activity.code)
        session.commit()

        assert report.object_key in store.removed
        register_package(
            session,
            store,
            activity_code=activity.code,
            path=package_file(tmp_path / "deux.h5p", minor="8"),
            licence="CC BY 4.0",
            source="https://example.com/essai",
        )

    def test_an_activity_with_no_package_is_refused(
        self, session: Session, store: RecordingStore
    ) -> None:
        activity = build_activity(session)
        session.commit()

        with pytest.raises(RegistrationRefused):
            unregister_package(session, store, activity_code=activity.code)

    def test_an_unknown_activity_is_refused(
        self, session: Session, store: RecordingStore
    ) -> None:
        with pytest.raises(RegistrationRefused):
            unregister_package(
                session, store, activity_code=f"{TEST_CODE_PREFIX}jamais-vue"
            )


class TestCatalogueCheck:
    """The counterpart ADR-013 owes: find the links no foreign key protects.

    The check looks at the whole catalogue, which is the point of it, so these
    tests assert about their own activities rather than about global soundness:
    the database they run against holds whatever else the project put there.
    """

    @staticmethod
    def dangling_for(report: object, activity_code: str) -> list[str]:
        return [
            link.competency_code
            for link in report.dangling  # type: ignore[attr-defined]
            if link.activity_code == activity_code
        ]

    def edition(self, session: Session, *codes: str) -> str:
        code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}"
        document = {
            "version": {"code": code, "label": "Édition d’essai"},
            "levels": [{"code": "cp", "label": "Cours préparatoire", "position": 1}],
            "subjects": [
                {
                    "code": "math",
                    "label": "Mathématiques",
                    "position": 1,
                    "domains": [
                        {"code": "math-num", "label": "Nombres", "position": 1}
                    ],
                }
            ],
            "competencies": [
                {
                    "code": competency,
                    "label": f"Compétence {competency}",
                    "description": None,
                    "position": index + 1,
                    "level": "cp",
                    "domain": "math-num",
                    "prerequisites": [],
                }
                for index, competency in enumerate(codes)
            ],
        }
        reconcile(session, ReferentialDocument.model_validate(document))
        publish(session, code)
        session.flush()
        return code

    def test_a_catalogue_that_resolves_is_sound(self, session: Session) -> None:
        edition = self.edition(session, "cp-math-num-01")
        activity = build_activity(session, status=ACTIVITY_STATUS_PUBLISHED)
        session.add(
            ActivityCompetency(
                activity_id=activity.id, competency_code="cp-math-num-01"
            )
        )
        session.commit()

        report = check_catalogue(session)

        assert report.edition_code == edition
        assert self.dangling_for(report, activity.code) == []
        assert activity.code not in report.activities_without_link
        assert report.linked_codes >= 1

    def test_a_code_that_designates_nothing_is_named(self, session: Session) -> None:
        """A dangling link is a silence, not an error, which is why it is hunted."""
        self.edition(session, "cp-math-num-01")
        activity = build_activity(session)
        session.add(
            ActivityCompetency(
                activity_id=activity.id, competency_code="cp-math-num-99"
            )
        )
        session.commit()

        report = check_catalogue(session)

        assert report.sound is False
        assert self.dangling_for(report, activity.code) == ["cp-math-num-99"]

    def test_an_activity_linked_to_nothing_is_named_too(self, session: Session) -> None:
        """It can never be recommended by step 12, which is just as silent."""
        self.edition(session, "cp-math-num-01")
        activity = build_activity(session)
        session.commit()

        report = check_catalogue(session)

        assert report.sound is False
        assert activity.code in report.activities_without_link

    def test_without_an_edition_in_force_nothing_can_be_resolved(
        self, session: Session
    ) -> None:
        activity = build_activity(session)
        session.add(
            ActivityCompetency(
                activity_id=activity.id, competency_code="cp-math-num-01"
            )
        )
        session.commit()

        report = check_catalogue(session)

        assert report.edition_code is None
        assert report.linked_codes == 0

    def test_a_link_valid_in_one_edition_may_dangle_in_the_next(
        self, session: Session
    ) -> None:
        """The risk ADR-013 accepts, made visible: publishing a slimmer edition
        leaves the catalogue pointing at a competency that no longer exists."""
        self.edition(session, "cp-math-num-01", "cp-math-num-02")
        activity = build_activity(session)
        session.add(
            ActivityCompetency(
                activity_id=activity.id, competency_code="cp-math-num-02"
            )
        )
        session.commit()
        assert self.dangling_for(check_catalogue(session), activity.code) == []

        self.edition(session, "cp-math-num-01")
        session.commit()

        report = check_catalogue(session)
        assert report.sound is False
        assert self.dangling_for(report, activity.code) == ["cp-math-num-02"]
