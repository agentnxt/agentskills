---
did: skill:023
version: "1.0.0"
created: "2026-04-29"
featureFlag: "production"
name: autonomyx-saas-evaluator
description: >
  Multi-persona enterprise SaaS evaluation framework based on the SaaS Usability Index.
  Use this skill whenever a user wants to evaluate, score, benchmark, or audit a SaaS
  product before procurement, investment, or competitive analysis. Triggers on: "evaluate
  [product]", "score this SaaS", "should we buy [tool]", "benchmark [vendor]",
  "procurement review of [software]", "how good is [product] for enterprise",
  "compare [tool A] vs [tool B]", "assess [vendor] for our team", "I'm the CISO and want
  to review [product]", "continue my evaluation of [product]", "what's the status of the
  [product] review". Also triggers when a user identifies their role (CISO, IT Admin,
  Procurement, CTO, Legal, Dept Head) alongside any SaaS product — they are likely
  starting or resuming a persona-based evaluation. Always use this skill when a product
  name and evaluation intent appear together, even casually.
---

# SaaS Usability Index — Multi-Persona Evaluator Skill

## Overview

This skill orchestrates a **team-based SaaS evaluation** where 6 specialist personas
each assess the metrics relevant to their domain. Scores and notes persist across
sessions per product. The final PDF report is only generated once all 6 personas have
submitted their sections.

**Output**: Professional PDF report saved to `/mnt/user-data/outputs/`

---

## The 6 Evaluator Personas

Each persona owns specific stages/metrics. Read their full profile in `references/personas/`:

| Persona | File | Owns Stages | Key Concerns |
|---------|------|-------------|--------------|
| CISO / Security Lead | `ciso.md` | 2 (partial), 4, 5 (partial) | Threat surface, compliance certs, IAM |
| IT Admin / IAM Engineer | `it-admin.md` | 3, 4, 5 (partial) | Provisioning, device mgmt, integrations |
| Procurement / Finance Lead | `procurement.md` | 1, 6 | Cost, contracts, vendor stability |
| CTO / Engineering Lead | `cto.md` | 2 (partial), 3 (partial) | APIs, architecture, TTV, automation |
| Legal & Compliance Officer | `legal.md` | 5 (partial), 7 | Data residency, exit rights, audit logs |
| End User / Dept Head | `dept-head.md` | 1 (partial), 3 (partial) | UX, adoption, feature fit, TTV |

**Metric ownership is exclusive** — each metric is evaluated by exactly ONE persona.
See `references/personas/metric-ownership.md` for the full assignment map.

---

## Stage Weights (Pre-defined)

| # | Stage | Weight |
|---|-------|--------|
| 1 | Pre-Purchase / Discovery | 10% |
| 2 | Vendor Evaluation & Selection | 20% |
| 3 | Onboarding & Implementation | 12% |
| 4 | Identity & Access Configuration | 18% |
| 5 | Operations & Governance | 20% |
| 6 | Commercial Lifecycle | 10% |
| 7 | Risk, Exit & Replacement | 10% |

---

## Persistent Memory Schema

Every evaluation is stored per product, per persona. Use the artifact storage API
(window.storage for web artifacts) OR write to filesystem at:
`/home/claude/saas-evaluator/data/[product-slug]/[persona-slug].json`

```json
{
  "product": "notion",
  "persona": "ciso",
  "persona_display": "CISO / Security Lead",
  "evaluator_name": "Jane Smith",
  "last_updated": "2025-07-15T10:30:00Z",
  "status": "complete",
  "metrics": {
    "2.3_login_methods_sso": {
      "score": 4,
      "evidence": "https://notion.so/security — SAML SSO documented",
      "notes": "SSO available but MFA enforcement requires admin action",
      "source": "web-search"
    }
  },
  "stage_notes": {
    "stage_4": "Strong IAM story overall; SCIM provisioning confirmed via Okta docs"
  },
  "red_flags": ["4.3_iga_coverage: no certifications found"],
  "persona_verdict": "Approvable with conditions — require vendor to confirm IGA roadmap"
}
```

**Storage key pattern**: `eval:[product-slug]:[persona-slug]`
e.g. `eval:notion:ciso`, `eval:rippling:procurement`

---

## Master Evaluation State

One additional file tracks overall evaluation progress:
`/home/claude/saas-evaluator/data/[product-slug]/state.json`

```json
{
  "product": "Notion",
  "product_slug": "notion",
  "initiated_by": "Jane Smith (CISO)",
  "initiated_at": "2025-07-10T09:00:00Z",
  "use_case": "Team wiki and knowledge management",
  "competitors_requested": ["Confluence", "Coda"],
  "persona_status": {
    "ciso": "complete",
    "it-admin": "complete",
    "procurement": "in-progress",
    "cto": "not-started",
    "legal": "not-started",
    "dept-head": "complete"
  },
  "cross_persona_flags": [
    {
      "topic": "DPA data processing scope",
      "raised_by": "procurement",
      "needs_input_from": ["legal", "ciso"],
      "resolved": false
    }
  ],
  "ready_for_report": false
}
```

`ready_for_report` = true only when ALL 6 persona statuses are "complete".

---

## Execution Workflow

### On Every Session Start — Detect Mode

**Step 1: Identify who is speaking and what product they mean.**

Ask if unclear: *"Which product are you evaluating, and what's your role in this review?"*

Then load state:
```
state = load /home/claude/saas-evaluator/data/[product-slug]/state.json
persona_data = load /home/claude/saas-evaluator/data/[product-slug]/[persona-slug].json
```

Branch into one of these modes:

---

### MODE A — New Evaluation (no state file exists)

1. Ask: *"Any specific use case or competitors to benchmark against?"*
2. Create `state.json` with all personas set to "not-started"
3. Announce the team: show the 6 personas and who needs to contribute
4. Auto-research ALL 35 metrics via web search (see search patterns below)
5. Pre-populate each persona's JSON with auto-researched scores + sources
6. Mark auto-researched metrics as `"source": "web-search"` vs `"source": "user-provided"`
7. Present the current persona's metrics for review and gap-filling
8. Save updated persona JSON, set status to "complete"
9. Show evaluation dashboard (which personas still pending)

---

### MODE B — Returning Persona (state exists, this persona not yet complete)

1. Greet by name if stored: *"Welcome back, [name]. Continuing the [product] evaluation."*
2. Load their existing persona JSON
3. Show their assigned metrics — pre-filled from auto-research
4. For any metric with `"source": "web-search"`, invite confirmation or override:
   *"I found this via web search: [evidence]. Score: [X]. Does this match your experience?"*
5. For gaps (score missing or flagged uncertain), ask directly
6. Capture `stage_notes` and `persona_verdict`
7. Save, set status = "complete"
8. Show updated dashboard

---

### MODE C — Checking Status

If user asks "what's the status of the [product] review":
- Load `state.json`
- Display dashboard: which personas complete, in-progress, not-started
- Show estimated completion (e.g. "3 of 6 personas done")
- If ready_for_report = true → offer to generate PDF immediately

---

### MODE D — Discussion Mode (any persona, any time)

Triggered when the human shares a fact, idea, claim, or concern and wants to
think it through — not just score it.

**Detection signals**: "What do you think about...", "The vendor says...",
"I'm not sure whether...", "Our team thinks we should...", "Is [X] actually
important?", or any statement that invites reaction rather than a data request.

**Behaviour**:
1. Load the current persona profile from `references/personas/[persona].md`
2. Engage using the Discussion Mode behaviours defined in that persona file:
   - Fact-challenge vendor claims using domain expertise
   - Stress-test the human's proposed approaches with specific counter-questions
   - Surface risks the human hasn't considered yet
   - Concede gracefully when the human makes a strong point
   - Raise proactive topics from the persona's watchlist unprompted
3. Maintain the persona's voice consistently throughout — a CISO sounds like a
   CISO, not a generic assistant. Tone, vocabulary, and risk framing must match.
4. After discussion reaches a conclusion, ask:
   *"Should I save this as an agreed condition for the evaluation?"*
5. If yes, append to `discussion_log` and `agreed_conditions` in persona JSON.

**Discussion never blocks scoring** — personas can discuss and score in any order
within the same session.

**Cross-persona flag**: If a topic spans multiple personas (e.g. "should we accept
their DPA?"), note it explicitly:
> "That's primarily Legal's domain, but the CISO should also weigh in on the data
> processing scope. I'll flag this for the CISO session."
Save the cross-persona flag to `state.json` under `cross_persona_flags`.

---

### MODE E — Report Generation (all 6 personas complete)

Triggered when `ready_for_report` flips to true, OR user asks for the report.

1. Load all 6 persona JSON files
2. Merge all metric scores into unified scoring matrix
3. Calculate stage scores and U_index (see formula below)
4. Read `references/report-template.md`
5. Generate PDF with multi-persona attribution (each metric shows which persona scored it)
6. Include Panel Consensus page synthesising all 6 persona verdicts + discussion outcomes
7. Save to `/mnt/user-data/outputs/[product-slug]-saas-evaluation.pdf`

---

## Auto-Research Search Patterns

When a new evaluation starts, search ALL metrics before asking any persona:

```
"[product] SSO SAML OIDC"            → personas: ciso, it-admin
"[product] SCIM provisioning Okta"   → persona: it-admin
"[product] SOC2 ISO 27001"           → personas: ciso, legal
"[product] pricing enterprise tiers" → persona: procurement
"[product] API documentation REST"   → persona: cto
"[product] audit logs retention"     → personas: ciso, legal
"[product] data export GDPR"         → persona: legal
"[product] roadmap 2025"             → personas: procurement, cto
"[product] onboarding templates"     → personas: it-admin, dept-head
"[product] mobile app UX reviews"    → persona: dept-head
"[product] funding crunchbase"       → persona: procurement
"[product] RBAC permissions"         → personas: ciso, it-admin
"[product] SLA support enterprise"   → personas: procurement, it-admin
"[product] compliance certifications"→ persona: legal
"[product] time to value deploy"     → personas: cto, dept-head
```

---

## Scoring Formula

```
Stage_Score     = (Σ metric_scores_in_stage) / (max_possible_for_stage) × 5
U_index         = Σ (Stage_Score × Stage_Weight)
```

Verdict thresholds:
- **< 2.0** = Not enterprise-ready (Do Not Procure)
- **2.0–2.9** = Emerging (Conditional — requires vendor commitments)
- **3.0–3.9** = Enterprise Baseline (Approvable with monitoring)
- **4.0–4.9** = Strong (Recommended)
- **5.0** = Best-in-class

Procurement blockers: any metric scoring 0 or 1 in Stages 2, 4, or 5 — surface
prominently in PDF and in dashboard.

---

## Key Principles

- **Search first, ask second.** Pre-populate all metrics from web search; personas only
  confirm, override, or fill genuine gaps.
- **Persona voice.** Each persona receives questions framed in their domain language.
  A CISO sees "Does this meet your threat model?" not "Is this a good product?"
- **Memory is sacred.** Never discard a persona's saved scores. On conflict, always
  ask the persona to confirm before overwriting.
- **Partial reports are blocked.** The PDF is never generated until all 6 personas
  have set status = "complete". Show the dashboard instead.
- **Flag blockers loudly.** Any 0 or 1 score in Stages 2, 4, 5 gets a 🚨 in every
  view — dashboard, deep-dive pages, and exec summary.

---

## Reference Files

- `references/metrics.md` — Full 35-metric definitions, 0/3/5 anchors, search queries
- `references/report-template.md` — PDF structure, radar chart, per-persona attribution
- `references/personas/ciso.md` — CISO persona: skills, metrics, question style
- `references/personas/it-admin.md` — IT Admin persona profile
- `references/personas/procurement.md` — Procurement persona profile
- `references/personas/cto.md` — CTO persona profile
- `references/personas/legal.md` — Legal persona profile
- `references/personas/dept-head.md` — Dept Head persona profile
- `references/personas/metric-ownership.md` — Master map: which persona owns each metric

---

## Autonomyx Standard

Read and apply `references/autonomyx-standard.md` at the end of every response.
This includes the feedback loop, author info, social links, and community CTA.
