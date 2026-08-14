# 07.1, Référentiel scolaire

## Objectif

Modéliser niveaux, matières, domaines et compétences avec identifiants stables et contraintes.

## Prérequis

- étape précédente clôturée ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels ;
- décisions et ADR concernés relus.

## Livrables

- documentation de conception et décisions ;
- code minimal du périmètre ;
- migration réversible si le schéma change ;
- tests unitaires, intégration et autorisation ;
- rapport de validation reproductible.

## Hors périmètre

- toute fonctionnalité d’une étape ultérieure ;
- données personnelles réelles ;
- simulation non explicitement demandée ;
- contournement de sécurité ou de contrôle d’accès.

## Contrôles

- état Git et diff propres ;
- formatage, lint, typage et tests ;
- upgrade, downgrade puis retour au head si migration ;
- inspection des réponses et absence de secrets ;
- revue indépendante avant commit.

## Statut

En revue. Modèles, migration `0004_referential_competencies` réversible, 23 tests
dédiés et documentation de conception livrés, contrôles locaux verts. Validation
consignée dans `rapport_2026-08-14_1730_modeles_referentiel.md`.
