# 03.1 - Docker Compose propre

## Objectif

Demarrer PostgreSQL, Redis, MinIO local, l'API FastAPI et le worker Celery dans le meme reseau Docker.

## Procedure

1. Copier `.env.example` vers `.env` et conserver des valeurs locales uniquement.
2. Si un ancien volume PostgreSQL existe avec un autre role, executer volontairement `infrastructure/scripts/reset_step03.ps1`.
3. Executer:

```bash
docker compose config --quiet
docker compose build api worker
docker compose up -d
docker compose ps
```

4. Verifier:

```bash
docker compose exec -T postgres pg_isready -U studentconnect -d studentconnect
docker compose exec -T postgres psql -U studentconnect -d studentconnect -c 'SELECT current_database(), current_user;'
docker compose exec -T redis redis-cli ping
docker compose logs --tail=100 storage-init
docker compose logs --tail=100 api
docker compose logs --tail=100 worker
curl --fail http://localhost:8000/health/live
```

## Decisions

- PostgreSQL n'est pas publie sur l'hote. L'API utilise `postgres:5432`.
- MinIO est un outil local seulement.
- L'API tourne dans Docker via Uvicorn.
- Le worker tourne dans Docker via Celery.

## Acceptation

- PostgreSQL, Redis, storage et API sont healthy.
- `storage-init` termine avec code 0.
- Le worker reste running.
- L'identite PostgreSQL est `studentconnect/studentconnect`.
- Les cinq buckets existent et restent prives.
