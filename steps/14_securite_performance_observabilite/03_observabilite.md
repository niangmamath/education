# Étape 14.3, configurer l’observabilité

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Rendre les incidents diagnosables sans exposer de données sensibles.

## Travaux obligatoires


1. Logs JSON avec trace_id.
2. Corrélation frontend, API et worker.
3. Métriques santé API, Celery, Redis et uploads.
4. Suivi erreurs abstrait par fournisseur configurable.
5. Alertes sur queue et ingestion en échec.
6. Redaction des données sensibles.


## Critères d’acceptation


- [ ] Une requête peut être suivie bout en bout.
- [ ] Aucun PIN, mot de passe ou statement sensible complet dans les logs.
- [ ] Health checks exploitables.
- [ ] Échec worker visible.


## Livrables

Observabilité et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
