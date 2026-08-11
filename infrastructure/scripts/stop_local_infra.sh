#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/.."

echo "Stopping local infrastructure..."

if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
else
  DC_CMD="docker compose"
fi

${DC_CMD} down

echo "Stopped." 
