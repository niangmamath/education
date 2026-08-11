# ADR 011 — Choix SQLAlchemy : Async Engine

Date: 2026-08-11

Contexte
-------

L'API FastAPI nécessite un accès à PostgreSQL. SQLAlchemy 2 supporte des engines sync et async.

Décision
--------

Nous choisissons d'utiliser l'API `AsyncEngine` de SQLAlchemy (dialecte `asyncpg`) pour les accès
base de données afin de garder les endpoints FastAPI non bloquants et permettre une meilleure
concurrence IO-bound.

Conséquences
------------

- Les handlers FastAPI pourront utiliser des sessions asynchrones (`AsyncSession`).
- Alembic sera configuré avec une `env.py` compatible async.
- Les opérations CPU-intensives devront être déléguées à des workers (Celery) pour ne pas
  bloquer la boucle async.

Alternatives considérées
------------------------

- Utiliser une approche sync (engine sync) avec `run_in_executor`. Avantage : simplicité.
  Inconvénient : moins performant pour I/O intensif et pas natif pour FastAPI async.

Décision prise par
------------------

GitHub Copilot (agent) — 2026-08-11
