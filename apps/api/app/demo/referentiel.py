"""Le référentiel de l'élémentaire : six classes, deux matières, un arbre.

**Six classes et non cinq.** L'élémentaire va du Cours d'Initiation au Cours
Moyen deuxième année : CI, CP, CE1, CE2, CM1, CM2. C'est le découpage en vigueur
au Sénégal et dans l'espace francophone ouest-africain, et il diffère du
découpage français, qui commence au CP.

**Les compétences sont cumulatives.** Un élève de CE2 doit tenir celles du CI, du
CP, du CE1 et du CE2. Ce n'est pas une convention d'affichage : c'est ce qui rend
le diagnostic capable de descendre. Quand un CM1 bute sur la division, la
plateforme remonte à la multiplication du CE2, puis à l'addition du CP si
nécessaire — et elle propose de travailler *là*, pas de refaire des divisions.

**Les prérequis traversent les niveaux exprès.** C'est le comportement le plus
utile de la plateforme, pas un cas particulier. Un enfant qui échoue en
conjugaison est renvoyé à la reconnaissance des groupes de verbes, qui est du
niveau d'en dessous — jamais l'inverse, car demander de conjuguer à qui ne
distingue pas les groupes revient à faire échouer deux fois au même endroit.

Le découpage des compétences suit la progression usuelle de l'élémentaire : les
lettres et les sons avant les syllabes, les syllabes avant les phonèmes, les
phonèmes avant la lecture de mots ; dénombrer avant lire les nombres, lire avant
comparer, comparer avant additionner. Rien ici n'est inventé pour la commodité de
l'implémentation.
"""

from __future__ import annotations

from typing import Any, Final

# ── Les six classes, dans l'ordre ───────────────────────────────────────────
CI: Final = "ci"
CP: Final = "cp"
CE1: Final = "ce1"
CE2: Final = "ce2"
CM1: Final = "cm1"
CM2: Final = "cm2"

# Le sigle précède le nom : « CE1 — Cours élémentaire première année ». Un
# parent connaît la classe de son enfant par son sigle bien avant d'en connaître
# le nom complet, et un menu qui n'affiche que le nom long l'oblige à le
# déchiffrer à chaque fois plutôt que de le reconnaître d'un coup d'œil.
LEVELS: Final[list[tuple[str, str]]] = [
    (CI, "CI — Cours d’initiation"),
    (CP, "CP — Cours préparatoire"),
    (CE1, "CE1 — Cours élémentaire première année"),
    (CE2, "CE2 — Cours élémentaire deuxième année"),
    (CM1, "CM1 — Cours moyen première année"),
    (CM2, "CM2 — Cours moyen deuxième année"),
]

LEVEL_CODES: Final[tuple[str, ...]] = tuple(code for code, _ in LEVELS)
LEVEL_LABELS: Final[dict[str, str]] = dict(LEVELS)


def levels_up_to(level_code: str) -> tuple[str, ...]:
    """Les classes qu'un élève de cette classe doit tenir, la sienne comprise.

    C'est la règle du cumul, écrite une fois. Un CE2 doit le CI, le CP, le CE1 et
    le CE2 ; un CI ne doit que le CI. Une classe inconnue ne donne rien plutôt
    que tout : mieux vaut ne rien proposer que proposer le programme entier.
    """
    if level_code not in LEVEL_CODES:
        return ()
    return LEVEL_CODES[: LEVEL_CODES.index(level_code) + 1]


def next_level(level_code: str) -> str | None:
    """La classe suivante, ou rien si l'élève est déjà en CM2.

    Le CM2 n'a pas de suivant dans l'élémentaire : la suite est le collège, que
    cette plateforme ne couvre pas et sur lequel elle ne prétend rien.
    """
    if level_code not in LEVEL_CODES:
        return None
    position = LEVEL_CODES.index(level_code)
    if position + 1 >= len(LEVEL_CODES):
        return None
    return LEVEL_CODES[position + 1]


# ── Les compétences ─────────────────────────────────────────────────────────
# CI
CI_FR_LETTRES: Final = "ci-fr-lettres"
CI_FR_SONS: Final = "ci-fr-sons"
CI_FR_SENS: Final = "ci-fr-sens"
CI_MA_DENOMBRER: Final = "ci-ma-denombrer"
CI_MA_CHIFFRES: Final = "ci-ma-chiffres"
CI_MA_COMPARER: Final = "ci-ma-comparer"
CI_AN_SALUTATIONS: Final = "ci-an-salutations"
CI_AN_COULEURS: Final = "ci-an-couleurs"
CI_AN_NOMBRES5: Final = "ci-an-nombres-5"

# CP
CP_FR_SYLLABES: Final = "cp-fr-syllabes"
CP_FR_PHONEMES: Final = "cp-fr-phonemes"
CP_FR_MOTS: Final = "cp-fr-mots"
CP_MA_NOMBRES: Final = "cp-ma-nombres-20"
CP_MA_RANGER: Final = "cp-ma-ranger"
CP_MA_ADDITION: Final = "cp-ma-addition"
CP_AN_ALPHABET: Final = "cp-an-alphabet"
CP_AN_ANIMAUX: Final = "cp-an-animaux"
CP_AN_NOMBRES10: Final = "cp-an-nombres-10"

# CE1
CE1_FR_PHRASE: Final = "ce1-fr-phrase"
CE1_FR_DICTEE: Final = "ce1-fr-dictee"
CE1_FR_ACCORDS: Final = "ce1-fr-accords"
CE1_MA_NOMBRES: Final = "ce1-ma-nombres-100"
CE1_MA_SOUSTRACTION: Final = "ce1-ma-soustraction"
CE1_MA_PROBLEME: Final = "ce1-ma-probleme"
CE1_AN_FAMILLE: Final = "ce1-an-famille"
CE1_AN_MOTS: Final = "ce1-an-mots"
CE1_AN_PRESENTATION: Final = "ce1-an-presentation"

# CE2
CE2_FR_GROUPES: Final = "ce2-fr-groupes"
CE2_FR_CONJUGAISON: Final = "ce2-fr-conjugaison"
CE2_FR_TEXTE: Final = "ce2-fr-texte"
CE2_MA_NOMBRES: Final = "ce2-ma-nombres-1000"
CE2_MA_MULTIPLICATION: Final = "ce2-ma-multiplication"
CE2_MA_MESURES: Final = "ce2-ma-mesures"
CE2_AN_PHRASES: Final = "ce2-an-phrases"
CE2_AN_QUESTIONS: Final = "ce2-an-questions"
CE2_AN_JOURS: Final = "ce2-an-jours"

# CM1
CM1_FR_NATURE: Final = "cm1-fr-nature"
CM1_FR_TEMPS: Final = "cm1-fr-temps"
CM1_FR_ESSENTIEL: Final = "cm1-fr-essentiel"
CM1_MA_FRACTIONS: Final = "cm1-ma-fractions"
CM1_MA_DIVISION: Final = "cm1-ma-division"
CM1_MA_PROBLEME2: Final = "cm1-ma-probleme-2"
CM1_AN_ETRE_AVOIR: Final = "cm1-an-etre-avoir"
CM1_AN_PLURIEL: Final = "cm1-an-pluriel"
CM1_AN_QUOTIDIEN: Final = "cm1-an-quotidien"

# CM2
CM2_FR_ACCORDS: Final = "cm2-fr-accords"
CM2_FR_COMPOSES: Final = "cm2-fr-temps-composes"
CM2_FR_REDACTION: Final = "cm2-fr-redaction"
CM2_MA_DECIMAUX: Final = "cm2-ma-decimaux"
CM2_MA_PROPORTION: Final = "cm2-ma-proportion"
CM2_MA_GEOMETRIE: Final = "cm2-ma-geometrie"
CM2_AN_TEXTE: Final = "cm2-an-texte"
CM2_AN_PRESENT: Final = "cm2-an-present"
CM2_AN_REDACTION: Final = "cm2-an-redaction"


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


# Cinquante-quatre compétences, neuf par classe, trois par matière. Les
# prérequis sont la vraie affirmation pédagogique de ce fichier : c'est par eux
# que la plateforme descend d'une difficulté visible à sa cause.
#
# Le français n'est prérequis de rien à l'oral : rien n'impose à un enfant de
# lire en français avant de saluer en anglais, et compter jusqu'à cinq ne
# demande pas de savoir lire. Mais deux familles de compétences en dépendent
# à l'écrit, et le prérequis traverse alors la matière exprès. En
# mathématiques, résoudre un problème commence par comprendre l'énoncé : un
# enfant qui ne lit pas encore une phrase française butera sur l'énoncé avant
# de buter sur le calcul, et le diagnostic doit le dire. En anglais, lire et
# écrire s'appuient sur la mécanique déjà acquise en français — reconnaître
# des lettres, décoder un mot, comprendre une phrase — le français servant de
# base de traduction (« eat » se comprend par « manger », pas dans le vide).
COMPETENCIES: Final[list[dict[str, Any]]] = [
    # ── CI ──────────────────────────────────────────────────────────────────
    _c(CI_FR_LETTRES, "Reconnaître les lettres de l’alphabet", "fr-code", CI, 1),
    _c(CI_FR_SONS, "Distinguer les sons du langage", "fr-code", CI, 2),
    _c(CI_FR_SENS, "Suivre le sens de la lecture", "fr-lire", CI, 3),
    _c(CI_MA_DENOMBRER, "Dénombrer une collection jusqu’à 10", "ma-nombres", CI, 1),
    _c(
        CI_MA_CHIFFRES,
        "Lire et écrire les chiffres jusqu’à 10",
        "ma-nombres",
        CI,
        2,
        [CI_MA_DENOMBRER],
    ),
    _c(
        CI_MA_COMPARER,
        "Comparer deux collections",
        "ma-nombres",
        CI,
        3,
        [CI_MA_DENOMBRER],
    ),
    _c(
        CI_AN_SALUTATIONS,
        "Comprendre et utiliser des salutations simples",
        "an-oral",
        CI,
        1,
    ),
    _c(CI_AN_COULEURS, "Nommer les couleurs de base", "an-oral", CI, 2),
    _c(CI_AN_NOMBRES5, "Compter de un à cinq", "an-oral", CI, 3),
    # ── CP ──────────────────────────────────────────────────────────────────
    _c(CP_FR_SYLLABES, "Manipuler les syllabes", "fr-code", CP, 1, [CI_FR_SONS]),
    _c(CP_FR_PHONEMES, "Manipuler les phonèmes", "fr-code", CP, 2, [CP_FR_SYLLABES]),
    _c(
        CP_FR_MOTS,
        "Lire et écrire des mots simples",
        "fr-lire",
        CP,
        3,
        [CP_FR_PHONEMES, CI_FR_LETTRES],
    ),
    _c(
        CP_MA_NOMBRES,
        "Lire et écrire les nombres jusqu’à 20",
        "ma-nombres",
        CP,
        1,
        [CI_MA_CHIFFRES],
    ),
    _c(
        CP_MA_RANGER,
        "Comparer et ranger jusqu’à 20",
        "ma-nombres",
        CP,
        2,
        [CP_MA_NOMBRES, CI_MA_COMPARER],
    ),
    _c(CP_MA_ADDITION, "Additionner jusqu’à 20", "ma-calcul", CP, 3, [CP_MA_RANGER]),
    _c(
        CP_AN_ALPHABET,
        "Reconnaître les lettres de l’alphabet anglais",
        "an-ecrit",
        CP,
        1,
        [CI_FR_LETTRES],
    ),
    _c(
        CP_AN_ANIMAUX,
        "Nommer des animaux familiers",
        "an-oral",
        CP,
        2,
        [CI_AN_SALUTATIONS],
    ),
    _c(
        CP_AN_NOMBRES10,
        "Compter et lire les nombres jusqu’à dix",
        "an-ecrit",
        CP,
        3,
        [CI_AN_NOMBRES5, CP_AN_ALPHABET],
    ),
    # ── CE1 ─────────────────────────────────────────────────────────────────
    _c(
        CE1_FR_PHRASE,
        "Lire une phrase et la comprendre",
        "fr-lire",
        CE1,
        1,
        [CP_FR_MOTS, CI_FR_SENS],
    ),
    _c(
        CE1_FR_DICTEE,
        "Écrire des mots et des phrases dictés",
        "fr-lire",
        CE1,
        2,
        [CP_FR_MOTS],
    ),
    _c(
        CE1_FR_ACCORDS,
        "Accorder le nom et le verbe",
        "fr-code",
        CE1,
        3,
        [CE1_FR_DICTEE],
    ),
    _c(
        CE1_MA_NOMBRES,
        "Lire, écrire et ranger jusqu’à 100",
        "ma-nombres",
        CE1,
        1,
        [CP_MA_RANGER],
    ),
    _c(
        CE1_MA_SOUSTRACTION,
        "Soustraire jusqu’à 100",
        "ma-calcul",
        CE1,
        2,
        [CP_MA_ADDITION],
    ),
    _c(
        CE1_MA_PROBLEME,
        "Résoudre un problème à une étape",
        "ma-calcul",
        CE1,
        3,
        [CE1_MA_SOUSTRACTION, CE1_FR_PHRASE],
    ),
    _c(
        CE1_AN_FAMILLE,
        "Nommer les membres de la famille",
        "an-oral",
        CE1,
        1,
        [CP_AN_ANIMAUX],
    ),
    _c(
        CE1_AN_MOTS,
        "Lire et écrire des mots anglais simples",
        "an-ecrit",
        CE1,
        2,
        [CP_AN_ALPHABET, CP_FR_MOTS],
    ),
    _c(
        CE1_AN_PRESENTATION,
        "Se présenter en anglais",
        "an-oral",
        CE1,
        3,
        [CI_AN_SALUTATIONS],
    ),
    # ── CE2 ─────────────────────────────────────────────────────────────────
    # Les groupes de verbes viennent AVANT la conjugaison, et c'est le sens de la
    # remarque du propriétaire : demander de conjuguer à qui ne distingue pas les
    # groupes, c'est faire échouer deux fois au même endroit.
    _c(
        CE2_FR_GROUPES,
        "Reconnaître les groupes de verbes",
        "fr-code",
        CE2,
        1,
        [CE1_FR_ACCORDS],
    ),
    _c(
        CE2_FR_CONJUGAISON,
        "Conjuguer au présent les verbes usuels",
        "fr-code",
        CE2,
        2,
        [CE2_FR_GROUPES],
    ),
    _c(
        CE2_FR_TEXTE,
        "Comprendre un texte court lu seul",
        "fr-lire",
        CE2,
        3,
        [CE1_FR_PHRASE],
    ),
    _c(
        CE2_MA_NOMBRES,
        "Lire, écrire et ranger jusqu’à 1000",
        "ma-nombres",
        CE2,
        1,
        [CE1_MA_NOMBRES],
    ),
    _c(
        CE2_MA_MULTIPLICATION,
        "Multiplier par un nombre à un chiffre",
        "ma-calcul",
        CE2,
        2,
        [CP_MA_ADDITION, CE1_MA_NOMBRES],
    ),
    _c(
        CE2_MA_MESURES,
        "Mesurer des longueurs et des durées",
        "ma-calcul",
        CE2,
        3,
        [CE1_MA_NOMBRES],
    ),
    _c(
        CE2_AN_PHRASES,
        "Lire et comprendre une phrase simple",
        "an-ecrit",
        CE2,
        1,
        [CE1_AN_MOTS, CE1_FR_PHRASE],
    ),
    _c(
        CE2_AN_QUESTIONS,
        "Poser et répondre à des questions simples",
        "an-oral",
        CE2,
        2,
        [CE1_AN_PRESENTATION],
    ),
    _c(
        CE2_AN_JOURS,
        "Nommer les jours de la semaine et les mois",
        "an-oral",
        CE2,
        3,
        [CE1_AN_FAMILLE],
    ),
    # ── CM1 ─────────────────────────────────────────────────────────────────
    _c(
        CM1_FR_NATURE,
        "Reconnaître la nature des mots",
        "fr-code",
        CM1,
        1,
        [CE1_FR_ACCORDS],
    ),
    _c(
        CM1_FR_TEMPS,
        "Distinguer le passé, le présent et le futur",
        "fr-code",
        CM1,
        2,
        [CE2_FR_CONJUGAISON],
    ),
    _c(
        CM1_FR_ESSENTIEL,
        "Retrouver l’essentiel d’un texte",
        "fr-lire",
        CM1,
        3,
        [CE2_FR_TEXTE],
    ),
    _c(
        CM1_MA_FRACTIONS,
        "Lire et comparer des fractions simples",
        "ma-nombres",
        CM1,
        1,
        [CE2_MA_NOMBRES],
    ),
    _c(
        CM1_MA_DIVISION,
        "Diviser par un nombre à un chiffre",
        "ma-calcul",
        CM1,
        2,
        [CE2_MA_MULTIPLICATION],
    ),
    _c(
        CM1_MA_PROBLEME2,
        "Résoudre un problème à deux étapes",
        "ma-calcul",
        CM1,
        3,
        [CE1_MA_PROBLEME, CE2_MA_MULTIPLICATION, CE2_FR_TEXTE],
    ),
    _c(
        CM1_AN_ETRE_AVOIR,
        "Utiliser to be et to have au présent",
        "an-ecrit",
        CM1,
        1,
        [CE2_AN_PHRASES, CE2_FR_CONJUGAISON],
    ),
    _c(
        CM1_AN_PLURIEL,
        "Former le pluriel des noms réguliers",
        "an-ecrit",
        CM1,
        2,
        [CE1_AN_MOTS],
    ),
    _c(
        CM1_AN_QUOTIDIEN,
        "Utiliser le vocabulaire du quotidien",
        "an-oral",
        CM1,
        3,
        [CE2_AN_QUESTIONS],
    ),
    # ── CM2 ─────────────────────────────────────────────────────────────────
    _c(
        CM2_FR_ACCORDS,
        "Accorder dans les cas difficiles",
        "fr-code",
        CM2,
        1,
        [CM1_FR_NATURE],
    ),
    _c(
        CM2_FR_COMPOSES,
        "Employer les temps composés",
        "fr-code",
        CM2,
        2,
        [CM1_FR_TEMPS],
    ),
    _c(
        CM2_FR_REDACTION,
        "Rédiger un texte cohérent",
        "fr-lire",
        CM2,
        3,
        [CM1_FR_ESSENTIEL, CE1_FR_DICTEE],
    ),
    _c(
        CM2_MA_DECIMAUX,
        "Lire et calculer avec les nombres décimaux",
        "ma-nombres",
        CM2,
        1,
        [CM1_MA_FRACTIONS],
    ),
    _c(
        CM2_MA_PROPORTION,
        "Résoudre un problème de proportionnalité",
        "ma-calcul",
        CM2,
        2,
        [CM1_MA_PROBLEME2, CM1_FR_ESSENTIEL],
    ),
    _c(
        CM2_MA_GEOMETRIE,
        "Calculer un périmètre et une aire",
        "ma-calcul",
        CM2,
        3,
        [CE2_MA_MESURES, CE2_MA_MULTIPLICATION],
    ),
    _c(
        CM2_AN_TEXTE,
        "Comprendre un texte court en anglais",
        "an-ecrit",
        CM2,
        1,
        [CE2_AN_PHRASES, CM1_AN_ETRE_AVOIR, CE2_FR_TEXTE],
    ),
    _c(
        CM2_AN_PRESENT,
        "Décrire une habitude au présent simple",
        "an-ecrit",
        CM2,
        2,
        [CM1_AN_ETRE_AVOIR],
    ),
    _c(
        CM2_AN_REDACTION,
        "Rédiger des phrases simples sur soi-même",
        "an-ecrit",
        CM2,
        3,
        [CE1_AN_PRESENTATION, CM1_AN_PLURIEL, CE1_FR_DICTEE],
    ),
]

COMPETENCIES_BY_LEVEL: Final[dict[str, list[dict[str, Any]]]] = {
    level: [row for row in COMPETENCIES if row["level"] == level]
    for level in LEVEL_CODES
}


def referential(edition_code: str, edition_label: str) -> dict[str, Any]:
    """L'édition complète, prête pour l'import contrôlé."""
    return {
        "version": {"code": edition_code, "label": edition_label},
        "levels": [
            {"code": code, "label": label, "position": position}
            for position, (code, label) in enumerate(LEVELS, start=1)
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
            {
                "code": "an",
                "label": "Anglais",
                "position": 3,
                "domains": [
                    {"code": "an-oral", "label": "Écouter et parler", "position": 1},
                    {"code": "an-ecrit", "label": "Lire et écrire", "position": 2},
                ],
            },
        ],
        "competencies": COMPETENCIES,
    }
