#!/bin/bash
set -e

echo "=== MovieVault startup ==="

# Tables are created automatically by SQLAlchemy in the app lifespan
# (Base.metadata.create_all) — no Alembic needed.

# Railway injects $PORT; fall back to 8000 for local Docker runs.
PORT="${PORT:-8000}"
echo "Starting on 0.0.0.0:${PORT} ..."

exec gunicorn \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  app.main:app \
  --bind "0.0.0.0:${PORT}" \
  --timeout 120 \
  --access-logfile -
