#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(pwd)"
[[ -d "$ROOT/.git" ]] || { echo "Erreur: executer depuis la racine du depot Git." >&2; exit 1; }
[[ -d "$ROOT/apps/api" ]] || { echo "Erreur: apps/api introuvable." >&2; exit 1; }
[[ -d "$ROOT/apps/web" ]] || { echo "Erreur: apps/web introuvable." >&2; exit 1; }

branch="$(git branch --show-current)"
echo "Branche active: $branch"
if [[ -n "$(git status --short)" ]]; then
  echo "AVERTISSEMENT: changements non commites detectes:" >&2
  git status --short >&2
fi

stamp="$(date +%Y%m%d_%H%M%S)"
backup="$ROOT/_backup_step03_$stamp"
mkdir -p "$backup"

backup_targets=(
  docker-compose.yml
  apps/api/Dockerfile.dev
  apps/api/Dockerfile.worker
  apps/api/alembic.ini
  apps/api/alembic
  apps/api/app/core/db.py
  apps/api/app/workers/celery_app.py
  .github/workflows
  steps/03_infrastructure_locale_ci
)
for rel in "${backup_targets[@]}"; do
  src="$ROOT/$rel"
  if [[ -e "$src" ]]; then
    mkdir -p "$backup/$(dirname "$rel")"
    cp -a "$src" "$backup/$rel"
  fi
done

# Supprimer uniquement les prompts des etapes futures.
find "$ROOT/steps" -mindepth 1 -maxdepth 1 -type d \
  \( -name '0[4-9]_*' -o -name '1[0-6]_*' \) -print -exec rm -rf {} +

rm -rf "$ROOT/steps/03_infrastructure_locale_ci"

# Retirer les artefacts generes sans toucher au code source.
find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.tsbuildinfo' \) -delete

replace_targets=(
  docker-compose.yml
  apps/api/Dockerfile.dev
  apps/api/Dockerfile.worker
  apps/api/alembic.ini
  apps/api/alembic
  apps/api/app/core/db.py
  apps/api/app/workers/celery_app.py
  .github/workflows
  infrastructure/scripts/create_minio_buckets.ps1
  infrastructure/scripts/create_minio_buckets.sh
  infrastructure/scripts/reset_local_infra.sh
  infrastructure/scripts/start_local_infra.sh
  infrastructure/scripts/stop_local_infra.sh
)
for rel in "${replace_targets[@]}"; do
  rm -rf "$ROOT/$rel"
done

echo "Nettoyage termine. Sauvegarde: $backup"
echo "Etape suivante: bash _step03/tools/02_apply_patch.sh"
