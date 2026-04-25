export const MODULE_REGISTRY = `
# Autonomyx SaaS Factory — Module Registry

22 open-source services across 5 layers + 10 Langflow AI agent components, pre-wired into a Docker Compose stack.

## Module Table

| ID | Name | Layer | Depends On | Subdomain | Health URL |
|---|---|---|---|---|---|
| postgres | PostgreSQL 16 | essential | — | — | TCP :5432 |
| redis | Redis 7 | essential | — | — | TCP :6379 |
| caddy | Caddy | essential | — | — | :80/:443 |
| logto | Logto | core | postgres | auth, auth-admin | /api/status |
| lago | Lago | core | postgres, redis | billing, billing-api | /health |
| rustfs | RustFS | core | — | storage, storage-console | /minio/health/live |
| glitchtip | GlitchTip | ops | postgres, redis | errors | / (200) |
| uptime-kuma | Uptime Kuma | ops | — | status | / (302) |
| grafana-stack | Grafana+Prometheus+Loki | ops | — | monitor | /api/health |
| matomo | Matomo | growth | — (own MariaDB) | analytics | / (200) |
| mautic | Mautic | growth | postgres | email | / (302) |
| stalwart | Stalwart | growth | — | — (SMTP ports) | /healthz |
| nocodb | NocoDB | growth | postgres | admin | /api/v1/health |
| n8n | n8n | growth | postgres | auto | /healthz |
| appsmith | Appsmith | growth | — | tools | / (200) |
| docmost | Docmost | growth | postgres, redis | docs | / (200) |
| posthog | PostHog | growth | postgres, redis | product | /_health |
| librechat | LibreChat | ai | redis (+ MongoDB, Meilisearch) | chat | /api/health |
| langflow | Langflow | ai | postgres | flow | /health |
| ollama | Ollama | ai | — | models | /api/tags |
| claude-agent | Claude Agent | ai | — | agent | /health |
| langfuse | Langfuse | ai | postgres | observe | /api/public/health |

## Layer Summary

| Layer | Services | Purpose | Always On? |
|---|---|---|---|
| **Essential** | PostgreSQL, Redis, Caddy | Foundation — database, cache, reverse proxy | Yes |
| **Core** | Logto, Lago, RustFS | Auth, billing, storage — the SaaS primitives | Yes |
| **Ops** | GlitchTip, Uptime Kuma, Grafana | Errors, uptime, metrics — observability | Recommended |
| **Growth** | Matomo, Mautic, Stalwart, NocoDB, n8n, Appsmith, Docmost, PostHog | Analytics, email, automation, admin | Pick what you need |
| **AI** | LibreChat, Langflow, Ollama, Claude Agent, Langfuse | LLM chat, flow builder, local models, agents, observability | Optional |

## Resource Requirements

| Profile | Modules | vCPU | RAM | Disk |
|---|---|---|---|---|
| Minimal | essential + core | 2 | 4 GB | 20 GB |
| Standard | + ops | 3 | 6 GB | 30 GB |
| Full | + all growth | 4 | 8 GB | 40 GB |
| AI | + all ai | 6 | 16 GB | 60 GB |

## Dependency Graph

\`\`\`
essential (postgres, redis, caddy)
  └── core (logto, lago → postgres+redis; rustfs → standalone)
       └── ops (glitchtip → postgres+redis; uptime-kuma, grafana → standalone)
            └── growth (matomo → own MariaDB; mautic, nocodb, n8n, docmost → postgres)
                 └── ai (librechat → redis+MongoDB; langflow → postgres; ollama, claude-agent → standalone)
\`\`\`

## Docker Compose Profiles

Use COMPOSE_PROFILES to control which layers start:

\`\`\`bash
# Minimal (essential + core)
COMPOSE_PROFILES=essential,core docker compose up -d

# Standard (+ ops)
COMPOSE_PROFILES=essential,core,ops docker compose up -d

# Full (everything)
COMPOSE_PROFILES=essential,core,ops,growth,ai docker compose up -d

# Cherry-pick
COMPOSE_PROFILES=essential,core,ops,n8n,matomo docker compose up -d
\`\`\`

## Multi-Tenancy Architecture

\`\`\`
Request → Caddy (TLS) → Auth Guard (Logto JWT) → Tenant Context → Rate Limiter → Usage Tracker → Route Handler
                                                       ↓                              ↓
                                                  PostgreSQL                    Redis (buffer)
                                                  (tenant data)                     ↓
                                                                              Lago (billing)
\`\`\`

Tables: tenants, users, tenant_memberships, api_keys, usage_events
Isolation: Row-level (tenant_id column on all tenant-scoped tables)
Plans: free (1K calls), starter (10K), pro (100K), enterprise (unlimited)

## AI MCP Tools (14 tools via fast_saas_* prefix)

### Ollama (5)
- fast_saas_ollama_list_models — List available local models
- fast_saas_ollama_pull_model — Download a model
- fast_saas_ollama_generate — Text generation (completion)
- fast_saas_ollama_chat — Chat completion
- fast_saas_ollama_delete_model — Remove a model

### Langflow (4)
- fast_saas_langflow_list_flows — List all flows
- fast_saas_langflow_get_flow — Get flow details
- fast_saas_langflow_run_flow — Execute a flow
- fast_saas_langflow_list_components — List available components

### Claude Agent (3)
- fast_saas_claude_run — Start an agent job
- fast_saas_claude_get_job — Get job status/result
- fast_saas_claude_list_jobs — List all jobs

### AI System (2)
- fast_saas_ai_health — Health check all AI services
- fast_saas_langfuse_health — Langfuse observability status

## Langflow Custom Components (10 installed)

Agentic AI platform components available as nodes in Langflow flows at flow.openautonomyx.com:

| Component | Provider | What it does |
|---|---|---|
| Salesforce Agentforce | Salesforce | Invoke Agentforce agents via Einstein Platform API |
| Vertex AI Agent Builder | Google | Invoke Dialogflow CX agents via Vertex AI |
| Microsoft Copilot Studio | Microsoft | Invoke Copilot Studio bots via Direct Line API |
| OpenAI Assistants (GPTs) | OpenAI | Invoke Assistants API v2 with threads + tool use |
| AWS Bedrock Agents | Amazon | Invoke Bedrock Agents with knowledge bases + action groups |
| Dify | Dify | Invoke Dify chatbots, completions, and workflows |
| Docker Agent (Model Runner) | Docker | Connect to Docker Model Runner or any OpenAI-compatible container |
| Claude Agent SDK | Anthropic | Invoke Claude via Messages API or Agent SDK server |
| Flowise | Flowise | Invoke Flowise chatflows and agentflows |
| LangSmith | LangChain | Query traces, datasets, examples, and log feedback |
`;

export function getModuleRegistry(): string {
  return MODULE_REGISTRY;
}
