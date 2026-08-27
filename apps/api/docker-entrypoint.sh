#!/bin/sh
# One executable, no shell chaining for a platform's `dockerCommand` to
# reinterpret. render.yaml passed `sh -c "step1 && step2 && step3"` as a
# single string on its first try, and whatever Render does to that string
# before running it did not preserve the `&&` as shell syntax — the whole
# line came back as one unresolved command name. A single token with no
# spaces cannot be mis-split that way, on Render or anywhere else.
set -e

python -m app.core.storage_init
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
