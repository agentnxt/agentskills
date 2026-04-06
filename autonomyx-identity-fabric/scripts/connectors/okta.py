"""
Okta connector.
Two auth modes:
  - SSWS API token (server-side admin): hits /api/v1/users/{id} directly
  - OAuth 2.0 Bearer (end-user): hits /oauth2/v1/userinfo

Env vars:
  OKTA_DOMAIN      e.g. dev-12345.okta.com
  OKTA_API_TOKEN   SSWS token for admin access (optional)
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import (
    BaseConnector,
    ConnectorError,
    IdentityNode,
    TokenExpiredError,
    get_json,
    head_check,
    post_form,
)

_ENV_DOMAIN = os.environ.get("OKTA_DOMAIN", "")
_ENV_SSWS   = os.environ.get("OKTA_API_TOKEN", "")


class OktaConnector(BaseConnector):
    provider_name = "okta"

    def __init__(self, domain: str = "", api_token: str = ""):
        self.domain = domain or _ENV_DOMAIN
        self.api_token = api_token or _ENV_SSWS
        if not self.domain:
            raise ConnectorError("okta", "OKTA_DOMAIN not set")

    # ── Admin API (SSWS) ──────────────────────────────────────────────────────

    async def _get_user_admin(self, user_id_or_login: str) -> Optional[dict]:
        """
        Fetch user via Admin Users API using SSWS token.
        Accepts Okta user ID, login (email), or shortname.
        """
        url = f"https://{self.domain}/api/v1/users/{user_id_or_login}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                url,
                headers={
                    "Authorization": f"SSWS {self.api_token}",
                    "Accept": "application/json",
                },
            )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return None
        if resp.status_code == 401:
            raise TokenExpiredError(self.provider_name, "SSWS API token invalid or expired")
        raise ConnectorError(self.provider_name, f"Admin API returned {resp.status_code}", resp.status_code)

    async def _search_users_admin(self, query: str) -> Optional[dict]:
        """Search Okta users by email/login using SSWS token."""
        url = f"https://{self.domain}/api/v1/users"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                url,
                params={"search": f'profile.email eq "{query}" or profile.login eq "{query}"', "limit": 1},
                headers={
                    "Authorization": f"SSWS {self.api_token}",
                    "Accept": "application/json",
                },
            )
        if resp.status_code == 200:
            users = resp.json()
            return users[0] if users else None
        return None

    # ── IdentityNode builder ──────────────────────────────────────────────────

    def _build_node_from_admin(self, user: dict) -> IdentityNode:
        profile = user.get("profile", {})
        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=user.get("id", ""),
            email=(profile.get("email") or "").lower() or None,
            email_verified=user.get("status") == "ACTIVE",  # ACTIVE = email confirmed
            phone=profile.get("mobilePhone") or profile.get("primaryPhone") or None,
            username=profile.get("login"),
            display_name=profile.get("displayName") or (
                f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip() or None
            ),
            org=profile.get("organization"),
            location=profile.get("city") or profile.get("countryCode") or None,
            raw_profile=user,
        )
        node.normalize_email()
        return node

    def _build_node_from_userinfo(self, data: dict) -> IdentityNode:
        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=data.get("sub", ""),
            email=(data.get("email") or "").lower() or None,
            email_verified=bool(data.get("email_verified")),
            phone=data.get("phone_number"),
            username=data.get("preferred_username"),
            display_name=data.get("name"),
            org=data.get("organization"),
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
        Resolution priority:
        1. SSWS admin token available → use Admin Users API (richer data)
        2. OAuth Bearer token supplied → use OIDC userinfo
        3. Neither → error
        """
        if self.api_token:
            # Try direct ID lookup first, then search
            user = await self._get_user_admin(identifier)
            if not user and "@" in identifier:
                user = await self._search_users_admin(identifier)
            if not user:
                return None
            return self._build_node_from_admin(user)

        if token:
            data = await get_json(
                f"https://{self.domain}/oauth2/v1/userinfo",
                token,
                self.provider_name,
            )
            return self._build_node_from_userinfo(data)

        raise ConnectorError(
            self.provider_name,
            "Either OKTA_API_TOKEN (SSWS) or an OAuth Bearer token is required",
        )

    async def introspect_token(self, token: str) -> dict:
        """Okta RFC 7662 introspection — requires client_id + client_secret."""
        client_id = os.environ.get("OKTA_CLIENT_ID", "")
        client_secret = os.environ.get("OKTA_CLIENT_SECRET", "")
        if not (client_id and client_secret):
            return await super().introspect_token(token)
        try:
            return await post_form(
                f"https://{self.domain}/oauth2/v1/introspect",
                self.provider_name,
                data={"token": token, "token_type_hint": "access_token"},
                auth=(client_id, client_secret),
            )
        except ConnectorError:
            return await super().introspect_token(token)

    async def health_check(self) -> bool:
        url = f"https://{self.domain}/.well-known/openid-configuration"
        return await head_check(url, self.provider_name)
