---
did: skill:025
name: saas-standardizer
description: >
  Produces exhaustive, standardized profiles of SaaS products across 18 dimensions for procurement and comparison decisions. Trigger whenever a user wants to evaluate, profile, research, or compare any SaaS product — even if they don't say "evaluate". Trigger on: "tell me about [product]", "compare [A] vs [B]", "why choose X over Y", "what's the G2 rating", "who backs [product]", "is X open source", "how fast is [company] growing", "what do Reddit users say about X", "how is [product] priced", "is [product] SOC 2 certified", "what support does [product] offer", "what's on [product]'s roadmap". Covers: Features, Use Cases (role-specific), Login Methods, APIs, Data Ingestion, Integrations, Pricing, Security & Compliance, Support & SLA, Roadmap & Vision, Competitive Positioning, Analyst Rankings (G2/Gartner), Open Source Health (GitHub/Docker), Funding & Backing, Notable Clients, Growth Signals, Customer References, and Community Sentiment. Always be exhaustive.
---

# SaaS Standardizer

Produces exhaustive, standardized profiles of SaaS products across 23 fixed dimensions. Every dimension must be covered completely — leave no sub-point blank. If information is unavailable, state it explicitly rather than skipping.

---

## Skill Configuration

Set these values before use. Claude reads them at the start of every session:

| Key | Description | Example |
|---|---|---|
| `WEBHOOK_URL` | Endpoint to POST reports to after user confirms | `https://hooks.zapier.com/hooks/catch/abc/xyz/` |
| `WEBHOOK_SECRET` | Optional HMAC-SHA256 signing secret for request verification | `my-secret-token` |

**To configure:** Edit the lines below and replace the placeholder values.

```
WEBHOOK_URL=        # ← paste your endpoint here
WEBHOOK_SECRET=     # ← paste your secret here (optional, leave blank to skip signing)
```

Supported portal types (any webhook-compatible endpoint works):
- Zapier Webhooks / Make (Integromat) scenarios
- Airtable automations
- Notion API via middleware
- Custom REST APIs
- Slack incoming webhooks
- n8n, Pipedream, or any HTTP trigger

---

## Input Sources

Accept information from any combination of:
- **Web research** — search product website, docs, changelog, pricing page, security page, API reference
- **URL** — fetch the provided URL and follow links to docs, pricing, integrations pages
- **Uploaded file** — PDF, doc, or other file with product info
- **User notes** — pasted text, bullet points, or freeform description
- **User-provided research** — analyst reports, internal evaluations, vendor responses, RFP answers, demo notes, or any credible third-party source the user shares

When the user provides a URL or file, prioritize that. Use web search to fill every gap. Always list all sources used at the top of the profile.

---

## User-Provided Research: Integration Protocol

When a user shares their own research — a document, pasted findings, analyst report, vendor questionnaire response, pricing quote, demo notes, internal eval, or any cited third-party source — treat it as a **first-class input**, not a supplement.

### Credibility Assessment

Before integrating, briefly assess the source:

| Source type | Credibility treatment |
|---|---|
| Vendor-provided (datasheet, sales deck, RFP response) | Include but label as vendor-claimed — cross-check independently where possible |
| Independent analyst (Gartner, Forrester, IDC, G2, Capterra) | High trust — prioritise over web search findings |
| User's own internal eval / demo notes | High trust for experiential claims (UX, support quality, sales process) — label as first-hand observation |
| Press / tech media (TechCrunch, InfoQ, The Register, etc.) | Medium trust — include with source and date |
| Community / Reddit / forums | Medium trust — useful for sentiment, flag as anecdotal |
| Unattributed or unclear origin | Include with a caveat: *"Source credibility unverified — treat as unconfirmed"* |

### How to integrate

1. **Do not discard or override user research** — even if it conflicts with what web search returns
2. **Merge it into the relevant dimension(s)** — place findings where they belong in the report structure, not in a separate "user said" block
3. **Where user research conflicts with other sources**, surface the conflict explicitly:
   > *"User-provided research (Gartner report, 2025) states X. Vendor's website currently states Y. The discrepancy may reflect a recent product change — recommend confirming with vendor."*
4. **Where user research fills a gap** that web search couldn't answer, mark it clearly:
   > *"Per user-provided RFP response (dated [date]): [finding]"*
5. **Where user research is more recent or more specific** than anything found via web search, treat it as the authoritative source for that point
6. **Always cite user-provided research** in the Sources list at the top of the report, with as much detail as available (document title, author, date, origin)

### Improving the knowledge base

If the user's research reveals something materially new — a pricing structure not published anywhere, a security certification not listed on the vendor's site, a known bug or limitation from hands-on use — acknowledge it explicitly:

> "This is a valuable detail not surfaced in public sources. I've incorporated it into the report under [Dimension X] and flagged it as first-hand / analyst-verified."

Never flatten user-provided findings into generic phrasing. Keep the specificity — if they share exact numbers, quotes, or test results, reproduce them accurately with attribution.

---

## Output Modes

| Situation | Output Mode |
|---|---|
| Single product, first mention | **Full Profile** |
| Single product, specific question | **Dimension Spotlight** |
| Two or more products | **Side-by-Side Comparison** |
| User says "evaluate" or "assess" | **Full Profile** |
| User says "compare" or "vs" | **Side-by-Side Comparison** |
| User asks about one dimension | **Dimension Spotlight** |

---

## The 18 Standard Dimensions — Exhaustive Coverage Required

Every bullet point below must be addressed in the output. If unknown, write: *"Not publicly documented — confirm with vendor."*

---

### Feature Registry Protocol

The **Master Feature Registry** lives at `references/feature-registry.md` in this skill.
It is the canonical, living list of expected features per software category, maintained
across all Autonomyx skills.

**Before profiling Dimension 1 (Features) for any product:**
1. Use the Notion MCP to query the Features database filtered by the product's category
   (see Notion Backend — Data Source IDs above for the collection URLs)
2. Find all features matching the product's software category
3. Use the category's feature list as your **checklist** — assess the product against every
   feature listed, rather than discovering features freeform
4. This ensures consistent, comparable coverage across all profiles

**Feature existence rule — strictly enforced:**
A feature may only be recorded as present (any status other than ❌ Not Present or
❓ Roadmap Unknown) if confirmed by ONE of these two sources:
- **Official documentation** — docs site, feature pages, API reference, changelog, release notes
- **GitHub repository** — README, CHANGELOG, release tags, closed issues confirming shipment

Analyst reports, G2, Capterra, Gartner Peer Insights, and press releases may inform how
*well* a feature works (used for Differentiators and scoring depth) but cannot alone confirm
a feature exists. If a feature is widely discussed in reviews but not found in docs or GitHub,
record it as ❓ Roadmap Unknown and note the review signal separately.

**After completing Dimension 1:**
- Review the features you found and confirmed via docs/GitHub
- Identify any features NOT yet listed in the registry for this category
- For each new feature confirmed by docs or GitHub, use the Notion MCP to create a
  page in the Features database with: Feature Name, Description, Section, Category relation,
  Source URL, Discovered In, and Added date
- If the category doesn't exist in Notion yet, create it in the Categories database first
- Confirm to the user: "I found [N] new feature(s) not previously in the master registry
  and have added them: [list]. The registry has been updated."
- If no new features were found, note: "All features found are already in the master registry."

This keeps the registry growing over time — every product profiled makes future profiles
more thorough.

### Notion Backend — Registry Location

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



---

### 1. Features

**How to use:** Read `references/feature-registry.md` for the relevant category's feature
checklist FIRST, then assess the product against each item. Add any newly discovered
features back to the registry after completing this dimension.

**Core Capabilities**
- Primary function / product category
- Full list of core modules or feature areas (check against registry checklist)
- Key sub-features within each module

**Differentiators**
- What makes this product unique vs. competitors?
- Proprietary technology, algorithms, or approaches (AI-native, graph-based, etc.)
- Analyst recognition, awards, or community reputation

**Automation & Customization**
- Automation builder: rule-based / visual / AI-assisted
- Custom fields, custom views, custom templates
- Workflow engine depth (conditions, branching, loops)

**Reporting & Analytics**
- Built-in dashboards and charts
- Custom report builder
- Data export options (CSV, PDF, API)
- Embedded analytics or white-label BI

**Mobile**
- iOS app: yes/no
- Android app: yes/no
- Feature parity with web (full / partial / view-only)
- Offline mode: yes/no

**Tiers & Gating**
- Features available on free plan
- Features locked to paid tiers
- Features requiring Enterprise / highest tier
- Add-ons or separately licensed modules

**Notable Gaps**
- Features common in this category that are missing or underdeveloped (check registry's Notable Gaps section)
- Known limitations or highly-requested unshipped features
- Deprecated features

---

### 2. Use Cases

**Target Audience**
- Primary buyer persona (role, seniority, department)
- Secondary personas / stakeholders
- Ideal company size: individual / SMB / mid-market / enterprise
- Industry verticals with strong fit
- Industry verticals with poor fit or friction

**Top Workflows Solved**
- Workflow 1: name + brief description
- Workflow 2: name + brief description
- Workflow 3: name + brief description
- Workflow 4: name + brief description
- Workflow 5: name + brief description

**Deployment Patterns**
- Common deployment scenarios (standalone, embedded, incumbent replacement)
- Where it sits in a typical tech stack
- Typical daily-active team size
- Time-to-value estimate
- Adoption model: bottom-up PLG / top-down / sales-led

**Anti-Use-Cases**
- Explicitly what this product is NOT suitable for
- Common mismatches (purchased for X, struggles with Y)

**Role-Specific Use Cases**
- **Engineering / DevOps:** how developers use it day-to-day
- **Product Management:** key workflows for PMs
- **Marketing:** campaigns, content, attribution use cases
- **Sales / RevOps:** CRM, pipeline, reporting workflows
- **HR / People Ops:** hiring, onboarding, performance workflows
- **Finance / Legal:** compliance, contracts, reporting workflows
- **Executive / Leadership:** visibility, reporting, decision support
- *Note only roles where the product has documented or notable fit; mark others as "not a primary target"*

---

### 3. Login Methods

**Authentication Methods**
- Email/password: yes/no, password strength requirements
- Google OAuth: yes/no
- GitHub OAuth: yes/no
- Microsoft / Azure AD OAuth: yes/no
- Apple Sign-In: yes/no
- Magic link / passwordless: yes/no
- Other OAuth providers: list all

**SSO (Single Sign-On)**
- SAML 2.0: yes/no
- OIDC / OpenID Connect: yes/no
- Supported IdPs: Okta, Azure AD, Google Workspace, OneLogin, Ping Identity, JumpCloud, others
- SSO initiation: IdP-initiated / SP-initiated / both
- Just-in-time (JIT) provisioning: yes/no
- SSO plan gating: which tier unlocks SSO?

**Multi-Factor Authentication**
- TOTP authenticator apps (Google Authenticator, Authy): yes/no
- SMS OTP: yes/no
- Email OTP: yes/no
- Hardware security keys (FIDO2 / WebAuthn / YubiKey): yes/no
- Admin-enforced MFA for all users: yes/no
- MFA plan gating: free or paid tier?

**Directory Sync & Provisioning**
- SCIM 2.0: yes/no
- Auto-deprovisioning on IdP removal: yes/no
- Group sync from IdP: yes/no
- SCIM plan gating: which tier?

**Session & Access Controls**
- Session timeout: configurable? default duration?
- Concurrent session limits: yes/no
- IP allowlisting / blocklisting: yes/no
- Device trust / managed device enforcement: yes/no
- Admin-forced logout / session revocation: yes/no
- Audit logs for auth events: yes/no, retention period?

---

### 4. APIs

**API Availability & Type**
- REST API: yes/no
- GraphQL API: yes/no
- gRPC: yes/no
- WebSocket / real-time API: yes/no
- Official SDKs: list all languages (Python, Node.js, Ruby, Go, Java, PHP, .NET, etc.)
- CLI tool: yes/no

**Authentication & Authorization**
- API key auth: yes/no
- OAuth 2.0 authorization code flow: yes/no
- OAuth 2.0 client credentials (machine-to-machine): yes/no
- JWT / Bearer tokens: yes/no
- Token scopes / permission levels
- Token expiry and refresh token support

**Documentation Quality**
- OpenAPI / Swagger spec published: yes/no
- Interactive API explorer (Swagger UI, Redoc, Postman collection): yes/no
- Code examples per endpoint: yes/no, which languages?
- API changelog: yes/no
- Versioning strategy: URI / header versioning, deprecation policy
- Dedicated developer portal: yes/no

**Rate Limits & Quotas**
- Rate limit per plan: requests/second, /minute, /hour, /day
- Burst limit
- Quota scope: per API key / per workspace / per user
- Rate limit headers in responses: yes/no
- Behavior on limit breach: 429 / queued / hard block

**Endpoint Coverage**
- Full list of top-level resources exposed via API
- Read-only vs. full CRUD per resource
- Bulk / batch endpoints: yes/no
- Admin / management APIs separate from data APIs: yes/no
- Notable resources NOT available via API

**Webhooks**
- Webhooks available: yes/no
- Configurable event types: list key events
- Delivery guarantee: at-least-once / at-most-once / exactly-once
- Retry logic and failure handling
- Webhook signature / HMAC secret for verification: yes/no
- Webhook logs / delivery history in UI: yes/no

---

### 5. Data Ingestion

**File Import**
- Supported formats: CSV, JSON, XML, XLSX, TSV, Parquet, Avro, others
- Max file size per upload
- Max rows per import
- Import via UI: yes/no
- Import via API: yes/no
- Schema / template required for import: yes/no
- Error handling on malformed data: reject all / skip rows / show errors

**Native Connectors (built-in, no-code)**
- Databases: PostgreSQL, MySQL, MSSQL, MongoDB, others
- Cloud storage: S3, GCS, Azure Blob
- SaaS sources: Salesforce, HubSpot, Google Sheets, etc.
- Event streams: Kafka, Kinesis, Pub/Sub
- Data warehouses: Snowflake, BigQuery, Redshift, Databricks

**Streaming & Batch**
- Real-time / event-driven ingestion: yes/no
- Scheduled batch: yes/no, minimum frequency (hourly / daily / weekly)
- Change data capture (CDC): yes/no
- Micro-batch: yes/no

**ETL / Reverse ETL**
- Fivetran connector: yes/no
- Airbyte connector: yes/no
- dbt integration: yes/no
- Census: yes/no
- Hightouch: yes/no
- Other ETL/ELT platforms supported

**Limits & Quotas**
- Storage limits by plan
- Row / record caps by plan
- Data retention period
- Archival or tiering options

**Data Quality & Transformation**
- Schema validation on ingest: yes/no
- Data type enforcement: yes/no
- Deduplication: yes/no
- Field mapping / renaming on ingest: yes/no
- Computed columns or transforms on ingest: yes/no
- Data lineage tracking: yes/no

---

### 6. Integrations

**Native / First-Party Integrations**
- Full list of built-in integrations (no middleware required)
- Depth per integration: read-only sync / bidirectional / action triggers
- Configuration: UI-based or requires developer setup?

**Communication & Collaboration**
- Slack: yes/no — triggers and actions available
- Microsoft Teams: yes/no — triggers and actions available
- Email (Gmail, Outlook): yes/no
- Google Calendar: yes/no
- Outlook Calendar: yes/no
- Zoom: yes/no
- Google Meet: yes/no
- Webex: yes/no

**Productivity & Docs**
- Google Drive / Docs / Sheets: yes/no
- Microsoft OneDrive / Word / Excel: yes/no
- Notion: yes/no
- Confluence: yes/no
- Coda: yes/no

**CRM & Sales**
- Salesforce: yes/no
- HubSpot: yes/no
- Pipedrive: yes/no
- Zoho CRM: yes/no
- Other CRMs: list

**Dev & Engineering Tools**
- GitHub: yes/no
- GitLab: yes/no
- Jira: yes/no
- Linear: yes/no
- Shortcut: yes/no
- PagerDuty: yes/no
- OpsGenie: yes/no
- CI/CD (Jenkins, CircleCI, GitHub Actions): yes/no

**Data & Analytics**
- Snowflake: yes/no
- BigQuery: yes/no
- Redshift: yes/no
- Databricks: yes/no
- Tableau: yes/no
- Looker: yes/no
- Power BI: yes/no
- Metabase: yes/no
- Google Analytics: yes/no
- Amplitude: yes/no
- Mixpanel: yes/no

**iPaaS & Automation Platforms**
- Zapier: yes/no — number of triggers / actions
- Make (Integromat): yes/no
- n8n: yes/no
- Workato: yes/no
- Tray.io: yes/no
- Power Automate: yes/no

**Enterprise Middleware**
- MuleSoft: yes/no
- Boomi: yes/no
- Informatica: yes/no
- Other enterprise iPaaS: list

**Marketplace / Ecosystem**
- App store or integration marketplace: yes/no
- Approximate number of apps / partners
- Third-party developers can build integrations: yes/no
- Partner certification program: yes/no

**Notable Gaps**
- Integrations expected for this category that are missing
- Integrations listed as roadmap / coming soon
- Integrations that require workarounds (API-only, no native UI)

---

### 7. Competitive Positioning

**Direct Competitors**
- List the 3–5 most direct competitors (same category, same buyer)
- For each: name, one-line positioning, key differentiator vs. this product

**Why Choose This Product**
- Top 3–5 reasons a buyer should pick this product over competitors
- Unique strengths not replicated elsewhere
- Scenarios / buyer profiles where this product clearly wins

**Why NOT Choose This Product**
- Honest scenarios where a competitor is a better fit
- Weaknesses relative to named competitors
- Common objections raised by buyers / prospects

**Comparison Articles & Resources**
- Actively search for "[Product] vs [Competitor]" articles from G2, Gartner Peer Insights, Capterra, analyst blogs, and tier-1 tech media (TechCrunch, Wired, InfoQ, The New Stack, etc.)
- For each article found: source name, publication date, URL, and a 1–2 sentence verdict summary
- Note which competitor pairings appear most frequently (signals where buyers are evaluating alternatives)
- Flag any articles that are clearly vendor-sponsored vs. independent
- Minimum: find and summarize 3 independent comparison articles; note if fewer exist

---

### 8. Analyst & Review Rankings

**G2**
- Overall star rating (out of 5) and number of reviews
- Category rank (e.g., "#1 in Project Management")
- Notable badges earned (Leader, High Performer, Momentum Leader, etc.)
- Top praised aspects from reviews
- Top criticisms from reviews
- Source link / date of data

**Gartner**
- Gartner Peer Insights rating and number of reviews
- Magic Quadrant position if applicable (Leader / Challenger / Visionary / Niche Player)
- Which Magic Quadrant report(s) — year and category
- Critical Capabilities score if published
- Source link / date of data

**Other Review Platforms**
- Capterra: rating, number of reviews, notable badges
- TrustRadius: rating, TrScore, notable badges
- Product Hunt: upvotes, ranking, launch date
- Forrester Wave position if applicable
- IDC MarketScape position if applicable
- Any other analyst recognition or awards

**Notable Mentions & Press**
- Tier-1 media coverage (TechCrunch, Forbes, Wired, etc.)
- Industry analyst blog mentions
- Awards (e.g., "Best of Breed 2024", "Top 10 HR Tools")
- Conference keynotes or speaking appearances as social proof

---

### 9. Open Source Health (GitHub & Docker)

*Skip this section entirely if the product is fully proprietary with no public repo.*

**GitHub Repository**
- Repository URL
- Stars: count + trend (growing / flat / declining)
- Forks: count
- Open Issues: count (and ratio to closed — indicates backlog health)
- Open Pull Requests: count
- Contributors: total count, active in last 90 days
- Latest release: version + date
- Release cadence: frequency of releases
- License: MIT / Apache 2.0 / GPL / BSL / proprietary / other
- Notable: any recent controversies (e.g., license changes, governance issues)

**Docker Hub / Container Registry**
- Official image available: yes/no
- Docker Hub pulls: count (or estimate range)
- Image variants: (e.g., slim, alpine, GPU, arm64)
- Last updated: date
- Verified publisher: yes/no
- Alternative registries: GHCR, Quay.io, etc.

**Community & Ecosystem Health**
- Slack / Discord community: member count
- Forum or Discourse: active threads per month (estimate)
- Stack Overflow tag: question count, answered %
- Plugin / extension ecosystem size

---

### 10. Funding & Backing

**Funding History**
- Total funding raised
- Latest round: stage, amount, date
- Full funding rounds list (stage, amount, date, lead investors)
- Valuation at last round (if disclosed)

**Investors & Sponsors**
- Lead investors by round
- Notable angels or strategic investors
- Corporate sponsors (if open source)
- Accelerator programs (YC, a16z, etc.)

**Financial Status**
- Public / Private / Acquired / Merged
- If public: stock ticker, market cap
- If acquired: acquirer, date, reported price
- Revenue (if disclosed or estimated by analysts)
- Profitability status (if disclosed)

---

### 11. Notable Clients

**Named Reference Customers**
- List all publicly named customers (from case studies, website, press releases)
- For each: company name, industry, use case (if disclosed)

**Customer Tiers**
- Enterprise logos featured on website
- SMB / mid-market presence (estimate from review platform data)
- Industry verticals with highest customer density

**Case Studies**
- Titles of published case studies + key outcomes/metrics cited
- Link or source for each

---

### 12. Growth Signals

**Company Growth**
- Headcount: current estimate (LinkedIn, Glassdoor, Crunchbase)
- Headcount growth rate (YoY % if available)
- Job postings trend: growing / stable / shrinking (indicator of investment areas)
- Key hiring areas (e.g., heavy on AI engineers = roadmap signal)

**Product Growth**
- User / seat count: disclosed or estimated
- Customer count: disclosed or estimated
- ARR / MRR: disclosed or estimated by analysts
- YoY growth rate: disclosed or estimated
- Geographic expansion signals

**Web & SEO Signals**
- Similarweb / Semrush traffic trend (growing / flat / declining)
- Alexa / global rank estimate
- Domain authority
- Organic keyword count trend

**App Store & Download Signals**
- iOS App Store rating + number of ratings
- Google Play rating + number of ratings
- Download trend (if available)

---

### 13. Customer References

**Direct Reference Availability**
- Does the vendor offer a customer reference program: yes/no/unknown
- Reference call availability: yes/no/contact sales required
- Peer reference marketplaces listed on (e.g., ReferenceEdge, Influitive)

**Testimonials**
- Named executive quotes (CEO, CTO, VP) from press releases or case studies
- Key metric-backed testimonials (e.g., "reduced onboarding time by 40%")

**Awards & Recognition from Customers**
- Customer-nominated awards
- NPS score (if disclosed)
- CSAT or CES scores (if disclosed)
- Customer retention / churn rate (if disclosed)

---

### 14. Community Sentiment

**Reddit**
- Relevant subreddits: list (e.g., r/projectmanagement, r/devops)
- Overall sentiment: positive / mixed / negative
- Most common praise themes from threads
- Most common complaints from threads
- Notable viral threads or controversies
- Approximate monthly mentions (if estimable)

**Hacker News**
- Sentiment on HN: positive / mixed / negative
- Notable Show HN posts or discussions
- Key criticisms or praise points

**Twitter / X & LinkedIn**
- Brand sentiment (positive / mixed / negative)
- Influencer or thought-leader endorsements
- Notable controversies or viral moments

**Developer Communities**
- Dev.to, Hashnode, Medium mentions
- YouTube tutorials / review videos: count + quality assessment
- Podcast mentions

**Support & Response Quality**
- Responsiveness to public issues on GitHub
- Response to negative G2 / Capterra reviews: yes/no / quality
- Community team presence in forums/Discord

---

### 15. Pricing & Total Cost of Ownership

> ⚙️ **Delegated to `saas-cost-analyzer` skill — do NOT calculate pricing yourself.**

This dimension is fully handled by the `saas-cost-analyzer` skill. Follow these steps exactly:

**Step 1 — Collect inputs before delegating**

Before invoking the cost analyzer, gather the following from the user (or infer from context if already provided):
- Number of users / seats
- Expected usage (API calls, storage, transactions, environments — as relevant)
- Contract duration preference (monthly / annual / multi-year)
- Expected growth rate over contract period
- Any governance or compliance constraints (HIPAA, GDPR, FedRAMP, SOC 2, etc.)
- Whether they are an AWS or GCP customer (for marketplace pricing)
- Any known negotiated discounts or existing quotes

If any required inputs are missing, **ask the user before proceeding** — do not guess or assume values silently.

**Step 2 — Invoke the saas-cost-analyzer skill**

Read `/mnt/skills/user/saas-cost-analyzer/SKILL.md` and follow its full methodology for the product(s) being profiled. Pass all inputs collected in Step 1.

The cost analyzer will produce:
- Cost Breakdown Table (per tool)
- Scenario Comparison Table (Small / Medium / Large scale)
- Hidden Cost & Risk Summary
- Assumptions Log
- Executive Summary
- Final Recommendation & Order of Preference (for comparisons)
- Marketplace pricing check (AWS + GCP)
- Open source / self-hosting cost model (if applicable)

**Step 3 — Embed the output**

Place the full saas-cost-analyzer output under this dimension heading in the report. Do not summarise or truncate it — include everything the cost analyzer produces.

**Step 4 — Cross-link to other dimensions**

After the pricing output, add a brief cross-reference note if relevant findings elsewhere in the report affect cost interpretation. For example:
- "See Dim 21 (Vendor Risk) — high lock-in risk increases effective switching cost"
- "See Dim 17 (Support & SLA) — enterprise support tier adds ~$X/month not included above"
- "See Dim 22 (Implementation) — professional services cost estimated at $X-$Y"

**What NOT to do:**
- Do not estimate, approximate, or calculate any pricing figures yourself
- Do not skip this dimension because pricing is not publicly listed — the cost analyzer handles opaque pricing by using competitor benchmarks and review data
- Do not produce a simplified price table as a substitute for the full cost analyzer output

---

### 16. Security & Compliance

**Certifications & Standards**
- SOC 2 Type I: yes/no / in progress
- SOC 2 Type II: yes/no / audit date / report available on request?
- ISO 27001: yes/no
- ISO 27017 / 27018 (cloud security): yes/no
- PCI DSS: yes/no / level
- HIPAA compliant: yes/no / BAA available?
- FedRAMP: yes/no / authorization level
- GDPR compliant: yes/no / DPA available?
- CCPA compliant: yes/no
- Other regional frameworks (DPDP India, PIPEDA Canada, LGPD Brazil, etc.)

**Data Residency & Sovereignty**
- Data residency options: US / EU / APAC / other regions
- Data stored in which cloud provider(s) and regions
- Customer-managed encryption keys (CMEK / BYOK): yes/no / which tier?
- Data processing agreements (DPA) available: yes/no

**Infrastructure Security**
- Cloud provider(s): AWS / GCP / Azure / multi-cloud / on-prem option
- Encryption at rest: yes/no, algorithm (AES-256, etc.)
- Encryption in transit: yes/no (TLS version)
- Network isolation / VPC peering / private link: yes/no
- Penetration testing: yes/no, frequency, last test date (if public)
- Bug bounty program: yes/no, platform (HackerOne, Bugcrowd, etc.)

**Access & Audit**
- Audit logs: yes/no, retention period, exportable?
- Role-based access control (RBAC): yes/no, granularity
- Attribute-based access control (ABAC): yes/no
- Admin console for security settings: yes/no
- Data loss prevention (DLP) features: yes/no

**Vulnerability & Incident Management**
- Public security page / trust center: yes/no, URL
- SLA for vulnerability disclosure and patching
- Historical security incidents: any publicly disclosed breaches?
- Status page for uptime / incidents: yes/no, URL

---

### 17. Support & SLA

**Support Channels**
- Email / ticket support: yes/no, which plans?
- Live chat: yes/no, hours, which plans?
- Phone support: yes/no, which plans?
- Dedicated CSM (Customer Success Manager): yes/no, which tier?
- Slack / Teams shared channel with vendor: yes/no, which tier?
- In-app support widget: yes/no

**Response Time SLAs**
- Response time by severity level (P1 / P2 / P3) per plan
- Resolution time targets (if published)
- Support hours: 24/7 / business hours / follow-the-sun
- SLA credits / penalties for missed targets: yes/no

**Self-Service Resources**
- Documentation / knowledge base: yes/no, quality assessment
- Video tutorials / learning library: yes/no
- Community forum: yes/no, activity level
- Certifications or training programs: yes/no
- Sandbox / test environment available: yes/no

**Onboarding**
- Guided onboarding: yes/no, assisted or self-serve?
- Dedicated implementation support: yes/no, which tier?
- Professional services / consulting arm: yes/no
- Typical time-to-production estimate
- Partner / SI ecosystem for implementation: yes/no

**Uptime & Reliability**
- Published SLA uptime guarantee: % (e.g., 99.9%)
- Historical uptime (from status page, if available)
- Planned maintenance window policy
- Disaster recovery / RTO / RPO targets (if published)

---

### 18. Roadmap & Vision

**Public Roadmap**
- Public roadmap available: yes/no, URL
- Format: Trello board / GitHub issues / dedicated page / changelog only
- How far ahead is the roadmap published (3 months / 6 months / 1 year)?
- Customer voting on roadmap items: yes/no

**Recent Release Cadence**
- Release frequency: continuous / weekly / monthly / quarterly
- Last 3 major releases: version, date, headline features
- Changelog publicly available: yes/no, URL
- Breaking changes / deprecation policy documented: yes/no

**Strategic Direction**
- Stated company vision / mission (from CEO, investor decks, or press)
- Key investment areas signaled by recent hires, blog posts, or releases
- AI / ML strategy: is AI being embedded, and where?
- Platform vs. point solution trajectory
- M&A activity: any recent acquisitions or being acquired?

**Community & Ecosystem Investment**
- Open source contributions or open-core strategy evolving?
- Developer program / partner program investment signals
- Conference presence (sponsor, speaker) as strategic signal
- Recent pivots or major strategic shifts

---

### 19. AI & ML Capabilities

*In 2026, AI features are a primary procurement criterion. Cover this dimension exhaustively regardless of whether the vendor markets itself as an "AI product".*

**AI Feature Inventory**
- Full list of AI/ML-powered features in the product
- Which features are AI-native vs. AI-augmented (bolted on)
- Model types used: Generative (LLM), Predictive (ML), Agentic (autonomous), or hybrid
- Named AI models / providers powering features (OpenAI, Anthropic, Gemini, proprietary, etc.)
- Option to bring your own model (BYOM) or choose preferred model: yes/no

**AI Governance & Transparency**
- Does vendor publish an AI usage / data training policy: yes/no
- Is customer data used to train vendor models: yes/no / opt-out available?
- AI outputs auditable / explainable: yes/no
- Human-in-the-loop controls available: yes/no
- EU AI Act compliance posture (if selling in EU): documented / in progress / not addressed
- AI incident disclosure policy: yes/no

**AI Pricing**
- AI features included in base plan: yes/no
- AI credits / token-based consumption model: yes/no, cost per unit
- AI features gated to higher tiers: which ones, which tiers?
- Usage caps on AI per plan

**AI Roadmap Signals**
- Recent AI feature launches (last 6 months)
- Stated AI investment / hiring signals
- Agentic or autonomous workflow capabilities: current or announced
- AI differentiators vs. competitors in same category

---

### 20. Data Privacy & Portability

**Data Ownership**
- Customer data ownership explicitly stated in ToS: yes/no
- Can vendor use customer data for product improvement: yes/no / opt-out?
- Sub-processors list publicly available: yes/no, URL
- Right to audit vendor's data practices: yes/no

**Data Portability**
- Export all data: yes/no, formats available (CSV, JSON, XML, SQL dump, etc.)
- Bulk export via UI: yes/no
- Bulk export via API: yes/no
- Export includes all metadata, history, attachments: yes/no / partial
- Self-service export vs. must request from vendor

**Data Deletion & Retention**
- Customer-initiated data deletion: yes/no, SLA for completion
- Data deletion on contract termination: yes/no, timeline
- Deletion confirmation / certificate: yes/no
- Backup data retention after deletion request: how long?
- Data retention policies configurable per plan: yes/no

**Right to Be Forgotten & Privacy Rights**
- GDPR data subject access requests (DSAR) workflow: yes/no
- CCPA opt-out mechanism: yes/no
- Consent management features built-in: yes/no
- Privacy by design principles documented: yes/no

---

### 21. Vendor Risk & Lock-in

**Switching Cost Assessment**
- Difficulty of data export (from Dim 20): low / medium / high
- API availability for migration: yes/no
- Migration tools or scripts provided: yes/no
- Known customer complaints about switching difficulty (from reviews)

**Contractual Lock-in Risks**
- Minimum contract length: month-to-month / annual / multi-year required?
- Auto-renewal clauses: yes/no, notice period required to cancel
- Price increase terms: capped / uncapped / at vendor discretion
- Early termination fees: yes/no, terms
- Data held hostage risk: can you get your data if you stop paying?

**Vendor Stability Risk**
- Risk of acquisition: any rumors or signals?
- Risk of shutdown: runway / funding status / profitability
- License change risk: open-source products — any history of license changes (e.g., AGPL → BSL, open → proprietary)?
- Dependency concentration: does the vendor rely on a single cloud, model provider, or key partner that creates upstream risk?

**Business Continuity**
- Escrow arrangements available (source code escrow): yes/no
- SLA for data access during vendor bankruptcy / wind-down
- Historical incidents of service discontinuation or product sunsetting

---

### 22. Implementation & Migration

**Implementation Complexity**
- Self-serve setup (no implementation needed): yes/no
- Typical implementation timeline by company size (SMB / mid-market / enterprise)
- Complexity drivers: data migration, integrations, custom config, training
- Certified implementation partners available: yes/no, how many globally

**Migration Support**
- Data migration from competitor products: which sources are supported?
- Migration tools built into product: yes/no
- Vendor-assisted migration: yes/no, cost, which tier?
- Migration documentation / playbooks publicly available: yes/no

**Change Management**
- Admin training included: yes/no, format (video / live / docs)
- End-user training resources: yes/no
- Change management templates or guides: yes/no
- Sandbox / staging environment for testing before production: yes/no

**Go-live & Hypercare**
- Dedicated launch support: yes/no, which tier?
- Hypercare period post-launch: duration, what's included
- Success metrics / onboarding KPIs tracked by vendor: yes/no
- Escalation path during implementation: defined / ad hoc

---

### 23. Accessibility & Internationalization

**Accessibility**
- WCAG 2.1 / 2.2 compliance level: A / AA / AAA / not documented
- Screen reader support: yes/no (tested with NVDA, JAWS, VoiceOver)
- Keyboard navigation fully supported: yes/no
- Accessibility conformance report (VPAT) available: yes/no
- Known accessibility gaps documented: yes/no

**Language & Localization**
- UI available in how many languages: list all
- RTL (right-to-left) language support: yes/no (Arabic, Hebrew, Farsi)
- Content / data localization (dates, numbers, currencies): yes/no
- Customer support available in which languages

**Regional & Compliance Availability**
- Available in which countries / regions
- Blocked or restricted in any jurisdictions
- Local data residency options (EU, India, Australia, etc.)
- Local billing currency options
- VAT / GST / tax handling: automatic / manual / not included

---

## Output Templates

### Full Profile

```
# [Product Name] — SaaS Profile
*Sources: [list all sources]*

## Overview
- **Category:** [product type]
- **Positioning:** [how the company describes itself]
- **Founded / HQ:** [year, location]
- **Pricing model:** [freemium / per-seat / usage-based / flat fee]

---

## 1. Features

**Core Capabilities**
- [...]

**Differentiators**
- [...]

**Automation & Customization**
- [...]

**Reporting & Analytics**
- [...]

**Mobile**
- [...]

**Tiers & Gating**
- [...]

**Notable Gaps**
- [...]

---

## 2. Use Cases

**Target Audience**
- [...]

**Top Workflows Solved**
- [...]

**Deployment Patterns**
- [...]

**Anti-Use-Cases**
- [...]

**Role-Specific Use Cases**
- [...]

---

## 3. Login Methods

**Authentication Methods**
- [...]

**SSO**
- [...]

**MFA**
- [...]

**Provisioning**
- [...]

**Session & Access Controls**
- [...]

---

## 4. APIs

**API Type & SDKs**
- [...]

**Authentication**
- [...]

**Documentation**
- [...]

**Rate Limits**
- [...]

**Endpoint Coverage**
- [...]

**Webhooks**
- [...]

---

## 5. Data Ingestion

**File Import**
- [...]

**Native Connectors**
- [...]

**Streaming & Batch**
- [...]

**ETL / Reverse ETL**
- [...]

**Limits & Quotas**
- [...]

**Data Quality**
- [...]

---

## 6. Integrations

**Native**
- [...]

**Communication**
- [...]

**Productivity**
- [...]

**CRM / Sales**
- [...]

**Dev Tools**
- [...]

**Data & Analytics**
- [...]

**iPaaS**
- [...]

**Enterprise Middleware**
- [...]

**Marketplace**
- [...]

**Notable Gaps**
- [...]

---

## 7. Pricing & Total Cost of Ownership

> ⚙️ *Output from `saas-cost-analyzer` skill — embedded in full here.*

[Full saas-cost-analyzer output: Cost Breakdown, Scenario Table, Hidden Costs, Assumptions Log, Executive Summary, Recommendation]
[Cross-references to Dim 21 (Vendor Risk), Dim 17 (Support), Dim 22 (Implementation) where relevant]

---

## 8. Security & Compliance

**Certifications & Standards** - [...]
**Data Residency & Sovereignty** - [...]
**Infrastructure Security** - [...]
**Access & Audit** - [...]
**Vulnerability & Incident Management** - [...]

---

## 9. Support & SLA

**Support Channels** - [...]
**Response Time SLAs** - [...]
**Self-Service Resources** - [...]
**Onboarding** - [...]
**Uptime & Reliability** - [...]

---

## 10. Roadmap & Vision

**Public Roadmap** - [...]
**Recent Release Cadence** - [...]
**Strategic Direction** - [...]
**Community & Ecosystem Investment** - [...]

---

## 11. Competitive Positioning

**Direct Competitors** - [...]
**Why Choose This Product** - [...]
**Why NOT Choose This Product** - [...]
**Comparison Articles** - [...]

---

## 12. Analyst & Review Rankings

**G2** - [...]
**Gartner** - [...]
**Other Platforms & Notable Mentions** - [...]

---

## 13. Open Source Health

**GitHub** - [...]
**Docker** - [...]
**Community & Ecosystem** - [...]

---

## 14. Funding & Backing

**Funding History** - [...]
**Investors & Sponsors** - [...]
**Financial Status** - [...]

---

## 15. Notable Clients

**Named Customers** - [...]
**Customer Tiers** - [...]
**Case Studies** - [...]

---

## 16. Growth Signals

**Company Growth** - [...]
**Product Growth** - [...]
**Web & App Signals** - [...]

---

## 17. Customer References

**Reference Program** - [...]
**Testimonials** - [...]
**NPS / CSAT** - [...]

---

## 18. Community Sentiment

**Reddit** - [...]
**Hacker News** - [...]
**Twitter / X & LinkedIn** - [...]
**Developer Communities** - [...]
**Support & Response Quality** - [...]

---

## 19. AI & ML Capabilities

**AI Feature Inventory** - [...]
**AI Governance & Transparency** - [...]
**AI Pricing** - [...]
**AI Roadmap Signals** - [...]

---

## 20. Data Privacy & Portability

**Data Ownership** - [...]
**Data Portability** - [...]
**Data Deletion & Retention** - [...]
**Privacy Rights** - [...]

---

## 21. Vendor Risk & Lock-in

**Switching Cost Assessment** - [...]
**Contractual Lock-in Risks** - [...]
**Vendor Stability Risk** - [...]
**Business Continuity** - [...]

---

## 22. Implementation & Migration

**Implementation Complexity** - [...]
**Migration Support** - [...]
**Change Management** - [...]
**Go-live & Hypercare** - [...]

---

## 23. Accessibility & Internationalization

**Accessibility** - [...]
**Language & Localization** - [...]
**Regional Availability** - [...]

---

## Evaluator's Summary
- **Strength:** [key differentiator]
- **Watch-out:** [key limitation or risk]
- **Best for:** [specific buyer profile]
- **Avoid if:** [specific disqualifying condition]
- **Market position:** [leader / challenger / niche / emerging]
- **Momentum:** [accelerating / stable / declining — based on growth signals + community]
- **Security posture:** [strong / adequate / weak — based on certifications + incidents]
- **Vendor risk:** [low / medium / high — based on lock-in, stability, funding]
- **AI readiness:** [leading / keeping pace / lagging — vs. category peers]
```

---

### Dimension Spotlight

```
## [Product Name] — [Dimension Name]

[All sub-sections for this dimension, each as bullet points]

*Sources: [list sources]*
```

---

### Side-by-Side Comparison

```
# [Product A] vs [Product B] — Comparison
*Sources: [list sources]*

| Dimension | [Product A] | [Product B] |
|---|---|---|
| Features | [summary] | [summary] |
| Use Cases | [summary] | [summary] |
| Login Methods | [summary] | [summary] |
| APIs | [summary] | [summary] |
| Data Ingestion | [summary] | [summary] |
| Integrations | [summary] | [summary] |
| Pricing | [summary] | [summary] |
| Security & Compliance | [summary] | [summary] |
| Support & SLA | [summary] | [summary] |
| Roadmap & Vision | [summary] | [summary] |
| Competitive Positioning | [summary] | [summary] |
| Analyst Rankings | [summary] | [summary] |
| Open Source Health | [summary] | [summary] |
| Funding & Backing | [summary] | [summary] |
| Notable Clients | [summary] | [summary] |
| Growth Signals | [summary] | [summary] |
| Customer References | [summary] | [summary] |
| Community Sentiment | [summary] | [summary] |
| AI & ML Capabilities | [summary] | [summary] |
| Data Privacy & Portability | [summary] | [summary] |
| Vendor Risk & Lock-in | [summary] | [summary] |
| Implementation & Migration | [summary] | [summary] |
| Accessibility & i18n | [summary] | [summary] |

## Bottom Line
- **[Product A]:** Best for [X]. Watch out for [Y]. Momentum: [Z].
- **[Product B]:** Best for [X]. Watch out for [Y]. Momentum: [Z].
- **Verdict:** [Which to choose and why, in 2–3 sentences]
```

---

## Handling Uncertainty

- If any sub-point can't be verified via web search: *"Not publicly documented — confirm with vendor."*
- Never fabricate specific values (rate limits, file size caps, named integrations). Mark estimates as *"likely"* or *"unconfirmed"*.
- For niche or new products, flag limited coverage upfront and note which sections need vendor verification.
- Do not skip or collapse sub-points due to lack of info — absence of info is itself informative.
- **If user-provided research resolves a gap** — use it and mark it as resolved: *"Confirmed via [source]"* rather than leaving it as unverified.
- **If user-provided research conflicts with public sources** — surface the conflict, state both data points, and recommend the user verify with the vendor rather than picking one silently.
- **Never downgrade user-provided first-hand findings** (e.g. demo experience, internal test results) just because they aren't publicly corroborated — label them clearly and include them.

---

## Behavior Notes

- **Be exhaustive without exception.** Every sub-point in every dimension must be addressed.
- **Never summarize away detail.** More specifics are always better than vaguer summaries.
- **Always include the full Evaluator's Summary** on Full Profiles.
- **On comparison requests**, ask "Full profiles for each, or just the table?" if unclear.
- **When info is from user notes**, acknowledge gaps and research further to fill them.
- **For dimensions 7–23** (all non-core dims), always use web search to pull live data — these change frequently and should never rely on training knowledge alone.
- **Section 13 (Open Source Health)** should be skipped with a note if the product is fully proprietary with no public repo.
- **Section 15 (Pricing)** — always delegated to the `saas-cost-analyzer` skill. Read `/mnt/skills/user/saas-cost-analyzer/SKILL.md` and follow its full methodology. Never calculate pricing yourself.
- **Section 19 (AI & ML)** — always research current AI features; this changes monthly for most products.
- **Section 21 (Vendor Risk)** — pay special attention to open-source license history and any recent acquisitions.
- **For growth signals**, clearly distinguish between disclosed figures and analyst estimates. Label estimates as *(estimated)*.
- **For community sentiment**, synthesize tone — don't just list sources. Give an actionable read: e.g., "Developers love the API flexibility but consistently flag poor documentation as a blocker."
- **For comparison articles**, prefer independent sources over vendor-sponsored content. Always note when a source has a commercial relationship with the product.

---

## Webhook: Report Submission

After every Full Profile or Side-by-Side Comparison is delivered, Claude must follow this confirmation and submission flow.

### Step 1 — Ask for Consent

Once the report is fully displayed, always ask for explicit informed consent before doing anything with the webhook. Show this message word-for-word:

> "Before I submit this report to your external portal, I want to let you know what will be sent:
>
> - The **full research report** (all dimensions, all findings)
> - The **Evaluator's Summary** (conclusions, recommendations, risk ratings)
> - **Product name**, report type, and dimensions covered
> - **All sources and URLs** used during research
> - A **timestamp** of when this report was generated
>
> This data will be sent via POST request to the configured webhook endpoint. It will not be shared with any other party.
>
> Do you consent to submitting this report? Reply **yes** to submit, or **no** to skip."

**Consent rules — strictly enforced:**
- Never fire the webhook without this explicit consent step, even if the user previously said "always submit" or "auto-submit"
- Consent is per-report — ask fresh every time, even in the same conversation
- Only the words "yes", "submit", "send it", "go ahead", "confirm", or clear equivalents count as consent
- If the user says "maybe", "later", or is ambiguous — treat it as **no** and skip
- If the user says "no" or "skip" — acknowledge and move on without submitting
- Never guilt, nudge, or re-ask after a "no"
- Never describe what will be sent in vague terms — always show the full list above so consent is genuinely informed

---

### Step 2 — Read Config

Before submitting, retrieve the webhook settings from this skill's config:

- `WEBHOOK_URL` — the endpoint to POST to
- `WEBHOOK_SECRET` — optional secret for request signing

If `WEBHOOK_URL` is empty or missing, tell the user:

> "No webhook URL is configured. To enable report submission, open the skill's SKILL.md and set `WEBHOOK_URL` in the config block at the top of the file."

Do not attempt to fire the webhook and do not ask the user to provide a URL inline.

---

### Step 3 — Build the Payload

Construct a JSON payload with the following structure:

```json
{
  "event": "saas_report_generated",
  "timestamp": "<ISO 8601 UTC timestamp>",
  "product": "<product name(s) profiled>",
  "report_type": "<full_profile | comparison | dimension_spotlight>",
  "dimensions_covered": ["<list of dimension names included>"],
  "summary": {
    "strength": "<from Evaluator's Summary>",
    "watch_out": "<from Evaluator's Summary>",
    "best_for": "<from Evaluator's Summary>",
    "avoid_if": "<from Evaluator's Summary>",
    "market_position": "<from Evaluator's Summary>",
    "momentum": "<from Evaluator's Summary>",
    "security_posture": "<from Evaluator's Summary>",
    "vendor_risk": "<from Evaluator's Summary>",
    "ai_readiness": "<from Evaluator's Summary>"
  },
  "full_report": "<the complete report text as a single string, preserving all sections>",
  "sources": ["<list of all URLs and sources used>"],
  "user_confirmed": true
}
```

**Rules:**
- `full_report` must contain the entire generated report — all dimensions, all sub-points — not a truncated version
- `dimensions_covered` lists only dimensions that were actually researched and included
- `sources` lists every URL fetched or search result cited during research
- All string values must be properly JSON-escaped

---

### Step 4 — Sign the Request (if WEBHOOK_SECRET is set)

If `WEBHOOK_SECRET` is non-empty, generate an HMAC-SHA256 signature:

```
signature = HMAC-SHA256(key=WEBHOOK_SECRET, message=<raw JSON payload string>)
```

Include it as a request header:
```
X-Webhook-Signature: sha256=<hex digest>
```

If `WEBHOOK_SECRET` is empty, omit the signature header entirely.

---

### Step 5 — POST the Payload

Send the payload to `WEBHOOK_URL`:

```
POST <WEBHOOK_URL>
Content-Type: application/json
X-Webhook-Signature: sha256=<hex digest>   (only if secret is set)

<JSON payload>
```

**Use `bash_tool` with curl** to fire the request:

```bash
curl -s -o /tmp/webhook_response.txt -w "%{http_code}" \
  -X POST "<WEBHOOK_URL>" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=<signature>" \  # omit if no secret
  -d '<escaped JSON payload>'
```

Capture both the HTTP status code and response body.

---

### Step 6 — Report Back to User

**On success (HTTP 2xx):**
> "✅ Report submitted successfully to your portal."

**On client error (HTTP 4xx):**
> "⚠️ Submission failed — the portal returned [status code]. This usually means the webhook URL is incorrect or the request format was rejected. Check your WEBHOOK_URL config and portal settings."

**On server error (HTTP 5xx):**
> "⚠️ Submission failed — the portal returned a server error ([status code]). The endpoint may be temporarily unavailable. You can try again by saying 'resubmit'."

**On network/connection error:**
> "⚠️ Could not reach the webhook URL. Check that the URL is correct and the endpoint is reachable."

Never expose the full raw response body to the user unless they ask for debug info.

---

### Step 7 — Check In & Human Handoff

After Step 6 (whether submission succeeded, failed, or was skipped), always close with this message:

> "Is there anything else you'd like to dig into — a specific dimension, a competitor comparison, or a deeper cost breakdown?
>
> If you'd like to speak with a specialist — for vendor negotiation, implementation planning, or a bespoke procurement review — I can connect you with a human expert. Just say **'connect me'** and I'll arrange it."

**Handling follow-up responses:**

- If the user asks another question → answer it, then repeat the handoff offer at the end
- If the user says **"connect me"**, **"speak to someone"**, **"talk to a human"**, **"get help"**, or similar:
  > "I'll flag this for a human specialist now. Please share:
  > 1. Your name and organisation (optional but helpful)
  > 2. What you need help with (e.g. vendor negotiation, implementation, compliance review)
  > 3. Preferred contact method and timezone
  >
  > Someone will be in touch shortly."
  
  Then fire a separate **handoff webhook event** to `WEBHOOK_URL` with this payload:
  ```json
  {
    "event": "human_handoff_requested",
    "timestamp": "<ISO 8601 UTC>",
    "product": "<product(s) from the report>",
    "report_type": "<full_profile | comparison | dimension_spotlight>",
    "user_context": {
      "name": "<if provided>",
      "organisation": "<if provided>",
      "help_needed": "<what they described>",
      "contact_preference": "<if provided>",
      "timezone": "<if provided>"
    },
    "conversation_summary": "<2-3 sentence summary of what was researched and any key concerns raised>"
  }
  ```
  
  This handoff webhook fires **without requiring consent** — the user has explicitly requested human contact, which constitutes consent for this specific event.

- If the user says **"no"**, **"I'm done"**, **"that's all"** → respond warmly and close:
  > "Got it — good luck with your evaluation. Feel free to come back anytime."
  
  Do not re-ask or linger.

---

### Resubmit Command

If the user says "resubmit", "try again", or "resend", re-fire the same payload without rebuilding the report. Confirm with:
> "Resubmitting the last report to your portal..."

Then follow Steps 4–6 again.

---

### Privacy Note

The full report payload may contain commercially sensitive research. Always confirm before submitting:
- Never auto-submit without explicit user approval
- Never send to any URL other than the configured `WEBHOOK_URL`
- Never log or expose `WEBHOOK_SECRET` in any response to the user
