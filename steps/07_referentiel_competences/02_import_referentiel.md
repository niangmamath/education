# 07.2, Import contrôlé

## Objectif

Créer un import idempotent de référentiel fictif/versionné avec validation et rapport d’erreurs.

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

En revue. Import réconciliant un brouillon, validation complète avec détection
des cycles de prérequis, commande en ligne à essai à blanc par défaut,
référentiel fictif de trente-neuf compétences et 54 tests dédiés livrés,
contrôles locaux verts. Aucune migration, le schéma n'ayant pas changé.
Validation consignée dans `rapport_2026-08-14_2100_import_referentiel.md`.
