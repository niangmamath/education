"""Put one edition of the referential in force, and step the previous one aside.

Publishing is deliberately not part of importing. An import corrects a draft and
may be run twenty times while a programme is being written; putting an edition
in force is a single decision that changes what every reader sees. Keeping them
apart means a mistyped import can never publish anything.

Only one edition may be in force at a time — a partial unique index says so —
so publishing archives the edition it replaces, in the same transaction. There
is no moment where two editions are published, and no moment where none is.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.referential import (
    VERSION_STATUS_ARCHIVED,
    VERSION_STATUS_PUBLISHED,
    ReferentialVersion,
)


class PublicationRefused(Exception):
    """The named edition cannot be put in force."""


@dataclass
class PublicationReport:
    """What publishing did, or found already done."""

    code: str
    label: str
    was_already_published: bool = False
    archived_code: str | None = None
    archived_label: str | None = None


def publish(session: Session, code: str) -> PublicationReport:
    """Put the named draft in force. The caller owns the transaction."""
    version = session.scalars(
        select(ReferentialVersion).where(ReferentialVersion.code == code)
    ).one_or_none()

    if version is None:
        raise PublicationRefused(f"Aucune édition ne porte le code « {code} ».")

    if version.status == VERSION_STATUS_PUBLISHED:
        return PublicationReport(
            code=version.code, label=version.label, was_already_published=True
        )

    if version.status == VERSION_STATUS_ARCHIVED:
        # Bringing a retired edition back would silently change the meaning of
        # every trace recorded since it was archived. If it must serve again,
        # that is a decision, not a command's default.
        raise PublicationRefused(
            f"L’édition « {code} » est archivée. Remettre en vigueur une édition "
            "retirée est une décision à part entière, que cette commande ne prend pas."
        )

    report = PublicationReport(code=version.code, label=version.label)

    in_force = session.scalars(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    ).one_or_none()
    if in_force is not None:
        in_force.status = VERSION_STATUS_ARCHIVED
        report.archived_code = in_force.code
        report.archived_label = in_force.label
        # Freed before the new edition claims it: the partial unique index
        # tolerates no overlap, however brief.
        session.flush()

    version.status = VERSION_STATUS_PUBLISHED
    session.flush()
    return report


def published_version(session: Session) -> ReferentialVersion | None:
    """The edition currently in force, if there is one."""
    return session.scalars(
        select(ReferentialVersion).where(
            ReferentialVersion.status == VERSION_STATUS_PUBLISHED
        )
    ).one_or_none()


__all__ = [
    "PublicationRefused",
    "PublicationReport",
    "publish",
    "published_version",
]
