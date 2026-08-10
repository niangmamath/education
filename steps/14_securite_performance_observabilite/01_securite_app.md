# Étape 14.1, renforcer la sécurité

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Appliquer les contrôles de sécurité applicatifs.

## Travaux obligatoires


Vérifier cookies, CSRF selon architecture, CORS, CSP, rate limiting, autorisation objet, validation, logs, secrets, headers, dépendances et audit.

Créer un threat model simple couvrant auth, upload H5P, iframe, postMessage, S3 et xAPI.


## Critères d’acceptation


- [ ] Menaces et contrôles documentés.
- [ ] Autorisation familiale testée.
- [ ] CSP active.
- [ ] Aucun secret dans le dépôt.


## Livrables

Threat model, rapport sécurité et rapport de réalisation.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
