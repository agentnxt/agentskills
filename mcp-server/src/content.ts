export const PHASE_1_ANALYSIS = `
## Phase 1: Project Analysis

### Step 1.1: Detect Project Stack

Scan the project root to identify the technology stack:

| Config File | Stack |
|-------------|-------|
| package.json | Node.js (Express, Fastify, Nest, Next, Nuxt) |
| requirements.txt / pyproject.toml | Python (Django, Flask, FastAPI) |
| go.mod | Go (Gin, Echo, Fiber) |
| Cargo.toml | Rust (Actix, Axum, Rocket) |
| Gemfile | Ruby / Rails |
| pom.xml / build.gradle | Java / Spring |
| composer.json | PHP / Laravel, Symfony |
| mix.exs | Elixir / Phoenix |
| *.csproj / *.sln | .NET / ASP.NET |

Record: language, version, web framework, database, cache/queue, frontend, auth, API style.

### Step 1.2: License Audit

| License | SaaS Viable? | Action |
|---------|-------------|--------|
| MIT, BSD, Apache-2.0, ISC | YES | Preserve copyright notice |
| LGPL-2.1, LGPL-3.0 | YES | Share modifications to LGPL files only |
| MPL-2.0 | YES | Share modifications to MPL files only |
| GPL-2.0, GPL-3.0 | CONDITIONAL | SaaS OK if not distributing |
| AGPL-3.0 | CAUTION | Must share ALL source code including SaaS modifications |
| SSPL | NO | Cannot offer as competing service |
| BSL / Commons Clause | NO | Most prohibit commercial SaaS |
| Elastic License 2.0 | CONDITIONAL | Cannot offer as managed service |

If AGPL: warn user, suggest boundary between AGPL code and proprietary SaaS layers.
If SSPL/BSL/Commons Clause: STOP — advise user SaaS may not be legally viable without commercial license.

### Step 1.3: Map Core Value Proposition

1. What problem it solves — Read README.md, docs/
2. Who uses it — Check issues, discussions
3. Key features — Examine routes, CLI commands, UI pages
4. Entry points — Find main(), app init, router definitions

### Step 1.4: Assess Current Architecture

| Check | How to Find | If Missing |
|-------|-------------|------------|
| User model | Grep for user schema/model | Create |
| Auth system | Grep for login/session/jwt | Add |
| DB migrations | Look for migrations/, alembic/, prisma/ | Create |
| Config system | Check .env, config/, settings.py | Add |
| API structure | Check routes/, controllers/ | Organize |
| Tests | Check test/, spec/, __tests__/ | Note |
| Docker | Check Dockerfile, docker-compose.yml | Create |
| CI/CD | Check .github/workflows/ | Create |
`;

export const PHASE_2_DESIGN = `
## Phase 2: SaaS Architecture Design

### Step 2.1: Multi-Tenancy Strategy

| Factor | DB-per-Tenant | Schema-per-Tenant | Row-Level Isolation |
|--------|---------------|-------------------|---------------------|
| Best when | Regulated, <100 tenants | PostgreSQL, moderate count | High tenant count, startups |
| Complexity | High | Medium | Low |
| Cost | High | Medium | Low |
| Data isolation | Physical | Logical (strong) | Logical (weak) |
| Recommended for | Healthcare, finance | Mid-market B2B | Dev tools, consumer SaaS |

Default: Row-level isolation.

### Step 2.2: Auth Strategy

| Project Has | Approach |
|------------|---------|
| No auth | Add JWT + refresh tokens + users table |
| Username/password | Extend with OAuth2, add JWT for API |
| Session-based | Keep for web, add JWT for API |
| OAuth already | Add multi-tenant scoping |
| Third-party (Auth0, Clerk) | Keep it, add tenant claims |

Default stack by framework:
- Node/Express: passport.js + JWT + bcrypt
- Node/Next.js: next-auth / auth.js
- Python/Django: django-allauth + simplejwt
- Python/FastAPI: python-jose + passlib
- Go: golang-jwt + bcrypt
- Ruby/Rails: devise + doorkeeper
- PHP/Laravel: Sanctum / Passport
- .NET: ASP.NET Identity + JWT Bearer

### Step 2.3: Tenant Data Model

Core entities: tenants (id, name, slug, plan, status, settings), users (id, email, password_hash, name), tenant_memberships (tenant_id, user_id, role), api_keys (tenant_id, key_hash, name, scopes, expires_at).

For row-level isolation: add tenant_id FK to EVERY existing table.

### Step 2.4: API Layer

Auth: /api/v1/auth/ (register, login, refresh, logout, forgot-password, reset-password)
Tenants: /api/v1/tenants/ (current, members)
Admin: /api/v1/admin/ (tenants CRUD, stats)
Billing: /api/v1/billing/ (plans, subscribe, portal, webhooks/lago)
Existing endpoints: now tenant-scoped under /api/v1/

### Step 2.5: Middleware Stack

1. CORS → 2. Rate limiter → 3. Request ID → 4. Auth (JWT/API key) → 5. Tenant context → 6. Usage tracking → 7. Route handler → 8. Error handler

### Step 2.6: Feature Tiers

free: 1000 API calls/mo, 100MB storage, 1 member, core features only
starter: 50K calls/mo, 5GB, 5 members, advanced features + API access
pro: 500K calls/mo, 50GB, 25 members, all features + SSO + custom domain

Present full plan to user for approval before coding.
`;

export const PHASE_3_IMPLEMENTATION = `
## Phase 3: Code Modifications

Execute in order. Verify project builds after each step.

### 3.1: Tenant Infrastructure
Create tenant data model using the project's migration framework:
- Prisma: schema.prisma models → prisma migrate
- Django: tenants app + models → makemigrations
- SQLAlchemy: models + Alembic migration
- Rails: rails generate model + migration
- Laravel: artisan make:model + migration
- Go: SQL migration files
- Knex/TypeORM: migration files

Create: Tenant, User (extend if exists), TenantMembership, ApiKey models + migrations + seed script.

### 3.2: Auth Layer
- Auth middleware: JWT verification, API key lookup
- Auth routes: register, login, refresh, logout, password reset
- JWT utility: sign, verify, refresh rotation
- Password hashing: bcrypt cost 12
- Auth guards: role-based (owner/admin/member/viewer)
- JWT payload: { sub: userId, tenantId, role, iat, exp }
- Access token: 15min TTL, Refresh token: 7 days (hashed, single-use)
- API keys: SHA-256 hash, prefix scs_live_ or scs_test_

### 3.3: Tenant Context Middleware
- Extract tenant_id from JWT or API key
- Load tenant (cache 60s TTL)
- Check status (suspended → 403)
- Load plan + feature flags
- Attach to request context

Query scoping by framework:
- Prisma: client extensions/middleware for tenant filter
- Django: custom manager with get_queryset() + thread-local tenant
- SQLAlchemy: session events or scoped query mixin
- ActiveRecord: default_scope with Current.tenant
- Eloquent: global scopes
- Go/raw SQL: query builder wrapper

### 3.4: Tenant-Scope Existing Models
For EVERY existing table with user data:
1. Add tenant_id column (UUID, NOT NULL, FK)
2. Migration to add column
3. Index on tenant_id + composite indexes
4. Update unique constraints (globally unique → unique-per-tenant)
5. Update ALL queries to filter by tenant_id

### 3.5: Usage Metering
- usage_events table (tenant_id, event_type, quantity, billing_period)
- Tracking middleware: increment API calls per tenant per period
- Limit check: exceeded → 429 with upgrade prompt
- Usage endpoint: GET /api/v1/usage

### 3.6: API Versioning
- Create /api/v1/ router group
- Move existing routes under prefix
- Add X-API-Version response header

### 3.7: Health Endpoints
- GET /healthz → { status: "ok" }
- GET /readyz → check DB + cache connections

### 3.8: Admin Dashboard
- GET /admin/tenants (list)
- GET /admin/tenants/:id (detail)
- POST /admin/tenants/:id/suspend
- POST /admin/tenants/:id/activate
- GET /admin/stats (totals, MRR, active users)

### 3.9: Environment Config
Create .env.example with: APP_NAME, APP_URL, DATABASE_URL, JWT_SECRET, JWT_ACCESS_TTL, JWT_REFRESH_TTL, LAGO_API_URL, LAGO_API_KEY, SMTP_*, REDIS_URL, RATE_LIMIT_*.
`;

export const PHASE_4_INFRASTRUCTURE = `
## Phase 4: Infrastructure & Deployment

### 4.1: Containerization
Multi-stage Dockerfile: builder stage (install + build) → production stage (slim image, nonroot user).
docker-compose.yml: app + db (postgres/mysql) + redis, with healthchecks and volumes.

### 4.2: CI/CD Pipeline
GitHub Actions: test job (with DB service container) → build job (Docker image).
Adapt setup action and test commands to project's language.

### 4.3: Database Migrations
- Use existing migration tool if present
- If none: numbered SQL files + _migrations tracking table
- Add migrate script to package.json/Makefile
- Run migrations before app start in deployment
`;

export const PHASE_5_BUSINESS = `
## Phase 5: Business Layer

### 5.1: Lago Integration (Open Source Billing)
- Deploy Lago instance (self-hosted via Docker or Lago Cloud)
- Lago API client wrapper (REST API + env LAGO_API_URL + LAGO_API_KEY)
- On tenant create → create Lago customer via POST /api/v1/customers
- Create Lago plans matching your tiers (free/starter/pro) via API or Lago UI
- Create Lago subscriptions: POST /api/v1/subscriptions (assign plan to customer)
- Usage-based billing: POST /api/v1/events to report metered usage events
- POST /webhooks/lago → handle events:
  - subscription.started → activate tenant plan
  - subscription.terminated → downgrade to free
  - invoice.created → record invoice
  - invoice.payment_status_updated → flag/unflag tenant payment status
- Billing portal: link to Lago customer portal or build custom UI using Lago API
- Add to tenant: lago_customer_id, lago_subscription_id, current_period_end

### 5.2: Pricing Config
free ($0): core features, conservative limits
starter ($29/mo): core + advanced, moderate limits
pro ($99/mo): all features, generous limits
enterprise (custom): all + SLA + SSO + dedicated support

### 5.3: Trial & Onboarding
- 14-day trial of starter plan on signup
- trial_ends_at column on tenants
- Background job: expire trial → downgrade to free
- Trial banner in UI
- Registration → user + tenant + trial
- Welcome/setup wizard endpoint
`;

export const PHASE_6_SECURITY = `
## Phase 6: Compliance & Security

### 6.1: Tenant Isolation Test
Create test: 2 tenants, data under tenant A, auth as tenant B, assert cross-tenant access returns 404/403.

### 6.2: Security Headers
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()

### 6.3: CORS
Dev: allow localhost. Prod: allow APP_URL only. Always: credentials, limited methods.

### 6.4: Rate Limiting
| Context | Free | Starter | Pro |
|---------|------|---------|-----|
| Unauthed | 20/min/IP | — | — |
| Authed API | 60/min | 300/min | 1000/min |
| Auth endpoints | 5/min/IP | 5/min/IP | 5/min/IP |

### 6.5: Input Validation
Audit all handlers for: missing validation (add Zod/Joi/Pydantic), SQL injection, XSS, mass assignment, file upload limits.

### 6.6: GDPR Scaffolding
- GET /api/v1/account/export → user + tenant data as JSON/ZIP
- DELETE /api/v1/account → soft-delete, hard-delete after 30 days
- Privacy policy placeholder
- Cookie consent banner (if frontend)
`;

export const EXECUTION_ORDER = `
## Execution Order & Verification

Step 3.1 (Tenant models)     → Run migrations, verify tables
Step 3.2 (Auth layer)        → Test register + login
Step 3.3 (Tenant middleware)  → Test tenant loading from JWT
Step 3.4 (Scope existing)    → Run existing tests
Step 3.5 (Usage metering)    → Test increment + limit check
Step 3.6 (API versioning)    → Verify routes under /api/v1/
Step 3.7 (Health endpoints)  → curl /healthz
Step 3.8 (Admin dashboard)   → Test admin routes
Step 3.9 (Env config)        → Verify .env.example
Step 4.1 (Docker)            → docker compose up
Step 4.2 (CI/CD)             → Verify workflow syntax
Step 4.3 (Migrations)        → Verify migration runner
Step 5.1 (Lago)              → Verify webhook parsing
Step 5.2 (Pricing)           → Verify config loads
Step 5.3 (Trial)             → Test trial on registration
Step 6.1 (Isolation)         → Run isolation test
Step 6.2-6.4 (Security)      → Verify headers, CORS, rate limits
Step 6.5 (Validation)        → Audit endpoints
Step 6.6 (GDPR)              → Test export + deletion

After all steps: run full test suite, fix regressions.
`;

export const IMPORTANT_NOTES = `
## Important Notes

- Preserve existing patterns. Follow the project's ORM, router, coding style.
- Do not rewrite working code. Add, wrap, extend.
- Every database query must be tenant-scoped. Missing tenant_id = data leak.
- Secrets in environment variables only. Never commit .env.
- Test after every step.
- This is not legal advice. Recommend consulting a lawyer for AGPL/SSPL/BSL.
`;

export function getFullGuide(): string {
  return [
    "# OSS-to-SaaS Conversion Guide",
    "",
    "You are a SaaS architect converting this open source project into a production-ready, multi-tenant SaaS product.",
    "Complete Phases 1-2 (analysis + design) and present the plan BEFORE writing any code.",
    "",
    PHASE_1_ANALYSIS,
    PHASE_2_DESIGN,
    PHASE_3_IMPLEMENTATION,
    PHASE_4_INFRASTRUCTURE,
    PHASE_5_BUSINESS,
    PHASE_6_SECURITY,
    EXECUTION_ORDER,
    IMPORTANT_NOTES,
  ].join("\n");
}

export function getPhase(phase: number): string {
  const phases: Record<number, string> = {
    1: PHASE_1_ANALYSIS,
    2: PHASE_2_DESIGN,
    3: PHASE_3_IMPLEMENTATION,
    4: PHASE_4_INFRASTRUCTURE,
    5: PHASE_5_BUSINESS,
    6: PHASE_6_SECURITY,
  };
  return phases[phase] || "Invalid phase number. Use 1-6.";
}
