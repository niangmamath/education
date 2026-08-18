"""What the demonstration contains, and why each piece of it is there.

Every value here is fictional, as the project's decisions require, and every
name is obviously so. Addresses belong to `example.com`, reserved by RFC 2606.

**The competencies are not invented.** They follow the structure of the French
national *Repères* assessments taken at the start of CP and CE1: for French,
letters and their sounds, syllables, phonemes, then reading and writing words;
for mathematics, counting a collection, reading and comparing numbers, then
adding, subtracting and solving a one-step problem. Borrowing that structure
costs nothing and means nobody has to defend a carving of the subject we made up.

The prerequisites cross the two levels on purpose. A CE1 child who fails at
adding is sent back to counting, which is CP — and that is the platform's most
useful behaviour, not an edge case.

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
from app.demo.referentiel import CE1, CI_MA_DENOMBRER, CM1
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

# The twelve repairs live in `app.demo.fiches`: they are sheets written here,
# with a lesson and four questions each, and they were long enough to deserve
# their own module.
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
    """L'édition à importer : six classes, deux matières, trente-six compétences."""
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
            {"pseudonym": "lea", "display_name": "Léa", "pin": "240613", "level": CE1},
            {"pseudonym": "tom", "display_name": "Tom", "pin": "731502", "level": CE1},
        ],
    },
    {
        "email": f"{PREFIX}parent.diallo@example.com",
        "display_name": "Awa Diallo",
        "children": [
            # En CM1, pour que la démonstration montre deux classes et non une.
            {"pseudonym": "noa", "display_name": "Noa", "pin": "518274", "level": CM1},
        ],
    },
]

# Comment chaque enfant a répondu à l'examen de sa classe. Rien ici n'énonce un
# résultat : ce sont les règles de la plateforme qui transforment ces réponses en
# lecture, de sorte que la démonstration ne peut pas contredire le produit.
#
# Léa bute sur ce qui dépend de l'écrit et sur la soustraction — la chaîne que
# l'arbre décrit, et qui redescend jusqu'au CP puis au CI. Tom réussit partout,
# parce qu'une démonstration où tous les enfants sont en difficulté enseigne le
# contraire de ce que fait le produit. Noa est absente de cette table exprès :
# son examen de CM1 l'attend, non passé.
ASSESSMENT_ANSWERS: Final[dict[str, dict[str, bool]]] = {
    "lea": {
        "ce1-q1": True,
        "ce1-q2": False,
        "ce1-q3": False,
        "ce1-q4": True,
        "ce1-q5": False,
        "ce1-q6": False,
    },
    "tom": {question["ref"]: True for question in EXAMS_BY_LEVEL[CE1]["questions"]},
}
