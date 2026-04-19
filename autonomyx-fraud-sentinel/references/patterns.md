# Autonomyx Fraud Sentinel — Pattern Registry

> This file is the authoritative, append-only list of fraud patterns.
> Never delete or renumber a pattern. Add new ones at the bottom.
> Each pattern must have: ID, name, description, triggers, risk level, indicators, notes.

---

## PATTERN-001 · Scarcity Manipulation

**Description:** Artificial urgency created through scarcity claims to pressure a target into
a hasty decision — financial, credential-sharing, or behavioural.

**Triggers:**
- First scarcity message from an account with no prior scarcity history
- Spike: 3+ accounts posting similar scarcity language within a 1-hour window
- Scarcity claim cannot be verified against any real inventory or deadline

**Risk Level:** Medium (isolated) → High (coordinated)

**Indicators:**
- Language: "only X left", "expires soon", "limited offer", "act now", "last chance"
- Account age > 30 days with zero prior scarcity messaging
- Identical or near-identical text across multiple accounts
- Scarcity paired with a payment or credential request

**Notes:** Often precedes phishing or payment fraud. Escalate if coordinated.

---

## PATTERN-002 · Dormant Identity Resurrection

**Description:** A previously inactive account, agent, or identity suddenly reactivates —
often with changed profile metadata and high-stakes first actions.

**Triggers:**
- Identity inactive for ≥ 14 days, then becomes active
- First post-resurrection action is financial, credential-seeking, or urgency-driven
- Profile metadata (name, avatar, bio, contact) changed within 24h of reactivation

**Risk Level:** High

**Indicators:**
- Last-active gap ≥ 14 days
- New device fingerprint or IP on reactivation
- Profile changes within 24h of reactivation
- First message requests money, login, OTP, or personal data
- Account was previously flagged (any status)

**Notes:** Common in account takeover and impersonation attacks. Cross-reference with
PATTERN-003 (Impersonation) when profile changes are detected.

---

## PATTERN-003 · Velocity Spike

**Description:** An identity initiates an unusually high number of transactions, messages,
or actions in a short time window — far outside their established baseline behaviour.

**Triggers:**
- 3+ payment attempts within 10 minutes from the same identity
- Message volume 5x above the identity's 7-day average within 1 hour
- Rapid sequential actions targeting multiple different recipients

**Risk Level:** Medium (isolated) → Critical (cross-account)

**Indicators:**
- Transaction or action count exceeds 3x the identity's rolling 7-day average
- Multiple failed attempts followed by a successful one (probing)
- Same amount sent to multiple different recipients in quick succession
- Actions span multiple platforms simultaneously

**Notes:** Often indicates automated fraud tooling or account takeover. Combine with
PATTERN-004 (new device) for higher confidence. Escalate immediately if cross-account.

---

## PATTERN-004 · New Device or Location on High-Stakes Action

**Description:** An identity accesses a platform from a new device fingerprint, IP address,
or geographic location — and immediately performs a high-stakes action (payment, credential
change, data export) without any warm-up activity.

**Triggers:**
- New device/IP detected AND first action is financial or credential-related
- Geographic location change of >500km since last session
- Device fingerprint not seen in the identity's last 30 days of activity

**Risk Level:** High

**Indicators:**
- New device fingerprint on first high-stakes action
- IP geolocation mismatch vs. identity's established location pattern
- No warm-up browsing — goes straight to payment or settings
- Login time outside identity's normal active hours
- VPN or Tor exit node detected

**Notes:** Standalone new device is Medium risk. New device + immediate high-stakes action
= High. Cross-reference with PATTERN-002 (dormant resurrection) — both often occur together
in account takeover scenarios.

---

## PATTERN-005 · Known Bad Actor Network (Graph Linkage)

**Description:** An identity has a direct or indirect connection to a previously confirmed
fraud actor — through shared payment destinations, referral chains, device fingerprints,
or communication patterns.

**Triggers:**
- Identity sends funds to or receives funds from a flagged identity
- Identity shares a device fingerprint with a flagged identity
- Identity was referred by or refers others to a flagged identity
- 2-hop graph connection to a confirmed fraud event

**Risk Level:** Medium (2-hop) → High (direct connection) → Critical (confirmed mule)

**Indicators:**
- Shared UPI ID, bank account, or wallet address with a flagged actor
- Shared device ID or cookie fingerprint with a flagged actor
- Referral chain traces back to a known fraud campaign
- Funds pass through identity without retention (immediate re-transfer) — mule pattern

**Notes:** Requires graph traversal across fraud_event records. Query SurrealDB for
shared identity_id, device_id, or payment_destination fields. Even if the identity
itself has no direct fraud history, network linkage is high-signal.

---

## PATTERN-006 · Time-of-Day Anomaly

**Description:** An identity performs high-stakes actions at times significantly outside
their established active hours — a strong signal of account takeover or automated fraud.

**Triggers:**
- High-stakes action (payment, credential change) between midnight and 5am local time
  for an identity that has never been active in that window
- Action timestamp falls outside the identity's 30-day active hour distribution by >3 sigma
- Sudden shift in active timezone without prior travel signal

**Risk Level:** Medium (time anomaly alone) → High (combined with new device or dormancy)

**Indicators:**
- Action time outside identity's established active hours (derived from 30-day history)
- No prior activity in the same time window across 30+ days of history
- Timezone of action inconsistent with identity's registered location
- Rapid session — login, action, logout in under 60 seconds at unusual hour

**Notes:** Standalone time anomaly = Medium. Combine with PATTERN-004 (new device) or
PATTERN-002 (dormant) to escalate to High/Critical. Banks like HDFC use this as a
primary signal — Fraud Sentinel should too.

---

## PATTERN-007 · Low-Value Probe Transaction

**Description:** A fraudster or compromised account sends a very small amount (₹1–₹500 or
equivalent) to a target or through a mule — deliberately staying below bank alert thresholds
to test liveness, build transaction history, or establish trust before a large-value attack.

**Triggers:**
- Transaction of ≤ ₹500 (or currency equivalent) to a new, unverified recipient
- Series of small transactions to the same recipient building up over days
- Small transaction to a recipient who has never interacted with the identity before
- Small amount sent immediately after account reactivation (PATTERN-002)

**Risk Level:** Low (single probe) → High (series building toward large transaction)

**Insight:** Most bank fraud systems (including HDFC) set amount-based thresholds —
e.g. warn at ₹5,000+. This creates a blind spot. **Fraud Sentinel warns based on
recipient identity risk, not transaction amount.** A ₹1 transfer to a suspicious
identity is as dangerous as a ₹1,00,000 transfer.

**Indicators:**
- Transaction amount ≤ ₹500 to a first-time recipient
- Recipient identity has fraud flags or network linkage (PATTERN-005)
- Pattern of escalating small amounts to same recipient over 3–7 days
- Small transaction immediately followed by a request for confirmation ("did you get it?")
  — social engineering to establish trust

**Notes:** This is the most under-detected pattern in traditional banking fraud systems.
Fraud Sentinel should flag ANY transaction — regardless of amount — when the recipient
identity carries risk signals. Amount is irrelevant. Identity risk is everything.

---

<!-- NEW PATTERNS APPENDED BELOW THIS LINE -->
