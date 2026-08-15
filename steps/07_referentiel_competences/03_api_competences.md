# 07.3, API du référentiel

## Objectif

Exposer des lectures filtrées et paginées des niveaux, matières et compétences.

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

En revue. Commande `publish` mettant une édition en vigueur, quatre routes de
lecture servant l'édition en vigueur seule, filtres par niveau, matière et
domaine, pagination plafonnée, et 37 tests dédiés livrés, contrôles locaux
verts. Aucune migration, le schéma n'ayant pas changé. Validation consignée dans
`rapport_2026-08-15_1430_api_referentiel.md`.
