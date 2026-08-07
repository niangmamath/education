# Prompt 01.1, auditer le dépôt et consolider l’état réel

Lis `PROMPT_GENERAL.md` et `etat.md`. Inspecte intégralement le dépôt `StudentConnect` sans modifier de code métier.

## Objectifs

- inventorier les fichiers, branches, dépendances et configurations ;
- identifier ce qui existe réellement versus ce qui est seulement documenté ;
- vérifier l’absence de secrets et de données réelles ;
- relever les divergences entre le dépôt et le cahier des charges technique ;
- proposer une arborescence cible compatible avec l’existant.

## Travaux

1. Exécuter `git status`, inspecter la branche et l’historique récent.
2. Lister l’arborescence et les fichiers de configuration.
3. Identifier la stack actuelle et les versions.
4. Chercher `.env`, secrets, tokens, bases locales et données sensibles.
5. Vérifier le README, `.gitignore`, licences et fichiers GitHub.
6. Comparer l’état réel avec la structure cible.
7. Ne supprimer ni déplacer aucun fichier.

## Livrables

- `docs/architecture/audit-initial.md`
- proposition de mise à jour de `etat.md`
- rapport de réalisation dans ce dossier

## Critères d’acceptation

- l’inventaire est complet ;
- les risques sont classés P0 à P3 ;
- aucun secret n’est affiché en clair dans le rapport ;
- les recommandations tiennent compte de l’existant.
