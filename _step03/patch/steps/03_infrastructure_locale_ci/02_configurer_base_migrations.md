# 03.2 - SQLAlchemy async et Alembic

## Objectif

Valider la connexion asynchrone PostgreSQL et une baseline Alembic propre.

## Procedure

```bash
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic current
docker compose exec -T api python -m pytest tests/test_db_session.py -q
```

Dans une base locale jetable, verifier aussi:

```bash
docker compose exec -T api alembic downgrade base
docker compose exec -T api alembic upgrade head
```

## Acceptation

- `DATABASE_URL` utilise `postgresql+asyncpg` et `postgres:5432`.
- La baseline s'applique sur base vide.
- Downgrade et upgrade sont reproductibles.
- Aucune migration metier n'est inventee pendant cette etape.
- Aucun mot de passe n'est code dans `alembic.ini`.
