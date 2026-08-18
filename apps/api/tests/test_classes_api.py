"""Les six classes, l'examen d'entrée qui va avec, et le passage.

Ce module éprouve ce qu'ADR-018 promet, et chaque classe de tests correspond à
une promesse qui pourrait se rompre sans que rien ne casse bruyamment.

**La classe décide de l'examen.** Un élève de CE1 ne doit pas recevoir l'examen
du CM2, et une plateforme qui se tromperait produirait une lecture d'apparence
normale sur des questions qu'il n'avait aucune raison de subir.

**Le passage monte le palier sans rien effacer.** C'est la promesse la plus facile
à trahir : il suffirait de supprimer des lignes pour « nettoyer », et le
diagnostic perdrait le moyen de remonter une lacune ancienne — ce qui est
précisément ce que ce produit sait faire.

Chaque adresse appartient à `example.com`, réservé par la RFC 2606, et tout ce
qui est créé ici porte un préfixe de test puis disparaît.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.db import sync_database_url
from app.main import app
from app.models.catalog import (
    ACTIVITY_KIND_ASSESSMENT,
    ACTIVITY_STATUS_PUBLISHED,
    Activity,
    ActivityCompetency,
    ActivityQuestion,
    AuthoredQuestion,
)
from app.referential.document import ReferentialDocument
from app.referential.importer import reconcile
from app.referential.publication import publish
from tests.support import no_edition_in_force

TEST_CODE_PREFIX = "test-classe-"
PASSWORD = "correct-horse-battery"
PIN = "428173"

CLASSES_URL = "/api/v1/auth/classes"
CHILDREN_URL = "/api/v1/auth/children"
ASSESSMENT_URL = "/api/v1/me/assessment"


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url())
    yield engine
    engine.dispose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


LEVELS: list[tuple[str, str]] = [
    ("ci", "Cours d’initiation"),
    ("cp", "Cours préparatoire"),
    ("ce1", "Cours élémentaire première année"),
    ("ce2", "Cours élémentaire deuxième année"),
    ("cm1", "Cours moyen première année"),
    ("cm2", "Cours moyen deuxième année"),
]


def document(code: str) -> dict[str, Any]:
    """Une édition à six classes, publiée par ce module et retirée après lui."""
    return {
        "version": {"code": code, "label": "Édition des classes"},
        "levels": [
            {"code": level, "label": label, "position": position}
            for position, (level, label) in enumerate(LEVELS, start=1)
        ],
        "subjects": [
            {
                "code": "ma",
                "label": "Mathématiques",
                "position": 1,
                "domains": [{"code": "ma-nombres", "label": "Nombres", "position": 1}],
            }
        ],
        "competencies": [
            {
                "code": f"{level}-ma-compter",
                "label": f"Compter en {level.upper()}",
                "description": None,
                "position": 1,
                "level": level,
                "domain": "ma-nombres",
                "prerequisites": [],
            }
            for level, _ in LEVELS
        ],
    }


@pytest.fixture
def edition(engine: Engine) -> Iterator[str]:
    """Publier une édition à six classes, et rendre la place ensuite.

    Ce module publie la sienne plutôt que d'emprunter celle qui traîne, et c'est
    une leçon payée : une première version lisait l'édition en vigueur et se
    sautait quand elle n'en trouvait pas assez. Un test qui se saute n'est pas un
    test — sur une base neuve, comme en intégration continue, il n'aurait jamais
    rien éprouvé du tout.
    """
    code = f"{TEST_CODE_PREFIX}{uuid.uuid4().hex[:8]}"
    with no_edition_in_force(engine, TEST_CODE_PREFIX):
        with Session(engine) as session:
            reconcile(session, ReferentialDocument.model_validate(document(code)))
            publish(session, code)
            session.commit()
        yield code


@pytest.fixture
def classes(client: TestClient, edition: str) -> list[dict[str, str]]:
    """Les classes de l'édition que ce module vient de publier."""
    response = client.get(CLASSES_URL)
    assert response.status_code == 200, response.text
    rows = list(response.json())
    assert len(rows) == len(LEVELS)
    return rows


@pytest.fixture
def exams(engine: Engine, classes: list[dict[str, str]]) -> Iterator[dict[str, str]]:
    """Un examen par classe, chacun avec une question qui lui est propre.

    Créés par ce module plutôt qu'empruntés au jeu de démonstration : un test qui
    dépend de ce qui traîne en base passe ou échoue selon la machine, et cette
    famille de défaut a déjà coûté assez cher au projet.
    """
    codes = {
        row["code"]: f"{TEST_CODE_PREFIX}{row['code']}-{uuid.uuid4().hex[:8]}"
        for row in classes
    }
    competency = f"test-comp-{uuid.uuid4().hex[:8]}"

    with Session(engine) as session:
        for level, code in codes.items():
            activity = Activity(
                code=code,
                title="Pour faire connaissance",
                kind=ACTIVITY_KIND_ASSESSMENT,
                status=ACTIVITY_STATUS_PUBLISHED,
                duration_minutes=5,
                level_code=level,
            )
            session.add(activity)
            session.flush()
            session.add(
                ActivityCompetency(activity_id=activity.id, competency_code=competency)
            )
            session.add(
                AuthoredQuestion(
                    activity_id=activity.id,
                    position=1,
                    question_ref=f"q-{level}",
                    prompt=f"Question de {level} ?",
                    choices=["A", "B", "C"],
                    correct_index=1,
                )
            )
            session.add(
                ActivityQuestion(
                    activity_id=activity.id,
                    question_ref=f"q-{level}",
                    competency_code=competency,
                )
            )
        session.commit()

    yield codes

    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM assignments WHERE activity_id IN "
                "(SELECT id FROM catalog_activities WHERE code LIKE :p)"
            ),
            {"p": f"{TEST_CODE_PREFIX}%"},
        )
        connection.execute(
            text("DELETE FROM catalog_activities WHERE code LIKE :p"),
            {"p": f"{TEST_CODE_PREFIX}%"},
        )


class Family:
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.email = f"classe-{uuid.uuid4().hex}@example.com"
        created = client.post(
            "/api/v1/auth/parent/register",
            json={
                "email": self.email,
                "password": PASSWORD,
                "display_name": "Parent Classe",
            },
        )
        assert created.status_code == 201, created.text
        self.family_code = created.json()["family_code"]
        self.as_parent()

    def as_parent(self) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/parent/login",
                json={"email": self.email, "password": PASSWORD},
            ).status_code
            == 200
        )
        return self.client

    def add_child(self, level_code: str) -> dict[str, Any]:
        pseudonym = f"lea{uuid.uuid4().hex[:6]}"
        created = self.as_parent().post(
            CHILDREN_URL,
            json={
                "pseudonym": pseudonym,
                "pin": PIN,
                "display_name": "Léa",
                "level_code": level_code,
            },
        )
        assert created.status_code == 201, created.text
        row = dict(created.json())
        row["pseudonym"] = pseudonym
        return row

    def as_child(self, pseudonym: str) -> TestClient:
        assert (
            self.client.post(
                "/api/v1/auth/child/login",
                json={
                    "family_code": self.family_code,
                    "pseudonym": pseudonym,
                    "pin": PIN,
                },
            ).status_code
            == 200
        )
        return self.client


@pytest.fixture
def family(client: TestClient, exams: dict[str, str]) -> Family:
    """La famille vient **après** les examens, et l'ordre compte.

    Créer un profil utilisable est ce qui lui donne son examen : un enfant créé
    avant ceux de ce module recevrait celui du jeu de démonstration, et le test
    mesurerait autre chose que ce qu'il croit.
    """
    return Family(client)


class TestLesClassesSontServies:
    def test_elles_sont_lisibles_sans_session(
        self, client: TestClient, classes: list[dict[str, str]]
    ) -> None:
        """La seule route de cette famille qui n'exige pas de session.

        Le formulaire d'inscription en a besoin **avant** qu'un compte existe :
        on ne demande pas sa classe à quelqu'un sans lui montrer les classes
        possibles. Ce qu'elle divulgue est le découpage scolaire d'un pays, qui
        est public, et rien d'aucune famille.
        """
        assert client.get(CLASSES_URL).status_code == 200

    def test_l_ordre_servi_est_celui_du_passage(
        self, family: Family, classes: list[dict[str, str]]
    ) -> None:
        """L'ordre de la liste n'est pas décoratif : c'est celui des passages.

        Un ordre alphabétique mettrait le CE1 avant le CI et le CM2 avant le CP.
        Le vérifier en faisant passer un élève est la seule façon d'éprouver que
        la liste servie au parent et la suite des classes sont bien la même
        chose, plutôt que deux ordres qui se ressemblent par chance.
        """
        child = family.add_child(classes[0]["code"])

        promoted = family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        assert promoted.status_code == 200, promoted.text
        assert promoted.json()["level_code"] == classes[1]["code"]

    def test_chacune_porte_un_nom_lisible(self, classes: list[dict[str, str]]) -> None:
        """Un parent ne lit pas « ce1 », et un code affiché tel quel est une
        fuite d'implémentation."""
        for row in classes:
            assert row["label"] and row["label"] != row["code"]


class TestLaClasseDecideDeLExamen:
    def test_un_eleve_recoit_l_examen_de_sa_classe(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        child = family.add_child(classes[1]["code"])

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()

        assert body["assignment_id"] is not None
        assert [q["question_ref"] for q in body["questions"]] == [
            f"q-{classes[1]['code']}"
        ]

    def test_deux_classes_recoivent_deux_examens_differents(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        """La promesse la plus simple, et celle qu'un défaut rendrait invisible :
        un examen unique produirait des lectures d'apparence normale sur des
        questions que l'élève n'avait aucune raison de subir."""
        petit = family.add_child(classes[0]["code"])
        grand = family.add_child(classes[-1]["code"])

        premier = family.as_child(petit["pseudonym"]).get(ASSESSMENT_URL).json()
        second = family.as_child(grand["pseudonym"]).get(ASSESSMENT_URL).json()

        assert premier["questions"][0]["question_ref"] == f"q-{classes[0]['code']}"
        assert second["questions"][0]["question_ref"] == f"q-{classes[-1]['code']}"

    def test_une_classe_absente_du_programme_est_refusee(
        self, family: Family, exams: dict[str, str]
    ) -> None:
        """Un profil portant « ce7 » ne recevrait aucun examen et personne ne
        saurait pourquoi."""
        refused = family.as_parent().post(
            CHILDREN_URL,
            json={
                "pseudonym": f"lea{uuid.uuid4().hex[:6]}",
                "pin": PIN,
                "display_name": "Léa",
                "level_code": "classe-qui-n-existe-pas",
            },
        )

        assert refused.status_code == 409

    def test_une_inscription_sans_classe_est_refusee(
        self, family: Family, exams: dict[str, str]
    ) -> None:
        """Il n'y a pas de classe par défaut qu'on pourrait supposer sans se
        tromper sur un enfant réel."""
        refused = family.as_parent().post(
            CHILDREN_URL,
            json={
                "pseudonym": f"lea{uuid.uuid4().hex[:6]}",
                "pin": PIN,
                "display_name": "Léa",
            },
        )

        assert refused.status_code == 422


class TestLePassageEnClasseSuperieure:
    def test_il_monte_l_eleve_d_une_classe(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        child = family.add_child(classes[1]["code"])

        promoted = family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        assert promoted.status_code == 200, promoted.text
        assert promoted.json()["level_code"] == classes[2]["code"]

    def test_il_donne_l_examen_de_la_nouvelle_classe(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        """Sans lui, la plateforme ne sait rien de l'année qui commence."""
        child = family.add_child(classes[1]["code"])
        family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()

        assert [q["question_ref"] for q in body["questions"]] == [
            f"q-{classes[2]['code']}"
        ]

    def test_il_n_efface_rien(
        self,
        family: Family,
        exams: dict[str, str],
        classes: list[dict[str, str]],
        engine: Engine,
    ) -> None:
        """La promesse la plus facile à trahir.

        Il suffirait de supprimer des lignes pour « nettoyer », et le diagnostic
        perdrait le moyen de remonter une lacune ancienne — ce qui est
        précisément ce que ce produit sait faire de mieux.
        """
        child = family.add_child(classes[1]["code"])
        family.as_child(child["pseudonym"])
        before = family.as_parent().get(CHILDREN_URL).json()

        family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        with engine.begin() as connection:
            assignments = connection.execute(
                text("SELECT count(*) FROM assignments WHERE child_id = :c"),
                {"c": child["id"]},
            ).scalar()
        # L'examen de CE1 est toujours là, et celui de CE2 s'y ajoute.
        assert assignments == 2
        assert len(before) == 1

    def test_le_cm2_n_a_pas_de_classe_suivante(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        """La suite est le collège, que cette plateforme ne couvre pas et sur
        lequel elle ne prétend rien."""
        child = family.add_child(classes[-1]["code"])

        refused = family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        assert refused.status_code == 409

    def test_chaque_passage_laisse_une_ligne_datee(
        self,
        family: Family,
        exams: dict[str, str],
        classes: list[dict[str, str]],
        engine: Engine,
    ) -> None:
        """Le dossier suit l'élève toute sa scolarité : savoir qu'une lacune a
        été observée alors qu'il était en CE1 n'a pas le même poids qu'une lacune
        observée trois ans plus tard."""
        child = family.add_child(classes[0]["code"])
        family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")
        family.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        with engine.begin() as connection:
            rows = connection.execute(
                text(
                    "SELECT from_level_code, to_level_code FROM auth_child_promotions "
                    "WHERE child_id = :c ORDER BY decided_at, to_level_code"
                ),
                {"c": child["id"]},
            ).all()

        # L'inscription elle-même en est la première ligne, sans classe d'avant.
        assert [(row[0], row[1]) for row in rows] == [
            (None, classes[0]["code"]),
            (classes[0]["code"], classes[1]["code"]),
            (classes[1]["code"], classes[2]["code"]),
        ]

    def test_un_parent_ne_fait_pas_passer_l_enfant_d_une_autre_famille(
        self, client: TestClient, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        theirs = Family(client)
        child = theirs.add_child(classes[1]["code"])
        ours = Family(client)

        refused = ours.as_parent().post(f"{CHILDREN_URL}/{child['id']}/promotion")

        assert refused.status_code == 404

    def test_un_enfant_ne_se_fait_pas_passer_lui_meme(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        """Le passage est un fait de la scolarité, décidé par un adulte."""
        child = family.add_child(classes[1]["code"])

        refused = family.as_child(child["pseudonym"]).post(
            f"{CHILDREN_URL}/{child['id']}/promotion"
        )

        assert refused.status_code in (401, 403)


class TestDeclarerOuCorrigerLaClasse:
    def test_un_parent_corrige_une_classe_saisie_de_travers(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        child = family.add_child(classes[-1]["code"])

        corrected = family.as_parent().put(
            f"{CHILDREN_URL}/{child['id']}/level",
            json={"level_code": classes[1]["code"]},
        )

        assert corrected.status_code == 200, corrected.text
        assert corrected.json()["level_code"] == classes[1]["code"]

    def test_la_correction_donne_l_examen_de_la_bonne_classe(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        child = family.add_child(classes[-1]["code"])
        family.as_parent().put(
            f"{CHILDREN_URL}/{child['id']}/level",
            json={"level_code": classes[1]["code"]},
        )

        body = family.as_child(child["pseudonym"]).get(ASSESSMENT_URL).json()

        assert {q["question_ref"] for q in body["questions"]} == {
            f"q-{classes[1]['code']}"
        }

    def test_une_classe_inconnue_est_refusee_aussi_a_la_correction(
        self, family: Family, exams: dict[str, str], classes: list[dict[str, str]]
    ) -> None:
        child = family.add_child(classes[1]["code"])

        refused = family.as_parent().put(
            f"{CHILDREN_URL}/{child['id']}/level",
            json={"level_code": "classe-qui-n-existe-pas"},
        )

        assert refused.status_code == 409

    def test_declarer_la_meme_classe_ne_fait_rien(
        self,
        family: Family,
        exams: dict[str, str],
        classes: list[dict[str, str]],
        engine: Engine,
    ) -> None:
        """Un enregistrement sans changement n'est pas un fait de scolarité, et
        l'historique ne doit pas se remplir de lignes qui ne disent rien."""
        child = family.add_child(classes[1]["code"])

        family.as_parent().put(
            f"{CHILDREN_URL}/{child['id']}/level",
            json={"level_code": classes[1]["code"]},
        )

        with engine.begin() as connection:
            rows = connection.execute(
                text("SELECT count(*) FROM auth_child_promotions WHERE child_id = :c"),
                {"c": child["id"]},
            ).scalar()

        assert rows == 1
