# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci --prefer-offline
COPY frontend/ ./frontend/
# vite.config.js: outDir = '../backend/static' → resolves to /app/backend/static
RUN mkdir -p backend/static && cd frontend && npm run build

# ── Stage 2: Python backend ────────────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app/backend

# Deps layer (cached unless requirements.txt changes)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source
COPY backend/ .

# Copy compiled frontend from stage 1
COPY --from=frontend-build /app/backend/static ./static

# Make start script executable
RUN chmod +x start.sh

# Railway injects $PORT; start.sh runs alembic migrations then gunicorn
EXPOSE 8000
CMD ["./start.sh"]
