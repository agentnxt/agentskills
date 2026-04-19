#!/usr/bin/env bash
# deploy/deploy.sh
# One-command deployment of autonomyx-identity-fabric to vps.opensaasapps.com
#
# Usage:
#   ./deploy.sh                          # deploy latest from GHCR
#   ./deploy.sh --build                  # build image locally on VPS, then deploy
#   ./deploy.sh --seed-schema            # also run schema_seed.sh after deploy
#
# Prerequisites on VPS:
#   - Docker + Docker Compose v2 installed
#   - nginx installed, shared-infra_default network exists
#   - /opt/identity-fabric/.env filled in (copy from .env.example)
#   - sudo access for ubuntu user

set -euo pipefail

VPS_HOST="${VPS_HOST:-vps.opensaasapps.com}"
VPS_USER="${VPS_USER:-ubuntu}"
REMOTE_DIR="/opt/identity-fabric"
IMAGE="ghcr.io/openautonomyx/identity-fabric:latest"
NGINX_CONF="/etc/nginx/sites-available/identity-fabric"
NGINX_ENABLED="/etc/nginx/sites-enabled/identity-fabric"
DOMAIN="identity.opensaasapps.com"

BUILD_LOCAL=false
SEED_SCHEMA=false
for arg in "$@"; do
  [[ "$arg" == "--build"       ]] && BUILD_LOCAL=true
  [[ "$arg" == "--seed-schema" ]] && SEED_SCHEMA=true
done

echo "▶ Deploying identity-fabric → $VPS_USER@$VPS_HOST:$REMOTE_DIR"

# ── 1. Copy deploy files to VPS ───────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ssh "$VPS_USER@$VPS_HOST" "sudo mkdir -p $REMOTE_DIR && sudo chown $VPS_USER:$VPS_USER $REMOTE_DIR"

scp "$SCRIPT_DIR/docker-compose.yml"          "$VPS_USER@$VPS_HOST:$REMOTE_DIR/docker-compose.yml"
scp "$SCRIPT_DIR/nginx-identity-fabric.conf"  "$VPS_USER@$VPS_HOST:/tmp/nginx-identity-fabric.conf"
scp "$SCRIPT_DIR/.env.example"                "$VPS_USER@$VPS_HOST:$REMOTE_DIR/.env.example"

# Copy schema seed script
scp "$SCRIPT_DIR/../scripts/schema_seed.sh"   "$VPS_USER@$VPS_HOST:$REMOTE_DIR/schema_seed.sh"
ssh "$VPS_USER@$VPS_HOST" "chmod +x $REMOTE_DIR/schema_seed.sh"

# Copy Dockerfile + scripts if building locally
if [[ "$BUILD_LOCAL" == true ]]; then
  echo "▶ Copying source for local build..."
  rsync -az --exclude "__pycache__" --exclude "*.pyc" --exclude ".pytest_cache" \
    "$SCRIPT_DIR/../" "$VPS_USER@$VPS_HOST:$REMOTE_DIR/src/"
fi

# ── 2. Ensure .env exists ─────────────────────────────────────────────────────
ssh "$VPS_USER@$VPS_HOST" bash << 'REMOTE'
if [[ ! -f /opt/identity-fabric/.env ]]; then
  cp /opt/identity-fabric/.env.example /opt/identity-fabric/.env
  echo "⚠️  .env created from template — EDIT /opt/identity-fabric/.env before continuing"
  echo "    Required: SURREAL_PASS, IDENTITY_FABRIC_ENC_KEY, IDENTITY_FABRIC_HMAC_KEY, AUTONOMYX_AGENT_SECRET"
  exit 1
fi
echo "✓ .env exists"
REMOTE

# ── 3. Build image (optional) or pull from GHCR ───────────────────────────────
if [[ "$BUILD_LOCAL" == true ]]; then
  echo "▶ Building Docker image on VPS..."
  ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
cd $REMOTE_DIR/src
sudo docker build -t $IMAGE .
echo "✓ Image built"
REMOTE
else
  echo "▶ Pulling image from GHCR..."
  ssh "$VPS_USER@$VPS_HOST" "sudo docker pull $IMAGE"
fi

# ── 4. Deploy container ───────────────────────────────────────────────────────
ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
cd $REMOTE_DIR
sudo docker compose pull 2>/dev/null || true
sudo docker compose up -d --remove-orphans
echo "✓ Container started"
sudo docker compose ps
REMOTE

# ── 5. nginx config ───────────────────────────────────────────────────────────
ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
sudo cp /tmp/nginx-identity-fabric.conf $NGINX_CONF
sudo ln -sf $NGINX_CONF $NGINX_ENABLED 2>/dev/null || true
sudo nginx -t && sudo nginx -s reload
echo "✓ nginx reloaded"
REMOTE

# ── 6. TLS (Let's Encrypt) ────────────────────────────────────────────────────
ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
if ! sudo test -d /etc/letsencrypt/live/$DOMAIN; then
  echo "▶ Issuing TLS certificate for $DOMAIN..."
  sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos \
    -m admin@openautonomyx.com || echo "⚠️  Certbot failed — run manually if DNS not yet pointed"
else
  echo "✓ TLS certificate already exists for $DOMAIN"
fi
REMOTE

# ── 7. Schema seed (optional) ────────────────────────────────────────────────
if [[ "$SEED_SCHEMA" == true ]]; then
  echo "▶ Seeding SurrealDB schema..."
  ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
source $REMOTE_DIR/.env
cd $REMOTE_DIR
SURREAL_URL=\$SURREAL_URL SURREAL_USER=\$SURREAL_USER SURREAL_PASS=\$SURREAL_PASS \
  bash schema_seed.sh
REMOTE
fi

# ── 8. Health check ───────────────────────────────────────────────────────────
echo "▶ Waiting for service to come up..."
sleep 5
ssh "$VPS_USER@$VPS_HOST" bash << REMOTE
for i in \$(seq 1 12); do
  STATUS=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8091/health)
  if [[ "\$STATUS" == "200" ]]; then
    echo "✓ Health check passed (HTTP \$STATUS)"
    curl -s http://localhost:8091/health | python3 -m json.tool
    exit 0
  fi
  echo "  attempt \$i — got HTTP \$STATUS, retrying..."
  sleep 5
done
echo "✗ Service did not come up after 60s — check logs:"
sudo docker compose -f $REMOTE_DIR/docker-compose.yml logs --tail=50
exit 1
REMOTE

echo ""
echo "✅ Deployment complete"
echo "   Service: https://$DOMAIN"
echo "   API docs: https://$DOMAIN/docs"
echo "   Health:   https://$DOMAIN/health"
