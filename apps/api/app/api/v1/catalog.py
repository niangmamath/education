"""Read the catalogue of activities.

Only **published** activities are served. A draft is editorial work in progress
and an archived activity has stopped being offered, though it never disappears:
the results of steps 10 to 12 will keep pointing at it.

Any authenticated session may read, Parent or Enfant, on the same reasoning as
the referential routes: this is not personal data, both spaces need it, and two
reading paths for the same data eventually diverge.

Nothing here assigns an activity to a child and nothing records a result. That
is step 09 and step 10. Nothing here hands over a package either: a client
learns that an activity plays `H5P.TrueFalse 1.8`, never where the file sits.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query
from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentSession, DbSession
from app.core.exceptions import NotFoundException
from app.models.catalog import (
    ACTIVITY_KINDS,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.schemas.catalog import ActivityH5P, ActivityPublic, CatalogPage

router = APIRouter()

ACTIVITY_NOT_FOUND_MESSAGE = "Cette activité n’existe pas ou n’est pas publiée"

PageNumber = Annotated[int, Query(ge=1, description="numéro de page, à partir de 1")]
PageSize = Annotated[
    int, Query(ge=1, le=100, description="taille de page, 100 au plus")
]
CodeFilter = Annotated[str | None, Query(min_length=1, max_length=50)]
KindFilter = Annotated[str | None, Query(pattern="^(h5p|phet|video)$")]
Minutes = Annotated[int | None, Query(ge=1, le=60)]


@router.get("/activities", response_model=CatalogPage[ActivityPublic])
async def list_activities(
    session: CurrentSession,
    db: DbSession,
    competency: CodeFilter = None,
    kind: KindFilter = None,
    max_duration: Minutes = None,
    page: PageNumber = 1,
    page_size: PageSize = 50,
) -> CatalogPage[ActivityPublic]:
    """The published activities, filtered by what they work on and how long.

    `max_duration` is the filter a Quick Repair needs: three to seven minutes is
    a product rule, and asking for it should not mean reading the whole
    catalogue and sorting client-side.
    """
    total = await db.scalar(
        _filtered(
            select(func.count(func.distinct(Activity.id))),
            competency,
            kind,
            max_duration,
        )
    )
    rows = await db.scalars(
        _filtered(select(Activity), competency, kind, max_duration)
        .order_by(Activity.duration_minutes, Activity.code)
        .limit(page_size)
        .offset((page - 1) * page_size)
        .options(
            selectinload(Activity.competencies), selectinload(Activity.h5p_package)
        )
    )

    return CatalogPage[ActivityPublic](
        items=[_public(row) for row in rows.unique()],
        page=page,
        page_size=page_size,
        total=total or 0,
    )


@router.get("/activities/{code}", response_model=ActivityPublic)
async def read_activity(code: str, session: CurrentSession, db: DbSession) -> Any:
    """One published activity.

    A draft answers exactly like an activity that does not exist: whether
    something is being prepared is not a client's business.
    """
    row = await db.scalar(
        select(Activity)
        .where(Activity.code == code, Activity.status == ACTIVITY_STATUS_PUBLISHED)
        .options(
            selectinload(Activity.competencies), selectinload(Activity.h5p_package)
        )
    )
    if row is None:
        raise NotFoundException(message=ACTIVITY_NOT_FOUND_MESSAGE)
    return _public(row)


@router.get("/kinds", response_model=list[str])
async def list_kinds(session: CurrentSession) -> list[str]:
    """The kinds an activity may have, so a client need not hard-code them."""
    return list(ACTIVITY_KINDS)


def _filtered(
    statement: Select[Any],
    competency: str | None,
    kind: str | None,
    max_duration: int | None,
) -> Select[Any]:
    """Published only, then whatever the caller asked to narrow.

    The competency filter joins rather than sub-selects, and the count above
    counts distinct activities: an activity working on two competencies is one
    activity, not two.
    """
    statement = statement.where(Activity.status == ACTIVITY_STATUS_PUBLISHED)
    if competency is not None:
        statement = statement.join(
            ActivityCompetency, ActivityCompetency.activity_id == Activity.id
        ).where(ActivityCompetency.competency_code == competency)
    if kind is not None:
        statement = statement.where(Activity.kind == kind)
    if max_duration is not None:
        statement = statement.where(Activity.duration_minutes <= max_duration)
    return statement


def _public(row: Activity) -> ActivityPublic:
    package = row.h5p_package
    return ActivityPublic(
        code=row.code,
        title=row.title,
        summary=row.summary,
        kind=row.kind,
        duration_minutes=row.duration_minutes,
        competencies=sorted(link.competency_code for link in row.competencies),
        h5p=ActivityH5P.model_validate(package) if package is not None else None,
    )
