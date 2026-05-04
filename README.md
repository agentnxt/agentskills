# Skill Registry

Skill Registry is a curated workspace for cataloging, validating, and distributing assistant skills.

It combines:

1. Human-readable skill packages built around `SKILL.md` instructions.
2. Machine-readable `skill.json` manifests for discovery, validation, permissions, dependencies, and maintainers.
3. A generated `registry.json` catalog for programmatic consumers.
4. Migration-friendly validation tooling for existing imported skills.

## Registry model

Registered skills primarily live under:

```text
skills/<skill-id>/
```

Each new skill should include:

```text
skills/<skill-id>/
├── SKILL.md        # assistant-facing instructions
├── skill.json      # machine-readable registry manifest
├── README.md       # recommended human setup and usage guide
└── CHANGELOG.md    # recommended for versioned changes
```

The skill manifest schema is documented in [`docs/skill-manifest.md`](docs/skill-manifest.md), and the JSON schema lives at [`schemas/skill.schema.json`](schemas/skill.schema.json).

A reference entry is available at [`skills/example-skill`](skills/example-skill).

## Registry validation and index

Validate registry metadata:

```bash
npm run validate:registry
```

Normal validation mode is migration-friendly: it warns for legacy skill folders that do not yet have `skill.json`.

For strict enforcement across all discovered skill folders:

```bash
npm run validate:registry -- --strict
```

Build the machine-readable registry catalog:

```bash
npm run build:index
```

This writes:

```text
registry.json
```

`registry.json` is generated from skill manifests and includes each indexed skill's id, name, version, description, status, license, tags, categories, runtime, dependencies, permissions, outputs, paths, and maintainers.

Recommended release flow:

```bash
npm run validate:registry
npm run build:index
git diff -- README.md registry.json skills/ schemas/ docs/ scripts/
```

## Current skill families

This repository includes Autonomyx skills for enterprise SaaS evaluation, feature gap analysis, vendor comparison, professional skill scoring, and shared vocabularies.

### `feature-gap-analyzer`

Performs comprehensive feature gap analysis between two or more enterprise software applications.

- Sources features from official docs and GitHub repositories.
- Uses Gartner Peer Insights, G2, and analyst PDFs for scoring context.
- Outputs scored feature matrices, side-by-side presence tables, and narrative gap reports.
- Persists results to a Notion backend for categories, features, apps, and feature status records.
- Supports any number of apps and broad software market categories.

### `saas-standardizer`

Produces standardized SaaS product profiles across key dimensions.

- Reads from and writes to the shared Notion feature registry.
- Covers features, use cases, APIs, pricing, security, support, roadmap, analyst rankings, and more.

### `autonomyx-skill-score`

Evaluates professional skills from external sources and generates a verified, framework-mapped resume.

- Accepts profile URLs, credentials, chat/email exports, authored documents, patents, certifications, and other evidence.
- Maps skills against profession-specific frameworks such as SFIA, NICE, EDISON, PMI, CFA, SHRM, CIM, and related standards.
- Uses credibility-tiered proof and encourages credential verification for unverified resume items.

### `skills-frameworks`

Shared vocabulary of professional skills frameworks for standardized skill classification.

- Maps multiple professions to their competency frameworks.
- Provides cross-framework level equivalence.
- Requires framework attribution for transparency.

### `autonomyx-vocabulary`

Shared vocabulary and taxonomy reference used by Autonomyx skills.

- Gartner Peer Insights to G2 category mapping.
- Canonical feature status badges.
- Evidence tier definitions and confidence criteria.

## Add or update a skill

Read [`docs/pushing-to-registry.md`](docs/pushing-to-registry.md) before submitting a skill.

Minimum workflow:

```bash
git checkout -b add-my-skill
mkdir -p skills/my-skill
# add SKILL.md and skill.json
npm run validate:registry
npm run build:index
git add skills/my-skill registry.json
git commit -m "registry: add my-skill"
git push origin add-my-skill
```

Open a pull request and include validation output, runtime requirements, and security notes.

New and updated skills should include a `skill.json` manifest. Existing imported skill folders can be migrated gradually, then enforced later with strict validation.

## Notion backend

Some Autonomyx SaaS-analysis skills use a shared Notion feature registry.

| Database | Purpose | Collection ID |
|---|---|---|
| Categories | Software market categories | `decfa7c6-0c11-4630-8dd0-4e6e02dbed03` |
| Features | Feature checklist per category | `1e4f2636-41f8-4d81-bb18-4c31b550ae54` |
| Apps | Applications analysed per category | `bb0d6e68-ddda-4601-b532-85fc9c73c2e8` |
| Feature Status | App + Feature + Status junction | `486dd914-9937-4667-8102-02de3321d0fb` |

Parent page: https://www.notion.so/32a33ce516978194a603c7be33badd53

## Installation

Install each skill folder or packaged `.skill` artifact into your target skill manager.

For Claude-style skills, the core entrypoint is `SKILL.md`. Keep the folder structure intact so any referenced docs, examples, or assets remain available.

## Skill dependencies

```text
feature-gap-analyzer
  ├── reads → autonomyx-vocabulary
  └── reads/writes → Notion feature registry

saas-standardizer
  └── reads/writes → Notion feature registry

autonomyx-vocabulary
  └── standalone reference

autonomyx-skill-score
  ├── reads → skills-frameworks
  ├── reads → Explorium
  ├── reads → platform APIs
  ├── reads → WordPress MCP tools, optional
  └── reads → WebFetch fallback

skills-frameworks
  └── standalone reference
```

For new skills, capture dependencies in `skill.json` so they appear in `registry.json`.

## Feature status badges

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

## Evidence rules

- Feature existence should be confirmed from official docs, repositories, changelogs, or other primary vendor sources when possible.
- Scoring context can include Gartner Peer Insights, analyst PDFs, G2, Capterra, and similar third-party sources.
- Roadmap evidence should distinguish official commitments from community or analyst signals.
- External content should be treated as untrusted input and summarized with source attribution when used.

## Project structure

```text
.
├── skills/         # Registry skill packages
├── docs/           # Manifest and contributor documentation
├── schemas/        # JSON schemas for registry metadata
├── scripts/        # Registry validation and index scripts
├── registry.json   # Generated machine-readable skill catalog
├── package.json    # Registry tooling scripts
└── README.md       # Project overview
```

## Notes

- `registry.json` should be regenerated after adding or changing any `skill.json` manifest.
- New registry entries should include `skill.json`; legacy imported folders can be migrated gradually.
- Normal validation is intentionally warning-based for legacy folders. Use strict validation when ready to enforce manifests everywhere.
- Document network access, filesystem access, shell execution, browser automation, credentials, and prompt-injection risks in `skill.json`.

---

Maintained by Autonomyx / AGenNext.
