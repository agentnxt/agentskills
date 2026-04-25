export const CONFIGURE_GUIDE = `
# Mode: Configure — Set Up Services via MCP Tools

Programmatically configure services after the stack is running. Uses MCP servers for each service when available.

## Configuration Workflow

1. Ask: "Which services do you want to configure?" or detect from .fast-saas.json
2. For each service, check if the MCP server is available in the conversation
3. If MCP available: use MCP tools directly
4. If MCP not available: provide step-by-step manual instructions
5. After each service, confirm success before moving to the next

---

## Lago (Billing) — opensaasapps-lago MCP

### Standard SaaS Pricing Plans

Create these plans:

| Plan | Monthly | API Calls | Storage | Members |
|---|---|---|---|---|
| Free | $0 | 1,000 (then $0.001/call) | 100 MB | 1 |
| Starter | $29 | 10,000 (then $0.0005/call) | 1 GB | 5 |
| Pro | $99 | 100,000 (then $0.0002/call) | 10 GB | 25 |
| Enterprise | Custom | Unlimited | Custom | Custom |

MCP tools:
- lago_create_billable_metric — create api_calls metric (sum aggregation)
- lago_create_plan — create each pricing plan
- lago_create_plan_charge — attach metered charges to plans

---

## n8n (Workflows) — opensaasapps-n8n MCP

### Pre-built Workflow Templates

Import these:
- welcome-email.json — Sends onboarding email on tenant signup
- usage-alert.json — Hourly check for tenants near usage limits
- error-alert.json — GlitchTip error forwarding
- backup-schedule.json — Daily 3am database backups
- billing-sync.json — Lago billing event processing
- onboarding-flow.json — 3-day onboarding drip campaign

MCP tools:
- n8n_create_workflow — import each workflow JSON
- n8n_activate_workflow — activate after testing
- n8n_create_credential — set up PostgreSQL and SMTP credentials

---

## NocoDB (Admin Dashboard) — opensaasapps-nocodb MCP

### Admin Base Setup

- Base name: "SaaS Admin"
- Tables: tenants, users, tenant_memberships, api_keys, usage_events
- Views: Tenant Kanban (group by plan), User Grid, Usage Calendar

MCP tools:
- nocodb_create_base — create the admin base
- nocodb_create_table — link to PostgreSQL tables
- nocodb_create_view — set up kanban/grid/calendar views

---

## GlitchTip (Error Tracking) — opensaasapps-glitchtip MCP

- Create organization and project
- Retrieve the DSN for SDK integration
- Set up alert rules (email on 5+ occurrences in 1 hour)

MCP tools:
- glitchtip_create_project — create error tracking project
- glitchtip_get_dsn — retrieve DSN for SDK setup

---

## Uptime Kuma — opensaasapps-uptime-kuma MCP

### Standard Monitors

| Monitor | Type | URL | Interval |
|---|---|---|---|
| App | HTTP(s) | https://app.DOMAIN | 60s |
| Auth | HTTP(s) | https://auth.DOMAIN/api/status | 60s |
| Billing API | HTTP(s) | https://billing-api.DOMAIN/health | 120s |
| Storage | HTTP(s) | https://storage.DOMAIN/minio/health/live | 120s |
| PostgreSQL | TCP | postgres:5432 | 60s |
| Redis | TCP | redis:6379 | 60s |

MCP tools:
- uptime_kuma_add_monitor — add each monitor
- uptime_kuma_create_status_page — create public status page

---

## Matomo (Analytics) — opensaasapps-matomo MCP

- Add website: app.DOMAIN
- Create goals: Signup, Upgrade, API Key Created
- Configure custom dimensions: tenant_id, plan

MCP tools:
- matomo_add_site — register the application
- matomo_add_goal — create conversion goals

---

## Mautic (Email Marketing) — opensaasapps-mautic MCP

- Create segments: Trial Users, Starter Plan, Pro Plan, Churned
- Create email templates: Welcome, Feature Announcement, Upgrade Prompt
- Configure SMTP to use Stalwart

MCP tools:
- mautic_create_segment — create user segments
- mautic_create_email — create email templates

---

## Stalwart (Mail) — opensaasapps-stalwart MCP

- Add domain
- Create noreply@ and support@ accounts
- Generate DKIM keys

MCP tools:
- stalwart_add_domain — configure email domain
- stalwart_create_account — create mailboxes
`;

export function getConfigureGuide(): string {
  return CONFIGURE_GUIDE;
}
