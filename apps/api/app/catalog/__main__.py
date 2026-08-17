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

import tempfile

from app.catalog.checks import check_catalogue
from app.catalog.h5p import PackageRefused
from app.catalog.registration import RegistrationRefused, register_package
from sqlalchemy import select
from app.catalog.storage import S3ObjectStore
from app.content import deploy as runtime
from app.core.config import settings
from app.core.db import DATABASE_URL, sync_database_url
from app.models.catalog import Activity

# Où le projet garde son arbre de bibliothèques : `deploy-runtime` le pose tel
# quel dans l'origine de contenu, et `libraries` y ajoute ce que de nouveaux
# paquets apportent.
PREPARED_LIBRARIES: Final = Path("experiments/h5p-spike/player/runtime/content")

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

    deploy = verbs.add_parser(
        "deploy", help="déployer un paquet vers l’origine de contenu"
    )
    deploy.add_argument("activite", help="code de l’activité à déployer")
    deploy.add_argument("--database-url", default=DATABASE_URL, help=argparse.SUPPRESS)

    runtime_parser = verbs.add_parser(
        "deploy-runtime",
        help="déployer les bibliothèques et le lecteur préparés hors ligne",
    )
    runtime_parser.add_argument(
        "dossier", type=Path, help="dossier préparé contenant libraries/ et player/"
    )

    libraries_parser = verbs.add_parser(
        "libraries",
        help="installer les bibliothèques que portent des paquets .h5p téléchargés",
    )
    libraries_parser.add_argument(
        "fichiers", type=Path, nargs="+", help="fichiers .h5p à dépouiller"
    )
    libraries_parser.add_argument(
        "--vers",
        type=Path,
        default=PREPARED_LIBRARIES,
        help=f"arbre de bibliothèques préparé (défaut : {PREPARED_LIBRARIES})",
    )

    arguments = parser.parse_args(argv)
    if arguments.verbe == "check":
        return _check(arguments.database_url)
    if arguments.verbe == "deploy":
        return _deploy(arguments.activite, arguments.database_url)
    if arguments.verbe == "deploy-runtime":
        return _deploy_runtime(arguments.dossier)
    if arguments.verbe == "libraries":
        return _libraries(arguments.fichiers, arguments.vers)
    return _register(
        arguments.activite,
        arguments.fichier,
        arguments.licence,
        arguments.source,
        arguments.database_url,
    )


def _libraries(packages: list[Path], prepared: Path) -> int:
    """Take the libraries out of downloaded packages and put them where the
    player looks.

    This is the step that used to be called "preparing the libraries offline",
    and it turns out to be nothing more than this: an `.h5p` already carries
    everything it needs to play. Nothing is fetched from the network here.
    """
    added: list[str] = []
    barren: list[str] = []
    for package in packages:
        try:
            report = runtime.merge_libraries(prepared, package)
        except (runtime.DeploymentRefused, OSError) as refusal:
            print(f"{package.name} : {refusal}", file=sys.stderr)
            return EXIT_REFUSED

        if not report.found:
            barren.append(package.name)
            print(
                f"{package.name} : AUCUNE bibliothèque dans l’archive.",
                file=sys.stderr,
            )
            continue

        added.extend(report.added)
        print(
            f"{package.name} : {len(report.found)} bibliothèque(s) portée(s), "
            f"{len(report.added)} nouvelle(s)"
        )
        for library in report.added:
            print(f"  + {library}")

    if barren:
        print(
            "\nCes archives ne contiennent que « h5p.json » et « content/ » : "
            "ce sont des exports « contenu seul ». Elles ne joueront pas tant que "
            "leurs bibliothèques ne sont pas dans l’arbre. Sur h5p.org, reprenez "
            "le téléchargement depuis la page du contenu — le bouton « Reuse » "
            "propose parfois la forme sans bibliothèques.",
            file=sys.stderr,
        )

    if not added:
        print("Aucune bibliothèque nouvelle installée.")
    else:
        print(f"\n{len(set(added))} bibliothèque(s) installée(s) dans {prepared}.")
        print("Déployez maintenant le runtime pour que l’origine les serve :")
        print(
            "  python -m app.catalog deploy-runtime "
            "experiments/h5p-spike/player/runtime"
        )
    return EXIT_OK


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


def _deploy(activity_code: str, url: str) -> int:
    """Lay a vetted package out where the content origin can serve it.

    The archive is read back from the bucket rather than from any copy that
    happens to be on disk: what is served must be what was vetted.
    """
    engine = create_engine(sync_database_url(url))
    try:
        with Session(engine) as session:
            activity = session.scalars(
                select(Activity).where(Activity.code == activity_code)
            ).one_or_none()
            if activity is None or activity.h5p_package is None:
                print(
                    f"L’activité « {activity_code} » n’existe pas ou n’a pas de "
                    "paquet H5P.",
                    file=sys.stderr,
                )
                return EXIT_REFUSED
            package = activity.h5p_package
            object_key, digest = package.object_key, package.sha256
    finally:
        engine.dispose()

    root = Path(settings.CONTENT_RUNTIME_ROOT)
    with tempfile.TemporaryDirectory() as workspace:
        archive = Path(workspace) / "package.h5p"
        try:
            S3ObjectStore().get(object_key, archive)
            report = runtime.deploy_package(root, archive, digest)
        except runtime.DeploymentRefused as refusal:
            print(str(refusal), file=sys.stderr)
            return EXIT_REFUSED

    print(f"Activité   : {activity_code}")
    print(f"Empreinte  : {report.digest}")
    print(f"Déployé    : {report.files} fichiers, {report.bytes_written} octets")
    print(f"Chemin     : {report.path}")
    return EXIT_OK


def _deploy_runtime(prepared: Path) -> int:
    """Put the offline-prepared libraries and player in place.

    ADR-012, condition 3: the libraries are internal artefacts, prepared away
    from the platform and frozen. An inventory of their digests is written
    beside them, because an artefact nobody can name is not frozen.
    """
    root = Path(settings.CONTENT_RUNTIME_ROOT)
    try:
        inventory = runtime.deploy_libraries(root, prepared / "libraries")
        players = runtime.deploy_player(root, prepared / "player")
    except runtime.DeploymentRefused as refusal:
        print(str(refusal), file=sys.stderr)
        return EXIT_REFUSED

    print(f"Bibliothèques : {len(inventory)} fichiers, inventaire écrit")
    print(f"Lecteur       : {players} fichiers")
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
