# 06.4, Clôture identité et famille

## Objectif

Valider migrations, sécurité, tests, API CI, Secret Scan, documentation et fusion.

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

En cours. Validation locale complète et rapport produit dans
`rapport_2026-08-14_cloture_etape_06.md`, branche poussée. Restent l’ouverture de
la Pull Request, que l’agent ne peut pas créer faute de l’outil `gh`, puis les
contrôles distants et la fusion vers `main`, qui appartiennent au propriétaire.
