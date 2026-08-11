#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/.."

echo "Starting local infrastructure with docker compose..."

# Prefer docker compose v2 plugin if available
if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
else
  DC_CMD="docker compose"
fi

echo "Using: $DC_CMD"

# Start services detached
${DC_CMD} up -d

echo "Waiting for services to become healthy (sleeping 5s)..."
sleep 5

echo "Creating MinIO buckets (if MinIO available)..."
if [ -f infrastructure/scripts/create_minio_buckets.sh ]; then
  infrastructure/scripts/create_minio_buckets.sh || echo "Bucket creation script exited with non-zero status"
else
  echo "create_minio_buckets.sh not found; skipping"
fi

echo "Done. Use 'infrastructure/scripts/stop_local_infra.sh' to stop, or 'infrastructure/scripts/reset_local_infra.sh' to reset volumes." 
