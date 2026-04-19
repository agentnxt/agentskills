# Autonomyx Fraud Sentinel — SurrealDB Active Schema

> This is the authoritative schema. Run in order on a fresh namespace.
> Namespace: autonomyx | Database: fraud_sentinel
> SurrealDB treats edges as first-class records — transactions are modelled
> as graph relationships, not flat rows. Events fire automatically on writes.

---

## Step 1 — Define Namespace & Database

```surql
DEFINE NAMESPACE autonomyx;
USE NS autonomyx;
DEFINE DATABASE fraud_sentinel;
USE DB fraud_sentinel;
```

---

## Step 2 — Define Tables

### identity
Every account, agent, user, or entity on any platform.

```surql
DEFINE TABLE identity SCHEMAFULL;

DEFINE FIELD platform        ON identity TYPE string;
DEFINE FIELD platform_id     ON identity TYPE string;
DEFINE FIELD display_name    ON identity TYPE option<string>;
DEFINE FIELD created_at      ON identity TYPE datetime DEFAULT time::now();
DEFINE FIELD last_active_at  ON identity TYPE datetime DEFAULT time::now();
DEFINE FIELD device_id       ON identity TYPE option<string>;
DEFINE FIELD ip              ON identity TYPE option<string>;
DEFINE FIELD risk_score      ON identity TYPE number  DEFAULT 0;
DEFINE FIELD risk_level      ON identity TYPE string  DEFAULT "Low";
DEFINE FIELD flags           ON identity TYPE array   DEFAULT [];
DEFINE FIELD status          ON identity TYPE string  DEFAULT "active";

DEFINE INDEX idx_platform_id ON identity FIELDS platform, platform_id UNIQUE;
DEFINE INDEX idx_risk        ON identity FIELDS risk_level;
```

---

### sent (graph edge — transaction)
Every transaction is a directed edge: `identity:A -> sent -> identity:B`

```surql
DEFINE TABLE sent SCHEMAFULL TYPE RELATION IN identity OUT identity;

DEFINE FIELD amount      ON sent TYPE number;
DEFINE FIELD currency    ON sent TYPE string DEFAULT "INR";
DEFINE FIELD platform    ON sent TYPE string;
DEFINE FIELD channel     ON sent TYPE string;   -- "upi" | "bank" | "wallet" | "crypto"
DEFINE FIELD created_at  ON sent TYPE datetime DEFAULT time::now();
DEFINE FIELD metadata    ON sent TYPE object   DEFAULT {};

DEFINE INDEX idx_sent_time ON sent FIELDS created_at;
```

---

### alert
Auto-created by DEFINE EVENTs. Never written manually by agents.

```surql
DEFINE TABLE alert SCHEMAFULL;

DEFINE FIELD pattern_id      ON alert TYPE string;
DEFINE FIELD identity        ON alert TYPE record<identity>;
DEFINE FIELD risk_level      ON alert TYPE string;
DEFINE FIELD confidence      ON alert TYPE number;
DEFINE FIELD evidence        ON alert TYPE object;
DEFINE FIELD status          ON alert TYPE string DEFAULT "open";
DEFINE FIELD created_at      ON alert TYPE datetime DEFAULT time::now();
DEFINE FIELD actioned_at     ON alert TYPE option<datetime>;
DEFINE FIELD platform        ON alert TYPE string;

DEFINE INDEX idx_alert_status   ON alert FIELDS status;
DEFINE INDEX idx_alert_identity ON alert FIELDS identity;
DEFINE INDEX idx_alert_pattern  ON alert FIELDS pattern_id;
```

---

### fraud_agent
Registered platform agents.

```surql
DEFINE TABLE fraud_agent SCHEMAFULL;

DEFINE FIELD platform       ON fraud_agent TYPE string;
DEFINE FIELD agent_version  ON fraud_agent TYPE string;
DEFINE FIELD status         ON fraud_agent TYPE string DEFAULT "active";
DEFINE FIELD registered_at  ON fraud_agent TYPE datetime DEFAULT time::now();
DEFINE FIELD signal_count   ON fraud_agent TYPE number DEFAULT 0;

DEFINE INDEX idx_agent_platform ON fraud_agent FIELDS platform UNIQUE;
```

---

### fraud_safety_check
Citizen safety checks — zero PII stored.

```surql
DEFINE TABLE fraud_safety_check SCHEMAFULL;

DEFINE FIELD txn_id             ON fraud_safety_check TYPE string;
DEFINE FIELD description_hash   ON fraud_safety_check TYPE string;
DEFINE FIELD signals_extracted  ON fraud_safety_check TYPE object;
DEFINE FIELD patterns_matched   ON fraud_safety_check TYPE array;
DEFINE FIELD risk_level         ON fraud_safety_check TYPE string;
DEFINE FIELD confidence         ON fraud_safety_check TYPE number;
DEFINE FIELD fraud_type         ON fraud_safety_check TYPE string;
DEFINE FIELD platform           ON fraud_safety_check TYPE option<string>;
DEFINE FIELD amount             ON fraud_safety_check TYPE option<number>;
DEFINE FIELD outcome            ON fraud_safety_check TYPE string DEFAULT "pending";
DEFINE FIELD created_at         ON fraud_safety_check TYPE datetime DEFAULT time::now();
DEFINE FIELD expires_at         ON fraud_safety_check TYPE datetime
    DEFAULT time::now() + 90d;

DEFINE INDEX idx_txn_id ON fraud_safety_check FIELDS txn_id UNIQUE;
```

---

## Step 3 — Define Events (Active Fraud Detection)

These fire automatically on every write. No agent needs to call Sentinel.
The database IS the fraud engine.

---

### EVENT-001 · Dormant Identity Resurrection (PATTERN-002)
Fires when an identity record is updated (last_active_at changes).
Checks if the identity was dormant for 14+ days and is now active.

```surql
DEFINE EVENT detect_dormant_resurrection
ON TABLE identity
WHEN $event = "UPDATE"
  AND $before.last_active_at < time::now() - 14d
  AND $after.last_active_at >= time::now() - 5m
THEN {
  CREATE alert SET
    pattern_id  = "PATTERN-002",
    identity    = $after.id,
    platform    = $after.platform,
    risk_level  = "High",
    confidence  = 0.85,
    evidence    = {
      last_active_before : $before.last_active_at,
      reactivated_at     : $after.last_active_at,
      dormant_days       : math::floor(
        duration::secs(time::now() - $before.last_active_at) / 86400
      ),
      device_changed     : $before.device_id != $after.device_id,
      ip_changed         : $before.ip != $after.ip
    };
};
```

---

### EVENT-002 · Mule Account Detection (PATTERN-005)
Fires on every new `sent` edge.
Catches accounts less than 1 day old receiving 3+ large payments.

```surql
DEFINE EVENT detect_mule_account
ON TABLE sent
WHEN $event = "CREATE"
THEN {
  LET $recipient = $after.out;

  IF time::now() - $recipient.created_at < 1d
    AND $recipient<-sent.len() > 2
    AND math::sum($recipient<-sent.amount) > 40000
  {
    CREATE alert SET
      pattern_id  = "PATTERN-005",
      identity    = $recipient,
      platform    = $after.platform,
      risk_level  = "Critical",
      confidence  = 0.92,
      evidence    = {
        account_age_hours  : math::floor(
          duration::secs(time::now() - $recipient.created_at) / 3600
        ),
        inbound_tx_count   : $recipient<-sent.len(),
        total_received     : math::sum($recipient<-sent.amount),
        latest_sender      : $after.in
      };
  };
};
```

---

### EVENT-003 · Velocity Spike (PATTERN-003)
Fires on every new `sent` edge.
Catches actors sending 3+ transactions within 10 minutes.

```surql
DEFINE EVENT detect_velocity_spike
ON TABLE sent
WHEN $event = "CREATE"
THEN {
  LET $sender        = $after.in;
  LET $recent_count  = (
    SELECT count() AS n FROM sent
    WHERE in = $sender
      AND created_at > time::now() - 10m
  )[0].n;

  IF $recent_count >= 3 {
    CREATE alert SET
      pattern_id  = "PATTERN-003",
      identity    = $sender,
      platform    = $after.platform,
      risk_level  = IF $recent_count >= 6 { "Critical" } ELSE { "High" },
      confidence  = 0.80,
      evidence    = {
        tx_count_last_10m : $recent_count,
        last_amount       : $after.amount,
        channel           : $after.channel
      };
  };
};
```

---

### EVENT-004 · Low-Value Probe (PATTERN-007)
Fires on every new `sent` edge.
Catches small payments to first-time recipients — the ₹1 test.

```surql
DEFINE EVENT detect_probe_transaction
ON TABLE sent
WHEN $event = "CREATE"
  AND $after.amount <= 500
THEN {
  LET $sender    = $after.in;
  LET $recipient = $after.out;

  LET $prior_txns = (
    SELECT count() AS n FROM sent
    WHERE in = $sender AND out = $recipient
  )[0].n;

  IF $prior_txns = 1 {   -- this is the very first transaction between them
    LET $recipient_risk = (SELECT risk_level FROM ONLY $recipient);

    IF $recipient_risk.risk_level IN ["High", "Critical"] {
      CREATE alert SET
        pattern_id  = "PATTERN-007",
        identity    = $sender,
        platform    = $after.platform,
        risk_level  = "High",
        confidence  = 0.75,
        evidence    = {
          probe_amount    : $after.amount,
          recipient       : $recipient,
          recipient_risk  : $recipient_risk.risk_level,
          first_contact   : true
        };
    };
  };
};
```

---

### EVENT-005 · New Device on High-Stakes Action (PATTERN-004)
Fires when identity is updated with a new device or IP.

```surql
DEFINE EVENT detect_new_device
ON TABLE identity
WHEN $event = "UPDATE"
  AND ($before.device_id != $after.device_id
    OR $before.ip != $after.ip)
THEN {
  CREATE alert SET
    pattern_id  = "PATTERN-004",
    identity    = $after.id,
    platform    = $after.platform,
    risk_level  = "Medium",
    confidence  = 0.65,
    evidence    = {
      old_device  : $before.device_id,
      new_device  : $after.device_id,
      old_ip      : $before.ip,
      new_ip      : $after.ip,
      changed_at  : time::now()
    };
};
```

---

### EVENT-006 · Fraud Ring Detection (PATTERN-005 — graph loop)
Fires on every new `sent` edge.
Detects circular money flows: A→B→C→A within 7 days — the classic mule ring.

```surql
DEFINE EVENT detect_fraud_ring
ON TABLE sent
WHEN $event = "CREATE"
THEN {
  LET $sender = $after.in;

  -- Traverse up to 5 hops, find if sender appears in its own downstream
  LET $ring_path = (
    SELECT ->sent(WHERE created_at > time::now() - 7d)->account.*
    FROM ONLY $sender
    WHERE id = $sender
    FETCH 5
  );

  IF array::len($ring_path) > 0 {
    CREATE alert SET
      pattern_id  = "PATTERN-005",
      identity    = $sender,
      platform    = $after.platform,
      risk_level  = "Critical",
      confidence  = 0.95,
      evidence    = {
        ring_detected : true,
        trigger_tx    : $after.id,
        ring_path     : $ring_path
      };
  };
};
```

---

## Step 4 — Live Queries (Agent Subscriptions)

Agents subscribe to the alert table. When an event fires and creates an alert,
it is pushed to all subscribers instantly — no polling.

### Subscribe to all new alerts (agent startup)
```surql
LIVE SELECT * FROM alert WHERE status = "open";
```

### Subscribe to alerts for a specific platform
```surql
LIVE SELECT * FROM alert
WHERE platform = "whatsapp"
  AND status = "open";
```

### Subscribe to Critical alerts only
```surql
LIVE SELECT * FROM alert
WHERE risk_level = "Critical"
  AND status = "open";
```

Cancel subscription:
```surql
KILL $live_query_uuid;
```

---

## Step 5 — Graph Traversal Queries

### Find all identities connected to a known bad actor (2-hop)
```surql
SELECT
  ->sent->identity.* AS direct_recipients,
  ->sent->identity->sent->identity.* AS second_hop
FROM ONLY identity:$bad_actor_id;
```

### Find fraud ring — circular paths (3+ hops, within 7 days)
```surql
SELECT ->sent(
  WHERE created_at > time::now() - 7d
)->identity.* AS ring
FROM ONLY identity:$suspect_id
WHERE id = $suspect_id;
```

### Find all senders to a mule account
```surql
SELECT
  <-sent<-identity.* AS senders,
  math::sum(<-sent.amount) AS total_received
FROM ONLY identity:$mule_id;
```

### Shortest path between two identities
```surql
SELECT ->sent->identity(
  WHERE id = identity:$target_id
).* AS path
FROM ONLY identity:$source_id
FETCH 10;
```

### Scarcity pattern — rapid identical messages (PATTERN-001)
```surql
SELECT identity, count() AS occurrences, array::group(evidence.message_hash) AS messages
FROM alert
WHERE pattern_id = "PATTERN-001"
  AND created_at > time::now() - 1h
GROUP BY identity
HAVING occurrences > 2;
```

---

## Step 6 — How Agents Write to the Graph

Agents do NOT call Sentinel's scoring engine for every transaction.
They write to SurrealDB directly. Events fire automatically.

### Agent registers a new identity
```surql
INSERT INTO identity {
  platform    : "whatsapp",
  platform_id : "+919876543210",
  created_at  : time::now(),
  last_active_at : time::now(),
  device_id   : $device_fingerprint,
  ip          : $ip_address
} ON DUPLICATE KEY UPDATE
  last_active_at = time::now(),
  device_id      = $device_fingerprint,
  ip             = $ip_address;
```

### Agent records a transaction
```surql
-- This single RELATE call triggers EVENT-002, EVENT-003, EVENT-004, EVENT-006
RELATE identity:$sender_id -> sent -> identity:$recipient_id
  SET
    amount   = $amount,
    currency = "INR",
    platform = "upi",
    channel  = "upi";
```

### Agent marks alert as actioned
```surql
UPDATE alert SET
  status      = "actioned",
  actioned_at = time::now()
WHERE id = $alert_id;
```

---

## Step 7 — SurrealML Integration (Future)

SurrealDB embeds ONNX runtime. You can run a trained fraud detection model
directly inside the database — no data leaves, no latency from external calls.

```surql
-- Future: load a gradient-boosted tree trained on fraud signals
-- DEFINE MODEL fraud_scorer OVERWRITE URL "file://fraud_gbt.surml";

-- Score a transaction at query time
-- SELECT ml::predict('fraud_scorer', {
--   amount: $amount,
--   account_age_days: $age,
--   tx_velocity: $velocity,
--   recipient_risk: $risk
-- }) AS fraud_probability
-- FROM ONLY sent:$tx_id;
```

---

## Architecture Summary

```
Platform Agent
    │
    │  RELATE / INSERT (write transactions + identities)
    ▼
SurrealDB (Active Fraud Engine)
    │
    ├── DEFINE EVENT fires on every write
    │       → Checks PATTERN-002, 003, 004, 005, 006, 007
    │       → Creates alert record if triggered
    │
    ├── LIVE SELECT pushes alert to subscribers
    │       → Agent receives alert in real time
    │       → Agent shows warning / blocks action
    │
    └── Graph traversal queries
            → Fraud rings
            → Bad actor networks
            → Multi-hop mule detection
```

