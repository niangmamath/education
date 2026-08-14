# 06.3, Création et accès Enfant

## Objectif

Permettre au Parent authentifié de créer un profil Enfant, hacher le PIN, connecter l’Enfant et garantir l’isolation familiale.

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

Terminé localement. Code, tests et documentation livrés, contrôles locaux verts,
migration `0003_family_code_child_status` vérifiée dans les deux sens, validation
consignée dans `rapport_2026-08-14_cloture_etape_06.md`. Reste la clôture distante,
traitée par 06.4.
