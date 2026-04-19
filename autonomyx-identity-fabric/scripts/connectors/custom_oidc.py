"""
Generic OIDC connector — works with any provider that implements OIDC Discovery.

Discovery flow:
  1. GET {issuer}/.well-known/openid-configuration
  2. Extract userinfo_endpoint
  3. GET userinfo_endpoint with Bearer token
  4. Map standard claims → IdentityNode

Registered via `identity_provider` table with type="custom" and issuer_url.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import (
    BaseConnector,
    ConnectorError,
    IdentityNode,
    head_check,
    get_json,
)

_DISCOVERY_CACHE: dict[str, dict] = {}   # in-process cache; keyed by issuer URL


async def _fetch_discovery(issuer: str) -> dict:
    """Fetch and cache OIDC discovery document."""
    if issuer in _DISCOVERY_CACHE:
        return _DISCOVERY_CACHE[issuer]
    url = issuer.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise ConnectorError("custom_oidc", f"OIDC discovery failed for {issuer}: HTTP {resp.status_code}")
    doc = resp.json()
    _DISCOVERY_CACHE[issuer] = doc
    return doc


class CustomOIDCConnector(BaseConnector):
    """
    OIDC connector for any standards-compliant IdP.
    Provide the issuer URL; the connector discovers everything else.
    """
    provider_name = "custom"

    def __init__(self, issuer: str, provider_name: str = "custom"):
        """
        issuer: OIDC issuer URL (e.g. https://sso.company.com/realms/main)
        provider_name: override for SurrealDB `account.provider` field
        """
        self.issuer = issuer.rstrip("/")
        self.provider_name = provider_name
        self._discovery: Optional[dict] = None

    async def _ensure_discovery(self) -> dict:
        if not self._discovery:
            self._discovery = await _fetch_discovery(self.issuer)
        return self._discovery

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Bearer token required for OIDC userinfo")

        doc = await self._ensure_discovery()
        userinfo_url = doc.get("userinfo_endpoint")
        if not userinfo_url:
            raise ConnectorError(self.provider_name, "OIDC discovery doc missing userinfo_endpoint")

        data = await get_json(userinfo_url, token, self.provider_name)

        # Standard OIDC claims → IdentityNode
        given  = data.get("given_name", "")
        family = data.get("family_name", "")
        display_name = (
            data.get("name")
            or f"{given} {family}".strip()
            or data.get("preferred_username")
            or None
        )

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=data.get("sub", ""),
            email=(data.get("email") or "").lower() or None,
            email_verified=bool(data.get("email_verified")),
            phone=data.get("phone_number"),
            username=data.get("preferred_username"),
            display_name=display_name,
            profile_photo_url=data.get("picture"),
            org=data.get("organization") or data.get("company"),
            location=data.get("locale"),
            raw_profile=data,
        )
        node.normalize_email()
        return node

    async def introspect_token(self, token: str) -> dict:
        """Use discovery introspection_endpoint if available; fall back to JWT decode."""
        try:
            doc = await self._ensure_discovery()
            introspect_url = doc.get("introspection_endpoint")
            if introspect_url:
                client_id     = os.environ.get(f"{self.provider_name.upper()}_CLIENT_ID", "")
                client_secret = os.environ.get(f"{self.provider_name.upper()}_CLIENT_SECRET", "")
                if client_id and client_secret:
                    from .base import post_form
                    return await post_form(
                        introspect_url,
                        self.provider_name,
                        data={"token": token},
                        auth=(client_id, client_secret),
                    )
        except Exception:
            pass
        return await super().introspect_token(token)

    async def health_check(self) -> bool:
        try:
            await self._ensure_discovery()
            return True
        except Exception:
            return False
