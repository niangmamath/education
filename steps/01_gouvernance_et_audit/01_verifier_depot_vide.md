# Étape 01.1, vérifier le dépôt vidé

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Confirmer que la reconstruction démarre réellement depuis zéro.

## Travaux obligatoires


1. Exécuter `git status`, identifier la branche et le remote.
2. Lister tous les fichiers visibles et cachés.
3. Confirmer que le dépôt ne contient plus ancien code, migrations, secrets, builds ou caches.
4. Vérifier que `.git/` existe encore et que le remote pointe vers le bon dépôt.
5. Ne rien initialiser pendant cette sous-étape.
6. Documenter tout fichier résiduel et proposer son traitement.


## Critères d’acceptation


- [ ] Le dépôt et le remote sont identifiés.
- [ ] Aucun fichier résiduel n’est ignoré dans l’analyse.
- [ ] Aucun secret n’est affiché en clair.
- [ ] Une décision explicite existe pour chaque résidu.


## Livrables

`docs/audit/depot-vide.md` et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
