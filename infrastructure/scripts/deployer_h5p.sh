#!/usr/bin/env bash

set -Eeuo pipefail

# Dépose un paquet H5P vetté dans le catalogue en une seule commande : copie
# le fichier depuis n'importe où lisible depuis WSL (le dossier Téléchargements
# Windows, /mnt/c/Users/<compte>/Downloads, par exemple) vers l'arbre versionné
# `experiments/h5p-spike/packages/`, puis enchaîne creer/register/deploy/check
# dans le conteneur API. Remplace la manipulation manuelle en trois commandes
# séparées, qui obligeait à réinventer titre, licence et provenance à chaque
# dépôt faute d'un endroit où les fixer une fois pour toutes.
#
# Marche dans les deux checkouts du dépôt, qui n'utilisent pas le même nom de
# fichier Compose : `docker-compose.yml` pour le déploiement,
# `docker-compose.dev.yml` pour ce worktree de développement, isolé exprès
# (réseau, volumes, ports propres). Le script cherche le second en premier —
# absent du checkout de déploiement par construction — et retombe sur le
# premier sinon, plutôt que de supposer lequel des deux tourne ici.
#
# Usage :
#   infrastructure/scripts/deployer_h5p.sh <fichier.h5p> <code-activite> \
#     <code-competence> "<titre>" [minutes]
#
# Exemple, depuis la racine du dépôt :
#   infrastructure/scripts/deployer_h5p.sh \
#     "/mnt/c/Users/tidia/Downloads/h4.h5p" \
#     son-ce1-fr-dictee ce1-fr-dictee "Écrire une phrase entendue" 5

if [ "$#" -lt 4 ]; then
  echo "Usage : $0 <fichier.h5p> <code-activite> <code-competence> <titre> [minutes]" >&2
  exit 1
fi

FICHIER="$1"
CODE="$2"
COMPETENCE="$3"
TITRE="$4"
MINUTES="${5:-5}"

# Provenance fixe et non négociable au cas par cas : tout ce qui passe par ce
# script est fabriqué en interne par le propriétaire avec Lumi, jamais
# téléchargé d'un tiers. ADR-012 (condition 8) exige une licence et une source
# attestées avant publication ; les inventer à chaque dépôt était la source de
# confusion corrigée le 24 août 2026. CC BY 4.0 est le choix confirmé par le
# propriétaire, déjà documenté dans docs/contenus/a-telecharger.md.
LICENCE="CC BY 4.0"
SOURCE="https://lumi.education, fabriqué par nos soins"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEPOT_DIR="$REPO_ROOT/experiments/h5p-spike/packages"
DESTINATION="$DEPOT_DIR/$CODE.h5p"

if [ -f "$REPO_ROOT/docker-compose.dev.yml" ]; then
  COMPOSE_FILE="$REPO_ROOT/docker-compose.dev.yml"
elif [ -f "$REPO_ROOT/docker-compose.yml" ]; then
  COMPOSE_FILE="$REPO_ROOT/docker-compose.yml"
else
  echo "Ni docker-compose.dev.yml ni docker-compose.yml trouvé dans $REPO_ROOT" >&2
  exit 1
fi
COMPOSE=(docker compose -f "$COMPOSE_FILE")

if [ ! -f "$FICHIER" ]; then
  echo "Fichier introuvable : $FICHIER" >&2
  exit 1
fi

cp "$FICHIER" "$DESTINATION"
echo "Copié vers $DESTINATION"

"${COMPOSE[@]}" exec -T api python -m app.catalog creer "$CODE" \
  --titre "$TITRE" --competence "$COMPETENCE" --minutes "$MINUTES"

"${COMPOSE[@]}" exec -T api python -m app.catalog register "$CODE" \
  "/opt/h5p-spike/packages/$CODE.h5p" --licence "$LICENCE" --source "$SOURCE"

"${COMPOSE[@]}" exec -T api python -m app.catalog deploy "$CODE"

"${COMPOSE[@]}" exec -T api python -m app.catalog check
