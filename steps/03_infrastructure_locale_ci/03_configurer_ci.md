# 03.3 - Integration continue

## Objectif

Valider frontend, backend, migrations et secrets dans GitHub Actions.

## Controles locaux avant push

```bash
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
pnpm --filter @studentconnect/web run build
docker compose exec -T api ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
```

## Point bloquant connu a corriger

Le rapport 02 indique que le lint Next.js et un test CORS n'etaient pas verts. Ne marquer la CI terminee qu'apres correction ou apres un rapport Bloque explicite. Un critere ne peut pas etre coche si la commande echoue.

## Acceptation

- `api-ci.yml`, `web-ci.yml` et `secret-scan.yml` sont valides.
- Les workflows utilisent les versions verrouillees du projet.
- Aucun deploiement n'est active.
- Les permissions GitHub sont minimales.
- Tous les checks obligatoires sont verts.
