# Compliance Reference — Identity Fabric
## DPDP Act 2023 (India) + GDPR (EU/UK)

---

## Data Classification

| Field | Classification | Storage Rule |
|---|---|---|
| `email` | Personal Data | Encrypted at rest (AES-256) |
| `phone` | Sensitive Personal Data | Encrypted at rest (AES-256) |
| `hashed_email` | Pseudonymous | HMAC-SHA256 with per-tenant key — never raw hash |
| `hashed_phone` | Pseudonymous | HMAC-SHA256 with per-tenant key |
| `raw_profile_enc` | Personal Data (encrypted blob) | AES-256, key in env/Vault |
| `profile_photo_url` | Personal Data | URL only, no binary; must be external CDN |
| `ip_hash` | Pseudonymous | SHA-256 of IP — never raw IP |
| `display_name` | Personal Data | Encrypted at rest |
| `bio`, `org`, `location` | Personal Data | Encrypted at rest |

---

## Encryption Implementation

```python
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib, hmac

ENC_KEY = bytes.fromhex(os.environ["IDENTITY_FABRIC_ENC_KEY"])  # 32 bytes
HMAC_KEY = os.environ["IDENTITY_FABRIC_HMAC_KEY"].encode()      # per-tenant

def encrypt(plaintext: str) -> str:
    """AES-256-GCM encrypt. Returns base64-encoded nonce+ciphertext."""
    aesgcm = AESGCM(ENC_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()

def decrypt(blob: str) -> str:
    raw = base64.b64decode(blob)
    nonce, ct = raw[:12], raw[12:]
    return AESGCM(ENC_KEY).decrypt(nonce, ct, None).decode()

def hmac_hash(value: str, tenant_id: str) -> str:
    """HMAC-SHA256 with tenant-scoped key. Normalize before hashing."""
    key = HMAC_KEY + tenant_id.encode()
    return hmac.new(key, value.lower().strip().encode(), hashlib.sha256).hexdigest()
```

---

## DPDP Act 2023 Requirements

| Obligation | Implementation |
|---|---|
| Purpose limitation | Identity data used only for identity resolution — purpose recorded in audit_log |
| Data minimisation | Only fields in IdentityNode spec are stored; no speculative collection |
| Consent | Caller must confirm user consent before ENRICH; `source: manual` links require admin role |
| Data localisation | SurrealDB instance: AWS ap-south-1 (Mumbai) — India residency satisfied |
| Right to erasure | `DELETE person:X FETCH account, identity_link` cascade + `audit_log` entry |
| Grievance officer | Contact: chinmay@openautonomyx.com |

---

## GDPR Requirements

| Obligation | Implementation |
|---|---|
| Lawful basis | Legitimate interest (IAM/fraud prevention) or explicit consent (customer 360) |
| Data minimisation | ✓ same as DPDP |
| Right of access | AUDIT mode returns full data per person on request |
| Right to erasure | Cascade delete supported; `audit_log` entries retained 90 days per legal requirement |
| Data breach | Audit log LIVE SELECT → triggers alert if bulk read detected (>100 records/min) |
| Sub-processor disclosure | SurrealDB Cloud (AWS), Anthropic (AI inference) — per Autonomyx Privacy Policy |
| Data transfer | SurrealDB AWS ap-south-1; no cross-border transfer for India data |

---

## Retention Policy

| Data type | Retention |
|---|---|
| account node | Until erasure request or 2 years post last_seen |
| device_session | 90 days |
| audit_log | 90 days (legal minimum) |
| raw_profile_enc | 24 hours post last ENRICH (refresh or delete) |

---

## Access Control Summary

| Scope | Allowed operations |
|---|---|
| `identity:read` | RESOLVE own identity only; ENRICH own identity only |
| `identity:admin` | RESOLVE any; ENRICH any; AUDIT any; create/delete links |
| `AUTONOMYX_AGENT_SECRET` | Operator mode — all operations — internal agents only |
| No token | Reject all — 401 + audit_log entry |

---

## Right to Erasure Procedure

```surql
-- Step 1: find all account nodes
LET $accounts = SELECT id FROM account WHERE tenant_id = $tenant AND id IN (
  SELECT out FROM owns WHERE in = $person_id
);

-- Step 2: delete all edges
DELETE linked_via WHERE in IN $accounts OR out IN $accounts;
DELETE authenticated_by WHERE in IN $accounts;
DELETE accessed_from WHERE in IN $accounts;
DELETE owns WHERE in = $person_id;

-- Step 3: delete account nodes
DELETE account WHERE id IN $accounts;

-- Step 4: delete person node
DELETE person WHERE id = $person_id;

-- Step 5: log erasure
CREATE audit_log SET
  tenant_id = $tenant,
  action = "ERASE",
  actor = $caller,
  target_id = $person_id,
  detail = string::concat("Erased ", <string>array::len($accounts), " account nodes");
```
