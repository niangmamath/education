# Import du référentiel

## Périmètre

Cette page décrit comment une édition du référentiel entre dans la base, ce que
l'import vérifie avant d'écrire, pourquoi le rejouer ne produit pas de doublon,
et comment une édition est mise en vigueur. La modélisation est décrite dans
`referentiel-competences.md`, les lectures dans `api-referentiel.md`.

## Ce qu'« idempotent » veut dire ici

Le référentiel est versionné dans son ensemble : une **version** est une édition
cohérente, et les traces des étapes 10 à 12 désignent les compétences d'une
édition précise. Un import ne peut donc pas se contenter d'insérer.

Le fichier décrit **l'état voulu d'une édition**. L'import fait correspondre la
base à ce fichier :

- une ligne que le fichier ajoute est créée ;
- une ligne qu'il modifie est mise à jour ;
- une ligne qu'il ne mentionne plus est **supprimée** ;
- une ligne identique n'est pas touchée.

Rejouer le même fichier ne rapporte donc rien à faire. C'est la définition
retenue de l'idempotence : non pas « le second import ne plante pas », mais « la
base après deux imports est exactement la base après un seul ».

L'identité d'une ligne, entre le fichier et la base, est son **code métier**.
Déplacer une compétence d'un domaine à un autre met à jour la ligne existante et
lui conserve son `id`, ce qui compte pour les traces qui la citeront.

## Une version publiée est immuable

L'import ne travaille que sur un brouillon.

| Statut de la version visée | Ce que fait l'import |
|---|---|
| absente | crée la version en `draft`, puis la remplit |
| `draft` | réconcilie le brouillon avec le fichier |
| `published` | **refuse**, code de retour 3 |
| `archived` | **refuse**, code de retour 3 |

Le refus n'est pas une prudence excessive. Une tentative enregistrée en 10, un
événement xAPI en 11, un diagnostic en 12 pointent vers une compétence d'une
édition publiée ; corriger cette édition sur place changerait rétroactivement le
sens de traces déjà écrites. Un programme corrigé s'importe sous un **nouveau
code de version**, que l'on publie ensuite à la place de l'ancienne.

L'import ne publie jamais. Mettre une édition en vigueur est un acte distinct,
décrit plus bas.

## Le fichier

Un fichier JSON, écrit à la main, qui ne parle qu'en codes métier et jamais en
identifiants de base :

```json
{
  "version": { "code": "fictif-2026-01", "label": "Référentiel fictif 2026-01" },
  "levels":   [ { "code": "cp", "label": "Cours préparatoire", "position": 1 } ],
  "subjects": [
    { "code": "math", "label": "Mathématiques", "position": 1,
      "domains": [ { "code": "math-num", "label": "Nombres et calcul", "position": 1 } ] }
  ],
  "competencies": [
    { "code": "cp-math-num-01", "label": "Dénombrer une collection jusqu’à 100",
      "description": null, "position": 1,
      "level": "cp", "domain": "math-num", "prerequisites": [] }
  ]
}
```

Un fichier qui ne cite que des codes se relit, se compare d'une édition à
l'autre et se rejoue contre une base vide.

**Une clé inconnue est refusée, pas ignorée.** Un référentiel s'écrit à la main,
et une clé mal orthographiée silencieusement écartée est précisément la perte
qu'un import ne doit pas couvrir.

## Ce que la validation vérifie

Tout est vérifié avant la moindre écriture, et **toutes les erreurs sont rendues
en une seule passe** : un fichier écrit à la main mérite la liste complète de
ses fautes, pas une par exécution.

| Vérification | Pourquoi ici |
|---|---|
| forme des codes, des intitulés et des rangs | Pydantic, valeur par valeur |
| code déclaré deux fois dans l'édition | la base le refuserait, mais sans dire quelle ligne |
| deux rangs identiques entre frères | l'ordre serait indéfini, or l'ordre scolaire existe |
| niveau ou domaine non déclaré dans le fichier | la clé étrangère composite refuserait sans nommer la ligne |
| prérequis non déclaré, ou compétence son propre prérequis | idem, et la contrainte `CHECK` ne dit pas où |
| **cycle de prérequis** | **aucune contrainte SQL ne peut l'exprimer** |

La dernière ligne est la seule vérification sans équivalent en base. `A` requiert
`B` qui requiert `A` forme deux lignes parfaitement légales, prises séparément.
Un tel cycle laisserait le moteur de remédiation de l'étape 12 sans point
d'entrée : chaque compétence de la boucle attendrait une autre compétence de la
même boucle. La détection se fait par un parcours en profondeur, itératif pour
ne pas dépendre de la limite de récursion de Python, et une même boucle trouvée
depuis trois départs n'est signalée qu'une fois.

Le rapport d'erreurs nomme la ligne fautive :

```text
Fichier refusé, 3 erreurs :
  - levels[1].code : code « cp » déjà déclaré par levels[0]
  - competencies[1].domain : le domaine « math-geo » n’est pas déclaré dans ce fichier
  - competencies[0].prerequisites : cycle de prérequis : cp-math-num-01 → cp-math-num-02 → cp-math-num-01
```

## La commande

```bash
# essai à blanc, rien n’est écrit
docker compose exec -T api python -m app.referential import seeds/referential/fictif-2026-01.json

# écriture
docker compose exec -T api python -m app.referential import seeds/referential/fictif-2026-01.json --apply
```

```text
Fichier   : seeds/referential/fictif-2026-01.json
Version   : fictif-2026-01 « Référentiel fictif 2026-01 », brouillon créé
Niveaux     : 5 créés, 0 modifié, 0 supprimé
Matières    : 2 créées, 0 modifiée, 0 supprimée
Domaines    : 8 créés, 0 modifié, 0 supprimé
Compétences : 39 créées, 0 modifiée, 0 supprimée
Prérequis   : 36 créés, 0 supprimé
Import appliqué.
```

**L'essai à blanc est le comportement par défaut**, parce qu'un import réécrit
une édition entière, suppressions comprises. Il n'estime pas ce qui se
passerait : il fait tout le travail dans une transaction, `flush` compris, donc
toutes les contraintes de la base sont éprouvées, puis il annule. Un essai à
blanc qui annoncerait des changements que l'écriture ne saurait pas produire
serait pire que pas d'essai du tout.

| Code de retour | Sens |
|---|---|
| 0 | import réussi, ou essai à blanc mené à son terme |
| 1 | fichier illisible |
| 2 | fichier refusé, JSON invalide ou validation en échec |
| 3 | version publiée ou archivée, donc immuable |
| 4 | refus de la base de données |

## Publier une édition

L'import s'arrête au brouillon. Mettre une édition en vigueur est un second
verbe :

```bash
docker compose exec -T api python -m app.referential publish fictif-2026-01
```

```text
fictif-2026-01 « Référentiel fictif 2026-01 »
  brouillon → en vigueur
  fictif-2025-09 : en vigueur → archivée
```

Deux verbes plutôt qu'un drapeau, parce que les deux actes n'ont pas la même
portée : un import corrige un brouillon et peut être rejoué vingt fois pendant
qu'un programme s'écrit, une publication change ce que voit chaque lecteur. Une
frappe de trop à l'import ne peut donc rien mettre en vigueur.

L'édition remplacée est archivée **dans la même transaction**. Il n'existe aucun
instant où deux éditions sont publiées, ni aucun où il n'y en a plus.

| Cas | Réponse |
|---|---|
| brouillon nommé | publié, l'édition précédente est archivée |
| édition déjà en vigueur | rien à faire, la commande le dit et rend `0` |
| code inconnu | refus, code de retour 3 |
| édition archivée | refus, code de retour 3 |

Le dernier refus est délibéré. Remettre en vigueur une édition retirée
changerait le sens de toutes les traces enregistrées depuis son archivage ;
c'est une décision à part entière, pas le comportement par défaut d'une
commande.

## Pourquoi une commande et non une route

Un import écrit une édition entière d'un coup. La route d'administration qui
l'exposerait demanderait un rôle Administrateur et son authentification, que le
projet n'a pas encore et que l'étape 15, « administration, sécurité,
exploitation », prévoit. Une commande n'ouvre aucune surface réseau et se
journalise dans le terminal de qui l'exécute.

La commande emprunte psycopg2, déjà installé pour Alembic, plutôt qu'asyncpg :
un outil en ligne de commande n'a pas de boucle d'événements à servir et aucune
raison d'en ouvrir une.

## Le référentiel fictif livré

`apps/api/seeds/referential/fictif-2026-01.json` couvre les cinq niveaux du
primaire, deux matières, huit domaines, trente-neuf compétences et trente-six
liens de prérequis, ces derniers traversant les niveaux pour que l'arbre de
l'étape 12 ait de quoi se déployer.

Ce fichier est **entièrement fictif**. Ses intitulés s'inspirent de l'école
primaire française pour rester plausibles, mais il ne reproduit aucun programme
officiel et n'en tient pas lieu.

## Ce que cette page ne couvre pas

- Les lectures filtrées et paginées, décrites dans `api-referentiel.md`.
- Aucune comparaison entre deux éditions : le code métier stable la rendra
  possible, rien ne la demande encore.
- Aucun lien vers les activités H5P, qui relève de l'étape 08.
