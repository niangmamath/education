#!/usr/bin/env bash

set -Eeuo pipefail

run() {
  local label="$1"
  shift

  printf '\n== %s ==\n' "$label"
  "$@"
}

run \
  "Validation Compose" \
  docker compose config --quiet

run \
  "Construction API et worker" \
  docker compose build api worker

run \
  "Démarrage des services" \
  docker compose up -d

sleep 12

run \
  "État des services" \
  docker compose ps

run \
  "PostgreSQL readiness" \
  docker compose exec -T postgres \
  pg_isready \
  -U studentconnect \
  -d studentconnect

run \
  "PostgreSQL identity" \
  docker compose exec -T postgres \
  psql \
  -U studentconnect \
  -d studentconnect \
  -c "SELECT current_database(), current_user;"

run \
  "Redis" \
  docker compose exec -T redis \
  redis-cli ping

run \
  "État initialisation stockage" \
  docker compose ps -a storage-init

run \
  "Migration Alembic" \
  docker compose exec -T api \
  alembic upgrade head

run \
  "Révision Alembic" \
  docker compose exec -T api \
  alembic current

run \
  "Format Ruff backend" \
  docker compose exec -T api \
  ruff format --check .

run \
  "Ruff backend" \
  docker compose exec -T api \
  ruff check .

run \
  "Mypy backend" \
  docker compose exec -T api \
  mypy app --ignore-missing-imports

run \
  "Tests backend" \
  docker compose exec -T api \
  python -m pytest tests -q

run \
  "Celery ping" \
  docker compose exec -T worker \
  celery \
  -A app.workers.celery_app:celery_app \
  inspect ping

run \
  "API live" \
  curl \
  --fail \
  --silent \
  http://localhost:8000/health/live

printf '\n'

run \
  "TypeScript frontend" \
  pnpm \
  --filter @studentconnect/web \
  run typecheck

run \
  "ESLint frontend" \
  pnpm \
  --filter @studentconnect/web \
  run lint

run \
  "Build frontend" \
  env NEXT_TELEMETRY_DISABLED=1 \
  pnpm \
  --filter @studentconnect/web \
  run build

printf '\nTous les contrôles de l étape 03 ont réussi.\n'
