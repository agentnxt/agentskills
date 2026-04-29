---
did: skill:020
name: oss-to-saas-analyzer
description: >
  Scores any OSS GitHub project across five commercial service archetypes —
  Managed Hosting, API Service, Consulting & Implementation, Managed Service
  (Ops), and Vertical SaaS — and recommends the cleanest service mix to build
  around it. Trigger on: "can I sell X as a service", "OSS to SaaS", "run oss
  to saas on X", "what services can I sell around X", "commercial strategy for
  X", "monetise X", "consulting on X", "managed service for X",
  "implementation for X", "provide APIs around X", or any request to evaluate
  an OSS project as a commercial opportunity.
---

# OSS-to-SaaS Analyzer

Given an OSS GitHub repo, propose the cleanest service business to build
around it. Evaluate all viable service archetypes and recommend the best
combination for the operator's context.

---

## Service Archetypes

Five ways to commercially wrap an OSS project. Each has different capital
requirements, margin profiles, and moats.

| # | Archetype | What you sell | Margin |
|---|---|---|---|
| A | **Managed Hosting** | Run the software for the customer — they get an endpoint | Medium |
| B | **API Service** | Wrap the engine in your API — customers call your layer | High |
| C | **Consulting & Implementation** | Set it up, integrate, train — time-based | High |
| D | **Managed Service (Ops)** | Ongoing ops in customer or your infra — SLA, monitoring, upgrades | Recurring |
| E | **Vertical SaaS** | Host + extend + sell to one specific industry segment | Highest |

---

## Inputs

| Input | Required | Notes |
|---|---|---|
| GitHub repo URL | Yes | e.g. `https://github.com/typesense/typesense` |
| Operator context | Optional | e.g. "Autonomyx, targeting SaaS builders" |
| Intended product name | Optional | e.g. AutonomyxSearch |
| Target segment | Optional | e.g. e-commerce, fintech, global developers |
| Deployment target | Optional | Default: Coolify / self-hosted VPS |

---

## Step 1 — Fetch repo signals

```
GET https://api.github.com/repos/{owner}/{repo}
  → stargazers_count, license.spdx_id, description, topics,
    forks_count, open_issues_count, pushed_at, default_branch

GET https://api.github.com/repos/{owner}/{repo}/contents/
  → look for: TRADEMARK, NOTICE, BRANDING, FUNDING.yml,
    docker-compose.yml, docker-compose.yaml, compose.yml

GET https://api.github.com/repos/{owner}/{repo}/contents/README.md
  → scan for: EE/Enterprise signals, cloud SaaS links,
    trademark notices, commercial restrictions, updater services,
    sponsor/funding mentions, competing hosted product

GET https://api.github.com/repos/{owner}/{repo}/releases/latest
  → tag_name, published_at — maintenance health

GET https://hub.docker.com/v2/repositories/{org}/{repo}/
  → pull_count — adoption and brand recognition
```

Also web search:
- Does upstream run a competing hosted SaaS? What do they charge?
- Existing resellers, hosters, implementation partners?
- Gartner / G2 category this product sits in
- Known consultants or agencies specialising in this product

---

## Step 2 — Foundation scoring (applies to all archetypes)

Score four foundation dimensions. These constrain all archetypes.

---

### F1 — Licence & Legal Rights (0–20)

| Licence | Score | Hosting | Consulting | Notes |
|---|---|---|---|---|
| MIT / Apache-2.0 / BSD | 20 | ✅ | ✅ | No obligations |
| GPL-2.0 / GPL-3.0 | 18 | ✅ | ✅ | Running as service ≠ distribution |
| MPL-2.0 / LGPL | 16 | ✅ | ✅ | File-level copyleft only |
| AGPL-3.0 | 10 | ✅ | ✅ | Modified source must be published if deployed |
| BUSL / SSPL / Commons Clause | 0 | 🔴 | Check terms | Stop — do not proceed with hosting |
| No licence / NOASSERTION | 0 | 🔴 | 🔴 | No rights granted |

Modifiers:
- Upstream README explicitly confirms SaaS hosting allowed → +2
- TRADEMARK file with usage restrictions → −3
- CLA required (upstream can relicence) → −2

---

### F2 — Project Health (0–20)

| Signal | Points |
|---|---|
| Commits in last 30 days | 5 |
| Latest release < 6 months old | 4 |
| > 100 contributors | 3 |
| > 5k stars | 3 |
| Active issue responses (not just opens) | 3 |
| Semver / no-breaking-changes policy | 2 |

Low score (< 8) → warn: operator may inherit maintenance burden.

---

### F3 — Upstream Competition Risk (0–20)

| Signal | Points |
|---|---|
| No upstream commercial product | 20 |
| Upstream sells enterprise licence only | 16 |
| Upstream SaaS targets enterprise / large scale only | 12 |
| Upstream SaaS competes at your price point | 6 |
| Upstream SaaS dominates your target segment | 2 |

Modifiers:
- Upstream SaaS USD-only, no regional pricing → +3
- Upstream usage-metered (you can offer flat) → +3
- No upstream implementation partner programme → +2 (consulting opening)
- Multiple well-funded hosters already in market → −3
- Upstream recently raised VC, likely to commoditise → −3

---

### F4 — Deploy & Ops Complexity (0–20)

| Signal | Points |
|---|---|
| Official Docker image exists | 4 |
| Single binary / minimal containers | 3 |
| Config via environment variables only | 3 |
| No mandatory managed cloud services | 3 |
| Built-in HA / clustering | 2 |
| Seamless version upgrades | 2 |
| RAM fits standard VPS (< 2GB base) | 2 |
| Active security patch cadence | 1 |

Subtract:
- Requires GPU → −4
- K8s / Helm only, no Compose → −4
- Mandatory paid cloud services → −3
- Frequent breaking upgrades → −3
- No backup/restore documentation → −2

---

## Step 3 — Archetype scoring

For each archetype compute a score using foundation scores +
archetype-specific signals. Produce a verdict for each.

Verdict thresholds per archetype (0–20 additional points):
- 16–20: ✅ Strongly viable
- 10–15: 🟡 Viable with conditions
- 5–9:  🟠 Marginal — only if no better option
- 0–4:  🔴 Not recommended

---

### Archetype A — Managed Hosting

You run the software. Customer gets endpoint + credentials + dashboard.
No server access. You own ops.

**Viable when:** Deploy complexity is low, multi-tenancy is native or
cheap to add, upstream leaves a price or regional gap.

Additional signals (0–20):
| Signal | Points |
|---|---|
| Native multi-tenancy (scoped keys, ACLs, namespaces) | 5 |
| REST API — easy to proxy and meter | 4 |
| Upstream usage-metered (you can offer flat monthly) | 4 |
| Regional hosting advantage (latency, compliance, currency) | 3 |
| Low RAM per tenant (< 512MB) | 2 |
| Single-tenant-per-container viable as isolation strategy | 2 |

What you must build:
- Tenant provisioning (namespace or container per customer)
- Scoped API key issuance per tenant
- Usage metering (records, queries, or resource-hours)
- Self-serve dashboard (index mgmt, key rotation, usage graph)
- Billing integration
- Per-tenant monitoring, alerting, backup, restore

Pricing: Resource-based (RAM/CPU/storage) OR usage-based (records/queries)
OR flat tier (free → starter → growth → enterprise).

---

### Archetype B — API Service

You wrap the OSS engine in your own API layer. Customers call your API.
You add auth, rate limiting, routing, transformation, enrichment.

**Viable when:** The engine's core function (search, inference,
transcription, embeddings) maps cleanly to an API call. You can add a
meaningful abstraction — normalised response format, multi-engine routing,
enrichment — that justifies your layer over calling the engine directly.

Additional signals (0–20):
| Signal | Points |
|---|---|
| Engine has clean REST API already | 5 |
| You add meaningful value at API layer (routing, enrichment, caching) | 4 |
| Multiple OSS engines can back your single API | 4 |
| High query volume expected (margins improve at scale) | 4 |
| Engine is stateless or near-stateless | 3 |

What you must build:
- API gateway (auth, rate limiting, routing, versioning)
- Unified API contract (your schema, not the engine's)
- Developer portal (docs, sandbox, API key management)
- Usage metering per API key
- SLA monitoring and uptime page

Pricing: Per-call, per-unit-of-output, or tiered monthly credits.

---

### Archetype C — Consulting & Implementation

You help customers install, configure, integrate, and launch the OSS
product in their own infrastructure. Project-based or retainer.

**Viable when:** The product is powerful but non-trivial to set up.
Integration work is significant. Customers have their own infra but
lack the expertise. No dominant implementation partner exists.

Additional signals (0–20):
| Signal | Points |
|---|---|
| Complex initial setup (schema design, relevance tuning, pipelines) | 5 |
| Significant integration work (sync from DB, CRM, CMS, ERP) | 4 |
| No official implementation partner programme | 4 |
| Active community of users asking for help | 3 |
| Enterprise sales cycle — customers budget for professional services | 2 |
| Certification or training programme exists | 2 |

What you must build:
- Implementation methodology (discovery → design → build → launch)
- Reference architectures for common stacks
- Integration playbooks per source system
- Fixed-price packaged offerings (e.g. "Launch in 4 weeks")
- Statement of work templates

Pricing: Fixed project fee, T&M, or ongoing retainer.
No infra cost — highest margin archetype.

---

### Archetype D — Managed Service (Ongoing Ops)

You run the software in the customer's own infrastructure or yours,
and own the ops: monitoring, upgrades, tuning, incident response,
backups. Ongoing recurring contract.

**Viable when:** Customers have compliance or data residency requirements
preventing hosted SaaS, but lack internal ops capacity. Or the software
is business-critical enough they want an expert permanently on call.

Additional signals (0–20):
| Signal | Points |
|---|---|
| Frequent upgrades or complex upgrade path | 4 |
| Performance tuning is ongoing (not set-and-forget) | 4 |
| Regulated industry customers (finance, health, govt) | 4 |
| Data residency requirements common in target market | 4 |
| Customers have existing on-prem or private cloud infra | 2 |
| Security patches require ops expertise | 2 |

What you must build:
- Runbook library (incident response, upgrade, backup/restore)
- Monitoring stack (alerting, dashboards, capacity planning)
- SLA definition and measurement tooling
- Customer reporting cadence (monthly health reports)
- Escalation and on-call process

Pricing: Monthly retainer per environment, tiered by SLA level
(business hours / 24×5 / 24×7).

---

### Archetype E — Vertical SaaS

Host + extend + sell a complete product to one specific industry.
Customers never know or care what OSS engine is underneath.

**Viable when:** A specific industry has unserved search/discovery/
retrieval needs. You can build domain-specific features on top of the
engine — product catalogue search, patient record search, legal document
search — and charge a premium that generic hosting cannot justify.

Additional signals (0–20):
| Signal | Points |
|---|---|
| Clear vertical with specific and underserved pain | 5 |
| Industry data models you can pre-build (schemas, taxonomies) | 4 |
| Compliance requirements create switching cost | 3 |
| Existing vertical players have poor search (legacy tech) | 3 |
| You have domain expertise in the vertical | 3 |
| Premium pricing accepted in the vertical | 2 |

What you must build:
- Vertical-specific data model + schema templates
- Connectors to industry systems (ERP, PIM, EMR, CRM, etc.)
- Domain-specific UI components (facets, filters, result cards)
- Compliance layer if regulated
- Vertical-specific onboarding, support, and documentation

Pricing: Flat monthly per account, tiered by usage or seats.
Premium to generic hosting — the vertical focus justifies it.

---

## Step 4 — Produce the report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OSS-TO-SAAS ANALYSIS — {UPSTREAM_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  FOUNDATION SCORES
  ─────────────────────────────────────────────
  F1  Licence & Legal Rights        {n}/20  {emoji}
  F2  Project Health                {n}/20  {emoji}
  F3  Upstream Competition Risk     {n}/20  {emoji}
  F4  Deploy & Ops Complexity       {n}/20  {emoji}
  ─────────────────────────────────────────────
  Foundation Total                  {n}/80

  LICENCE
  ────────
  {spdx_id} — {plain English: what you can and cannot do}
  Obligations: {list or "none"}

  UPSTREAM COMMERCIAL LANDSCAPE
  ───────────────────────────────
  {What upstream sells, at what price, to whom. Where the gaps are.}

  SERVICE ARCHETYPE SCORES
  ─────────────────────────────────────────────────────────────────
  A  Managed Hosting          {n}/20  {emoji}  {VERDICT}
  B  API Service              {n}/20  {emoji}  {VERDICT}
  C  Consulting & Impl.       {n}/20  {emoji}  {VERDICT}
  D  Managed Service (Ops)    {n}/20  {emoji}  {VERDICT}
  E  Vertical SaaS            {n}/20  {emoji}  {VERDICT}

  RECOMMENDED SERVICE MIX
  ────────────────────────
  Primary:   {archetype + name} — {why this is the lead motion}
  Secondary: {archetype + name} — {why this complements primary}
  Later:     {archetype + name} — {when to add this and why}
  Avoid:     {archetype + name} — {why not, at least not now}

  GO-TO-MARKET SEQUENCE
  ──────────────────────
  Phase 1 — {what to launch first, to whom, at what price}
  Phase 2 — {what to add once Phase 1 has traction}
  Phase 3 — {longer-term expansion motion}

  WHAT YOU MUST BUILD
  ────────────────────
  Layer 1 — Infrastructure
    {list}
  Layer 2 — Tenant / customer isolation
    {list}
  Layer 3 — Self-serve / customer-facing
    {list}
  Layer 4 — Moat / differentiation
    {list}

  PRICING MODEL
  ──────────────
  {Concrete tier sketch — free tier, paid tiers, what changes between
   them, billing mechanism, currency notes}

  REPO STRATEGY
  ──────────────
  Engine fork:   {org/repo} — {public/private} — {opensaasapps or keep private}
  Product repo:  {org/repo} — private — your service layer
  Attribution:   {Recommended "Powered by X" phrasing}
  Upstream sync: Daily GitHub Action — PR on drift

  RISKS
  ──────
  {2–4 specific risks with mitigation for each}

  SPONSORSHIP
  ────────────
  {Funding options found — links — recommended action}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Returning to a calling skill

```json
{
  "upstream": "{owner}/{repo}",
  "licence": "{spdx_id}",
  "licence_verdict": "clean|obligations|restricted|blocked",
  "foundation_score": {n},
  "archetype_scores": {
    "A_managed_hosting": {n},
    "B_api_service": {n},
    "C_consulting": {n},
    "D_managed_service": {n},
    "E_vertical_saas": {n}
  },
  "recommended_primary": "A|B|C|D|E",
  "recommended_secondary": "A|B|C|D|E|null",
  "deploy_ready": true|false,
  "risks": ["{risk1}", "{risk2}"]
}
```
