"""What the catalogue schema refuses, checked against real PostgreSQL.

A constraint only guarantees what the database actually rejects, so these tests
write rows and expect refusals. Two of them matter more than the rest: the H5P
library allowlist, which carries ADR-012 into the schema, and the absence of a
foreign key on the competency link, which carries ADR-013.

The builders below flush, because a row's identifier is needed to hang the next
row off it. A refusal therefore lands on the builder call and not on the commit,
which is why those calls sit inside the `pytest.raises` blocks.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, ForeignKeyConstraint, create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_KIND_PHET,
    ACTIVITY_STATUS_ARCHIVED,
    ACTIVITY_STATUS_DRAFT,
    ACTIVITY_STATUS_PUBLISHED,
    MAX_DURATION_MINUTES,
    Activity,
    ActivityCompetency,
    H5PPackage,
)

TEST_CODE_PREFIX = "test-cat-"
DIGEST = "9914c27552f00aa91d4a29e85f6a299b11f984030c3451658fb0246f84b07f3c"


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
            text("DELETE FROM catalog_activities WHERE code LIKE :pattern"),
            {"pattern": f"{TEST_CODE_PREFIX}%"},
        )


def build_activity(session: Session, **overrides: object) -> Activity:
    values: dict[str, object] = {
        "code": f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}",
        "title": "Activité d’essai",
        "kind": ACTIVITY_KIND_H5P,
        "status": ACTIVITY_STATUS_DRAFT,
        "duration_minutes": 5,
    }
    values.update(overrides)
    row = Activity(**values)
    session.add(row)
    session.flush()
    return row


def build_package(session: Session, row: Activity, **overrides: object) -> H5PPackage:
    values: dict[str, object] = {
        "activity_id": row.id,
        "library_name": "H5P.TrueFalse",
        "library_version": "1.8",
        "object_key": "h5p-packages/essai.h5p",
        "sha256": uuid.uuid4().hex + uuid.uuid4().hex,
        "size_bytes": 4096,
        "licence": "CC BY 4.0",
        "source": "https://example.com/essai",
    }
    values.update(overrides)
    package = H5PPackage(**values)
    session.add(package)
    session.flush()
    return package


class TestActivity:
    def test_an_activity_is_created_as_a_draft(self, session: Session) -> None:
        row = build_activity(session)
        session.commit()

        assert row.status == ACTIVITY_STATUS_DRAFT

    def test_a_code_may_not_be_used_twice(self, session: Session) -> None:
        """One catalogue, so a code is unique outright, unlike a referential code."""
        first = build_activity(session)
        session.commit()

        with pytest.raises(IntegrityError):
            build_activity(session, code=first.code)
            session.commit()

    @pytest.mark.parametrize("kind", ["quiz", "pdf", "", "H5P"])
    def test_an_unknown_kind_is_refused(self, session: Session, kind: str) -> None:
        with pytest.raises(IntegrityError):
            build_activity(session, kind=kind)
            session.commit()

    def test_an_unknown_status_is_refused(self, session: Session) -> None:
        with pytest.raises(IntegrityError):
            build_activity(session, status="relecture")
            session.commit()

    @pytest.mark.parametrize("minutes", [0, -1, MAX_DURATION_MINUTES + 1])
    def test_a_duration_outside_the_bounds_is_refused(
        self, session: Session, minutes: int
    ) -> None:
        """A Quick Repair lasts minutes: nothing may claim to take no time at
        all, nor an hour and a half."""
        with pytest.raises(IntegrityError):
            build_activity(session, duration_minutes=minutes)
            session.commit()

    def test_the_three_statuses_are_accepted(self, session: Session) -> None:
        for status in (
            ACTIVITY_STATUS_DRAFT,
            ACTIVITY_STATUS_PUBLISHED,
            ACTIVITY_STATUS_ARCHIVED,
        ):
            build_activity(session, status=status)

        session.commit()


class TestCompetencyLink:
    def test_an_activity_names_the_competencies_it_works_on(
        self, session: Session
    ) -> None:
        row = build_activity(session)
        session.add(
            ActivityCompetency(activity_id=row.id, competency_code="cm1-math-num-01")
        )
        session.commit()

        assert [link.competency_code for link in row.competencies] == [
            "cm1-math-num-01"
        ]

    def test_the_same_competency_cannot_be_linked_twice(self, session: Session) -> None:
        row = build_activity(session)
        session.add(
            ActivityCompetency(activity_id=row.id, competency_code="cm1-math-num-01")
        )
        session.commit()

        session.add(
            ActivityCompetency(activity_id=row.id, competency_code="cm1-math-num-01")
        )
        with pytest.raises(IntegrityError):
            session.commit()

    def test_the_link_has_no_foreign_key_to_the_referential(self) -> None:
        """ADR-013, and the reason it is a decision rather than an oversight.

        A competency row belongs to one edition; a foreign key would have to be
        rewritten every time an edition is published. The catalogue outlives
        editions instead, at the price of a link the database cannot check.
        """
        referenced = {
            constraint.referred_table.name
            for constraint in ActivityCompetency.__table__.constraints
            if isinstance(constraint, ForeignKeyConstraint)
        }

        assert referenced == {"catalog_activities"}

    def test_a_code_that_designates_nothing_is_accepted_by_the_database(
        self, session: Session
    ) -> None:
        """The other side of ADR-013: this is what `app.catalog check` is for."""
        row = build_activity(session)
        session.add(
            ActivityCompetency(activity_id=row.id, competency_code="jamais-vu-01")
        )

        session.commit()

    def test_deleting_an_activity_takes_its_links_with_it(
        self, session: Session
    ) -> None:
        row = build_activity(session)
        session.add(
            ActivityCompetency(activity_id=row.id, competency_code="cm1-math-num-01")
        )
        session.commit()
        activity_id = row.id

        session.delete(row)
        session.commit()

        remaining = session.query(ActivityCompetency).filter_by(activity_id=activity_id)
        assert remaining.count() == 0


class TestH5PPackage:
    def test_the_pilot_library_is_accepted(self, session: Session) -> None:
        row = build_activity(session)
        build_package(session, row)

        session.commit()

    @pytest.mark.parametrize(
        ("name", "version"),
        [
            ("H5P.MultiChoice", "1.16"),
            ("H5P.TrueFalse", "1.7"),
            ("H5P.TrueFalse", "2.0"),
            ("h5p.truefalse", "1.8"),
        ],
    )
    def test_any_other_library_is_refused_by_the_database(
        self, session: Session, name: str, version: str
    ) -> None:
        """ADR-012 refuses every other type by default, and says so in the schema.

        An application rule could be relaxed by a configuration change; a check
        constraint takes a migration and an amended ADR, which is the friction
        the decision asked for. The last case matters too: the name is compared
        exactly, so a differently-cased spelling is another library.
        """
        row = build_activity(session)

        with pytest.raises(IntegrityError):
            build_package(session, row, library_name=name, library_version=version)
            session.commit()

    def test_a_digest_that_is_not_a_sha256_is_refused(self, session: Session) -> None:
        row = build_activity(session)

        with pytest.raises(IntegrityError):
            build_package(session, row, sha256="trop-court")
            session.commit()

    def test_the_same_file_cannot_be_registered_twice(self, session: Session) -> None:
        """Two activities playing the same bytes would be one activity."""
        first = build_activity(session)
        build_package(session, first, sha256=DIGEST)
        session.commit()

        second = build_activity(session)
        with pytest.raises(IntegrityError):
            build_package(session, second, sha256=DIGEST)
            session.commit()

    def test_an_activity_holds_at_most_one_package(self, session: Session) -> None:
        row = build_activity(session)
        build_package(session, row)
        session.commit()

        with pytest.raises(IntegrityError):
            build_package(session, row)
            session.commit()

    def test_an_empty_file_is_refused(self, session: Session) -> None:
        row = build_activity(session)

        with pytest.raises(IntegrityError):
            build_package(session, row, size_bytes=0)
            session.commit()

    def test_provenance_is_recorded_with_the_package(self) -> None:
        """ADR-012, condition 8: licence and provenance checked before publication."""
        columns = {column.name for column in inspect(H5PPackage).columns}

        assert {"licence", "source", "sha256", "object_key"} <= columns

    def test_a_phet_activity_needs_no_package(self, session: Session) -> None:
        row = build_activity(session, kind=ACTIVITY_KIND_PHET)
        session.commit()

        assert row.h5p_package is None
