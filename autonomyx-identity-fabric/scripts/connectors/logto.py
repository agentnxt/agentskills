"""
Logto connector — Autonomyx native IdP.
Primary path: OIDC userinfo (for end-user tokens).
Management API path: fetch full user record including identities map (for M2M tokens).

Key capability: `identities` object lists all federated provider subs — fastest
path to cross-provider linkage without hitting each provider separately.

Env vars:
  LOGTO_DOMAIN           e.g. auth.openautonomyx.com
  LOGTO_M2M_APP_ID       Machine-to-machine app client_id
  LOGTO_M2M_APP_SECRET   Machine-to-machine app secret
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

_ENV_DOMAIN = os.environ.get("LOGTO_DOMAIN", "")
_ENV_M2M_ID = os.environ.get("LOGTO_M2M_APP_ID", "")
_ENV_M2M_SECRET = os.environ.get("LOGTO_M2M_APP_SECRET", "")


class LogtoConnector(BaseConnector):
    provider_name = "logto"

    def __init__(
        self,
        domain: str = "",
        m2m_app_id: str = "",
        m2m_app_secret: str = "",
    ):
        self.domain = domain or _ENV_DOMAIN
        self.m2m_app_id = m2m_app_id or _ENV_M2M_ID
        self.m2m_app_secret = m2m_app_secret or _ENV_M2M_SECRET

        if not self.domain:
            raise ConnectorError("logto", "LOGTO_DOMAIN not set")

    # ── M2M token management ──────────────────────────────────────────────────

    async def _get_m2m_token(self) -> str:
        """Obtain a short-lived M2M access token for the Management API."""
        data = await post_form(
            f"https://{self.domain}/oidc/token",
            self.provider_name,
            data={
                "grant_type": "client_credentials",
                "resource": f"https://{self.domain}/api",
                "scope": "all",
            },
            auth=(self.m2m_app_id, self.m2m_app_secret),
        )
        token = data.get("access_token")
        if not token:
            raise ConnectorError(self.provider_name, "Failed to obtain Logto M2M token")
        return token

    # ── Management API helpers ────────────────────────────────────────────────

    async def _get_user_by_id(self, user_id: str, m2m_token: str) -> dict:
        return await get_json(
            f"https://{self.domain}/api/users/{user_id}",
            m2m_token,
            self.provider_name,
        )

    async def _search_user(self, search: str, m2m_token: str) -> Optional[dict]:
        """Search Management API by email/phone/username. Returns first match."""
        data = await get_json(
            f"https://{self.domain}/api/users",
            m2m_token,
            self.provider_name,
            params={"search": search, "searchFields": "primaryEmail,primaryPhone,username", "pageSize": 1},
        )
        users = data if isinstance(data, list) else data.get("items", [])
        return users[0] if users else None

    # ── IdentityNode builder ──────────────────────────────────────────────────

    def _build_node(self, user: dict) -> IdentityNode:
        """Convert Logto user record to IdentityNode."""
        identities = user.get("identities", {})
        linked_stubs = [
            {"provider": prov, "provider_sub": str(info.get("userId", ""))}
            for prov, info in identities.items()
        ]

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=user.get("id") or user.get("sub", ""),
            email=(user.get("primaryEmail") or user.get("email") or "").lower() or None,
            email_verified=bool(
                user.get("primaryEmail") or user.get("email_verified")
            ),
            phone=user.get("primaryPhone") or user.get("phone_number") or None,
            username=user.get("username"),
            display_name=user.get("name"),
            profile_photo_url=user.get("avatar"),
            linked_account_stubs=linked_stubs,
            raw_profile=user,
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
        Two paths:
        1. End-user token supplied → call OIDC userinfo (fast path, basic fields)
        2. No token or M2M credentials available → search Management API (full fields + identities)
        """
        if token:
            try:
                # OIDC userinfo — returns basic profile
                data = await get_json(
                    f"https://{self.domain}/oidc/userinfo",
                    token,
                    self.provider_name,
                )
                sub = data.get("sub", "")

                # If we have M2M credentials, fetch full record for identities map
                if self.m2m_app_id and self.m2m_app_secret and sub:
                    try:
                        m2m = await self._get_m2m_token()
                        full = await self._get_user_by_id(sub, m2m)
                        return self._build_node(full)
                    except ConnectorError:
                        pass  # fall back to userinfo-only
                return self._build_node(data)
            except TokenExpiredError:
                raise

        # No token — search by identifier via Management API
        if not (self.m2m_app_id and self.m2m_app_secret):
            raise ConnectorError(
                self.provider_name,
                "Either end-user token or M2M credentials are required",
            )

        m2m = await self._get_m2m_token()
        user = await self._search_user(identifier, m2m)
        if not user:
            return None
        return self._build_node(user)

    async def introspect_token(self, token: str) -> dict:
        """Logto supports RFC 7662 token introspection."""
        if not (self.m2m_app_id and self.m2m_app_secret):
            return await super().introspect_token(token)
        try:
            return await post_form(
                f"https://{self.domain}/oidc/token/introspection",
                self.provider_name,
                data={"token": token},
                auth=(self.m2m_app_id, self.m2m_app_secret),
            )
        except ConnectorError:
            return await super().introspect_token(token)

    async def health_check(self) -> bool:
        url = f"https://{self.domain}/.well-known/openid-configuration"
        return await head_check(url, self.provider_name)
