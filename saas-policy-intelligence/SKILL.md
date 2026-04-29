---
did: skill:024
name: saas-policy-intelligence
description: >
  Analyses inbound SaaS vendor policy documents across five domains: Privacy & Data Usage,
  AI/ML Training Policy, Carbon Footprint, Security Posture, and Governance Frameworks.
  Trigger when a vendor URL is shared or on questions like: "what changed in X's policy",
  "is X GDPR compliant", "what's X's AI training default", "does X have SOC 2", "what's
  X's carbon commitment", "opt-out of AI training on X", "subprocessor list for X",
  "what's X's security posture", "compare X vs Y on compliance", "should we worry about
  X's new terms", "summarise this policy for our security review". Also trigger when a
  URL appears alongside: policy, terms, privacy, DPA, security, AI training, carbon,
  sustainability, governance, changelog. Skill scope: analyses vendor policies (inbound).
  For drafting your own policies use website-policy-drafting-skill. For procurement
  scoring use saas-evaluator. Outputs 8 sections: what changed, privacy, AI training,
  security, carbon, governance, competitor comparison, and deadline-bound actions.
---

# SaaS Policy Intelligence

Turns any inbound vendor policy URL, policy change, or policy question into a structured
8-section analyst brief. Designed for engineering leads, security teams, legal/compliance,
procurement, and DPOs who need to understand what a vendor's policy actually means —
especially when it just changed.

**Skill boundaries:**
- This skill = analyse inbound vendor policies (reactive, monitoring, due diligence)
- `website-policy-drafting-skill` = draft your own policies (outbound, creation)
- `saas-evaluator` = score a vendor across all dimensions for procurement decisions

---

## Five policy domains — always cover all five

Even if the user only shares one document, research the vendor's published materials across
all five domains. If information is not publicly available, state that explicitly.

| Domain | What to look for |
|---|---|
| **Privacy & Data Usage** | Collection, retention, sharing, lawful basis, subprocessors, user rights |
| **AI/ML Training Policy** | Training defaults (opt-in/out/never), interaction data, model providers, enterprise exemption |
| **Carbon Footprint** | Net zero target, Scope 1/2/3, SBTi status, renewable energy %, third-party verification |
| **Security Posture** | SOC 2, ISO 27001, FedRAMP, pen testing, bug bounty, encryption, breach history |
| **Governance & Compliance** | GDPR, CCPA, HIPAA, DPA availability, audit rights, subprocessor notification |

---

## Research workflow — 8 steps, always execute all

**Never rely on training knowledge for policy details.** Policies change constantly.
Search and fetch everything. Stale data causes compliance failures.

### Step 1 — Fetch primary source
- If URL given: fetch it immediately with web_fetch
- Search for the vendor's full policy suite: privacy policy, ToS, DPA, AI policy, trust center,
  subprocessor list, sustainability/ESG report, any recent changelogs
- Queries: `[vendor] privacy policy`, `[vendor] DPA trust center`, `[vendor] AI training policy`,
  `[vendor] sustainability report`, `[vendor] SOC 2`, `[vendor] changelog [year]`

### Step 2 — Find the diff (what changed vs before)
- Search Wayback Machine snapshots, prior blog posts, community references to old policy
- Label changes explicitly: **NEW** / **CHANGED** / **REMOVED**
- Surface changes buried in footnotes, defined terms, exhibit updates — these matter

### Step 3 — Community and expert reaction
Search: Hacker News, Reddit (r/privacy r/netsec r/programming r/sysadmin), GitHub Discussions,
GitGuardian blog, Snyk, Trail of Bits, IAPP, noyb.eu, Twitter/X, LinkedIn.
Capture: dominant sentiment, technical objections, legal challenges filed, regulatory
investigations, migration announcements from notable teams.

### Step 4 — Security posture
From trust center or third-party sources:
- Certifications: SOC 2 (Type I vs II, scope, recency), ISO 27001 (issuing body, scope),
  FedRAMP (level, check marketplace.fedramp.gov), PCI DSS, HIPAA BAA
- Encryption: at rest (algorithm), in transit (TLS version), key management model
- Pen testing cadence and last disclosed date
- Bug bounty: platform, scope
- Incident response SLA and breach notification window
- Breach/CVE history: search `[vendor] data breach`, `[vendor] security incident`
- Load `references/security-certifications.md` for verification guidance

### Step 5 — Carbon and environmental assessment
- Fetch sustainability/ESG page or annual report
- SBTi status: committed / validated / not committed (verify at publicdisclosure.sciencebasedtargets.org)
- Net zero target year and Scope coverage (Scope 1 only vs 1+2 vs 1+2+3)
- Renewable energy % and method (RECs vs direct PPA vs behind-the-meter)
- Data centre PUE if disclosed; underlying cloud provider and their commitments
- CDP score if available (cdp.net)
- Credibility rating: Credible & verified / Aspirational / No commitment / Not disclosed
- Load `references/carbon-frameworks.md` for assessment guidance

### Step 6 — Governance and compliance mapping
Map against: GDPR, CCPA/CPRA, HIPAA, SOC 2, ISO 27001, FedRAMP, EU AI Act.
For each: status, DPA/BAA availability, audit rights, subprocessor notification period.
Load `references/governance-frameworks.md` for framework details and DPA checklist.
Load `references/lawful-basis-cheatsheet.md` if EU/EEA users are affected.

### Step 7 — Competitor comparison
3–5 direct competitors, same five domains, comparison table.
Start with `references/competitor-privacy-tiers.md` but always verify live — do not cite cached data.

### Step 8 — Synthesise: gaps, risks, deadlines
- What the policy does NOT address (gaps = often the most important finding)
- Ambiguous language creating compliance risk
- Hard deadlines: effective dates, renewal windows, regulatory deadlines
- Who needs to act: engineering, legal, security, procurement, DPO

---

## Output — always produce all 8 sections

```markdown
# [Vendor] Policy Intelligence Brief
**Date:** [today] | **Effective date:** [date] | **Action deadline:** [date or none]
**Domains:** Privacy · AI Policy · Carbon · Security · Governance

## 1. What changed (and what it replaced)
One-sentence summary of the shift.
| Dimension | Before | After | Status |
Effective date · notice period given.

## 2. Privacy & Data Usage
- Data types collected + retention periods
- Processing purposes + lawful basis (flag "legitimate interest" for AI training)
- Subprocessors: named or link to live list
- Third-party sharing: affiliates, model providers, analytics
- Data residency + transfer mechanism (SCCs, BCRs, adequacy)
- User rights + how to exercise them
- Enterprise vs individual split — always check, always different

## 3. AI / ML Training Policy
- Default: opt-IN / opt-OUT / NEVER — per tier
- Data in scope: prompts, outputs, interaction data, content at rest
- Enterprise exemption: yes / no / conditional
- Third-party model providers receiving data
- Opt-out: step-by-step path
- Prior data: deleted on opt-out or just future collection stopped?
- Private content gap: interaction data from private repos/workspaces?

## 4. Security Posture
| Cert | Type | Scope | Expiry | Verification |
- Encryption: at rest / in transit / key management
- Pen testing: cadence + last disclosed date
- Bug bounty: platform + scope
- Incident response SLA + notification window
- Breach/CVE history (past 24 months) — state clearly if none found
- Gap vs industry standard for this product category

## 5. Carbon Footprint & Environmental Commitments
- Net zero: year + scope (1 only / 1+2 / 1+2+3)
- SBTi: committed / validated / not committed
- Renewable energy: % + method (RECs / direct PPA / behind-the-meter)
- Data centre PUE if disclosed
- Third-party verification: CDP score, GRI, independent auditor
- Credibility: Credible & verified / Aspirational / No commitment / Not disclosed

## 6. Governance & Compliance Framework
| Framework | Status | DPA/BAA available | Audit rights | Notes |
| GDPR | ✅/⚠️/❌ | | | |
| CCPA/CPRA | ✅/⚠️/❌ | | | |
| HIPAA | ✅/⚠️/❌ | | | |
| SOC 2 Type II | ✅/⚠️/❌ | | | |
| ISO 27001 | ✅/⚠️/❌ | | | |
| FedRAMP | ✅/⚠️/❌ | | | |
| EU AI Act | ✅/⚠️/❌ | | | |
Subprocessor change notice: X days · Data deletion on termination: Y days SLA

## 7. Competitor Comparison
| Vendor | Privacy default | AI training | Key certs | Net zero | Governance |

## 8. Recommended Actions
### Immediate — before [deadline]
- [ ] [Action] — Owner: [Engineering / Legal / Security / Procurement / DPO]
### Short-term — within 30 days
- [ ] [Action] — Owner: [role]
### Long-term / strategic
- [ ] [Action] — Owner: [role]
### Risk register
| Risk | Severity H/M/L | Likelihood | Owner | Mitigation |
```

---

## Quality standards

- **Evidence first** — every claim cites a URL, document section, or community thread
- **No guessing** — if policy language is ambiguous, say so and flag it as a risk
- **Flag gaps** — what the policy does NOT say is often the most important finding
- **Unbiased** — vendor's stated rationale alongside expert/community criticism
- **Enterprise vs individual** — never assume equal; almost always different
- **Deadline prominent** — effective dates at the top, not buried
- **Verified, not assumed** — cross-check cert claims; SOC 2 scope may exclude the product used
- **Scope-aware** — "SOC 2 certified" means nothing if it excludes the product in question

---

## Reference files — load on demand, not all upfront

| File | Load when |
|---|---|
| `references/lawful-basis-cheatsheet.md` | EU/EEA users affected or GDPR lawful basis claimed |
| `references/security-certifications.md` | Assessing security posture or verifying cert claims |
| `references/carbon-frameworks.md` | Assessing environmental commitments or net zero claims |
| `references/governance-frameworks.md` | Building governance section or DPA checklist |
| `references/competitor-privacy-tiers.md` | Starting point for competitor comparison (verify live) |
