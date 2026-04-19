#!/usr/bin/env bash
# build-and-push.sh
# Runs on the VPS — builds the identity-fabric Docker image,
# tags it, and optionally pushes to GHCR.
#
# Usage:
#   bash build-and-push.sh              # build + tag locally only
#   bash build-and-push.sh --push       # build + push to GHCR
#   GHCR_TOKEN=xxx bash build-and-push.sh --push

set -euo pipefail

REPO_DIR="/opt/identity-fabric/src"
CONTEXT="$REPO_DIR/autonomyx-identity-fabric"
IMAGE_LOCAL="identity-fabric:latest"
IMAGE_GHCR="ghcr.io/openautonomyx/identity-fabric"
PUSH=false

for arg in "$@"; do
  [[ "$arg" == "--push" ]] && PUSH=true
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   Identity Fabric — Docker Build                    ║"
echo "╚══════════════════════════════════════════════════════╝"

# 1. Pull latest source
echo ""
echo "▶ [1/4] Pulling latest source from GitHub..."
if [[ -d "$REPO_DIR/.git" ]]; then
  git -C "$REPO_DIR" pull --ff-only
else
  git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/agentnxt/agentskills.git "$REPO_DIR"
  git -C "$REPO_DIR" sparse-checkout set autonomyx-identity-fabric
fi
echo "   ✓ Source up to date"

# 2. Show what we're building
echo ""
echo "▶ [2/4] Build context: $CONTEXT"
echo "   Dockerfile:"
cat "$CONTEXT/Dockerfile"

# 3. Build
echo ""
echo "▶ [3/4] Building Docker image..."
GIT_SHA=$(git -C "$REPO_DIR" rev-parse --short HEAD)
BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)

sudo docker build \
  --tag "$IMAGE_LOCAL" \
  --tag "${IMAGE_GHCR}:latest" \
  --tag "${IMAGE_GHCR}:${GIT_SHA}" \
  --label "org.opencontainers.image.created=${BUILD_DATE}" \
  --label "org.opencontainers.image.revision=${GIT_SHA}" \
  --label "org.opencontainers.image.source=https://github.com/agentnxt/agentskills" \
  --label "org.opencontainers.image.title=autonomyx-identity-fabric" \
  --label "org.opencontainers.image.description=Multimodal identity resolution across social + SSO providers" \
  "$CONTEXT"

echo "   ✓ Image built"
sudo docker images | grep -E "identity-fabric|REPOSITORY"

# 4. Push to GHCR (optional)
echo ""
if [[ "$PUSH" == true ]]; then
  echo "▶ [4/4] Pushing to GHCR..."
  TOKEN="${GHCR_TOKEN:-}"
  if [[ -z "$TOKEN" ]]; then
    echo "   ✗ GHCR_TOKEN not set — run: GHCR_TOKEN=ghp_xxx bash build-and-push.sh --push"
    exit 1
  fi
  echo "$TOKEN" | sudo docker login ghcr.io -u openautonomyx --password-stdin
  sudo docker push "${IMAGE_GHCR}:latest"
  sudo docker push "${IMAGE_GHCR}:${GIT_SHA}"
  echo "   ✓ Pushed ${IMAGE_GHCR}:latest"
  echo "   ✓ Pushed ${IMAGE_GHCR}:${GIT_SHA}"
else
  echo "▶ [4/4] Skipping GHCR push (pass --push to enable)"
fi

# 5. Restart running containers that use this image
echo ""
echo "▶ Restarting containers using identity-fabric image..."
for container in identity_fabric identity_fabric_mcp; do
  if sudo docker ps -q --filter "name=^${container}$" | grep -q .; then
    sudo docker restart "$container"
    echo "   ✓ Restarted $container"
  else
    echo "   – $container not running (skip)"
  fi
done

# 6. Health check
echo ""
echo "▶ Health check..."
sleep 8
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8091/health 2>/dev/null || echo "000")
if [[ "$STATUS" == "200" ]]; then
  echo "   ✓ HTTP API healthy (port 8091)"
  curl -s http://localhost:8091/health | python3 -m json.tool
else
  echo "   ⚠  HTTP API returned $STATUS — check: sudo docker logs identity_fabric"
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅  Build complete                                ║"
echo "║   Local:  $IMAGE_LOCAL"
echo "║   GHCR:   ${IMAGE_GHCR}:${GIT_SHA}"
echo "╚══════════════════════════════════════════════════════╝"
