# Étape 09.2, créer l’upload présigné

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Implémenter l’upload privé direct vers le stockage objet.

## Travaux obligatoires


1. Créer endpoint de demande d’upload.
2. Vérifier rôle créateur.
3. Générer clé serveur et URL présignée temporaire.
4. Exiger taille, checksum et extension.
5. Stocker métadonnées d’upload.
6. Créer callback de finalisation idempotent.
7. Tester upload valide, expiré et non autorisé.


## Critères d’acceptation


- [ ] Le navigateur ne reçoit pas de credentials S3.
- [ ] La clé d’objet est générée côté serveur.
- [ ] URL expire.
- [ ] Upload non autorisé rejeté.


## Livrables

Upload présigné et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
