# Étape 02.3, initialiser FastAPI

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Créer le backend FastAPI typé et modulaire.

## Travaux obligatoires


1. Créer `apps/api` avec gestion moderne des dépendances Python.
2. Installer FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2, Alembic, psycopg, Redis, Celery et dépendances de test.
3. Créer la structure `app/api/v1`, `core`, `auth`, `families`, `students`, `competencies`, `assessments`, `gaps`, `contents`, `remediation`, `analytics`, `notifications`, `storage`, `workers`, `audit`.
4. Créer endpoints `/health/live` et `/health/ready`.
5. Configurer settings sans secret.
6. Ajouter logs structurés et trace_id minimal.
7. Ajouter tests de santé.


## Critères d’acceptation


- [ ] L’API démarre.
- [ ] OpenAPI est disponible.
- [ ] Les health checks sont testés.
- [ ] Les settings lisent l’environnement.
- [ ] Aucun service externe réel n’est requis pour le test unitaire.


## Livrables

API minimale et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
