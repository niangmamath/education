"""What the demonstration contains, and why each piece of it is there.

Every value here is fictional, as the project's decisions require, and every
name is obviously so. Addresses belong to `example.com`, reserved by RFC 2606.

The dataset is not a random filling of tables. It is arranged so that a
five-minute demonstration walks through the platform's three least obvious
behaviours without anybody having to set them up by hand:

1. **A prerequisite is worked before what depends on it.** Léa fails at counting
   *and* at adding, and adding requires counting. The platform therefore
   proposes only counting, and shows adding as deferred with the reason. Saying
   "she is behind on additions" would be the ordinary answer and the wrong one.
2. **A gap is a candidate, not a verdict.** Every conclusion on screen carries
   the rule that produced it and the counts it was read from.
3. **One family cannot see another.** A second family exists for exactly that:
   signing in as the other parent shows nothing of the first.

Tom is here for contrast: everything he has done went well, so his dashboard is
what a calm one looks like. A demonstration where every child is in difficulty
teaches the wrong thing about the product.
"""

from __future__ import annotations

from typing import Any, Final, TypedDict


class PastActivity(TypedDict):
    """One activity a demonstration child has already worked through."""

    activity: str
    answers: list[bool]


class ChildProfile(TypedDict):
    pseudonym: str
    display_name: str
    pin: str


class FamilyProfile(TypedDict):
    email: str
    display_name: str
    children: list[ChildProfile]


# Everything the demonstration creates carries this prefix, so `--reset` can
# take back exactly what it put in and nothing else.
PREFIX: Final = "demo-"

EDITION_CODE: Final = f"{PREFIX}2026"

COMP_COUNT: Final = f"{PREFIX}num-compter"
COMP_ADD: Final = f"{PREFIX}num-additionner"
COMP_COMPARE: Final = f"{PREFIX}num-comparer"
COMP_SYLLABLES: Final = f"{PREFIX}lec-syllabes"
COMP_WORDS: Final = f"{PREFIX}lec-mots"


def referential() -> dict[str, Any]:
    """One edition, two subjects, and a prerequisite that carries the demo.

    `additionner` and `comparer` both require `compter`. That single edge is
    what makes the deferral visible, and it is also true of the subject: a child
    who cannot count to twenty cannot be helped by drilling additions.
    """
    return {
        "version": {"code": EDITION_CODE, "label": "Édition de démonstration"},
        "levels": [{"code": "cp", "label": "Cours préparatoire", "position": 1}],
        "subjects": [
            {
                "code": "math",
                "label": "Mathématiques",
                "position": 1,
                "domains": [
                    {"code": "math-num", "label": "Nombres et calcul", "position": 1}
                ],
            },
            {
                "code": "fr",
                "label": "Français",
                "position": 2,
                "domains": [{"code": "fr-lec", "label": "Lecture", "position": 1}],
            },
        ],
        "competencies": [
            _competency(COMP_COUNT, "Compter jusqu’à 20", position=1),
            _competency(
                COMP_ADD,
                "Additionner deux nombres jusqu’à 10",
                position=2,
                prerequisites=[COMP_COUNT],
            ),
            _competency(
                COMP_COMPARE,
                "Comparer deux nombres",
                position=3,
                prerequisites=[COMP_COUNT],
            ),
            _competency(
                COMP_SYLLABLES,
                "Reconnaître les syllabes d’un mot",
                position=1,
                domain="fr-lec",
            ),
            _competency(
                COMP_WORDS,
                "Lire des mots simples",
                position=2,
                domain="fr-lec",
                prerequisites=[COMP_SYLLABLES],
            ),
        ],
    }


def _competency(code: str, label: str, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "label": label,
        "description": None,
        "position": 1,
        "level": "cp",
        "domain": "math-num",
        "prerequisites": [],
    }
    payload.update(overrides)
    return payload


# Two lengths, and the difference is the product's. A Quick Repair lasts three
# to seven minutes; anything longer is never proposed as one, however well it
# matches. The long ones here are what reveals a difficulty, the short ones are
# what the platform offers to do about it.
ACTIVITIES: Final[list[tuple[str, str, str, int]]] = [
    # code, title, competency, minutes
    (f"{PREFIX}eval-compter", "Compter les objets d’une image", COMP_COUNT, 12),
    (f"{PREFIX}fix-compter", "Compter avec la bande numérique", COMP_COUNT, 5),
    (f"{PREFIX}eval-additionner", "Additions à trous", COMP_ADD, 12),
    (f"{PREFIX}fix-additionner", "Additionner avec ses doigts", COMP_ADD, 4),
    (f"{PREFIX}eval-syllabes", "Frapper les syllabes", COMP_SYLLABLES, 10),
    (f"{PREFIX}fix-syllabes", "Couper les mots en syllabes", COMP_SYLLABLES, 3),
    (f"{PREFIX}decouverte-lecture", "Reconnaître les lettres", COMP_WORDS, 6),
]

# Only one activity actually plays, and the platform is what decides that: a
# package belongs to one activity, and the pilot holds exactly one vetted
# package. Rather than work around that rule for a demonstration, the one
# playable activity is the one the demonstration ends on — the repair the
# platform proposes for Léa, which the parent gives and the child then does.
# The others furnish the lists, and the script says which is which rather than
# letting somebody find out by clicking.
PLAYABLE: Final = (f"{PREFIX}fix-compter",)

PASSWORD: Final = "demonstration-2026"

# Two families, because isolation is a claim until somebody tries the other
# account. Diallo has one child and no history: it is there to be signed into,
# not to be read.
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

# What each child has already done. `correct` says how the questions went; the
# platform's own rules turn that into a reading, so nothing here states an
# outcome directly — stating one would let the demonstration disagree with the
# product.
#
# Léa: counting and adding both went badly, syllables went well. Since adding
# requires counting, the platform proposes counting alone.
# Tom: everything went well, which is what a calm dashboard looks like.
HISTORY: Final[dict[str, list[PastActivity]]] = {
    "lea": [
        {"activity": f"{PREFIX}eval-compter", "answers": [False, False, True]},
        {"activity": f"{PREFIX}eval-additionner", "answers": [False, False]},
        {"activity": f"{PREFIX}eval-syllabes", "answers": [True, True, True]},
    ],
    "tom": [
        {"activity": f"{PREFIX}eval-compter", "answers": [True, True, True]},
        {"activity": f"{PREFIX}eval-syllabes", "answers": [True, True]},
    ],
}

# Given and not started, so the Élève space has something to open during the
# demonstration rather than only a history to read.
WAITING: Final[dict[str, str]] = {"lea": f"{PREFIX}decouverte-lecture"}
