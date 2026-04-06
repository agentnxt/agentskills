"""
Auth0 connector.
Primary: Management API v2 /api/v2/users/{id} — requires management token.
Fallback: OIDC userinfo endpoint — requires end-user Bearer token.

Auth0 `identities` array provides cross-provider linkage stubs (same pattern as Logto).

Env vars:
  AUTH0_DOMAIN          e.g. dev-abc123.us.auth0.com
  AUTH0_M2M_CLIENT_ID   Machine-to-machine app client_id
  AUTH0_M2M_CLIENT_SECRET
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

_ENV_DOMAIN    = os.environ.get("AUTH0_DOMAIN", "")
_ENV_M2M_ID    = os.environ.get("AUTH0_M2M_CLIENT_ID", "")
_ENV_M2M_SEC   = os.environ.get("AUTH0_M2M_CLIENT_SECRET", "")


class Auth0Connector(BaseConnector):
    provider_name = "auth0"

    def __init__(
        self,
        domain: str = "",
        m2m_client_id: str = "",
        m2m_client_secret: str = "",
    ):
        self.domain = domain or _ENV_DOMAIN
        self.m2m_client_id = m2m_client_id or _ENV_M2M_ID
        self.m2m_client_secret = m2m_client_secret or _ENV_M2M_SEC
        if not self.domain:
            raise ConnectorError("auth0", "AUTH0_DOMAIN not set")

    # ── Management token ──────────────────────────────────────────────────────

    async def _get_mgmt_token(self) -> str:
        data = await post_form(
            f"https://{self.domain}/oauth/token",
            self.provider_name,
            data={
                "grant_type": "client_credentials",
                "client_id": self.m2m_client_id,
                "client_secret": self.m2m_client_secret,
                "audience": f"https://{self.domain}/api/v2/",
            },
        )
        token = data.get("access_token")
        if not token:
            raise ConnectorError(self.provider_name, "Failed to obtain Auth0 management token")
        return token

    # ── Management API helpers ────────────────────────────────────────────────

    async def _get_user_mgmt(self, user_id: str, mgmt_token: str) -> Optional[dict]:
        try:
            return await get_json(
                f"https://{self.domain}/api/v2/users/{user_id}",
                mgmt_token,
                self.provider_name,
            )
        except ConnectorError as e:
            if e.status_code == 404:
                return None
            raise

    async def _search_users_mgmt(self, query: str, mgmt_token: str) -> Optional[dict]:
        """Lucene search via Management API."""
        lucene = f'email:"{query}"' if "@" in query else f'username:"{query}"'
        data = await get_json(
            f"https://{self.domain}/api/v2/users",
            mgmt_token,
            self.provider_name,
            params={"q": lucene, "search_engine": "v3", "per_page": 1},
        )
        users = data if isinstance(data, list) else []
        return users[0] if users else None

    # ── IdentityNode builder ──────────────────────────────────────────────────

    def _build_node(self, user: dict) -> IdentityNode:
        identities = user.get("identities", [])
        # user_id format: "provider|sub" e.g. "google-oauth2|103xxx"
        user_id = user.get("user_id", "")

        # Linked stubs = other entries in identities array (not the primary connection)
        primary_provider = user_id.split("|")[0].replace("-oauth2", "").replace("-oidc", "") if "|" in user_id else ""
        linked_stubs = [
            {
                "provider": i.get("provider", "").replace("-oauth2", "").replace("-oidc", ""),
                "provider_sub": str(i.get("user_id", "")),
            }
            for i in identities
            if i.get("provider", "").replace("-oauth2", "").replace("-oidc", "") != primary_provider
        ]

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=user_id,
            email=(user.get("email") or "").lower() or None,
            email_verified=bool(user.get("email_verified")),
            phone=user.get("phone_number"),
            username=user.get("username") or user.get("nickname"),
            display_name=user.get("name"),
            profile_photo_url=user.get("picture"),
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
        Resolution order:
        1. Management API (M2M) — full data + identities linkage map
        2. OIDC userinfo with Bearer token — basic profile only
        """
        # Attempt Management API first
        if self.m2m_client_id and self.m2m_client_secret:
            mgmt = await self._get_mgmt_token()
            user = await self._get_user_mgmt(identifier, mgmt)
            if not user:
                user = await self._search_users_mgmt(identifier, mgmt)
            if user:
                return self._build_node(user)

        # Fall back to OIDC userinfo
        if token:
            data = await get_json(
                f"https://{self.domain}/userinfo",
                token,
                self.provider_name,
            )
            return self._build_node(data)

        raise ConnectorError(
            self.provider_name,
            "Either M2M credentials or an end-user Bearer token is required",
        )

    async def introspect_token(self, token: str) -> dict:
        """Auth0 OIDC userinfo doubles as introspection for end-user tokens."""
        if not token:
            return {}
        try:
            if self.m2m_client_id and self.m2m_client_secret:
                return await post_form(
                    f"https://{self.domain}/oauth/token/introspect",
                    self.provider_name,
                    data={"token": token},
                    auth=(self.m2m_client_id, self.m2m_client_secret),
                )
        except ConnectorError:
            pass
        return await super().introspect_token(token)

    async def health_check(self) -> bool:
        url = f"https://{self.domain}/.well-known/openid-configuration"
        return await head_check(url, self.provider_name)
