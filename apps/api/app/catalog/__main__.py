"""Manage the catalogue from the command line.

    python -m app.catalog register <code-activité> <fichier.h5p> --licence L --source U
    python -m app.catalog check

There is no editor and no upload route, by ADR-006 and ADR-012. A package is
inspected, stored and recorded by someone with access to the server, which is
the whole of the "no unsafe import" the step asked for.

`check` is what ADR-013 owes: it resolves every competency link of the catalogue
against the edition in force and returns non-zero when something dangles.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.catalog.checks import check_catalogue
from app.catalog.h5p import PackageRefused
from app.catalog.registration import RegistrationRefused, register_package
from app.catalog.storage import S3ObjectStore
from app.core.db import DATABASE_URL, sync_database_url

EXIT_OK: Final = 0
EXIT_REFUSED: Final = 3
EXIT_DATABASE: Final = 4
EXIT_DANGLING: Final = 5


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.catalog",
        description="Gère le catalogue d’activités et ses paquets H5P.",
    )
    verbs = parser.add_subparsers(dest="verbe", required=True)

    register = verbs.add_parser("register", help="enregistrer un paquet H5P vérifié")
    register.add_argument("activite", help="code de l’activité qui joue ce paquet")
    register.add_argument("fichier", type=Path, help="fichier .h5p à vérifier")
    register.add_argument(
        "--licence", required=True, help="licence vérifiée du contenu, ADR-012"
    )
    register.add_argument(
        "--source", required=True, help="provenance vérifiée du contenu, ADR-012"
    )
    register.add_argument(
        "--database-url", default=DATABASE_URL, help=argparse.SUPPRESS
    )

    check = verbs.add_parser(
        "check", help="vérifier les liens du catalogue vers le référentiel"
    )
    check.add_argument("--database-url", default=DATABASE_URL, help=argparse.SUPPRESS)

    arguments = parser.parse_args(argv)
    if arguments.verbe == "check":
        return _check(arguments.database_url)
    return _register(
        arguments.activite,
        arguments.fichier,
        arguments.licence,
        arguments.source,
        arguments.database_url,
    )


def _register(
    activity_code: str, path: Path, licence: str, source: str, url: str
) -> int:
    engine = create_engine(sync_database_url(url))
    try:
        with Session(engine) as session:
            try:
                report = register_package(
                    session,
                    S3ObjectStore(),
                    activity_code=activity_code,
                    path=path,
                    licence=licence,
                    source=source,
                )
                session.commit()
            except (PackageRefused, RegistrationRefused) as refusal:
                session.rollback()
                print(str(refusal), file=sys.stderr)
                return EXIT_REFUSED
            except SQLAlchemyError as error:
                session.rollback()
                print(f"Refus de la base de données : {error}", file=sys.stderr)
                return EXIT_DATABASE
    finally:
        engine.dispose()

    print(f"Activité   : {report.activity_code}")
    print(f"Type H5P   : {report.library}, autorisé par ADR-012")
    print(f"Empreinte  : {report.sha256}")
    print(f"Taille     : {report.size_bytes} octets")
    print(f"Objet      : {report.object_key}")
    print("Paquet enregistré.")
    return EXIT_OK


def _check(url: str) -> int:
    engine = create_engine(sync_database_url(url))
    try:
        with Session(engine) as session:
            report = check_catalogue(session)
    finally:
        engine.dispose()

    if report.edition_code is None:
        print(
            "Aucune édition du référentiel n’est en vigueur : les liens du "
            "catalogue ne peuvent pas être résolus.",
            file=sys.stderr,
        )
        return EXIT_DANGLING

    print(f"Édition    : {report.edition_code}")
    print(f"Liens      : {report.linked_codes}")

    for link in report.dangling:
        print(
            f"  - {link.activity_code} « {link.activity_title} » cite la compétence "
            f"« {link.competency_code} », absente de l’édition en vigueur.",
            file=sys.stderr,
        )
    for code in report.activities_without_link:
        print(
            f"  - {code} n’est reliée à aucune compétence, donc ne sera jamais "
            "recommandée.",
            file=sys.stderr,
        )

    if report.sound:
        print("Catalogue cohérent avec l’édition en vigueur.")
        return EXIT_OK

    print(
        f"{len(report.dangling)} lien(s) mort(s), "
        f"{len(report.activities_without_link)} activité(s) sans lien.",
        file=sys.stderr,
    )
    return EXIT_DANGLING


if __name__ == "__main__":
    raise SystemExit(main())
