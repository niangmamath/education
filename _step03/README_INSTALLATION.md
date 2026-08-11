# StudentConnect - reprise propre de l'etape 03 sous WSL Ubuntu 24.04

Cette archive est concue pour etre utilisee dans le terminal Ubuntu de WSL, avec Bash. N'utilisez pas PowerShell pour cette procedure.

## Avant de commencer

Depuis WSL, placez-vous a la racine du depot, par exemple:

```bash
cd ~/projects/StudentConnect
pwd
git status
docker version
docker compose version
```

Le moteur Docker Desktop peut etre utilise, mais toutes les commandes du projet sont executees depuis WSL.

## Installation

```bash
unzip studentconnect_step03_wsl.zip -d _step03
bash _step03/tools/01_prepare_step03.sh
bash _step03/tools/02_apply_patch.sh
cp .env.example .env
```

Comme l'ancien volume PostgreSQL a ete initialise avec un mauvais role, executez ensuite:

```bash
bash _step03/tools/03_reset_volumes.sh
```

Le script exige la saisie exacte `RESET-LOCAL`.

## Controle

```bash
bash infrastructure/scripts/check_step03.sh
```

## Important

- Ne commitez pas `.env`.
- Ne commitez pas `_step03/` ni `_backup_step03_*`.
- PostgreSQL n'est pas publie sur l'hote. L'API Docker utilise `postgres:5432`.
- Les rapports sont crees uniquement apres observation des resultats reels.
