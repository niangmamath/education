"""The diagnostic to the Parent, the next steps to the Élève.

Three routes, and the split between the first two is the design of this step
rather than a detail of it.

A **Parent** is shown the diagnostic: candidate gaps, what they may have in
common, what may sit underneath them, the health score and its terms. All of it
carries the rule that produced it, because a parent who cannot argue with a
conclusion is only being told what to think.

An **Élève** is shown what to do now, and nothing else. Not the score, not the
gaps, not the rule that named one. That is not secrecy about her own work — her
attempts, her results and her progress remain hers to read, and each of those
explains itself. It is that a list of repairs handed to a child *as a diagnosis*
is a judgement she has no way to answer, and the product has an adult in the
loop precisely so that she does not have to.

The **rules** are readable by any authenticated session, as the reading rules of
step 10 are: they are published so a parent can be shown what named a
difficulty, and publishing them behind a door only some can open would publish
them to nobody who needs them.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentChild, CurrentParent, CurrentSession, DbSession
from app.core.exceptions import NotFoundException
from app.diagnostic import rules, service
from app.models.identity import CHILD_STATUS_ACTIVE, Child
from app.schemas.diagnostic import (
    AppliedRemediation,
    ChildDiagnostic,
    DiagnosticRulePublic,
    NextSteps,
)

router = APIRouter()

CHILD_NOT_FOUND_MESSAGE = "Ce profil enfant n’existe pas"


@router.get("/children/{child_id}/diagnostic", response_model=ChildDiagnostic)
async def read_child_diagnostic(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Any:
    """What the platform proposes about one child of this family.

    A child of another family is refused as one that does not exist, so the
    answer cannot be used to tell an identifier that exists elsewhere from one
    that exists nowhere.
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
    return await service.child_diagnostic(db, child_id)


@router.post("/children/{child_id}/remediation", response_model=AppliedRemediation)
async def apply_remediation(
    child_id: uuid.UUID, parent: CurrentParent, db: DbSession
) -> Any:
    """Give the activities the platform proposes for this child.

    The parent's act, always: **the platform assigns nothing by itself.** What
    this route removes is the retyping, not the decision — agreeing with the
    proposals should not mean copying them one by one into the assignment form.

    Proposals the child already has, or that would pass the ceiling of open
    assignments, are skipped and named rather than forced.
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
    applied = await service.apply_recommendations(db, parent, child_id)
    await db.commit()
    return applied


@router.get("/me/next-steps", response_model=NextSteps)
async def read_my_next_steps(child: CurrentChild, db: DbSession) -> Any:
    """A few short activities this child can do now.

    Same engine as the diagnostic, and deliberately far less of it crossing.
    """
    return await service.child_next_steps(db, child.id)


@router.get("/diagnostic/rules", response_model=list[DiagnosticRulePublic])
async def list_diagnostic_rules(session: CurrentSession) -> list[DiagnosticRulePublic]:
    """The rules that name a difficulty and state health, so they can be quoted.

    Published rather than made configurable: choosing the threshold at which the
    platform calls something a difficulty is a decision about what is said of a
    child, not a setting, and there is nobody to make it before the
    Administrateur role of step 15.
    """
    return [DiagnosticRulePublic(**rule) for rule in rules.published_rules()]
