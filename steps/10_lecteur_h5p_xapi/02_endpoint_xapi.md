# Étape 10.2, industrialiser la collecte xAPI

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Créer modèles, endpoint, déduplication et validation.

## Travaux obligatoires


1. Créer LearningSessions et XapiLogs.
2. Valider student, content et session.
3. Valider schéma minimal du statement.
4. Dédupliquer event_id.
5. Enregistrer avant projection.
6. Publier tâche Celery.
7. Ajouter rate limiting et limites de payload.
8. Tester événements valides, dupliqués, falsifiés et hors session.


## Critères d’acceptation


- [ ] Un événement valide est stocké une fois.
- [ ] Un événement falsifié est rejeté.
- [ ] La réponse API reste rapide.
- [ ] Le statement brut est conservé de façon limitée.


## Livrables

Collecte xAPI et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
