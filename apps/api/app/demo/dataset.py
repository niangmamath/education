"""What the demonstration contains, and why each piece of it is there.

Every value here is fictional, as the project's decisions require, and every
name is obviously so. Addresses belong to `example.com`, reserved by RFC 2606.

**The competencies are not invented.** They follow the structure of the French
national *Repères* assessments taken at the start of CP and CE1: for French,
letters and their sounds, syllables, phonemes, then reading and writing words;
for mathematics, counting a collection, reading and comparing numbers, then
adding, subtracting and solving a one-step problem. Borrowing that structure
costs nothing and means nobody has to defend a carving of the subject we made up.

The prerequisites cross levels on purpose. A CP child who fails at ranging
numbers can be sent back to comparing them at CI — a level her own exam never
touches, since an exam only ever covers the class declared — and that is the
platform's most useful behaviour, not an edge case.

The dataset is arranged so a demonstration walks through the least obvious
behaviours without anybody setting them up:

1. **A new child starts full, not empty.** She is given the initiation
   assessment at activation, and has readings from the moment she takes it.
2. **A prerequisite is worked before what depends on it.**
3. **A gap is a candidate**, carrying the rule and the counts it came from.
4. **One family cannot see another.**
"""

from __future__ import annotations

from typing import Final, TypedDict

from app.demo.examens import EXAMS_BY_LEVEL
from app.demo.referentiel import (
    CI,
    CI_MA_DENOMBRER,
    CP,
    CP_FR_MOTS,
    CP_MA_ADDITION,
    CP_MA_RANGER,
)
from app.demo.referentiel import referential as _referential


class ChildProfile(TypedDict):
    pseudonym: str
    display_name: str
    pin: str
    # La classe déclarée à l'inscription : c'est elle qui décide de l'examen.
    level: str


class FamilyProfile(TypedDict):
    email: str
    display_name: str
    children: list[ChildProfile]


# Everything the demonstration creates carries this prefix, so `--reset` can
# take back exactly what it put in and nothing else. Competency codes do not
# need it: they live inside the edition, and go when it goes.
PREFIX: Final = "demo-"

EDITION_CODE: Final = f"{PREFIX}2026"

# The fifteen repairs live in `app.demo.fiches`: they are sheets written here,
# with a lesson and a reserve of eight questions each (four drawn per attempt,
# HORS-10), and they were long enough to deserve their own module.
#
# What stays here is the one imported activity. The pilot holds exactly one
# vetted H5P package, and ADR-012 allows exactly one library, so it cannot be
# spread over twelve repairs — but the content runtime is real work and has to
# stay demonstrable. It therefore gets an activity of its own, outside the
# repairs, and nothing in the parcours depends on it playing.
H5P_DEMO_CODE: Final = f"{PREFIX}h5p-vrai-faux"
H5P_DEMO_TITLE: Final = "Vrai ou faux : compter jusqu’à 20"
H5P_DEMO_COMPETENCY: Final = CI_MA_DENOMBRER
H5P_DEMO_MINUTES: Final = 4

PLAYABLE: Final = (H5P_DEMO_CODE,)

EDITION_LABEL: Final = "Élémentaire, six classes, démonstration"


def referential() -> dict[str, object]:
    """L'édition à importer : six classes, trois matières, cinquante-quatre
    compétences."""
    return _referential(EDITION_CODE, EDITION_LABEL)


PASSWORD: Final = "demonstration-2026"

# Two families, because isolation is a claim until somebody tries the other
# account. Noa has taken nothing: she shows what a brand new profile looks like —
# the assessment waiting, and nothing else.
FAMILIES: Final[list[FamilyProfile]] = [
    {
        "email": f"{PREFIX}parent.martin@example.com",
        "display_name": "Camille Martin",
        "children": [
            {"pseudonym": "lea", "display_name": "Léa", "pin": "240613", "level": CP},
            {"pseudonym": "tom", "display_name": "Tom", "pin": "731502", "level": CP},
        ],
    },
    {
        "email": f"{PREFIX}parent.diallo@example.com",
        "display_name": "Awa Diallo",
        "children": [
            # En CI, pour que la démonstration montre les deux classes
            # retenues pour l'instant, CI et CP, plutôt qu'une seule.
            {"pseudonym": "noa", "display_name": "Noa", "pin": "518274", "level": CI},
        ],
    },
]

# Léa échoue trois compétences de CP : lire des mots simples, et la chaîne
# ranger puis additionner. `cp-ma-addition` dépend de `cp-ma-ranger`, qui
# dépend à son tour de `ci-ma-comparer` — un niveau que l'examen de Léa ne
# couvre jamais, puisqu'un examen ne porte que sur la classe déclarée. C'est
# la chaîne que l'arbre décrit, jusqu'à un prérequis jamais observé. Tom
# réussit partout, parce qu'une démonstration où tous les enfants sont en
# difficulté enseigne le contraire de ce que fait le produit. Noa est absente
# de cette table exprès : son examen de CI l'attend, non passé.
_CP_QUESTIONS: Final = EXAMS_BY_LEVEL[CP]["questions"]
_LEA_FAILS: Final = {CP_FR_MOTS, CP_MA_RANGER, CP_MA_ADDITION}

# Comment chaque enfant a répondu à l'examen de sa classe. Rien ici n'énonce un
# résultat : ce sont les règles de la plateforme qui transforment ces réponses en
# lecture, de sorte que la démonstration ne puisse pas contredire le produit.
ASSESSMENT_ANSWERS: Final[dict[str, dict[str, bool]]] = {
    "lea": {
        question["ref"]: question["competency"] not in _LEA_FAILS
        for question in _CP_QUESTIONS
    },
    "tom": {question["ref"]: True for question in _CP_QUESTIONS},
}
