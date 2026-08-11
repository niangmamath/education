# 03.4 - Cloturer l'etape 03

## Objectif

Produire des preuves reelles avant commit et push.

## Verification globale

```bash
bash infrastructure/scripts/check_step03.sh
git status --short
git diff --check
git diff --stat
```

## Rapports a creer

- `rapport_YYYY-MM-DD_HHMM_docker_compose.md`
- `rapport_YYYY-MM-DD_HHMM_base_migrations.md`
- `rapport_YYYY-MM-DD_HHMM_ci.md`
- `rapport_YYYY-MM-DD_HHMM_etape_complete.md`

## Commit propose

```bash
git add .
git commit -m "chore(infra): establish local services migrations and CI"
git push origin main
```

Ne pas commit si un controle obligatoire echoue. Ne jamais commiter `.env` ni `_backup_step03_*`.
