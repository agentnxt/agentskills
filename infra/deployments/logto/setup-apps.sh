#!/usr/bin/env bash
# Creates Logto OIDC applications for each service in the OpenAtonomyx stack.
# Run after Logto is healthy: docker compose up logto logto-db -d && sleep 30
#
# Requires: curl, jq
# Usage:  LOGTO_ADMIN_ENDPOINT=https://logto-admin.example.com ./setup-apps.sh

set -euo pipefail

LOGTO_ADMIN="${LOGTO_ADMIN_ENDPOINT:-https://authadmin.openautonomyx.com}"

# Get management API access token (M2M)
get_token() {
  echo "→ Obtaining Logto management API token..."
  # For self-hosted: use the built-in management API M2M app
  # The default M2M app credentials are shown in the Logto Console after first boot.
  echo "⚠  Open ${LOGTO_ADMIN} and create an M2M app with Management API access."
  echo "   Then set LOGTO_M2M_APP_ID and LOGTO_M2M_APP_SECRET and re-run."
  echo ""
  echo "   export LOGTO_M2M_APP_ID=<app_id>"
  echo "   export LOGTO_M2M_APP_SECRET=<app_secret>"

  if [[ -z "${LOGTO_M2M_APP_ID:-}" || -z "${LOGTO_M2M_APP_SECRET:-}" ]]; then
    echo "❌ M2M credentials not set. Exiting."
    exit 1
  fi

  TOKEN=$(curl -s -X POST "${LOGTO_ADMIN}/oidc/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "resource=https://default.logto.app/api" \
    -d "client_id=${LOGTO_M2M_APP_ID}" \
    -d "client_secret=${LOGTO_M2M_APP_SECRET}" \
    | jq -r '.access_token')

  if [[ "$TOKEN" == "null" || -z "$TOKEN" ]]; then
    echo "❌ Failed to get access token"
    exit 1
  fi
  echo "✅ Token obtained"
}

# Create a Traditional Web Application
create_app() {
  local name="$1"
  local redirect_uri="$2"
  local post_logout_uri="$3"

  echo "→ Creating app: ${name}..."
  RESPONSE=$(curl -s -X POST "${LOGTO_ADMIN}/api/applications" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"${name}\",
      \"type\": \"Traditional\",
      \"oidcClientMetadata\": {
        \"redirectUris\": [\"${redirect_uri}\"],
        \"postLogoutRedirectUris\": [\"${post_logout_uri}\"]
      }
    }")

  APP_ID=$(echo "$RESPONSE" | jq -r '.id')
  APP_SECRET=$(echo "$RESPONSE" | jq -r '.secret')

  if [[ "$APP_ID" == "null" || -z "$APP_ID" ]]; then
    echo "  ⚠  App may already exist or creation failed:"
    echo "  $RESPONSE" | jq .
    return
  fi

  echo "  ✅ ${name}"
  echo "     Client ID:     ${APP_ID}"
  echo "     Client Secret: ${APP_SECRET}"
  echo ""
}

DOMAIN="${DOMAIN:-agnxxt.com}"
PROTO="${PROTOCOL:-https}"

get_token

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Creating OIDC apps for OpenAtonomyx services"
echo "═══════════════════════════════════════════════════"
echo ""

create_app "Liferay Portal" \
  "${PROTO}://liferay.${DOMAIN}/c/portal/login/openid_connect" \
  "${PROTO}://liferay.${DOMAIN}/c/portal/logout"

create_app "Lago Billing" \
  "${PROTO}://lago.${DOMAIN}/auth/callback" \
  "${PROTO}://lago.${DOMAIN}/auth/logout"

create_app "ERPNext" \
  "${PROTO}://erp.${DOMAIN}/api/method/frappe.integrations.oauth2_logins.custom/logto" \
  "${PROTO}://erp.${DOMAIN}"

create_app "Odoo" \
  "${PROTO}://odoo.${DOMAIN}/auth_oauth/signin" \
  "${PROTO}://odoo.${DOMAIN}/web/session/logout"

create_app "n8n Workflows" \
  "${PROTO}://n8n.${DOMAIN}/rest/oauth2-credential/callback" \
  "${PROTO}://n8n.${DOMAIN}"

create_app "Sim Studio" \
  "${PROTO}://sim.${DOMAIN}/api/auth/callback/oidc" \
  "${PROTO}://sim.${DOMAIN}"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Done. Copy each Client ID + Secret into .env"
echo "═══════════════════════════════════════════════════"
