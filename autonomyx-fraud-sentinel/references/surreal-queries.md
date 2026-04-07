# Autonomyx Fraud Sentinel — SurrealDB Query Reference

> All queries use SurrealDB HTTP REST API.
> Base URL: $SURREAL_URL
> Headers: Authorization: Basic <base64(user:pass)>, NS: $SURREAL_NS, DB: $SURREAL_DB

---

## Create a Fraud Event

```surql
CREATE fraud_event SET
  event_id           = rand::uuid(),
  source_platform    = $source_platform,
  agent_id           = $agent_id,
  reporter_id        = $reporter_id,
  identity_id        = $identity_id,
  pattern_id         = $pattern_id,
  risk_level         = $risk_level,
  confidence         = $confidence,
  raw_evidence       = $raw_evidence,
  indicators_matched = $indicators_matched,
  status             = "open",
  created_at         = time::now(),
  updated_at         = time::now(),
  broadcasts_sent    = [],
  block_issued       = false;
```

---

## Store Raw Signal (Immutable Audit Log)

```surql
CREATE fraud_signal SET
  signal_id       = rand::uuid(),
  source_platform = $source_platform,
  agent_id        = $agent_id,
  reporter_id     = $reporter_id,
  identity_id     = $identity_id,
  signal_type     = $signal_type,
  raw_evidence    = $raw_evidence,
  received_at     = time::now();
```

---

## Update Event After Action

```surql
UPDATE fraud_event SET
  broadcasts_sent = $audiences_notified,
  block_issued    = $block_issued,
  status          = "actioned",
  updated_at      = time::now()
WHERE event_id = $event_id;
```

---

## Register a New Platform Agent

```surql
CREATE fraud_agent SET
  agent_id      = rand::uuid(),
  platform      = $platform,
  agent_version = $version,
  registered_at = time::now(),
  status        = "active",
  signal_count  = 0;
```

---

## Query Open Events by Risk Level

```surql
SELECT * FROM fraud_event
WHERE risk_level = $risk_level
AND status = "open"
ORDER BY created_at DESC;
```

---

## Query All Events for an Identity

```surql
SELECT * FROM fraud_event
WHERE identity_id = $identity_id
ORDER BY created_at DESC;
```

---

## Query Pending Block Signals (No Agent Yet)

```surql
SELECT * FROM fraud_event
WHERE block_issued = false
AND risk_level IN ["High", "Critical"]
AND status = "actioned";
```

---

## Increment Agent Signal Count

```surql
UPDATE fraud_agent
SET signal_count = signal_count + 1,
    updated_at   = time::now()
WHERE agent_id = $agent_id;
```

---

## Check for Repeat Offender (Same Identity, Multiple Events)

```surql
SELECT count() AS total, identity_id FROM fraud_event
WHERE identity_id = $identity_id
GROUP BY identity_id;
```

---

## Store Pre-Action Log

```surql
CREATE fraud_preaction_log SET
  query_id           = rand::uuid(),
  agent_id           = $agent_id,
  source_platform    = $source_platform,
  actor_identity_id  = $actor_identity_id,
  target_identity_id = $target_identity_id,
  action_type        = $action_type,
  action_value       = $action_value,
  decision           = $decision,
  risk_score         = $risk_score,
  patterns_matched   = $patterns_matched,
  confidence         = $confidence,
  queried_at         = time::now();
```

---

## Check Target Identity Risk History

```surql
SELECT risk_level, confidence, pattern_id, created_at
FROM fraud_event
WHERE identity_id = $target_identity_id
ORDER BY created_at DESC
LIMIT 10;
```

---

## Check Actor Velocity (Last 10 Minutes)

```surql
SELECT count() AS action_count
FROM fraud_preaction_log
WHERE actor_identity_id = $actor_identity_id
AND queried_at > time::now() - 10m;
```

---

## Build Identity Behaviour Baseline (Active Hours)

```surql
SELECT time::hour(queried_at) AS hour, count() AS count
FROM fraud_preaction_log
WHERE actor_identity_id = $actor_identity_id
AND queried_at > time::now() - 30d
GROUP BY hour
ORDER BY hour ASC;
```

---

## Check Graph Linkage (Target Linked to Known Bad Actor)

```surql
-- Direct link: target is a known fraud actor
SELECT event_id, risk_level FROM fraud_event
WHERE identity_id = $target_identity_id
AND risk_level IN ["High", "Critical"];

-- 2-hop link: target shares payment destination with a known fraud actor
SELECT DISTINCT fe.identity_id, fe.risk_level
FROM fraud_event AS fe
WHERE fe.raw_evidence CONTAINS $target_identity_id
AND fe.risk_level IN ["High", "Critical"];
```

---

## Create Safety Check Record (No PII)

```surql
CREATE fraud_safety_check SET
  txn_id            = $txn_id,
  description_hash  = crypto::sha256($description),
  signals_extracted = $signals_extracted,
  patterns_matched  = $patterns_matched,
  risk_level        = $risk_level,
  confidence        = $confidence,
  fraud_type        = $fraud_type,
  platform          = $platform,
  amount            = $amount,
  outcome           = "pending",
  created_at        = time::now(),
  expires_at        = time::now() + 90d;
```

---

## Check TXN ID Exists (Collision Check)

```surql
SELECT txn_id FROM fraud_safety_check
WHERE txn_id = $txn_id LIMIT 1;
```

---

## Update Outcome After Fraud Reported

```surql
UPDATE fraud_safety_check SET
  outcome    = "fraud_occurred",
  updated_at = time::now()
WHERE txn_id = $txn_id;
```

---

## Aggregate Safety Check Stats (for public dashboard)

```surql
SELECT risk_level, count() AS total, fraud_type
FROM fraud_safety_check
WHERE created_at > time::now() - 7d
GROUP BY risk_level, fraud_type
ORDER BY total DESC;
```

---

## False Negative Analysis (LOW risk → fraud occurred)

```surql
SELECT fraud_type, patterns_matched, signals_extracted
FROM fraud_safety_check
WHERE outcome = "fraud_occurred"
AND risk_level IN ["Low", "Medium"]
ORDER BY created_at DESC
LIMIT 50;
```
