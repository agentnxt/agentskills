---
name: feature-gap-analyzer
description: >
  Performs a feature gap analysis between two or more enterprise software applications. Accepts
  user-supplied inputs (PDF files, URLs, or pasted text) from trusted analyst sources — Gartner
  Magic Quadrant, Gartner Market Guide, Forrester Wave, IDC MarketScape, G2, Capterra — and uses
  them as primary evidence, supplemented by live web research on Gartner Peer Insights. Covers
  10 universal dimensions (platform features, AI/ML, API, data ingestion, reporting, integrations,
  security, mobile, support, pricing) plus auto-detected category-specific dimensions. Supports
  any number of apps. Outputs: scored matrix (0-100%), side-by-side feature table, and narrative
  gap report. Always trigger for: compare software, feature gap analysis, vendor evaluation,
  procurement, competitive analysis, "what does X have that Y doesn't", "compare A vs B", "which
  tool has better AI/reporting/integrations". Covers all 500+ Gartner categories: CRM, HCM, BI,
  ERP, ITSM, Marketing Automation, DevOps, Cybersecurity, Supply Chain, and more.
---

# Feature Gap Analyzer

Analyzes feature gaps between two or more software applications. Feature existence is confirmed
exclusively from the application's official documentation and GitHub repository. Analyst reports,
Gartner Peer Insights, and G2 are used for scoring context and positioning only — never as the
primary source for confirming whether a feature exists.

---

## Step 1 - Collect inputs and prompt for analyst reports

### 1a. Extract app names and scope

From the user's message, identify:
- **App names** — required (ask if missing)
- **Category** — infer from app names if not stated
- **Scope** — full analysis (default) or a specific dimension (e.g. "just AI features")

### 1b. Ask the user for analyst documents (always do this)

After confirming app names, always ask:

> "Do you have any analyst reports for these products? Sharing them will significantly improve
> the accuracy of the analysis. You can provide any of the following:
>
> - **PDF upload** — Gartner Magic Quadrant, Gartner Market Guide, Forrester Wave,
>   IDC MarketScape, or any other analyst report
> - **URL** — a public product page, feature comparison page, press release, or review link
> - **Pasted text** — copy-paste from a report, review, or product page
>
> If you don't have any of these, no problem — I'll research using Gartner Peer Insights,
> G2, and official documentation."

Wait for the user's response before proceeding to research. If they provide inputs, process them
in Step 2 before doing any web research.

---

## Step 2 - Process user-supplied inputs

Handle each input type as follows. All inputs from recognised analyst sources are treated as
**Tier 1 (highest trust)** evidence and override or enrich web-sourced data.

### PDF files

Read the uploaded PDF and extract:
- Vendor/product names mentioned
- Feature capability assessments, ratings, or scores
- Analyst commentary on strengths and weaknesses
- Positioning language (e.g. "Leader", "Challenger", "Strong Performer")
- Any comparison tables, capability matrices, or scoring rubrics
- Publication date and analyst firm name

Label all data extracted from PDFs as: `[Source: <Analyst Firm> <Report Type> <Year>]`

### URLs

Fetch the URL and apply the following strict source rules.

**Feature existence — ONLY these two sources confirm a feature exists:**

| Source | What to fetch | Label |
|---|---|---|
| **Official documentation** | vendor.com/docs, /features, /api, /help, /developers, /changelog, /release-notes | `[Docs: <URL> — <date>]` |
| **GitHub repository** | github.com/<org>/<repo> — README, feature flags, release tags, open/closed issues, wiki | `[GitHub: <repo URL> — <date>]` |

A feature may only be marked ✅ GA, 🔶 Beta, 🔷 Early Access, or 🚩 Feature Flag if confirmed
by at least one of these two sources. No other source is sufficient to assert feature existence.

**Scoring context sources (use to inform scoring weight and positioning — NOT feature existence):**
- Gartner Peer Insights — reviewer sentiment, relative strength ratings, satisfaction scores
- Analyst PDFs (MQ, Wave, MarketScape) — market positioning, analyst-assessed capability depth
- G2 / Capterra / TrustRadius — user satisfaction signals, comparative ratings
- Press releases — announcement of new features (follow up with docs/GitHub to confirm availability)

These sources help you calibrate *how well* a confirmed feature is implemented, but cannot
confirm that a feature exists in the first place.

**Roadmap sources (for 🗓️ Upcoming Official and 💬 Upcoming Signal labels only):**
- Official roadmap pages, changelog entries, conference announcements → `[Roadmap: Official]`
- Community idea boards, analyst roadmap references → `[Roadmap: Community signal]`

**Ignore entirely for feature purposes:**
- Competitor-authored comparison pages
- Third-party review aggregators or reseller sites
- Social media, Reddit, forums
- Marketing landing pages without doc links

Label data from URLs as: `[Source: <type> — <URL> — <date fetched>]`

### Pasted text

Assess the source of the pasted content and apply the same feature-existence rule:
- If the user identifies it as from **official docs or a GitHub page** — use to confirm feature existence (Track A)
- If the user identifies it as from an **analyst report** — use for scoring context only (Track B); ask for docs/GitHub link to confirm the feature itself
- If the source is unclear — ask: "Where is this from? If it's from the official docs or GitHub, I can use it to confirm feature existence. If it's from a review or analyst source, I'll use it for context only."
- If it appears to be **vendor marketing copy** — treat as a signal to search the docs for confirmation; do not confirm feature existence from marketing copy alone

---

## Step 3 - Build the evidence map

Before scoring, build an internal evidence map for each app across each dimension:

```
App: [Name]
Dimension: [e.g. AI / ML Capabilities]

Feature existence (docs/GitHub only):
  [Docs: docs.vendor.com/ai-copilot — Mar 2026] AI copilot — confirmed GA
  [Docs: docs.vendor.com/changelog — Feb 2026] Generative AI content — "Early Access, opt-in"
  [GitHub: github.com/vendor/repo/releases — Mar 2026] Predictive analytics — confirmed in v4.2 release notes
  [Docs: docs.vendor.com/roadmap — Jan 2026] Real-time streaming — "Coming Q2 2026"
  !! NOT FOUND in docs or GitHub: Native mobile offline — cannot confirm existence

Scoring context (analyst / review sources):
  [Gartner MQ 2025] Positioned as Leader; AI copilot strength highlighted
  [Gartner Peer Insights, 189 reviews, avg 4.3] AI assistant satisfaction strong
  [G2, 312 reviews] Users rate predictive analytics highly vs competitors

Roadmap signals:
  [Roadmap: Official] Changelog Oct 2025: "Generative AI — Early Access"
  [Roadmap: Official] Roadmap page: "Real-time streaming — Q2 2026"
  [Roadmap: Community signal] IdeaExchange: 1,200 votes for mobile offline (status: Planned)

Feature status (derived — only from docs/GitHub confirmed items):
  AI copilot: ✅ GA
  Predictive analytics: ✅ GA
  Generative AI content: 🔷 Early Access
  Real-time streaming: 🗓️ Upcoming Official — Q2 2026
  Native mobile offline: ❓ Roadmap Unknown (not in docs or GitHub; community signal only)

Confidence: High / Medium / Low
```

Tiers and feature status labels are defined in `autonomyx-vocabulary/SKILL.md`:
- Evidence tiers (Tier 1 / 2 / 3 definitions and label formats) → Section 4
- Feature status badges (GA / Beta / Early Access / Feature Flag / Upcoming / etc.) → Section 3
- Confidence levels → Section 5

Read those sections before scoring if you need a reminder of the definitions.

---

## Step 4 - Research

Research has two separate tracks. Run both for every app.

---

### Track A — Feature existence (PRIMARY — docs and GitHub only)

This track determines what features actually exist. Only these two sources count.

**Step A1 — Official documentation**
```
Search: "<App Name>" official documentation features
Fetch: docs.<vendor>.com  OR  <vendor>.com/docs  OR  <vendor>.com/features
Also fetch: changelog, release notes, API reference, developer portal
```
Look for: feature pages, capability lists, release notes confirming GA/Beta/Early Access status,
API endpoints that imply feature availability, feature flag documentation.

**Step A2 — GitHub repository**
```
Search: "<App Name>" github.com/<org>
Fetch: github.com/<org>/<repo>
```
Look for: README feature lists, CHANGELOG / releases tab (confirm shipped versions),
open/closed issues mentioning feature availability, wiki pages, feature flag config files,
.github/FEATURE_FLAGS or equivalent, labels like "released", "beta", "experimental".

If no public GitHub repo exists, note: `[GitHub: No public repository found]` and rely
solely on official docs for feature confirmation.

**A feature may only receive a non-❌ status badge if confirmed by Track A.**
If a feature is mentioned by an analyst or in G2 reviews but cannot be found in docs or
GitHub, it must be marked ❓ Roadmap Unknown until confirmed.

---

### Track B — Scoring context (SECONDARY — analyst and review sources)

This track informs *how well* confirmed features are implemented, and provides comparative
positioning. It does NOT confirm feature existence.

**Gartner Peer Insights**
```
Search: "<App Name>" site:gartner.com/reviews
```
Extract: overall rating, satisfaction scores per dimension, reviewer quotes about quality,
depth, and reliability of features. Use to calibrate scores for confirmed features.

**Analyst PDFs (if user-supplied)**
Use for: market positioning context, relative capability assessments, analyst cautions.
Never use as sole evidence that a feature exists.

**G2 / Capterra (fallback scoring context)**
Use for: comparative satisfaction ratings, user sentiment about feature quality.
Never use as sole evidence that a feature exists.

### Roadmap research (always do this for every app)

For each app, actively research its public roadmap and upcoming features. This is essential for
accurately flagging gaps as "coming soon" vs "truly missing". Use multiple sources:

**Official roadmap sources (Tier 2 — confirmed):**
```
Search: "<App Name>" roadmap 2025 2026 upcoming features
Search: "<App Name>" product roadmap site:<vendor-domain>.com
Search: "<App Name>" "coming soon" OR "in beta" OR "early access" OR "feature flag" 2025
```

- Check the vendor's official roadmap page (e.g. vendor.com/roadmap, Trello/Productboard boards,
  public GitHub project boards)
- Check release notes and changelog pages for beta/preview labels
- Check the vendor's developer blog or "What's New" / "Release Notes" pages

**Community and analyst roadmap signals (Tier 3 — signal only, not confirmed):**
```
Search: "<App Name>" roadmap community feature requests 2025
Search: "<App Name>" "planned" OR "under review" OR "coming soon" site:community.<vendor>.com
```

- Product community idea boards (e.g. Salesforce IdeaExchange, HubSpot Ideas, Jira community)
- G2 reviewer comments mentioning upcoming capabilities
- Conference keynote announcements (Dreamforce, Inspire, Inbound, etc.)
- Analyst report roadmap references

**Label roadmap evidence clearly in all outputs:**
- `[Roadmap: Official]` — vendor-confirmed via roadmap page, release notes, or official blog
- `[Roadmap: Community signal]` — unconfirmed, from idea boards or user reports
- `[Roadmap: Analyst note]` — cited by analyst firm in a report

---

## Step 5 - Detect category and load feature checklist

### 5a — Resolve category (via Autonomyx Vocabulary)

Follow `autonomyx-vocabulary/SKILL.md` Section 1–2 for category resolution:
1. Gartner Peer Insights → canonical Gartner market name
2. Not on Gartner → G2 → map via vocabulary skill → label "via G2 mapping"
3. No mapping → G2 label directly → label "G2 only"
4. Neither → infer from product description → label "Inferred"

Display at the top of every report:
`Category: [Name] | Source: [Gartner Peer Insights / G2 mapped / G2 only / Inferred]`

---

### 5b — Load feature checklist from Notion

## Notion Backend — Persistent Storage

The Master Feature Registry is stored in Notion. Use the Notion MCP tools to read and write.

### Database IDs

| Database | Purpose | Data Source ID |
|---|---|---|
| Categories | Software market categories | `collection://decfa7c6-0c11-4630-8dd0-4e6e02dbed03` |
| Features | Feature checklist per category | `collection://1e4f2636-41f8-4d81-bb18-4c31b550ae54` |
| Apps | Applications analysed per category | `collection://bb0d6e68-ddda-4601-b532-85fc9c73c2e8` |
| Feature Status | App + Feature + Status junction | `collection://486dd914-9937-4667-8102-02de3321d0fb` |

Parent page: https://www.notion.so/32a33ce516978194a603c7be33badd53

### Reading features for a category

```
1. Query Categories to find the category page URL by name
2. Query Features filtered by Category = <category page URL>
   → returns all features for that category with Section, Description, Source
```

### Writing a new feature discovery

```
Create a page in Features with:
  "Feature Name": <name>
  "Description": <desc>
  "Section": <one of the 10 section options>
  "Category": [<category page URL>]
  "Source": <docs or GitHub URL>
  "Discovered In": <app name>
  "Added": <YYYY-MM-DD>
```

### Writing a feature status (gap analysis result)

```
Create a page in Feature Status with:
  "Name": "<App Name> — <Feature Name>"
  "App": [<app page URL>]
  "Feature": [<feature page URL>]
  "Status": <GA | Beta | Early Access | Feature Flag | Upcoming (Official) | Upcoming (Signal) | Not Present | Roadmap Unknown>
  "Evidence Source": <docs or GitHub URL>
  "Notes": <analyst quote, roadmap ETA, or review excerpt>
  "Last Verified": <YYYY-MM-DD>
```

### Adding a new app

```
Create a page in Apps with:
  "App Name": <name>
  "Category": [<category page URL>]
  "Docs URL": <official docs URL>
  "GitHub URL": <public GitHub repo URL>
  "Gartner URL": <Gartner Peer Insights page URL>
  "Last Analysed": <YYYY-MM-DD>
```


To load the feature checklist for the resolved category:
1. Use the Notion MCP to query the Categories database for the category name
2. Use the returned page URL to query the Features database filtered by that category
3. Use every returned feature as your checklist — assess each app against every feature listed

**If a feature is not found in the Notion Features database:**
Treat it as a new discovery and follow the write-back protocol in Step 5c below.

---

### 5c — Write new feature discoveries back to the registry

During gap analysis, you may encounter features that exist in one or both products but are
NOT listed in the registry. These are new discoveries — they must be added back to the
master list so future analyses benefit.

**Discovery criteria:** A feature is "new" if:
- It is not listed in the registry under the product's category
- It appears to be a genuine capability (not a minor UX element or marketing claim)
- It is confirmed by at least Tier 2 evidence (official docs, G2 grid, or analyst report)

**Write-back process:**
1. Identify all new features found during the analysis (across all apps compared)
2. For each new feature confirmed at Tier 2+ evidence (docs or GitHub):
   - Use the Notion MCP to create a page in the Features database (see Notion Backend section above)
3. For the apps being compared, create or update Feature Status records in the Feature Status database
4. If the app does not yet exist in the Apps database, create it first
5. Confirm the writes to the user: "I've added [N] new features and [M] feature status records to your Notion registry."

**Report the write-back to the user** at the end of the analysis:
> "📚 Registry update: I found [N] new feature(s) not previously in the master feature
> registry and have added them to `saas-standardizer/references/feature-registry.md`:
> - [Feature 1] → added to [Category] > [Sub-section]
> - [Feature 2] → added to [Category] > [Sub-section]
>
> These will be included in future gap analyses for [category] products."

If no new features were found:
> "📚 Registry: All features found are already in the master registry. No updates needed."

---

Once the category is resolved and the registry is loaded, add relevant dimensions beyond the universal set:

### Universal Dimensions (always included)

| # | Dimension | What to assess |
|---|---|---|
| 1 | **Platform Features** | Core functionality, UX, workflow automation, customization |
| 2 | **AI / ML Capabilities** | Native AI, copilot, predictive analytics, gen AI, agents |
| 3 | **API & Developer Tools** | REST/GraphQL, webhooks, SDKs, docs quality, sandbox |
| 4 | **Data Ingestion** | Import formats, ETL connectors, real-time streaming, bulk upload |
| 5 | **Reporting & Analytics** | Dashboards, custom reports, export, embedded BI, alerting |
| 6 | **Integrations & Ecosystem** | Native integrations, marketplace, iPaaS support |
| 7 | **Security & Compliance** | SOC 2, GDPR/CCPA, SSO/MFA/RBAC, data residency, audit logs |
| 8 | **Mobile** | Native apps, offline support, responsive web, push notifications |
| 9 | **Support & Onboarding** | Tiers, SLAs, docs quality, community, implementation help |
| 10 | **Pricing & Scalability** | Per-seat vs usage-based, enterprise tiers, scaling headroom |

### Category-Specific Additions

**CRM / Sales Force Automation**
Pipeline & opportunity management, CPQ, territory management, sales forecasting,
email/calendar sync, deal rooms

**Marketing Automation**
Journey builder / campaign orchestration, A/B testing, lead scoring & routing,
attribution modeling, CDP integration, ABM

**HR / HCM**
Payroll (native vs integrated), performance management, compliance & labor law,
workforce planning, LMS, recruiting/ATS

**ERP / Finance**
GL/AP/AR depth, multi-entity & multi-currency, consolidation, revenue recognition,
audit trails, SOX/IFRS compliance, budgeting & forecasting

**Analytics & Business Intelligence**
Data modeling & semantic layer, live query vs extract, data catalog, NLQ,
embedded analytics, governance & lineage

**Project Management**
Gantt/timeline, resource management & capacity planning, portfolio views,
time tracking, budget management, risk management

**ITSM / IT Service Management**
ITIL v4 alignment, incident/problem/change management, SLA management,
CMDB/asset management, self-service portal, knowledge management

**Customer Success / Support**
Customer health scoring, 360-degree view, playbook automation, NPS/CSAT,
escalation workflows, renewal/expansion tracking

**DevOps / Engineering Tools**
CI/CD pipelines, IaC support, observability & APM, secrets management,
GitOps workflows, container/Kubernetes support

**Cybersecurity**
Threat detection, MITRE ATT&CK mapping, SOAR, compliance reporting,
SIEM/EDR/XDR integration, false positive rate

**Supply Chain / Procurement**
Supplier management, demand forecasting, inventory optimization, PO/contract lifecycle,
multi-tier visibility, logistics integration

**Data Management / Integration**
MDM, data quality & cleansing, connector library breadth, real-time vs batch,
data lineage, governance frameworks

For any category not listed above, use judgment to add 3-5 relevant domain dimensions.

---

## Step 6 - Score each dimension (0-100%)

| Score Range | Meaning |
|---|---|
| 85-100% | Best-in-class — market-leading, frequently praised by analysts and users |
| 70-84% | Strong — full-featured, minor gaps or occasional complaints |
| 50-69% | Adequate — core capability present but notable limitations |
| 30-49% | Limited — partial implementation, significant gaps vs competitors |
| 0-29% | Weak / Absent — feature missing or severely underdeveloped |

**Rules:**
- Tier 1 evidence (analyst PDFs, Gartner Peer Insights) carries the most weight
- Every score needs at least one cited source
- Never fabricate — mark N/A if data is genuinely unavailable
- For AI: always distinguish Native GA / Beta / Third-party integration / Roadmap only
- Gap Delta = Score(A) minus Score(B); "Tied" = gap of 5% or less

**Roadmap score adjustments:**
- A feature that is **Beta or Early Access** scores as if it is 60-70% of full GA value
  (it exists but carries risk; don't penalise fully, but don't credit as complete)
- A feature that is **Upcoming (Official)** with a confirmed date within 12 months scores
  at 30-40% — it signals intent but buyers cannot rely on it today
- A feature that is **Upcoming (Signal / unconfirmed)** scores 0% for current capability
  but must be noted in the Gap row as a signal
- A feature that is **Feature Flag** scores as 50-60% — it exists but requires vendor
  intervention and is not self-serve
- Always show the *current* score and annotate the roadmap trajectory:
  e.g. "45% today → 🗓️ Expected GA Q3 2026"
- When a gap is closing due to an upcoming feature, flag it explicitly in the Gap column:
  e.g. "Gap: -33% (closing — App A has Official roadmap item Q2 2026)" 

---

## Step 7 - Produce all three output components

### Output A: Scored Feature Matrix

```
| Dimension               | App A | App B | Gap (A-B) | Leader  |
|-------------------------|-------|-------|-----------|---------|
| Platform Features       |  82%  |  71%  |   +11%    | App A   |
| AI / ML Capabilities    |  55%  |  88%  |   -33%    | App B   |
| API & Developer Tools   |  79%  |  80%  |   -1%     | Tied    |
| Data Ingestion          |  74%  |  52%  |   +22%    | App A   |
| Reporting & Analytics   |  61%  |  85%  |   -24%    | App B   |
| Integrations            |  88%  |  76%  |   +12%    | App A   |
| Security & Compliance   |  85%  |  83%  |   +2%     | Tied    |
| Mobile                  |  65%  |  58%  |   +7%     | App A   |
| Support & Onboarding    |  72%  |  69%  |   +3%     | Tied    |
| Pricing & Scalability   |  70%  |  75%  |   -5%     | App B   |
| [Category Dimension]    |  xx%  |  xx%  |   ...     | ...     |
| **Overall Average**     |  73%  |  74%  |   -1%     | Tied    |
```

For 3+ apps, add columns per app; show range (highest - lowest) instead of a single delta.

---

### Output B: Side-by-Side Feature Presence Table

Drill into specific features per dimension. Include analyst evidence where available.

Use the following status badges consistently — never just "Yes" or "No":

| Badge | Meaning |
|---|---|
| ✅ GA | Generally Available — production-ready |
| 🔶 Beta | Available but not yet GA; opt-in or limitations may apply |
| 🔷 Early Access | Available to select customers only; not broadly released |
| 🚩 Feature Flag | In the product but gated; must be enabled by vendor/admin |
| 🗓️ Upcoming (Official) | Confirmed on public roadmap or announced — add timeframe if known |
| 💬 Upcoming (Signal) | Unconfirmed — community votes, analyst hint, or keynote mention only |
| ❌ Not Present | No evidence of feature existing or being planned |
| ❓ Roadmap Unknown | Absent with no roadmap information found |

Example:
```
### AI / ML Capabilities
| Feature                       | App A                              | App B                          |
|-------------------------------|------------------------------------|--------------------------------|
| Native AI assistant / copilot | 🔶 Beta (opt-in, limited to Ent)   | ✅ GA — praised in MQ 2025     |
| Predictive analytics          | ✅ GA                              | ✅ GA                          |
| Generative AI content         | 🗓️ Upcoming (Official — Q2 2026)  | ✅ GA                          |
| AI-powered forecasting        | ✅ GA — strong per GPI reviews     | 🔶 Beta                        |
| LLM / AI platform integration | 🚩 Feature Flag (enable via admin) | ✅ GA — native                 |
| Agentic AI / autonomous tasks | 💬 Upcoming (Signal — IdeaExchange 980 votes) | ❌ Not Present    |
| Natural language query        | ❌ Not Present                     | 🔷 Early Access (sign-up req.) |
```

Group features by dimension; cover all universal + category dimensions.

---

### Output C: Narrative Gap Analysis Report

**1. Executive Summary** (2-3 sentences)
Overall gap picture, which app leads, the most critical gap, and whether analyst evidence
from user-supplied documents was used.

**2. Analyst Intelligence** (only if user provided PDFs or reports)
Summarise what the analyst report(s) said about each vendor — positioning quadrant,
key strengths and cautions as identified by the analyst, and publication date.

**3. Where [App A] Leads**
Bullet list: dimension, specific strength, evidence source.

**4. Where [App B] Leads**
Same structure.

**5. Critical Gaps (score difference >= 20%)**
For each critical gap:
- Dimension and score delta
- Specific missing capabilities — with their current feature status badge (❌ / 🔶 / 🗓️ etc.)
- Business impact: who is affected and in what scenarios
- Analyst commentary on the gap (if available from supplied docs)
- **Roadmap outlook**: Is this gap closing? Include:
  - If the missing feature is in Beta/Early Access: expected GA timeline if known
  - If it is on the official roadmap: confirmed delivery timeframe
  - If it is only a community signal: vote count and current status label (e.g. "Planned", "Under Review")
  - If no roadmap information exists: state "No public roadmap signal found"
- Mitigation options: third-party integrations or workarounds available TODAY while the feature matures

**6. Feature Parity Areas (gap <= 5%)**
Dimensions where both apps are comparable.

**7. Recommendations**
- Choose [App A] if: ...
- Choose [App B] if: ...
- Gap mitigations for each app

**8. Next Steps**
Which gaps to probe in a demo, what to request in a POC, which teams to involve.

---

## Step 8 - Source and confidence footer

```
### Sources & Confidence
| Dimension | Primary Source | Tier | Data Date | Confidence |
|---|---|---|---|---|
| AI Capabilities | Gartner MQ 2025 (user PDF) | 1 | 2025 | High |
| Platform Features | Gartner Peer Insights 142 reviews | 1 | Feb 2026 | High |
| Data Ingestion | G2 feature grid | 2 | Jan 2026 | Medium |
| Pricing | Vendor pricing page | 2 | Mar 2026 | Medium |

Confidence: High = Tier 1 analyst data (20+ data points)
            Medium = Tier 2 official sources or limited Tier 1
            Low = Tier 3 marketing claims only
```

---

## Quality Rules

1. **Never fabricate** — mark N/A if data is unavailable; never estimate without evidence
2. **Cite everything** — every feature status badge needs a docs or GitHub source; every score needs a source
3. **Docs and GitHub are the ONLY feature sources** — a feature may only be marked as existing
   (any badge other than ❌ or ❓) if confirmed by official documentation or the application's
   GitHub repository; analyst reports, G2, Gartner Peer Insights, and Capterra may inform scoring
   weight but cannot alone assert that a feature exists
4. **Analyst PDFs inform scoring depth, not existence** — use analyst reports to calibrate how
   strong or weak a confirmed feature is; never use them as the sole evidence a feature is present
5. **AI nuance** — distinguish: Native GA / Beta / Third-party integration / Roadmap only
6. **Recency** — prefer 2024-2026 data; flag anything older than 18 months
7. **Scope flexibility** — for single-dimension requests, produce only that section of all three outputs
8. **Scale to N apps** — extend tables and add one narrative block per app for 3+ comparisons
9. **Gartner first for scoring context**  — always try Gartner Peer Insights for scoring context (Track B) before other review sources — always try Gartner Peer Insights before other web sources
10. **Proactively ask** — always invite the user to share PDFs/URLs at Step 1b; don't skip this
10. **Use Autonomyx Vocabulary for categories** — always read `autonomyx-vocabulary/SKILL.md`
    Section 1–2 for category resolution; never guess the Gartner category without checking;
    fall back to G2 via the mapping table if Gartner listing is absent
11. **Read the registry before scoring** — always load `saas-standardizer/references/feature-registry.md`
    for the relevant category before building the feature presence table; use it as the checklist,
    not as a ceiling — products may have features beyond what the registry lists
13. **Write back all new discoveries** — any feature confirmed at Tier 2+ that is not in the
    registry must be appended before the analysis is complete; never skip the write-back step
13. **Registry is the single source of truth** — if a feature is in the registry and was not
    assessed, that is an incomplete analysis; every registry item for the category must have a
    status badge for every app being compared
15. **Roadmap research is mandatory** — always research roadmap for every app before finalising
    the feature presence table; a gap labelled ❌ without checking the roadmap is incomplete
15. **Never conflate roadmap with reality** — a feature on the roadmap is NOT a current capability;
    always show current score separately from future trajectory; never upgrade a score based solely
    on an unconfirmed roadmap signal
17. **Status badge consistency** — refer to Autonomyx Vocabulary Section 3 for the canonical badge list; — always use the 8 defined status badges (GA / Beta / Early Access /
    Feature Flag / Upcoming Official / Upcoming Signal / Not Present / Roadmap Unknown);
    never use vague terms like "partial", "limited", "coming soon" without a badge
