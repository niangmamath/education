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

Terminé, avec un écart assumé par rapport au prompt.

`diagnostic/service.py:_tree` a bien été remplacé par un appel à
`referential.graph.load`, ce qui partage la lecture du graphe entre l'examen
et le diagnostic et supprime la requête dupliquée. En revanche
`_root_causes` et `_unobserved_causes` **n'ont pas** été réécrites pour
marcher à plusieurs sauts, et ce n'est pas un renforcement reporté faute de
temps : la lecture montre que `_root_causes` reconstruit déjà une chaîne
entière de lacunes confirmées en une seule passe, puisqu'elle examine chaque
lacune et trouve donc chaque arête indépendamment. Ce que le pas unique ne
fait délibérément pas, c'est franchir un prérequis **jamais testé** pour
aller chercher plus loin derrière lui — avancer une hypothèse à deux sauts
de toute lecture contredirait ADR-015. Un module
`app.referential.graph.unmet_ancestors` avait été esquissé pour cette marche
transitive puis retiré, faute d'appelant sain qui en aurait eu besoin. Détail
complet dans ADR-021.
