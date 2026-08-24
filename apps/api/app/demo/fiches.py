"""The twelve remediation sheets, written here rather than downloaded.

**Why they are not H5P.** Four reasons, and three of them are walls.

*The attribution does not exist anywhere else.* A repair owes a proof, and a
proof that cannot be tied to the competency it repairs proves nothing. No content
bank, however large, can supply a question that works on `cp-ma-denombrer` —
that code is ours. Without the tie, a reading spreads over every competency of
the activity, which is exactly the coarse attribution the project refuses.

*ADR-012 allows one library.* `H5P.TrueFalse` 1.8, enforced by a check
constraint on the packages table. Importing anything else means extending the
allow-list, a migration, an amended ADR, antivirus and licence verification —
the deliberate friction that decision asked for, and it should not be spent on a
demonstration.

*The content origin is not deployed.* On Render a disk belongs to one service, so
the isolated origin nginx serves from has nowhere to live. An imported sheet
would not play there. A sheet written here plays wherever the assessment plays,
which is everywhere.

*A repair has to teach.* A downloaded true-or-false question asks; it does not
explain. Each sheet here opens with what to remember and answers back after every
question, which is the whole difference between a repair and a second test.

**What a sheet is.** Three to seven minutes, one competency, a short lesson and
a bank of eight questions, four of which are drawn and served on any one
attempt (HORS-10, ADR-020) — a child who repeats a sheet is not shown the same
four in the same order every time. Each question carries the sentence a child
is told once she has answered — the same sentence whether she was right or
wrong, because a sheet explains what is true, it does not comment on her.

**Quinze fiches sur cinquante-quatre compétences.** Le référentiel couvre six
classes et trois matières ; douze de ces fiches couvrent celles que la première
version du produit avait écrites, du CI au CE1, en français et en
mathématiques. Trois de plus couvrent l'anglais du CI, ajouté par ADR-019 —
saluer, nommer une couleur, compter jusqu'à cinq — parce que le CI reste la
classe la plus fragile de tout le référentiel et qu'une nouvelle matière n'y
change rien. Les trente-neuf autres n'ont pas encore de réparation, et c'est un
manque connu et mesuré plutôt qu'un oubli : une lacune que la plateforme sait
nommer et ne sait pas réparer est pire qu'une lacune dont elle ne parle pas,
parce que le parent agit et il ne se passe rien. Un test épingle la couverture
actuelle et échoue si elle régresse en silence.

**What these sheets still cannot do.** Hear. The phonology sheet approximates
sounds by talking about written words, exactly as the assessment does, and it is
a compromise rather than a design. Audio is the first thing to add if any of this
is used outside a demonstration. Nor do they draw: counting is done on rows of
typed symbols, which works up to about ten and no further.
"""

from __future__ import annotations

from typing import Final, TypedDict

from app.demo.dataset import PREFIX
from app.demo.referentiel import (
    CE1_FR_DICTEE as FR_DICTEE,
)
from app.demo.referentiel import (
    CE1_FR_PHRASE as FR_COMPREHENSION,
)
from app.demo.referentiel import (
    CE1_MA_PROBLEME as MA_PROBLEME,
)
from app.demo.referentiel import (
    CE1_MA_SOUSTRACTION as MA_SOUSTRACTION,
)
from app.demo.referentiel import (
    CI_AN_COULEURS as AN_COULEURS,
)
from app.demo.referentiel import (
    CI_AN_NOMBRES5 as AN_NOMBRES5,
)
from app.demo.referentiel import (
    CI_AN_SALUTATIONS as AN_SALUTATIONS,
)
from app.demo.referentiel import (
    CI_FR_LETTRES as FR_LETTRES,
)
from app.demo.referentiel import (
    CI_MA_CHIFFRES as MA_LIRE,
)
from app.demo.referentiel import (
    CI_MA_DENOMBRER as MA_DENOMBRER,
)
from app.demo.referentiel import (
    CP_FR_MOTS as FR_MOTS,
)
from app.demo.referentiel import (
    CP_FR_PHONEMES as FR_PHONEMES,
)
from app.demo.referentiel import (
    CP_FR_SYLLABES as FR_SYLLABES,
)
from app.demo.referentiel import (
    CP_MA_ADDITION as MA_ADDITION,
)
from app.demo.referentiel import (
    CP_MA_RANGER as MA_COMPARER,
)


class SheetQuestion(TypedDict):
    ref: str
    prompt: str
    choices: list[str]
    correct: int
    explanation: str


class Sheet(TypedDict):
    code: str
    title: str
    competency: str
    minutes: int
    guidance: str
    questions: list[SheetQuestion]


FICHES: Final[list[Sheet]] = [
    # ── Français ────────────────────────────────────────────────────────────
    {
        "code": f"{PREFIX}fix-fr-lettres",
        "title": "L’alphabet et ses sons",
        "competency": FR_LETTRES,
        "minutes": 5,
        "guidance": (
            "Une lettre a un nom et un son, et ce ne sont pas la même chose. "
            "La lettre S se nomme « esse », mais dans un mot elle fait « sss » : "
            "sac, soleil. C’est le son qui sert à lire.\n\n"
            "Certains sons peuvent s’étirer aussi longtemps qu’on a du souffle : "
            "M fait « mmmm », L fait « llll », F fait « ffff », R fait « rrrr ». "
            "D’autres s’arrêtent net et ne durent pas : P, T, K, B, D.\n\n"
            "Quand tu hésites sur une lettre, essaie de tenir son son. Si tu peux "
            "le tenir, tu sais déjà dans quel groupe elle est."
        ),
        "questions": [
            {
                "ref": "f-lettres-1",
                "prompt": "Quelle lettre se nomme « esse » ?",
                "choices": ["S", "C", "Z"],
                "correct": 0,
                "explanation": (
                    "On dit « esse » pour la nommer, mais dans un mot elle fait "
                    "« sss ». Le C et le Z portent d’autres noms : « cé » et « zède »."
                ),
            },
            {
                "ref": "f-lettres-2",
                "prompt": "Quelle lettre vient juste après le M dans l’alphabet ?",
                "choices": ["L", "N", "O"],
                "correct": 1,
                "explanation": (
                    "L’ordre est K, L, M, N, O, P. Le L vient juste avant le M, "
                    "et le O vient une place plus loin."
                ),
            },
            {
                "ref": "f-lettres-3",
                "prompt": "Quelle lettre fait un son que l’on peut tenir longtemps ?",
                "choices": ["P", "F", "T"],
                "correct": 1,
                "explanation": (
                    "Le F fait « ffff » et dure tant qu’on souffle. Le P et le T "
                    "s’arrêtent net : impossible de les faire durer."
                ),
            },
            {
                "ref": "f-lettres-4",
                "prompt": "Combien de lettres différentes y a-t-il dans « papa » ?",
                "choices": ["Deux", "Trois", "Quatre"],
                "correct": 0,
                "explanation": (
                    "Quatre lettres sont écrites, mais seulement deux sont "
                    "différentes : le p et le a, chacun écrit deux fois."
                ),
            },
            {
                "ref": "f-lettres-5",
                "prompt": "Quelle lettre est ronde comme un ballon ?",
                "choices": ["O", "T", "L"],
                "correct": 0,
                "explanation": (
                    "Le O se trace comme un cercle. Le T et le L sont faits de "
                    "traits droits, sans rondeur."
                ),
            },
            {
                "ref": "f-lettres-6",
                "prompt": "Quelle lettre vient juste avant le G dans l’alphabet ?",
                "choices": ["F", "H", "E"],
                "correct": 0,
                "explanation": (
                    "L’ordre est E, F, G, H. Le F précède directement le G ; le "
                    "H et le E sont plus loin."
                ),
            },
            {
                "ref": "f-lettres-7",
                "prompt": "Combien de lettres différentes y a-t-il dans « lili » ?",
                "choices": ["Une", "Deux", "Quatre"],
                "correct": 1,
                "explanation": (
                    "Quatre lettres sont écrites, mais seulement deux sont "
                    "différentes : le l et le i, chacun répété deux fois."
                ),
            },
            {
                "ref": "f-lettres-8",
                "prompt": (
                    "Quelle lettre fait un son qui s’arrête net, sans pouvoir "
                    "durer ?"
                ),
                "choices": ["S", "P", "V"],
                "correct": 1,
                "explanation": (
                    "Le P s’arrête net dès qu’on le prononce. Le S et le V, "
                    "eux, peuvent s’étirer aussi longtemps qu’on a du souffle."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-fr-syllabes",
        "title": "Frapper les syllabes",
        "competency": FR_SYLLABES,
        "minutes": 4,
        "guidance": (
            "Une syllabe, c’est ce qu’on dit d’un seul coup de voix. Pour les "
            "compter, frappe dans tes mains en disant le mot lentement : "
            "cho-co-lat, trois frappes. Bou-teille, deux frappes.\n\n"
            "Le piège est toujours le même : on compte ce qu’on entend, pas les "
            "lettres. « Fleur » s’écrit avec cinq lettres et ne fait qu’une seule "
            "frappe.\n\n"
            "Si tu n’arrives pas à découper, dis le mot en le chantant. Les "
            "syllabes se séparent toutes seules."
        ),
        "questions": [
            {
                "ref": "f-syllabes-1",
                "prompt": "Combien de syllabes entends-tu dans « ordinateur » ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 1,
                "explanation": (
                    "or-di-na-teur : quatre coups de voix. C’est un mot long, "
                    "mais chaque frappe reste courte."
                ),
            },
            {
                "ref": "f-syllabes-2",
                "prompt": "Quel mot se dit d’un seul coup de voix ?",
                "choices": ["Souris", "Pluie", "Lapin"],
                "correct": 1,
                "explanation": (
                    "« Pluie » se dit d’un coup. Sou-ris et la-pin en demandent "
                    "deux chacun."
                ),
            },
            {
                "ref": "f-syllabes-3",
                "prompt": "Quel mot a le plus de syllabes ?",
                "choices": ["Éléphant", "Girafe", "Chat"],
                "correct": 0,
                "explanation": (
                    "é-lé-phant fait trois frappes, gi-rafe en fait deux, et le "
                    "dernier une seule. Le mot le plus long à écrire est ici "
                    "aussi le plus long à dire, mais ce n’est pas toujours vrai."
                ),
            },
            {
                "ref": "f-syllabes-4",
                "prompt": "« Chat » s’écrit avec quatre lettres. Combien de syllabes ?",
                "choices": ["Une", "Deux", "Quatre"],
                "correct": 0,
                "explanation": (
                    "Une seule : on le dit d’un coup. Les lettres et les syllabes "
                    "ne se comptent jamais ensemble."
                ),
            },
            {
                "ref": "f-syllabes-5",
                "prompt": "Combien de syllabes y a-t-il dans « escargot » ?",
                "choices": ["Deux", "Trois", "Quatre"],
                "correct": 1,
                "explanation": (
                    "es-car-got : trois frappes. On entend bien trois coups de "
                    "voix, même si le mot paraît long à l’écrit."
                ),
            },
            {
                "ref": "f-syllabes-6",
                "prompt": "Quel mot se dit en deux coups de voix ?",
                "choices": ["Vélo", "Ananas", "Fourmi"],
                "correct": 0,
                "explanation": (
                    "Vé-lo se dit en deux frappes. A-na-nas et four-mi en "
                    "demandent trois chacun."
                ),
            },
            {
                "ref": "f-syllabes-7",
                "prompt": "Quel mot a le moins de syllabes ?",
                "choices": ["Ordinateur", "Chat", "Bicyclette"],
                "correct": 1,
                "explanation": (
                    "Chat se dit d’un seul coup. Les deux autres mots se "
                    "découpent chacun en plusieurs frappes."
                ),
            },
            {
                "ref": "f-syllabes-8",
                "prompt": "« Tomate » s’écrit avec six lettres. Combien de syllabes ?",
                "choices": ["Deux", "Trois", "Six"],
                "correct": 1,
                "explanation": (
                    "to-ma-te : trois frappes. Les lettres et les syllabes ne "
                    "se comptent jamais ensemble."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-fr-phonemes",
        "title": "Chasse aux sons",
        "competency": FR_PHONEMES,
        "minutes": 5,
        "guidance": (
            "Un phonème, c’est le plus petit son d’un mot. « Loup » a deux sons : "
            "« lll » puis « ou » — pourtant il s’écrit avec quatre lettres.\n\n"
            "C’est que plusieurs lettres peuvent se mettre ensemble pour faire un "
            "seul son : ou, on, an, in, oi, ch. Chacun de ces groupes compte pour "
            "un.\n\n"
            "Et le même son peut s’écrire de plusieurs façons. Le son « fff » "
            "s’écrit f dans fusée et ph dans photo : deux orthographes, un seul "
            "son."
        ),
        "questions": [
            {
                "ref": "f-phonemes-1",
                "prompt": "Combien de sons différents entends-tu dans « chat » ?",
                "choices": ["Deux", "Trois", "Quatre"],
                "correct": 0,
                "explanation": (
                    "« ch » puis « a » : deux sons. Les quatre lettres se "
                    "regroupent, elles ne se comptent pas une par une."
                ),
            },
            {
                "ref": "f-phonemes-2",
                "prompt": "Quel mot contient le son « on », comme dans « pont » ?",
                "choices": ["Bonbon", "Banane", "Bateau"],
                "correct": 0,
                "explanation": (
                    "Bon-bon : le son y est deux fois. Dans banane on entend "
                    "« an », qui est un son voisin mais différent."
                ),
            },
            {
                "ref": "f-phonemes-3",
                "prompt": "Quel mot commence par le même son que « fenêtre » ?",
                "choices": ["Photo", "Vélo", "Bateau"],
                "correct": 0,
                "explanation": (
                    "« Photo » commence par le son « fff », écrit ph. Le son "
                    "compte, pas la façon dont on l’écrit."
                ),
            },
            {
                "ref": "f-phonemes-4",
                "prompt": "Quel mot se termine par le même son que « bateau » ?",
                "choices": ["Cadeau", "Fenêtre", "Maison"],
                "correct": 0,
                "explanation": (
                    "Il finit par le son « o », écrit eau. Les deux autres "
                    "finissent sur des sons différents, même si l’un d’eux "
                    "s’écrit aussi avec un e à la fin."
                ),
            },
            {
                "ref": "f-phonemes-5",
                "prompt": "Combien de sons différents entends-tu dans « feu » ?",
                "choices": ["Un", "Deux", "Trois"],
                "correct": 1,
                "explanation": (
                    "« fff » puis « eu » : deux sons pour trois lettres. Un "
                    "groupe de lettres peut faire un seul son."
                ),
            },
            {
                "ref": "f-phonemes-6",
                "prompt": "Quel mot contient le son « in », comme dans « lapin » ?",
                "choices": ["Matin", "Maison", "Melon"],
                "correct": 0,
                "explanation": (
                    "Ma-tin contient le son « in ». Les deux autres mots ont "
                    "des sons de fin différents."
                ),
            },
            {
                "ref": "f-phonemes-7",
                "prompt": "Quel mot commence par le même son que « genou » ?",
                "choices": ["Girafe", "Chameau", "Renard"],
                "correct": 0,
                "explanation": (
                    "« Genou » et « girafe » commencent tous deux par le son "
                    "« jjj ». Chameau et renard commencent par des sons "
                    "différents."
                ),
            },
            {
                "ref": "f-phonemes-8",
                "prompt": "Quel mot se termine par le même son que « manteau » ?",
                "choices": ["Chapeau", "Ballon", "Maison"],
                "correct": 0,
                "explanation": (
                    "Les deux mots finissent par le son « o », même si l’un "
                    "s’écrit -eau. Les deux autres se terminent par des sons "
                    "différents."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-fr-mots",
        "title": "Lire des mots courts",
        "competency": FR_MOTS,
        "minutes": 6,
        "guidance": (
            "Pour lire un mot inconnu, découpe-le en syllabes et assemble : "
            "mar-teau, marteau. Ne devine pas d’après la première lettre.\n\n"
            "Il y a des lettres qu’on écrit sans les dire : le s du pluriel dans "
            "« les chats », le e à la fin de « porte », le d de « grand ». On les "
            "appelle des lettres muettes. Pour les retrouver, cherche un mot de la "
            "même famille : grand devient grande, et là le d s’entend.\n\n"
            "Une règle qui sert tout le temps : entre deux voyelles, un seul s se "
            "lit « zzz », et deux s se lisent « sss »."
        ),
        "questions": [
            {
                "ref": "f-mots-1",
                "prompt": "Quel mot est écrit correctement ?",
                "choices": ["oizeau", "oiseau", "oisseau"],
                "correct": 1,
                "explanation": (
                    "Un seul s entre deux voyelles suffit pour le son « zzz ». "
                    "Deux s auraient donné « sss »."
                ),
            },
            {
                "ref": "f-mots-2",
                "prompt": "Dans « petit », quelle lettre ne s’entend pas ?",
                "choices": ["Le p", "Le t de la fin", "Le i"],
                "correct": 1,
                "explanation": (
                    "On dit « peti ». La lettre revient au féminin, dans petite, "
                    "et c’est là qu’on l’entend."
                ),
            },
            {
                "ref": "f-mots-3",
                "prompt": "Quel mot se lit avec le son « sss » ?",
                "choices": ["Poison", "Poisson", "Maison"],
                "correct": 1,
                "explanation": (
                    "Deux s font « sss ». Un seul s entre deux voyelles fait "
                    "« zzz », et c’est ce qui sépare ces deux mots-là."
                ),
            },
            {
                "ref": "f-mots-4",
                "prompt": "Combien de mots y a-t-il dans « il y a un chat » ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 2,
                "explanation": (
                    "il / y / a / un / chat. Les petits mots comptent autant que "
                    "les grands : ce sont les espaces qui les séparent."
                ),
            },
            {
                "ref": "f-mots-5",
                "prompt": "Quel mot est écrit correctement ?",
                "choices": ["bato", "bateau", "batau"],
                "correct": 1,
                "explanation": (
                    "Le son « o » s’écrit ici -eau, comme dans château. Les "
                    "deux autres orthographes ne correspondent à aucune "
                    "écriture correcte du mot."
                ),
            },
            {
                "ref": "f-mots-6",
                "prompt": "Dans « grand », quelle lettre ne s’entend pas ?",
                "choices": ["Le g", "Le d de la fin", "Le r"],
                "correct": 1,
                "explanation": (
                    "On dit « gran ». Le d revient au féminin, dans grande, et "
                    "c’est là qu’on l’entend enfin."
                ),
            },
            {
                "ref": "f-mots-7",
                "prompt": "Quel mot se lit avec le son « zzz » ?",
                "choices": ["Chasse", "Case", "Tasse"],
                "correct": 1,
                "explanation": (
                    "Un seul s entre deux voyelles se lit « zzz ». Les deux "
                    "autres mots ont deux s, qui se lisent « sss »."
                ),
            },
            {
                "ref": "f-mots-8",
                "prompt": "Combien de mots y a-t-il dans « le chat dort là » ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 1,
                "explanation": (
                    "le / chat / dort / là. Quatre mots séparés par des "
                    "espaces, même si certains sont très courts."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-fr-dictee",
        "title": "Écrire des mots simples",
        "competency": FR_DICTEE,
        "minutes": 6,
        "guidance": (
            "Avant de rendre une phrase dictée, vérifie trois choses, toujours "
            "dans cet ordre.\n\n"
            "1. La majuscule au début et le point à la fin.\n"
            "2. Le pluriel : si on peut dire « plusieurs », le nom prend un s — "
            "et le verbe prend -nt. Les chats dorment : les deux marques vont "
            "ensemble.\n"
            "3. Ce qui accompagne le nom : une petite fille, un petit garçon. "
            "L’adjectif s’accorde avec le nom, pas avec le mot d’à côté.\n\n"
            "Ces trois vérifications rattrapent la plupart des erreurs, et elles "
            "prennent moins de temps que de tout relire."
        ),
        "questions": [
            {
                "ref": "f-dictee-1",
                "prompt": "Quelle phrase est écrite correctement ?",
                "choices": [
                    "Les oiseau chantent.",
                    "Les oiseaux chante.",
                    "Les oiseaux chantent.",
                ],
                "correct": 2,
                "explanation": (
                    "Ils sont plusieurs, donc le nom prend sa marque et le verbe "
                    "la sienne. Les deux manquent rarement ensemble : c’est "
                    "presque toujours l’une des deux qu’on oublie."
                ),
            },
            {
                "ref": "f-dictee-2",
                "prompt": "Quel groupe de mots est correct ?",
                "choices": [
                    "une grand maison",
                    "une grande maison",
                    "un grande maison",
                ],
                "correct": 1,
                "explanation": (
                    "Maison est un nom féminin. Ce qui l’accompagne se met au "
                    "féminin aussi, du début à la fin du groupe."
                ),
            },
            {
                "ref": "f-dictee-3",
                "prompt": "Que manque-t-il à cette phrase : « le chien dort » ?",
                "choices": ["Une majuscule et un point", "Rien du tout", "Un s"],
                "correct": 0,
                "explanation": (
                    "Une phrase commence par une majuscule et se termine par un "
                    "point. Il n’y a qu’un seul chien, donc aucun s à ajouter."
                ),
            },
            {
                "ref": "f-dictee-4",
                "prompt": "Comment s’écrit le pluriel de « un cheval » ?",
                "choices": ["des chevals", "des chevaux", "des chevaus"],
                "correct": 1,
                "explanation": (
                    "Les mots en -al changent de fin au pluriel : un journal, "
                    "des journaux ; un animal, des animaux. Le s ordinaire ne "
                    "convient pas."
                ),
            },
            {
                "ref": "f-dictee-5",
                "prompt": "Quelle phrase est écrite correctement ?",
                "choices": [
                    "Les filles chante.",
                    "Les filles chantent.",
                    "Les fille chantent.",
                ],
                "correct": 1,
                "explanation": (
                    "Elles sont plusieurs : le nom et le verbe prennent chacun "
                    "leur marque de pluriel, jamais un seul des deux."
                ),
            },
            {
                "ref": "f-dictee-6",
                "prompt": "Quel groupe de mots est correct ?",
                "choices": ["un petite chat", "un petit chat", "une petit chat"],
                "correct": 1,
                "explanation": (
                    "Chat est un nom masculin. Ce qui l’accompagne reste au "
                    "masculin tout du long."
                ),
            },
            {
                "ref": "f-dictee-7",
                "prompt": "Que manque-t-il à cette phrase : « les enfants jouent » ?",
                "choices": [
                    "Une majuscule et un point",
                    "Un s au verbe",
                    "Rien du tout",
                ],
                "correct": 0,
                "explanation": (
                    "Une phrase commence par une majuscule et se termine par un "
                    "point. Le verbe est déjà bien accordé au pluriel."
                ),
            },
            {
                "ref": "f-dictee-8",
                "prompt": "Comment s’écrit le pluriel de « un journal » ?",
                "choices": ["des journals", "des journaux", "des journeaux"],
                "correct": 1,
                "explanation": (
                    "Les mots en -al changent de fin au pluriel, comme cheval "
                    "et chevaux. Le s ordinaire ne convient pas ici non plus."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-fr-comprehension",
        "title": "Comprendre une petite histoire",
        "competency": FR_COMPREHENSION,
        "minutes": 7,
        "guidance": (
            "Comprendre un texte, ce n’est pas retenir les mots. C’est savoir qui "
            "fait quoi, où, et pourquoi.\n\n"
            "Souvent la réponse n’est pas écrite : il faut la deviner à partir "
            "d’un indice. Si on lit « Léa met ses bottes et son manteau », "
            "personne n’a écrit qu’il pleut — mais les bottes le disent.\n\n"
            "Quand tu ne trouves pas, relis la phrase juste avant. C’est presque "
            "toujours là que se trouve l’indice."
        ),
        "questions": [
            {
                "ref": "f-comprehension-1",
                "prompt": (
                    "« Tom pose son cartable, sort son cahier et taille son "
                    "crayon. » Où est Tom ?"
                ),
                "choices": ["À la piscine", "En classe", "Au marché"],
                "correct": 1,
                "explanation": (
                    "Le texte ne le dit nulle part. Le cartable, le cahier et le "
                    "crayon le disent à sa place : trois indices qui vont ensemble."
                ),
            },
            {
                "ref": "f-comprehension-2",
                "prompt": (
                    "« Léa court vers la cuisine. Le gâteau sent le brûlé. » "
                    "Pourquoi court-elle ?"
                ),
                "choices": ["Elle a faim", "Le gâteau brûle", "Elle joue"],
                "correct": 1,
                "explanation": (
                    "L’odeur est l’indice, et elle explique la course. Léa ne "
                    "court pas pour manger : elle court pour arriver à temps."
                ),
            },
            {
                "ref": "f-comprehension-3",
                "prompt": "« Le chat de Léa dort sur le lit de Tom. » À qui est le chat ?",
                "choices": ["À Léa", "À Tom", "Aux deux"],
                "correct": 0,
                "explanation": (
                    "Le petit mot « de » dit à qui appartient chaque chose. Il "
                    "apparaît deux fois dans la phrase, et il ne désigne pas la "
                    "même personne les deux fois."
                ),
            },
            {
                "ref": "f-comprehension-4",
                "prompt": (
                    "« Il pleut depuis ce matin. Tom regarde par la fenêtre en "
                    "soupirant. » Que ressent Tom ?"
                ),
                "choices": ["De la déception", "De la peur", "De la colère"],
                "correct": 0,
                "explanation": (
                    "Soupirer devant la pluie, c’est regretter quelque chose qui "
                    "n’aura pas lieu. Le texte ne le dit pas : il le laisse "
                    "comprendre."
                ),
            },
            {
                "ref": "f-comprehension-5",
                "prompt": (
                    "« Awa enfile ses gants et son bonnet avant de sortir. » "
                    "Quel temps fait-il ?"
                ),
                "choices": ["Il fait froid", "Il fait chaud", "Il pleut des fleurs"],
                "correct": 0,
                "explanation": (
                    "Le texte ne le dit nulle part. Les gants et le bonnet le "
                    "disent à sa place, comme deux indices qui vont ensemble."
                ),
            },
            {
                "ref": "f-comprehension-6",
                "prompt": (
                    "« Le chien remue la queue et court vers la porte. » Que "
                    "va-t-il probablement se passer ?"
                ),
                "choices": ["Quelqu’un arrive", "Il va pleuvoir", "Le chien a faim"],
                "correct": 0,
                "explanation": (
                    "Un chien qui remue la queue vers la porte annonce presque "
                    "toujours une arrivée. Le texte ne le dit pas, il le laisse "
                    "deviner."
                ),
            },
            {
                "ref": "f-comprehension-7",
                "prompt": (
                    "« Le vélo de Léa est rouge, celui de Tom est bleu. » À qui "
                    "est le vélo bleu ?"
                ),
                "choices": ["À Léa", "À Tom", "Aux deux"],
                "correct": 1,
                "explanation": (
                    "La phrase associe chaque vélo à sa couleur, l’un après "
                    "l’autre. Celui de Tom est cité en second, avec sa couleur "
                    "juste après."
                ),
            },
            {
                "ref": "f-comprehension-8",
                "prompt": (
                    "« Moussa range ses jouets et éteint la lumière. » Que "
                    "va-t-il probablement faire ensuite ?"
                ),
                "choices": ["Se coucher", "Aller à l’école", "Manger un gâteau"],
                "correct": 0,
                "explanation": (
                    "Ranger ses jouets et éteindre la lumière sont les gestes "
                    "qui précèdent le coucher. Le texte ne le dit pas, il le "
                    "laisse comprendre."
                ),
            },
        ],
    },
    # ── Mathématiques ───────────────────────────────────────────────────────
    {
        "code": f"{PREFIX}fix-ma-denombrer",
        "title": "Compter une collection",
        "competency": MA_DENOMBRER,
        "minutes": 4,
        "guidance": (
            "Pour savoir combien il y a d’objets, on les compte un par un, sans "
            "en oublier ni en compter deux fois. Le truc : touche-les ou barre-les "
            "au fur et à mesure.\n\n"
            "Le dernier nombre que tu dis, c’est le total. Si tu dis « un, deux, "
            "trois, quatre », il y en a quatre en tout — pas seulement le "
            "quatrième.\n\n"
            "Quand il y en a beaucoup, fais des paquets de cinq et compte les "
            "paquets. C’est plus rapide et on se trompe moins."
        ),
        "questions": [
            {
                "ref": "f-denombrer-1",
                "prompt": "Combien y a-t-il de ronds ?   ● ● ● ● ● ●",
                "choices": ["Cinq", "Six", "Sept"],
                "correct": 1,
                "explanation": (
                    "En les touchant un par un, on n’en saute aucun et on ne "
                    "repasse pas deux fois sur le même."
                ),
            },
            {
                "ref": "f-denombrer-2",
                "prompt": (
                    "Tom compte des jetons un par un, puis s’arrête. Le dernier "
                    "nombre qu’il a dit répond-il à « combien y en a-t-il ? »"
                ),
                "choices": [
                    "Oui, c’est le total",
                    "Non, il faut tout recompter",
                    "Non, il faut encore ajouter un",
                ],
                "correct": 0,
                "explanation": (
                    "Le dernier nombre prononcé dit le total. C’est la règle qui "
                    "manque le plus souvent : on sait réciter la suite, mais on "
                    "ne sait pas encore que le dernier mot répond à la question."
                ),
            },
            {
                "ref": "f-denombrer-3",
                "prompt": "Combien d’étoiles en tout ?   ★★★★★   ★★★",
                "choices": ["Sept", "Huit", "Neuf"],
                "correct": 1,
                "explanation": (
                    "Cinq dans le premier paquet, puis on continue : six, sept, "
                    "huit. On ne recompte pas le paquet déjà compté."
                ),
            },
            {
                "ref": "f-denombrer-4",
                "prompt": (
                    "Il y a 4 billes dans une boîte fermée. On en ajoute 2. "
                    "Combien y en a-t-il ?"
                ),
                "choices": ["Cinq", "Six", "Sept"],
                "correct": 1,
                "explanation": (
                    "Pas besoin de rouvrir la boîte : on part de quatre et on "
                    "avance de deux. Compter à partir d’un nombre, sans "
                    "recommencer à un, fait gagner beaucoup de temps."
                ),
            },
            {
                "ref": "f-denombrer-5",
                "prompt": "Combien y a-t-il de triangles ?   ▲ ▲ ▲ ▲ ▲",
                "choices": ["Quatre", "Cinq", "Six"],
                "correct": 1,
                "explanation": (
                    "En touchant chaque triangle une seule fois, on arrive à "
                    "cinq. Ne pas en sauter ni en recompter un deux fois est la "
                    "règle qui compte le plus."
                ),
            },
            {
                "ref": "f-denombrer-6",
                "prompt": (
                    "Léa compte 7 jetons, puis en ajoute 1 sans les recompter. "
                    "Combien en a-t-elle ?"
                ),
                "choices": ["Sept", "Huit", "Neuf"],
                "correct": 1,
                "explanation": (
                    "On repart du nombre déjà connu, sept, et on avance d’un : "
                    "huit. Pas besoin de tout recompter depuis le début."
                ),
            },
            {
                "ref": "f-denombrer-7",
                "prompt": "Combien d’étoiles en tout ?   ★★★★★   ★★",
                "choices": ["Six", "Sept", "Huit"],
                "correct": 1,
                "explanation": (
                    "Cinq dans le premier paquet, puis on continue : six, "
                    "sept. Le second paquet ne se recompte pas depuis un."
                ),
            },
            {
                "ref": "f-denombrer-8",
                "prompt": (
                    "Il y a 3 billes dans une main fermée. On en ajoute 3 dans "
                    "l’autre main. Combien en a-t-on en tout ?"
                ),
                "choices": ["Cinq", "Six", "Sept"],
                "correct": 1,
                "explanation": (
                    "Pas besoin d’ouvrir les mains : trois et trois de plus "
                    "font six. Compter par groupes déjà connus va plus vite que "
                    "tout reprendre à un."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-ma-lire",
        "title": "Écrire les nombres jusqu’à 10",
        "competency": MA_LIRE,
        "minutes": 5,
        "guidance": (
            "Chaque nombre a trois habits : le chiffre (7), le mot (sept) et la "
            "quantité (●●●●●●●). Savoir passer de l’un à l’autre, c’est savoir "
            "lire un nombre.\n\n"
            "De zéro à dix : zéro, un, deux, trois, quatre, cinq, six, sept, "
            "huit, neuf, dix.\n\n"
            "Les chiffres qu’on confond le plus se ressemblent à l’envers : le 6 "
            "et le 9, le 2 et le 5. Quand tu hésites, compte sur tes doigts : "
            "c’est la quantité qui tranche, jamais la forme du trait."
        ),
        "questions": [
            {
                "ref": "f-lire-1",
                "prompt": "Quel nombre s’écrit « huit » ?",
                "choices": ["6", "8", "9"],
                "correct": 1,
                "explanation": (
                    "Il se trace en faisant deux ronds l’un sur l’autre. Le 6 et "
                    "le 9 n’ont qu’un seul rond, en haut ou en bas."
                ),
            },
            {
                "ref": "f-lire-2",
                "prompt": "Quel nombre vient juste après neuf ?",
                "choices": ["Huit", "Dix", "Onze"],
                "correct": 1,
                "explanation": (
                    "Huit vient juste avant neuf, et onze arrive une place plus "
                    "loin. Réciter la suite à voix haute est la façon la plus sûre "
                    "de vérifier."
                ),
            },
            {
                "ref": "f-lire-3",
                "prompt": "Combien font ●●●● et ●●● réunis ?",
                "choices": ["Six", "Sept", "Huit"],
                "correct": 1,
                "explanation": (
                    "Quatre, puis on continue : cinq, six, sept. Le résultat "
                    "s’écrit avec le chiffre 7."
                ),
            },
            {
                "ref": "f-lire-4",
                "prompt": "On écrit 0. Combien cela fait-il ?",
                "choices": ["Aucun", "Un", "Dix"],
                "correct": 0,
                "explanation": (
                    "Le zéro dit qu’il n’y a rien, et c’est quand même un nombre. "
                    "Il ne vaut dix que si un autre chiffre se tient devant lui."
                ),
            },
            {
                "ref": "f-lire-5",
                "prompt": "Quel chiffre s’écrit « cinq » ?",
                "choices": ["3", "5", "6"],
                "correct": 1,
                "explanation": (
                    "Il se trace avec une barre en haut et un ventre rond en "
                    "bas. Le 3 et le 6 ont une forme bien différente."
                ),
            },
            {
                "ref": "f-lire-6",
                "prompt": "Quel nombre vient juste avant sept ?",
                "choices": ["Cinq", "Six", "Huit"],
                "correct": 1,
                "explanation": (
                    "Six vient juste avant sept, et cinq vient encore une "
                    "place plus tôt. Réciter la suite à l’envers aide à "
                    "vérifier."
                ),
            },
            {
                "ref": "f-lire-7",
                "prompt": "Combien font ●●● et ●●●● réunis ?",
                "choices": ["Six", "Sept", "Huit"],
                "correct": 1,
                "explanation": (
                    "Trois, puis on continue : quatre, cinq, six, sept. Le "
                    "résultat s’écrit avec le chiffre 7."
                ),
            },
            {
                "ref": "f-lire-8",
                "prompt": "On écrit 1. Combien cela fait-il ?",
                "choices": ["Aucun", "Un", "Dix"],
                "correct": 1,
                "explanation": (
                    "Le chiffre 1 tout seul vaut un. Il ne vaut dix que placé "
                    "devant un zéro, comme dans 10."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-ma-comparer",
        "title": "Plus grand, plus petit",
        "competency": MA_COMPARER,
        "minutes": 5,
        "guidance": (
            "Comparer deux nombres, c’est dire lequel vient le plus loin quand on "
            "compte. Plus on compte longtemps pour l’atteindre, plus il est "
            "grand.\n\n"
            "Le piège est là : entre 0 et 20, un nombre à deux chiffres est "
            "toujours plus grand qu’un nombre à un chiffre, même si le chiffre "
            "seul paraît plus gros. Douze est plus grand que neuf.\n\n"
            "Pour ranger plusieurs nombres, cherche d’abord le plus petit et "
            "mets-le devant. Recommence avec ceux qui restent."
        ),
        "questions": [
            {
                "ref": "f-comparer-1",
                "prompt": "Quel nombre est le plus grand ?",
                "choices": ["9", "12", "7"],
                "correct": 1,
                "explanation": (
                    "Deux chiffres l’emportent toujours sur un seul, dans cette "
                    "plage. Le 9 paraît gros mais on l’atteint plus tôt en comptant."
                ),
            },
            {
                "ref": "f-comparer-2",
                "prompt": "Quel nombre est le plus petit ?",
                "choices": ["11", "8", "15"],
                "correct": 1,
                "explanation": (
                    "C’est celui qu’on atteint en premier quand on compte. Les "
                    "deux autres viennent après lui."
                ),
            },
            {
                "ref": "f-comparer-3",
                "prompt": "Quel nombre se trouve entre 6 et 8 ?",
                "choices": ["5", "7", "9"],
                "correct": 1,
                "explanation": (
                    "Il n’y en a qu’un seul entre les deux. Le 5 vient avant le 6, "
                    "et le 9 vient après le 8."
                ),
            },
            {
                "ref": "f-comparer-4",
                "prompt": "Les nombres 3, 10, 7 sont-ils rangés du plus petit au plus grand ?",
                "choices": [
                    "Oui, ils sont bien rangés",
                    "Non, le 7 devrait venir avant le 10",
                    "Non, le 3 devrait venir en dernier",
                ],
                "correct": 1,
                "explanation": (
                    "Bien rangés, ils feraient 3, 7, 10. Le plus petit est déjà à "
                    "sa place ; ce sont les deux autres qui sont inversés."
                ),
            },
            {
                "ref": "f-comparer-5",
                "prompt": "Quel nombre est le plus grand ?",
                "choices": ["14", "6", "10"],
                "correct": 0,
                "explanation": (
                    "Deux chiffres l’emportent sur un seul dans cette plage, "
                    "et entre deux nombres à deux chiffres, on compare le "
                    "premier chiffre : 14 devance 10."
                ),
            },
            {
                "ref": "f-comparer-6",
                "prompt": "Quel nombre est le plus petit ?",
                "choices": ["13", "4", "9"],
                "correct": 1,
                "explanation": (
                    "C’est celui qu’on atteint en premier en comptant à partir "
                    "de zéro. Les deux autres viennent bien après lui."
                ),
            },
            {
                "ref": "f-comparer-7",
                "prompt": "Quel nombre se trouve entre 12 et 14 ?",
                "choices": ["11", "13", "15"],
                "correct": 1,
                "explanation": (
                    "Il n’y en a qu’un seul entre les deux. Le 11 vient avant "
                    "12, et le 15 vient après 14."
                ),
            },
            {
                "ref": "f-comparer-8",
                "prompt": "Les nombres 8, 2, 5 sont-ils rangés du plus petit au plus grand ?",
                "choices": [
                    "Oui, ils sont bien rangés",
                    "Non, il faudrait commencer par 2",
                    "Non, il faudrait finir par 5",
                ],
                "correct": 1,
                "explanation": (
                    "Bien rangés, ils feraient 2, 5, 8. Le 2 est le plus petit "
                    "et devrait venir en premier, pas le 8."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-ma-addition",
        "title": "Additionner avec la bande numérique",
        "competency": MA_ADDITION,
        "minutes": 6,
        "guidance": (
            "Additionner, c’est avancer. Pour 8 + 5, pars de 8 et avance de cinq "
            "pas : 9, 10, 11, 12, 13.\n\n"
            "Plus rapide : passe par 10, qui est une marche facile. Pour 8 + 5, "
            "il faut 2 pour atteindre 10, et il reste 3 à ajouter — donc 13. "
            "Découper l’ajout en deux morceaux évite de compter longtemps.\n\n"
            "Et l’ordre ne change rien au résultat : commence toujours par le plus "
            "grand des deux, il y aura moins de pas à faire.\n\n"
            "Les doubles sont à connaître par cœur : 5+5, 6+6, 7+7. Ils servent "
            "partout, y compris pour ce qui les entoure."
        ),
        "questions": [
            {
                "ref": "f-addition-1",
                "prompt": "Combien font 8 + 6 ?",
                "choices": ["13", "14", "15"],
                "correct": 1,
                "explanation": (
                    "Deux pas pour atteindre dix, puis il en reste quatre. On peut "
                    "aussi avancer de six depuis huit et arriver au même endroit."
                ),
            },
            {
                "ref": "f-addition-2",
                "prompt": "Pour calculer 4 + 9, par quel nombre vaut-il mieux commencer ?",
                "choices": [
                    "Par le 4, c’est l’ordre écrit",
                    "Par le 9, il y a moins de pas à faire",
                    "Il faut d’abord passer par 10",
                ],
                "correct": 1,
                "explanation": (
                    "En partant du plus grand, il ne reste que quatre pas au lieu "
                    "de neuf. Le résultat est le même : c’est le chemin qui est "
                    "plus court."
                ),
            },
            {
                "ref": "f-addition-3",
                "prompt": "On sait que 7 + 3 fait 10. Combien font 7 + 4 ?",
                "choices": ["10", "11", "14"],
                "correct": 1,
                "explanation": (
                    "On ajoute un de plus qu’avant, donc le résultat augmente "
                    "d’un. S’appuyer sur un calcul déjà connu évite de tout "
                    "reprendre."
                ),
            },
            {
                "ref": "f-addition-4",
                "prompt": "Combien font 6 + 6 ?",
                "choices": ["11", "12", "13"],
                "correct": 1,
                "explanation": (
                    "C’est un double, et les doubles se retiennent par cœur. Une "
                    "fois celui-là su, 6 + 7 se trouve sans compter : un de plus."
                ),
            },
            {
                "ref": "f-addition-5",
                "prompt": "Combien font 9 + 7 ?",
                "choices": ["15", "16", "17"],
                "correct": 1,
                "explanation": (
                    "Un pas pour atteindre dix depuis neuf, puis il en reste "
                    "six. Dix plus six font seize."
                ),
            },
            {
                "ref": "f-addition-6",
                "prompt": "Pour calculer 3 + 8, par quel nombre vaut-il mieux commencer ?",
                "choices": [
                    "Par le 3",
                    "Par le 8",
                    "Peu importe, ça change le résultat",
                ],
                "correct": 1,
                "explanation": (
                    "En partant du plus grand, il ne reste que trois pas à "
                    "faire au lieu de huit. Le résultat est le même, seul le "
                    "chemin change."
                ),
            },
            {
                "ref": "f-addition-7",
                "prompt": "On sait que 6 + 4 fait 10. Combien font 6 + 5 ?",
                "choices": ["10", "11", "15"],
                "correct": 1,
                "explanation": (
                    "On ajoute un de plus qu’avant, donc le résultat augmente "
                    "d’un aussi. S’appuyer sur un calcul connu évite de tout "
                    "recompter."
                ),
            },
            {
                "ref": "f-addition-8",
                "prompt": "Combien font 7 + 7 ?",
                "choices": ["13", "14", "15"],
                "correct": 1,
                "explanation": (
                    "C’est un double à connaître par cœur. Une fois celui-ci "
                    "su, 7 + 8 se retrouve sans compter : un de plus."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-ma-soustraction",
        "title": "Soustraire pas à pas",
        "competency": MA_SOUSTRACTION,
        "minutes": 6,
        "guidance": (
            "Soustraire, c’est reculer — ou bien chercher ce qui manque. Les deux "
            "chemins donnent le même résultat, et le second est souvent plus "
            "court.\n\n"
            "Pour 13 − 5 : soit on recule de cinq depuis 13, soit on part de 5 et "
            "on avance jusqu’à 13. De 5 à 10 il y a cinq pas, de 10 à 13 il y en a "
            "trois : huit en tout.\n\n"
            "Attention, l’ordre compte, contrairement à l’addition. 13 − 5 et "
            "5 − 13 ne sont pas la même chose du tout.\n\n"
            "Et une soustraction défait une addition : si tu connais l’addition, "
            "tu connais déjà la soustraction qui lui correspond."
        ),
        "questions": [
            {
                "ref": "f-soustraction-1",
                "prompt": "Combien font 15 − 7 ?",
                "choices": ["7", "8", "9"],
                "correct": 1,
                "explanation": (
                    "De sept à dix il y a trois pas, de dix à quinze il y en a "
                    "cinq. On additionne les deux morceaux du chemin."
                ),
            },
            {
                "ref": "f-soustraction-2",
                "prompt": "Tom a 12 billes et il en perd 4. Combien lui en reste-t-il ?",
                "choices": ["6", "8", "16"],
                "correct": 1,
                "explanation": (
                    "Perdre, c’est reculer. Le troisième choix serait la réponse "
                    "s’il en avait gagné quatre : c’est l’erreur la plus fréquente, "
                    "et elle vient de n’avoir pas lu le verbe."
                ),
            },
            {
                "ref": "f-soustraction-3",
                "prompt": "On sait que 8 + 5 fait 13. Que fait 13 − 5 ?",
                "choices": ["5", "8", "13"],
                "correct": 1,
                "explanation": (
                    "La soustraction rend ce que l’addition avait ajouté. Chaque "
                    "addition connue en offre une gratuitement."
                ),
            },
            {
                "ref": "f-soustraction-4",
                "prompt": "Peut-on écrire 4 − 9 à la place de 9 − 4 ?",
                "choices": [
                    "Oui, c’est pareil",
                    "Non, l’ordre change tout",
                    "Oui, mais c’est plus long",
                ],
                "correct": 1,
                "explanation": (
                    "On ne peut pas enlever neuf objets d’un tas qui n’en a que "
                    "quatre. C’est justement ce qui distingue la soustraction de "
                    "l’addition, où l’ordre est libre."
                ),
            },
            {
                "ref": "f-soustraction-5",
                "prompt": "Combien font 17 − 9 ?",
                "choices": ["7", "8", "9"],
                "correct": 1,
                "explanation": (
                    "De neuf à dix il y a un pas, de dix à dix-sept il y en a "
                    "sept : huit en tout."
                ),
            },
            {
                "ref": "f-soustraction-6",
                "prompt": "Léa a 10 images et en donne 3. Combien lui en reste-t-il ?",
                "choices": ["6", "7", "13"],
                "correct": 1,
                "explanation": (
                    "Donner, c’est reculer. Le dernier choix additionne au "
                    "lieu de soustraire, l’erreur la plus fréquente ici."
                ),
            },
            {
                "ref": "f-soustraction-7",
                "prompt": "On sait que 6 + 9 fait 15. Que fait 15 − 9 ?",
                "choices": ["6", "9", "15"],
                "correct": 0,
                "explanation": (
                    "La soustraction rend ce que l’addition avait ajouté. "
                    "Chaque addition connue en offre une gratuitement."
                ),
            },
            {
                "ref": "f-soustraction-8",
                "prompt": "Peut-on écrire 3 − 10 à la place de 10 − 3 ?",
                "choices": [
                    "Oui, c’est pareil",
                    "Non, l’ordre change tout",
                    "Oui, mais c’est plus long",
                ],
                "correct": 1,
                "explanation": (
                    "On ne peut pas enlever dix objets d’un tas qui n’en a que "
                    "trois. L’ordre compte en soustraction, contrairement à "
                    "l’addition."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-ma-probleme",
        "title": "Un problème, une étape",
        "competency": MA_PROBLEME,
        "minutes": 7,
        "guidance": (
            "Un problème se lit trois fois, et pas une seule.\n\n"
            "1. De quoi parle-t-on ? Repère les nombres et ce qu’ils comptent.\n"
            "2. Que demande exactement la question ? Relis-la seule, sans le "
            "reste.\n"
            "3. Ajoute-t-on ou enlève-t-on ? On gagne, on reçoit, on met ensemble : "
            "on ajoute. On perd, on donne, on mange, il reste : on enlève.\n\n"
            "À la fin, vérifie que ta réponse est possible. On ne peut pas donner "
            "plus qu’on n’a, ni qu’il reste plus qu’au début."
        ),
        "questions": [
            {
                "ref": "f-probleme-1",
                "prompt": (
                    "Léa a 7 images. Sa sœur lui en donne 6. Combien en a-t-elle "
                    "maintenant ?"
                ),
                "choices": ["12", "13", "1"],
                "correct": 1,
                "explanation": (
                    "On lui donne, donc elle en gagne : c’est une addition. Le "
                    "dernier choix serait la réponse à une autre question — "
                    "combien elle en a de moins que sa sœur."
                ),
            },
            {
                "ref": "f-probleme-2",
                "prompt": "Tom a 14 bonbons. Il en mange 6. Combien lui en reste-t-il ?",
                "choices": ["8", "20", "6"],
                "correct": 0,
                "explanation": (
                    "Manger, c’est enlever. Le deuxième choix additionne au lieu "
                    "de soustraire : c’est ce qui arrive quand on lit les nombres "
                    "sans lire le verbe."
                ),
            },
            {
                "ref": "f-probleme-3",
                "prompt": (
                    "Une boîte contient 9 crayons, Léa en sort 3. Pour savoir ce "
                    "qui reste dans la boîte, que faut-il faire ?"
                ),
                "choices": ["Une addition", "Une soustraction", "Rien à calculer"],
                "correct": 1,
                "explanation": (
                    "Sortir des crayons, c’est en retirer à la boîte. Il en "
                    "restera six — mais l’important ici est d’avoir choisi la "
                    "bonne opération avant de calculer."
                ),
            },
            {
                "ref": "f-probleme-4",
                "prompt": "Tom a 5 billes et il en donne 8 à Léa. Est-ce possible ?",
                "choices": [
                    "Oui, il lui en restera 3",
                    "Non, il n’en a pas assez",
                    "Oui, il lui en restera 13",
                ],
                "correct": 1,
                "explanation": (
                    "On ne peut pas donner plus qu’on ne possède. Un problème peut "
                    "être impossible, et le remarquer est une vraie réponse — pas "
                    "un refus de répondre."
                ),
            },
            {
                "ref": "f-probleme-5",
                "prompt": (
                    "Awa a 9 perles. Son frère lui en donne 5. Combien en "
                    "a-t-elle maintenant ?"
                ),
                "choices": ["14", "4", "13"],
                "correct": 0,
                "explanation": (
                    "On lui donne, donc elle en gagne : c’est une addition. "
                    "Neuf plus cinq font quatorze."
                ),
            },
            {
                "ref": "f-probleme-6",
                "prompt": (
                    "Moussa a 16 bonbons. Il en donne 7 à son ami. Combien "
                    "lui en reste-t-il ?"
                ),
                "choices": ["9", "23", "7"],
                "correct": 0,
                "explanation": (
                    "Donner, c’est enlever. Le deuxième choix additionne au "
                    "lieu de soustraire, ce qui arrive quand on ne lit pas le "
                    "verbe."
                ),
            },
            {
                "ref": "f-probleme-7",
                "prompt": (
                    "Un panier contient 12 oranges, on en retire 5. Pour "
                    "savoir ce qui reste, que faut-il faire ?"
                ),
                "choices": ["Une addition", "Une soustraction", "Rien à calculer"],
                "correct": 1,
                "explanation": (
                    "Retirer des oranges, c’est en enlever au panier. Il en "
                    "restera sept, mais l’important est d’abord de choisir la "
                    "bonne opération."
                ),
            },
            {
                "ref": "f-probleme-8",
                "prompt": "Tom a 6 images et il en donne 10 à Léa. Est-ce possible ?",
                "choices": [
                    "Oui, il lui en restera 4",
                    "Non, il n’en a pas assez",
                    "Oui, il lui en restera 16",
                ],
                "correct": 1,
                "explanation": (
                    "On ne peut pas donner plus qu’on ne possède. Remarquer "
                    "qu’un problème est impossible est une vraie réponse."
                ),
            },
        ],
    },
    # ── Anglais ─────────────────────────────────────────────────────────────
    {
        "code": f"{PREFIX}fix-an-salutations",
        "title": "Se saluer en anglais",
        "competency": AN_SALUTATIONS,
        "minutes": 4,
        "guidance": (
            "En anglais, on ne salue pas de la même façon en arrivant et en "
            "partant. Pour arriver, on dit « Hello », qui veut dire « bonjour ». "
            "Pour partir, on dit « Goodbye », ou plus court, « Bye ».\n\n"
            "Il y a aussi deux mots de politesse qui ne se disent jamais au même "
            "moment. « Please » sert à demander quelque chose, avant de l’avoir "
            "reçu. « Thank you » sert à remercier, après l’avoir reçu.\n\n"
            "Un moyen de ne pas se tromper : si tu demandes une chose, pense à "
            "« please ». Si on vient de te donner quelque chose, pense à "
            "« thank you »."
        ),
        "questions": [
            {
                "ref": "f-an-salutations-1",
                "prompt": "Comment dit-on « bonjour » en anglais, quand on arrive ?",
                "choices": ["Goodbye", "Hello", "Bye"],
                "correct": 1,
                "explanation": (
                    "« Hello » sert à saluer en arrivant. « Goodbye » et « Bye » "
                    "servent au contraire à saluer en partant, jamais en arrivant."
                ),
            },
            {
                "ref": "f-an-salutations-2",
                "prompt": "Quel mot dit-on en partant, pas en arrivant ?",
                "choices": ["Hello", "Goodbye", "Please"],
                "correct": 1,
                "explanation": (
                    "« Goodbye » marque un départ. « Hello » sert à l’arrivée, "
                    "dans l’autre sens, et « Please » n’a rien à voir avec les "
                    "salutations : c’est pour demander quelque chose."
                ),
            },
            {
                "ref": "f-an-salutations-3",
                "prompt": (
                    "Tu veux demander un verre d’eau poliment en anglais. Quel "
                    "mot ajoutes-tu ?"
                ),
                "choices": ["Thank you", "Goodbye", "Please"],
                "correct": 2,
                "explanation": (
                    "« Please » accompagne une demande, avant de recevoir la "
                    "chose. « Thank you » vient après, pour remercier, jamais "
                    "avant."
                ),
            },
            {
                "ref": "f-an-salutations-4",
                "prompt": "Léa vient de recevoir un cadeau. Que dit-elle ?",
                "choices": ["Please", "Hello", "Thank you"],
                "correct": 2,
                "explanation": (
                    "Recevoir quelque chose appelle un remerciement, après coup : "
                    "« thank you ». « Please » se dit avant de recevoir, pas après."
                ),
            },
            {
                "ref": "f-an-salutations-5",
                "prompt": "Comment dit-on « merci » en anglais ?",
                "choices": ["Please", "Thank you", "Sorry"],
                "correct": 1,
                "explanation": (
                    "« Thank you » sert à remercier. « Please » accompagne "
                    "une demande, pas un remerciement, et « Sorry » sert à "
                    "s’excuser."
                ),
            },
            {
                "ref": "f-an-salutations-6",
                "prompt": "Quel mot utilise-t-on pour s’excuser en anglais ?",
                "choices": ["Sorry", "Hello", "Please"],
                "correct": 0,
                "explanation": (
                    "« Sorry » sert à s’excuser. « Hello » sert à saluer, et "
                    "« Please » sert à demander quelque chose poliment."
                ),
            },
            {
                "ref": "f-an-salutations-7",
                "prompt": (
                    "Awa arrive à l’école et voit sa maîtresse. Que dit-elle "
                    "en premier ?"
                ),
                "choices": ["Goodbye", "Hello", "Thank you"],
                "correct": 1,
                "explanation": (
                    "En arrivant quelque part, on salue avec « Hello ». "
                    "« Goodbye » se dit seulement en partant."
                ),
            },
            {
                "ref": "f-an-salutations-8",
                "prompt": "Comment dit-on « s’il te plaît » en anglais ?",
                "choices": ["Please", "Thank you", "Hello"],
                "correct": 0,
                "explanation": (
                    "« Please » sert à demander poliment. « Thank you » vient "
                    "après avoir reçu, jamais avant."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-an-couleurs",
        "title": "Les couleurs en anglais",
        "competency": AN_COULEURS,
        "minutes": 4,
        "guidance": (
            "Certaines couleurs se retiennent par une image : « red » comme une "
            "pomme rouge, « yellow » comme le soleil, « green » comme l’herbe, "
            "« blue » comme le ciel.\n\n"
            "Le piège habituel, c’est de confondre deux mots qui commencent par "
            "un son proche. « Yellow » (jaune) et « green » (vert) ne se "
            "ressemblent pourtant pas du tout une fois qu’on les compare à voix "
            "haute.\n\n"
            "Si tu hésites, pense d’abord à l’objet que tu connais déjà dans "
            "cette couleur, puis dis son nom anglais."
        ),
        "questions": [
            {
                "ref": "f-an-couleurs-1",
                "prompt": "Comment dit-on « rouge » en anglais ?",
                "choices": ["Blue", "Red", "Green"],
                "correct": 1,
                "explanation": (
                    "« Red » désigne le rouge, par exemple celui d’une pomme. "
                    "« Blue » est le bleu, et « Green » le vert : trois mots à "
                    "ne pas confondre."
                ),
            },
            {
                "ref": "f-an-couleurs-2",
                "prompt": "Quelle couleur est « green » ?",
                "choices": ["Rouge", "Vert", "Jaune"],
                "correct": 1,
                "explanation": (
                    "« Green » se dit pour le vert, la couleur de l’herbe. Le "
                    "jaune se dit « yellow », un mot différent malgré un début "
                    "de son proche."
                ),
            },
            {
                "ref": "f-an-couleurs-3",
                "prompt": "Comment dit-on « bleu » en anglais ?",
                "choices": ["Blue", "Black", "Brown"],
                "correct": 0,
                "explanation": (
                    "« Blue » désigne le bleu. Les deux autres commencent par "
                    "une lettre proche mais désignent le noir et le marron."
                ),
            },
            {
                "ref": "f-an-couleurs-4",
                "prompt": "Le soleil est jaune. Comment dit-on « jaune » en anglais ?",
                "choices": ["Yellow", "Green", "Red"],
                "correct": 0,
                "explanation": (
                    "« Yellow » désigne le jaune. Il ne faut pas le confondre "
                    "avec « green », qui commence par un son proche mais "
                    "désigne le vert."
                ),
            },
            {
                "ref": "f-an-couleurs-5",
                "prompt": "Comment dit-on « noir » en anglais ?",
                "choices": ["Black", "White", "Brown"],
                "correct": 0,
                "explanation": (
                    "« Black » désigne le noir. « White » est le blanc, et "
                    "« Brown » le marron : trois couleurs à ne pas confondre."
                ),
            },
            {
                "ref": "f-an-couleurs-6",
                "prompt": "Quelle couleur est « white » ?",
                "choices": ["Noir", "Blanc", "Gris"],
                "correct": 1,
                "explanation": (
                    "« White » se dit pour le blanc. Le noir se dit « black », "
                    "un mot très différent malgré la même première lettre."
                ),
            },
            {
                "ref": "f-an-couleurs-7",
                "prompt": "Comment dit-on « marron » en anglais ?",
                "choices": ["Brown", "Black", "Blue"],
                "correct": 0,
                "explanation": (
                    "« Brown » désigne le marron. Il ne faut pas le confondre "
                    "avec « black », qui désigne le noir."
                ),
            },
            {
                "ref": "f-an-couleurs-8",
                "prompt": "L’herbe est verte. Comment dit-on « vert » en anglais ?",
                "choices": ["Blue", "Green", "Yellow"],
                "correct": 1,
                "explanation": (
                    "« Green » désigne le vert, la couleur de l’herbe. "
                    "« Yellow » est le jaune, une couleur différente."
                ),
            },
        ],
    },
    {
        "code": f"{PREFIX}fix-an-nombres-5",
        "title": "Compter jusqu’à cinq en anglais",
        "competency": AN_NOMBRES5,
        "minutes": 4,
        "guidance": (
            "Compter en anglais jusqu’à cinq, c’est cinq mots à connaître par "
            "cœur, dans l’ordre : one, two, three, four, five.\n\n"
            "Deux d’entre eux se confondent souvent à l’oreille : « three » "
            "(trois) et « four » (quatre) commencent presque pareil. Pour ne "
            "pas te tromper, retiens que « three » siffle au début, alors que "
            "« four » commence par un son plus sourd.\n\n"
            "Une astuce : compte sur tes doigts en anglais à voix haute "
            "plusieurs fois de suite. L’ordre finit par se retenir tout seul, "
            "comme une comptine."
        ),
        "questions": [
            {
                "ref": "f-an-nombres5-1",
                "prompt": "Comment dit-on « un » en anglais ?",
                "choices": ["Two", "One", "Five"],
                "correct": 1,
                "explanation": (
                    "« One » désigne le premier nombre, un. « Two » est deux, "
                    "et « Five » est cinq : des mots distincts à ne pas "
                    "mélanger."
                ),
            },
            {
                "ref": "f-an-nombres5-2",
                "prompt": "Quel nombre est « four » en anglais ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 1,
                "explanation": (
                    "« Four » correspond à quatre. « Three », qui lui ressemble "
                    "à l’oral, correspond à trois : deux mots proches à ne pas "
                    "confondre."
                ),
            },
            {
                "ref": "f-an-nombres5-3",
                "prompt": "Comment dit-on « trois » en anglais ?",
                "choices": ["Four", "Three", "Five"],
                "correct": 1,
                "explanation": (
                    "« Three » désigne le nombre trois. Il commence par un son "
                    "qui siffle, contrairement à « four », qu’on confond "
                    "parfois avec lui."
                ),
            },
            {
                "ref": "f-an-nombres5-4",
                "prompt": "« One, two, three, four, … » Quel nombre vient ensuite ?",
                "choices": ["Three", "Four", "Five"],
                "correct": 2,
                "explanation": (
                    "Après quatre vient cinq, qui se dit « five ». La suite ne "
                    "s’arrête pas à four : il reste un nombre à réciter."
                ),
            },
            {
                "ref": "f-an-nombres5-5",
                "prompt": "Comment dit-on « deux » en anglais ?",
                "choices": ["One", "Two", "Four"],
                "correct": 1,
                "explanation": (
                    "« Two » désigne le nombre deux. « One » est un, et "
                    "« Four » est quatre : des mots à ne pas mélanger."
                ),
            },
            {
                "ref": "f-an-nombres5-6",
                "prompt": "Quel nombre est « five » en anglais ?",
                "choices": ["Trois", "Quatre", "Cinq"],
                "correct": 2,
                "explanation": (
                    "« Five » correspond à cinq, le dernier nombre de cette "
                    "suite. « Four », qui le précède, correspond à quatre."
                ),
            },
            {
                "ref": "f-an-nombres5-7",
                "prompt": "Comment dit-on « quatre » en anglais ?",
                "choices": ["Three", "Four", "Five"],
                "correct": 1,
                "explanation": (
                    "« Four » désigne le nombre quatre. Il se distingue de "
                    "« three », qui lui ressemble un peu à l’oral."
                ),
            },
            {
                "ref": "f-an-nombres5-8",
                "prompt": "« Five, four, three, two, … » Quel nombre vient ensuite ?",
                "choices": ["Two", "One", "Zero"],
                "correct": 1,
                "explanation": (
                    "En comptant à l’envers, après deux vient un, qui se dit "
                    "« one ». La suite ne s’arrête pas avant d’atteindre le "
                    "début."
                ),
            },
        ],
    },
]
