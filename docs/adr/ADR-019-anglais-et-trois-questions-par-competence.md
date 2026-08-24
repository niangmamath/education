# ADR-019, Une troisième matière, des prérequis qui traversent les matières, trois questions par compétence

- Statut : Accepté
- Date : 24 août 2026, amendée le même jour

## Amendement du 24 août 2026

La première version de cette décision posait que les prérequis de l'anglais ne
traversaient pas les matières, au même titre que le français et les
mathématiques n'en avaient jamais eu entre eux. Le propriétaire a corrigé ce
point le jour même : deux dépendances croisées sont réelles et devaient être
modélisées.

**Résoudre un problème commence par comprendre l'énoncé.** Un enfant qui ne lit
pas encore une phrase française butera sur l'énoncé d'un problème de
mathématiques avant même de buter sur le calcul qu'il demande. Sans ce
prérequis, la plateforme aurait imputé l'échec au calcul quand la vraie cause
était la lecture.

**Le français sert de base de traduction à l'anglais.** Apprendre que « eat »
se dit en anglais passe par le mot déjà connu, « manger » — ce n'est pas un
apprentissage dans le vide. Section « Décision » et « Conséquences » réécrites
en conséquence ; le reste de la décision (l'anglais lui-même, les trois
questions par compétence) est inchangé.

## Contexte

Le propriétaire a demandé deux choses en même temps, et elles se répondent :
ajouter l'anglais comme troisième matière, et cesser de mesurer une compétence
avec une seule question à l'examen d'entrée — trois sont nécessaires.

**Une seule question ne peut rendre qu'un verdict binaire.** Avec un item par
compétence, `app.attempts.rules.read_counts` calcule un ratio qui ne peut valoir
que 0 ou 1 : la bande `partial` (entre le seuil de maîtrise et zéro) était
inatteignable en pratique, alors que le code la prévoyait déjà. Un enfant qui
connaît une notion à moitié recevait donc le même verdict qu'un enfant qui ne la
connaît pas du tout.

**L'anglais n'était pas prévu, mais rien ne l'empêchait.** Le référentiel
modélise déjà la matière comme une vraie table (`Subject`), pas comme un enum ou
un préfixe codé en dur : `fr` et `ma` sont des lignes de données, pas des cas
particuliers du schéma. Ajouter `an` ne demande donc aucune migration, seulement
du contenu.

## Décision

### Anglais, troisième matière

Sujet `an`, deux domaines — `an-oral` (écouter et parler) et `an-ecrit` (lire et
écrire) — et dix-huit compétences, trois par classe du CI au CM2, cumulatives
comme le reste du référentiel. Le CI reste oral seulement, comme pour le
français : saluer, nommer des couleurs, compter jusqu'à cinq. Le CM2 attend la
compréhension d'un texte court et la rédaction de phrases simples sur soi-même.

Le référentiel compte désormais neuf compétences par classe et cinquante-quatre
au total, trois par matière.

### Des prérequis qui traversent les matières, à deux endroits précis

Le principe reste que le français, les mathématiques et l'anglais s'apprennent
en parallèle : la très grande majorité des compétences n'a de prérequis que
dans sa propre matière, exactement comme avant. Deux familles font exception,
et chacune a une justification pédagogique directe plutôt qu'une règle
générale imposée partout.

**Les compétences « résoudre un problème » dépendent de la compréhension de
phrase ou de texte en français**, au niveau où le problème se pose :
`ce1-ma-probleme` dépend de `ce1-fr-phrase`, `cm1-ma-probleme-2` de
`ce2-fr-texte`, `cm2-ma-proportion` de `cm1-fr-essentiel`. Un énoncé de
problème est une phrase ou un texte avant d'être un calcul ; le prérequis suit
la complexité de lecture qu'il suppose, pas seulement la classe.

**Les compétences anglaises qui lisent ou écrivent dépendent de la mécanique
équivalente déjà acquise en français**, le français servant de base de
traduction : `cp-an-alphabet` dépend de `ci-fr-lettres` (reconnaître des
lettres est le même geste dans les deux alphabets), `ce1-an-mots` et
`ce2-an-phrases` dépendent respectivement de `cp-fr-mots` et `ce1-fr-phrase`
(décoder un mot, comprendre une phrase, avant de le refaire dans une langue
qu'on ne parle pas encore), `cm1-an-etre-avoir` dépend de `ce2-fr-conjugaison`
(la notion qu'un verbe change de forme selon qui agit), et `cm2-an-texte` /
`cm2-an-redaction` dépendent de `ce2-fr-texte` / `ce1-fr-dictee`.

**Le vocabulaire oral de l'anglais ne dépend de rien en français.** Saluer,
nommer une couleur, compter jusqu'à cinq ou dix, nommer un animal ou un jour de
la semaine : ces compétences du domaine `an-oral` restent sans prérequis
français. Le référentiel ne modélise pas de compétence « vocabulaire oral
français », puisque le français est la langue déjà parlée par l'enfant à son
entrée — il n'y a rien à quoi les accrocher, et rien ne prouve qu'un enfant a
besoin de savoir *lire* « bonjour » en français pour apprendre à dire « hello ».

## Conséquences

**Le diagnostic peut désormais reporter une lacune de mathématiques ou
d'anglais derrière une lacune de français**, y compris entre compétences du
même examen. `ce1-ma-probleme` et `ce1-fr-phrase` sont posées à la même classe,
donc dans le même examen d'entrée : ce n'est pas `unobserved-prerequisite` qui
joue ici (les deux ont une lecture), mais la règle d'ADR-015/DIA-05 — une
compétence dont le prérequis est en lacune n'est plus proposée du tout. Un
enfant de CE1 qui échoue le problème *et* la phrase se voit proposer de
travailler la lecture, pas le calcul : c'est exactement le comportement demandé.

**Quarante-deux compétences sur cinquante-quatre n'ont pas de fiche de
remédiation**, dix-huit de plus qu'avant : les dix-huit d'anglais s'ajoutent aux
vingt-quatre de français et de mathématiques déjà en dette. Le test qui épingle
cette couverture dans les deux sens (`tests/test_fiche_items.py`) a été relevé
en conséquence — il continuera d'échouer tant que la dette ne baisse pas
visiblement.

**Le temps de passation de l'examen a plus que doublé.** Neuf minutes de plus en
moyenne par classe, dans une fourchette de 20 (CI) à 32 (CM2) minutes. Rien
n'indique qu'un enfant de six ans tienne vingt minutes d'affilée sans
interruption ; c'est une hypothèse non vérifiée, la même que celle déjà admise
pour l'examen initial.

### Trois questions par compétence, et non une

L'examen d'entrée passe de six questions par classe à vingt-sept : neuf
compétences, trois questions chacune. Ni le modèle de données, ni le moteur de
résultats n'ont dû changer : `authored_questions` et
`catalog_activity_questions` acceptaient déjà plusieurs lignes par compétence,
et `_compute_results()` (`app/attempts/service.py`) regroupait déjà toutes les
réponses jugées sur un même code avant d'appeler `read_counts`. La seule
addition a été le contenu — cent soixante-deux questions au total sur les six
classes — et une référence dérivée du code de compétence (`{compétence}-q{n}`),
qui ne peut pas entrer en collision puisque le code l'est déjà.

## Alternatives écartées

**Garder une seule question par compétence et vivre sans bande « partielle ».**
C'était l'état antérieur. Le propriétaire l'a explicitement jugé insuffisant :
une compétence à moitié maîtrisée ne doit pas recevoir le même verdict qu'une
compétence ignorée.

**Faire dépendre tout le vocabulaire anglais, y compris oral, du français.**
Écarté faute d'un point d'accroche : le référentiel ne trace pas de compétence
de vocabulaire oral français, puisque le français est la langue déjà parlée en
entrant sur la plateforme. Forcer un prérequis vers une compétence de lecture
française pour apprendre à *dire* « hello » aurait bloqué un enfant qui parle
mais ne lit pas encore, sur une base qui n'a rien à voir avec ce qu'on lui
demande.

**Faire dépendre les mathématiques du français à chaque compétence, pas
seulement la résolution de problèmes.** Compter, lire un nombre ou poser une
addition ne suppose aucune lecture de phrase. Étendre le prérequis à tout le
domaine `ma-nombres` et `ma-calcul` aurait affirmé une dépendance qui n'existe
que pour l'énoncé d'un problème, pas pour le calcul lui-même.
