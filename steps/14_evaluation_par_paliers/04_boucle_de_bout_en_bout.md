# 14.4, Boucle de bout en bout

## Objectif

Déclencher réellement le service par palier depuis l'API, et prouver la
boucle complète : palier servi, échec, remédiation, retest, palier suivant
débloqué — sans construire de mécanisme parallèle à celui de l'étape 10.

## Prérequis

- 14.2 et 14.3 clôturées ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels.

## Livrables

- `GET /api/v1/me/assessment` (`api/v1/assessment.py:read_my_assessment`)
  appelle `assessment.give_to(db, child)` avant de répondre. C'est la seule
  lecture du projet qui écrit ; décision assumée, à consigner dans l'ADR de
  14.5 : c'est l'endroit déjà unique où la plateforme s'auto-assigne
  (l'examen), la même exception déjà en vigueur, étendue d'un cran plutôt
  qu'une nouvelle créée.
- `AssessmentPublic` gagne un champ optionnel `competency_codes`.
- Confirmation que la retest après remédiation ne construit rien de
  nouveau : `POST /children/{id}/remediation` → `quick_repairs` existent
  déjà, et la fiche complétée produit un `AttemptResult` par les règles
  inchangées de l'étape 10 ; `progress.child_progress` prenant déjà la
  dernière lecture par compétence toutes activités confondues, la
  compétence repasse « maîtrisée » dès cette lecture.
- Test d'intégration bout en bout : enfant synthétique, palier 1 → échec sur
  une compétence → remédiation appliquée par le parent → fiche complétée →
  palier 2 servi à la lecture suivante, la compétence réparée exclue de
  toute nouvelle évaluation.

## Hors périmètre

- toute interface web nouvelle (les pages restent celles de l'étape 05) ;
- la construction de cours (étape 15, non ouverte).

## Contrôles

- état Git et diff propres ;
- formatage, lint, typage et tests ;
- test bout en bout rejoué sur la pile vivante ;
- revue indépendante avant commit.

## Statut

À faire.
