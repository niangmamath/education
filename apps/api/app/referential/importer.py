"""Reconcile a draft version with the file that describes it.

Importing is not inserting. The file is the intended state of one edition, and
the import makes the database match it: rows the file adds are created, rows it
changes are updated, rows it no longer mentions are deleted. Replaying the same
file therefore reports nothing to do, which is what idempotence means here.

Reconciliation only ever touches a **draft**. A published or archived version is
refused, because attempts, xAPI events and diagnoses of the later steps point at
its competencies: editing it in place would change the meaning of traces already
recorded. A corrected programme becomes a new version, not a rewritten one.

Nothing is committed here. The caller owns the transaction, which is what lets a
dry run do the full work — flushes included, so every database constraint is
exercised — and then roll it back. A dry run that reported changes the real run
could not perform would be worse than no dry run at all.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Final, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

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
from app.referential.document import ReferentialDocument

LEVELS: Final = "levels"
SUBJECTS: Final = "subjects"
DOMAINS: Final = "domains"
COMPETENCIES: Final = "competencies"
PREREQUISITES: Final = "prerequisites"

ENTITIES: Final = (LEVELS, SUBJECTS, DOMAINS, COMPETENCIES, PREREQUISITES)


_Row = TypeVar("_Row", Level, Subject, Domain, Competency)


def _scoped(model: type[_Row], version: ReferentialVersion) -> Select[tuple[_Row]]:
    """Every row of that kind belonging to this edition, and no other."""
    return select(model).where(model.version_id == version.id)


def _by_code(rows: Iterable[_Row]) -> dict[str, _Row]:
    """Business codes are what the file and the database have in common."""
    return {row.code: row for row in rows}


# The operator reads the refusal, so the refusal speaks their language.
_STATUS_IN_FRENCH: Final = {
    VERSION_STATUS_PUBLISHED: "publiée",
    VERSION_STATUS_ARCHIVED: "archivée",
}


class ImportRefused(Exception):
    """The target version exists and may not be written to."""

    def __init__(self, code: str, status: str) -> None:
        super().__init__(
            f"La version « {code} » est {_STATUS_IN_FRENCH.get(status, status)} et ne "
            "peut plus être modifiée ; importez sous un nouveau code de version."
        )
        self.code = code
        self.status = status


@dataclass
class Counts:
    """What happened to one kind of row."""

    created: int = 0
    updated: int = 0
    deleted: int = 0

    @property
    def touched(self) -> bool:
        return bool(self.created or self.updated or self.deleted)


@dataclass
class ImportReport:
    """What the import did, or would do if it were applied."""

    version_code: str
    version_label: str
    version_status: str
    version_created: bool = False
    version_updated: bool = False
    counts: dict[str, Counts] = field(
        default_factory=lambda: {entity: Counts() for entity in ENTITIES}
    )
    applied: bool = False

    @property
    def changed(self) -> bool:
        """True when the database is not already what the file describes."""
        return (
            self.version_created
            or self.version_updated
            or any(counts.touched for counts in self.counts.values())
        )


def reconcile(session: Session, document: ReferentialDocument) -> ImportReport:
    """Make the edition match the document, without committing.

    The document is expected to have passed `validate_document` first: this
    function trusts that its references resolve.
    """
    version, report = _load_or_create_version(session, document)

    _upsert_levels(session, version, document, report)
    _upsert_subjects(session, version, document, report)
    session.flush()

    _upsert_domains(session, version, document, report)
    session.flush()

    _upsert_competencies(session, version, document, report)
    session.flush()

    _reconcile_prerequisites(session, version, document, report)
    session.flush()

    # Deletions run from the leaves up, so that a row is gone before the row it
    # pointed at. The database would cascade anyway; doing it in the open is
    # what keeps the reported counts honest.
    _delete_missing_competencies(session, version, document, report)
    session.flush()
    _delete_missing_domains(session, version, document, report)
    _delete_missing_subjects(session, version, document, report)
    _delete_missing_levels(session, version, document, report)
    session.flush()

    return report


def _load_or_create_version(
    session: Session, document: ReferentialDocument
) -> tuple[ReferentialVersion, ImportReport]:
    version = session.scalars(
        select(ReferentialVersion).where(
            ReferentialVersion.code == document.version.code
        )
    ).one_or_none()

    if version is None:
        version = ReferentialVersion(
            code=document.version.code,
            label=document.version.label,
            status=VERSION_STATUS_DRAFT,
        )
        session.add(version)
        session.flush()
        return version, ImportReport(
            version_code=version.code,
            version_label=version.label,
            version_status=version.status,
            version_created=True,
        )

    if version.status != VERSION_STATUS_DRAFT:
        raise ImportRefused(version.code, version.status)

    report = ImportReport(
        version_code=version.code,
        version_label=document.version.label,
        version_status=version.status,
    )
    if version.label != document.version.label:
        version.label = document.version.label
        report.version_updated = True
    return version, report


def _upsert_levels(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    existing = _by_code(session.scalars(_scoped(Level, version)))
    for level in document.levels:
        row = existing.get(level.code)
        if row is None:
            session.add(
                Level(
                    version_id=version.id,
                    code=level.code,
                    label=level.label,
                    position=level.position,
                )
            )
            report.counts[LEVELS].created += 1
        elif (row.label, row.position) != (level.label, level.position):
            row.label = level.label
            row.position = level.position
            report.counts[LEVELS].updated += 1


def _upsert_subjects(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    existing = _by_code(session.scalars(_scoped(Subject, version)))
    for subject in document.subjects:
        row = existing.get(subject.code)
        if row is None:
            session.add(
                Subject(
                    version_id=version.id,
                    code=subject.code,
                    label=subject.label,
                    position=subject.position,
                )
            )
            report.counts[SUBJECTS].created += 1
        elif (row.label, row.position) != (subject.label, subject.position):
            row.label = subject.label
            row.position = subject.position
            report.counts[SUBJECTS].updated += 1


def _upsert_domains(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    subject_ids = {
        row.code: row.id for row in session.scalars(_scoped(Subject, version))
    }
    existing = _by_code(session.scalars(_scoped(Domain, version)))
    for subject, domain in document.domains():
        subject_id = subject_ids[subject.code]
        row = existing.get(domain.code)
        if row is None:
            session.add(
                Domain(
                    version_id=version.id,
                    subject_id=subject_id,
                    code=domain.code,
                    label=domain.label,
                    position=domain.position,
                )
            )
            report.counts[DOMAINS].created += 1
        elif (row.subject_id, row.label, row.position) != (
            subject_id,
            domain.label,
            domain.position,
        ):
            row.subject_id = subject_id
            row.label = domain.label
            row.position = domain.position
            report.counts[DOMAINS].updated += 1


def _upsert_competencies(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    domain_ids = {row.code: row.id for row in session.scalars(_scoped(Domain, version))}
    level_ids = {row.code: row.id for row in session.scalars(_scoped(Level, version))}
    existing = _by_code(session.scalars(_scoped(Competency, version)))

    for competency in document.competencies:
        domain_id = domain_ids[competency.domain]
        level_id = level_ids[competency.level]
        row = existing.get(competency.code)
        if row is None:
            session.add(
                Competency(
                    version_id=version.id,
                    domain_id=domain_id,
                    level_id=level_id,
                    code=competency.code,
                    label=competency.label,
                    description=competency.description,
                    position=competency.position,
                )
            )
            report.counts[COMPETENCIES].created += 1
        elif (
            row.domain_id,
            row.level_id,
            row.label,
            row.description,
            row.position,
        ) != (
            domain_id,
            level_id,
            competency.label,
            competency.description,
            competency.position,
        ):
            row.domain_id = domain_id
            row.level_id = level_id
            row.label = competency.label
            row.description = competency.description
            row.position = competency.position
            report.counts[COMPETENCIES].updated += 1


def _reconcile_prerequisites(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    """An edge is either there or not: it has nothing to update."""
    competency_ids = {
        row.code: row.id for row in session.scalars(_scoped(Competency, version))
    }
    codes_by_id = {row_id: code for code, row_id in competency_ids.items()}

    desired = {
        (competency.code, required)
        for competency in document.competencies
        for required in competency.prerequisites
    }
    existing = {
        (codes_by_id[edge.competency_id], codes_by_id[edge.prerequisite_id]): edge
        for edge in session.scalars(
            select(CompetencyPrerequisite).where(
                CompetencyPrerequisite.version_id == version.id
            )
        )
    }

    for pair in desired - set(existing):
        holder, required = pair
        session.add(
            CompetencyPrerequisite(
                competency_id=competency_ids[holder],
                prerequisite_id=competency_ids[required],
                version_id=version.id,
            )
        )
        report.counts[PREREQUISITES].created += 1

    for pair, edge in existing.items():
        if pair not in desired:
            session.delete(edge)
            report.counts[PREREQUISITES].deleted += 1


def _delete_missing_competencies(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    kept = {competency.code for competency in document.competencies}
    for row in session.scalars(_scoped(Competency, version)):
        if row.code not in kept:
            session.delete(row)
            report.counts[COMPETENCIES].deleted += 1


def _delete_missing_domains(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    kept = {domain.code for _, domain in document.domains()}
    for row in session.scalars(_scoped(Domain, version)):
        if row.code not in kept:
            session.delete(row)
            report.counts[DOMAINS].deleted += 1


def _delete_missing_subjects(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    kept = {subject.code for subject in document.subjects}
    for row in session.scalars(_scoped(Subject, version)):
        if row.code not in kept:
            session.delete(row)
            report.counts[SUBJECTS].deleted += 1


def _delete_missing_levels(
    session: Session,
    version: ReferentialVersion,
    document: ReferentialDocument,
    report: ImportReport,
) -> None:
    kept = {level.code for level in document.levels}
    for row in session.scalars(_scoped(Level, version)):
        if row.code not in kept:
            session.delete(row)
            report.counts[LEVELS].deleted += 1
