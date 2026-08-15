# 08.2, Contenus H5P autorisés

## Objectif

Intégrer uniquement les types validés par ADR-012, sans éditeur ni import non sécurisé.

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

Terminé. Vérification des paquets sans extraction, allowlist ADR-012 doublée
par une contrainte en base, commandes `register` et `check`, 31 tests. Contrôles locaux verts.
Validation consignée dans `rapport_2026-08-15_1530_catalogue.md`.
