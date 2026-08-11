#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(pwd)"
ARCHIVE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH="$ARCHIVE_ROOT/patch"
[[ -d "$ROOT/.git" ]] || { echo "Erreur: executer depuis la racine du depot." >&2; exit 1; }
[[ -d "$PATCH" ]] || { echo "Erreur: patch introuvable: $PATCH" >&2; exit 1; }
cp -a "$PATCH"/. "$ROOT"/

if [[ -f "$ROOT/.gitignore.step03" ]]; then
  touch "$ROOT/.gitignore"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    grep -Fqx "$line" "$ROOT/.gitignore" || printf '%s\n' "$line" >> "$ROOT/.gitignore"
  done < "$ROOT/.gitignore.step03"
  rm -f "$ROOT/.gitignore.step03"
fi
chmod +x "$ROOT/infrastructure/scripts/"*.sh 2>/dev/null || true
echo "Correctif de l'etape 03 applique."
echo "Executer: cp .env.example .env"
