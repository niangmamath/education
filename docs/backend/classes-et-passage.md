# Les six classes, le cumul et le passage

## Ce que couvre la plateforme

L'élémentaire, six ans : **CI, CP, CE1, CE2, CM1, CM2**. Trente-six compétences,
six par classe, trois en français et trois en mathématiques.

Les niveaux ne sont pas écrits dans le code. Ils appartiennent à l'édition du
référentiel en vigueur, et `app.levels.service` les lit — une plateforme qui les
figerait refuserait de servir un pays qui découpe autrement.

## Les compétences sont cumulatives

Un élève de CE2 doit tenir celles du CI, du CP, du CE1 et du CE2.

Ce n'est pas une convention d'affichage. C'est ce qui permet au diagnostic de
**descendre**, et descendre est ce que cette plateforme fait de plus utile :
quand un CM1 bute sur la division, elle remonte à la multiplication du CE2, puis
à l'addition du CP si nécessaire, et propose de travailler *là*.

Les prérequis traversent donc les niveaux exprès. La conjugaison du CE2 dépend de
la reconnaissance des groupes de verbes ; la division du CM1 dépend de la
multiplication du CE2, qui dépend de l'addition du CP.

## Un examen d'entrée par classe

Six examens, six questions chacun, une par compétence de la classe.

**Il ne porte que sur la classe déclarée.** Un examen qui balaierait aussi les
classes antérieures ferait trente-six questions à un CM2, et aucun enfant ne le
finirait — un examen abandonné produit une lecture pire qu'une absence de
lecture.

L'examen est donné à **l'entrée dans une classe** : à l'inscription, puis à
chaque passage. C'est toujours la seule chose que la plateforme assigne d'elle-
même, et pour la même raison qu'avant : sans lui, elle ne sait rien de l'année
qui commence.

## Comment le diagnostic descend quand même

C'est la règle `unobserved-prerequisite`, née avec les six classes.

Un CM1 qui échoue en division n'a **aucune lecture** sur la multiplication du
CE2 : son examen ne l'a jamais interrogée. L'ancienne version écartait ces
prérequis — « rien à en dire » — ce qui laissait la plateforme constater l'échec
sans rien pouvoir remonter. Elle aurait dit « échec en division » et proposé de
refaire des divisions, exactement ce que le produit refuse.

Désormais, un prérequis sans lecture devient une **hypothèse** : « on ne sait pas
encore, et c'est par là qu'il vaut mieux commencer. » La remédiation le vise, et
la travailler produira la lecture qui confirmera ou infirmera l'hypothèse.

La phrase affichée dit qu'on ne sait pas, jamais qu'on a constaté. Rien n'a été
observé, donc rien ne peut être affirmé — un parent ne doit pas lire « votre
enfant ne sait pas compter » là où la plateforme veut dire « nous ne le lui avons
jamais demandé ».

## La classe est déclarée, jamais devinée

Demandée à l'inscription, sur les deux chemins : le parent qui crée un profil, et
l'enfant qui rejoint sa famille avec le code.

La colonne est **nullable**, et c'est délibéré. Un profil ouvert avant que la
plateforme ne demande la classe existe ; lui en attribuer une d'office
affirmerait sur un enfant réel quelque chose que personne n'a dit. Sans classe,
il ne reçoit aucun examen, et l'interface le dit en toutes lettres au lieu de le
laisser deviner.

Quand une édition est en vigueur, la classe doit s'y trouver. Quand aucune n'est
publiée, la déclaration est acceptée : la plateforme n'a alors aucune base pour
contredire un parent, et refuser empêcherait une famille d'exister tant qu'un
opérateur n'a pas importé de programme.

## Le passage en classe supérieure

Un bouton, côté parent, qui nomme la classe d'arrivée plutôt que de dire
« passer » : on doit voir où l'on envoie son enfant avant d'appuyer.

**C'est le parent qui décide.** La plateforme ne connaît ni l'école de l'enfant,
ni son année scolaire, ni ce qu'un conseil de maîtres a tranché ; s'arroger ce
passage reviendrait à prétendre le savoir. Elle ne fait pas passer les élèves
automatiquement au changement d'année non plus — elle se tromperait en silence
sur tous les redoublements.

Ce que le passage fait :

- le palier de compétences monte, et la plateforme propose désormais celles de la
  nouvelle classe ;
- l'élève reçoit l'examen d'entrée de cette classe ;
- une ligne s'ajoute à son historique de classes, avec la date et le parent qui a
  décidé.

Ce qu'il ne fait **pas** : effacer quoi que ce soit. Toutes les lectures des
classes antérieures restent en base, et le diagnostic continue d'y descendre.
C'est exactement ce qui permet de remonter une lacune ancienne quand une
compétence nouvelle bute dessus.

Rien ne se met à jour dans cet historique. Savoir qu'une lacune a été observée
alors que l'élève était en CE1 n'a pas le même poids qu'une lacune observée trois
ans plus tard. Un parent qui se trompe de bouton fait un passage de plus ; il ne
réécrit pas le précédent, comme une observation n'écrase jamais l'historique.

Le CM2 n'a pas de suivant : la suite est le collège, que cette plateforme ne
couvre pas et sur lequel elle ne prétend rien.

## Les routes

| Route | Ce qu'elle fait |
|---|---|
| `GET /auth/classes` | Les classes de l'édition en vigueur. **Sans session** : le formulaire d'inscription en a besoin avant qu'un compte existe |
| `POST /auth/children` | Crée un profil, classe comprise |
| `POST /auth/child/register` | L'enfant rejoint sa famille, classe comprise |
| `PUT /children/{id}/level` | Déclare ou corrige la classe |
| `POST /children/{id}/promotion` | Passe dans la classe supérieure |

## Ce qui reste en dette

- **Vingt-quatre compétences sur trente-six n'ont pas de fiche de remédiation.**
  Les douze existantes couvrent du CI au CE1. Un test épingle la couverture dans
  les deux sens, pour que la dette ne baisse pas sans qu'on la voie baisser.
- **Les examens du CI sont les plus fragiles.** Un enfant de cours d'initiation ne
  lit pas encore, et un examen écrit lui demande de déchiffrer la question. Il
  faudrait du son et des images.
- **Une édition qui renomme une classe laisse des élèves sans classe reconnue.**
  La route de correction existe ; rien ne la déclenche automatiquement.
