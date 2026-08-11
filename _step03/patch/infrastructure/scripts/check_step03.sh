#!/usr/bin/env bash
set -Eeuo pipefail
run() {
  local label="$1"; shift
  printf '\n== %s ==\n' "$label"
  "$@"
}
run "Validation Compose" docker compose config --quiet
run "Construction API et worker" docker compose build api worker
run "Demarrage" docker compose up -d
sleep 12
run "Etat des services" docker compose ps
run "PostgreSQL readiness" docker compose exec -T postgres pg_isready -U studentconnect -d studentconnect
run "PostgreSQL identity" docker compose exec -T postgres psql -U studentconnect -d studentconnect -c 'SELECT current_database(), current_user;'
run "Redis" docker compose exec -T redis redis-cli ping
run "Migration Alembic" docker compose exec -T api alembic upgrade head
run "Revision Alembic" docker compose exec -T api alembic current
run "Tests API" docker compose exec -T api python -m pytest tests -q
run "Celery ping" docker compose exec -T worker celery -A app.workers.celery_app:celery_app inspect ping
run "API live" curl --fail --silent http://localhost:8000/health/live
printf '\nTous les controles de l etape 03 ont reussi.\n'
