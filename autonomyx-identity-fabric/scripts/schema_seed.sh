#!/usr/bin/env bash
# scripts/schema_seed.sh
# Seeds the Identity Fabric schema on a fresh SurrealDB instance.
# Run once per environment. Safe to re-run (uses IF NOT EXISTS / DEFINE ... OVERWRITE where needed).

set -euo pipefail

SURREAL_URL="${SURREAL_URL:-wss://schemadb-06ehsj292ppah8kbsk9pmnjjbc.aws-aps1.surreal.cloud}"
SURREAL_USER="${SURREAL_USER:-root}"
SURREAL_PASS="${SURREAL_PASS:?SURREAL_PASS env var required}"
NS="autonomyx"
DB="identity_fabric"

echo "→ Seeding Identity Fabric schema on $SURREAL_URL / $NS / $DB"

surreal import \
  --conn "$SURREAL_URL" \
  --user "$SURREAL_USER" \
  --pass "$SURREAL_PASS" \
  --ns "$NS" \
  --db "$DB" \
  "$(dirname "$0")/../references/surrealdb-schema.surql"

echo "✓ Schema seeded successfully."
echo ""
echo "Next steps:"
echo "  1. Set IDENTITY_FABRIC_ENC_KEY  (32-byte hex: openssl rand -hex 32)"
echo "  2. Set IDENTITY_FABRIC_HMAC_KEY (passphrase per tenant)"
echo "  3. Set LOGTO_DOMAIN, LOGTO_M2M_APP_ID, LOGTO_M2M_APP_SECRET"
echo "  4. Register identity_provider records for each active IdP"
