#!/usr/bin/env bash
# Liferay — Deploy to www.openautonomyx.com
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
echo "  Liferay — Deploying to www.openautonomyx.com"
echo "═══════════════════════════════════════════════════"
echo ""

echo "→ Pulling images..."
docker compose pull
echo "✅ Images up to date"
echo ""

echo "→ Starting services..."
docker compose up -d
echo ""

echo "→ Waiting for Liferay to become healthy (may take 2-3 min)..."
timeout 180 bash -c 'until docker inspect --format="{{.State.Health.Status}}" oax-liferay 2>/dev/null | grep -q healthy; do sleep 10; echo "  waiting..."; done' || {
  echo "⚠  Liferay not healthy in 180s — check: docker compose logs liferay"
}
echo "✅ Liferay is healthy"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Deployment complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  🌐 Liferay Portal → https://www.openautonomyx.com"
echo ""
