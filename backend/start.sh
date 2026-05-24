#!/bin/bash
set -e

echo "=== MovieVault startup ==="

# Run Alembic migrations before the server starts.
# On first deploy this creates all tables; on subsequent deploys it's a no-op.
echo "Running database migrations..."
alembic upgrade head
echo "Migrations done."

# Railway injects $PORT; fall back to 8000 for local Docker runs.
PORT="${PORT:-8000}"
echo "Starting gunicorn on 0.0.0.0:${PORT} ..."

exec gunicorn \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  app.main:app \
  --bind "0.0.0.0:${PORT}" \
  --timeout 120 \
  --access-logfile -
