-- ============================================================
-- Autonomyx Identity Fabric — SurrealDB Schema
-- Instance: schemadb-06ehsj292ppah8kbsk9pmnjjbc.aws-aps1.surreal.cloud
-- Namespace: autonomyx | Database: identity_fabric
-- ============================================================

-- ─── NAMESPACE / DATABASE ────────────────────────────────────
DEFINE NAMESPACE IF NOT EXISTS autonomyx;
USE NAMESPACE autonomyx;
DEFINE DATABASE IF NOT EXISTS identity_fabric;
USE DATABASE identity_fabric;

-- ─── TABLES ──────────────────────────────────────────────────

-- person: canonical identity (one per real human)
DEFINE TABLE person SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope = "identity:read" OR $auth.scope = "identity:admin" OR $auth.id = id
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD tenant_id        ON person TYPE string ASSERT $value != NONE;
DEFINE FIELD canonical_email  ON person TYPE option<string>;
DEFINE FIELD canonical_phone  ON person TYPE option<string>;
DEFINE FIELD display_name     ON person TYPE option<string>;
DEFINE FIELD created_at       ON person TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at       ON person TYPE datetime VALUE time::now();

DEFINE INDEX person_tenant     ON person FIELDS tenant_id;
DEFINE INDEX person_email      ON person FIELDS canonical_email;

-- account: one node per (provider, provider_sub) pair
DEFINE TABLE account SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD tenant_id         ON account TYPE string ASSERT $value != NONE;
DEFINE FIELD provider          ON account TYPE string  -- google|github|microsoft|apple|linkedin|twitter|logto|okta|auth0|azuread|ping|keycloak
  ASSERT $value IN ["google","github","microsoft","apple","linkedin","twitter","logto","okta","auth0","azuread","ping","keycloak","custom"];
DEFINE FIELD provider_sub      ON account TYPE string ASSERT $value != NONE;
DEFINE FIELD email             ON account TYPE option<string>;
DEFINE FIELD email_verified    ON account TYPE bool DEFAULT false;
DEFINE FIELD phone             ON account TYPE option<string>;
DEFINE FIELD username          ON account TYPE option<string>;
DEFINE FIELD display_name      ON account TYPE option<string>;
DEFINE FIELD profile_photo_url ON account TYPE option<string>;
DEFINE FIELD bio               ON account TYPE option<string>;
DEFINE FIELD org               ON account TYPE option<string>;
DEFINE FIELD location          ON account TYPE option<string>;
-- raw_profile: encrypted JSON blob (AES-256, key in env IDENTITY_FABRIC_ENC_KEY)
DEFINE FIELD raw_profile_enc   ON account TYPE option<string>;
-- HMAC-SHA256 of normalized email (key: IDENTITY_FABRIC_HMAC_KEY per tenant)
DEFINE FIELD hashed_email      ON account TYPE option<string>;
DEFINE FIELD hashed_phone      ON account TYPE option<string>;
DEFINE FIELD created_at        ON account TYPE datetime DEFAULT time::now();
DEFINE FIELD last_seen         ON account TYPE datetime DEFAULT time::now();
DEFINE FIELD ttl_refresh_at    ON account TYPE datetime DEFAULT time::now() + 24h;
DEFINE FIELD stale             ON account TYPE bool DEFAULT false;

DEFINE INDEX account_provider_sub  ON account FIELDS provider, provider_sub UNIQUE;
DEFINE INDEX account_hashed_email  ON account FIELDS hashed_email;
DEFINE INDEX account_hashed_phone  ON account FIELDS hashed_phone;
DEFINE INDEX account_tenant        ON account FIELDS tenant_id;

-- identity_provider: registered IdP / OAuth app config
DEFINE TABLE identity_provider SCHEMAFULL PERMISSIONS
  FOR select, create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD name              ON identity_provider TYPE string;
DEFINE FIELD type              ON identity_provider TYPE string
  ASSERT $value IN ["social","sso","corporate_idp","custom"];
DEFINE FIELD issuer_url        ON identity_provider TYPE option<string>;
DEFINE FIELD client_id         ON identity_provider TYPE option<string>;
DEFINE FIELD scopes            ON identity_provider TYPE array<string>;
DEFINE FIELD tenant_id         ON identity_provider TYPE string;
DEFINE FIELD active            ON identity_provider TYPE bool DEFAULT true;

-- device_session: browser/device access records
DEFINE TABLE device_session SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD tenant_id         ON device_session TYPE string;
DEFINE FIELD user_agent        ON device_session TYPE option<string>;
DEFINE FIELD ip_hash           ON device_session TYPE option<string>;  -- hashed, not raw
DEFINE FIELD country           ON device_session TYPE option<string>;
DEFINE FIELD device_type       ON device_session TYPE option<string>;
DEFINE FIELD session_start     ON device_session TYPE datetime;
DEFINE FIELD session_end       ON device_session TYPE option<datetime>;

-- ─── RELATION TABLES (GRAPH EDGES) ────────────────────────────

-- owns: person → account
DEFINE TABLE owns TYPE RELATION IN person OUT account SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD asserted_at  ON owns TYPE datetime DEFAULT time::now();
DEFINE FIELD source       ON owns TYPE string DEFAULT "system"  -- system|manual|logto
  ASSERT $value IN ["system","manual","logto"];

-- linked_via: account → account (cross-provider linkage)
DEFINE TABLE linked_via TYPE RELATION IN account OUT account SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD confidence   ON linked_via TYPE string
  ASSERT $value IN ["HIGH","MEDIUM","LOW"];
DEFINE FIELD signal       ON linked_via TYPE string
  ASSERT $value IN ["verified_email_match","unverified_email_match","phone_match","oauth_token_claim","logto_session","manual","username_heuristic"];
DEFINE FIELD asserted_at  ON linked_via TYPE datetime DEFAULT time::now();
DEFINE FIELD asserted_by  ON linked_via TYPE option<string>;  -- agent_id or "system"

-- authenticated_by: account → identity_provider
DEFINE TABLE authenticated_by TYPE RELATION IN account OUT identity_provider SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

DEFINE FIELD first_seen   ON authenticated_by TYPE datetime DEFAULT time::now();
DEFINE FIELD last_used    ON authenticated_by TYPE datetime DEFAULT time::now();

-- accessed_from: account → device_session
DEFINE TABLE accessed_from TYPE RELATION IN account OUT device_session SCHEMAFULL PERMISSIONS
  FOR select WHERE $auth.scope IN ["identity:read", "identity:admin"]
  FOR create, update, delete WHERE $auth.scope = "identity:admin";

-- ─── AUDIT LOG ────────────────────────────────────────────────

DEFINE TABLE audit_log SCHEMAFULL PERMISSIONS
  FOR select, create WHERE $auth.scope = "identity:admin";

DEFINE FIELD tenant_id    ON audit_log TYPE string;
DEFINE FIELD action       ON audit_log TYPE string;  -- RESOLVE|ENRICH|AUDIT|LINK|UNLINK|ERASE
DEFINE FIELD actor        ON audit_log TYPE string;  -- caller sub or agent_id
DEFINE FIELD target_id    ON audit_log TYPE option<string>;
DEFINE FIELD detail       ON audit_log TYPE option<string>;
DEFINE FIELD ts           ON audit_log TYPE datetime DEFAULT time::now();

-- ─── LIVE SELECTS (real-time alerts) ──────────────────────────
-- Fire when a new LOW-confidence link is asserted
DEFINE EVENT low_confidence_link ON TABLE linked_via WHEN $event = "CREATE" AND $after.confidence = "LOW" THEN {
  CREATE audit_log SET
    tenant_id = $after.in.tenant_id,
    action = "LOW_CONFIDENCE_LINK_ASSERTED",
    actor = "system",
    target_id = <string>$after.id,
    detail = string::concat("Signal: ", $after.signal);
};

-- Fire when an account node goes stale
DEFINE EVENT account_stale ON TABLE account WHEN $event = "UPDATE" AND $after.stale = true AND $before.stale = false THEN {
  CREATE audit_log SET
    tenant_id = $after.tenant_id,
    action = "ACCOUNT_STALE",
    actor = "system",
    target_id = <string>$after.id,
    detail = string::concat("Provider: ", $after.provider);
};
