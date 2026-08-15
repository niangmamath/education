# Prérequis transverse, runtime de contenu

## Objectif

Rendre un paquet H5P vérifié réellement jouable, servi depuis une origine isolée
avec sa CSP, sans que le contenu puisse atteindre l'application.

## Origine de ce travail

Il ne figurait pas au découpage initial. Trois étapes présupposent un runtime de
contenu sans qu'aucune ne le construise : 11.2 parle de « ne pas exposer
l'identité au runtime de contenu », 13.1 d'une « activité à reprendre », et 16.1
teste les activités de bout en bout.

Il a d'abord été rattaché au début de l'étape 11, avec un décalage de l'étape 10
après elle. **Ce décalage était une erreur** : l'objectif de 11.3 est de produire
des agrégats « à partir des événements **et résultats** », et ces résultats sont
ceux de 10.3. L'étape 11 dépend de l'étape 10, pas l'inverse. Le raisonnement
initial — une tentative n'a de sens qu'une fois un contenu jouable — justifiait
de faire le runtime en premier, pas d'inverser deux étapes.

Ce travail n'est donc le contenu d'aucune des deux : c'est un **prérequis
commun**, fusionné avant elles. Ordre rétabli et écart assumé validés par le
propriétaire le 15 août 2026.

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
- tentatives et résultats, qui sont l'étape 10 ;
- intégration web, qui suppose la session entre deux origines et vient avec
  l'étape 13 ;
- antivirus, condition 2 d'ADR-012 pour la production.

## Statut

Terminé. Origine isolée avec CSP, tickets vérifiés par `auth_request`, commandes
`deploy-runtime` et `deploy`, 23 tests dédiés. Éprouvé sur la pile vivante :
contenu et bibliothèques servis avec ticket, `403` sans, `403` pour un ticket
d'un autre contenu. Validation consignée dans
`rapport_2026-08-15_1630_runtime_contenu.md`.
