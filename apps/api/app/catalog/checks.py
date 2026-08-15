"""Find the links ADR-013 knowingly left unprotected.

The catalogue names competencies by their business code, with no foreign key, so
that it survives the publication of a new referential edition. The cost is that
a code designating nothing is accepted by the database. Such a link does not
break a reading: the activity is simply absent from results filtered on that
code — a silence, which is more dangerous than an error.

This is the counterpart that decision owes, and it should be run after every
publication of an edition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Activity, ActivityCompetency
from app.models.referential import Competency
from app.referential.publication import published_version


@dataclass
class DanglingLink:
    activity_code: str
    activity_title: str
    competency_code: str


@dataclass
class CheckReport:
    """What the catalogue looks like against the edition in force."""

    edition_code: str | None
    linked_codes: int = 0
    dangling: list[DanglingLink] = field(default_factory=list)
    activities_without_link: list[str] = field(default_factory=list)

    @property
    def sound(self) -> bool:
        return not self.dangling and not self.activities_without_link


def check_catalogue(session: Session) -> CheckReport:
    """Resolve every competency link against the published edition."""
    edition = published_version(session)
    if edition is None:
        return CheckReport(edition_code=None)

    known = set(
        session.scalars(
            select(Competency.code).where(Competency.version_id == edition.id)
        )
    )

    report = CheckReport(edition_code=edition.code)
    rows = session.execute(
        select(Activity.code, Activity.title, ActivityCompetency.competency_code)
        .join(ActivityCompetency, ActivityCompetency.activity_id == Activity.id)
        .order_by(Activity.code, ActivityCompetency.competency_code)
    )
    for activity_code, title, competency_code in rows:
        report.linked_codes += 1
        if competency_code not in known:
            report.dangling.append(
                DanglingLink(
                    activity_code=activity_code,
                    activity_title=title,
                    competency_code=competency_code,
                )
            )

    # An activity attached to nothing can never be recommended by step 12. It is
    # not a broken link, but it is just as silently useless.
    report.activities_without_link = list(
        session.scalars(
            select(Activity.code)
            .outerjoin(
                ActivityCompetency, ActivityCompetency.activity_id == Activity.id
            )
            .where(ActivityCompetency.id.is_(None))
            .order_by(Activity.code)
        )
    )
    return report
