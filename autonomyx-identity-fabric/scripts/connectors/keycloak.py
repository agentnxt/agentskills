"""
Keycloak connector.
Two auth modes:
  - End-user Bearer token → OIDC userinfo endpoint
  - Admin credentials (client_credentials) → Admin REST API (full profile + federated identities)

Env vars:
  KEYCLOAK_BASE_URL    e.g. https://auth.openautonomyx.com
  KEYCLOAK_REALM       e.g. autonomyx
  KEYCLOAK_ADMIN_CLIENT_ID
  KEYCLOAK_ADMIN_CLIENT_SECRET
"""

from __future__ import annotations

import os
from typing import Optional

from .base import (
    BaseConnector,
    ConnectorError,
    IdentityNode,
    TokenExpiredError,
    get_json,
    head_check,
    post_form,
)

_ENV_BASE_URL   = os.environ.get("KEYCLOAK_BASE_URL", "")
_ENV_REALM      = os.environ.get("KEYCLOAK_REALM", "master")
_ENV_ADMIN_ID   = os.environ.get("KEYCLOAK_ADMIN_CLIENT_ID", "")
_ENV_ADMIN_SEC  = os.environ.get("KEYCLOAK_ADMIN_CLIENT_SECRET", "")


class KeycloakConnector(BaseConnector):
    provider_name = "keycloak"

    def __init__(
        self,
        base_url: str = "",
        realm: str = "",
        admin_client_id: str = "",
        admin_client_secret: str = "",
    ):
        self.base_url = (base_url or _ENV_BASE_URL).rstrip("/")
        self.realm    = realm or _ENV_REALM
        self.admin_client_id     = admin_client_id or _ENV_ADMIN_ID
        self.admin_client_secret = admin_client_secret or _ENV_ADMIN_SEC

        if not self.base_url:
            raise ConnectorError("keycloak", "KEYCLOAK_BASE_URL not set")

        self._realm_url = f"{self.base_url}/realms/{self.realm}"
        self._admin_url = f"{self.base_url}/admin/realms/{self.realm}"

    # ── Admin token ───────────────────────────────────────────────────────────

    async def _get_admin_token(self) -> str:
        if not (self.admin_client_id and self.admin_client_secret):
            raise ConnectorError("keycloak", "Admin credentials not configured")
        data = await post_form(
            f"{self._realm_url}/protocol/openid-connect/token",
            self.provider_name,
            data={
                "grant_type": "client_credentials",
                "client_id": self.admin_client_id,
                "client_secret": self.admin_client_secret,
            },
        )
        token = data.get("access_token")
        if not token:
            raise ConnectorError(self.provider_name, "Failed to obtain Keycloak admin token")
        return token

    # ── Admin REST helpers ────────────────────────────────────────────────────

    async def _get_user_by_id(self, user_id: str, admin_token: str) -> Optional[dict]:
        try:
            return await get_json(
                f"{self._admin_url}/users/{user_id}",
                admin_token,
                self.provider_name,
            )
        except ConnectorError as e:
            if e.status_code == 404:
                return None
            raise

    async def _search_users(self, query: str, admin_token: str) -> Optional[dict]:
        """Search users by email or username."""
        params = {"max": 1}
        if "@" in query:
            params["email"] = query
        else:
            params["username"] = query
        users = await get_json(
            f"{self._admin_url}/users",
            admin_token,
            self.provider_name,
            params=params,
        )
        return users[0] if isinstance(users, list) and users else None

    async def _get_federated_identities(self, user_id: str, admin_token: str) -> list[dict]:
        """
        GET /admin/realms/{realm}/users/{id}/federated-identity
        Returns list of {identityProvider, userId, userName}
        """
        try:
            return await get_json(
                f"{self._admin_url}/users/{user_id}/federated-identity",
                admin_token,
                self.provider_name,
            ) or []
        except ConnectorError:
            return []

    # ── IdentityNode builder ──────────────────────────────────────────────────

    def _build_node_from_admin(self, user: dict, fed_identities: list[dict]) -> IdentityNode:
        attrs = user.get("attributes", {})

        # Phone may be in custom attributes
        phone = None
        for key in ("phone", "phoneNumber", "mobile", "mobilePhone"):
            val = attrs.get(key)
            if val:
                phone = val[0] if isinstance(val, list) else val
                break

        # Org / department from attributes
        org = None
        for key in ("org", "organization", "department", "company"):
            val = attrs.get(key)
            if val:
                org = val[0] if isinstance(val, list) else val
                break

        # Cross-provider stubs from federated identities
        linked_stubs = [
            {
                "provider": fi.get("identityProvider", ""),
                "provider_sub": fi.get("userId", ""),
            }
            for fi in fed_identities
            if fi.get("identityProvider") and fi.get("userId")
        ]

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=user.get("id", ""),
            email=(user.get("email") or "").lower() or None,
            email_verified=bool(user.get("emailVerified")),
            phone=phone,
            username=user.get("username"),
            display_name=f"{user.get('firstName', '')} {user.get('lastName', '')}".strip() or None,
            org=org,
            linked_account_stubs=linked_stubs,
            raw_profile=user,
        )
        node.normalize_email()
        return node

    def _build_node_from_userinfo(self, data: dict) -> IdentityNode:
        attrs = data.get("attributes", {}) if isinstance(data.get("attributes"), dict) else {}
        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=data.get("sub", ""),
            email=(data.get("email") or "").lower() or None,
            email_verified=bool(data.get("email_verified")),
            phone=data.get("phone_number") or (attrs.get("phone") or [None])[0],
            username=data.get("preferred_username"),
            display_name=data.get("name") or (
                f"{data.get('given_name','')} {data.get('family_name','')}".strip() or None
            ),
            raw_profile=data,
        )
        node.normalize_email()
        return node

    # ── BaseConnector interface ───────────────────────────────────────────────

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        """
        Priority:
        1. Admin REST API (client_credentials) — full profile + federated identities
        2. OIDC userinfo (end-user Bearer) — basic profile
        """
        if self.admin_client_id and self.admin_client_secret:
            admin_token = await self._get_admin_token()
            user = await self._get_user_by_id(identifier, admin_token)
            if not user:
                user = await self._search_users(identifier, admin_token)
            if not user:
                return None
            fed = await self._get_federated_identities(user["id"], admin_token)
            return self._build_node_from_admin(user, fed)

        if token:
            data = await get_json(
                f"{self._realm_url}/protocol/openid-connect/userinfo",
                token,
                self.provider_name,
            )
            return self._build_node_from_userinfo(data)

        raise ConnectorError(
            self.provider_name,
            "Either admin client credentials or an end-user Bearer token is required",
        )

    async def introspect_token(self, token: str) -> dict:
        """Keycloak RFC 7662 token introspection."""
        if not (self.admin_client_id and self.admin_client_secret):
            return await super().introspect_token(token)
        try:
            return await post_form(
                f"{self._realm_url}/protocol/openid-connect/token/introspect",
                self.provider_name,
                data={"token": token},
                auth=(self.admin_client_id, self.admin_client_secret),
            )
        except ConnectorError:
            return await super().introspect_token(token)

    async def health_check(self) -> bool:
        url = f"{self._realm_url}/.well-known/openid-configuration"
        return await head_check(url, self.provider_name)
