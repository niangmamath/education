# ADR-018, Six classes cumulatives, un examen par classe, un passage décidé par le parent

- Statut : Accepté
- Date : 18 août 2026

## Contexte

Le référentiel ne connaissait que deux classes, CP et CE1, et douze compétences.
C'était assez pour éprouver la mécanique et pas assez pour servir : l'élémentaire
en compte **six**, du Cours d'Initiation au Cours Moyen deuxième année, et un
élève y passe six ans.

Trois manques en découlaient, et chacun rendait la plateforme inutilisable au
delà d'une démonstration.

**Un seul examen d'entrée.** Ce qu'on demande à un CI et ce qu'on demande à un
CM2 n'ont rien de commun. Un examen unique mesurait l'un ou l'autre, jamais les
deux, et produisait pour le reste des lectures fausses qui avaient l'air vraies.

**Aucune classe sur le profil.** La plateforme ne savait pas où en était l'élève,
donc elle ne pouvait ni choisir un examen, ni savoir ce qu'il devait tenir.

**Aucun moyen de passer en classe supérieure.** Le dossier d'un élève le suit
toute sa scolarité ; sans passage, il restait figé sur la classe de son
inscription.

## Décision

### Six classes, et elles sont cumulatives

`ci`, `cp`, `ce1`, `ce2`, `cm1`, `cm2`. **Un élève d'une classe doit tenir les
compétences de toutes les classes antérieures, la sienne comprise.** Ce n'est pas
une convention d'affichage : c'est ce qui rend le diagnostic capable de
descendre, et descendre est ce que cette plateforme fait de plus utile.

Les niveaux ne sont **pas écrits en dur dans le code**. Ils appartiennent à
l'édition du référentiel, seule autorisée à dire de quoi l'élémentaire est fait.
Une plateforme qui les figerait refuserait de servir un pays qui découpe
autrement. `app.levels.service` pose les deux seules questions qui comptent —
« que doit tenir un élève de cette classe ? » et « quelle est la classe
suivante ? » — en lisant l'édition en vigueur.

Trente-six compétences, six par classe, trois par matière. Les prérequis
traversent les niveaux exprès : la conjugaison du CE2 dépend de la
reconnaissance des groupes de verbes, la division du CM1 dépend de la
multiplication du CE2, qui dépend de l'addition du CP.

### Un examen d'entrée par classe

Six examens, six questions chacun, une par compétence de la classe.

**Il ne porte que sur la classe déclarée**, et c'est un arbitrage. Un examen qui
balaierait aussi les classes antérieures ferait trente-six questions à un CM2, et
aucun enfant ne le finirait. La descente est le travail du diagnostic, pas celui
de l'examen.

L'examen est donné **à l'entrée dans une classe** — à l'inscription, et de nouveau
à chaque passage. C'est toujours le seul endroit où la plateforme assigne quelque
chose d'elle-même, et l'argument est le même qu'avant : sans lui, elle ne sait
rien de l'année qui commence.

### La classe est déclarée, jamais devinée

Demandée à l'inscription, sur les deux chemins — le parent qui crée un profil et
l'enfant qui rejoint sa famille avec le code. La colonne est **nullable** : un
profil ouvert avant que la plateforme ne demande la classe existe, et lui en
attribuer une d'office affirmerait sur un enfant réel ce que personne n'a dit.
Une route permet de la déclarer ou de la corriger après coup.

Quand une édition est en vigueur, la classe doit s'y trouver. Quand **aucune**
n'est publiée, la déclaration est acceptée telle quelle : la plateforme n'a alors
aucune base pour contredire un parent, et refuser reviendrait à empêcher une
famille d'exister tant qu'un opérateur n'a pas importé de programme.

### Le passage est un fait, décidé par le parent

Un bouton, côté parent. La plateforme ne fait passer personne toute seule : elle
ne connaît ni l'école de l'enfant, ni son année scolaire, ni ce qu'un conseil de
maîtres a décidé.

Chaque passage est **une ligne** dans `auth_child_promotions`, avec sa date et le
parent qui l'a décidé. Rien ne s'y met à jour : savoir qu'une lacune a été
observée alors que l'élève était en CE1 n'a pas le même poids qu'une lacune
observée trois ans plus tard. Un parent qui se trompe de bouton fait un passage
de plus ; il ne réécrit pas le précédent, exactement comme une observation
n'écrase jamais l'historique.

**Le palier monte, rien n'est effacé.** Les compétences des classes antérieures
cessent d'être proposées comme travail courant, et toutes leurs lectures restent
en base. C'est précisément ce qui permet de remonter une lacune ancienne quand
une compétence nouvelle bute dessus.

### Une règle de plus : le prérequis jamais observé

`unobserved-prerequisite`. Une compétence non acquise dont le prérequis n'a
**aucune lecture** produit une hypothèse : « on ne sait pas encore, et c'est par
là qu'il faut commencer ». La remédiation vise ce prérequis.

Cette règle n'existait pas et ne pouvait pas exister avant : avec un seul examen,
tout ce qui comptait avait été observé. Avec un examen par classe, un CM1 qui
échoue en division n'a **aucune lecture** sur la multiplication du CE2 ni sur
l'addition du CP. Sans cette règle, la plateforme constaterait l'échec et
n'aurait rien à remonter — elle dirait « échec en division » et proposerait de
refaire des divisions, ce que le produit refuse depuis le premier jour.

La phrase produite dit qu'on ne sait pas, et non qu'on a constaté. Rien n'a été
observé, donc rien ne peut être affirmé : c'est une hypothèse sur l'endroit où
chercher, et travailler ce prérequis produira la lecture qui la confirmera ou
l'infirmera.

## Conséquences

**Vingt-quatre compétences sur trente-six n'ont pas encore de fiche de
remédiation.** Les douze existantes couvrent du CI au CE1. C'est la dette la
mieux mesurée du projet, et un test épingle la couverture dans les deux sens : il
échoue si une fiche disparaît, et il échoue quand de nouvelles arrivent, pour que
personne ne fasse baisser la dette sans la voir baisser.

**Les examens du CI sont les plus fragiles de tout le référentiel.** Un enfant de
cours d'initiation ne lit pas encore, et un examen écrit lui demande déjà de
déchiffrer la question. Ils resteront un pis-aller tant qu'il n'y aura ni son ni
image — c'est le même manque que la phonologie signale depuis le premier examen,
et il est ici plus grave.

**Une classe supprimée d'une édition ultérieure laisserait des élèves orphelins.**
`level_code` est une chaîne sans clé étrangère, par le raisonnement d'ADR-013 : un
niveau appartient à une édition, la classe d'un enfant lui survit. Le prix est
qu'une édition qui renomme `ce1` laisse ces élèves sans classe reconnue. La route
de correction existe pour cela, mais rien ne la déclenche automatiquement.

## Alternatives écartées

**Un examen unique couvrant les six classes.** Trente-six questions pour un CM2 :
aucun enfant ne le finit, et un examen abandonné produit une lecture pire qu'une
absence de lecture.

**Un examen adaptatif qui s'arrête quand l'élève décroche.** C'est la bonne
réponse à terme, et c'est un vrai morceau de travail — il faut décider quand
s'arrêter, et se tromper produit exactement les lectures fausses qu'on cherche à
éviter. La règle du prérequis non observé en fait l'essentiel pour un coût
incomparablement moindre.

**Faire passer les élèves automatiquement au changement d'année.** La plateforme
ne connaît pas l'année scolaire des pays qu'elle sert, ni les redoublements. Un
passage automatique se tromperait sur une partie des élèves, en silence.
