# Étape 04.1, préparer les paquets H5P de test

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Constituer un jeu de test légal et documenté pour le spike.

## Travaux obligatoires


1. Sélectionner un ou deux paquets H5P autorisés.
2. Enregistrer source, auteur, licence, type de contenu, version et checksum.
3. Ne pas commiter un paquet si la licence ou la taille ne le permet pas. Prévoir un script/document de récupération.
4. Identifier les bibliothèques H5P requises.
5. Créer un paquet volontairement invalide uniquement pour les tests locaux.


## Critères d’acceptation


- [ ] Provenance et licence documentées.
- [ ] Aucun contenu sans droit n’est commité.
- [ ] Checksums enregistrés.
- [ ] Types H5P identifiés.


## Livrables

`docs/architecture/h5p-test-matrix.md` et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
