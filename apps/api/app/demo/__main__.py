"""Build the demonstration dataset.

    python -m app.demo            # créer, ou compléter ce qui manque
    python -m app.demo --reset    # tout retirer, puis recréer
    python -m app.demo --clean    # tout retirer et s'arrêter

**Everything goes through the real services.** The attempts are started,
answered and completed by the same code a child's browser reaches, so the
readings on screen are produced by the rules and not written down beside them.
A demonstration whose data was inserted directly would be a demonstration of the
tables, and it would drift from the product the first time a rule changed.

The dataset itself is described in `dataset.py`, which says why each piece of it
is there. This file only builds it.

Nothing here is destructive beyond its own prefix: `--reset` removes what
carries `demo-` and leaves whatever else the database holds.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeVar

from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.assignments import service as assignments
from app.attempts import service as attempts
from app.catalog.registration import RegistrationRefused, register_package
from app.catalog.storage import S3ObjectStore
from app.content import deploy as runtime
from app.core.config import settings
from app.core.db import AsyncSessionFactory, sync_database_url
from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import generate_family_code, hash_password, hash_pin
from app.demo import dataset
from app.models.catalog import (
    ACTIVITY_KIND_H5P,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
)
from app.models.identity import CHILD_STATUS_ACTIVE, Child, Parent
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.models.referential import ReferentialVersion
from app.referential.publication import PublicationRefused, publish

EXIT_OK: Final = 0
EXIT_FAILED: Final = 1

T = TypeVar("T")
# One act of a demonstration child's past: what a single HTTP request would do.
Act = Callable[[AsyncSession, Parent, Child], Awaitable[T]]


@dataclass(frozen=True)
class SeededChild:
    """One demonstration profile, with the code the operator must be told."""

    child: Child
    pin: str


@dataclass(frozen=True)
class SeededFamily:
    parent: Parent
    children: list[SeededChild]


# The vetted package of ADR-012's evidence: one True/False question, the only
# H5P type the pilot allows. Every playable demonstration activity gets this
# same file — the point being demonstrated is the platform, not the content.
# Mounted read-only into the API container by Docker Compose. These are project
# artefacts the API has to lay out, and ADR-012's third condition asks that the
# libraries be prepared away from the platform and frozen — so they are read
# from where they were prepared, never rebuilt here.
SPIKE: Final = Path("/opt/h5p-spike")
PACKAGE_NAME: Final = "packages/true-false-question-34806.h5p"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.demo",
        description="Construit un jeu de données de démonstration, entièrement fictif.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="retirer les données de démonstration d’abord",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="retirer les données de démonstration et s’arrêter",
    )
    parser.add_argument(
        "--spike",
        type=Path,
        default=SPIKE,
        help="dossier des artefacts H5P vérifiés (paquet et runtime préparé)",
    )
    arguments = parser.parse_args(argv)

    if arguments.reset or arguments.clean:
        removed = clean()
        print(
            f"Données de démonstration retirées ({removed} comptes, activités, édition)."
        )
        if arguments.clean:
            return EXIT_OK

    try:
        asyncio.run(build(arguments.spike))
    except Exception as error:  # pragma: no cover - operator feedback
        print(f"Échec : {error}", file=sys.stderr)
        return EXIT_FAILED
    return EXIT_OK


def clean() -> int:
    """Take back exactly what the prefix names.

    Order matters only because of the referential's partial unique index: the
    edition is deleted last so nothing is left pointing at half of it.
    """
    engine = create_engine(sync_database_url())
    removed = 0
    try:
        with engine.begin() as connection:
            removed += connection.execute(
                text(
                    "DELETE FROM assignments WHERE activity_id IN "
                    "(SELECT id FROM catalog_activities WHERE code LIKE :p)"
                ),
                {"p": f"{dataset.PREFIX}%"},
            ).rowcount
            removed += connection.execute(
                text("DELETE FROM catalog_activities WHERE code LIKE :p"),
                {"p": f"{dataset.PREFIX}%"},
            ).rowcount
            removed += connection.execute(
                text("DELETE FROM auth_parents WHERE email LIKE :p"),
                {"p": f"{dataset.PREFIX}%"},
            ).rowcount
            removed += connection.execute(
                text("DELETE FROM ref_versions WHERE code LIKE :p"),
                {"p": f"{dataset.PREFIX}%"},
            ).rowcount
    finally:
        engine.dispose()
    return removed


async def build(spike: Path) -> None:
    _referential()
    _activities()
    packaged = _packages(spike)

    async with AsyncSessionFactory() as db:
        families = await _families(db)
        await db.commit()
        for family in families:
            for entry in family.children:
                await db.refresh(entry.child)
            await db.refresh(family.parent)

    await _history(families)
    _report(families, packaged)


def _referential() -> None:
    """Put the demonstration edition in force.

    Publishing archives whatever edition was in force, which is the platform's
    own rule and not a shortcut taken here: only one edition may be published at
    a time. `--clean` removes this one, and the previous one stays archived —
    putting it back in force is a decision, not a side effect of a demo script.
    """
    engine = create_engine(sync_database_url())
    try:
        with Session(engine) as session:
            existing = session.scalar(
                select(ReferentialVersion).where(
                    ReferentialVersion.code == dataset.EDITION_CODE
                )
            )
            if existing is None:
                reconcile(
                    session, ReferentialDocument.model_validate(dataset.referential())
                )
            try:
                publish(session, dataset.EDITION_CODE)
            except PublicationRefused as refusal:
                # Already in force, or archived by a later edition. Neither is a
                # reason to stop: the rest of the dataset stands on its own, and
                # only the grouping of gaps needs the tree.
                print(f"Édition non republiée : {refusal}", file=sys.stderr)
            session.commit()
    finally:
        engine.dispose()


def _activities() -> None:
    engine = create_engine(sync_database_url())
    try:
        with Session(engine) as session:
            for code, title, competency, minutes in dataset.ACTIVITIES:
                if session.scalar(select(Activity).where(Activity.code == code)):
                    continue
                activity = Activity(
                    code=code,
                    title=title,
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=minutes,
                )
                session.add(activity)
                session.flush()
                session.add(
                    ActivityCompetency(
                        activity_id=activity.id, competency_code=competency
                    )
                )
            session.commit()
    finally:
        engine.dispose()


def _packages(spike: Path) -> list[str]:
    """Register the vetted package on the activities a demonstration opens.

    The archive is inspected and stored by the same code an operator would use,
    then laid out for the content origin. If the object store or the runtime
    volume is out of reach, the rest of the demonstration is still built and the
    caller is told which activities will not play — a dataset that half exists
    is more useful than a script that refuses to finish.
    """
    archive = spike / PACKAGE_NAME
    if not archive.is_file():
        print(f"Paquet H5P introuvable : {archive}", file=sys.stderr)
        return []

    root = Path(settings.CONTENT_RUNTIME_ROOT)
    try:
        # The spike prepared the libraries under `runtime/content`; the deploy
        # helper names that tree `libraries`. Passing the path directly keeps the
        # rename in one place instead of copying the tree to rename a folder.
        runtime.deploy_libraries(root, spike / "player" / "runtime" / "content")
        runtime.deploy_player(root, spike / "player" / "runtime" / "player")
    except (runtime.DeploymentRefused, OSError) as refusal:
        print(f"Runtime de contenu non déployé : {refusal}", file=sys.stderr)

    engine = create_engine(sync_database_url())
    store = S3ObjectStore()
    packaged: list[str] = []
    try:
        for code in dataset.PLAYABLE:
            with Session(engine) as session:
                try:
                    report = register_package(
                        session,
                        store,
                        activity_code=code,
                        path=archive,
                        licence="MIT, paquet de démonstration H5P",
                        source="https://h5p.org/true-false-question",
                    )
                    session.commit()
                except RegistrationRefused as refusal:
                    session.rollback()
                    print(f"  {code} : {refusal}", file=sys.stderr)
                    continue
                except Exception as error:  # pragma: no cover - operator feedback
                    session.rollback()
                    print(f"  {code} : {error}", file=sys.stderr)
                    continue
            try:
                runtime.deploy_package(root, archive, report.sha256)
            except (runtime.DeploymentRefused, OSError) as refusal:
                print(f"  {code} : déploiement impossible, {refusal}", file=sys.stderr)
                continue
            packaged.append(code)
    finally:
        engine.dispose()
    return packaged


async def _families(db: AsyncSession) -> list[SeededFamily]:
    built: list[SeededFamily] = []
    for family in dataset.FAMILIES:
        email = str(family["email"])
        parent = await db.scalar(select(Parent).where(Parent.email == email))
        if parent is None:
            parent = Parent(
                email=email,
                family_code=generate_family_code(),
                password_hash=hash_password(dataset.PASSWORD),
                display_name=str(family["display_name"]),
                is_active=True,
            )
            db.add(parent)
            await db.flush()

        children: list[SeededChild] = []
        for profile in family["children"]:
            pseudonym = str(profile["pseudonym"])
            child = await db.scalar(
                select(Child).where(
                    Child.parent_id == parent.id, Child.pseudonym == pseudonym
                )
            )
            if child is None:
                child = Child(
                    parent_id=parent.id,
                    pseudonym=pseudonym,
                    pin_hash=hash_pin(str(profile["pin"])),
                    display_name=str(profile["display_name"]),
                    status=CHILD_STATUS_ACTIVE,
                )
                db.add(child)
                await db.flush()
            children.append(SeededChild(child=child, pin=str(profile["pin"])))

        built.append(SeededFamily(parent=parent, children=children))
    return built


async def _history(families: list[SeededFamily]) -> None:
    """Play each child's past through the real services.

    Give, start, answer, finish — the same four acts a browser performs, and
    **each in its own session**, because that is also what a browser does. It is
    not a detail: an attempt loaded before its responses exist keeps an empty
    collection, and the reading at completion would then find nothing to read.
    One session for the whole past would produce a dataset with attempts and
    answers but no conclusions — which is exactly what it did before this was
    fixed.
    """
    for family in families:
        for entry in family.children:
            for past in dataset.HISTORY.get(entry.child.pseudonym, []):
                await _work_through(family.parent.id, entry.child.id, past)

            waiting = dataset.WAITING.get(entry.child.pseudonym)
            if waiting is not None:
                await _act(family.parent.id, entry.child.id, _give(waiting))


async def _work_through(
    parent_id: uuid.UUID, child_id: uuid.UUID, past: dataset.PastActivity
) -> None:
    """One activity, from given to finished, one session per act."""
    assignment_id = await _act(parent_id, child_id, _give(past["activity"]))
    if assignment_id is None:
        return

    async def start(db: AsyncSession, parent: Parent, child: Child) -> uuid.UUID:
        await assignments.start_assignment(db, child, assignment_id)
        attempt, _ = await attempts.start_or_resume(db, child, assignment_id)
        return attempt.id

    attempt_id = await _act(parent_id, child_id, start)
    if attempt_id is None:
        return

    for index, correct in enumerate(past["answers"], start=1):
        await _act(parent_id, child_id, _answer(attempt_id, index, correct))

    async def finish(db: AsyncSession, parent: Parent, child: Child) -> None:
        await attempts.complete(db, child, attempt_id)

    await _act(parent_id, child_id, finish)


def _give(activity_code: str) -> Act[uuid.UUID]:
    async def act(db: AsyncSession, parent: Parent, child: Child) -> uuid.UUID:
        assignment = await assignments.assign_activity(
            db, parent, child.id, activity_code
        )
        return assignment.id

    return act


def _answer(attempt_id: uuid.UUID, index: int, correct: bool) -> Act[None]:
    async def act(db: AsyncSession, parent: Parent, child: Child) -> None:
        await attempts.record_response(
            db,
            child,
            attempt_id,
            question_ref=f"q{index}",
            response="vrai" if correct else "faux",
            is_correct=correct,
        )

    return act


async def _act(parent_id: uuid.UUID, child_id: uuid.UUID, act: Act[T]) -> T | None:
    """Run one act in its own session, and swallow what the platform refuses.

    A refusal here means the dataset is already partly there — the same activity
    still owed, an attempt already running. Running the script twice must
    complete what is missing rather than fail on what exists.
    """
    async with AsyncSessionFactory() as db:
        parent = await db.get(Parent, parent_id)
        child = await db.get(Child, child_id)
        if parent is None or child is None:
            return None
        try:
            result = await act(db, parent, child)
            await db.commit()
            return result
        except ConflictException:
            await db.rollback()
            return None
        except NotFoundException as missing:
            await db.rollback()
            print(f"  {missing.message}", file=sys.stderr)
            return None


def _report(families: list[SeededFamily], packaged: list[str]) -> None:
    print()
    print("Jeu de données de démonstration prêt. Tout y est fictif.")
    print()
    print(f"Mot de passe des comptes Parent : {dataset.PASSWORD}")
    print()
    for family in families:
        print(f"  {family.parent.display_name}")
        print(f"    e-mail        : {family.parent.email}")
        print(f"    code famille  : {family.parent.family_code}")
        for entry in family.children:
            print(
                f"    enfant        : {entry.child.display_name}"
                f"  pseudo « {entry.child.pseudonym} »  code secret {entry.pin}"
            )
        print()

    if packaged:
        print("Activités réellement jouables :")
        for code in packaged:
            print(f"    {code}")
    else:
        print(
            "Aucune activité jouable : le stockage ou le volume de contenu n’a pas "
            "répondu. Les tableaux de bord fonctionnent quand même."
        )
    print()
    print("Pour retirer ces données : python -m app.demo --clean")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
