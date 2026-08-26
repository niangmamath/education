# ADR-021, Évaluation par paliers, bornée à la classe déclarée

- Statut : Accepté
- Date : 25 août 2026

## Contexte

Le propriétaire a jugé, le 25 août 2026, que le modèle d'évaluation de la
plateforme était faux dans son principe : l'examen d'entrée (HORS-07,
HORS-08) teste toutes les compétences d'une classe d'un coup, et un enfant
qui valide 100 % ne reçoit rien de plus à ce niveau que celui qui échoue
partout. Le modèle voulu est une progression par **paliers** gagnés un à
un — un enfant n'est testé que sur les premières compétences nécessaires,
une lacune déclenche une remédiation ciblant le vrai prérequis en cause puis
un retest, et un enfant qui valide un palier passe simplement au suivant,
sans rien de plus à faire à celui qu'il vient de valider.

Trois faits du code existant rendaient cette correction possible sans
migration :

- le graphe de prérequis (`ref_competencies` / `ref_competency_prerequisites`,
  étape 07) modélise déjà des arêtes traversant matières et classes
  (ADR-019) ;
- le diagnostic (étape 12, ADR-015) sait déjà différer une compétence
  derrière son prérequis en lacune (`defer-behind-prerequisite`, DIA-05) et
  descendre vers une compétence jamais testée (`unobserved-prerequisite`,
  ADR-018) ;
- rien n'est stocké nulle part dans cette chaîne : le diagnostic, comme les
  progrès, se recalcule à chaque lecture.

Ce qui manquait n'était donc pas une brique de calcul, mais la **politique
de service** de l'examen : il servait toute la banque d'une classe en un
seul `Assignment`, jamais un sous-ensemble.

## Décision

### Le palier n'est pas stocké

Comme le diagnostic depuis ADR-015, un palier se recalcule à chaque lecture
plutôt que d'être persisté : un palier stocké serait une chose de plus
capable de contredire la lecture des tentatives dont il devrait dépendre.

`app.referential.graph` porte la lecture du graphe de prérequis, partagée
par l'examen et le diagnostic plutôt que dupliquée : `CompetencyGraph.load`
charge les compétences et arêtes de l'édition publiée, bornées à une classe
ou non selon l'appelant ; `frontier` rend les codes prêts à être testés dans
un ensemble donné ; `unmet_ancestors` marche le graphe en profondeur pour le
diagnostic. `app.assessment.tiers.next_sitting` compose cette lecture avec
les compétences que l'examen de la classe déclare réellement (via
`catalog_activity_competencies`, ADR-013) et avec les lectures déjà
produites (`app.progress`) pour dire ce qui est dû maintenant.

### Un palier reste borné à la classe déclarée

Décision confirmée par le propriétaire, entre deux lectures possibles de sa
propre demande :

- **Retenue.** Un palier ne considère que les compétences de la classe
  déclarée de l'enfant, et seulement les arêtes de prérequis internes à
  cette classe pour décider ce qui est prêt. La descente vers une classe
  antérieure jamais testée reste **réactive**, déclenchée par un échec —
  exactement ce que fait déjà `unobserved-prerequisite` — jamais un balayage
  systématique du bas du graphe à chaque nouvelle classe.
- **Écartée.** Des paliers cumulatifs, étendus sur tout le graphe depuis la
  toute première classe, le premier palier testé étant littéralement les
  racines du graphe entier.

La première lecture est plus petite et plus sûre : une `Activity` par
classe reste inchangée, aucune tentative n'a besoin de porter des questions
de deux classes à la fois, et surtout elle évite qu'un enfant inscrit
directement en CM2 commence par des questions de CI le jour de son premier
examen. Elle correspond aussi à la lettre de la demande — « même peut-être
jusqu'aux compétences des classes antérieures » est une possibilité
conditionnelle, pas un point de départ obligé.

### Le seuil de maîtrise est celui qui existe déjà

Une compétence débloque ce qui en dépend quand sa dernière lecture est
`mastered` (`RULE_ALL_CORRECT`, étape 10) — le seuil déjà en vigueur pour
tout le reste de la plateforme, sans nouveau seuil inventé pour l'occasion.
Fixer ce que « acquis » veut dire est une décision produit qu'ADR-015 réserve
déjà à un futur rôle Administrateur ; l'hériter plutôt que le redéfinir est
cohérent avec cette réserve.

### Ce qui devient l'exception, étendue d'un cran

`GET /api/v1/me/assessment` appelle désormais `give_to` avant de répondre :
c'est la seule lecture du projet qui écrit. Ce n'est pas une nouvelle
exception : l'examen était déjà, depuis sa création, le seul endroit où la
plateforme s'assigne quelque chose d'elle-même (`examen-initiation.md`).
L'étendre d'un cran — à chaque palier plutôt qu'à la seule activation — sert
le même argument plutôt que d'en introduire un nouveau, et reste silencieux
et idempotent exactement comme avant quand rien n'est dû.

### Ce qui ne change pas

- Le diagnostic garde son calcul de causes racines à un saut
  (`_root_causes`, `_unobserved_causes`), et la lecture montre que ce n'est
  pas une limite à combler : `_root_causes` examine **chaque** lacune, donc
  une chaîne A ⟵ B ⟵ C toutes trois en lacune produit les deux arêtes (A, B)
  et (B, C) **en un seul appel**, sans avoir besoin de plusieurs lectures
  successives — la reconstruction complète de la chaîne n'attendait déjà
  rien. Ce que le pas unique ne fait délibérément pas, c'est franchir un
  prérequis **jamais testé** pour aller chercher plus loin derrière lui :
  tant que rien ne l'a évalué, rien ne dit que le problème continue au-delà,
  et proposer une hypothèse à deux sauts de toute lecture contredirait
  ADR-015 (« une cause racine reste une hypothèse jusqu'à la
  réévaluation » — jusqu'à une lecture, pas jusqu'à une déduction sur la
  forme du graphe). Un module `app.referential.graph.unmet_ancestors` avait
  été esquissé pour une marche transitive puis retiré : aucun appelant sain
  n'en avait besoin une fois ce raisonnement fait jusqu'au bout.
- Le contenu de l'examen (`app.demo.examens`, `_examens()`) ne change pas
  d'un caractère. Seule sa politique de service change.
- La remédiation (`quick_repairs`) fait le travail de retest : une fiche
  complétée produit une lecture par les règles inchangées de l'étape 10, et
  `app.progress.child_progress` prenant déjà la dernière lecture par
  compétence toutes activités confondues, la compétence repasse
  « maîtrisée » sans mécanisme de retest séparé à construire.

## Conséquences

Un enfant qui valide 100 % à son premier palier ne reçoit rien de plus à ce
palier : la lecture suivante lui sert directement le palier suivant. Un
enfant qui échoue une compétence reçoit la remédiation qui vise son vrai
prérequis, comme avant ADR-021, mais ne revoit plus cette compétence dans un
examen tant que la remédiation ne l'a pas fait remonter comme maîtrisée.

`AssessmentPublic` gagne un champ optionnel `competency_codes`, additif : un
client qui l'ignore ne perd rien, un futur client peut s'en servir pour
afficher « palier 2 sur 3 ».

## Alternatives écartées

**Stocker un palier courant sur `auth_children`.** Aurait évité de
recalculer le graphe à chaque lecture, mais aurait recréé exactement ce
qu'ADR-015 refuse pour le diagnostic : une quatrième chose capable de
contredire les trois dont elle devrait dépendre, à tenir à jour à la main à
chaque nouvelle lecture de tentative.

**Généraliser `_root_causes` / `_unobserved_causes` à une marche
transitive complète.** Esquissée (`app.referential.graph.unmet_ancestors`),
puis retirée après avoir tracé le comportement existant jusqu'au bout :
`_root_causes` reconstruit déjà une chaîne entière de lacunes confirmées en
une seule lecture, et franchir un prérequis jamais testé pour en proposer un
plus profond reviendrait à avancer une hypothèse sans la moindre lecture
pour la soutenir — exactement ce qu'ADR-015 interdit. Ce n'est pas une
optimisation reportée faute de temps ; c'est un comportement qui aurait été
incorrect.
