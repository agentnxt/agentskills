# Self-Hosting Firecrawl on Coolify

Deploy Firecrawl to your VPS (`51.75.251.56`) via Coolify so the crawler runs against
your own infrastructure — no API credits, no rate limits, full data sovereignty.

---

## What you get

- Firecrawl API at `http://vps.agnxxt.com:3002` (or a subdomain via nginx)
- Same API shape as cloud: `/v1/scrape`, `/v1/crawl`, `/v1/map`
- No Fire-engine (cloud anti-bot layer) — but handles most JS sites fine via Playwright

---

## Docker Compose (deploy via Coolify)

Create a new Coolify service → Docker Compose → paste:

```yaml
version: "3.8"

services:
  firecrawl-api:
    image: ghcr.io/firecrawl/firecrawl:latest
    environment:
      - WORKER_MODE=api
      - REDIS_URL=redis://firecrawl-redis:6379
      - BULL_AUTH_KEY=${FIRECRAWL_API_KEY:-your-secret-key}
      - NUM_WORKERS_PER_QUEUE=8
      - PORT=3002
    ports:
      - "3002:3002"
    depends_on:
      - firecrawl-redis
    networks:
      - shared-infra_default
      - firecrawl-internal

  firecrawl-worker:
    image: ghcr.io/firecrawl/firecrawl:latest
    environment:
      - WORKER_MODE=worker
      - REDIS_URL=redis://firecrawl-redis:6379
      - BULL_AUTH_KEY=${FIRECRAWL_API_KEY:-your-secret-key}
      - NUM_WORKERS_PER_QUEUE=8
    depends_on:
      - firecrawl-redis
    networks:
      - firecrawl-internal

  firecrawl-redis:
    image: redis:7-alpine
    volumes:
      - firecrawl-redis-data:/data
    networks:
      - firecrawl-internal

volumes:
  firecrawl-redis-data:

networks:
  firecrawl-internal:
  shared-infra_default:
    external: true
```

**Environment variables to set in Coolify:**
```
FIRECRAWL_API_KEY=your-secret-key-here
```

---

## nginx reverse proxy (optional — expose as subdomain)

Add to your nginx config to expose as `crawl.openautonomyx.com`:

```nginx
server {
    listen 80;
    server_name crawl.openautonomyx.com;

    location / {
        proxy_pass http://127.0.0.1:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

Then SSL via Certbot:
```bash
sudo certbot --nginx -d crawl.openautonomyx.com
```

---

## Using the self-hosted instance

```bash
export FIRECRAWL_URL=http://vps.agnxxt.com:3002
export FIRECRAWL_API_KEY=your-secret-key-here

python scripts/crawl.py \
  --url "https://example.com" \
  --output ./output
```

Or if exposed via subdomain:
```bash
export FIRECRAWL_URL=https://crawl.openautonomyx.com
```

---

## Verify it's running

```bash
curl http://vps.agnxxt.com:3002/v1/scrape \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["markdown"]}'
```

Expected response:
```json
{"success": true, "data": {"markdown": "# Example Domain\n\n..."}}
```

---

## Limitations vs cloud

| Feature | Self-hosted | Cloud |
|---|---|---|
| Fire-engine (proxy rotation, anti-bot) | ❌ | ✅ |
| JS rendering (Playwright) | ✅ | ✅ |
| Clean markdown extraction | ✅ | ✅ |
| `/v1/crawl`, `/v1/scrape`, `/v1/map` | ✅ | ✅ |
| Rate limits | None (your infra) | Plan-based |
| Gartner / LinkedIn bypass | ❌ | ✅ (Fire-engine) |

For sites protected by enterprise anti-bot (Gartner, LinkedIn, Cloudflare Enterprise),
use the cloud API. Self-hosted handles 95% of public sites fine.
