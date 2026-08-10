# Étape 01.2, recréer les fichiers racine

## Prérequis

Rapport 01.1 terminé.

## Objectif

Créer les fichiers fondamentaux d’un dépôt professionnel vide.

## Travaux obligatoires


Créer depuis zéro :

- `README.md` ;
- `.gitignore` couvrant Node, Python, Next.js, FastAPI, environnements, IDE, Docker, logs, coverage, Playwright, stockage local et fichiers H5P temporaires ;
- `.editorconfig` ;
- `.gitattributes` ;
- `.env.example` sans secret ;
- `LICENSE` seulement si la licence du projet est décidée, sinon `docs/adr/ADR-000-licence-projet.md` en Proposed ;
- `SECURITY.md` ;
- `CONTRIBUTING.md` ;
- `CODE_OF_CONDUCT.md` si approprié ;
- `AGENTS.md` pointant vers le dossier steps.

Le README doit présenter produit, stack, prérequis, démarrage futur, arborescence, sécurité et statut actuel.


## Critères d’acceptation


- [ ] Tous les fichiers sont cohérents avec la stack finale.
- [ ] `.gitignore` exclut secrets, builds et données temporaires.
- [ ] `.env.example` ne contient aucune valeur réelle.
- [ ] Le README ne prétend pas que l’application est déjà fonctionnelle.


## Livrables

Fichiers racine et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
