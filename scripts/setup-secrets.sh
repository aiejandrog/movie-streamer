#!/usr/bin/env bash
# Sets GitHub Actions secrets for movie-streamer
#
# Prerequisites:
#   1. gh CLI installed — https://cli.github.com
#   2. gh auth login already run
#   3. Railway project already created — https://railway.app
#
# Usage:
#   bash scripts/setup-secrets.sh
#
# Where to find each value:
#   RAILWAY_DEPLOY_HOOK  → Railway dashboard → your service → Settings → Deploy Triggers → Deploy Hook URL
#   TMDB_API_KEY         → https://www.themoviedb.org/settings/api
#   API_KEY              → generate below, or leave blank to auto-generate

set -euo pipefail

REPO="${GH_REPO:-aiejandrog/movie-streamer}"

echo "================================================"
echo "  MovieVault — GitHub Actions Secret Setup"
echo "  Repo: $REPO"
echo "================================================"
echo ""

# ── Collect secrets ──────────────────────────────────────────────────────

read -rsp "RAILWAY_DEPLOY_HOOK (Railway dashboard → Service → Settings → Deploy Triggers): " RAILWAY_DEPLOY_HOOK; echo
if [[ -z "$RAILWAY_DEPLOY_HOOK" ]]; then
  echo "ERROR: RAILWAY_DEPLOY_HOOK is required."
  exit 1
fi

read -rsp "TMDB_API_KEY: " TMDB_API_KEY; echo
if [[ -z "$TMDB_API_KEY" ]]; then
  echo "ERROR: TMDB_API_KEY is required."
  exit 1
fi

read -rsp "API_KEY (leave blank to auto-generate a 32-byte hex key): " API_KEY; echo
if [[ -z "${API_KEY}" ]]; then
  API_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  echo "  Auto-generated API_KEY: $API_KEY"
  echo "  (copy this — you'll need it for Railway dashboard and VITE_API_KEY)"
fi

# ── Set GitHub secrets ────────────────────────────────────────────────────

echo ""
echo "Setting GitHub Actions secrets..."
gh secret set RAILWAY_DEPLOY_HOOK --body "$RAILWAY_DEPLOY_HOOK" --repo "$REPO"
gh secret set TMDB_API_KEY        --body "$TMDB_API_KEY"        --repo "$REPO"
gh secret set API_KEY             --body "$API_KEY"             --repo "$REPO"

echo ""
echo "✓ GitHub secrets set (3 total)"
echo ""

# ── Print Railway dashboard checklist ─────────────────────────────────────────────

echo "================================================"
echo "  Now set these in Railway dashboard:"
echo "  (Your service → Variables)"
echo "================================================"
echo ""
echo "  DATABASE_URL     → added automatically by Railway Postgres add-on"
echo "  TMDB_API_KEY     → $TMDB_API_KEY"
echo "  API_KEY          → $API_KEY"
echo "  VITE_API_KEY     → $API_KEY  (same value — used by React frontend)"
echo "  ALLOWED_ORIGINS  → https://your-app.up.railway.app"
echo "  VIDEOS_DIR       → /app/videos"
echo "  SECRET_KEY       → $(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo ""
echo "  Also set in GitHub repo → Settings → Variables → Actions:"
echo "  RAILWAY_APP_URL  → https://your-app.up.railway.app"
echo "  (used to show the live URL in the deploy job summary)"
echo ""
echo "================================================"
echo "  Deploy sequence:"
echo "  1. git push origin main"
echo "  2. GH Actions: pytest → npm build → docker validate → deploy hook"
echo "  3. Railway builds Dockerfile and deploys"
echo "  4. Live in ~5 minutes"
echo "================================================"
