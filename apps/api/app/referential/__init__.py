"""Controlled import of a school referential edition.

An import file describes one whole edition: its version, its levels, its
subjects and their domains, and the competencies attached to a domain and a
level. The file speaks in business codes only, never in database identifiers,
so it stays readable and can be replayed against an empty database.

The import is idempotent by reconciliation: replaying the same file against the
draft it created leaves the database exactly as it was. See
`docs/backend/import-referentiel.md`.
"""

from app.referential.document import ReferentialDocument
from app.referential.importer import Counts, ImportRefused, ImportReport, reconcile
from app.referential.validation import ImportIssue, validate_document

__all__ = [
    "Counts",
    "ImportIssue",
    "ImportRefused",
    "ImportReport",
    "ReferentialDocument",
    "reconcile",
    "validate_document",
]
