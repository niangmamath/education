"""Integration tests proving the referential constraints bite.

A schema only guarantees what the database refuses, so these tests run against
real PostgreSQL and check that the refusals happen. Every fixture builds
fictional French school content; nothing here comes from a real programme.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import DATABASE_URL
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

TEST_CODE_PREFIX = "test-ref-"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    """A synchronous engine: these tests speak to the database, not to the API."""
    engine = create_engine(
        DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    )
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


def build_version(
    session: Session,
    status: str = VERSION_STATUS_DRAFT,
    competency_code: str = "cm1-math-num-01",
) -> tuple[ReferentialVersion, Competency]:
    """Create one coherent edition holding a single competency."""
    version = ReferentialVersion(
        code=f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}",
        label="Édition fictive de test",
        status=status,
    )
    session.add(version)
    session.flush()

    level = Level(version_id=version.id, code="cm1", label="Cours moyen 1", position=4)
    subject = Subject(
        version_id=version.id, code="math", label="Mathématiques", position=1
    )
    session.add_all([level, subject])
    session.flush()

    domain = Domain(
        version_id=version.id,
        subject_id=subject.id,
        code="numeration",
        label="Nombres et calcul",
        position=1,
    )
    session.add(domain)
    session.flush()

    competency = Competency(
        version_id=version.id,
        domain_id=domain.id,
        level_id=level.id,
        code=competency_code,
        label="Additionner deux nombres à deux chiffres",
        position=1,
    )
    session.add(competency)
    session.flush()

    return version, competency


class TestVersionScope:
    def test_a_version_holds_a_coherent_tree(self, session: Session) -> None:
        version, competency = build_version(session)
        session.commit()

        assert competency.version_id == version.id
        assert competency.domain.subject.version_id == version.id
        assert competency.level.version_id == version.id

    def test_two_versions_may_hold_the_same_competency_code(
        self, session: Session
    ) -> None:
        """A competency keeps its code from one edition to the next."""
        _, first = build_version(session, competency_code="cm1-math-num-01")
        _, second = build_version(session, competency_code="cm1-math-num-01")
        session.commit()

        assert first.code == second.code
        assert first.version_id != second.version_id

    def test_one_version_may_not_hold_the_same_code_twice(
        self, session: Session
    ) -> None:
        version, competency = build_version(session)
        session.commit()

        session.add(
            Competency(
                version_id=version.id,
                domain_id=competency.domain_id,
                level_id=competency.level_id,
                code=competency.code,
                label="Doublon",
                position=2,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

    def test_a_competency_cannot_borrow_a_domain_from_another_version(
        self, session: Session
    ) -> None:
        """The composite foreign key is what makes this impossible."""
        _, foreign = build_version(session)
        version, competency = build_version(session)
        session.commit()

        session.add(
            Competency(
                version_id=version.id,
                domain_id=foreign.domain_id,
                level_id=competency.level_id,
                code="cm1-math-num-02",
                label="Compétence à cheval sur deux éditions",
                position=2,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

    def test_a_competency_cannot_borrow_a_level_from_another_version(
        self, session: Session
    ) -> None:
        _, foreign = build_version(session)
        version, competency = build_version(session)
        session.commit()

        session.add(
            Competency(
                version_id=version.id,
                domain_id=competency.domain_id,
                level_id=foreign.level_id,
                code="cm1-math-num-03",
                label="Compétence à cheval sur deux éditions",
                position=2,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

    def test_deleting_a_version_takes_its_content_with_it(
        self, session: Session
    ) -> None:
        version, competency = build_version(session)
        session.commit()
        competency_id = competency.id

        session.delete(version)
        session.commit()

        assert session.get(Competency, competency_id) is None
        assert session.query(Level).filter_by(version_id=version.id).count() == 0
        assert session.query(Domain).filter_by(version_id=version.id).count() == 0


class TestPrerequisites:
    def test_a_competency_requires_another_one(self, session: Session) -> None:
        version, first = build_version(session)
        second = Competency(
            version_id=version.id,
            domain_id=first.domain_id,
            level_id=first.level_id,
            code="cm1-math-num-10",
            label="Poser une multiplication",
            position=2,
        )
        session.add(second)
        session.flush()

        session.add(
            CompetencyPrerequisite(
                competency_id=second.id,
                prerequisite_id=first.id,
                version_id=version.id,
            )
        )
        session.commit()

        assert [link.prerequisite_id for link in second.prerequisites] == [first.id]

    def test_a_competency_cannot_require_itself(self, session: Session) -> None:
        version, competency = build_version(session)
        session.commit()

        session.add(
            CompetencyPrerequisite(
                competency_id=competency.id,
                prerequisite_id=competency.id,
                version_id=version.id,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

    def test_a_prerequisite_cannot_cross_versions(self, session: Session) -> None:
        _, foreign = build_version(session)
        version, competency = build_version(session)
        session.commit()

        session.add(
            CompetencyPrerequisite(
                competency_id=competency.id,
                prerequisite_id=foreign.id,
                version_id=version.id,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()

    def test_the_same_pair_cannot_be_declared_twice(self, session: Session) -> None:
        version, first = build_version(session)
        second = Competency(
            version_id=version.id,
            domain_id=first.domain_id,
            level_id=first.level_id,
            code="cm1-math-num-11",
            label="Poser une division",
            position=2,
        )
        session.add(second)
        session.flush()
        session.add(
            CompetencyPrerequisite(
                competency_id=second.id,
                prerequisite_id=first.id,
                version_id=version.id,
            )
        )
        session.commit()

        session.add(
            CompetencyPrerequisite(
                competency_id=second.id,
                prerequisite_id=first.id,
                version_id=version.id,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()


class TestPublication:
    def test_only_one_version_may_be_published(self, session: Session) -> None:
        build_version(session, status=VERSION_STATUS_PUBLISHED)
        session.commit()

        # The refusal lands on the flush inside the builder, not on the commit:
        # the partial index bites as soon as the second published row is written.
        with pytest.raises(IntegrityError):
            build_version(session, status=VERSION_STATUS_PUBLISHED)
            session.commit()

    def test_drafts_and_archives_may_be_as_many_as_needed(
        self, session: Session
    ) -> None:
        build_version(session, status=VERSION_STATUS_DRAFT)
        build_version(session, status=VERSION_STATUS_DRAFT)
        build_version(session, status=VERSION_STATUS_ARCHIVED)
        build_version(session, status=VERSION_STATUS_ARCHIVED)

        session.commit()

    def test_an_unknown_status_is_refused(self, session: Session) -> None:
        """Short enough to fit the column, so the check constraint is what refuses."""
        session.add(
            ReferentialVersion(
                code=f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}",
                label="Statut inventé",
                status="relecture",
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()
