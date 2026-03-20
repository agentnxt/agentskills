# Liferay 7.4 CE — Deployment Guide (Ubuntu + Docker + Dokploy)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Dokploy                       │
│  (localhost:3000 — manages compose deployments)  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Nginx    │  │ Liferay  │  │ PostgreSQL   │  │
│  │ :443/:80 │──│ :8080    │──│ :5432        │  │
│  │ SSL term │  │ CE 7.4   │  │ 15-alpine    │  │
│  └──────────┘  └────┬─────┘  └──────────────┘  │
│                      │                           │
│                ┌─────┴──────┐                    │
│                │ Elastic    │                    │
│                │ search     │                    │
│                │ 7.17       │                    │
│                └────────────┘                    │
│                                                  │
│  Traefik (Dokploy's reverse proxy :80/:443)     │
└─────────────────────────────────────────────────┘
```

## Docker Compose for Dokploy

This is the compose file to set via Dokploy's API or UI. Use `sourceType: "raw"` in Dokploy.

```yaml
services:
  postgresql:
    image: postgres:15-alpine
    container_name: liferay_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: lportal
      POSTGRES_USER: liferay
      POSTGRES_PASSWORD: CHANGE_ME
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U liferay -d lportal"]
      interval: 10s
      timeout: 5s
      retries: 5

  elasticsearch:
    image: elasticsearch:7.17.18
    container_name: liferay_search
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  liferay:
    image: liferay/portal:7.4.3.120-ga120  # Or custom image
    container_name: liferay_portal
    restart: unless-stopped
    depends_on:
      postgresql:
        condition: service_healthy
    environment:
      LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_DRIVER_UPPERCASEC_LASS_UPPERCASEN_AME: org.postgresql.Driver
      LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_URL: jdbc:postgresql://postgresql:5432/lportal
      LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_USERNAME: liferay
      LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_PASSWORD: CHANGE_ME
      LIFERAY_JVM_OPTS: "-Xms1g -Xmx2g"
    volumes:
      - liferay_data:/opt/liferay/data
      - /opt/liferay/portal-ext.properties:/opt/liferay/portal-ext.properties:ro
    ports:
      - "8080:8080"

  nginx:
    image: nginx:1.25-alpine
    container_name: liferay_nginx
    restart: unless-stopped
    depends_on:
      - liferay
    ports:
      - "8443:443"
    volumes:
      - /opt/liferay/nginx.conf:/etc/nginx/conf.d/liferay.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro

volumes:
  pg_data:
  es_data:
  liferay_data:
```

### Using Existing Volumes (Data Migration)

When redeploying with existing data, declare volumes as external:

```yaml
volumes:
  pg_data:
    external: true
    name: liferay_pg_data        # Existing volume name
  es_data:
    external: true
    name: liferay_es_data
  liferay_data:
    external: true
    name: liferay_liferay_data
```

Find existing volumes: `docker volume ls | grep liferay`

## Dokploy API Integration

### Authentication (Better Auth)

```bash
# Login - returns token + sets session cookie
curl -s -c /tmp/dokploy_cookies -X POST http://localhost:3000/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'
```

All subsequent calls use cookie auth: `-b /tmp/dokploy_cookies`

### Create Project + Compose Service

```bash
# Create project
curl -s -X POST http://localhost:3000/api/trpc/project.create \
  -b /tmp/dokploy_cookies \
  -H "Content-Type: application/json" \
  -d '{"json":{"name":"Liferay","description":"Liferay Portal"}}'

# Create compose service
curl -s -X POST http://localhost:3000/api/trpc/compose.create \
  -b /tmp/dokploy_cookies \
  -H "Content-Type: application/json" \
  -d '{"json":{"name":"liferay","projectId":"PROJECT_ID","environmentId":"ENV_ID"}}'

# Set compose file (sourceType: raw)
curl -s -X POST http://localhost:3000/api/trpc/compose.update \
  -b /tmp/dokploy_cookies \
  -H "Content-Type: application/json" \
  -d '{"json":{"composeId":"COMPOSE_ID","sourceType":"raw","composeFile":"YAML_CONTENT"}}'

# Deploy
curl -s -X POST http://localhost:3000/api/trpc/compose.deploy \
  -b /tmp/dokploy_cookies \
  -H "Content-Type: application/json" \
  -d '{"json":{"composeId":"COMPOSE_ID"}}'
```

## portal-ext.properties

Place at `/opt/liferay/portal-ext.properties` on host, mount read-only into container.

```properties
# ── Database ──────────────────────────────────────────────
jdbc.default.driverClassName=org.postgresql.Driver
jdbc.default.url=jdbc:postgresql://postgresql:5432/lportal
jdbc.default.username=liferay
jdbc.default.password=CHANGE_ME

# ── Elasticsearch (Remote) ────────────────────────────────
com.liferay.portal.search.elasticsearch7.configuration.ElasticsearchConfiguration.operationMode=REMOTE
com.liferay.portal.search.elasticsearch7.configuration.ElasticsearchConfiguration.networkHostAddresses=["http://elasticsearch:9200"]

# ── File Storage ──────────────────────────────────────────
dl.store.impl=com.liferay.portal.store.file.system.AdvancedFileSystemStore

# ── Web Server (HTTPS behind proxy) ──────────────────────
web.server.protocol=https
web.server.host=yourdomain.com
web.server.http.port=-1
web.server.https.port=-1

# ── Virtual Hosts ─────────────────────────────────────────
virtual.hosts.valid.hosts=localhost,127.0.0.1,yourdomain.com

# ── Security ──────────────────────────────────────────────
auth.token.check.enabled=true
session.timeout=30
company.security.strangers=false
setup.wizard.enabled=false

# ── Company ───────────────────────────────────────────────
company.name=Your Company
company.default.name=Your Company
default.guest.friendly.url=/web/exp

# ── Mail (Optional) ──────────────────────────────────────
# mail.session.mail=true
# mail.session.mail.smtp.host=smtp.example.com
# mail.session.mail.smtp.port=587
# mail.session.mail.smtp.user=user
# mail.session.mail.smtp.password=password
# mail.session.mail.smtp.auth=true
# mail.session.mail.smtp.starttls.enable=true
```

## Nginx Configuration (SSL Termination)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://yourdomain.com$request_uri; }
}

server {
    listen 443 ssl;
    http2 on;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    client_max_body_size 100M;

    location / {
        proxy_pass http://liferay_portal:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|woff2?)$ {
        proxy_pass http://liferay_portal:8080;
        proxy_set_header Host $host;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## Startup Timeline

| Phase | Duration | Indicator |
|-------|----------|-----------|
| PostgreSQL ready | ~10s | `pg_isready` passes healthcheck |
| Elasticsearch ready | ~15s | Port 9200 responds |
| Liferay JVM start | ~10s | `Server initialization in [X] milliseconds` |
| OSGi bundle loading | ~20-40s | `Started initial/dynamic/web bundles` |
| Auto-deploy themes | ~10s | `Themes for ... copied successfully` |
| Full startup | ~60-90s | `Server startup in [X] milliseconds` |
| First DB initialization | ~3-5 min | Only on fresh database |

## Monitoring

```bash
# Container status
docker ps --filter "name=liferay"

# Liferay logs (follow)
docker logs -f liferay_portal 2>&1

# Check startup complete
docker logs liferay_portal 2>&1 | grep "Server startup"

# Check HTTP response
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080

# Database connectivity
docker exec liferay_db psql -U liferay -d lportal -c "SELECT 1;"

# Elasticsearch health
curl -s http://localhost:9200/_cluster/health
```

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Liferay can't connect to DB | `docker logs liferay_portal` for JDBC errors | Verify PG is healthy, check credentials in portal-ext |
| Blank page / 500 | Check if ES is running | Restart elasticsearch container |
| Theme not showing | `docker logs` for deploy errors | Check WAR ownership, no web.xml |
| SSL redirect loop | portal-ext `web.server.protocol` | Ensure nginx passes `X-Forwarded-Proto` |
| Slow startup | First run creates DB schema | Wait 3-5 min on first deploy |
| Port 80/443 conflict with Dokploy | Traefik uses those ports | Use 8443 for nginx, or route through Traefik |
