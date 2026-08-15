"""Progress, read by the child it belongs to and by her parent.

Two routes for one reading, rather than one route that serves either. The child
asks for her own and cannot name anyone; the parent names a child and must own
her. A single route taking an optional identifier would be one forgotten check
away from showing a family another family's work.

Both return the same shape. There is nothing here a child may not see about
herself: the point of a reading that names its rule and carries its counts is
precisely that it can be shown to the person it is about.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentChild, CurrentParent, DbSession
from app.core.exceptions import NotFoundException
from app.models.identity import CHILD_STATUS_ACTIVE, Child
from app.progress import service
from app.schemas.progress import ChildProgress

router = APIRouter()

CHILD_NOT_FOUND_MESSAGE = "Ce profil enfant n’existe pas"


@router.get("/me/progress", response_model=ChildProgress)
async def read_my_progress(child: CurrentChild, db: DbSession) -> Any:
    """This child's own progress, and nobody else's."""
    return await service.child_progress(db, child.id)


@router.get("/children/{child_id}/progress", response_model=ChildProgress)
async def read_child_progress(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Any:
    """The progress of one child of this family.

    A child of another family is refused as one that does not exist: the answer
    must not let anyone tell an identifier that exists elsewhere from one that
    exists nowhere.
    """
    owned = await db.scalar(
        select(Child).where(
            Child.id == child_id,
            Child.parent_id == parent.id,
            Child.status == CHILD_STATUS_ACTIVE,
        )
    )
    if owned is None:
        raise NotFoundException(message=CHILD_NOT_FOUND_MESSAGE)
    return await service.child_progress(db, child_id)
