#!/usr/bin/env bash
# WuzAPI — Deploy to www.openautonomyx.com
# Prerequisites: Docker, Docker Compose v2, DNS A records for openautonomyx.com + www
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose v2 not found"; exit 1; }

if [ ! -f .env ]; then
  echo "⚠  No .env found — copying from .env.example"
  cp .env.example .env
  echo "   Edit .env and fill in the REQUIRED values, then re-run."
  exit 1
fi

echo "═══════════════════════════════════════════════════"
echo "  WuzAPI — Deploying to www.openautonomyx.com"
echo "═══════════════════════════════════════════════════"
echo ""

echo "→ Pulling images..."
docker compose pull
echo "✅ Images up to date"
echo ""

echo "→ Starting services..."
docker compose up -d
echo ""

echo "═══════════════════════════════════════════════════"
echo "  Deployment complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  📱 WuzAPI → https://www.openautonomyx.com"
echo ""
echo "  API auth header:"
echo "    Authorization: Bearer <WUZAPI_ADMIN_TOKEN>"
echo ""
echo "  Quick test:"
echo "    curl https://www.openautonomyx.com/api/sessions -H 'token: <WUZAPI_ADMIN_TOKEN>'"
echo ""
