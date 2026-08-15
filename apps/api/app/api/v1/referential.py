"""Read the referential edition currently in force.

These routes serve the `published` edition and nothing else. A draft is work in
progress: it is re-read with the import command in dry run, never over HTTP, so
that no client can build on a programme that is still being written. An archived
edition is not served either — the traces that cite it will need it one day, and
that day will bring its own route.

Any authenticated session may read, Parent or Enfant alike. The referential is
not personal data and both spaces need it; requiring a session simply keeps the
whole base from being harvested by anyone who finds the URL.

Nothing here exposes the prerequisite tree. It has been modelled since 07.1 and
belongs to the remediation of step 12.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentSession, DbSession
from app.core.exceptions import NotFoundException
from app.models.referential import (
    VERSION_STATUS_PUBLISHED,
    Competency,
    Domain,
    Level,
    ReferentialVersion,
    Subject,
)
from app.schemas.referential import (
    CompetencyPublic,
    EditionPublic,
    LevelPublic,
    Page,
    SubjectPublic,
)

router = APIRouter()

NO_EDITION_MESSAGE = "Aucune édition du référentiel n’est en vigueur"

PageNumber = Annotated[int, Query(ge=1, description="numéro de page, à partir de 1")]
PageSize = Annotated[
    int, Query(ge=1, le=100, description="taille de page, 100 au plus")
]
CodeFilter = Annotated[str | None, Query(min_length=1, max_length=50)]


async def _edition_in_force(db: DbSession) -> ReferentialVersion | None:
    """The published edition, or nothing when none has been put in force."""
    return await db.scalar(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    )


@router.get("/edition", response_model=EditionPublic)
async def read_edition(session: CurrentSession, db: DbSession) -> ReferentialVersion:
    """The edition every other route on this router reads from."""
    edition = await _edition_in_force(db)
    if edition is None:
        raise NotFoundException(message=NO_EDITION_MESSAGE)
    return edition


@router.get("/levels", response_model=Page[LevelPublic])
async def list_levels(
    session: CurrentSession,
    db: DbSession,
    page: PageNumber = 1,
    page_size: PageSize = 50,
) -> Page[LevelPublic]:
    """The school years of the edition in force, in school order."""
    edition = await _edition_in_force(db)
    if edition is None:
        return _empty(page, page_size)

    total = await _count(db, select(func.count()).select_from(Level), edition.id, Level)
    rows = await db.scalars(
        _paginate(
            select(Level)
            .where(Level.version_id == edition.id)
            .order_by(Level.position, Level.code),
            page,
            page_size,
        )
    )
    return Page[LevelPublic](
        edition=EditionPublic.model_validate(edition),
        items=[LevelPublic.model_validate(row) for row in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/subjects", response_model=Page[SubjectPublic])
async def list_subjects(
    session: CurrentSession,
    db: DbSession,
    page: PageNumber = 1,
    page_size: PageSize = 50,
) -> Page[SubjectPublic]:
    """The subjects of the edition in force, each with its domains."""
    edition = await _edition_in_force(db)
    if edition is None:
        return _empty(page, page_size)

    total = await _count(
        db, select(func.count()).select_from(Subject), edition.id, Subject
    )
    rows = await db.scalars(
        _paginate(
            select(Subject)
            .where(Subject.version_id == edition.id)
            .order_by(Subject.position, Subject.code)
            .options(selectinload(Subject.domains)),
            page,
            page_size,
        )
    )
    items = []
    for row in rows:
        subject = SubjectPublic.model_validate(row)
        subject.domains.sort(key=lambda domain: (domain.position, domain.code))
        items.append(subject)

    return Page[SubjectPublic](
        edition=EditionPublic.model_validate(edition),
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/competencies", response_model=Page[CompetencyPublic])
async def list_competencies(
    session: CurrentSession,
    db: DbSession,
    level: CodeFilter = None,
    subject: CodeFilter = None,
    domain: CodeFilter = None,
    page: PageNumber = 1,
    page_size: PageSize = 50,
) -> Page[CompetencyPublic]:
    """The competencies of the edition in force, filtered by codes.

    A filter naming a code the edition does not hold returns an empty page
    rather than an error: it is a filter, and filtering out everything is an
    ordinary answer.
    """
    edition = await _edition_in_force(db)
    if edition is None:
        return _empty(page, page_size)

    filters = (level, subject, domain)
    total = await db.scalar(
        _shelves(select(func.count()).select_from(Competency), edition.id, *filters)
    )
    rows = await db.execute(
        _paginate(
            _shelves(
                select(Competency, Level.code, Domain.code, Subject.code),
                edition.id,
                *filters,
            ).order_by(
                Subject.position,
                Domain.position,
                Level.position,
                Competency.position,
                Competency.code,
            ),
            page,
            page_size,
        )
    )

    return Page[CompetencyPublic](
        edition=EditionPublic.model_validate(edition),
        items=[
            CompetencyPublic(
                code=competency.code,
                label=competency.label,
                description=competency.description,
                position=competency.position,
                level=level_code,
                domain=domain_code,
                subject=subject_code,
            )
            for competency, level_code, domain_code, subject_code in rows
        ],
        page=page,
        page_size=page_size,
        total=total or 0,
    )


def _shelves(
    statement: Select[Any],
    edition_id: uuid.UUID,
    level: str | None,
    subject: str | None,
    domain: str | None,
) -> Select[Any]:
    """Join a competency to its level, its domain and that domain's subject.

    The joins repeat `version_id` on purpose: it is half of every composite key
    of the schema, and leaving it out would let a query wander across editions.
    """
    statement = (
        statement.join(
            Level,
            and_(
                Level.id == Competency.level_id,
                Level.version_id == Competency.version_id,
            ),
        )
        .join(
            Domain,
            and_(
                Domain.id == Competency.domain_id,
                Domain.version_id == Competency.version_id,
            ),
        )
        .join(
            Subject,
            and_(
                Subject.id == Domain.subject_id,
                Subject.version_id == Domain.version_id,
            ),
        )
        .where(Competency.version_id == edition_id)
    )
    if level is not None:
        statement = statement.where(Level.code == level)
    if subject is not None:
        statement = statement.where(Subject.code == subject)
    if domain is not None:
        statement = statement.where(Domain.code == domain)
    return statement


def _paginate(statement: Select[Any], page: int, page_size: int) -> Select[Any]:
    return statement.limit(page_size).offset((page - 1) * page_size)


async def _count(
    db: DbSession, statement: Select[Any], edition_id: uuid.UUID, model: Any
) -> int:
    total = await db.scalar(statement.where(model.version_id == edition_id))
    return total or 0


def _empty(page: int, page_size: int) -> Any:
    """No edition in force is not an error: the referential simply has none."""
    return Page(edition=None, items=[], page=page, page_size=page_size, total=0)
