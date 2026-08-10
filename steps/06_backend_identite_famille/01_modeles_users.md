# Étape 06.1, créer les modèles utilisateurs

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Implémenter Users, profils et rattachements familiaux.

## Travaux obligatoires


1. Créer enums de rôles et statuts.
2. Implémenter Users, ParentProfiles, StudentProfiles et ParentStudentLinks.
3. Ajouter contraintes, indexes et timestamps.
4. Créer migration Alembic.
5. Ajouter repositories et services.
6. Ajouter tests de contraintes et relations.


## Critères d’acceptation


- [ ] Contrainte unique parent-enfant.
- [ ] Enfant sans email autorisé.
- [ ] Suppression ou révocation respectent l’historique.
- [ ] Migration testée.


## Livrables

Modèles d’identité et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
