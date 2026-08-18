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
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, TypeVar

from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.assessment import service as assessment
from app.authored import service as authored
from app.assignments import service as assignments
from app.attempts import service as attempts
from app.catalog.registration import RegistrationRefused, register_package
from app.catalog.storage import S3ObjectStore
from app.content import deploy as runtime
from app.core.config import settings
from app.core.db import AsyncSessionFactory, sync_database_url
from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import generate_family_code, hash_password, hash_pin
from app.demo import dataset, examens, fiches, referentiel
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_KIND_H5P,
    ACTIVITY_KIND_REMEDIATION,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    ActivityQuestion,
    AuthoredQuestion,
)
from app.models.identity import (
    CHILD_STATUS_ACTIVE,
    Child,
    ChildPromotion,
    Parent,
)
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
        "--contenus",
        action="store_true",
        help="n’installer que le référentiel, les activités et l’examen, sans comptes",
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
        asyncio.run(build(arguments.spike, families=not arguments.contenus))
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


async def build(spike: Path, families: bool = True) -> None:
    """Install the content, and the demonstration families unless told otherwise.

    `--contenus` exists for the case where the accounts are to be created by
    hand: the referential, the activities and the initiation assessment are what
    a real account needs to have anything to do, and seeding families alongside
    would put fictional children next to real ones.
    """
    _referential()
    _fiches()
    _examens()
    packaged = _packages(spike)

    if not families:
        _content_report(packaged)
        return

    async with AsyncSessionFactory() as db:
        seeded = await _families(db)
        await db.commit()
        for family in seeded:
            for entry in family.children:
                await db.refresh(entry.child)
            await db.refresh(family.parent)

    await _history(seeded)
    _report(seeded, packaged)


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


def _install_authored(
    session: Session,
    activity: Activity,
    questions: Sequence[Mapping[str, Any]],
) -> None:
    """Write an authored activity's questions, wording and attribution together.

    Two tables, and the split is deliberate. `authored_questions` holds what is
    asked; `catalog_activity_questions` holds which competency each question
    works on. The second already existed and is what the results engine reads —
    it must go on reading one table whether an activity was imported or written
    here, and never learn the difference.

    The competency is also declared on the activity itself, or a reading would
    find a question attributed to something the activity does not claim to work
    on.
    """
    existing = {
        row.question_ref
        for row in session.scalars(
            select(AuthoredQuestion).where(AuthoredQuestion.activity_id == activity.id)
        )
    }
    claimed = {
        row.competency_code
        for row in session.scalars(
            select(ActivityCompetency).where(
                ActivityCompetency.activity_id == activity.id
            )
        )
    }

    for position, question in enumerate(questions, start=1):
        ref = str(question["ref"])
        competency = str(question["competency"])
        if competency not in claimed:
            session.add(
                ActivityCompetency(activity_id=activity.id, competency_code=competency)
            )
            claimed.add(competency)
        if ref in existing:
            continue
        session.add(
            AuthoredQuestion(
                activity_id=activity.id,
                position=position,
                question_ref=ref,
                prompt=str(question["prompt"]),
                choices=question["choices"],
                correct_index=int(question["correct"]),  # type: ignore[call-overload]
                explanation=question.get("explanation"),
            )
        )
        session.add(
            ActivityQuestion(
                activity_id=activity.id,
                question_ref=ref,
                competency_code=competency,
            )
        )


def _fiches() -> None:
    """The twelve remediation sheets, and the one imported activity beside them.

    A sheet is a repair a child can actually do: a short lesson, four questions
    on one competency, and an explanation after each. Before this, the twelve
    repairs were catalogue rows with nothing behind them — the diagnostic could
    propose a repair that opened on an empty page.
    """
    engine = create_engine(sync_database_url())
    try:
        with Session(engine) as session:
            for sheet in fiches.FICHES:
                activity = session.scalar(
                    select(Activity).where(Activity.code == sheet["code"])
                )
                if activity is None:
                    activity = Activity(
                        code=sheet["code"],
                        title=sheet["title"],
                        kind=ACTIVITY_KIND_REMEDIATION,
                        status=ACTIVITY_STATUS_PUBLISHED,
                        duration_minutes=sheet["minutes"],
                        guidance=sheet["guidance"],
                    )
                    session.add(activity)
                    session.flush()

                _install_authored(
                    session,
                    activity,
                    [
                        {**question, "competency": sheet["competency"]}
                        for question in sheet["questions"]
                    ],
                )

            # The imported activity, kept apart from the repairs so that the
            # content runtime stays demonstrable without the parcours depending
            # on a package that cannot be deployed everywhere.
            if not session.scalar(
                select(Activity).where(Activity.code == dataset.H5P_DEMO_CODE)
            ):
                imported = Activity(
                    code=dataset.H5P_DEMO_CODE,
                    title=dataset.H5P_DEMO_TITLE,
                    kind=ACTIVITY_KIND_H5P,
                    status=ACTIVITY_STATUS_PUBLISHED,
                    duration_minutes=dataset.H5P_DEMO_MINUTES,
                )
                session.add(imported)
                session.flush()
                session.add(
                    ActivityCompetency(
                        activity_id=imported.id,
                        competency_code=dataset.H5P_DEMO_COMPETENCY,
                    )
                )
            session.commit()
    finally:
        engine.dispose()


def _examens() -> None:
    """Installer un examen d'entrée par classe, du CI au CM2.

    Six activités et non une : ce qu'on demande à un CI et ce qu'on demande à un
    CM2 n'ont rien de commun, et c'est la classe déclarée par l'élève qui décide
    de celui qu'il reçoit. `level_code` est ce qui les distingue — sans lui, la
    plateforme ne saurait pas lequel donner.

    Leurs questions ne portent aucune explication, et c'est une décision : dire
    la réponse à un enfant pendant qu'on le mesure abîme la mesure.
    """
    engine = create_engine(sync_database_url())
    try:
        with Session(engine) as session:
            for exam in examens.EXAMS:
                code = f"{dataset.PREFIX}examen-{exam['level']}"
                activity = session.scalar(select(Activity).where(Activity.code == code))
                if activity is None:
                    activity = Activity(
                        code=code,
                        title=exam["title"],
                        kind=ACTIVITY_KIND_ASSESSMENT,
                        status=ACTIVITY_STATUS_PUBLISHED,
                        duration_minutes=exam["minutes"],
                        level_code=exam["level"],
                    )
                    session.add(activity)
                    session.flush()

                _install_authored(session, activity, list(exam["questions"]))
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
                    level_code=str(profile["level"]),
                    status=CHILD_STATUS_ACTIVE,
                )
                db.add(child)
                await db.flush()
                db.add(
                    ChildPromotion(
                        child_id=child.id,
                        decided_by_parent_id=parent.id,
                        from_level_code=None,
                        to_level_code=str(profile["level"]),
                    )
                )
                await db.flush()
            # Activation is what gives the assessment, and these profiles are
            # created already active. Giving it here is what the activation route
            # would have done, not a shortcut around it.
            await assessment.give_to(db, parent.id, child)
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
            answers = dataset.ASSESSMENT_ANSWERS.get(entry.child.pseudonym)
            if answers is not None:
                await _take_assessment(family.parent.id, entry.child.id, answers)


async def _take_assessment(
    parent_id: uuid.UUID, child_id: uuid.UUID, answers: dict[str, bool]
) -> None:
    """Let a child sit her initiation assessment, one act per session.

    The assessment was given to her at activation, by the platform. From there
    it is an ordinary activity: started, answered, finished — and the reading
    that follows is produced by the rules, not written down beside them.

    The answer chosen is the correct one or the first wrong one, which is enough
    for a demonstration and keeps this file from restating what a right answer is.
    """
    assignment_id = await _act(parent_id, child_id, _pending_assessment())
    if assignment_id is None:
        return

    async def start(db: AsyncSession, parent: Parent, child: Child) -> uuid.UUID:
        await assignments.start_assignment(db, child, assignment_id)
        attempt, _ = await attempts.start_or_resume(db, child, assignment_id)
        return attempt.id

    attempt_id = await _act(parent_id, child_id, start)
    if attempt_id is None:
        return

    questions = [
        question
        for exam in examens.EXAMS
        for question in exam["questions"]
        if question["ref"] in answers
    ]
    for question in questions:
        wanted = answers.get(question["ref"])
        if wanted is None:
            continue
        chosen = question["correct"] if wanted else _first_wrong(question)
        await _act(parent_id, child_id, _answer(attempt_id, question["ref"], chosen))

    async def finish(db: AsyncSession, parent: Parent, child: Child) -> None:
        await attempts.complete(db, child, attempt_id)

    await _act(parent_id, child_id, finish)


def _first_wrong(question: examens.ExamQuestion) -> int:
    return next(
        index
        for index in range(len(question["choices"]))
        if index != question["correct"]
    )


def _pending_assessment() -> Act[uuid.UUID]:
    async def act(db: AsyncSession, parent: Parent, child: Child) -> uuid.UUID:
        pending = await assessment.pending_for(db, child.id)
        if pending is None:
            raise NotFoundException(message="aucun examen d’initiation en attente")
        return pending.id

    return act


def _answer(attempt_id: uuid.UUID, question_ref: str, chosen: int) -> Act[None]:
    async def act(db: AsyncSession, parent: Parent, child: Child) -> None:
        attempt = await attempts.own_attempt(db, child, attempt_id)
        answer, correct, _ = await authored.grade(db, attempt, question_ref, chosen)
        await attempts.record_response(
            db,
            child,
            attempt_id,
            question_ref=question_ref,
            response=answer,
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


def _content_report(packaged: list[str]) -> None:
    """What was installed when no account was."""
    print()
    print("Contenus installés. Aucun compte créé.")
    print()
    print(f"  Référentiel   : {dataset.EDITION_CODE}, en vigueur")
    print(f"  Compétences   : {len(referentiel.COMPETENCIES)}")
    print(f"  Examens       : {len(examens.EXAMS)}, un par classe")
    print(f"  Remédiations  : {len(fiches.FICHES)} fiches")
    if packaged:
        print(f"  Jouable       : {', '.join(packaged)}")
    else:
        print("  Jouable       : aucune ; le stockage ou le volume n’a pas répondu")
    print()
    print("Créez maintenant les comptes depuis l’interface : un profil enfant")
    print("activé reçoit l’examen d’initiation automatiquement.")


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
