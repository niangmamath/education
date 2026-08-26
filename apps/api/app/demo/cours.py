"""A first, small batch of courses — the pilot that proves the mechanism.

Étape 15. A course teaches a competency **before** it is ever tested, unlike
a remediation sheet (ADR-017) which repairs one already found in gap. Two
pilots only, both on competencies a fiche already covers (`ci-fr-lettres`,
`ci-ma-denombrer`): a child who does not open the course, or who opens it and
still fails the exam, meets a remediation that already exists — the full
loop this étape aims for is demonstrable end to end without waiting on the
other fifty-two competencies.

Covering the rest of the referential is deliberately left for later, the same
way the first twelve remediation sheets preceded HORS-09's three more: this
proves the shape, it does not claim completeness.
"""

from __future__ import annotations

from typing import Final, TypedDict

from app.demo.dataset import PREFIX
from app.demo.referentiel import CI_FR_LETTRES as FR_LETTRES
from app.demo.referentiel import CI_MA_DENOMBRER as MA_DENOMBRER


class CourseCheck(TypedDict):
    ref: str
    prompt: str
    choices: list[str]
    correct: int
    explanation: str


class Course(TypedDict):
    code: str
    title: str
    competency: str
    minutes: int
    guidance: str
    questions: list[CourseCheck]


COURSES: Final[list[Course]] = [
    {
        "code": f"{PREFIX}cours-fr-lettres",
        "title": "Les lettres et leurs sons",
        "competency": FR_LETTRES,
        "minutes": 10,
        "guidance": (
            "Chaque lettre a un nom et un son, et ce ne sont pas la même chose. "
            "La lettre S se nomme « esse », mais dans un mot elle fait « sss » : "
            "sac, soleil. C’est le son qui sert à lire, pas le nom.\n\n"
            "Il y a vingt-six lettres, toujours dans le même ordre : A, B, C, D, "
            "E, F, G... jusqu’à Z. Les redire souvent dans l’ordre aide à "
            "retrouver une lettre sans hésiter.\n\n"
            "Certains sons peuvent s’étirer aussi longtemps qu’on a du souffle — "
            "M fait « mmmm », F fait « ffff » — et d’autres s’arrêtent net : P, "
            "T, K. Essaie de tenir le son d’une lettre : si tu peux le tenir, tu "
            "sais déjà dans quel groupe elle est."
        ),
        "questions": [
            {
                "ref": "cours-fr-lettres-1",
                "prompt": "Quelle lettre vient juste après le C dans l’alphabet ?",
                "choices": ["B", "D", "E"],
                "correct": 1,
                "explanation": (
                    "L’ordre est A, B, C, D, E. Le D vient juste après le C."
                ),
            },
            {
                "ref": "cours-fr-lettres-2",
                "prompt": "Quelle lettre fait un son que l’on peut tenir longtemps ?",
                "choices": ["T", "M", "K"],
                "correct": 1,
                "explanation": (
                    "Le M fait « mmmm » et dure tant qu’on souffle. Le T et le K "
                    "s’arrêtent net."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}cours-ma-denombrer",
        "title": "Compter des objets un par un",
        "competency": MA_DENOMBRER,
        "minutes": 10,
        "guidance": (
            "Dénombrer, c’est dire combien il y a d’objets, pas seulement "
            "réciter des nombres. La règle est simple : toucher un seul objet à "
            "la fois, dire un seul nombre à la fois, et ne jamais toucher deux "
            "fois le même objet.\n\n"
            "Le dernier nombre dit est la réponse — pas le premier, pas un "
            "nombre inventé après coup. Si tu comptes trois jetons et que le "
            "dernier mot dit est « trois », alors il y a trois jetons.\n\n"
            "Quand les objets sont en désordre, les aligner ou les pointer un à "
            "un aide à ne pas en oublier ni en compter deux fois."
        ),
        "questions": [
            {
                "ref": "cours-ma-denombrer-1",
                "prompt": "Tu comptes des jetons et le dernier mot que tu dis est « quatre ». Combien y a-t-il de jetons ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 1,
                "explanation": (
                    "Le dernier nombre dit en comptant est la réponse : quatre."
                ),
            },
            {
                "ref": "cours-ma-denombrer-2",
                "prompt": "Pour bien compter des objets, que ne faut-il jamais faire ?",
                "choices": [
                    "Toucher chaque objet une seule fois",
                    "Toucher le même objet deux fois",
                    "Dire les nombres dans l’ordre",
                ],
                "correct": 1,
                "explanation": (
                    "Toucher deux fois le même objet le compte deux fois, ce "
                    "qui donne un total trop grand."
                ),
            },
        ],
    },
]
