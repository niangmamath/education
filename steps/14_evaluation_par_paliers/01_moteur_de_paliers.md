# 14.1, Moteur de paliers

## Objectif

Construire le module partagé qui lit le graphe de prérequis du référentiel
publié et en tire, pour une classe donnée, la liste des compétences prêtes à
être testées maintenant — le « palier courant ».

## Prérequis

- étape précédente clôturée ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels ;
- décisions et ADR concernés relus, notamment ADR-015 et ADR-018.

## Livrables

- `app/referential/graph.py` : `load(db, level_code=None)` charge les
  compétences et arêtes de prérequis de l'édition publiée, bornées à une
  classe si demandé ; `CompetencyGraph.frontier(scope_codes, mastered,
  tested, in_scope_edges_only=True)` rend les codes prêts à tester, ordonnés
  comme le programme les enseigne ; `CompetencyGraph.unmet_ancestors(code,
  mastered, tested)` marche le graphe en profondeur, sans restriction de
  classe, pour trouver la vraie cause racine à plusieurs sauts.
- `app/assessment/tiers.py:next_sitting(db, child)` : combine `graph.load`
  et `progress.child_progress` pour rendre les codes à servir maintenant, ou
  une liste vide si rien n'est dû.
- Tests d'intégration contre PostgreSQL réel : arêtes intra-classe vs
  inter-classe, chaîne de prérequis à plusieurs sauts, ordre déterministe.

## Hors périmètre

- toute modification du schéma du référentiel (aucune migration) ;
- l'examen lui-même et sa route (étape 14.2) ;
- le diagnostic existant (étape 14.3) ;
- la construction de cours (étape 15, non ouverte).

## Contrôles

- état Git et diff propres ;
- formatage, lint, typage et tests ;
- inspection des réponses et absence de secrets ;
- revue indépendante avant commit.

## Statut

Terminé.
