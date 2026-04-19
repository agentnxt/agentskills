# Carbon & Environmental Frameworks Reference

## Greenhouse Gas Scopes (GHG Protocol)

| Scope | What it covers | Examples |
|---|---|---|
| **Scope 1** | Direct emissions from owned/controlled sources | Company-owned data centres, company vehicles |
| **Scope 2** | Indirect emissions from purchased energy | Electricity used to power servers and offices |
| **Scope 3** | All other indirect emissions in value chain | Employee travel, supply chain, customer use of product, cloud providers used |

**Key point for SaaS:** Most SaaS companies host on AWS, GCP, or Azure. Their Scope 2 is
mostly the cloud provider's electricity. Scope 3 is far larger. Vendors that only report
Scope 1+2 are hiding most of their footprint.

---

## Science Based Targets initiative (SBTi)

The credibility gold standard for corporate climate commitments.

**Levels:**
- **Committed**: Company has pledged to set a target — no actual target yet
- **Target set**: Company has submitted a target, not yet validated
- **Validated**: Target independently verified to align with 1.5°C or well-below 2°C pathways
- **Net-Zero validated**: Highest standard — covers full value chain, validated by SBTi

**How to verify:** publicdisclosure.sciencebasedtargets.org (public database)

**Red flags:**
- "Net zero by 2050" without SBTi validation — this is a pledge, not a commitment
- Only Scope 1+2 targets with no Scope 3 roadmap
- "Carbon neutral" via offsets alone — SBTi requires actual emissions reduction, not just offsets

---

## CDP (formerly Carbon Disclosure Project)

Companies voluntarily disclose climate data to CDP. Scoring: A, A-, B, B-, C, D, D-.
A/A- indicates leadership-level disclosure and performance.

**How to verify:** cdp.net/en/responses (search by company name)

**What to look for:** Disclosure score (transparency) vs performance score (actual emissions trajectory)

---

## GRI (Global Reporting Initiative)

Voluntary sustainability reporting standard. More comprehensive than CDP but less
specifically focused on climate. Look for "GRI-aligned" or "GRI Standards" in the report.

---

## Renewable Energy

**Two types of renewable energy claims:**

1. **RECs / EACs (Renewable Energy Certificates)**: Buying a certificate that someone
   somewhere generated renewable electricity. The vendor's actual servers may run on
   fossil fuels. This is the weakest form.

2. **Direct PPAs (Power Purchase Agreements)**: Vendor contracts directly with a
   renewable generator for electricity from a specific facility. Much stronger.

3. **Behind-the-meter**: Vendor owns/operates renewable generation on-site. Strongest.

**Red flag:** "100% renewable" claims — always ask how. RECs alone are not equivalent
to actually running on renewable power.

---

## Data Centre Efficiency: PUE (Power Usage Effectiveness)

PUE = Total facility power / IT equipment power

| PUE | Rating |
|---|---|
| 1.0 | Perfect (theoretically impossible) |
| 1.1–1.2 | Excellent (hyperscale cloud providers) |
| 1.2–1.5 | Good |
| 1.5–2.0 | Average |
| >2.0 | Poor |

AWS/GCP/Azure hyperscale facilities typically achieve 1.1–1.2. Legacy co-lo data centres
can be 1.5–2.0+.

---

## Assessing credibility of net zero claims

**Credible & verified:** SBTi validated target, Scope 1+2+3 covered, third-party
audited progress reports, specific interim milestones, reduction-first (not offset-first)

**Aspirational:** Public pledge without SBTi validation, Scope 3 excluded or vague,
no third-party verification, reliant on offsets

**No commitment:** No public target, no disclosure, or carbon neutral claims based
entirely on purchasing offsets without reduction targets

**Not disclosed:** No sustainability page, no ESG report, no CDP disclosure — flag this
as a gap; many smaller SaaS companies simply haven't addressed this yet

---

## Quick search queries for carbon assessment

- `[vendor] sustainability report [year]`
- `[vendor] carbon neutral net zero`
- `[vendor] ESG report`
- `[vendor] CDP disclosure`
- `[vendor] science based targets`
- `[vendor] renewable energy data centre`
- site:cdp.net [vendor]
- site:sciencebasedtargets.org [vendor]
