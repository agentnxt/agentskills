export const DIAGNOSE_GUIDE = `
# Mode: Diagnose — Health Check & Troubleshooting

## Quick Health Check

\`\`\`bash
cd PROJECT_DIR

# Option 1: Makefile
make health

# Option 2: Script
./scripts/health-check.sh

# Option 3: Manual
docker compose ps
docker stats --no-stream
\`\`\`

## Systematic Troubleshooting

For any failing service, check in this order:

### 1. Is the container running?
\`\`\`bash
docker compose ps SERVICE_NAME
# Look for: State = running, Health = healthy
\`\`\`

### 2. Check container logs
\`\`\`bash
docker compose logs --tail=50 SERVICE_NAME
# Look for: error, fatal, panic, exception, failed, denied
\`\`\`

### 3. Check health endpoint
Use the health URL from the module registry (get_module_registry tool).

### 4. Check dependencies
If a service depends on PostgreSQL or Redis, verify those are healthy first:
\`\`\`bash
docker compose exec postgres pg_isready
docker compose exec redis redis-cli ping
\`\`\`

### 5. Check resources
\`\`\`bash
docker stats --no-stream
free -h
df -h
\`\`\`

## Common Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| Logto 502 | Database not initialized | Run ./scripts/setup.sh |
| Lago unhealthy | Missing encryption keys | Check LAGO_ENCRYPTION_PRIMARY_KEY in .env |
| Lago clock crash | Ruby bundler error | docker compose restart lago_clock |
| GlitchTip 500 | Redis connection refused | Verify REDIS_PASSWORD matches, check firewall |
| Caddy cert error | DNS not configured | Add A records for all subdomains |
| n8n can't connect | PostgreSQL DB missing | Run: docker compose exec postgres createdb n8n |
| Matomo install loop | MariaDB not ready | Wait 30s, refresh; check MariaDB logs |
| Mautic 500 | PostgreSQL credentials wrong | Check POSTGRES_PASSWORD in .env matches |
| High memory usage | Too many growth/ai modules | Reduce COMPOSE_PROFILES, disable unused modules |
| ERPNext workers crash | Redis auth mismatch | Remove rq_password from common_site_config.json |
| Container OOM killed | Insufficient RAM | Add swap: fallocate -l 4G /swapfile && mkswap && swapon |
| Port conflict | Another service on same port | Check: ss -ltn | grep :PORT; change port in .env |
| Volume permission denied | Root/non-root mismatch | chown inside container: docker compose exec -u root SERVICE chown -R user:user /data |
| SSL cert not renewing | Certbot timer stopped | sudo systemctl enable --now certbot.timer |
| Zombie processes piling up | Containers not reaping children | Add init: true to docker-compose.yml for affected services |

## MCP-Assisted Diagnosis

If MCP servers are available, use them for deeper diagnosis:

### Uptime Kuma — opensaasapps-uptime-kuma MCP
- Check all monitors for current status
- Get downtime history for specific services
- Verify alert notifications are firing

### GlitchTip — opensaasapps-glitchtip MCP
- List recent errors grouped by type
- Find error patterns (same error across multiple tenants = platform bug)
- Check if error volume is trending up

### n8n — opensaasapps-n8n MCP
- Check workflow execution history
- Find failed runs and their error messages
- Verify credentials are still valid

### Lago — opensaasapps-lago MCP
- Check webhook delivery status
- Verify subscription states match expected
- Look for failed payment events

## Emergency Procedures

### Service is down and won't restart
\`\`\`bash
# 1. Check why it stopped
docker compose logs --tail=100 SERVICE

# 2. Try restart
docker compose restart SERVICE

# 3. If OOM, check memory
docker stats --no-stream
free -h

# 4. Nuclear option: rebuild
docker compose down SERVICE
docker compose up -d --build SERVICE
\`\`\`

### Database is corrupted
\`\`\`bash
# 1. Stop all services except postgres
docker compose stop $(docker compose ps --services | grep -v postgres)

# 2. Try repair
docker compose exec postgres pg_isready
docker compose exec postgres psql -U postgres -c "SELECT 1;"

# 3. Restore from backup
./scripts/restore.sh BACKUP_FILE
\`\`\`

### All services down after server reboot
\`\`\`bash
# Docker usually auto-restarts containers (restart: unless-stopped)
# If not:
cd PROJECT_DIR
docker compose up -d

# If Docker daemon didn't start:
sudo systemctl start docker
docker compose up -d
\`\`\`
`;

export function getDiagnoseGuide(): string {
  return DIAGNOSE_GUIDE;
}
