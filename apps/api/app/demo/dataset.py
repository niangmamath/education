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

from typing import Any, Final, TypedDict


class ChildProfile(TypedDict):
    pseudonym: str
    display_name: str
    pin: str


class FamilyProfile(TypedDict):
    email: str
    display_name: str
    children: list[ChildProfile]


class ExamQuestion(TypedDict):
    """One question of the initiation assessment."""

    ref: str
    competency: str
    prompt: str
    choices: list[str]
    correct: int


# Everything the demonstration creates carries this prefix, so `--reset` can
# take back exactly what it put in and nothing else. Competency codes do not
# need it: they live inside the edition, and go when it goes.
PREFIX: Final = "demo-"

EDITION_CODE: Final = f"{PREFIX}2026"

FR_LETTRES: Final = "cp-fr-lettres"
FR_SYLLABES: Final = "cp-fr-syllabes"
FR_PHONEMES: Final = "cp-fr-phonemes"
FR_MOTS: Final = "ce1-fr-mots"
FR_DICTEE: Final = "ce1-fr-dictee"
FR_COMPREHENSION: Final = "ce1-fr-comprehension"

MA_DENOMBRER: Final = "cp-ma-denombrer"
MA_LIRE: Final = "cp-ma-lire-nombres"
MA_COMPARER: Final = "cp-ma-comparer"
MA_ADDITION: Final = "ce1-ma-addition"
MA_SOUSTRACTION: Final = "ce1-ma-soustraction"
MA_PROBLEME: Final = "ce1-ma-probleme"


def _c(
    code: str,
    label: str,
    domain: str,
    level: str,
    position: int,
    prerequisites: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "label": label,
        "description": None,
        "position": position,
        "level": level,
        "domain": domain,
        "prerequisites": prerequisites or [],
    }


def referential() -> dict[str, Any]:
    """Twelve competencies, two subjects, two levels, and a real tree.

    The prerequisites are the pedagogical claim of the whole dataset: adding
    requires comparing, which requires reading numbers, which requires counting.
    A child who fails at additions is sent back along that chain rather than made
    to drill additions.
    """
    return {
        "version": {"code": EDITION_CODE, "label": "Repères CP et CE1, démonstration"},
        "levels": [
            {"code": "cp", "label": "Cours préparatoire", "position": 1},
            {"code": "ce1", "label": "Cours élémentaire première année", "position": 2},
        ],
        "subjects": [
            {
                "code": "fr",
                "label": "Français",
                "position": 1,
                "domains": [
                    {"code": "fr-code", "label": "Étude de la langue", "position": 1},
                    {"code": "fr-lire", "label": "Lire et écrire", "position": 2},
                ],
            },
            {
                "code": "ma",
                "label": "Mathématiques",
                "position": 2,
                "domains": [
                    {"code": "ma-nombres", "label": "Nombres", "position": 1},
                    {
                        "code": "ma-calcul",
                        "label": "Calcul et problèmes",
                        "position": 2,
                    },
                ],
            },
        ],
        "competencies": [
            _c(FR_LETTRES, "Reconnaître les lettres et leur son", "fr-code", "cp", 1),
            _c(FR_SYLLABES, "Manipuler les syllabes", "fr-code", "cp", 2, [FR_LETTRES]),
            _c(
                FR_PHONEMES,
                "Manipuler les phonèmes",
                "fr-code",
                "cp",
                3,
                [FR_SYLLABES],
            ),
            _c(FR_MOTS, "Lire des mots simples", "fr-lire", "ce1", 1, [FR_PHONEMES]),
            _c(FR_DICTEE, "Écrire des mots dictés", "fr-lire", "ce1", 2, [FR_MOTS]),
            _c(
                FR_COMPREHENSION,
                "Comprendre un texte lu seul",
                "fr-lire",
                "ce1",
                3,
                [FR_MOTS],
            ),
            _c(MA_DENOMBRER, "Dénombrer une collection", "ma-nombres", "cp", 1),
            _c(
                MA_LIRE,
                "Lire et écrire les nombres jusqu’à 10",
                "ma-nombres",
                "cp",
                2,
                [MA_DENOMBRER],
            ),
            _c(
                MA_COMPARER,
                "Comparer et ranger des nombres",
                "ma-nombres",
                "cp",
                3,
                [MA_LIRE],
            ),
            _c(
                MA_ADDITION,
                "Additionner jusqu’à 20",
                "ma-calcul",
                "ce1",
                1,
                [MA_COMPARER],
            ),
            _c(
                MA_SOUSTRACTION,
                "Soustraire jusqu’à 20",
                "ma-calcul",
                "ce1",
                2,
                [MA_ADDITION],
            ),
            _c(
                MA_PROBLEME,
                "Résoudre un problème à une étape",
                "ma-calcul",
                "ce1",
                3,
                [MA_ADDITION],
            ),
        ],
    }


# The initiation assessment: one question per competency, and the correct answer
# never leaves the server. No timer and no score shown — the point is to find a
# starting place, not to rank a six-year-old.
#
# **An item must not contain its own answer.** The first draft failed this badly:
# "quelle lettre fait le son « mmm » ?" spelled the answer three times in the
# prompt, "dans quel mot entends-tu le son « ou » ?" listed *loup* with the
# letters visible, and the spelling question quoted the word already spelled
# correctly. Those measured nothing but the ability to copy — worse than no
# question, because the reading they produce looks real.
#
# **What this assessment cannot do without audio**, and does not pretend to: hear
# a sound. Phonological items are approximated by asking about the beginning of a
# written word, which is a compromise and is written down as one. Real audio is
# the first thing to add if the assessment is ever used outside a demonstration.
ASSESSMENT_CODE: Final = f"{PREFIX}examen-initiation"
ASSESSMENT_TITLE: Final = "Pour faire connaissance"
ASSESSMENT_MINUTES: Final = 10

ASSESSMENT: Final[list[ExamQuestion]] = [
    {
        "ref": "q-fr-lettres",
        "competency": FR_LETTRES,
        "prompt": "Par quelle lettre commence le mot « bateau » ?",
        "choices": ["B", "D", "P"],
        "correct": 0,
    },
    {
        "ref": "q-fr-syllabes",
        "competency": FR_SYLLABES,
        "prompt": "Combien de syllabes y a-t-il dans le mot « papillon » ?",
        "choices": ["Deux", "Trois", "Quatre"],
        "correct": 1,
    },
    {
        "ref": "q-fr-phonemes",
        "competency": FR_PHONEMES,
        "prompt": "Quel mot commence par le même son que « souris » ?",
        "choices": ["Salade", "Chapeau", "Maison"],
        "correct": 0,
    },
    {
        "ref": "q-fr-mots",
        "competency": FR_MOTS,
        "prompt": "Quel mot est écrit correctement ?",
        "choices": ["chapo", "chapeau", "chapiau"],
        "correct": 1,
    },
    {
        "ref": "q-fr-dictee",
        "competency": FR_DICTEE,
        "prompt": "Quelle phrase est écrite correctement ?",
        "choices": [
            "Les enfant jouent dans la cour.",
            "Les enfants jouent dans la cour.",
            "Les enfants joue dans la cour.",
        ],
        "correct": 1,
    },
    {
        "ref": "q-fr-comprehension",
        "competency": FR_COMPREHENSION,
        "prompt": "« Tom prend son parapluie avant de sortir. » Quel temps fait-il ?",
        "choices": ["Il pleut", "Il fait très chaud", "Il neige"],
        "correct": 0,
    },
    {
        "ref": "q-ma-denombrer",
        "competency": MA_DENOMBRER,
        "prompt": "Combien y a-t-il d’étoiles ?  ★ ★ ★ ★ ★ ★ ★",
        "choices": ["Six", "Sept", "Huit"],
        "correct": 1,
    },
    {
        "ref": "q-ma-lire",
        "competency": MA_LIRE,
        "prompt": "Quel nombre s’écrit avec le chiffre 9 ?",
        "choices": ["Six", "Neuf", "Dix-neuf"],
        "correct": 1,
    },
    {
        "ref": "q-ma-comparer",
        "competency": MA_COMPARER,
        "prompt": "Quel nombre est le plus grand ?",
        "choices": ["8", "12", "10"],
        "correct": 1,
    },
    {
        "ref": "q-ma-addition",
        "competency": MA_ADDITION,
        "prompt": "Combien font 7 + 6 ?",
        "choices": ["12", "13", "14"],
        "correct": 1,
    },
    {
        "ref": "q-ma-soustraction",
        "competency": MA_SOUSTRACTION,
        "prompt": "Combien font 15 − 8 ?",
        "choices": ["6", "7", "8"],
        "correct": 1,
    },
    {
        "ref": "q-ma-probleme",
        "competency": MA_PROBLEME,
        "prompt": "Tom a 12 billes. Il en donne 4 à Léa. Combien lui en reste-t-il ?",
        "choices": ["6", "8", "16"],
        "correct": 1,
    },
]


# One repair per competency, so every difficulty the assessment can find has an
# answer. All within the three-to-seven minute band that makes a repair quick.
ACTIVITIES: Final[list[tuple[str, str, str, int]]] = [
    (f"{PREFIX}fix-fr-lettres", "L’alphabet et ses sons", FR_LETTRES, 5),
    (f"{PREFIX}fix-fr-syllabes", "Frapper les syllabes", FR_SYLLABES, 4),
    (f"{PREFIX}fix-fr-phonemes", "Chasse aux sons", FR_PHONEMES, 5),
    (f"{PREFIX}fix-fr-mots", "Lire des mots courts", FR_MOTS, 6),
    (f"{PREFIX}fix-fr-dictee", "Écrire des mots simples", FR_DICTEE, 6),
    (
        f"{PREFIX}fix-fr-comprehension",
        "Comprendre une petite histoire",
        FR_COMPREHENSION,
        7,
    ),
    (f"{PREFIX}fix-ma-denombrer", "Compter une collection", MA_DENOMBRER, 4),
    (f"{PREFIX}fix-ma-lire", "Écrire les nombres jusqu’à 10", MA_LIRE, 5),
    (f"{PREFIX}fix-ma-comparer", "Plus grand, plus petit", MA_COMPARER, 5),
    (f"{PREFIX}fix-ma-addition", "Additionner avec la bande numérique", MA_ADDITION, 6),
    (f"{PREFIX}fix-ma-soustraction", "Soustraire pas à pas", MA_SOUSTRACTION, 6),
    (f"{PREFIX}fix-ma-probleme", "Un problème, une étape", MA_PROBLEME, 7),
]

# Only one activity actually plays, and the platform is what decides that: a
# package belongs to one activity, and the pilot holds exactly one vetted
# package. Rather than work around that rule for a demonstration, the playable
# one is a repair the assessment is likely to propose.
PLAYABLE: Final = (f"{PREFIX}fix-ma-denombrer",)

PASSWORD: Final = "demonstration-2026"

# Two families, because isolation is a claim until somebody tries the other
# account. Noa has taken nothing: she shows what a brand new profile looks like —
# the assessment waiting, and nothing else.
FAMILIES: Final[list[FamilyProfile]] = [
    {
        "email": f"{PREFIX}parent.martin@example.com",
        "display_name": "Camille Martin",
        "children": [
            {"pseudonym": "lea", "display_name": "Léa", "pin": "240613"},
            {"pseudonym": "tom", "display_name": "Tom", "pin": "731502"},
        ],
    },
    {
        "email": f"{PREFIX}parent.diallo@example.com",
        "display_name": "Awa Diallo",
        "children": [
            {"pseudonym": "noa", "display_name": "Noa", "pin": "518274"},
        ],
    },
]

# How each child answered her initiation assessment. Nothing here states an
# outcome: the platform's rules turn these answers into a reading, so the
# demonstration cannot disagree with the product.
#
# Léa stumbles on counting and on everything built above it — the chain the tree
# describes. Tom is solid throughout, because a demonstration where every child
# is in difficulty teaches the wrong thing about the product. Noa is absent from
# this map on purpose: her assessment is waiting, untaken.
ASSESSMENT_ANSWERS: Final[dict[str, dict[str, bool]]] = {
    "lea": {
        "q-fr-lettres": True,
        "q-fr-syllabes": True,
        "q-fr-phonemes": False,
        "q-fr-mots": False,
        "q-fr-dictee": False,
        "q-fr-comprehension": True,
        "q-ma-denombrer": False,
        "q-ma-lire": True,
        "q-ma-comparer": False,
        "q-ma-addition": False,
        "q-ma-soustraction": False,
        "q-ma-probleme": True,
    },
    "tom": {question["ref"]: True for question in ASSESSMENT},
}
