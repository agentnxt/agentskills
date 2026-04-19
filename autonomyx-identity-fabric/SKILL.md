---
name: autonomyx-identity-fabric
description: "Resolves any user identifier (email, phone, username, OAuth sub, employee ID) into a unified identity graph stored in SurrealDB. Traverses linked accounts across social providers (Google, GitHub, Microsoft/Entra, Apple, LinkedIn, Twitter/X) and corporate SSO/IdP (Okta, Auth0, Azure AD, Ping, Keycloak, Logto). Three modes: RESOLVE (find all linked accounts), ENRICH (cache full profile data), AUDIT (compliance/IAM review). Always trigger for: find all accounts for, who is this user, link identity, identity graph, identity resolution, linked accounts, federated identity, account correlation, map user across platforms, SSO identity lookup, customer 360 identity, identity fabric, or any request to trace a user across multiple platforms or systems."
metadata:
  version: "1.0.0"
  author: "Autonomyx"
---

# Autonomyx Identity Fabric

**Multimodal identity resolution and graph persistence across all social, SSO, and corporate IdP sources.**

---

## Modes

| Mode | Trigger phrases | What it does |
|---|---|---|
| `RESOLVE` | "find all accounts for X", "who is this user", "linked accounts" | Takes any identifier → returns full identity graph for that person |
| `ENRICH` | "enrich this identity", "get profile data for", "pull details" | Fetches and caches profile fields (photo, bio, org, location) per node |
| `AUDIT` | "audit identity links", "list all SSO connections", "IAM review" | Lists all accounts, providers, and edges for a given person node |

---

## Architecture

```
Identifier (any type)
       │
       ▼
  [Normalizer]  ──── resolves type: email / phone / username / sub / employee_id
       │
       ▼
  [Graph Lookup]  ─── SurrealDB: MATCH person by canonical identifier
       │                         traverse account edges
       │
       ├── Cache HIT  ──► return graph nodes + edges
       │
       └── Cache MISS ──► [Provider Connectors] → live OAuth API lookups
                                │
                                ▼
                         [Merge & Write]  ─── upsert nodes, edges into SurrealDB
                                │
                                ▼
                         return enriched graph
```

---

## SurrealDB Schema

> Reference file: `references/surrealdb-schema.surql`
> Read this before writing any SurrealQL.

Key tables: `person`, `account`, `identity_provider`, `device_session`, `identity_link`

Key relation tables (graph edges):
- `owns` — `person → account`
- `linked_via` — `account → account` (OAuth token / shared email)
- `authenticated_by` — `account → identity_provider`
- `accessed_from` — `account → device_session`

SurrealDB instance: `schemadb-06ehsj292ppah8kbsk9pmnjjbc.aws-aps1.surreal.cloud`

---

## Provider Connectors

> Reference file: `references/provider-connectors.md`
> Read this for OAuth endpoint details, required scopes, and field mapping per provider.

Supported providers in v1:

**Social login:**
- Google (OpenID Connect, `userinfo` endpoint)
- GitHub (OAuth 2, `/user` + `/user/emails`)
- Microsoft / Entra ID (Graph API `/me`)
- Apple (Sign in with Apple, limited: sub + email only)
- LinkedIn (OpenID Connect, `/v2/userinfo`)
- Twitter/X (OAuth 2, `/2/users/me`)

**Corporate SSO / IdP:**
- Logto (Autonomyx native — JWT introspect + Management API)
- Okta (OIDC + `/api/v1/users/{id}`)
- Auth0 (Management API v2 `/api/v2/users/{id}`)
- Azure AD / Entra ID (Graph API — same as Microsoft above)
- Ping Identity (PingOne API)
- Keycloak (Admin REST API + OIDC introspect)

**Connector interface:** Every connector implements `resolve(identifier, token?) → IdentityNode`.
See `scripts/connectors/base.py` for the abstract base class.

---

## Data Model (per node)

```python
class IdentityNode:
    id: str                    # SurrealDB record ID: account:google|sub|103xxx
    provider: str              # google | github | microsoft | logto | okta | ...
    provider_sub: str          # provider-native user ID
    email: str | None          # normalized, lowercased
    email_verified: bool
    phone: str | None          # E.164 format
    username: str | None
    display_name: str | None
    profile_photo_url: str | None   # multimodal — URL stored, not binary
    bio: str | None
    org: str | None
    location: str | None
    raw_profile: dict          # full provider response (encrypted at rest)
    hashed_email: str          # SHA-256 of normalized email — used for linkage
    hashed_phone: str | None
    created_at: datetime
    last_seen: datetime
    ttl_refresh_at: datetime   # cache freshness timestamp
```

---

## Identity Linkage Logic

Two accounts are considered linked if ANY of:
1. `hashed_email` matches across providers
2. `hashed_phone` matches across providers
3. OAuth token explicitly contains a `linked_account` claim (e.g. GitHub ↔ Google via sign-in flow)
4. Logto session record references both `provider_sub` values
5. Admin-asserted merge (manual link recorded in `identity_link` table with `source: manual`)

**Confidence scoring:**

| Signal | Confidence |
|---|---|
| Verified email match | HIGH |
| Unverified email match | MEDIUM |
| Phone match | HIGH |
| OAuth token claim | HIGH |
| Logto session join | HIGH |
| Manual admin assertion | MEDIUM |
| Username heuristic only | LOW |

Edges in `linked_via` carry `{ confidence, signal, asserted_at }`.

---

## Compliance Posture (DPDP Act 2023 + GDPR)

> Reference file: `references/compliance.md`
> Read before writing any code that stores or transmits PII.

- Raw profile fields are **encrypted at rest** in SurrealDB (AES-256, key in Vault/env)
- `hashed_email` and `hashed_phone` use SHA-256 with a per-tenant HMAC key (not raw hash)
- `profile_photo_url` stores the URL only — no binary image data persisted
- Every write to `account` or `person` tables records `tenant_id` for data isolation
- LIVE SELECT subscriptions must not stream PII fields to unauthenticated agents
- Right-to-erasure: `DELETE person:X FETCH account, identity_link` cascade supported
- Data residency: SurrealDB instance is AWS ap-south-1 (India region) — DPDP compliant

---

## Caller Authentication

The skill supports **Logto JWT** as the primary caller auth mechanism:
- Extract `sub` from JWT → resolve to `person` node in SurrealDB
- Check `scope` claim for `identity:read` or `identity:admin`
- `identity:read` → RESOLVE + ENRICH own identity only
- `identity:admin` → RESOLVE + ENRICH + AUDIT any identity
- Missing/invalid token → return 401, log to `audit_log` table

For internal/agent use without Logto, an `AUTONOMYX_AGENT_SECRET` env var bypasses JWT check (operator mode only — never expose to tenants).

---

## Skill Execution Workflow

### RESOLVE mode

```
1. Normalize input identifier → detect type
2. SurrealDB: SELECT account WHERE hashed_email = $h OR provider_sub = $id
3. If found → traverse linked_via edges (depth ≤ 3)
4. For each node with ttl_refresh_at < NOW() → trigger ENRICH
5. Return: person node + all account nodes + all edges + confidence scores
```

### ENRICH mode

```
1. For each account node missing fresh data:
   a. Load provider connector
   b. Call provider API with stored OAuth token (or prompt for re-auth if expired)
   c. Merge returned fields into account node
   d. Update ttl_refresh_at = NOW() + 24h
2. Re-derive hashed_email / hashed_phone
3. Run linkage check → write any new linked_via edges
```

### AUDIT mode

```
1. Resolve person node
2. SELECT * FROM owns, linked_via, authenticated_by, accessed_from
   WHERE in = $person_id OR out = $person_id
3. Return structured audit report:
   - Identity summary (# accounts, # providers, last active)
   - Full edge list with confidence + signal
   - Anomaly flags (e.g. LOW confidence links, unverified emails, orphaned accounts)
```

---

## Output Format

### Graph JSON (primary — for downstream agents)

```json
{
  "person": { "id": "person:uuid", "canonical_email": "...", "display_name": "..." },
  "accounts": [
    { "id": "account:google|sub|xxx", "provider": "google", "email": "...", ... }
  ],
  "edges": [
    { "type": "owns", "from": "person:uuid", "to": "account:google|sub|xxx" },
    { "type": "linked_via", "from": "account:google|sub|xxx", "to": "account:github|sub|yyy",
      "confidence": "HIGH", "signal": "verified_email_match" }
  ],
  "audit_flags": [],
  "resolved_at": "2026-04-05T10:00:00Z"
}
```

### Markdown report (for human review)

Rendered after graph JSON. Includes: identity summary card, provider table, edge list with confidence badges, compliance flags.

### Mermaid graph (visual)

Auto-generated from edge list. Output only when user explicitly asks for visualization or when AUDIT mode is run.

---

## Error Handling

| Error | Behavior |
|---|---|
| Provider OAuth token expired | Flag node as `stale`, skip live fetch, return cached data with `stale: true` |
| Provider API rate limited | Exponential backoff ×3, then return cached |
| Identifier not found in any source | Return empty graph + `resolution_status: not_found` |
| SurrealDB connection failure | Propagate error, do not silently return empty graph |
| Caller auth failed | Return 401 + audit log entry |

---

## File Reference Index

| File | When to read |
|---|---|
| `references/surrealdb-schema.surql` | Before writing any SurrealQL — tables, indexes, LIVE SELECTs |
| `references/provider-connectors.md` | API endpoint specs and field mappings for all 12 providers |
| `references/compliance.md` | Before any code touching PII storage or transmission |
| `scripts/resolve.py` | RESOLVE orchestrator — identifier normalisation, BFS traversal |
| `scripts/enrich.py` | ENRICH pipeline — upsert, encryption, linkage discovery |
| `scripts/audit.py` | AUDIT report — anomaly detection, Mermaid graph, Markdown report |
| `scripts/schema_seed.sh` | Run once to seed SurrealDB schema on a fresh instance |
| `scripts/connectors/base.py` | `IdentityNode`, `BaseConnector`, typed exceptions, HTTP utilities |
| `scripts/connectors/__init__.py` | Registry — `get_connector()`, `register_connector()`, `run_health_checks()` |
| `scripts/connectors/google.py` | Google OIDC + optional People API phone fetch |
| `scripts/connectors/github.py` | GitHub OAuth — `/user` + `/user/emails` |
| `scripts/connectors/microsoft.py` | Microsoft Graph `/me` — personal + Entra ID + Azure AD |
| `scripts/connectors/apple.py` | Apple Sign In — JWT decode only, Private Relay detection |
| `scripts/connectors/linkedin.py` | LinkedIn OIDC `/v2/userinfo` |
| `scripts/connectors/twitter.py` | Twitter/X v2 `/users/me` |
| `scripts/connectors/logto.py` | Logto OIDC + Management API — `identities` map for cross-provider stubs |
| `scripts/connectors/okta.py` | Okta SSWS admin API + OIDC userinfo fallback |
| `scripts/connectors/auth0.py` | Auth0 Management API v2 + OIDC userinfo fallback |
| `scripts/connectors/ping.py` | PingOne worker app — multi-region, UUID auto-detection |
| `scripts/connectors/keycloak.py` | Keycloak Admin REST + federated-identity endpoint |
| `scripts/connectors/custom_oidc.py` | Generic OIDC Discovery for any compliant IdP |
| `tests/test_connectors.py` | 23 unit tests — run with `pytest tests/ --asyncio-mode=auto` |
