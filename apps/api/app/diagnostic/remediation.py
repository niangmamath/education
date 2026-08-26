"""Proposing a Quick Repair for a competency that is in difficulty.

A recommendation engine, and deliberately the dullest one that answers the
question: *which short published activity works on this competency, and has this
child not just been given it?* There is no ranking model and no personalisation
beyond what the catalogue and the child's own history already say.

Three constraints shape it, and all three come from the project rather than from
taste.

**Three to seven minutes.** A Quick Repair is defined by its length: something a
child can actually do now, not a lesson. An activity outside that band is not
proposed, however well it matches — proposing a twenty-minute activity as a
quick repair would make the promise false.

**Every remediation has a final proof.** So only activities that can be
attempted are proposed — published, and working on the competency — and each
recommendation names the proof it leads to: the reading of the attempt, by the
rules of step 10. Recommending something that concludes nothing would leave the
gap exactly where it was.

**Opening a content never validates a competency on its own.** Nothing here
marks anything as repaired. It proposes work; what the work shows is decided
elsewhere, from the attempt.
"""

from __future__ import annotations

import uuid
from typing import Final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import (
    ASSIGNMENT_STATUS_ASSIGNED,
    ASSIGNMENT_STATUS_COMPLETED,
    ASSIGNMENT_STATUS_IN_PROGRESS,
    Assignment,
)
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_KIND_COURSE,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.schemas.diagnostic import Recommendation

# What makes a repair *quick*. Both bounds are inclusive, and they are the
# product's numbers rather than this file's.
QUICK_REPAIR_MIN_MINUTES: Final = 3
QUICK_REPAIR_MAX_MINUTES: Final = 7

# A repair may be any short published activity that works on the competency —
# a native sheet as much as an imported H5P exercise or a PhET simulation;
# nothing here favours one medium. Two kinds are excluded on purpose rather
# than left to the duration band alone: an assessment is never a repair by
# nature, and a course (étape 15) is already given automatically the moment
# it is due — recommending it a second time as a "repair" would contradict
# that it is not something a parent proposes.
_NOT_A_REPAIR: Final = (ACTIVITY_KIND_ASSESSMENT, ACTIVITY_KIND_COURSE)

PROOF = (
    "La preuve finale est la lecture de la tentative : réponses évaluées, règle "
    "nommée, et compétence relue à la clôture."
)

# Already on her plate. Proposing it again would add noise, not help.
_PENDING = (ASSIGNMENT_STATUS_ASSIGNED, ASSIGNMENT_STATUS_IN_PROGRESS)


async def quick_repairs(
    db: AsyncSession, child_id: uuid.UUID, competency_codes: list[str]
) -> list[Recommendation]:
    """One Quick Repair per competency, in the order the competencies are given.

    The order matters and is the caller's: `service.py` puts root-cause
    candidates first, so that what is proposed first is what may be underneath
    the rest.

    At most one activity per competency. A child looking at her next steps needs
    something to do, not a catalogue; and proposing three activities for one
    difficulty would suggest the platform knows which is best, which it does not.
    """
    if not competency_codes:
        return []

    rows = (
        await db.execute(
            select(ActivityCompetency.competency_code, Activity)
            .join(Activity, Activity.id == ActivityCompetency.activity_id)
            .where(
                ActivityCompetency.competency_code.in_(competency_codes),
                Activity.kind.not_in(_NOT_A_REPAIR),
                Activity.status == ACTIVITY_STATUS_PUBLISHED,
                Activity.duration_minutes >= QUICK_REPAIR_MIN_MINUTES,
                Activity.duration_minutes <= QUICK_REPAIR_MAX_MINUTES,
            )
            .order_by(Activity.duration_minutes, Activity.code)
        )
    ).all()
    if not rows:
        return []

    history = await _history(db, child_id, [activity.id for _, activity in rows])

    candidates: dict[str, list[Activity]] = {}
    for code, activity in rows:
        candidates.setdefault(code, []).append(activity)

    recommendations = []
    for code in competency_codes:
        chosen = _choose(candidates.get(code, []), history)
        if chosen is None:
            # No short published activity works on this competency. Saying
            # nothing is the honest answer: inventing a longer one, or one that
            # works on something else, would be worse than an empty list.
            continue
        activity, already_done = chosen
        recommendations.append(
            Recommendation(
                competency_code=code,
                activity_code=activity.code,
                title=activity.title,
                kind=activity.kind,
                duration_minutes=activity.duration_minutes,
                already_done=already_done,
                reason=_reason(code, activity.duration_minutes, already_done),
                proof=PROOF,
            )
        )
    return recommendations


def _choose(
    activities: list[Activity], history: dict[uuid.UUID, str]
) -> tuple[Activity, bool] | None:
    """The activity to propose among those that fit, and whether it is a repeat.

    Never given before comes first. Already finished comes second, and is
    flagged: doing it again is a reasonable repair, but the parent should be
    told it is a second pass rather than a discovery. Anything currently
    assigned or under way is not proposed at all — it is already waiting for her.
    """
    fresh = [row for row in activities if row.id not in history]
    if fresh:
        return fresh[0], False

    done = [
        row for row in activities if history.get(row.id) == ASSIGNMENT_STATUS_COMPLETED
    ]
    if done:
        return done[0], True
    return None


def _reason(competency_code: str, minutes: int, already_done: bool) -> str:
    when = (
        "Elle a déjà été faite ; la refaire est une seconde passe, pas une "
        "découverte."
        if already_done
        else "Elle n’a pas encore été proposée à cet enfant."
    )
    return f"Activité de {minutes} minutes travaillant « {competency_code} ». {when}"


async def _history(
    db: AsyncSession, child_id: uuid.UUID, activity_ids: list[uuid.UUID]
) -> dict[uuid.UUID, str]:
    """What this child has already been given among these activities.

    A pending assignment outranks a completed one for the same activity: what
    matters here is whether it is waiting for her now, and it is.
    """
    rows = (
        await db.execute(
            select(Assignment.activity_id, Assignment.status).where(
                Assignment.child_id == child_id,
                Assignment.activity_id.in_(activity_ids),
                Assignment.status.in_((*_PENDING, ASSIGNMENT_STATUS_COMPLETED)),
            )
        )
    ).all()

    history: dict[uuid.UUID, str] = {}
    for activity_id, status in rows:
        if history.get(activity_id) in _PENDING:
            continue
        history[activity_id] = status
    return history
