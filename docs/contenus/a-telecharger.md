# Ce qu'il faut télécharger, et où le poser

Cette page est une liste de courses. Elle dit **où** trouver les huit types
autorisés, **où** déposer les fichiers et **quelle commande** lancer ensuite.
Elle ne dit pas quel exercice construire pour quelle compétence : c'est le rôle
de [`exercices-par-competence.md`](exercices-par-competence.md), qui couvre les
cinquante-quatre compétences du référentiel à six classes et trois matières.

## D'abord, la vérité sur ce qui manque vraiment

Le contenu pédagogique existe déjà pour une bonne part du référentiel. Quinze
fiches de remédiation sur cinquante-quatre compétences, cent vingt questions
(une réserve de huit par fiche, quatre tirées au hasard à chaque tentative,
ADR-020), quinze leçons, six examens d'entrée à cent soixante-deux questions
au total (trois fixes par compétence, l'examen n'étant pas concerné par le
tirage) — tout est écrit, rattaché aux compétences et corrigé côté serveur.

**Ce que ce contenu-là ne sait pas faire, c'est se faire entendre et se faire
manipuler.** C'est exactement ce que H5P et PhET apportent, et c'est à cela qu'il
faut dépenser le téléchargement :

| Ce qui manque | Ce qui le comble |
|---|---|
| **Le son** — la phonologie se lit au lieu de s'entendre | `H5P.Dictation` |
| **Le geste** — ranger, apparier, déplacer | `H5P.DragText`, `H5P.DragQuestion` |
| **L'image** — dénombrer autre chose que des symboles typographiques | `H5P.DragQuestion`, PhET |
| **La manipulation libre** — essayer, se tromper, recommencer sans être noté | PhET |

Un QCM H5P n'apporte rien qu'une fiche ne fasse déjà, et il perd le
rattachement à la compétence. **Ne dépensez pas votre soirée sur des QCM.**

## Les huit types autorisés

ADR-012 amendée le 17 août 2026, sur votre validation. La liste est tenue par une
contrainte en base : un type absent de cette liste est refusé avant que le
fichier n'atteigne le stockage.

| Type H5P | Ce qu'il permet |
|---|---|
| `H5P.Dictation` | **Un son à écouter**, un texte à écrire — la dette la plus large du référentiel |
| `H5P.DragText` | Remettre des mots ou des syllabes dans l'ordre |
| `H5P.DragQuestion` | Glisser sur une image, apparier, dénombrer, placer sur une droite graduée |
| `H5P.MarkTheWords` | Repérer dans un texte les mots qui portent un sens ou une forme |
| `H5P.Blanks` | Texte à trous |
| `H5P.MultiChoice` | QCM avec image |
| `H5P.SingleChoiceSet` | Suite de questions à un seul choix, gros boutons |
| `H5P.TrueFalse` | Vrai ou faux, déjà en place |

**Quel type pour quelle compétence** : voir
[`exercices-par-competence.md`](exercices-par-competence.md), qui donne un
exercice concret pour chacune des cinquante-quatre.

**Refusés volontairement, et pourquoi** — pour que vous ne perdiez pas de temps
dessus :

- `H5P.QuestionSet` : il regroupe plusieurs questions sous une seule activité.
  Rattacher chacune à sa compétence demande de lire les identifiants de
  sous-contenu dans l'archive à la main. Faisable, mais pas gratuit.
- `H5P.ArithmeticQuiz` : il chronomètre l'enfant. Cette plateforme ne
  chronomètre pas un enfant de six ans.
- `H5P.InteractiveVideo`, `H5P.Column`, `H5P.Accordion` : ce sont des
  conteneurs, pas des exercices ; ils ne produisent pas de lecture.

## Où les trouver

### 1. Les fabriquer — c'est la voie principale

Il n'existe **pas de banque publique de H5P français pour le primaire** prête à
télécharger. L'essentiel du H5P qui circule est fabriqué par ceux qui l'utilisent.
C'est aussi la seule voie qui donne une licence claire : le contenu est à vous.

Et le travail est plus court qu'il n'en a l'air : **les énoncés sont déjà
écrits**, dans `apps/api/app/demo/fiches.py`. Il s'agit de les rejouer dans un
éditeur, pas de les inventer.

Deux outils :

- **Lumi** — <https://lumi.education> — application de bureau, gratuite, libre,
  hors ligne. Elle exporte des `.h5p` **complets, avec leurs bibliothèques**.
  C'est celle que je recommande : rien ne dépend d'un compte ni d'une connexion.
- **h5p.com** — votre compte. Créez le contenu, puis « Download » pour obtenir le
  `.h5p`. Attention au piège décrit plus bas.

### 2. Les exemples officiels

<https://h5p.org/content-types-and-applications> — chaque type a sa page avec un
exemple jouable et un bouton de téléchargement. Utile pour **obtenir les
bibliothèques** d'un type, même si le contenu de l'exemple est en anglais et ne
vous servira pas tel quel.

Vérifiez la licence affichée sous chaque exemple : ADR-012 demande qu'elle soit
constatée avant publication, et la commande d'enregistrement l'exige en argument.

### 3. PhET, pour les simulations

<https://phet.colorado.edu/fr/simulations/filter?subjects=math&type=html> — en
français, gratuit, licence CC BY.

Pour CP et CE1 : **Jouer avec les nombres**, **Comparer les nombres**, **Faire
dix**, **Arithmétique**. Chaque page a un bouton de téléchargement qui donne un
**fichier HTML unique fonctionnant hors ligne** — exactement ce que notre origine
isolée sait servir.

PhET ne passe pas par le circuit H5P : c'est ADR-007, une iframe, et une activité
de nature `phet`.

## Le piège : l'export « contenu seul »

**Un `.h5p` peut ne contenir aucune bibliothèque.** Il n'a alors que `h5p.json`
et `content/`, il ressemble à un paquet complet, et il ne jouera jamais tout seul.

C'est le cas du paquet du pilote, et c'est pour cela que ses bibliothèques
avaient dû être préparées à la main.

La commande vous le dit en toutes lettres :

```
essai.h5p : AUCUNE bibliothèque dans l’archive.
```

Si vous voyez ce message, reprenez le téléchargement depuis la page du contenu
plutôt que par « Reuse ». **Les exports de Lumi contiennent toujours leurs
bibliothèques.**

## Où déposer les fichiers

```
experiments/h5p-spike/packages/          ← vos fichiers .h5p ici
experiments/h5p-spike/player/runtime/content/   ← les bibliothèques (la commande s'en charge)
```

## Un paquet nouveau : une seule commande

`infrastructure/scripts/deployer_h5p.sh` enchaîne tout ce dont un paquet a
besoin pour devenir jouable : copie du fichier vers l'arbre versionné, ouverture
de l'activité, enregistrement du paquet, déploiement. La licence et la source
sont fixées une fois pour toutes dans le script (`CC BY 4.0`,
`https://lumi.education, fabriqué par nos soins`) — plus besoin de les
retaper, ni de risquer d'en inventer une différente à chaque dépôt.

Depuis la racine du dépôt, la pile Docker démarrée :

```bash
infrastructure/scripts/deployer_h5p.sh \
    "/mnt/c/Users/<votre compte>/Downloads/mon-exercice.h5p" \
    son-<competence> <competence> "Titre affiché à l'enfant" 5
```

Le fichier peut venir de n'importe où lisible depuis WSL — le dossier
Téléchargements Windows en particulier, `/mnt/c/Users/<compte>/Downloads/`.

Le code de l'activité est libre, mais gardez une convention lisible :
`son-<compétence>` pour ce qu'un son ajoute à côté d'une fiche existante,
`h5p-<compétence>` pour un exercice complet sur une compétence qui n'a
encore rien — les deux se retrouvent dans
[`exercices-par-competence.md`](exercices-par-competence.md). **Jamais de
préfixe `demo-`** : ces activités sont du contenu réel et déployé, pas les
données fictives que `python -m app.demo --reset` recrée et détruit à chaque
fois — un code qui commence par `demo-` serait supprimé au reset suivant sans
être recréé.

`register`, appelé par le script, refuse le fichier s'il n'est pas une
archive, s'il pèse trop lourd, s'il contient un chemin qui sort de l'archive,
ou si son type n'est pas dans les huit. C'est voulu : le refus est le
comportement par défaut.

### Si le paquet apporte une bibliothèque encore jamais vue

Ça n'arrive qu'une fois par bibliothèque (`H5P.Dictation`, `H5P.DragText`…), pas
à chaque paquet — le script ne s'en charge pas, ces deux commandes restent
manuelles :

```bash
# Depuis apps/api
python -m app.catalog libraries ../../experiments/h5p-spike/packages/*.h5p
python -m app.catalog deploy-runtime ../../experiments/h5p-spike/player/runtime
```

## Ce qu'il reste à faire après le dépôt

Une activité qui joue un paquet H5P **remplace** la fiche écrite pour la même
compétence, ou vient à côté d'elle. Deux façons :

- **à côté** : créez une activité de plus, avec son propre code, qui déclare la
  même compétence. Le diagnostic proposera l'une ou l'autre ;
- **à la place** : donnez au paquet le code de la fiche existante — mais la fiche
  perd alors sa leçon et ses explications, qu'un H5P ne porte pas.

Je recommande **à côté**, et de réserver le H5P à ce qu'une fiche ne sait pas
faire : le son et le geste.
