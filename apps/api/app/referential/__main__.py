"""Manage referential editions from the command line.

    python -m app.referential import <fichier.json>            essai à blanc
    python -m app.referential import <fichier.json> --apply    écriture
    python -m app.referential publish <code>                   mise en vigueur

Importing corrects a draft and may be run twenty times while a programme is
being written. Publishing is a single decision that changes what every reader
sees. They are two verbs so that a mistyped import can never put an edition in
force.

An import is a dry run by default, because it rewrites a whole edition,
deletions included. The dry run does the entire work inside a transaction it
then rolls back, so what it reports is what `--apply` will do, constraint
failures included.

These are commands and not routes: they write a whole edition at once, and the
Administrator role that would guard such a route belongs to step 15.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
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
from app.referential.publication import PublicationRefused, publish
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
        description="Gère les éditions du référentiel scolaire.",
    )
    verbs = parser.add_subparsers(dest="verbe", required=True)

    importer = verbs.add_parser(
        "import", help="importer une édition depuis un fichier JSON"
    )
    importer.add_argument("fichier", type=Path, help="fichier JSON décrivant l’édition")
    importer.add_argument(
        "--apply",
        action="store_true",
        help="écrire réellement ; sans ce drapeau, rien n’est enregistré",
    )
    importer.add_argument(
        "--database-url", default=DATABASE_URL, help=argparse.SUPPRESS
    )

    publisher = verbs.add_parser("publish", help="mettre une édition en vigueur")
    publisher.add_argument("code", help="code de l’édition à publier")
    publisher.add_argument(
        "--database-url", default=DATABASE_URL, help=argparse.SUPPRESS
    )

    arguments = parser.parse_args(argv)
    if arguments.verbe == "publish":
        return _publish(arguments.code, arguments.database_url)
    return _import(arguments.fichier, arguments.database_url, arguments.apply)


@contextmanager
def _database(url: str) -> Iterator[Session]:
    """One session, one engine, disposed whatever happens."""
    engine = create_engine(sync_database_url(url))
    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def _guarded(session: Session, work: Callable[[], int]) -> int:
    """Run a command, turning the two expected refusals into exit codes."""
    try:
        return work()
    except (ImportRefused, PublicationRefused) as refusal:
        session.rollback()
        print(str(refusal), file=sys.stderr)
        return EXIT_REFUSED
    except SQLAlchemyError as error:
        session.rollback()
        print(f"Refus de la base de données : {error}", file=sys.stderr)
        return EXIT_DATABASE


def _import(path: Path, url: str, apply: bool) -> int:
    document, issues = _read(path)
    if document is None:
        return _report_issues(issues) if issues else EXIT_UNREADABLE

    issues = validate_document(document)
    if issues:
        return _report_issues(issues)

    with _database(url) as session:

        def work() -> int:
            report = reconcile(session, document)
            if apply:
                session.commit()
                report.applied = True
            else:
                session.rollback()
            _print_import(report, path)
            return EXIT_OK

        return _guarded(session, work)


def _publish(code: str, url: str) -> int:
    with _database(url) as session:

        def work() -> int:
            report = publish(session, code)
            session.commit()

            if report.was_already_published:
                print(f"{report.code} « {report.label} » est déjà en vigueur.")
                return EXIT_OK

            print(f"{report.code} « {report.label} »")
            print("  brouillon → en vigueur")
            if report.archived_code is not None:
                print(f"  {report.archived_code} : en vigueur → archivée")
            return EXIT_OK

        return _guarded(session, work)


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


def _report_issues(issues: list[ImportIssue]) -> int:
    plural = "s" if len(issues) > 1 else ""
    print(f"Fichier refusé, {len(issues)} erreur{plural} :", file=sys.stderr)
    for issue in issues:
        print(f"  - {issue}", file=sys.stderr)
    return EXIT_INVALID


def _print_import(report: ImportReport, path: Path) -> None:
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
