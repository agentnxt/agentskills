---
name: autonomyx-vocabulary
description: >
  Shared vocabulary, taxonomy, and category mapping reference used by all Autonomyx skills.
  Contains the authoritative Gartner Peer Insights to G2 category mapping table, covering 80+
  software markets. Use this skill whenever any Autonomyx skill needs to: resolve a software
  product's analyst category, fall back from Gartner to G2 category, look up equivalent category
  names across analyst platforms, or determine which platform's category label to use when a
  product is not found on Gartner Peer Insights. Also referenced for standardised feature status
  badges, evidence tier definitions, and confidence level labels shared across all Autonomyx skills.
---

# Autonomyx Vocabulary

Shared reference skill for all Autonomyx skills. Contains taxonomy mappings, status badges,
evidence tier definitions, and category resolution logic.

Read the relevant section for your use case:
- **Category resolution** → Section 1 (how to determine a product's category)
- **Gartner → G2 mapping** → Section 2 (the full mapping table)
- **Feature status badges** → Section 3
- **Evidence tiers** → Section 4
- **Confidence levels** → Section 5

---

## Section 1 — Category Resolution Logic

When any Autonomyx skill needs to determine a product's software category, follow this order:

### Step A — Try Gartner Peer Insights first
```
Search: "<App Name>" site:gartner.com/reviews
```
If a Gartner Peer Insights product page is found and accessible, extract the market/category
name directly from the page. Use the Gartner category name as the canonical label.

### Step B — Fall back to G2 if Gartner unavailable
If the product is not found on Gartner Peer Insights (no listing, paywalled, or category
not yet covered), look up the product on G2:
```
Search: "<App Name>" site:g2.com/products
```
Find the G2 category name on the product page. Then use Section 2 of this skill to map the
G2 category to its Gartner equivalent. If a mapping exists, use the Gartner name as the
canonical label but note: "Category: [Gartner label] (via G2 mapping — Gartner listing
not found)".

### Step C — Use G2 label directly if no mapping exists
If the G2 category does not appear in the mapping table in Section 2, use the G2 category
name directly as the working label. Note it as: "Category: [G2 label] (G2 only — no Gartner
mapping identified)".

### Step D — Infer from product description if neither source works
If neither Gartner nor G2 yields a category, infer the category from the product's website
and feature set. Label it: "Category: [Inferred label] (inferred — no analyst listing found)".

### Category label format for all outputs
Always display category as:
```
[Category Name] | Source: Gartner Peer Insights  ← preferred
[Category Name] | Source: G2 (mapped from Gartner)
[Category Name] | Source: G2 only
[Category Name] | Source: Inferred
```

---

## Section 2 — Gartner Peer Insights → G2 Category Mapping

Full bidirectional mapping table. Left column = Gartner Peer Insights market name.
Right column = closest G2 category equivalent.

When falling back to G2, find the G2 category in the right column and use the corresponding
Gartner name as the canonical label.

### CRM & Sales

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Sales Force Automation | CRM |
| CRM Customer Engagement Center | Customer Service Software |
| Sales Engagement Platforms | Sales Engagement |
| Configure, Price and Quote (CPQ) | CPQ Software |
| Revenue Intelligence | Revenue Operations & Intelligence (RO&I) |
| Digital Commerce Platforms | E-Commerce Platforms |
| Sales Performance Management | Sales Performance Management |
| Partner Relationship Management | Partner Management Software |
| Subscription Management | Subscription Management |
| Field Sales | Field Sales Software |

### Marketing

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| B2B Marketing Automation Platforms | Marketing Automation |
| Email Marketing | Email Marketing |
| Account-Based Marketing Platforms | Account-Based Marketing |
| Customer Data Platforms | Customer Data Platform (CDP) |
| Digital Marketing Analytics | Marketing Analytics |
| Multichannel Marketing Hubs | Multichannel Marketing Hub |
| Social Marketing Management | Social Media Management |
| Demand-Side Platforms | Demand-Side Platforms (DSP) |
| Content Marketing Platforms | Content Marketing |
| Personalization Engines | Personalization Software |
| Event Technology Platforms | Event Management Software |
| Conversational Marketing Platforms | Conversational Marketing |

### HR & Workforce

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Cloud HCM Suites for 1000+ Employee Enterprises | Core HR Software |
| Talent Acquisition Suites | Applicant Tracking Systems (ATS) |
| Talent Management Suites | Talent Management |
| Learning Management Systems (LMS) | Learning Management Systems (LMS) |
| Workforce Management | Workforce Management |
| Payroll | Payroll |
| Employee Engagement Platforms | Employee Engagement Software |
| Performance Management | Performance Management Systems |
| Compensation Management | Compensation Management |
| HR Service Delivery | HR Service Delivery Software |
| Skills Management Platforms | Skills Management Software |

### Finance & ERP

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Cloud Core Financial Management Suites | ERP Systems |
| Procure-to-Pay Suites | Procurement Software |
| Source-to-Pay Suites | Sourcing Software |
| Financial Planning & Analysis Platforms | Financial Planning & Analysis (FP&A) |
| Financial Consolidation & Close Solutions | Financial Close Software |
| Tax and Revenue Management Platforms | Tax Management Software |
| Accounts Payable Invoice Automation | Accounts Payable Automation |
| Contract Lifecycle Management | Contract Management |
| GRC Platforms | Governance, Risk & Compliance (GRC) |
| Audit Management | Audit Management Software |

### Analytics & Data

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Analytics and Business Intelligence Platforms | Business Intelligence Platforms |
| Augmented Analytics Platforms | Augmented Analytics |
| Data Science and Machine Learning Platforms | Data Science and Machine Learning Platforms |
| Cloud Database Management Systems | Database Management Systems |
| Data Integration Tools | Data Integration Tools |
| Master Data Management Solutions | Master Data Management (MDM) |
| Data Quality Solutions | Data Quality Software |
| Data Cataloging Tools | Data Catalog Software |
| Streaming Analytics | Streaming Analytics |
| Observability Platforms | IT Monitoring & Observability |
| Metadata Management Solutions | Data Governance Software |
| AIOps Platforms | AIOps Platforms |
| Embedded Analytics Platforms | Embedded Business Intelligence |

### IT Service Management & Operations

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| IT Service Management Tools | IT Service Management (ITSM) Tools |
| IT Asset Management Tools | IT Asset Management |
| DevOps Platforms | DevOps Platforms |
| Application Performance Monitoring | Application Performance Monitoring (APM) |
| IT Operations Management | IT Operations Management (ITOM) |
| Service Desk | Help Desk Software |
| Configuration Management Database | CMDB Software |
| Digital Employee Experience Management Tools | Digital Employee Experience (DEX) |
| Network Performance Monitoring and Diagnostics | Network Monitoring Software |
| Unified Endpoint Management Tools | Unified Endpoint Management (UEM) |

### Project & Work Management

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Project and Portfolio Management | Project Management |
| Collaborative Work Management | Collaborative Work Management |
| Enterprise Agile Planning Tools | Enterprise Agile Planning |
| No-Code/Low-Code Application Platforms | Low-Code Development Platforms |
| Work Management Platforms | Work Management |
| Resource Management | Resource Management |

### Security & Risk

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Endpoint Protection Platforms | Endpoint Protection |
| Security Information and Event Management | Security Information and Event Management (SIEM) |
| Identity and Access Management | Identity and Access Management (IAM) |
| Privileged Access Management | Privileged Access Management (PAM) |
| Zero Trust Network Access | Zero Trust Networking |
| Cloud Security Posture Management | Cloud Security |
| Extended Detection and Response | Extended Detection and Response (XDR) |
| Web Application and API Protection | Web Application Firewall (WAF) |
| Data Loss Prevention | Data Loss Prevention (DLP) |
| Vulnerability Assessment | Vulnerability Management |
| Security Orchestration, Automation and Response | Security Orchestration Automation Response (SOAR) |
| Identity Governance and Administration | Identity Governance and Administration (IGA) |
| Email Security | Email Security |
| Network Firewalls | Firewall Software |

### Customer Service & Success

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Customer Service Management | Customer Service Software |
| Field Service Management | Field Service Management |
| Customer Self-Service Technologies | Self-Service Software |
| Customer Success Management Platforms | Customer Success Software |
| Knowledge Management | Knowledge Management Systems |
| Contact Center Infrastructure | Contact Center Software |
| Workforce Engagement Management | Workforce Engagement Management |
| AI-Augmented Customer Service Platforms | AI Customer Service |

### Infrastructure & Cloud

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Cloud Infrastructure and Platform Services | Cloud Infrastructure |
| Container Management | Container Management Software |
| Backup and Recovery Solutions | Backup Software |
| Enterprise Content Management Platforms | Enterprise Content Management (ECM) |
| Hyperconverged Infrastructure | Hyperconverged Infrastructure |
| Database as a Service | Database as a Service (DBaaS) |
| API Management | API Management |
| Integration Platform as a Service | Integration Platform as a Service (iPaaS) |
| Application Integration Suites | Application Integration Software |
| Robotic Process Automation | Robotic Process Automation (RPA) |

### Collaboration & Productivity

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Meeting Solutions | Video Conferencing |
| Team Collaboration | Team Collaboration |
| Digital Signature | Electronic Signature |
| Enterprise File Sync and Share | Cloud Storage |
| Intranet Platforms | Intranet Software |
| Unified Communications as a Service | Unified Communications |

### Supply Chain & Operations

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Supply Chain Management Systems | Supply Chain Management |
| Transportation Management Systems | Transportation Management |
| Warehouse Management Systems | Warehouse Management |
| Supply Chain Planning Solutions | Supply Chain Planning |
| Manufacturing Execution Systems | Manufacturing Execution System (MES) |
| Demand Planning | Demand Planning Software |
| Inventory Management Systems | Inventory Management |

### Industry-Specific

| Gartner Peer Insights Market | G2 Category Equivalent |
|---|---|
| Electronic Health Records | Electronic Health Records (EHR) |
| Practice Management | Medical Practice Management |
| Property Management Systems | Property Management |
| Banking CRM | Financial Services CRM |
| Insurance Policy Administration Systems | Insurance Software |
| Learning Experience Platforms | Learning Experience Platforms (LXP) |
| Student Information Systems | Student Information Systems |

---

## Section 3 — Feature Status Badges

Standardised badges used across all Autonomyx skill outputs. Never use vague terms
("partial", "limited", "coming soon") without pairing with one of these badges.

| Badge | Label | Meaning |
|---|---|---|
| ✅ | GA | Generally Available — production-ready, broadly released |
| 🔶 | Beta | Publicly available but pre-GA; may have limitations or require opt-in |
| 🔷 | Early Access | Available to select customers only; not broadly released |
| 🚩 | Feature Flag | In the product but gated; must be enabled by vendor or admin |
| 🗓️ | Upcoming (Official) | Confirmed on public roadmap, changelog, or conference announcement |
| 💬 | Upcoming (Signal) | Unconfirmed; inferred from community votes, analyst hints, or keynote rumours |
| ❌ | Not Present | No evidence of feature existing or being planned |
| ❓ | Roadmap Unknown | Feature is absent; no public roadmap information found |

**Scoring impact of each status (for feature-gap-analyzer):**
- GA: Full credit per evidence quality
- Beta / Feature Flag: 50–70% of full GA score
- Early Access: 40–60% of full GA score
- Upcoming (Official, within 12 months): 30–40% of full GA score
- Upcoming (Official, 12+ months away): 10–20% of full GA score
- Upcoming (Signal only): 0% current score — noted as signal only
- Not Present / Roadmap Unknown: 0%

---

## Section 4 — Evidence Tiers

Standardised evidence quality tiers used for source labelling across all Autonomyx skills.

### Feature Existence Sources (the only sources that confirm a feature exists)

| Source | What it covers | Label format |
|---|---|---|
| **Official documentation** | docs site, feature pages, API reference, changelog, release notes | `[Docs: <URL> — <date>]` |
| **GitHub repository** | README, CHANGELOG, release tags, closed issues, wiki, feature flag files | `[GitHub: <repo URL> — <date>]` |

**Rule:** A feature badge of ✅ GA / 🔶 Beta / 🔷 Early Access / 🚩 Feature Flag may ONLY
be assigned if confirmed by one of these two sources. All other sources — including analyst
reports and G2 — cannot alone assert that a feature exists.

### Scoring Context Sources (inform quality and depth — never feature existence)

| Tier | Sources | Use for |
|---|---|---|
| Tier 1 | Gartner MQ / Market Guide / Peer Insights, Forrester Wave, IDC MarketScape | Scoring weight, positioning, capability depth assessments |
| Tier 2 | G2 verified grids, TrustRadius verified scoring, Capterra feature tables | Comparative satisfaction ratings, user sentiment |
| Tier 3 | Vendor marketing copy, community idea boards, LinkedIn, Reddit, conference presentations | Signal only — roadmap hints, sentiment; always label unconfirmed |

### Roadmap Sources (for 🗓️ Upcoming Official and 💬 Upcoming Signal only)

| Label | Sources |
|---|---|
| `[Roadmap: Official]` | Official roadmap page, changelog entry, conference announcement by vendor |
| `[Roadmap: Community signal]` | Idea boards, analyst roadmap references, keynote hints — unconfirmed |

**Label format for citations:**
- `[Docs: docs.vendor.com/ai-copilot — Mar 2026]`
- `[GitHub: github.com/vendor/repo/releases/v4.2 — Feb 2026]`
- `[Tier 1 | Gartner MQ 2025 | <vendor> | <date>]` — scoring context only
- `[Tier 2 | G2 feature grid | <vendor> | <date>]` — scoring context only
- `[Roadmap: Official | vendor.com/roadmap — Q2 2026]`
- `[Roadmap: Community signal | IdeaExchange — 980 votes — status: Planned]`

---

## Section 5 — Confidence Levels

Used in source/confidence footers across all Autonomyx skill outputs.

| Level | Criteria |
|---|---|
| **High** | Tier 1 data from 20+ reviews or a current (≤18 months) analyst report |
| **Medium** | Tier 1 data with fewer than 20 reviews, or Tier 2 official sources only |
| **Low** | Tier 3 sources only, or data older than 18 months |
| **N/A** | No data found; dimension cannot be scored |

---

## Maintenance Notes

This skill is the single source of truth for Autonomyx category mappings and taxonomy.
When a new Gartner market or G2 category is introduced, update Section 2 here first —
all other skills inherit from this reference.

Last reviewed: March 2026
Gartner markets covered: ~120 | G2 categories mapped: ~120
Source: gartner.com/reviews/markets + g2.com/categories
