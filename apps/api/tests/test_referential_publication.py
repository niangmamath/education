"""Integration tests for putting an edition in force.

Publishing is the act that changes what every reader sees, so these tests run
against real PostgreSQL: only there does the partial unique index refuse a
second published edition, and only there can the hand-over be shown to leave no
gap. Every edition carries a test prefix and is deleted afterwards.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.models.referential import (
    VERSION_STATUS_ARCHIVED,
    VERSION_STATUS_DRAFT,
    VERSION_STATUS_PUBLISHED,
    ReferentialVersion,
)
from app.referential.publication import (
    PublicationRefused,
    publish,
    published_version,
)
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-publish-"


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


def edition(session: Session, status: str = VERSION_STATUS_DRAFT) -> ReferentialVersion:
    version = ReferentialVersion(
        code=f"{TEST_CODE_PREFIX}{uuid.uuid4().hex}",
        label="Édition d’essai",
        status=status,
    )
    session.add(version)
    session.flush()
    return version


def test_a_draft_is_put_in_force(session: Session) -> None:
    draft = edition(session)

    report = publish(session, draft.code)
    session.commit()

    assert report.was_already_published is False
    assert report.archived_code is None
    assert draft.status == VERSION_STATUS_PUBLISHED


def test_the_edition_it_replaces_is_archived(session: Session) -> None:
    """One edition steps aside as the other steps in, in the same transaction."""
    previous = edition(session, status=VERSION_STATUS_PUBLISHED)
    successor = edition(session)
    session.commit()

    report = publish(session, successor.code)
    session.commit()

    assert report.archived_code == previous.code
    assert previous.status == VERSION_STATUS_ARCHIVED
    assert successor.status == VERSION_STATUS_PUBLISHED


def test_exactly_one_edition_is_in_force_afterwards(session: Session) -> None:
    edition(session, status=VERSION_STATUS_PUBLISHED)
    successor = edition(session)
    session.commit()

    publish(session, successor.code)
    session.commit()

    in_force = session.scalars(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    ).all()
    assert [version.code for version in in_force] == [successor.code]


def test_publishing_twice_changes_nothing(session: Session) -> None:
    draft = edition(session)
    session.commit()
    publish(session, draft.code)
    session.commit()

    report = publish(session, draft.code)
    session.commit()

    assert report.was_already_published is True
    assert report.archived_code is None
    assert draft.status == VERSION_STATUS_PUBLISHED


def test_an_unknown_code_is_refused(session: Session) -> None:
    with pytest.raises(PublicationRefused) as refusal:
        publish(session, f"{TEST_CODE_PREFIX}jamais-vu")

    assert "jamais-vu" in str(refusal.value)


def test_an_archived_edition_is_not_brought_back(session: Session) -> None:
    """Reviving a retired edition would change the meaning of recent traces."""
    retired = edition(session, status=VERSION_STATUS_ARCHIVED)
    session.commit()

    with pytest.raises(PublicationRefused) as refusal:
        publish(session, retired.code)
    session.rollback()

    assert "archivée" in str(refusal.value)
    assert retired.status == VERSION_STATUS_ARCHIVED


def test_the_edition_in_force_is_found_and_none_is_not_an_error(
    session: Session,
) -> None:
    assert published_version(session) is None

    draft = edition(session)
    publish(session, draft.code)
    session.commit()

    found = published_version(session)
    assert found is not None
    assert found.code == draft.code
