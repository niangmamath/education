# Étape 06.2, implémenter l’auth Parent

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Créer inscription, vérification, connexion et sessions opaques.

## Travaux obligatoires


1. Hacher les mots de passe avec Argon2id.
2. Créer inscription Parent.
3. Préparer vérification d’email avec provider abstrait et mode local.
4. Créer sessions opaques dans Redis.
5. Déposer cookie HttpOnly, Secure selon environnement, SameSite et rotation.
6. Ajouter logout, révocation et rate limiting.
7. Ajouter tests sécurité et API.


## Critères d’acceptation


- [ ] Aucun token de session exposé à JavaScript.
- [ ] Rotation après connexion.
- [ ] Logout révoque Redis.
- [ ] Rate limiting testé.


## Livrables

Auth parent et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
