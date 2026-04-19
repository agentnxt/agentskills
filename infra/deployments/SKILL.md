---
name: openatonomyx-deploy
description: >
  Deploys the full OpenAtonomyx stack — Logto (IdP), Liferay (portal),
  Lago (billing), ERPNext (ERP), Odoo (business apps), and n8n (workflow
  automation) — as a unified Docker Compose monorepo with centralized
  Logto OIDC authentication. Trigger on: "deploy openatonomyx",
  "spin up the full stack", "deploy liferay lago erpnext odoo logto n8n",
  "set up the openatonomyx platform".
---

# OpenAtonomyx Deploy

Deploys a six-app open-source enterprise stack with Logto as the centralized
identity provider. All services run on a shared Docker network and authenticate
through Logto OIDC.

---

## Architecture

```
                    ┌─────────────┐
                    │   Logto     │  ← Central IdP (OIDC)
                    │   :3001     │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┬───────┐
           ▼       ▼       ▼       ▼       ▼       ▼
       ┌───────┐┌──────┐┌──────┐┌─────┐┌──────┐┌─────┐
       │Liferay││ Lago ││ERPNxt││Odoo ││ n8n  ││ ... │
       │ :8080 ││ :8090││:8069 ││:8070││:5678 ││     │
       └───────┘└──────┘└──────┘└─────┘└──────┘└─────┘
           │       │       │       │       │
       Postgres  Postgres MariaDB Postgres Postgres
         + ES    + Redis  + Redis
```

## Services

| Service | Image | Port | License | Upstream |
|---|---|---|---|---|
| **Logto** | `svhd/logto` | 3001, 3002 | MIT | github.com/logto-io/logto |
| **Liferay** | `liferay/dxp` | 8080 | LGPL-2.1 | github.com/liferay/liferay-portal |
| **Lago** | `getlago/api` | 3000, 8090 | AGPL-3.0 | github.com/getlago/lago |
| **ERPNext** | `frappe/erpnext` | 8069 | GPL-3.0 | github.com/frappe/erpnext |
| **Odoo** | `odoo:17.0` | 8070 | LGPL-3.0 | github.com/odoo/odoo |
| **n8n** | `n8nio/n8n` | 5678 | Sustainable Use | github.com/n8n-io/n8n |

---

## Deployment Steps

### Step 1 — Environment Setup

```bash
cd deployments/
cp .env.example .env
```

Fill in all `# REQUIRED` values. Generate secrets:
```bash
# Quick secret generator for all fields
openssl rand -hex 32   # passwords, encryption keys
openssl rand -base64 32 # cookie keys
openssl genrsa 2048     # RSA private key (Lago)
```

### Step 2 — Start Logto First

```bash
docker network create openatonomyx
docker compose -f logto/docker-compose.yml up -d
```

Wait for healthy status, then open the Logto Admin Console (port 3002) and
complete initial setup.

### Step 3 — Create OIDC Applications in Logto

Run the setup script or create apps manually in Logto Console:

```bash
chmod +x logto/setup-apps.sh
DOMAIN=example.com PROTOCOL=https ./logto/setup-apps.sh
```

Copy each Client ID + Secret into `.env`:
- `LIFERAY_OIDC_CLIENT_ID` / `LIFERAY_OIDC_CLIENT_SECRET`
- `LAGO_OIDC_CLIENT_ID` / `LAGO_OIDC_CLIENT_SECRET`
- `ERPNEXT_OIDC_CLIENT_ID` / `ERPNEXT_OIDC_CLIENT_SECRET`
- `ODOO_OIDC_CLIENT_ID` / `ODOO_OIDC_CLIENT_SECRET`
- `N8N_OIDC_CLIENT_ID` / `N8N_OIDC_CLIENT_SECRET`

### Step 4 — Deploy All Services

```bash
docker compose up -d
```

Or deploy individually:
```bash
docker compose up -d liferay liferay-db liferay-es
docker compose up -d lago-api lago-front lago-db lago-redis lago-worker
docker compose up -d erpnext erpnext-db erpnext-redis-cache erpnext-redis-queue erpnext-worker
docker compose up -d odoo odoo-db
docker compose up -d n8n n8n-db
```

### Step 5 — Post-Deploy Configuration

| App | Post-deploy action |
|---|---|
| **Liferay** | OIDC is pre-wired via env vars. Verify in Control Panel → SSO |
| **Lago** | OIDC auto-configured. Test login at Lago UI |
| **ERPNext** | Go to Setup → Integrations → Social Login → add Logto as Custom provider |
| **Odoo** | Install `auth_oauth` module → Settings → OAuth Providers → add Logto |
| **n8n** | SSO is wired via env vars (Enterprise feature for full OIDC) |

### Step 6 — Verify SSO

For each app:
1. Open the app's login page
2. Click "Sign in with Logto" (or equivalent)
3. Authenticate on Logto
4. Confirm redirect back and user creation

---

## Coolify Deployment

To deploy via Coolify instead of raw Docker Compose, use the
**coolify-one-click-deploy** skill with this repo as the source:

```
Mode: opensaasapps (public) or unboxd.cloud (private)
Repo: this monorepo
Compose path: deployments/docker-compose.yml
```

The skill will handle forking, env var wiring, and Coolify service creation.

---

## Directory Structure

```
deployments/
├── docker-compose.yml       ← Master orchestrator (extends all sub-stacks)
├── .env.example             ← All environment variables
├── SKILL.md                 ← This file
├── logto/
│   ├── docker-compose.yml   ← Logto + Postgres
│   └── setup-apps.sh        ← Creates OIDC apps for each service
├── liferay/
│   └── docker-compose.yml   ← Liferay + Postgres + Elasticsearch
├── lago/
│   └── docker-compose.yml   ← Lago API + Frontend + Worker + Postgres + Redis
├── erpnext/
│   └── docker-compose.yml   ← ERPNext + MariaDB + Redis (cache + queue)
├── odoo/
│   └── docker-compose.yml   ← Odoo + Postgres
└── n8n/
    └── docker-compose.yml   ← n8n + Postgres
```
