#!/usr/bin/env bash
set -Eeuo pipefail
echo "AVERTISSEMENT: cette commande supprime les trois volumes locaux StudentConnect."
read -r -p "Taper RESET-LOCAL pour continuer: " answer
[[ "$answer" == "RESET-LOCAL" ]] || exit 0
docker compose down --remove-orphans
for v in studentconnect_postgres_data studentconnect_redis_data studentconnect_storage_data; do
  docker volume inspect "$v" >/dev/null 2>&1 && docker volume rm "$v" || true
done
