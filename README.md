# Autonomyx Skills

A suite of Claude skills for enterprise SaaS evaluation, feature gap analysis, and vendor comparison.

## Skills

### `feature-gap-analyzer`
Performs a comprehensive feature gap analysis between two or more enterprise software applications.
- Sources features exclusively from official docs and GitHub repos
- Uses Gartner Peer Insights, G2, and analyst PDFs for scoring context
- Outputs: scored feature matrix (0–100%), side-by-side presence table, narrative gap report
- Persists all results to a Notion backend (Categories, Features, Apps, Feature Status databases)
- Supports any number of apps; covers all 500+ Gartner market categories

### `saas-standardizer`
Produces exhaustive, standardised profiles of SaaS products across 18 dimensions.
- Reads from and writes to the shared Notion feature registry
- Covers: features, use cases, APIs, pricing, security, support, roadmap, analyst rankings, and more

### `autonomyx-skill-score`
Evaluates professional skills from any source and generates a verified, framework-mapped resume.
- Accepts any input: profile URLs (LinkedIn, GitHub, Docker Hub, Stack Overflow, npm, PyPI, etc.), Verifiable Credentials, chat/email exports, authored documents, patents, certifications
- Evaluates each skill against profession-specific frameworks (SFIA, NICE, EDISON, PMI, CFA, SHRM, CIM, etc.) with proficiency levels and credibility-tiered proof ([S] self-evident through [G] self-reported)
- Uses Explorium prospect matching and enrichment for professional background
- Generates comprehensive skills table with framework mapping, behavioral + technical skills
- Supports Verifiable Credentials (W3C, JWT, SD-JWT, Open Badges v3) with trust tiers
- Encourages credential verification for unverified resume items

### `skills-frameworks`
Shared vocabulary of professional skills frameworks for standardized skill classification.
- Maps 17+ professions to their respective competency frameworks (SFIA, NICE/NIST, EDISON, PMI, CFA, SHRM, CIM, UXPA, etc.)
- Cross-framework level equivalence table (Beginner/Intermediate/Advanced/Expert across all frameworks)
- Protocol for industries without a recognized framework (ask user, use universal levels as fallback)
- Mandatory framework attribution for transparency

### `autonomyx-vocabulary`
Shared vocabulary and taxonomy reference used by all Autonomyx skills.
- Gartner Peer Insights → G2 category mapping (~120 markets)
- Canonical feature status badges (GA / Beta / Early Access / Feature Flag / Upcoming / etc.)
- Evidence tier definitions and confidence level criteria

## Notion Backend

The master feature registry lives in Notion (4 linked databases):

| Database | Purpose | Collection ID |
|---|---|---|
| Categories | Software market categories | `decfa7c6-0c11-4630-8dd0-4e6e02dbed03` |
| Features | Feature checklist per category | `1e4f2636-41f8-4d81-bb18-4c31b550ae54` |
| Apps | Applications analysed per category | `bb0d6e68-ddda-4601-b532-85fc9c73c2e8` |
| Feature Status | App + Feature + Status junction | `486dd914-9937-4667-8102-02de3321d0fb` |

Parent page: https://www.notion.so/32a33ce516978194a603c7be33badd53

## Installation

Install each `.skill` file from the `dist/` folder into your Claude skill manager.

## Skill Dependencies

```
feature-gap-analyzer
  └── reads → autonomyx-vocabulary (category resolution, badges, tiers)
  └── reads/writes → Notion (feature registry)

saas-standardizer
  └── reads/writes → Notion (feature registry)

autonomyx-vocabulary
  └── standalone reference (no dependencies)

autonomyx-skill-score
  └── reads → skills-frameworks (skill classification and framework mapping)
  └── reads → Explorium (match-prospects, enrich-prospects)
  └── reads → Platform APIs (GitHub, Docker Hub, Stack Overflow, npm, PyPI, Dev.to, etc.)
  └── reads → WordPress MCP tools (optional)
  └── reads → WebFetch (fallback for any platform)

skills-frameworks
  └── standalone reference (no dependencies)
```

## Feature Status Badges

| Badge | Meaning |
|---|---|
| ✅ GA | Generally Available — production-ready |
| 🔶 Beta | Available but not GA; opt-in or limitations |
| 🔷 Early Access | Select customers only |
| 🚩 Feature Flag | Gated; must be enabled by vendor/admin |
| 🗓️ Upcoming (Official) | Confirmed on public roadmap |
| 💬 Upcoming (Signal) | Unconfirmed — community/analyst hint |
| ❌ Not Present | No evidence of feature existing or planned |
| ❓ Roadmap Unknown | Absent, no roadmap info found |

## Evidence Rules

- **Feature existence**: confirmed only from official docs or GitHub repo
- **Scoring context**: Gartner Peer Insights, analyst PDFs, G2, Capterra
- **Roadmap**: official roadmap pages, changelogs, community idea boards

---

Maintained by Autonomyx. Last updated: March 2026.
