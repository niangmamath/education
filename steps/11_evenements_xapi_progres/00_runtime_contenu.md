# 11.0, Runtime de contenu

## Objectif

Rendre un paquet H5P vérifié réellement jouable, servi depuis une origine isolée
avec sa CSP, sans que le contenu puisse atteindre l'application.

## Origine de la sous-étape

Elle ne figurait pas au découpage initial. Trois étapes présupposent un runtime
de contenu sans qu'aucune ne le construise : 11.2 parle de « ne pas exposer
l'identité au runtime de contenu », 13.1 d'une « activité à reprendre », et 16.1
teste les activités de bout en bout. Rattachement au début de l'étape 11 validé
par le propriétaire le 15 août 2026.

## Prérequis

- étape 09 clôturée, dette résorbée ;
- paquet H5P vérifié et enregistré par 08.2 ;
- bibliothèques et lecteur préparés hors ligne, ADR-012 condition 3.

## Livrables

- origine de contenu distincte, servie par nginx, avec CSP restrictive ;
- ticket de courte durée remplaçant le cookie de session, vérifié par
  `auth_request` ;
- commandes de déploiement des bibliothèques, du lecteur et d'un paquet ;
- page du lecteur remontant les événements par `postMessage` ;
- tests et rapport de validation.

## Hors périmètre

- ingestion des événements xAPI, qui est 11.1 ;
- intégration web, qui suppose la session entre deux origines et vient avec
  l'étape 13 ;
- antivirus, condition 2 d'ADR-012 pour la production.

## Statut

Terminé. Origine isolée avec CSP, tickets vérifiés par `auth_request`, commandes
`deploy-runtime` et `deploy`, 23 tests dédiés. Éprouvé sur la pile vivante :
contenu et bibliothèques servis avec ticket, `403` sans, `403` pour un ticket
d'un autre contenu. Validation consignée dans
`rapport_2026-08-15_1630_runtime_contenu.md`.
