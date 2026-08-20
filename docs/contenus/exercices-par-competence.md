# Les exercices à fabriquer, compétence par compétence

Cette liste complète [`a-telecharger.md`](a-telecharger.md), qui dit comment
fabriquer et déposer un fichier. Celle-ci dit **quoi fabriquer**, pour chacune
des trente-six compétences du référentiel.

## Comment lire cette liste

**Douze compétences ont déjà une fiche native** — une leçon et quatre questions,
écrites dans la plateforme, sans H5P. Pour elles, cette liste ne propose **pas**
de tout refaire : elle propose un seul exercice H5P, réservé à ce que la fiche
ne sait pas faire — entendre un son, manipuler un objet. Construire un QCM de
plus sur une compétence déjà couverte ne vaut rien : la fiche le fait déjà, avec
le rattachement à la compétence en plus.

**Vingt-quatre compétences n'ont rien du tout.** Pour elles, la liste propose un
jeu complet — de quoi produire une vraie remédiation, pas un seul exercice
isolé.

**La priorité** suit un ordre simple : d'abord ce qui manque le plus (le son,
partout où il manque), puis les classes dans l'ordre où un enfant les traverse
— CI et CP avant CM2, puisque c'est là que la plupart des lacunes se reportent.

Chaque ligne nomme un type H5P de la liste des huit autorisés par ADR-012, ou
« PhET » quand une simulation manipulable sert mieux qu'un exercice noté.

---

## Priorité 1 — Le son manquant sur les douze compétences déjà couvertes

Aucune de ces douze n'a besoin d'un second exercice complet. Une seule chose
leur manque, et c'est toujours la même : entendre.

| Compétence | Ce qui manque | Type H5P | À construire |
|---|---|---|---|
| `ci-fr-sons`\* | le son isolé | **Dictation** | Un son de lettre isolé (« mmm », « sss »…) ; l'enfant écrit ou choisit la lettre entendue. |
| `cp-fr-syllabes` | compter à l'oreille | **Dictation** | Un mot prononcé entier ; l'enfant tape le nombre de syllabes entendues. |
| `cp-fr-phonemes` | isoler un son dans un mot | **Dictation** | Un mot prononcé ; l'enfant écrit le premier son entendu, ou choisit parmi trois sons proposés à l'oral. |
| `cp-fr-mots` | lire à voix réelle | **DragText** | Remettre les syllabes d'un mot illustré dans l'ordre (glisser-déposer), pour la manipulation que le clavier ne donne pas. |
| `ce1-fr-dictee` | la vraie dictée | **Dictation** | Une phrase courte prononcée entièrement ; l'enfant l'écrit. C'est l'exercice qui porte le nom de la compétence — la fiche actuelle ne fait qu'en approcher l'esprit par écrit. |
| `ci-ma-denombrer` | compter des objets, pas des symboles | **DragQuestion** | Une image (fruits, jetons) ; l'enfant glisse un jeton sur chaque objet compté, ou saisit le total après avoir touché chaque objet. |
| `cp-ma-addition` | manipuler pour additionner | **DragQuestion** | Deux groupes d'objets à réunir par glisser-déposer, puis saisir le total — la manipulation physique que taper un nombre ne donne pas. |
| `ce1-ma-soustraction` | manipuler pour soustraire | **DragQuestion** | Un groupe d'objets dont on retire ceux qui sont barrés/glissés hors du cadre, puis saisir ce qui reste. |

\* `ci-fr-sons` (« Distinguer les sons du langage ») n'a **pas** de fiche native —
elle n'appartient donc pas vraiment aux douze. Elle est mise ici, en tête, parce
qu'elle est le prérequis qui bloque toute remédiation sur `cp-fr-syllabes` puis
`cp-fr-phonemes` : tant qu'elle n'est jamais observée, le moteur de diagnostic
ne propose rien pour ses deux dépendantes, quel que soit le contenu déposé sur
elles. Vérifié en le constatant : un enfant CP en échec sur les deux ne recevait
aucune remédiation tant que `ci-fr-sons` restait sans activité ; `demo-son-ci-fr-sons`
le corrige.

Attention à ne pas confondre `ci-fr-sons` avec `ci-fr-lettres` (« Reconnaître les
lettres de l'alphabet ») : celle-ci a bien sa fiche, est purement visuelle, et
n'a **pas** de manque sonore — c'est un exercice de dictée de sons de lettres qui
avait été déposé par erreur sous son code avant d'être corrigé.

*(`ci-fr-lettres`, `ci-fr-sens`, `cp-ma-ranger`, `ci-ma-chiffres`, `ce1-fr-phrase`,
`ce1-ma-probleme` n'ont pas de manque sonore ou gestuel qui justifie un second
exercice : la fiche suffit.)*

---

## Priorité 2 — CE2, rien n'existe encore

| Compétence | Type H5P principal | À construire |
|---|---|---|
| `ce2-fr-groupes` | **MarkTheWords** | Un court texte ; l'enfant surligne les verbes, puis un second texte où il classe (glisser ou QCM) chaque verbe surligné dans son groupe. |
| `ce2-fr-conjugaison` | **Blanks** | Cinq phrases à trous, un verbe usuel au présent à chaque fois (« Nous ___ à l'école »), avec la liste des verbes juste au-dessus. |
| `ce2-fr-texte` | **MultiChoice** | Un texte de cinq à huit lignes suivi de trois questions à choix, sur ce que le texte dit et sur ce qu'il laisse deviner (comme les items de l'examen). |
| `ce2-ma-nombres-1000` | **DragQuestion** | Placer cinq nombres sur une droite graduée de 0 à 1000, par glisser-déposer. |
| `ce2-ma-multiplication` | **DragQuestion** ou PhET | Une grille à remplir en glissant des jetons pour former un rectangle de multiplication (4 × 3 = 4 rangées de 3) ; PhET *Multiplication* fait la même chose en manipulation libre, sans note. |
| `ce2-ma-mesures` | **DragQuestion** | Associer un objet illustré (une porte, un crayon, un trajet) à l'unité qui convient (cm, m, min, h) par glisser-déposer. |

---

## Priorité 3 — CM1, rien n'existe encore

| Compétence | Type H5P principal | À construire |
|---|---|---|
| `cm1-fr-nature` | **DragText** ou MarkTheWords | Une phrase où chaque mot se glisse dans la bonne colonne (nom / verbe / adjectif). |
| `cm1-fr-temps` | **MarkTheWords** | Un texte au passé, présent et futur mêlés ; l'enfant surligne les verbes selon le temps demandé, une couleur par temps si l'outil le permet, sinon trois passages. |
| `cm1-fr-essentiel` | **MultiChoice** | Un texte de dix lignes suivi de « quel est le titre qui lui va le mieux » et « quelle phrase résume le mieux ce texte », parmi trois propositions. |
| `cm1-ma-fractions` | **DragQuestion** | Associer une fraction écrite (1/4, 1/2, 3/4) à la portion coloriée d'une figure correspondante, par glisser-déposer ; PhET *Fractions* en complément pour manipuler librement. |
| `cm1-ma-division` | **DragQuestion** | Répartir une collection d'objets en parts égales par glisser-déposer, puis saisir le quotient et le reste s'il y en a un. |
| `cm1-ma-probleme-2` | **MultiChoice** | Un énoncé à deux étapes (« Awa achète... elle paie... combien lui rend-on »), avec les résultats intermédiaires plausibles parmi les choix, pour repérer qui s'arrête après la première étape. |

---

## Priorité 4 — CM2, rien n'existe encore

| Compétence | Type H5P principal | À construire |
|---|---|---|
| `cm2-fr-accords` | **Blanks** | Cinq phrases à trous sur les accords difficiles (participe passé avec avoir, pluriels irréguliers), un point de règle rappelé au-dessus de chaque groupe de phrases. |
| `cm2-fr-temps-composes` | **Blanks** | Cinq phrases à trous demandant un temps composé (« Hier, j'___ mon travail »), avec les verbes proposés juste au-dessus. |
| `cm2-fr-redaction` | **MultiChoice** | Une suite de trois phrases dont une seule enchaîne logiquement après une phrase donnée (comme l'item de l'examen de CM2), répété sur trois amorces différentes. |
| `cm2-ma-decimaux` | **DragQuestion** | Placer cinq nombres décimaux sur une droite graduée entre deux entiers consécutifs. |
| `cm2-ma-proportion` | **MultiChoice** ou DragQuestion | Trois énoncés de proportionnalité (prix, recette, vitesse) avec la bonne réponse et deux erreurs de raisonnement courantes (addition au lieu de multiplication, oubli du rapport). |
| `cm2-ma-geometrie` | **DragQuestion** ou PhET | Une figure avec ses mesures ; l'enfant compose le calcul de périmètre ou d'aire en glissant les bonnes opérations, ou PhET *Aire et périmètre* pour une manipulation libre sur quadrillage. |

---

## PhET, où elle sert vraiment

PhET n'est utile que là où **manipuler sans être noté** apprend quelque chose
qu'aucun exercice corrigé ne peut donner. Quatre simulations couvrent
l'essentiel du référentiel :

| Simulation | Compétences qu'elle sert |
|---|---|
| **Jouer avec les nombres** (*Number Play*) | `ci-ma-denombrer`, `ci-ma-chiffres`, `cp-ma-nombres-20` |
| **Comparer les nombres** (*Number Compare*) | `ci-ma-comparer`, `cp-ma-ranger`, `ce1-ma-nombres-100` |
| **Fractions : introduction** | `cm1-ma-fractions`, `cm2-ma-decimaux` |
| **Aire et périmètre** | `cm2-ma-geometrie` |

Retrouvez-les sur
<https://phet.colorado.edu/fr/simulations/filter?subjects=math&type=html> ; le
bouton de téléchargement donne un fichier HTML unique, hors ligne, exactement ce
que l'origine de contenu isolée sait servir.

## Après le dépôt

Chaque exercice construit reste **à côté** de la fiche existante quand il y en a
une, jamais à sa place : la fiche garde sa leçon et ses explications, qu'aucun
paquet H5P ne porte. Pour les vingt-quatre compétences sans rien, une seule
activité H5P suffit à sortir la compétence de la dette mesurée par
`test_the_sheets_cover_the_competencies_they_are_written_for` — ce test devra
être mis à jour (le compte de 12 devra monter) le jour où une vraie fiche native
vient s'y ajouter ; un exercice H5P seul ne l'y fait pas entrer, puisque le test
mesure les fiches natives et non le catalogue entier.
