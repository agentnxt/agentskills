export const DEPLOY_GUIDE = `
# Mode: Deploy — Push to Production

Deploy the SaaS stack to production using Coolify or Docker Compose directly.

## Pre-Flight Checklist

Before deploying, verify ALL of these:

- [ ] All .env values are production-ready (no CHANGE_ME, no localhost, no default passwords)
- [ ] Domain DNS is configured (A record or CNAME for all subdomains)
- [ ] SSL strategy chosen (Caddy auto-TLS or external cert manager)
- [ ] Backup strategy in place (at minimum: daily PostgreSQL dump + volume snapshots)
- [ ] Resource requirements met (see table below)
- [ ] Firewall configured (block DB/Redis ports from external access)
- [ ] SMTP configured (for auth emails, alerts, marketing)

## Resource Requirements

| Profile | Modules | vCPU | RAM | Disk |
|---|---|---|---|---|
| Minimal (essential + core) | 6 containers | 2 | 4 GB | 20 GB |
| Standard (+ ops) | 9 containers | 3 | 6 GB | 30 GB |
| Full (+ all growth) | 17 containers | 4 | 8 GB | 40 GB |
| AI (+ all ai) | 22 containers | 6 | 16 GB | 60 GB |

## Option A: Deploy via Coolify

### Workflow

1. Read .fast-saas.json to get the module list
2. Get Coolify connection details: API URL, token, server UUID, project UUID
3. For each module, use the deploy-to-coolify skill's compose templates
4. Deploy in dependency order: essential → core → ops → growth → ai
5. After deployment, verify health endpoints
6. Configure DNS records for all subdomains

### Coolify API Sequence

\`\`\`bash
# 1. Create project
curl -X POST COOLIFY_URL/api/v1/projects \\
  -H "Authorization: Bearer TOKEN" \\
  -d '{"name": "PROJECT_NAME"}'

# 2. Create environment
curl -X POST COOLIFY_URL/api/v1/projects/PROJECT_ID/environments \\
  -d '{"name": "production"}'

# 3. Deploy each service (example: Logto)
curl -X POST COOLIFY_URL/api/v1/services \\
  -H "Authorization: Bearer TOKEN" \\
  -d '{
    "type": "docker-compose",
    "server_uuid": "SERVER_UUID",
    "project_uuid": "PROJECT_UUID",
    "environment_name": "production",
    "docker_compose": "BASE64_ENCODED_COMPOSE"
  }'
\`\`\`

## Option B: Deploy via Docker Compose (Direct SSH)

### Deployment Steps

1. **Prepare the server**
\`\`\`bash
# Install Docker + Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone the project
git clone https://github.com/ORG/PROJECT.git
cd PROJECT
\`\`\`

2. **Configure environment**
\`\`\`bash
cp .env.example .env
# Edit .env with production values
# Generate secrets:
openssl rand -hex 32  # for JWT_SECRET, LAGO_ENCRYPTION_PRIMARY_KEY, etc.
\`\`\`

3. **Start services in order**
\`\`\`bash
# Start essential first
COMPOSE_PROFILES=essential docker compose up -d
sleep 10

# Then core
COMPOSE_PROFILES=essential,core docker compose up -d
sleep 15

# Then ops
COMPOSE_PROFILES=essential,core,ops docker compose up -d

# Run setup script
./scripts/setup.sh
\`\`\`

4. **Configure reverse proxy**
   - If using Caddy (bundled): Already configured via Caddyfile
   - If using nginx: Create server blocks for each subdomain, issue SSL certs via certbot

5. **Configure firewall**
\`\`\`bash
# Block database ports from external access
sudo iptables -I DOCKER-USER -i eth0 -p tcp --dport 5432 -j DROP
sudo iptables -I DOCKER-USER -i eth0 -p tcp --dport 6379 -j DROP
sudo iptables -I DOCKER-USER -i eth0 -p tcp --dport 3306 -j DROP
sudo netfilter-persistent save
\`\`\`

6. **Verify health**
\`\`\`bash
make health
# or
./scripts/health-check.sh
\`\`\`

## DNS Configuration

For each enabled service, create A records pointing to the server IP:

| Subdomain | Service |
|---|---|
| app.DOMAIN | Your SaaS application |
| auth.DOMAIN | Logto |
| auth-admin.DOMAIN | Logto Admin |
| billing.DOMAIN | Lago UI |
| billing-api.DOMAIN | Lago API |
| storage.DOMAIN | RustFS |
| errors.DOMAIN | GlitchTip |
| status.DOMAIN | Uptime Kuma |
| monitor.DOMAIN | Grafana |
| analytics.DOMAIN | Matomo |
| auto.DOMAIN | n8n |
| admin.DOMAIN | NocoDB |
| email.DOMAIN | Mautic |
| tools.DOMAIN | Appsmith |
| docs.DOMAIN | Docmost |
| product.DOMAIN | PostHog |
| chat.DOMAIN | LibreChat |
| flow.DOMAIN | Langflow |
| observe.DOMAIN | Langfuse |

## Post-Deploy Verification

1. Check all health endpoints (make health)
2. Verify SSL certs are issued for all subdomains
3. Test auth flow: register → login → get JWT
4. Test billing: create Lago customer → assign plan
5. Verify error tracking: trigger test error → check GlitchTip
6. Verify monitoring: check Grafana dashboards + Uptime Kuma
7. Run backup script and verify restore works
`;

export function getDeployGuide(): string {
  return DEPLOY_GUIDE;
}
