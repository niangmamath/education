"""Import a referential file from the command line.

    python -m app.referential <fichier.json>            essai à blanc
    python -m app.referential <fichier.json> --apply    écriture

A dry run is the default because an import rewrites a whole edition, deletions
included. The dry run does the entire work inside a transaction it then rolls
back, so what it reports is what `--apply` will do, constraint failures
included.

The import is a command and not a route: it writes a whole edition at once, and
the Administrator role that would guard such a route belongs to step 15.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Final

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import DATABASE_URL, sync_database_url
from app.referential.document import ReferentialDocument, read_json
from app.referential.importer import (
    COMPETENCIES,
    DOMAINS,
    LEVELS,
    PREREQUISITES,
    SUBJECTS,
    ImportRefused,
    ImportReport,
    reconcile,
)
from app.referential.validation import (
    ImportIssue,
    issues_from_validation_error,
    validate_document,
)

EXIT_OK: Final = 0
EXIT_UNREADABLE: Final = 1
EXIT_INVALID: Final = 2
EXIT_REFUSED: Final = 3
EXIT_DATABASE: Final = 4

# Label, and whether French makes the past participle agree in the feminine.
ENTITY_NAMES: Final = {
    LEVELS: ("Niveaux", False),
    SUBJECTS: ("Matières", True),
    DOMAINS: ("Domaines", False),
    COMPETENCIES: ("Compétences", True),
    PREREQUISITES: ("Prérequis", False),
}
COLUMN: Final = max(len(name) for name, _ in ENTITY_NAMES.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.referential",
        description="Importe une édition du référentiel scolaire depuis un fichier JSON.",
    )
    parser.add_argument("fichier", type=Path, help="fichier JSON décrivant l’édition")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="écrire réellement ; sans ce drapeau, rien n’est enregistré",
    )
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help="base cible ; par défaut celle de la configuration",
    )
    arguments = parser.parse_args(argv)

    document, issues = _read(arguments.fichier)
    if document is None:
        return _report_issues(issues) if issues else EXIT_UNREADABLE

    issues = validate_document(document)
    if issues:
        return _report_issues(issues)

    return _import(document, arguments.fichier, arguments.database_url, arguments.apply)


def _read(path: Path) -> tuple[ReferentialDocument | None, list[ImportIssue]]:
    """Read and shape the file, or say why it could not be read."""
    try:
        payload = read_json(path)
    except OSError as error:
        print(f"Fichier illisible : {error}", file=sys.stderr)
        return None, []
    except json.JSONDecodeError as error:
        return None, [ImportIssue(path=str(path), message=f"JSON invalide, {error}")]

    try:
        return ReferentialDocument.model_validate(payload), []
    except ValidationError as error:
        return None, issues_from_validation_error(error)


def _import(document: ReferentialDocument, path: Path, url: str, apply: bool) -> int:
    engine = create_engine(sync_database_url(url))
    try:
        with Session(engine) as session:
            try:
                report = reconcile(session, document)
            except ImportRefused as refusal:
                session.rollback()
                print(str(refusal), file=sys.stderr)
                return EXIT_REFUSED
            except SQLAlchemyError as error:
                session.rollback()
                print(f"Refus de la base de données : {error}", file=sys.stderr)
                return EXIT_DATABASE

            if apply:
                session.commit()
                report.applied = True
            else:
                session.rollback()
    finally:
        engine.dispose()

    _print_report(report, path)
    return EXIT_OK


def _report_issues(issues: list[ImportIssue]) -> int:
    plural = "s" if len(issues) > 1 else ""
    print(f"Fichier refusé, {len(issues)} erreur{plural} :", file=sys.stderr)
    for issue in issues:
        print(f"  - {issue}", file=sys.stderr)
    return EXIT_INVALID


def _print_report(report: ImportReport, path: Path) -> None:
    print(f"Fichier   : {path}")
    print(
        f"Version   : {report.version_code} « {report.version_label} », "
        f"{_version_state(report)}"
    )
    for entity, (name, feminine) in ENTITY_NAMES.items():
        counts = report.counts[entity]
        parts = [
            _count(counts.created, "créé", feminine),
            _count(counts.deleted, "supprimé", feminine),
        ]
        if entity != PREREQUISITES:
            parts.insert(1, _count(counts.updated, "modifié", feminine))
        print(f"{name.ljust(COLUMN)} : {', '.join(parts)}")

    if not report.applied:
        state = "identique au fichier" if not report.changed else "à mettre à jour"
        print(f"Essai à blanc : rien n’a été écrit, base {state}.")
        if report.changed:
            print("Relancez avec --apply pour appliquer ces changements.")
    elif report.changed:
        print("Import appliqué.")
    else:
        print("Import appliqué : la base était déjà conforme au fichier.")


def _version_state(report: ImportReport) -> str:
    if report.version_created:
        return "brouillon créé"
    if report.version_updated:
        return "brouillon existant, intitulé mis à jour"
    return "brouillon existant"


def _count(quantity: int, participle: str, feminine: bool) -> str:
    """« 1 créé », « 2 créées » : French agrees, so the report agrees too."""
    agreement = ("e" if feminine else "") + ("s" if quantity > 1 else "")
    return f"{quantity} {participle}{agreement}"


if __name__ == "__main__":
    raise SystemExit(main())
