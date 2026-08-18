"""Un examen d'entrée par classe, du CI au CM2.

**Pourquoi un par classe.** Un élève nouvellement inscrit n'a aucun historique :
sans lui demander quelque chose, la plateforme ne sait rien et n'a rien à
proposer. L'examen le lui demande — mais ce qu'on demande à un CI et ce qu'on
demande à un CM2 n'ont rien à voir, d'où six examens et non un.

**Il ne porte que sur la classe déclarée**, six questions, une par compétence de
ce niveau. C'est court exprès : un examen qui balaierait aussi les cinq classes
d'en dessous ferait trente-six questions à un CM2, et un enfant ne le finirait
pas. La descente vers les classes antérieures est le travail du diagnostic, pas
celui de l'examen : quand une compétence n'est pas acquise et que son prérequis
n'a **jamais été observé**, la plateforme le dit et propose de le travailler.

**Aucune réponse ne quitte le serveur**, et aucune question ne porte
d'explication : expliquer pendant qu'on mesure abîme la mesure. C'est ce qui
sépare un examen d'une fiche de remédiation.

**Ce que ces examens ne savent pas faire.** Entendre, et montrer. Le CI en
souffre le plus : un enfant de cours d'initiation ne lit pas encore, et un examen
écrit lui demande déjà de déchiffrer la question. Les items du CI sont les plus
fragiles de tout ce fichier, et ils resteront un pis-aller tant qu'il n'y aura ni
son ni image.
"""

from __future__ import annotations

from typing import Final, TypedDict

from app.demo import referentiel as ref


class ExamQuestion(TypedDict):
    ref: str
    competency: str
    prompt: str
    choices: list[str]
    correct: int


class Exam(TypedDict):
    level: str
    title: str
    minutes: int
    questions: list[ExamQuestion]


def _q(
    ref_: str, competency: str, prompt: str, choices: list[str], correct: int
) -> ExamQuestion:
    return {
        "ref": ref_,
        "competency": competency,
        "prompt": prompt,
        "choices": choices,
        "correct": correct,
    }


# Le titre est le même partout, et à dessein : une enfant de six ans qui
# rencontre une page intitulée « évaluation diagnostique de niveau CI » apprend
# quelque chose sur l'école avant d'apprendre quoi que ce soit sur elle-même.
TITLE: Final = "Pour faire connaissance"

EXAMS: Final[list[Exam]] = [
    {
        "level": ref.CI,
        "title": TITLE,
        "minutes": 8,
        "questions": [
            _q(
                "ci-q1",
                ref.CI_FR_LETTRES,
                "Combien de lettres différentes vois-tu ?   A   A   B",
                ["Une", "Deux", "Trois"],
                1,
            ),
            _q(
                "ci-q2",
                ref.CI_FR_SONS,
                "Quel mot commence par le même son que « papa » ?",
                ["Porte", "Table", "Lune"],
                0,
            ),
            _q(
                "ci-q3",
                ref.CI_FR_SENS,
                "Quand on lit une phrase en français, par où commence-t-on ?",
                ["Par la gauche", "Par la droite", "Par le milieu"],
                0,
            ),
            _q(
                "ci-q4",
                ref.CI_MA_DENOMBRER,
                "Combien y a-t-il de ronds ?   ● ● ● ●",
                ["Trois", "Quatre", "Cinq"],
                1,
            ),
            _q(
                "ci-q5",
                ref.CI_MA_CHIFFRES,
                "Quel chiffre s’écrit « trois » ?",
                ["2", "3", "5"],
                1,
            ),
            _q(
                "ci-q6",
                ref.CI_MA_COMPARER,
                "Quel groupe a le plus d’objets ?   A : ● ●    B : ● ● ● ●    C : ●",
                ["A", "B", "C"],
                1,
            ),
        ],
    },
    {
        "level": ref.CP,
        "title": TITLE,
        "minutes": 10,
        "questions": [
            _q(
                "cp-q1",
                ref.CP_FR_SYLLABES,
                "Combien de syllabes y a-t-il dans le mot « papillon » ?",
                ["Deux", "Trois", "Quatre"],
                1,
            ),
            _q(
                "cp-q2",
                ref.CP_FR_PHONEMES,
                "Quel mot commence par le même son que « souris » ?",
                ["Salade", "Chapeau", "Maison"],
                0,
            ),
            _q(
                "cp-q3",
                ref.CP_FR_MOTS,
                "Quel mot est écrit correctement ?",
                ["chapo", "chapeau", "chapiau"],
                1,
            ),
            _q(
                "cp-q4",
                ref.CP_MA_NOMBRES,
                "Quel nombre s’écrit « quatorze » ?",
                ["4", "14", "40"],
                1,
            ),
            _q(
                "cp-q5",
                ref.CP_MA_RANGER,
                "Quel nombre est le plus grand ?",
                ["8", "12", "10"],
                1,
            ),
            _q(
                "cp-q6",
                ref.CP_MA_ADDITION,
                "Combien font 7 + 6 ?",
                ["12", "13", "14"],
                1,
            ),
        ],
    },
    {
        "level": ref.CE1,
        "title": TITLE,
        "minutes": 10,
        "questions": [
            _q(
                "ce1-q1",
                ref.CE1_FR_PHRASE,
                "« Tom prend son parapluie avant de sortir. » Quel temps fait-il ?",
                ["Il pleut", "Il fait très chaud", "Il neige"],
                0,
            ),
            _q(
                "ce1-q2",
                ref.CE1_FR_DICTEE,
                "Quelle phrase est écrite correctement ?",
                [
                    "Les enfant jouent dans la cour.",
                    "Les enfants jouent dans la cour.",
                    "Les enfants joue dans la cour.",
                ],
                1,
            ),
            _q(
                "ce1-q3",
                ref.CE1_FR_ACCORDS,
                "« Les oiseaux … dans le ciel. » Quelle forme convient ?",
                ["vole", "volent", "volons"],
                1,
            ),
            _q(
                "ce1-q4",
                ref.CE1_MA_NOMBRES,
                "Quel nombre vient juste après 79 ?",
                ["70", "80", "90"],
                1,
            ),
            _q(
                "ce1-q5",
                ref.CE1_MA_SOUSTRACTION,
                "Combien font 15 − 8 ?",
                ["6", "7", "8"],
                1,
            ),
            _q(
                "ce1-q6",
                ref.CE1_MA_PROBLEME,
                "Tom a 12 billes. Il en donne 4 à Léa. Combien lui en reste-t-il ?",
                ["6", "8", "16"],
                1,
            ),
        ],
    },
    {
        "level": ref.CE2,
        "title": TITLE,
        "minutes": 12,
        "questions": [
            _q(
                "ce2-q1",
                ref.CE2_FR_GROUPES,
                "À quel groupe appartient le verbe « finir » ?",
                ["Premier groupe", "Deuxième groupe", "Troisième groupe"],
                1,
            ),
            _q(
                "ce2-q2",
                ref.CE2_FR_CONJUGAISON,
                "« Nous … à l’école tous les matins. » Quelle forme convient ?",
                ["allons", "allez", "vont"],
                0,
            ),
            _q(
                "ce2-q3",
                ref.CE2_FR_TEXTE,
                "« La pluie tombait depuis trois jours. La rivière montait. » "
                "Que risque-t-il d’arriver ?",
                ["Une sécheresse", "Une inondation", "Un incendie"],
                1,
            ),
            _q(
                "ce2-q4",
                ref.CE2_MA_NOMBRES,
                "Quel nombre est le plus grand ?",
                ["405", "450", "98"],
                1,
            ),
            _q(
                "ce2-q5",
                ref.CE2_MA_MULTIPLICATION,
                "Combien font 7 × 8 ?",
                ["48", "56", "64"],
                1,
            ),
            _q(
                "ce2-q6",
                ref.CE2_MA_MESURES,
                "Combien de centimètres y a-t-il dans un mètre ?",
                ["10", "100", "1000"],
                1,
            ),
        ],
    },
    {
        "level": ref.CM1,
        "title": TITLE,
        "minutes": 12,
        "questions": [
            _q(
                "cm1-q1",
                ref.CM1_FR_NATURE,
                "Lequel de ces mots est un adjectif ?",
                ["Chien", "Rapide", "Courir"],
                1,
            ),
            _q(
                "cm1-q2",
                ref.CM1_FR_TEMPS,
                "« Demain, nous irons au marché. » De quel moment parle-t-on ?",
                ["Du passé", "Du futur", "Du présent"],
                1,
            ),
            _q(
                "cm1-q3",
                ref.CM1_FR_ESSENTIEL,
                "« Amadou se lève tôt, prépare son sac et part à pied. Il arrive "
                "à l’heure. » De quoi ce texte parle-t-il ?",
                [
                    "D’un départ pour l’école",
                    "D’un repas de fête",
                    "D’un voyage en car",
                ],
                0,
            ),
            _q(
                "cm1-q4",
                ref.CM1_MA_FRACTIONS,
                "Quelle fraction est la plus grande ?",
                ["1/4", "1/2", "1/8"],
                1,
            ),
            _q(
                "cm1-q5",
                ref.CM1_MA_DIVISION,
                "Combien font 56 ÷ 7 ?",
                ["6", "8", "9"],
                1,
            ),
            _q(
                "cm1-q6",
                ref.CM1_MA_PROBLEME2,
                "Awa achète 3 cahiers à 200 francs l’un. Elle paie avec un billet "
                "de 1000 francs. Combien lui rend-on ?",
                ["300", "400", "600"],
                1,
            ),
        ],
    },
    {
        "level": ref.CM2,
        "title": TITLE,
        "minutes": 15,
        "questions": [
            _q(
                "cm2-q1",
                ref.CM2_FR_ACCORDS,
                "« Les fleurs que j’ai … sont belles. » Quelle forme convient ?",
                ["cueilli", "cueillies", "cueillis"],
                1,
            ),
            _q(
                "cm2-q2",
                ref.CM2_FR_COMPOSES,
                "« Hier, j’… mon travail avant le dîner. » Quelle forme convient ?",
                ["ai fini", "finis", "finirai"],
                0,
            ),
            _q(
                "cm2-q3",
                ref.CM2_FR_REDACTION,
                "Quelle phrase enchaîne le mieux après « Il pleuvait très fort » ?",
                [
                    "Pourtant, nous sommes sortis.",
                    "Le chat mange une souris.",
                    "Trois plus quatre font sept.",
                ],
                0,
            ),
            _q(
                "cm2-q4",
                ref.CM2_MA_DECIMAUX,
                "Quel nombre est le plus grand ?",
                ["0,9", "0,25", "0,7"],
                0,
            ),
            _q(
                "cm2-q5",
                ref.CM2_MA_PROPORTION,
                "Trois cahiers coûtent 600 francs. Combien coûtent cinq cahiers ?",
                ["800", "1000", "1200"],
                1,
            ),
            _q(
                "cm2-q6",
                ref.CM2_MA_GEOMETRIE,
                "Quel est le périmètre d’un carré de 5 cm de côté ?",
                ["10 cm", "20 cm", "25 cm"],
                1,
            ),
        ],
    },
]

EXAMS_BY_LEVEL: Final[dict[str, Exam]] = {exam["level"]: exam for exam in EXAMS}
