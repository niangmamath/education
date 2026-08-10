# Étape 03.1, créer l’infrastructure locale

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Fournir PostgreSQL, Redis et stockage objet de développement.

## Travaux obligatoires


1. Créer `docker-compose.yml`.
2. Ajouter PostgreSQL avec health check et volume nommé.
3. Ajouter Redis avec health check.
4. Ajouter un stockage S3 compatible de développement. Ne pas figer ce choix comme production sans ADR.
5. Ajouter scripts de création des buckets locaux.
6. Créer un réseau dédié.
7. Documenter commandes démarrage, arrêt, reset et logs.
8. Ne pas exposer inutilement les services.


## Critères d’acceptation


- [ ] Tous les services deviennent healthy.
- [ ] Les volumes persistent après redémarrage.
- [ ] Le reset est explicite et non exécuté silencieusement.
- [ ] Aucun mot de passe réel n’est commité.


## Livrables

Infrastructure locale et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
