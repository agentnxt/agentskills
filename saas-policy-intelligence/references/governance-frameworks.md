# Governance & Compliance Frameworks Reference

## GDPR (General Data Protection Regulation) — EU/EEA

**Applies to:** Any company processing data of EU/EEA residents, regardless of where
the company is based.

**What to look for in vendor documentation:**

| Item | Where to find it | Red flag if missing |
|---|---|---|
| Lawful basis for each processing purpose | Privacy Policy | ⚠️ High |
| DPA (Data Processing Agreement) | Legal hub / on request | ⚠️ High |
| Subprocessor list | Trust center / Privacy Policy | ⚠️ Medium |
| Data transfer mechanism (SCCs, BCRs, adequacy) | DPA / Privacy Policy | ⚠️ High for non-EU vendors |
| DPO contact details | Privacy Policy | ⚠️ Medium |
| Data retention periods | Privacy Policy | ⚠️ Medium |
| User rights mechanism (access, erasure, portability) | Privacy Policy | ⚠️ High |
| Breach notification SLA | Privacy Policy / DPA | 72-hour requirement |

**Data transfer mechanisms post-Schrems II:**
- Standard Contractual Clauses (SCCs) — most common for US vendors
- Binding Corporate Rules (BCRs) — for intra-group transfers in multinationals
- Adequacy decisions — UK, Switzerland, Japan, South Korea, others (not US as of 2024)
- EU-US Data Privacy Framework (DPF) — reinstated 2023, legal challenges ongoing

---

## CCPA / CPRA (California Consumer Privacy Act / Rights Act)

**Applies to:** Companies meeting any of: $25M+ annual revenue, data on 100K+ CA consumers,
50%+ revenue from selling personal data.

**Key rights:** Know, delete, opt-out of sale/sharing, correct, limit sensitive data use.

**What to look for:**
- "Do Not Sell or Share My Personal Information" link on website
- CCPA-specific privacy notice
- Response mechanism for consumer rights requests

---

## HIPAA (Health Insurance Portability and Accountability Act) — US

**Applies to:** Covered entities and their business associates handling PHI.

**For SaaS vendors:**
- Must offer a Business Associate Agreement (BAA)
- HIPAA-eligible tier may differ from standard product
- AI features almost always require careful review — many model providers will not sign BAAs

**Key question:** "Does your AI / ML product feature operate under the BAA?" Almost always ask.

---

## SOC 2 — see security-certifications.md for full detail

Quick summary for governance section:
- Type II, recent audit period (<12 months), scope matches product used
- Report available under NDA — if vendor refuses, that's a red flag

---

## ISO 27001 — see security-certifications.md for full detail

Quick summary: Check scope and verify against accreditation body's public registry.

---

## FedRAMP — see security-certifications.md for full detail

Quick summary: Check marketplace.fedramp.gov. "In Process" ≠ Authorized.

---

## EU AI Act (effective August 2026 for high-risk systems)

**Risk tiers:**
- **Prohibited:** Social scoring, real-time biometric surveillance (most commercial SaaS: N/A)
- **High-risk:** AI in hiring, credit, education, critical infrastructure, law enforcement
- **Limited risk:** Chatbots, deepfakes — transparency obligations
- **Minimal risk:** Most AI features — no specific obligations

**What to look for for SaaS AI products:**
- Does the vendor classify their AI product under the EU AI Act?
- Do they publish a conformity assessment (required for high-risk systems)?
- Do they have a "general-purpose AI model" declaration (GPAI) if applicable?
- Are they registered in the EU AI Act database (when live)?

---

## DPA checklist (what a good Data Processing Agreement covers)

- [ ] Scope of processing (purposes, data types, duration)
- [ ] Controller vs processor obligations clearly defined
- [ ] Sub-processor list and change notification mechanism
- [ ] Data transfer provisions (SCCs or equivalent)
- [ ] Security obligations (specific, not just "reasonable measures")
- [ ] Audit rights (right to audit or commission audit)
- [ ] Data deletion on termination (timeline specified)
- [ ] Breach notification obligation (72-hour for GDPR)
- [ ] Return of data on termination

---

## Subprocessor chain — what to look for

Every major SaaS product uses subprocessors (cloud hosting, analytics, support tools, AI providers).
Key questions:
1. Is the list publicly accessible or available on request?
2. How much notice is given before adding a new subprocessor? (30 days is standard; fewer is weak)
3. Does the right to object exist? (GDPR requires it)
4. Are AI model providers (OpenAI, Anthropic, Google, etc.) listed? And do they have their own BAAs/DPAs?

---

## Governance maturity scoring (internal use)

Use this to rate a vendor's overall governance posture in the brief:

| Score | Label | Criteria |
|---|---|---|
| 5 | **Exemplary** | SOC 2 Type II + ISO 27001 + GDPR DPA + SBTi validated + public transparency report |
| 4 | **Strong** | SOC 2 Type II + GDPR DPA + at least one framework from above |
| 3 | **Adequate** | SOC 2 Type I or ISO 27001 + basic GDPR compliance |
| 2 | **Developing** | Self-attested compliance, no third-party audit, partial documentation |
| 1 | **Insufficient** | No certifications, no DPA, no transparency |
