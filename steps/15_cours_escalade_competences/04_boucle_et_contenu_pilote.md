# 15.4, Boucle de bout en bout et contenu pilote

## Objectif

Éprouver le mécanisme sur un petit lot de compétences réelles, pour valider
la conception avant de s'engager sur la couverture complète des
cinquante-quatre compétences — suite prévue en travaux hors étape, comme
HORS-04 puis HORS-09 l'ont fait pour les fiches de remédiation.

## Prérequis

- 15.1, 15.2 et 15.3 terminées.

## Livrables

- 2 à 4 cours natifs pilotes (CI ou CP, français ou mathématiques), même
  gabarit qu'une fiche : une leçon puis 2 à 3 questions expliquées.
- Tests d'intégration contre PostgreSQL réel :
  - le cours et l'examen du palier suivant sont tous deux dus, et donc tous
    deux assignés, dès que le palier précédent est maîtrisé ;
  - passer l'examen directement, sans avoir ouvert le cours, reste possible
    et non bloqué ;
  - répondre à une question du cours ne modifie aucune lecture de
    compétence (`app.progress.child_progress` inchangé avant/après) ;
  - achever le cours (route générique) n'affecte pas non plus la maîtrise ;
  - un cours déjà testé (examen passé) ne réapparaît pas à la lecture
    suivante.

## Hors périmètre

- la couverture des cinquante-quatre compétences (dette assumée, à traiter
  hors étape) ;
- toute interface web dédiée au cours (les pages web restent les maquettes
  de l'étape 05, comme pour le reste du backend).

## Contrôles

- état Git et diff propres ;
- Ruff, Mypy, Pytest ;
- scénario rejoué sur la pile Docker Compose de ce worktree.

## Deux défauts trouvés par la suite de tests complète, corrigés

- `quick_repairs` avait d'abord été restreint au seul type `remediation`,
  ce qui aurait empêché de proposer une réparation en H5P ou PhET —
  régression que `test_diagnostic_api.py` a révélée immédiatement. Corrigé
  en excluant seulement `assessment` et `course` plutôt qu'en restreignant
  à un seul type.
- `GET /catalog/kinds` et le filtre de `GET /catalog/activities`
  n'excluaient que `assessment` de ce qu'un parent peut parcourir. Un
  cours, donné automatiquement et jamais parcouru, rejoint l'exclusion.

## Statut

Terminé.
