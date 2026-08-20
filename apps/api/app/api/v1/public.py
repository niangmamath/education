"""What a visitor may know before signing in.

No session, no cookie, nothing personal: every number here is a count, never a
name, an email, or an activity anyone could trace back to a specific family.
That is what makes it safe to serve with no authentication at all — the same
posture as the referential and the catalogue, which any authenticated session
may already read, taken one step further because this route needs no session
either.
"""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DbSession
from app.models.attempt import ATTEMPT_STATUS_COMPLETED, Attempt, AttemptResult
from app.models.identity import CHILD_STATUS_ACTIVE, Child, Parent
from app.models.referential import Competency
from app.schemas.public import PublicStats

router = APIRouter()


@router.get("/public/stats", response_model=PublicStats)
async def read_public_stats(db: DbSession) -> PublicStats:
    """Counts a visitor may see before deciding whether to sign up.

    `competencies_covered` counts a competency once it has at least one
    finished reading, whatever that reading concluded — a competency that
    stays `not_mastered` every time is still a competency the platform has
    worked, not one it has ignored.
    """
    families = await db.scalar(select(func.count(Parent.id))) or 0
    children = (
        await db.scalar(
            select(func.count(Child.id)).where(Child.status == CHILD_STATUS_ACTIVE)
        )
        or 0
    )
    activities_completed = (
        await db.scalar(
            select(func.count(Attempt.id)).where(
                Attempt.status == ATTEMPT_STATUS_COMPLETED
            )
        )
        or 0
    )
    competencies_covered = (
        await db.scalar(select(func.count(func.distinct(AttemptResult.competency_code))))
        or 0
    )
    competencies_total = await db.scalar(select(func.count(Competency.id))) or 0

    return PublicStats(
        families=families,
        children=children,
        activities_completed=activities_completed,
        competencies_covered=competencies_covered,
        competencies_total=competencies_total,
    )
