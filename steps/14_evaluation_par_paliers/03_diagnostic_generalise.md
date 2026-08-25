# 14.3, Diagnostic généralisé

## Objectif

Faire marcher la logique existante « ne pas proposer une compétence tant que
son prérequis est en lacune » (DIA-05, `defer-behind-prerequisite`) sur le
graphe complet plutôt qu'à un seul saut, en réutilisant le moteur de paliers
de 14.1 au lieu d'une seconde implémentation.

## Prérequis

- 14.1 clôturée ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels ;
- ADR-015 relue.

## Livrables

- `diagnostic/service.py:_tree` remplacé par un appel à
  `referential.graph.load` (non borné).
- `_root_causes` et `_unobserved_causes` marchent via
  `graph.unmet_ancestors` au lieu d'un seul saut.
- Le seuil de maîtrise réutilisé pour « prérequis acquis » reste exactement
  celui déjà en vigueur (`RULE_ALL_CORRECT` / `OUTCOME_MASTERED`), sans
  nouveau seuil inventé.
- Suite `test_diagnostic_*` existante rejouée sans changement de résultat
  observable : c'est un renforcement, les chaînes se résolvaient déjà
  d'elles-mêmes sur des lectures successives (ADR-015).
- Nouveaux cas de test pour des chaînes de prérequis à plus d'un saut.

## Hors périmètre

- tout changement des cinq règles de diagnostic déjà publiées ;
- la remédiation elle-même (`quick_repairs`), réutilisée telle quelle ;
- la route ou le déclenchement de l'examen (étape 14.2, 14.4).

## Contrôles

- état Git et diff propres ;
- formatage, lint, typage et tests ;
- suite `test_diagnostic_*` complète verte, sans régression de comportement ;
- revue indépendante avant commit.

## Statut

À faire.
