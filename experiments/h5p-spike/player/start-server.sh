#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Serveur: http://127.0.0.1:4174/"
echo "Arrêt: Ctrl+C"
python3 -m http.server 4174 --bind 127.0.0.1 --directory "$ROOT"
