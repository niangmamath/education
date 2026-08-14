# Référentiel de compétences

## Périmètre

Cette page décrit la sous-étape 07.1 : la modélisation des niveaux, matières,
domaines et compétences, avec leurs identifiants stables et leurs contraintes.
L'import relève de 07.2 et l'API de lecture de 07.3 ; aucune route n'est exposée
ici.

## Le référentiel est versionné dans son ensemble

Une **version** est une édition cohérente du référentiel : elle porte ses propres
niveaux, ses matières, ses domaines et ses compétences. Réimporter un programme
crée une nouvelle version au lieu de modifier celle que des résultats désignent
déjà.

C'est la condition pour que les étapes suivantes tiennent. Une tentative
enregistrée en 10, un événement xAPI en 11, un diagnostic en 12 pointent tous vers
une compétence ; si le référentiel était modifié sur place, ces traces
changeraient de sens rétroactivement.

| Statut | Sens | Combien |
|---|---|---|
| `draft` | En préparation, jamais servi | autant que voulu |
| `published` | En vigueur | **un seul à la fois** |
| `archived` | A servi, conservé pour les traces qui le citent | autant que voulu |

L'unicité du statut publié n'est pas une règle applicative : c'est un index unique
partiel, `WHERE status = 'published'`. Deux versions publiées laisseraient chaque
lecteur deviner laquelle fait foi, donc la base l'interdit.

## Quatre concepts, quatre tables

```text
ref_versions        une édition du référentiel
├── ref_levels      CP, CE1, CE2, CM1, CM2
├── ref_subjects    Mathématiques, Français
│   └── ref_domains Nombres et calcul, Géométrie, Grammaire
└── ref_competencies  rattachée à un domaine ET à un niveau
    └── ref_competency_prerequisites  l'arbre de compétences
```

ADR-004 esquissait une table unique `skills` auto-référencée. Quatre tables
explicites ont été retenues : les lectures filtrées de 07.3 deviennent des
jointures directes, et rien ne permet plus de ranger une matière sous une
compétence. Le schéma dit ce qu'il modélise.

Chaque table porte un `position` entier, parce que l'ordre scolaire n'est ni
alphabétique ni déductible du code : CE2 vient après CE1 et avant CM1.

## Ce qui rend une version étanche

Chaque ligne fille répète le `version_id` de son parent et le référence par une
**clé étrangère composite** :

```sql
FOREIGN KEY (domain_id, version_id)
    REFERENCES ref_domains (id, version_id)
```

Les contraintes `UNIQUE (id, version_id)` de chaque table parente n'ont pas
d'autre raison d'être : elles sont la cible de ces références composites. Sans
elles, `domain_id` seul suffirait, et une compétence de l'édition 2026 pourrait
pointer vers un domaine de l'édition 2025 sans que rien ne s'y oppose.

L'étanchéité est donc une propriété de la base, pas une promesse du code
d'import. Elle vaut aussi pour l'arbre de prérequis : les deux extrémités d'un
lien appartiennent forcément à la même version.

## Identifiants

Chaque entité porte deux identifiants, et ils ne servent pas à la même chose :

- l'`id` UUID, clé technique, qui change à chaque nouvelle version ;
- le `code`, identifiant métier stable, unique **dans sa version**. `cm1-math-num-01`
  désigne la même compétence d'une édition à l'autre, ce qui permettra à l'import
  de 07.2 d'être idempotent et de comparer deux éditions.

L'unicité du code est familiale au référentiel, si l'on peut dire : deux versions
peuvent nommer `cm1-math-num-01`, une même version ne le peut pas deux fois.

## L'arbre de compétences

`ref_competency_prerequisites` porte les arêtes : une compétence en requiert une
autre. La paire est la clé primaire, donc un prérequis ne peut pas être déclaré
deux fois, et une contrainte `CHECK` interdit qu'une compétence soit son propre
prérequis.

**Un cycle plus long, où A requiert B qui requiert A, dépasse ce qu'une contrainte
SQL peut exprimer.** Sa détection appartient à la validation de l'import, en 07.2.
C'est une limite connue et non un oubli : la modéliser en base demanderait un
déclencheur récursif dont le coût dépasse le bénéfice à ce stade.

Cette table est modélisée maintenant, alors que la fiche 07.1 ne nomme que quatre
concepts, parce que « détection de lacunes via arbre de compétences » est une
décision finale du projet et que l'étape 12 en dépend. Aucune route ne l'expose
avant l'heure.

## Suppression

Supprimer une version emporte tout ce qu'elle contient, par cascade. C'est
volontaire : une édition à moitié supprimée serait pire qu'une édition archivée.
La règle du projet reste de basculer une version en `archived` plutôt que de la
supprimer dès que des résultats la citent.

## Ce que 07.1 ne fait pas

- Aucune donnée : ni contenu réel, ni jeu de démonstration. L'import arrive en 07.2.
- Aucune route : les lectures filtrées et paginées arrivent en 07.3.
- Aucun lien vers les activités H5P, qui relève de l'étape 08.
- Aucune détection de cycle dans l'arbre, qui relève de la validation d'import.
