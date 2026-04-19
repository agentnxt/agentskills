# Autonomyx Fraud Sentinel — External Data Providers

> This file defines the external enrichment layer for pre-action risk scoring.
> Providers are queried in parallel during Step B2 (Scoring Engine).
> Always use the minimum data necessary. Never store raw API responses — store only the extracted signals.

---

## Provider Tier Structure

```
TIER 1 — PRIMARY (always query)
  └── FRI (India) — free, government, mobile number risk
  └── IPQS — affordable, global, device/IP/email/phone

TIER 2 — SECONDARY (query when Tier 1 confidence < 0.6)
  └── SEON — social + digital identity enrichment
  └── SpyCloud — darknet breach / credential exposure

TIER 3 — ENTERPRISE (query for Critical risk events only)
  └── LexisNexis Risk — identity + public records + fraud rings
  └── Alloy — orchestration across 200+ sources
```

---

## TIER 1 — FRI (Financial Fraud Risk Indicator)

**Provider:** Department of Telecommunications, Government of India
**Platform:** Digital Intelligence Platform (DIP)
**Cost:** Free (requires registration with DoT/DIU)
**Coverage:** India — mobile numbers only
**Latency:** Real-time (<100ms)
**Mandatory:** Yes for any India-based transaction involving a mobile number

### What it provides
- Risk classification: `Medium` | `High` | `Very High`
- Sources: I4C NCRP cybercrime reports + DoT Chakshu + bank intelligence
- Mobile Number Revocation List (MNRL) — numbers disconnected for fraud

### Integration
```
Registration: Apply via Digital Intelligence Unit (DIU), DoT
API endpoint: Provided post-registration (DIP secure API)
Auth: API key (provided by DIU after onboarding)
Query: Mobile number → risk classification
```

### How to apply
1. Visit: https://www.dot.gov.in/digital-intelligence-unit
2. Register as a financial institution / payment platform
3. Receive API credentials from DIU
4. Integrate into pre-action query flow

### Signal mapping for Fraud Sentinel
| FRI Classification | Risk Score Contribution | Fraud Sentinel Action |
|-------------------|------------------------|----------------------|
| Very High | +45 | Auto-escalate to STRONG_WARN or BLOCK |
| High | +30 | Escalate risk level by 1 tier |
| Medium | +15 | Flag for monitoring |
| Not found / Clean | 0 | No adjustment |

### Environment variables
```
FRI_API_URL=<provided by DoT DIU post-registration>
FRI_API_KEY=<provided by DoT DIU post-registration>
```

---

## TIER 1 — IPQS (IPQualityScore)

**Provider:** IPQualityScore
**Website:** https://www.ipqualityscore.com
**Cost:** Free tier (5,000 queries/month) → paid tiers from ~$20/month
**Coverage:** Global
**Latency:** Real-time (<50ms)
**Use for:** IP address, email address, phone number, device fingerprint, URL scanning

### APIs to use

#### 1. IP Reputation API
```
GET https://ipqualityscore.com/api/json/ip/{API_KEY}/{ip_address}
Returns: fraud_score (0-100), is_proxy, is_vpn, is_tor, country_code, recent_abuse
```

#### 2. Email Validation API
```
GET https://ipqualityscore.com/api/json/email/{API_KEY}/{email}
Returns: fraud_score, disposable, recent_abuse, leaked, valid
```

#### 3. Phone Validation API
```
GET https://ipqualityscore.com/api/json/phone/{API_KEY}/{phone}?country=IN
Returns: fraud_score, risky, active, line_type, recent_abuse, leaked
```

#### 4. Device Fingerprint (JS SDK)
```
Include IPQS JS snippet → collect fingerprint → query
Returns: fraud_score, is_bot, is_emulator, device_id
```

### Signal mapping for Fraud Sentinel
| IPQS Fraud Score | Risk Score Contribution |
|-----------------|------------------------|
| 85–100 | +40 |
| 75–84 | +25 |
| 60–74 | +15 |
| 0–59 | 0 |
| is_proxy / is_tor = true | +20 (additional) |
| recent_abuse = true | +15 (additional) |
| leaked = true | +20 (additional) |

### Environment variables
```
IPQS_API_KEY=<from ipqualityscore.com dashboard>
```

---

## TIER 2 — SEON

**Provider:** SEON Technologies
**Website:** https://seon.io
**Cost:** Paid — contact for pricing (usage-based)
**Coverage:** Global
**Use for:** Social/digital footprint lookup — does this email/phone have a real online presence?

### What it provides
- Social media profile existence check (LinkedIn, Facebook, Instagram, Twitter, etc.)
- Email/phone age and activity signals
- Risk score based on digital footprint depth
- AML / KYC signals

### Key insight for Fraud Sentinel
A fraudulent identity often has a very thin or zero digital footprint — no social profiles,
no online history, brand new email. SEON detects this. A legitimate identity usually has
years of digital presence across multiple platforms.

### Signal mapping
| SEON Signal | Risk Score Contribution |
|------------|------------------------|
| fraud_score > 80 | +30 |
| No social profiles found | +20 |
| Email created < 7 days ago | +25 |
| AML flag | +40 |

### Environment variables
```
SEON_API_KEY=<from seon.io dashboard>
SEON_API_URL=https://api.seon.io/SeonRestService/fraud-api/v2/
```

---

## TIER 2 — SpyCloud

**Provider:** SpyCloud
**Website:** https://spycloud.com
**Cost:** Enterprise — contact for pricing
**Coverage:** Global darknet / breach intelligence
**Use for:** Has this identity been exposed in a breach? Are their credentials circulating on darknet?

### What it provides
- Breach exposure — is email/phone in known data breaches?
- Credential exposure — password hashes, plaintext passwords in darknet
- Cookie/session theft signals — active stolen sessions
- Infostealer malware infection signals

### Key insight for Fraud Sentinel
If an identity's credentials are freshly leaked (especially with active session cookies),
account takeover is imminent or already in progress. SpyCloud surfaces this
an average of **9 months before other providers**.

### Signal mapping
| SpyCloud Signal | Risk Score Contribution |
|----------------|------------------------|
| Active breach exposure (< 30 days) | +35 |
| Credential in darknet | +25 |
| Active stolen session cookie | +45 |
| Infostealer infection signal | +40 |

### Environment variables
```
SPYCLOUD_API_KEY=<from spycloud.com dashboard>
SPYCLOUD_API_URL=https://api.spycloud.io/enterprise-v2/
```

---

## TIER 3 — NPCI MuleHunter.AI

**Provider:** National Payments Corporation of India (NPCI)
**Cost:** Free for certified NPCI partner banks / TSPs
**Coverage:** India — UPI transaction network
**Use for:** Mule account detection in UPI ecosystem

### What it provides
- Real-time risk score per UPI transaction
- Mule account identification (PATTERN-005 graph linkage)
- Transaction pattern analysis across the entire UPI network
- Federated learning — improves without sharing raw customer data

### Access
Available to NPCI certified Technology Service Providers (TSPs).
Register at: https://www.npci.org.in/what-we-do/upi/partner-with-us

### Signal mapping
| NPCI Signal | Risk Score Contribution |
|------------|------------------------|
| Mule account flagged | +50 |
| High-risk transaction pattern | +30 |
| Network anomaly | +20 |

### Environment variables
```
NPCI_TSP_ID=<assigned post NPCI TSP certification>
NPCI_API_KEY=<assigned post NPCI TSP certification>
NPCI_API_URL=<assigned post NPCI TSP certification>
```

---

## Enrichment Orchestration Logic

Run all available Tier 1 providers in parallel. Run Tier 2 if Tier 1 confidence < 0.6.
Run Tier 3 for India UPI transactions always (when NPCI credentials available).

```
function enrich_identity(query):

  signals = []

  // TIER 1 — always, in parallel
  if query.actor_context.ip:
    signals += ipqs.check_ip(query.actor_context.ip)

  if query.target_identity_id contains "@":
    signals += ipqs.check_email(query.target_identity_id)

  if query.target_identity_id matches phone pattern:
    signals += ipqs.check_phone(query.target_identity_id)
    if india_number(query.target_identity_id):
      signals += fri.check_mobile(query.target_identity_id)   // India only

  if query.actor_context.device_id:
    signals += ipqs.check_device(query.actor_context.device_id)

  // TIER 2 — if Tier 1 confidence < 0.6
  tier1_score = sum(signals.score_contributions)
  if tier1_score < 30:
    signals += seon.check_digital_footprint(query.target_identity_id)

  // TIER 3 — India UPI always
  if query.action_type == "payment" and query.source_platform == "upi":
    signals += npci.mule_hunter(query.target_identity_id, query.action_value)

  return signals
```

---

## Privacy & Data Minimisation Rules

1. **Never send PII to external providers unless required** — use hashed identifiers where possible.
2. **Never store raw API responses** — extract only the score/flag fields and store those.
3. **Log every external query** in `fraud_enrichment_log` table in SurrealDB (provider, queried_at, signal extracted).
4. **GDPR / DPDP compliance** — user consent must cover fraud risk scoring before querying external providers.
5. **Fail open** — if an external provider is unavailable, proceed with internal scoring only. Never block a transaction solely because an enrichment API timed out.

---

## SurrealDB — Enrichment Log Table

```surql
CREATE fraud_enrichment_log SET
  log_id          = rand::uuid(),
  query_id        = $query_id,        -- links to fraud_preaction_log
  provider        = $provider,        -- "FRI" | "IPQS" | "SEON" | "SpyCloud" | "NPCI"
  identity_queried= $identity_queried,
  signal_extracted= $signal_extracted, -- only the score/flag, never raw response
  score_contribution = $score_contribution,
  queried_at      = time::now(),
  response_ms     = $response_ms;     -- latency tracking
```

---

## Onboarding Checklist — Data Providers

| Provider | Action | Est. Time |
|----------|--------|-----------|
| FRI (DoT DIU) | Register at dot.gov.in/digital-intelligence-unit | 1–2 weeks (govt approval) |
| IPQS | Sign up at ipqualityscore.com — instant free tier | Minutes |
| NPCI MuleHunter | Apply for TSP certification at npci.org.in | 4–8 weeks |
| SEON | Contact sales at seon.io | 1–3 days |
| SpyCloud | Contact enterprise sales at spycloud.com | 1–2 weeks |

**Start with IPQS** (instant free tier, no approval needed).
**Apply for FRI in parallel** (most important for India, but needs govt registration).
