"""Un examen d'entrée par classe, du CI au CM2.

**Pourquoi un par classe.** Un élève nouvellement inscrit n'a aucun historique :
sans lui demander quelque chose, la plateforme ne sait rien et n'a rien à
proposer. L'examen le lui demande — mais ce qu'on demande à un CI et ce qu'on
demande à un CM2 n'ont rien à voir, d'où six examens et non un.

**Il ne porte que sur la classe déclarée**, vingt-sept questions en tout, trois
par compétence de ce niveau. C'est court exprès pour une classe : un examen qui
balaierait aussi les cinq classes d'en dessous ferait plus de cent soixante
questions à un CM2, et un enfant ne le finirait pas. La descente vers les
classes antérieures est le travail du diagnostic, pas celui de l'examen : quand
une compétence n'est pas acquise et que son prérequis n'a **jamais été
observé**, la plateforme le dit et propose de le travailler.

**Ce module ne décrit que le contenu, jamais la façon dont il est servi.**
Depuis l'étape 14, les vingt-sept questions d'une classe ne sont plus données
en une seule fois : `app.assessment.tiers` décide, à chaque lecture, quel
palier de compétences est prêt à être testé, et `app.authored.service` n'en
sert que les questions. Ce fichier reste la banque entière d'une classe ; la
politique de service vit ailleurs, et c'est délibéré — un contenu ne devrait
pas savoir comment il est distribué.

**Trois questions et non une.** Une seule question par compétence ne peut
rendre qu'un verdict binaire — acquis ou pas — et le propriétaire a demandé
mieux : avec trois lectures, un enfant qui réussit deux questions sur trois
obtient une compétence « partielle » plutôt qu'un couperet, ce que
`app.attempts.rules.read_counts` sait déjà faire sans qu'il ait fallu y
toucher.

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


def _q3(
    competency: str,
    items: list[tuple[str, list[str], int]],
) -> list[ExamQuestion]:
    """Les trois questions d'une compétence, sous une référence dérivée du code.

    La référence est `{compétence}-q{n}` : elle ne peut pas entrer en collision
    avec celle d'une autre compétence, puisque le code de compétence est déjà
    unique dans le référentiel.
    """
    return [
        {
            "ref": f"{competency}-q{position}",
            "competency": competency,
            "prompt": prompt,
            "choices": choices,
            "correct": correct,
        }
        for position, (prompt, choices, correct) in enumerate(items, start=1)
    ]


# Le titre est le même partout, et à dessein : une enfant de six ans qui
# rencontre une page intitulée « évaluation diagnostique de niveau CI » apprend
# quelque chose sur l'école avant d'apprendre quoi que ce soit sur elle-même.
TITLE: Final = "Pour faire connaissance"

EXAMS: Final[list[Exam]] = [
    {
        "level": ref.CI,
        "title": TITLE,
        "minutes": 20,
        "questions": [
            *_q3(
                ref.CI_FR_LETTRES,
                [
                    (
                        "Combien de lettres différentes vois-tu ?   A   A   B",
                        ["Une", "Deux", "Trois"],
                        1,
                    ),
                    (
                        "Quelle lettre vient juste après « B » dans l'alphabet ?",
                        ["A", "C", "D"],
                        1,
                    ),
                    (
                        "Quelle est la première lettre de l'alphabet ?",
                        ["A", "Z", "M"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CI_FR_SONS,
                [
                    (
                        "Quel mot commence par le même son que « papa » ?",
                        ["Porte", "Table", "Lune"],
                        0,
                    ),
                    (
                        "Quel mot commence par le même son que « chat » ?",
                        ["Chaise", "Robe", "Nid"],
                        0,
                    ),
                    (
                        "Quel mot se termine par le même son que « chapeau » ?",
                        ["Bateau", "Table", "Lune"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CI_FR_SENS,
                [
                    (
                        "Quand on lit une phrase en français, par où commence-t-on ?",
                        ["Par la gauche", "Par la droite", "Par le milieu"],
                        0,
                    ),
                    (
                        "Après avoir lu la dernière ligne à droite, où commence-t-on "
                        "à lire la ligne suivante ?",
                        ["En bas, à gauche", "En haut, à droite", "Au milieu"],
                        0,
                    ),
                    (
                        "Dans un livre, de quel côté tourne-t-on les pages pour "
                        "avancer dans l'histoire ?",
                        [
                            "De droite à gauche",
                            "De gauche à droite",
                            "On ne tourne pas les pages",
                        ],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CI_MA_DENOMBRER,
                [
                    (
                        "Combien y a-t-il de ronds ?   ● ● ● ●",
                        ["Trois", "Quatre", "Cinq"],
                        1,
                    ),
                    (
                        "Combien y a-t-il d'étoiles ?   ★ ★ ★ ★ ★ ★",
                        ["Cinq", "Six", "Sept"],
                        1,
                    ),
                    (
                        "Combien y a-t-il de carrés ?   ▪ ▪ ▪",
                        ["Deux", "Trois", "Quatre"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CI_MA_CHIFFRES,
                [
                    ("Quel chiffre s'écrit « trois » ?", ["2", "3", "5"], 1),
                    ("Quel chiffre s'écrit « sept » ?", ["6", "7", "9"], 1),
                    (
                        "Comment s'écrit le chiffre 9 en toutes lettres ?",
                        ["Six", "Huit", "Neuf"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CI_MA_COMPARER,
                [
                    (
                        "Quel groupe a le plus d'objets ?   "
                        "A : ● ●    B : ● ● ● ●    C : ●",
                        ["A", "B", "C"],
                        1,
                    ),
                    (
                        "Quel groupe a le moins d'objets ?   "
                        "A : ★ ★ ★    B : ★    C : ★ ★",
                        ["A", "B", "C"],
                        1,
                    ),
                    (
                        "Quel groupe a autant d'objets que   ▪ ▪ ▪   ?",
                        ["● ●", "● ● ●", "● ● ● ●"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CI_AN_SALUTATIONS,
                [
                    (
                        "Comment dit-on « bonjour » en anglais ?",
                        ["Goodbye", "Hello", "Please"],
                        1,
                    ),
                    (
                        "Comment dit-on « au revoir » en anglais ?",
                        ["Hello", "Thank you", "Goodbye"],
                        2,
                    ),
                    (
                        "Quelle réponse convient si un ami te salue le matin ?",
                        ["Hello", "Goodbye", "Please"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CI_AN_COULEURS,
                [
                    (
                        "Comment dit-on « rouge » en anglais ?",
                        ["Blue", "Red", "Green"],
                        1,
                    ),
                    (
                        "Comment dit-on « bleu » en anglais ?",
                        ["Blue", "Yellow", "Black"],
                        0,
                    ),
                    (
                        "Quelle couleur est « yellow » en français ?",
                        ["Vert", "Jaune", "Noir"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CI_AN_NOMBRES5,
                [
                    (
                        "Comment dit-on « trois » en anglais ?",
                        ["Two", "Three", "Five"],
                        1,
                    ),
                    (
                        "Comment dit-on « cinq » en anglais ?",
                        ["Four", "Five", "Six"],
                        1,
                    ),
                    (
                        "« One, two, three, four, … » Quel nombre manque ?",
                        ["Five", "Six", "Ten"],
                        0,
                    ),
                ],
            ),
        ],
    },
    {
        "level": ref.CP,
        "title": TITLE,
        "minutes": 25,
        "questions": [
            *_q3(
                ref.CP_FR_SYLLABES,
                [
                    (
                        "Combien de syllabes y a-t-il dans le mot « papillon » ?",
                        ["Deux", "Trois", "Quatre"],
                        1,
                    ),
                    (
                        "Combien de syllabes y a-t-il dans le mot « maison » ?",
                        ["Une", "Deux", "Trois"],
                        1,
                    ),
                    ("Quel mot a une seule syllabe ?", ["Chat", "Table", "Voiture"], 0),
                ],
            ),
            *_q3(
                ref.CP_FR_PHONEMES,
                [
                    (
                        "Quel mot commence par le même son que « souris » ?",
                        ["Salade", "Chapeau", "Maison"],
                        0,
                    ),
                    (
                        "Quel mot contient le son « on » ?",
                        ["Maison", "Lapin", "Table"],
                        0,
                    ),
                    (
                        "Quel mot se termine par le son « an » ?",
                        ["Maman", "Vélo", "Tasse"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CP_FR_MOTS,
                [
                    (
                        "Quel mot est écrit correctement ?",
                        ["chapo", "chapeau", "chapiau"],
                        1,
                    ),
                    (
                        "Quel mot est écrit correctement ?",
                        ["tabl", "table", "tabel"],
                        1,
                    ),
                    ("Quel mot désigne un animal ?", ["Chien", "Chaise", "Fenêtre"], 0),
                ],
            ),
            *_q3(
                ref.CP_MA_NOMBRES,
                [
                    ("Quel nombre s'écrit « quatorze » ?", ["4", "14", "40"], 1),
                    ("Quel nombre s'écrit « dix-huit » ?", ["8", "18", "80"], 1),
                    (
                        "Comment écrit-on 16 en toutes lettres ?",
                        ["Seize", "Six", "Soixante"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CP_MA_RANGER,
                [
                    ("Quel nombre est le plus grand ?", ["8", "12", "10"], 1),
                    ("Quel nombre est le plus petit ?", ["15", "9", "17"], 1),
                    ("Quel nombre vient entre 11 et 13 ?", ["10", "12", "14"], 1),
                ],
            ),
            *_q3(
                ref.CP_MA_ADDITION,
                [
                    ("Combien font 7 + 6 ?", ["12", "13", "14"], 1),
                    ("Combien font 9 + 8 ?", ["16", "17", "18"], 1),
                    ("Combien font 5 + 5 ?", ["9", "10", "11"], 1),
                ],
            ),
            *_q3(
                ref.CP_AN_ALPHABET,
                [
                    (
                        "Quelle lettre vient juste après « C » dans l'alphabet "
                        "anglais ?",
                        ["B", "D", "E"],
                        1,
                    ),
                    (
                        "Combien de lettres compte l'alphabet anglais ?",
                        ["24", "26", "28"],
                        1,
                    ),
                    (
                        "Quelle est la dernière lettre de l'alphabet anglais ?",
                        ["Y", "Z", "X"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CP_AN_ANIMAUX,
                [
                    ("Comment dit-on « chat » en anglais ?", ["Dog", "Cat", "Bird"], 1),
                    (
                        "Comment dit-on « chien » en anglais ?",
                        ["Dog", "Cow", "Fish"],
                        0,
                    ),
                    (
                        "Quel animal est un « bird » ?",
                        ["Un poisson", "Un oiseau", "Une vache"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CP_AN_NOMBRES10,
                [
                    (
                        "Comment dit-on « huit » en anglais ?",
                        ["Seven", "Eight", "Nine"],
                        1,
                    ),
                    ("Comment dit-on « dix » en anglais ?", ["Nine", "Ten", "Two"], 1),
                    (
                        "« Six, seven, eight, … » Quel nombre manque ?",
                        ["Nine", "Ten", "Five"],
                        0,
                    ),
                ],
            ),
        ],
    },
    {
        "level": ref.CE1,
        "title": TITLE,
        "minutes": 25,
        "questions": [
            *_q3(
                ref.CE1_FR_PHRASE,
                [
                    (
                        "« Tom prend son parapluie avant de sortir. » Quel temps "
                        "fait-il ?",
                        ["Il pleut", "Il fait très chaud", "Il neige"],
                        0,
                    ),
                    (
                        "« Awa met son manteau et son bonnet. » Quel temps fait-il ?",
                        ["Il fait chaud", "Il fait froid", "Il pleut des fleurs"],
                        1,
                    ),
                    (
                        "« Le chien aboie et court partout dès qu'on ouvre le "
                        "portail. » Où se passe la scène ?",
                        ["Dans le jardin", "À l'école", "Dans la cuisine"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_FR_DICTEE,
                [
                    (
                        "Quelle phrase est écrite correctement ?",
                        [
                            "Les enfant jouent dans la cour.",
                            "Les enfants jouent dans la cour.",
                            "Les enfants joue dans la cour.",
                        ],
                        1,
                    ),
                    (
                        "Quel mot est écrit correctement ?",
                        ["oiseau", "oizeau", "oisau"],
                        0,
                    ),
                    (
                        "Quelle phrase est écrite correctement ?",
                        [
                            "Le chat dor sur le lit.",
                            "Le chat dort sur le lit.",
                            "Le chat dors sur le lit.",
                        ],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_FR_ACCORDS,
                [
                    (
                        "« Les oiseaux … dans le ciel. » Quelle forme convient ?",
                        ["vole", "volent", "volons"],
                        1,
                    ),
                    (
                        "« Le chat … sur le mur. » Quelle forme convient ?",
                        ["marche", "marchent", "marchons"],
                        0,
                    ),
                    (
                        "« Mes amis … à la piscine. » Quelle forme convient ?",
                        ["nage", "nagez", "nagent"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_MA_NOMBRES,
                [
                    ("Quel nombre vient juste après 79 ?", ["70", "80", "90"], 1),
                    (
                        "Quel nombre est le plus grand ?",
                        ["68", "86", "Ils sont égaux"],
                        1,
                    ),
                    (
                        "Comment écrit-on 45 en toutes lettres ?",
                        ["Quarante-cinq", "Cinquante-quatre", "Quatorze-cinq"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_MA_SOUSTRACTION,
                [
                    ("Combien font 15 − 8 ?", ["6", "7", "8"], 1),
                    ("Combien font 42 − 15 ?", ["25", "27", "29"], 1),
                    ("Combien font 90 − 30 ?", ["50", "60", "70"], 1),
                ],
            ),
            *_q3(
                ref.CE1_MA_PROBLEME,
                [
                    (
                        "Tom a 12 billes. Il en donne 4 à Léa. Combien lui en "
                        "reste-t-il ?",
                        ["6", "8", "16"],
                        1,
                    ),
                    (
                        "Awa a 20 francs. Elle achète un bonbon à 5 francs. Combien "
                        "lui reste-t-il ?",
                        ["10", "15", "25"],
                        1,
                    ),
                    (
                        "Il y a 6 enfants. Chacun reçoit 2 crayons. Combien de "
                        "crayons a-t-on distribués ?",
                        ["8", "10", "12"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_AN_FAMILLE,
                [
                    (
                        "Comment dit-on « maman » en anglais ?",
                        ["Sister", "Mother", "Brother"],
                        1,
                    ),
                    (
                        "Comment dit-on « papa » en anglais ?",
                        ["Father", "Uncle", "Friend"],
                        0,
                    ),
                    (
                        "Comment dit-on « frère » en anglais ?",
                        ["Sister", "Brother", "Cousin"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_AN_MOTS,
                [
                    (
                        "Quel mot anglais désigne le soleil ?",
                        ["Moon", "Sun", "Star"],
                        1,
                    ),
                    (
                        "Quel mot anglais est écrit correctement pour « chien » ?",
                        ["Dogg", "Dog", "Doog"],
                        1,
                    ),
                    (
                        "Quel mot anglais désigne une maison ?",
                        ["House", "Horse", "Mouse"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE1_AN_PRESENTATION,
                [
                    (
                        "Comment dit-on « Je m'appelle Awa » en anglais ?",
                        ["I am fine", "My name is Awa", "Thank you Awa"],
                        1,
                    ),
                    (
                        "Comment demande-t-on le nom de quelqu'un en anglais ?",
                        ["What is your name?", "How old are you?", "Where are you?"],
                        0,
                    ),
                    (
                        "Comment répond-on à « How are you? » quand on va bien ?",
                        ["I am fine, thank you", "My name is Tom", "Goodbye"],
                        0,
                    ),
                ],
            ),
        ],
    },
    {
        "level": ref.CE2,
        "title": TITLE,
        "minutes": 28,
        "questions": [
            *_q3(
                ref.CE2_FR_GROUPES,
                [
                    (
                        "À quel groupe appartient le verbe « finir » ?",
                        ["Premier groupe", "Deuxième groupe", "Troisième groupe"],
                        1,
                    ),
                    (
                        "À quel groupe appartient le verbe « chanter » ?",
                        ["Premier groupe", "Deuxième groupe", "Troisième groupe"],
                        0,
                    ),
                    (
                        "À quel groupe appartient le verbe « prendre » ?",
                        ["Premier groupe", "Deuxième groupe", "Troisième groupe"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_FR_CONJUGAISON,
                [
                    (
                        "« Nous … à l'école tous les matins. » Quelle forme "
                        "convient ?",
                        ["allons", "allez", "vont"],
                        0,
                    ),
                    (
                        "« Tu … tes devoirs avant le dîner. » Quelle forme "
                        "convient ?",
                        ["fais", "fait", "faisons"],
                        0,
                    ),
                    (
                        "« Elles … dans la cour à midi. » Quelle forme convient ?",
                        ["joue", "joues", "jouent"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_FR_TEXTE,
                [
                    (
                        "« La pluie tombait depuis trois jours. La rivière "
                        "montait. » Que risque-t-il d'arriver ?",
                        ["Une sécheresse", "Une inondation", "Un incendie"],
                        1,
                    ),
                    (
                        "« Le ciel est tout noir et le tonnerre gronde. » Que "
                        "va-t-il probablement se passer ?",
                        [
                            "Un orage",
                            "Une belle journée ensoleillée",
                            "Une chute de neige",
                        ],
                        0,
                    ),
                    (
                        "« Amina a mal au ventre depuis ce matin et n'a pas "
                        "d'appétit. » Que devrait-elle faire ?",
                        [
                            "Aller courir",
                            "Voir un médecin",
                            "Manger un gros repas",
                        ],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_MA_NOMBRES,
                [
                    ("Quel nombre est le plus grand ?", ["405", "450", "98"], 1),
                    ("Quel nombre est le plus petit ?", ["720", "270", "702"], 1),
                    (
                        "Comment écrit-on 350 en toutes lettres ?",
                        [
                            "Trois cent cinquante",
                            "Cinq cent trente",
                            "Trois cent quinze",
                        ],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_MA_MULTIPLICATION,
                [
                    ("Combien font 7 × 8 ?", ["48", "56", "64"], 1),
                    ("Combien font 6 × 9 ?", ["45", "54", "63"], 1),
                    ("Combien font 4 × 7 ?", ["24", "28", "32"], 1),
                ],
            ),
            *_q3(
                ref.CE2_MA_MESURES,
                [
                    (
                        "Combien de centimètres y a-t-il dans un mètre ?",
                        ["10", "100", "1000"],
                        1,
                    ),
                    (
                        "Combien de minutes y a-t-il dans une heure ?",
                        ["30", "60", "100"],
                        1,
                    ),
                    (
                        "Combien de jours compte le mois de février une année "
                        "normale ?",
                        ["28", "29", "30"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_AN_PHRASES,
                [
                    (
                        "« The cat is on the table. » Où est le chat ?",
                        ["Sur la table", "Sous la table", "Dans la boîte"],
                        0,
                    ),
                    (
                        "« I have a red bag. » De quelle couleur est le sac ?",
                        ["Bleu", "Rouge", "Vert"],
                        1,
                    ),
                    (
                        "« She is my sister. » Que veut dire cette phrase ?",
                        ["C'est mon frère", "C'est ma sœur", "C'est ma mère"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_AN_QUESTIONS,
                [
                    (
                        "Comment demande-t-on l'âge de quelqu'un en anglais ?",
                        [
                            "How old are you?",
                            "What is your name?",
                            "Where do you live?",
                        ],
                        0,
                    ),
                    (
                        "« Where do you live? » Que demande-t-on ?",
                        ["Le nom", "L'âge", "Le lieu où l'on habite"],
                        2,
                    ),
                    (
                        "Comment répond-on à « How old are you? » quand on a huit "
                        "ans ?",
                        ["I am eight", "I am fine", "My name is eight"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CE2_AN_JOURS,
                [
                    (
                        "Comment dit-on « lundi » en anglais ?",
                        ["Sunday", "Monday", "Tuesday"],
                        1,
                    ),
                    (
                        "Quel jour anglais est « Friday » ?",
                        ["Mercredi", "Jeudi", "Vendredi"],
                        2,
                    ),
                    (
                        "Comment dit-on « janvier » en anglais ?",
                        ["June", "January", "July"],
                        1,
                    ),
                ],
            ),
        ],
    },
    {
        "level": ref.CM1,
        "title": TITLE,
        "minutes": 28,
        "questions": [
            *_q3(
                ref.CM1_FR_NATURE,
                [
                    (
                        "Lequel de ces mots est un adjectif ?",
                        ["Chien", "Rapide", "Courir"],
                        1,
                    ),
                    (
                        "Lequel de ces mots est un verbe ?",
                        ["Table", "Chanter", "Joli"],
                        1,
                    ),
                    ("Lequel de ces mots est un nom ?", ["Grand", "Maison", "Vite"], 1),
                ],
            ),
            *_q3(
                ref.CM1_FR_TEMPS,
                [
                    (
                        "« Demain, nous irons au marché. » De quel moment "
                        "parle-t-on ?",
                        ["Du passé", "Du futur", "Du présent"],
                        1,
                    ),
                    (
                        "« Hier, il a plu toute la journée. » De quel moment "
                        "parle-t-on ?",
                        ["Du passé", "Du futur", "Du présent"],
                        0,
                    ),
                    (
                        "« En ce moment, je lis un livre. » De quel moment "
                        "parle-t-on ?",
                        ["Du passé", "Du futur", "Du présent"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CM1_FR_ESSENTIEL,
                [
                    (
                        "« Amadou se lève tôt, prépare son sac et part à pied. Il "
                        "arrive à l'heure. » De quoi ce texte parle-t-il ?",
                        [
                            "D'un départ pour l'école",
                            "D'un repas de fête",
                            "D'un voyage en car",
                        ],
                        0,
                    ),
                    (
                        "« Fatou arrose ses fleurs chaque matin. Elles poussent "
                        "bien et sentent bon. » De quoi parle ce texte ?",
                        [
                            "D'un jardin entretenu",
                            "D'une tempête",
                            "D'un repas de fête",
                        ],
                        0,
                    ),
                    (
                        "« Les élèves rangent leurs affaires et sortent en "
                        "silence après la sonnerie. » Que décrit ce texte ?",
                        ["La fin de la classe", "Le début du sport", "Un anniversaire"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CM1_MA_FRACTIONS,
                [
                    ("Quelle fraction est la plus grande ?", ["1/4", "1/2", "1/8"], 1),
                    (
                        "Quelle fraction représente la moitié d'un tout ?",
                        ["1/3", "1/2", "1/4"],
                        1,
                    ),
                    ("Quelle fraction est la plus petite ?", ["1/2", "1/5", "1/3"], 1),
                ],
            ),
            *_q3(
                ref.CM1_MA_DIVISION,
                [
                    ("Combien font 56 ÷ 7 ?", ["6", "8", "9"], 1),
                    ("Combien font 63 ÷ 9 ?", ["6", "7", "8"], 1),
                    ("Combien font 45 ÷ 5 ?", ["8", "9", "10"], 1),
                ],
            ),
            *_q3(
                ref.CM1_MA_PROBLEME2,
                [
                    (
                        "Awa achète 3 cahiers à 200 francs l'un. Elle paie avec un "
                        "billet de 1000 francs. Combien lui rend-on ?",
                        ["300", "400", "600"],
                        1,
                    ),
                    (
                        "Un panier contient 4 sachets de 6 oranges. On en vend 10. "
                        "Combien en reste-t-il ?",
                        ["12", "14", "16"],
                        1,
                    ),
                    (
                        "Moussa a 500 francs. Il achète 2 crayons à 75 francs "
                        "chacun. Combien lui reste-t-il ?",
                        ["325", "350", "375"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM1_AN_ETRE_AVOIR,
                [
                    (
                        "« I … a book. » Quelle forme convient ?",
                        ["am", "have", "is"],
                        1,
                    ),
                    (
                        "« She … happy today. » Quelle forme convient ?",
                        ["is", "are", "have"],
                        0,
                    ),
                    (
                        "« They … two dogs. » Quelle forme convient ?",
                        ["has", "have", "is"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM1_AN_PLURIEL,
                [
                    (
                        "Quel est le pluriel de « cat » en anglais ?",
                        ["Cats", "Cates", "Catss"],
                        0,
                    ),
                    (
                        "Quel est le pluriel de « book » en anglais ?",
                        ["Bookes", "Books", "Boox"],
                        1,
                    ),
                    (
                        "Quel est le pluriel de « box » en anglais ?",
                        ["Boxs", "Box", "Boxes"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CM1_AN_QUOTIDIEN,
                [
                    (
                        "Comment dit-on « école » en anglais ?",
                        ["Home", "School", "Shop"],
                        1,
                    ),
                    (
                        "Comment dit-on « manger » en anglais ?",
                        ["Eat", "Sleep", "Play"],
                        0,
                    ),
                    (
                        "Comment dit-on « maison » en anglais ?",
                        ["School", "House", "Street"],
                        1,
                    ),
                ],
            ),
        ],
    },
    {
        "level": ref.CM2,
        "title": TITLE,
        "minutes": 32,
        "questions": [
            *_q3(
                ref.CM2_FR_ACCORDS,
                [
                    (
                        "« Les fleurs que j'ai … sont belles. » Quelle forme "
                        "convient ?",
                        ["cueilli", "cueillies", "cueillis"],
                        1,
                    ),
                    (
                        "« La maison qu'il a … est grande. » Quelle forme "
                        "convient ?",
                        ["construit", "construite", "construits"],
                        1,
                    ),
                    (
                        "« Les lettres qu'elle a … sont arrivées. » Quelle forme "
                        "convient ?",
                        ["envoyé", "envoyés", "envoyées"],
                        2,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_FR_COMPOSES,
                [
                    (
                        "« Hier, j'… mon travail avant le dîner. » Quelle forme "
                        "convient ?",
                        ["ai fini", "finis", "finirai"],
                        0,
                    ),
                    (
                        "« Quand nous sommes arrivés, ils … déjà partis. » "
                        "Quelle forme convient ?",
                        ["étaient", "seront", "sont"],
                        0,
                    ),
                    (
                        "« Elle … à Dakar avant de venir ici. » Quelle forme "
                        "convient ?",
                        ["vivra", "a vécu", "vit"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_FR_REDACTION,
                [
                    (
                        "Quelle phrase enchaîne le mieux après « Il pleuvait très "
                        "fort » ?",
                        [
                            "Pourtant, nous sommes sortis.",
                            "Le chat mange une souris.",
                            "Trois plus quatre font sept.",
                        ],
                        0,
                    ),
                    (
                        "Quelle phrase enchaîne le mieux après « Le match allait "
                        "commencer » ?",
                        [
                            "Les joueurs sont entrés sur le terrain.",
                            "La soupe était trop salée.",
                            "Il a plu la semaine dernière.",
                        ],
                        0,
                    ),
                    (
                        "Quel connecteur relie logiquement « Il a bien révisé » "
                        "et « il a réussi son examen » ?",
                        ["donc", "cependant", "ailleurs"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_MA_DECIMAUX,
                [
                    ("Quel nombre est le plus grand ?", ["0,9", "0,25", "0,7"], 0),
                    ("Combien font 2,5 + 1,3 ?", ["3,7", "3,8", "3,9"], 1),
                    ("Quel nombre est le plus petit ?", ["1,4", "1,04", "1,44"], 1),
                ],
            ),
            *_q3(
                ref.CM2_MA_PROPORTION,
                [
                    (
                        "Trois cahiers coûtent 600 francs. Combien coûtent cinq "
                        "cahiers ?",
                        ["800", "1000", "1200"],
                        1,
                    ),
                    (
                        "Quatre stylos coûtent 400 francs. Combien coûtent six "
                        "stylos ?",
                        ["500", "600", "700"],
                        1,
                    ),
                    (
                        "Deux kilos de riz coûtent 1000 francs. Combien coûtent "
                        "cinq kilos ?",
                        ["2000", "2500", "3000"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_MA_GEOMETRIE,
                [
                    (
                        "Quel est le périmètre d'un carré de 5 cm de côté ?",
                        ["10 cm", "20 cm", "25 cm"],
                        1,
                    ),
                    (
                        "Quelle est l'aire d'un rectangle de 4 cm sur 3 cm ?",
                        ["7 cm²", "12 cm²", "14 cm²"],
                        1,
                    ),
                    (
                        "Quel est le périmètre d'un rectangle de 6 cm sur 2 cm ?",
                        ["12 cm", "16 cm", "8 cm"],
                        0,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_AN_TEXTE,
                [
                    (
                        "« Tom wakes up at seven. He eats breakfast and goes to "
                        "school. » À quelle heure Tom se réveille-t-il ?",
                        ["À six heures", "À sept heures", "À huit heures"],
                        1,
                    ),
                    (
                        "« Tom wakes up at seven. He eats breakfast and goes to "
                        "school. » Que fait Tom après le petit-déjeuner ?",
                        ["Il dort", "Il va à l'école", "Il joue au ballon"],
                        1,
                    ),
                    (
                        "« My sister likes cats but she does not like dogs. » "
                        "Qu'aime la sœur ?",
                        ["Les chiens", "Les chats", "Les oiseaux"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_AN_PRESENT,
                [
                    (
                        "« He … football every Sunday. » Quelle forme convient ?",
                        ["play", "plays", "playing"],
                        1,
                    ),
                    (
                        "« I … to school every day. » Quelle forme convient ?",
                        ["go", "goes", "going"],
                        0,
                    ),
                    (
                        "« She … her homework in the evening. » Quelle forme "
                        "convient ?",
                        ["do", "does", "doing"],
                        1,
                    ),
                ],
            ),
            *_q3(
                ref.CM2_AN_REDACTION,
                [
                    (
                        "Quelle phrase se traduit par « J'ai neuf ans » ?",
                        [
                            "I am nine years old.",
                            "I have nine years.",
                            "I am nine dogs.",
                        ],
                        0,
                    ),
                    (
                        "Quelle phrase se traduit par « J'habite à Dakar » ?",
                        ["I live in Dakar.", "I am Dakar.", "I go Dakar."],
                        0,
                    ),
                    (
                        "Quelle phrase se traduit par « Mon anniversaire est en "
                        "mai » ?",
                        [
                            "My birthday is in May.",
                            "My birthday have May.",
                            "I birthday May.",
                        ],
                        0,
                    ),
                ],
            ),
        ],
    },
]

EXAMS_BY_LEVEL: Final[dict[str, Exam]] = {exam["level"]: exam for exam in EXAMS}
