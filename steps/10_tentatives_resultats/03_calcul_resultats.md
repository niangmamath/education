# 10.3, Calcul des résultats

## Objectif

Calculer les résultats selon des règles explicites, testées et rattachées aux compétences.

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

Terminé. Trois règles nommées sur des comptes, phrase explicative construite des mêmes
valeurs que celles stockées, aucune preuve ne concluant rien.
Validation consignée dans `rapport_2026-08-15_1820_tentatives.md`.
