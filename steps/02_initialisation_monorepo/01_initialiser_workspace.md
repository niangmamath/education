# Étape 02.1, initialiser le monorepo

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Créer la structure du monorepo et les outils de workspace.

## Travaux obligatoires


1. Créer `apps/web`, `apps/api`, `packages/ui`, `packages/schemas`, `packages/config`, `infrastructure`, `docs` et `steps` si absent.
2. Choisir et documenter le gestionnaire Node, recommandé `pnpm`.
3. Créer `package.json` racine et workspace.
4. Ajouter scripts racine `dev`, `build`, `lint`, `typecheck`, `test` et `format` sans masquer les erreurs.
5. Ajouter un outil de tâches de monorepo seulement si nécessaire, recommandé Turborepo, sinon documenter l’absence.
6. Ne pas initialiser encore les fonctionnalités métier.


## Critères d’acceptation


- [ ] Le workspace détecte `apps` et `packages`.
- [ ] Les scripts racine sont cohérents.
- [ ] Aucune dépendance superflue n’est ajoutée.
- [ ] L’arborescence correspond au cahier définitif.


## Livrables

Monorepo minimal et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
