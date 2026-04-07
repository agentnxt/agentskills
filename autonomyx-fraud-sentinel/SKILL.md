---
name: autonomyx-fraud-sentinel
description: >
  Fraud Detection, Prevention, Reporting, and Public Awareness for Autonomyx. Collects signals from
  agents and users. Detects 7 patterns: scarcity manipulation, dormant identity resurrection, velocity
  spikes, new device anomalies, bad actor networks, time-of-day anomalies, low-value probe transactions.
  SurrealDB active engine — DEFINE EVENTs fire on every write, LIVE SELECT pushes alerts in real time.
  Enriches via FRI (India), IPQS, SEON, SpyCloud, NPCI MuleHunter.AI. Warns on IDENTITY RISK not
  amount — ₹1 to a suspicious identity is flagged. Pre-action scoring: ALLOW/WARN/STRONG_WARN/BLOCK
  in <200ms. Citizen Safety Check: describe a transaction, get a TXN ID — zero PII stored, usable
  as evidence for bank claims, cybercrime.gov.in, or police FIR.
  ALWAYS trigger when: "fraud", "scam", "suspicious", "fake", "impersonation", "dormant account",
  "sudden urgency", "probe transaction", "small payment", "access block" appear; user reports fraud;
  agent submits a signal; or new platform agent is being onboarded.
---

# Autonomyx Fraud Sentinel

A cross-platform fraud intelligence system. Agents report in. Humans report in. The Sentinel detects,
stores, alerts, and broadcasts — then recommends action and, where warranted, signals an access block.

---

## Core Concepts

| Term | Meaning |
|------|---------|
| **Signal** | A raw fraud indicator from an agent or user |
| **Event** | A validated fraud occurrence stored in SurrealDB |
| **Pattern** | A named fraud behaviour template (extensible) |
| **Broadcast** | A public awareness message sent to one or more audiences |
| **Block Signal** | An instruction to revoke or restrict access for an identity |
| **Risk Score** | A real-time 0–100 score returned to an agent before an action executes |
| **Pre-Action Query** | An agent asking "should I allow this?" before executing a high-stakes action |
| **TXN ID** | A simulated transaction reference ID issued to a citizen after a safety check — no PII stored |
| **Safety Check** | A citizen describes a transaction in plain language — Sentinel scores it and issues a TXN ID |

---

## Two Operating Modes

Fraud Sentinel operates in two modes. Both are always active.

```
MODE A — REACTIVE (post-event)          MODE B — PROACTIVE (pre-action)        MODE C — CITIZEN SAFETY CHECK
─────────────────────────────           ──────────────────────────────          ──────────────────────────────
Agent/user reports fraud    →           Agent about to execute action →         Citizen describes transaction →
Sentinel analyses & stores  →           Sentinel scores recipient     →         Sentinel scores in plain English →
Sentinel alerts & broadcasts            Sentinel returns ALLOW/WARN/BLOCK       Issues TXN ID, zero PII stored
```

**Mode B is the primary protection layer.** It intercepts fraud before it happens —
exactly how HDFC warns before a payment goes through. Mode A captures what Mode B misses.
**Mode C is the public-facing protection layer** — any citizen can check a transaction
before proceeding, without sharing any phone number or personal data.

> ⚡ **SurrealDB is the active fraud engine.** Agents write transactions using `RELATE`.
> `DEFINE EVENT` rules fire automatically on every write — no manual scoring calls needed.
> `LIVE SELECT` pushes alerts to agents in real time. The database detects fraud, not the agent.

---

## Core Design Principle — Identity Risk Over Amount

> ⚠️ **Fraud Sentinel does NOT use transaction amount as the primary warning threshold.**
>
> A ₹1 transfer to a suspicious identity is as dangerous as a ₹1,00,000 transfer.
> Traditional bank systems (e.g. HDFC) warn at ₹5,000+ — this creates a deliberate
> blind spot that fraudsters exploit via low-value probe transactions.
>
> **Fraud Sentinel warns based on recipient/sender identity risk. Amount is a secondary signal only.**

---

## Fraud Pattern Registry (v2)

Patterns are stored in `references/patterns.md`. New patterns are appended there over time.
Always load `references/patterns.md` before analysis.

### Current Patterns (summary)

| ID | Name | Risk Level |
|----|------|-----------|
| PATTERN-001 | Scarcity Manipulation | Medium → High |
| PATTERN-002 | Dormant Identity Resurrection | High |
| PATTERN-003 | Velocity Spike | Medium → Critical |
| PATTERN-004 | New Device or Location on High-Stakes Action | High |
| PATTERN-005 | Known Bad Actor Network (Graph Linkage) | Medium → Critical |
| PATTERN-006 | Time-of-Day Anomaly | Medium → High |
| PATTERN-007 | Low-Value Probe Transaction | Low → High |

> 📌 Full pattern details (triggers, indicators, notes) are in `references/patterns.md`.
> Always load that file before running any analysis. Never rely on this summary alone.

---

## Workflow B — Pre-Action Risk Scoring (Proactive)

An agent calls this workflow BEFORE executing any high-stakes action (payment, credential
request, data share, link click, file transfer). The Sentinel scores the recipient/target
identity in real time and returns a decision.

### B1 · Pre-Action Query Input

Agent sends this payload before executing an action:

```json
{
  "query_type": "pre_action",
  "agent_id": "string",
  "source_platform": "string",
  "actor_identity_id": "string",        // who is performing the action
  "target_identity_id": "string",       // who/what is the recipient/target
  "action_type": "payment|credential_request|link|file|message|other",
  "action_value": "string|number|null", // amount, URL, filename, etc.
  "actor_context": {
    "last_active": "ISO8601|null",
    "device_id": "string|null",
    "ip": "string|null",
    "location": "string|null",
    "action_timestamp": "ISO8601"
  }
}
```

### B2 · Enrich Identity (External Data)

Before internal scoring, enrich the target identity using external data providers.
Load `references/data-providers.md` for full provider details, API specs, and signal mapping.

```
Tier 1 (always): IPQS → IP / email / phone / device score
                 FRI  → India mobile number risk (free govt API)
Tier 2 (if Tier 1 score < 30): SEON → digital footprint depth
Tier 3 (India UPI only): NPCI MuleHunter.AI → mule account detection
```

Run all applicable Tier 1 providers in parallel. Target total enrichment time < 100ms.
Store enrichment signals in `fraud_enrichment_log` (see data-providers.md for schema).
Never store raw API responses — extract score/flag only.

### B3 · Scoring Engine

Run ALL checks in parallel. Each check contributes to a composite risk score (0–100).
External enrichment signals from B2 feed directly into this scoring table.

| Check | Source | Max Score Contribution |
|-------|--------|----------------------|
| FRI: Very High risk mobile | External / FRI | +45 |
| IPQS: Fraud score 85–100 | External / IPQS | +40 |
| SpyCloud: Active stolen session | External / SpyCloud | +45 |
| NPCI: Mule account flagged | External / NPCI | +50 |
| SEON: No digital footprint | External / SEON | +20 |
| Target identity in fraud_event records | PATTERN-005 | +40 |
| Target identity dormant then active | PATTERN-002 | +25 |
| Actor on new device + high-stakes action | PATTERN-004 | +20 |
| Action at unusual time for actor | PATTERN-006 | +15 |
| Action value ≤ ₹500 / $5 to unknown target | PATTERN-007 | +10 |
| Velocity: actor has 3+ actions in last 10min | PATTERN-003 | +20 |
| Target linked to known bad actor (2-hop) | PATTERN-005 | +30 |
| Scarcity language in associated messages | PATTERN-001 | +15 |

**Composite score → Decision:**

| Score | Decision | Agent Action |
|-------|----------|-------------|
| 0–20 | ✅ ALLOW | Proceed silently |
| 21–50 | ⚠️ WARN | Show user a warning, allow override |
| 51–79 | 🔶 STRONG WARN | Show prominent warning, require explicit confirmation |
| 80–100 | 🚫 BLOCK | Block action, log event, notify admin |

### B4 · Pre-Action Response Payload

Return to the agent immediately (target: <200ms):

```json
{
  "query_id": "uuid",
  "decision": "ALLOW|WARN|STRONG_WARN|BLOCK",
  "risk_score": 0-100,
  "risk_level": "Low|Medium|High|Critical",
  "patterns_matched": ["PATTERN-XXX"],
  "warning_message": "string|null",     // shown to end user if WARN/STRONG_WARN
  "block_reason": "string|null",        // shown to end user if BLOCK
  "confidence": 0.0-1.0,
  "scored_at": "ISO8601",
  "log_event": true|false               // whether to store a fraud_event record
}
```

**Warning message** (shown to end user — plain language, no jargon):
- WARN: "We noticed something unusual about this transaction. Please verify the recipient before proceeding."
- STRONG_WARN: "This recipient has been flagged for suspicious activity. We strongly recommend you do not proceed."
- BLOCK: "This action has been blocked to protect your account. If you believe this is an error, contact support."

### B5 · Store Pre-Action Log

Always store every pre-action query in SurrealDB — even ALLOW decisions.
This builds the identity behaviour baseline used for future scoring.

```surql
CREATE fraud_preaction_log SET
  query_id          = rand::uuid(),
  agent_id          = $agent_id,
  source_platform   = $source_platform,
  actor_identity_id = $actor_identity_id,
  target_identity_id= $target_identity_id,
  action_type       = $action_type,
  action_value      = $action_value,
  decision          = $decision,
  risk_score        = $risk_score,
  patterns_matched  = $patterns_matched,
  confidence        = $confidence,
  queried_at        = time::now();
```

> Pre-action logs are **never deleted** — they are the behavioural baseline.
> Over time, ALLOW decisions build a trust profile for each identity.
> Sudden deviation from baseline auto-increases risk score (PATTERN-006 logic).

---

## Workflow A — Reactive (Post-Event)

### Step 1 · Receive Signal

> ⚡ **Preferred path:** Platform agents write directly to SurrealDB using `RELATE` (graph edge).
> `DEFINE EVENT` rules detect fraud automatically. Only use this manual workflow for
> unstructured reports (user chat messages, emails, manual submissions).

Signals arrive from two sources:

**A. Autonomyx Agent — Graph Write (preferred, automatic)**

Agent calls SurrealDB directly:
```surql
-- Register/update identity (triggers EVENT-001, EVENT-005 if device/dormancy detected)
INSERT INTO identity {
  platform: "whatsapp", platform_id: $id,
  device_id: $device, ip: $ip,
  last_active_at: time::now()
} ON DUPLICATE KEY UPDATE
  last_active_at = time::now(), device_id = $device, ip = $ip;

-- Record transaction (triggers EVENT-002, EVENT-003, EVENT-004, EVENT-006)
RELATE identity:$sender -> sent -> identity:$recipient
  SET amount = $amount, currency = "INR", platform = "upi";
```
Events fire. Alerts are created. Agent receives via LIVE SELECT. No manual call to Sentinel.

**B. Manual Agent Report** (for non-transactional signals — e.g. suspicious message content)
```
{
  source_platform: string,
  agent_id: string,
  identity_id: string,
  signal_type: string,           // pattern ID or "unknown"
  raw_evidence: string,
  timestamp: ISO8601,
  agent_confidence: 0.0–1.0
}
```

**C. User-Reported Fraud**
```
{
  reporter_id: string,
  platform: string,
  reported_identity: string,
  description: string,
  evidence_links: [string],
  timestamp: ISO8601
}
```

If input is unstructured (plain chat message), extract fields as best as possible.
Ask for clarification only if platform and description are both missing.

---

### Step 2 · Pattern Match

Load `references/patterns.md`. Check the signal against all known patterns.

For each pattern match:
- Assign the pattern ID
- Set risk level (Low / Medium / High / Critical)
- Note which indicators were matched
- Flag as `UNMATCHED` if no pattern fits — store anyway for future pattern discovery

**Confidence scoring:**
- Agent report alone: base confidence = agent_confidence value
- User report alone: base confidence = 0.5
- Both sources agree: confidence = min(0.9, average + 0.2)
- 3+ independent reports on same identity: escalate to Critical

---

### Step 3 · Store to SurrealDB

Store every signal — matched or not. Use the SurrealDB REST API (cloud URL from environment/config).

**Record schema:**

```surql
CREATE fraud_event SET
  event_id        = rand::uuid(),
  source_platform = $source_platform,
  agent_id        = $agent_id,           -- null if user-reported
  reporter_id     = $reporter_id,        -- null if agent-reported
  identity_id     = $identity_id,
  pattern_id      = $pattern_id,         -- null if UNMATCHED
  risk_level      = $risk_level,
  confidence      = $confidence,
  raw_evidence    = $raw_evidence,
  indicators_matched = $indicators_matched,
  status          = "open",
  created_at      = time::now(),
  updated_at      = time::now(),
  broadcasts_sent = [],
  block_issued    = false;
```

Also store raw signal in `fraud_signal` table (immutable audit log, never deleted).

---

### Step 4 · Generate Outputs

Always generate all applicable outputs. Do not skip any unless explicitly instructed.

#### 4a · Alert Summary
A concise internal alert (2–4 sentences):
- What was detected
- Which identity/platform
- Risk level and confidence
- Event ID for tracking

#### 4b · Recommended Action Steps
Tiered by risk level:

| Risk | Actions |
|------|---------|
| Low | Monitor. Add to watchlist. Log only. |
| Medium | Notify platform admin. Request identity verification. Increase monitoring frequency. |
| High | Suspend identity pending review. Notify all affected users. Escalate to internal team. |
| Critical | Immediate access block. Notify government/authorities. Broadcast public awareness. Preserve all evidence. |

Always output as a numbered checklist.

#### 4c · Access Block Signal
Issue when risk = High or Critical, OR when confidence ≥ 0.85.

```
BLOCK SIGNAL
identity_id: <value>
platform: <value>
reason: <pattern_id + summary>
issued_at: <timestamp>
issued_by: autonomyx-fraud-sentinel
event_id: <value>
escalation_level: <High|Critical>
```

The platform agent receiving this signal is responsible for executing the block.
If no agent is connected yet for the platform, flag as `PENDING_AGENT` and store in SurrealDB.

#### 4d · Public Awareness Broadcast

Draft tailored messages for each applicable audience. Tone and detail vary by audience:

| Audience | Tone | Detail Level | Channel |
|----------|------|-------------|---------|
| End users of platform | Friendly, protective | High — specific warning | In-app / email |
| General public (social) | Clear, non-alarmist | Medium — general warning | Twitter/X, LinkedIn, Facebook |
| Subscribed watchers/admins | Technical | High — full details | Email / webhook |
| Internal team | Direct | Full — all metadata | Slack / internal |
| Government & local authorities | Formal | High — evidence-focused | Email / official report |

For each audience, produce:
- Subject / headline
- Body (platform-appropriate length)
- Recommended send time (immediate for High/Critical, scheduled for Medium/Low)

Always use `references/broadcast-templates.md` as a starting point and customise per event.

---

### Step 5 · Update SurrealDB Record

After outputs are generated:

```surql
UPDATE fraud_event SET
  broadcasts_sent = $audiences_notified,
  block_issued    = $block_issued,
  status          = "actioned",
  updated_at      = time::now()
WHERE event_id = $event_id;
```

---

## Onboarding a New Platform Agent

When a new Autonomyx agent is being connected to the Sentinel:

1. Register the agent in SurrealDB:
```surql
CREATE fraud_agent SET
  platform       = $platform,
  agent_version  = $version,
  registered_at  = time::now(),
  status         = "active",
  signal_count   = 0;
```

2. Apply the full active schema from `references/surreal-schema.md` if not already applied.
   This creates all tables, DEFINE EVENTs, and indexes.

3. Provide the agent with:
   - SurrealDB endpoint + credentials
   - `RELATE` syntax for recording transactions (see surreal-schema.md Step 6)
   - `LIVE SELECT` subscription query for receiving alerts in real time
   - List of current pattern IDs (for manual signal reporting only)

4. Start the LIVE SELECT subscription on the agent:
```surql
LIVE SELECT * FROM alert
WHERE platform = $platform AND status = "open";
```

5. Confirm two-way connectivity:
   - Agent writes a test `RELATE` transaction
   - Verify an alert is received via LIVE SELECT within 200ms

---

## Configuration Reference

All config is environment-based. Never hardcode credentials.

| Key | Description |
|-----|-------------|
| `SURREAL_URL` | SurrealDB cloud endpoint |
| `SURREAL_NS` | Namespace (e.g. `autonomyx`) |
| `SURREAL_DB` | Database name (e.g. `fraud_sentinel`) |
| `SURREAL_USER` | Auth user |
| `SURREAL_PASS` | Auth password |
| `BROADCAST_WEBHOOK_ADMIN` | Webhook URL for admin/watcher alerts |
| `BROADCAST_WEBHOOK_INTERNAL` | Webhook URL for internal team |
| `FRI_API_URL` | DoT DIU Financial Fraud Risk Indicator endpoint |
| `FRI_API_KEY` | DoT DIU API key (post registration) |
| `IPQS_API_KEY` | IPQualityScore API key |
| `SEON_API_KEY` | SEON fraud API key (Tier 2) |
| `SPYCLOUD_API_KEY` | SpyCloud darknet intelligence key (Tier 2) |
| `NPCI_TSP_ID` | NPCI TSP certification ID (India UPI) |
| `NPCI_API_KEY` | NPCI MuleHunter API key |
| `NPCI_API_URL` | NPCI MuleHunter endpoint |

---

## Reference Files

| File | Purpose | When to load |
|------|---------|-------------|
| `references/patterns.md` | Full pattern registry | Always — before any analysis |
| `references/broadcast-templates.md` | Message templates per audience | When generating broadcasts |
| `references/surreal-queries.md` | Utility queries (aggregates, lookups) | When reading/writing data |
| `references/surreal-schema.md` | Full active schema — tables, events, live queries, graph traversal | Always load when setting up SurrealDB or onboarding a new agent |
| `references/authority-contacts.md` | Gov/authority contact directory | When escalating Critical events |
| `references/data-providers.md` | External enrichment providers, API specs, signal mapping | Always — load before B2 enrichment step |

---

## Workflow C — Citizen Safety Check (Public-Facing)

A citizen describes a transaction they are about to make in plain language.
No phone numbers, UPI IDs, or personal identifiers required.
Sentinel analyses the description, scores the risk, and issues a **TXN ID** as evidence.

### C1 · Accept Plain Language Description

The citizen submits a free-text description. Examples:

> "I'm about to pay ₹5,000 to someone on WhatsApp who says they're selling a second-hand phone"
> "A person on Instagram said I won a prize and needs ₹200 to release it"
> "My friend's number messaged me asking for ₹10,000 urgently, says they're in trouble"

No structured input required. Extract signals from natural language:

```
signals_to_extract:
  platform:          where the interaction happened (WhatsApp, Instagram, email, phone call...)
  amount:            transaction amount if mentioned (any currency)
  relationship:      stranger / known contact / impersonation claim / authority figure
  urgency:           is there time pressure? ("urgent", "today only", "last chance")
  prize_or_reward:   claim of winning, reward, refund, cashback
  request_type:      payment / OTP / credential / personal info / click link
  contact_method:    how they were contacted (unsolicited / responded to ad / inbound call)
  emotional_pressure: fear / excitement / sympathy / authority
```

If the description is too vague to extract any signals, ask one clarifying question only.
Never ask for phone numbers, names, or any identifying information.

---

### C2 · Pattern Match Against Description

Load `references/patterns.md`. Match extracted signals against all patterns.

| Signal | Pattern triggered |
|--------|-----------------|
| Urgency + stranger + payment | PATTERN-001 (scarcity) |
| Unsolicited contact + prize/reward | PATTERN-001 (scarcity manipulation) |
| Friend's number acting strangely | PATTERN-002 (dormant/hijacked identity) |
| Multiple payment requests in context | PATTERN-003 (velocity) |
| Low amount first, escalating | PATTERN-007 (probe transaction) |
| "Authority" claiming refund/fine | PATTERN-001 + social engineering |
| OTP / credential request | PATTERN-004 (account takeover attempt) |

Assign:
- `patterns_matched[]` — list of pattern IDs
- `risk_level` — Low / Medium / High / Critical
- `confidence` — 0.0–1.0 (lower for vague descriptions)
- `fraud_type` — human-readable name: "Prize scam", "UPI fraud", "Impersonation", etc.

---

### C3 · Generate TXN ID

Issue a unique, traceable reference ID. Format:

```
TXN-AX-{YEAR}-{4-CHAR-ALPHANUM}
Example: TXN-AX-2026-7F3K
```

Rules:
- Collision-resistant — check SurrealDB before issuing
- Human-readable — easy to quote over phone or in an FIR
- No PII encoded in the ID — it is a random reference only
- Valid for 90 days — after which it is archived but not deleted

---

### C4 · Store Safety Check (No PII)

```surql
CREATE fraud_safety_check SET
  txn_id           = $txn_id,
  description_hash = crypto::sha256($description),  -- hash only, never raw text
  signals_extracted = $signals_extracted,
  patterns_matched  = $patterns_matched,
  risk_level        = $risk_level,
  confidence        = $confidence,
  fraud_type        = $fraud_type,
  platform          = $platform,
  amount            = $amount,
  outcome           = "pending",   -- updated if user reports fraud later
  created_at        = time::now(),
  expires_at        = time::now() + 90d;
```

**Never store the raw description text** — store only the hash and extracted signals.
This ensures zero PII in the database even if the user accidentally included a phone number.

---

### C5 · Generate Citizen Response

Return a clear, plain-English response. No jargon. Designed for any literacy level.

#### Response template — HIGH / CRITICAL risk

```
⚠️  HIGH RISK — We recommend you do NOT proceed.

What we detected:
  [fraud_type] — [1-sentence plain English explanation]

Warning signs in your description:
  • [signal 1 in plain English]
  • [signal 2 in plain English]
  • [signal 3 in plain English]

Your reference ID: TXN-AX-2026-7F3K
Keep this safe. If you are defrauded, quote this ID when:
  • Calling your bank's fraud helpline
  • Reporting on cybercrime.gov.in
  • Filing a police complaint

What to do now:
  1. Do not make the payment or share any OTP
  2. Do not click any links they sent you
  3. If this came from a known contact's number, call them on a different number to verify
  4. Report the fraudster: cybercrime.gov.in or call 1930

This is a risk indicator, not a legal finding. Always use your own judgment.
```

#### Response template — MEDIUM risk

```
⚠️  CAUTION — Proceed carefully.

[fraud_type] — [explanation]

We found some warning signs but cannot be certain this is fraud.
Double-check before proceeding.

Your reference ID: TXN-AX-2026-7F3K

Steps to verify:
  • [context-specific verification step]
  • [context-specific verification step]

If something feels wrong, trust your instinct and report: 1930
```

#### Response template — LOW risk

```
✅  LOW RISK — No major warning signs detected.

Your reference ID: TXN-AX-2026-7F3K

This does not guarantee the transaction is safe.
If anything feels wrong, call 1930 before proceeding.
```

---

### C6 · Outcome Tracking (Optional)

If the user later reports they were defrauded despite a LOW/MEDIUM result:

```surql
UPDATE fraud_safety_check SET
  outcome    = "fraud_occurred",
  updated_at = time::now()
WHERE txn_id = $txn_id;
```

This feeds back into pattern refinement — improving future scoring for similar descriptions.

---

## TXN ID as Evidence

The TXN ID serves multiple downstream purposes:

| Use | How |
|-----|-----|
| Bank fraud claim | Quote TXN ID — shows due diligence before transacting |
| cybercrime.gov.in report | Include in complaint — pre-documented risk assessment |
| Police FIR | Attach as evidence — Sentinel issued a warning |
| Autonomyx internal | Links safety check to any subsequent fraud event |

---

## Extensibility Rules

1. **New patterns** → append to `references/patterns.md` with a new PATTERN-XXX ID. Never delete old patterns.
   Then add a corresponding `DEFINE EVENT` in `references/surreal-schema.md`.
2. **New platforms** → onboard via the agent registration flow. No changes to core skill needed.
3. **New audiences** → add a row to the broadcast table above and a template in `references/broadcast-templates.md`.
4. **New outputs** → add a Step 4x section and update the SurrealDB record schema accordingly.
5. **New ML model** → export as ONNX, load via SurrealML (`DEFINE MODEL`), call via `ml::predict()` in events or queries. See surreal-schema.md Step 7.
