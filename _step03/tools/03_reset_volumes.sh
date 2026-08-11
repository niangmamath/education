#!/usr/bin/env bash
set -Eeuo pipefail
echo "AVERTISSEMENT: cette commande supprime les volumes locaux PostgreSQL, Redis et MinIO."
read -r -p "Taper exactement RESET-LOCAL pour continuer: " answer
[[ "$answer" == "RESET-LOCAL" ]] || { echo "Annule."; exit 0; }
docker compose down --remove-orphans
for volume in studentconnect_postgres_data studentconnect_redis_data studentconnect_storage_data; do
  if docker volume inspect "$volume" >/dev/null 2>&1; then
    docker volume rm "$volume"
  fi
done
echo "Volumes locaux supprimes."
