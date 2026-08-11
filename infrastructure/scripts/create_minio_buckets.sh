#!/usr/bin/env bash
set -euo pipefail

# Loads .env if present (for MINIO credentials)
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs) || true
fi

## Prefer generic S3 creds; fall back to MINIO_* for backwards compatibility
MINIO_USER=${S3_ACCESS_KEY:-${MINIO_ROOT_USER:-minioadmin}}
MINIO_PASS=${S3_SECRET_KEY:-${MINIO_ROOT_PASSWORD:-minioadmin}}

# Determine endpoint from env or default
S3_ENDPOINT_VAL=${S3_ENDPOINT:-http://minio:9000}

# When calling from inside a container on the compose network, use the container hostname `minio`
# if the configured endpoint points to localhost. This avoids localhost resolving to the wrong container.
DOCKER_S3_ENDPOINT="$S3_ENDPOINT_VAL"
if [[ "$DOCKER_S3_ENDPOINT" =~ localhost ]] || [[ "$DOCKER_S3_ENDPOINT" =~ 127.0.0.1 ]]; then
  # replace host with 'minio'
  DOCKER_S3_ENDPOINT=$(echo "$DOCKER_S3_ENDPOINT" | sed -E 's#(https?://)(localhost|127\.0\.0\.1)(:[0-9]+)?#\1minio\3#')
fi



echo "Detecting Docker network for Compose..."
# Try to find a network that ends with 'studentconnect_local' created by compose
NETWORK=$(docker network ls --format "{{.Name}}" | grep "studentconnect_local$" || true)
if [ -z "$NETWORK" ]; then
  # fallback to the plain name
  NETWORK=studentconnect_local
fi

echo "Using network: $NETWORK"

S3_BUCKET_VAL=${S3_BUCKET:-studentconnect}
echo "Creating MinIO bucket '${S3_BUCKET_VAL}'..."
## Wait for MinIO HTTP health endpoint to be ready
# Derive scheme and port
SCHEME="http"
if [[ "$S3_ENDPOINT_VAL" =~ ^([a-zA-Z]+):// ]]; then
  SCHEME="${BASH_REMATCH[1]}"
fi
PORT=9000
if [[ "$S3_ENDPOINT_VAL" =~ :([0-9]+) ]]; then
  PORT="${BASH_REMATCH[1]}"
fi
HEALTH_URL="$SCHEME://minio:${PORT}/minio/health/ready"
echo "Waiting for MinIO health endpoint: $HEALTH_URL"
ready=0
for i in $(seq 1 30); do
  if docker run --network "$NETWORK" --rm curlimages/curl:latest -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "MinIO HTTP endpoint ready"
    ready=1
    break
  fi
  echo "MinIO not ready yet ($i/30), retrying..."
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "Warning: MinIO health endpoint did not become ready, proceeding to creation attempts anyway"
fi

for i in $(seq 1 30); do
  # Try with AWS CLI container (S3 API) first
  if docker run --network "$NETWORK" --rm -e AWS_ACCESS_KEY_ID="${MINIO_USER}" -e AWS_SECRET_ACCESS_KEY="${MINIO_PASS}" -e AWS_REGION="${S3_REGION:-us-east-1}" amazon/aws-cli s3 --endpoint-url ${DOCKER_S3_ENDPOINT} mb s3://${S3_BUCKET_VAL} >/dev/null 2>&1; then
    echo "Bucket created (aws-cli) or already exists"
    exit 0
  fi

  # Fallback to mc if aws-cli not available or failed
  docker run --network "$NETWORK" --rm minio/mc:latest alias set local ${DOCKER_S3_ENDPOINT} "${MINIO_USER}" "${MINIO_PASS}" >/dev/null 2>&1 || true
  if docker run --network "$NETWORK" --rm minio/mc:latest mb local/${S3_BUCKET_VAL} >/dev/null 2>&1; then
    echo "Bucket created or already exists (mc)"
    exit 0
  fi

    echo "MinIO not ready, retrying... ($i)"
    sleep 2
  done

  echo "Failed to create bucket after retries — checking if bucket already exists..."
  # Final check: list buckets and see if our bucket exists
  if docker run --network "$NETWORK" --rm -e AWS_ACCESS_KEY_ID="${MINIO_USER}" -e AWS_SECRET_ACCESS_KEY="${MINIO_PASS}" -e AWS_REGION="${S3_REGION:-us-east-1}" amazon/aws-cli s3 ls --endpoint-url ${DOCKER_S3_ENDPOINT} 2>/dev/null | grep -q "${S3_BUCKET_VAL}"; then
    echo "Bucket already exists"
    exit 0
  fi

  # fallback: try mc ls
  if docker run --network "$NETWORK" --rm minio/mc:latest alias set local ${DOCKER_S3_ENDPOINT} "${MINIO_USER}" "${MINIO_PASS}" >/dev/null 2>&1 && docker run --network "$NETWORK" --rm minio/mc:latest ls local 2>/dev/null | grep -q "${S3_BUCKET_VAL}"; then
    echo "Bucket already exists (mc)"
    exit 0
  fi

  echo "Failed to create bucket after retries" >&2
  exit 1
