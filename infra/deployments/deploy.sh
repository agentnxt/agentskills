#!/usr/bin/env bash
# OpenAtonomyx — One-command deploy for agnxxt.com
# Prerequisites: Docker, Docker Compose v2, DNS A records for *.agnxxt.com
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Preflight checks ─────────────────────────────────────────────
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose v2 not found"; exit 1; }

if [ ! -f .env ]; then
  echo "⚠  No .env found — copying from .env.example"
  cp .env.example .env
  echo "   Edit .env and fill in the REQUIRED values, then re-run."
  exit 1
fi

echo "═══════════════════════════════════════════════════"
echo "  OpenAtonomyx — Deploying to agnxxt.com"
echo "═══════════════════════════════════════════════════"
echo ""

# ── Step 1: Create the shared network ────────────────────────────
docker network inspect openatonomyx >/dev/null 2>&1 || \
  docker network create openatonomyx
echo "✅ Network: openatonomyx"

# ── Step 2: Pull latest images ───────────────────────────────────
echo ""
echo "→ Pulling images..."
docker compose pull
echo "✅ Images up to date"

# ── Step 3: Start the stack ──────────────────────────────────────
echo ""
echo "→ Starting services..."
docker compose up -d
echo ""

# ── Step 4: Wait for Logto health ────────────────────────────────
echo "→ Waiting for Logto to become healthy..."
timeout 120 bash -c 'until docker inspect --format="{{.State.Health.Status}}" openatonomyx-logto 2>/dev/null | grep -q healthy; do sleep 5; echo "  waiting..."; done' || {
  echo "⚠  Logto did not become healthy in 120s — check logs:"
  echo "   docker compose logs logto"
}
echo "✅ Logto is healthy"

# ── Step 5: Show status ─────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Deployment complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Services:"
echo "    🔐 Logto Admin   → https://authadmin.openautonomyx.com"
echo "    🔑 Logto Auth    → https://logto.agnxxt.com"
echo "    🌐 Liferay       → https://liferay.agnxxt.com"
echo "    💰 Lago Billing  → https://lago.agnxxt.com"
echo "    📊 ERPNext       → https://erp.agnxxt.com"
echo "    🏢 Odoo          → https://odoo.agnxxt.com"
echo "    ⚡ n8n           → https://n8n.agnxxt.com"
echo "    📱 WuzAPI        → https://wuzapi.agnxxt.com"
echo "    💬 Matrix/Conduit→ https://matrix.agnxxt.com"
echo "    🤖 Sim Studio   → https://sim.agnxxt.com"
echo ""
echo "  Next steps:"
echo "    1. Open https://authadmin.openautonomyx.com"
echo "    2. Create an M2M app with Management API access"
echo "    3. Run: LOGTO_M2M_APP_ID=<id> LOGTO_M2M_APP_SECRET=<secret> ./logto/setup-apps.sh"
echo "    4. Copy each Client ID + Secret into .env"
echo "    5. Restart: docker compose up -d"
echo ""
