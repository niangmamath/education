# Rapport de réalisation

## Métadonnées

- Étape : `03_infrastructure_locale_ci`
- Sous-étape : `01_docker_compose`
- Date et heure : 11 août 2026, 17:09
- Agent : Cheikh Ahmed Tidiane Sarr NDIAYE avec M365 Copilot
- ID du planning : `P0-05A`
- Branche : `main`
- Statut : **Terminé**

## Objectif

Mettre en place une infrastructure locale Docker Compose reproductible sous WSL Ubuntu 24.04 pour StudentConnect.

## État initial observé

- Conflit entre PostgreSQL Docker et le port `5432` de l’hôte.
- Volume PostgreSQL déjà initialisé avec un rôle différent de `studentconnect`.
- Premiers scripts préparés pour PowerShell alors que le projet est exécuté dans WSL.
- API et worker non validés de bout en bout.
- Ancienne configuration MinIO et rapports 03 non fiables.

## Travaux réalisés

- Création du réseau Docker `studentconnect_network`.
- Configuration de PostgreSQL 17 sans publication du port `5432` sur l’hôte.
- Configuration de Redis 7 avec persistance locale.
- Configuration de MinIO pour le développement local.
- Ajout d’un service idempotent `storage-init`.
- Exécution de FastAPI avec Uvicorn dans le conteneur `api`.
- Exécution du worker Celery dans le conteneur `worker`.
- Réinitialisation volontaire des volumes locaux devenus incohérents.
- Alignement des variables `.env.example` avec Docker Compose.
- Correction et validation de CORS pour `http://localhost:3000`.
- Normalisation du point d’entrée FastAPI sur `app.main:app`.

## Services validés

- PostgreSQL : `healthy`.
- Redis : `healthy`.
- MinIO : `healthy`.
- FastAPI : `healthy`.
- Worker Celery : `running`.
- `storage-init` : `Exited (0)`.

## Vérifications exécutées

```text
PostgreSQL readiness : accepting connections
Base active          : studentconnect
Rôle actif           : studentconnect
Redis                 : PONG
FastAPI               : {"status":"live"}
Celery inspect ping   : pong
Tâche Celery          : studentconnect.health.ping → pong
```

## Buckets créés

- `studentconnect-h5p-packages`
- `studentconnect-h5p-runtime`
- `studentconnect-media`
- `studentconnect-private-evidence`
- `studentconnect-thumbnails`

Les cinq buckets sont privés. Les logs du service `storage-init` confirment la création et l’application de la politique privée.

## Problèmes rencontrés et corrigés

- Conflit du port PostgreSQL 5432.
- Mauvais rôle dans le volume PostgreSQL existant.
- Mélange entre scripts PowerShell et WSL.
- Valeur `CORS_ORIGINS` non décodable par Pydantic Settings.
- Double point d’entrée FastAPI.
- Middleware CORS absent de l’application exécutée par Docker.
- Test CORS incorrect, car il ne transmettait aucun en-tête `Origin`.

## Critères d’acceptation

- [x] PostgreSQL est healthy.
- [x] Redis est healthy.
- [x] MinIO est healthy.
- [x] L’API est healthy.
- [x] Le worker Celery est opérationnel.
- [x] Les cinq buckets sont créés et privés.
- [x] PostgreSQL ne provoque plus de conflit de port sur l’hôte.
- [x] CORS simple et preflight sont validés.

## Livrables principaux

- `docker-compose.yml`
- `apps/api/Dockerfile.dev`
- `apps/api/Dockerfile.worker`
- `infrastructure/scripts/create_minio_buckets.sh`
- `infrastructure/scripts/reset_step03.sh`
- `.env.example`
