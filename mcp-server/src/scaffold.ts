export const SCAFFOLD_GUIDE = `
# Mode: Scaffold — Generate a Complete SaaS Project

Generate a full SaaS project from scratch using the Autonomyx Fast SaaS Toolkit.

## Step 1: Gather Requirements

Ask the user:
1. **Project name** — lowercase, hyphens only (e.g., my-saas-app)
2. **Domain** — e.g., myapp.com
3. **Admin email** — for SSL certs and system notifications
4. **Which modules?** Present this menu:

\`\`\`
Essential (always included):
  ✓ PostgreSQL 16, Redis 7, Caddy

Core (default on):
  [ ] Logto — Auth, SSO, RBAC, multi-tenant organizations
  [ ] Lago — Usage-based billing and subscriptions
  [ ] RustFS — S3-compatible object storage

Ops (default on):
  [ ] GlitchTip — Error tracking (Sentry-compatible)
  [ ] Uptime Kuma — Uptime monitoring and status pages
  [ ] Grafana Stack — Metrics, dashboards, log aggregation

Growth (opt-in):
  [ ] Matomo — Web analytics (GDPR-compliant)
  [ ] PostHog — Product analytics, feature flags
  [ ] Mautic — Email marketing automation
  [ ] Stalwart — Full SMTP/IMAP mail server
  [ ] NocoDB — Admin dashboard
  [ ] n8n — Workflow automation
  [ ] Appsmith — Low-code internal tools
  [ ] Docmost — Knowledge base

AI (opt-in):
  [ ] LibreChat — Multi-model chat UI
  [ ] Langflow — Visual flow builder for AI pipelines
  [ ] Ollama — Local LLM inference
  [ ] Claude Agent — Anthropic agent runner
  [ ] Langfuse — LLM observability
\`\`\`

## Step 2: Generate Project Files

### Option A: CLI (if available)
\`\`\`bash
npx @autonomyx/fast-saas init PROJECT_NAME
\`\`\`

### Option B: Direct file generation
Generate these files in the project directory:

1. **docker-compose.yml** — All selected services with:
   - Health checks for every service
   - Named volumes for persistent data
   - Internal Docker network (saas-net)
   - COMPOSE_PROFILES for layer control
   - Correct dependency ordering (depends_on with condition: service_healthy)

2. **.env** — All configuration variables:
   - DOMAIN, ADMIN_EMAIL
   - POSTGRES_PASSWORD, REDIS_PASSWORD (auto-generated)
   - LOGTO_*, LAGO_*, RUSTFS_* credentials (auto-generated)
   - COMPOSE_PROFILES (based on module selection)
   - Per-service config vars

3. **Caddyfile** — Reverse proxy config:
   - Auto-TLS via Let's Encrypt
   - One entry per service subdomain
   - Security headers (HSTS, X-Frame-Options, etc.)
   - WebSocket support where needed (n8n, Uptime Kuma)

4. **Makefile** — Common operations:
   - make up / make down / make restart
   - make logs SERVICE=name
   - make backup / make restore
   - make health — check all service health endpoints
   - make setup — first-time initialization

5. **scripts/** — Automation scripts:
   - setup.sh — Initialize databases, run migrations, create admin users
   - health-check.sh — Hit all health endpoints, report status
   - backup.sh — Dump PostgreSQL + copy volumes
   - restore.sh — Restore from backup

6. **migrations/** — Database setup:
   - 001_create_tenants.sql
   - 002_create_users.sql
   - 003_create_tenant_memberships.sql
   - 004_create_api_keys.sql
   - 005_create_usage_events.sql

7. **.fast-saas.json** — Project manifest:
   \`\`\`json
   {
     "name": "PROJECT_NAME",
     "domain": "DOMAIN",
     "version": "1.0.0",
     "modules": ["postgres", "redis", "caddy", "logto", "lago", ...],
     "profiles": ["essential", "core", "ops"]
   }
   \`\`\`

## Step 3: Post-Scaffold Guidance

After generating the project, present:
1. **Service URL map** — e.g., auth.DOMAIN → Logto, billing.DOMAIN → Lago
2. **First 5 minutes checklist** — ordered steps to get running:
   - docker compose up -d
   - Wait for health checks
   - Run make setup
   - Open auth-admin.DOMAIN → configure Logto
   - Open billing.DOMAIN → configure Lago plans
3. **Offer to enter Configure mode** to set up services programmatically
`;

export function getScaffoldGuide(): string {
  return SCAFFOLD_GUIDE;
}
