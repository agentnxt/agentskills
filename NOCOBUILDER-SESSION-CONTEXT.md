# NocoBuilder Session Context

## What's Done

### 1. Rebrand Complete (SimStudio → NocoBuilder)
- Repo: `https://github.com/agentnxxt/nocobuilder` (cloned from simstudioai/sim)
- All `simstudio`, `SimStudio`, `sim-studio`, `simstudioai` refs replaced with `nocobuilder`/`NocoBuilder`
- `sim.ai` → `nocobuilder.cloud`
- `apps/sim` → `apps/nocobuilder`, `helm/sim` → `helm/nocobuilder`
- Docker images: `agentnxxt/nocobuilder`, `agentnxxt/nocobuilder-realtime`, `agentnxxt/nocobuilder-migrations`
- Author/org: `AgentNXXT`
- Env vars: `SIM_AGENT_API_URL` → `NOCO_AGENT_API_URL`
- Code pushed to `main` branch

### 2. MCP Servers Added to Compose Files
- Source copied to `mcp-servers/` directory in nocobuilder repo
- All 3 docker-compose files (local, prod, coolify) updated with MCP services
- Changes are LOCAL only in `/home/user/nocobuilder` — NOT yet pushed to GitHub

## What Needs to Be Done

### Priority 1: Push pending changes
The nocobuilder repo at `/home/user/nocobuilder` has uncommitted changes:
- `docker-compose.local.yml` — modified (MCP servers added + SIM_AGENT fix)
- `docker-compose.prod.yml` — modified (MCP servers added + image refs fixed from ghcr.io → agentnxxt/)
- `docker-compose.coolify.yml` — modified (MCP servers added)
- `docker/app.Dockerfile` — modified
- `docker/realtime.Dockerfile` — modified
- `mcp-servers/` — new directory (ghost-mcp-server, hostinger-mcp, logto-mcp-server)
- `.github/workflows/docker-publish.yml` — new
- `docker-build-push.sh` — new

Run:
```bash
rm -rf mcp-servers/ghost-mcp-server/.git mcp-servers/hostinger-mcp/.git mcp-servers/logto-mcp-server/.git
git add -A
git commit -m "Add MCP servers and fix docker-compose files"
git push origin main
```

### Priority 2: Build & Push Docker Images
No Docker images exist on Docker Hub yet. Need to build and push:
```bash
docker build -f docker/app.Dockerfile -t agentnxxt/nocobuilder:latest .
docker build -f docker/realtime.Dockerfile -t agentnxxt/nocobuilder-realtime:latest .
docker build -f docker/db.Dockerfile -t agentnxxt/nocobuilder-migrations:latest .
docker build -f mcp-servers/ghost-mcp-server/Dockerfile -t agentnxxt/ghost-mcp-server:latest mcp-servers/ghost-mcp-server/
docker build -f mcp-servers/hostinger-mcp/Dockerfile -t agentnxxt/hostinger-mcp:latest mcp-servers/hostinger-mcp/
docker build -f mcp-servers/logto-mcp-server/Dockerfile -t agentnxxt/logto-mcp-server:latest mcp-servers/logto-mcp-server/

docker push agentnxxt/nocobuilder:latest
docker push agentnxxt/nocobuilder-realtime:latest
docker push agentnxxt/nocobuilder-migrations:latest
docker push agentnxxt/ghost-mcp-server:latest
docker push agentnxxt/hostinger-mcp:latest
docker push agentnxxt/logto-mcp-server:latest
```

### Priority 3: Deploy with Docker Compose
```bash
cp apps/nocobuilder/.env.example .env
# Edit .env — fill in required secrets:
#   NEXT_PUBLIC_APP_URL, BETTER_AUTH_SECRET, ENCRYPTION_KEY,
#   INTERNAL_API_SECRET, POSTGRES_PASSWORD, NEXT_PUBLIC_SOCKET_URL
#   GHOST_URL, GHOST_ADMIN_API_KEY, GHOST_CONTENT_API_KEY
#   HOSTINGER_API_KEY
#   LOGTO_ENDPOINT, LOGTO_APP_ID, LOGTO_APP_SECRET, LOGTO_ACCOUNTS_TOKEN

# For local dev (builds from source):
docker compose -f docker-compose.local.yml up -d --build

# For production (uses pre-built images from Docker Hub):
docker compose -f docker-compose.prod.yml up -d

# For Coolify (builds from source on deploy):
# Just point Coolify to docker-compose.coolify.yml
```

## Architecture

### Services (docker-compose)
| Service | Port | Image (prod) | Description |
|---------|------|--------------|-------------|
| nocobuilder | 3000 | agentnxxt/nocobuilder | Main Next.js app |
| realtime | 3002 | agentnxxt/nocobuilder-realtime | WebSocket server |
| migrations | - | agentnxxt/nocobuilder-migrations | DB migrations (run once) |
| db | 5432 | pgvector/pgvector:pg17 | PostgreSQL with pgvector |
| ghost-mcp | - | agentnxxt/ghost-mcp-server | Ghost CMS MCP (56 tools) |
| hostinger-mcp | 8000 | agentnxxt/hostinger-mcp | Hostinger API MCP |
| logto-mcp | - | agentnxxt/logto-mcp-server | Logto auth MCP |

### MCP Server Env Vars
| Server | Required Env Vars |
|--------|-------------------|
| ghost-mcp | GHOST_URL, GHOST_ADMIN_API_KEY, GHOST_CONTENT_API_KEY |
| hostinger-mcp | HOSTINGER_API_KEY |
| logto-mcp | LOGTO_ENDPOINT, LOGTO_APP_ID, LOGTO_APP_SECRET, LOGTO_ACCOUNTS_TOKEN |

### Repos
- **nocobuilder**: `https://github.com/agentnxxt/nocobuilder` — main app
- **agentskills**: `https://github.com/agentnxxt/agentskills` — tools, skills, MCP servers, rebrand script

### Git Config
```
user.name: fractional-pm
user.email: chinmay@openautonomyx.com
```
