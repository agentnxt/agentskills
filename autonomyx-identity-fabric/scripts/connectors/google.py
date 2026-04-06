"""
Google OIDC connector.
Scopes: openid email profile
Optional: People API for phone numbers.
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

_USERINFO_URL  = "https://openidconnect.googleapis.com/v1/userinfo"
_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
_PEOPLE_URL    = "https://people.googleapis.com/v1/people/me"


class GoogleConnector(BaseConnector):
    provider_name = "google"

    def __init__(self, fetch_phone: bool = False):
        """
        fetch_phone: if True, also call People API for phone numbers.
        Requires 'https://www.googleapis.com/auth/contacts.readonly' scope.
        """
        self.fetch_phone = fetch_phone

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Token required for Google resolver")

        data = await get_json(_USERINFO_URL, token, self.provider_name)

        phone = None
        if self.fetch_phone:
            try:
                people = await get_json(
                    _PEOPLE_URL, token, self.provider_name,
                    params={"personFields": "phoneNumbers"},
                )
                numbers = people.get("phoneNumbers", [])
                # prefer primary, fall back to first
                primary = next(
                    (n["value"] for n in numbers if n.get("metadata", {}).get("primary")),
                    numbers[0]["value"] if numbers else None,
                )
                phone = primary
            except ConnectorError:
                pass  # phone is optional; don't fail the whole resolve

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=str(data.get("sub", "")),
            email=(data.get("email") or "").lower() or None,
            email_verified=bool(data.get("email_verified")),
            phone=phone,
            display_name=data.get("name"),
            profile_photo_url=data.get("picture"),
            org=data.get("hd"),   # Google Workspace domain only
            raw_profile=data,
        )
        node.normalize_email()
        return node

    async def introspect_token(self, token: str) -> dict:
        """Use Google's tokeninfo endpoint to validate and get claims. Falls back to JWT decode."""
        try:
            async with __import__("httpx").AsyncClient(timeout=5) as client:
                resp = await client.get(_TOKENINFO_URL, params={"access_token": token})
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 400:
                raise TokenExpiredError(self.provider_name, "Token invalid or expired per tokeninfo")
        except TokenExpiredError:
            raise
        except Exception:
            # Network unavailable or timeout — fall back to JWT payload decode
            return await super().introspect_token(token)
        return {}

    async def health_check(self) -> bool:
        return await head_check(_TOKENINFO_URL, self.provider_name)
