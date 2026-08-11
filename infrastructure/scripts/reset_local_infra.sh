#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/.."

echo "Resetting local infrastructure: stopping containers and removing volumes (explicit confirmation required)."

read -p "This will remove named volumes defined in docker-compose.yml (pgdata, redisdata, miniodata). Are you sure? (yes/NO) " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted. No changes made."
  exit 0
fi

if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
else
  DC_CMD="docker compose"
fi

${DC_CMD} down -v

echo "Volumes removed. You can now run '${DC_CMD} up -d' to recreate containers." 
