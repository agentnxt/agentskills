"""
Microsoft Graph connector — covers personal accounts, Entra ID, and Azure AD.
Scopes: openid email profile User.Read
Optional photo fetch via /me/photo/$value (stored as URL, not binary).
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
)

_ME_URL          = "https://graph.microsoft.com/v1.0/me"
_PHOTO_META_URL  = "https://graph.microsoft.com/v1.0/me/photo"
_PHOTO_VALUE_URL = "https://graph.microsoft.com/v1.0/me/photo/$value"
_HEALTH_URL      = "https://graph.microsoft.com/v1.0/$metadata"

# Tenant-specific introspect: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token/introspect
# Common endpoint (works for both personal + Entra):
_OIDC_USERINFO   = "https://graph.microsoft.com/oidc/userinfo"


class MicrosoftConnector(BaseConnector):
    provider_name = "microsoft"

    def __init__(
        self,
        photo_cdn_upload_fn=None,
    ):
        """
        photo_cdn_upload_fn: optional async callable(bytes, content_type) -> str (URL).
        If provided, the connector fetches the profile photo binary, uploads it, and
        stores the returned URL. If None, photo_url is left as None (safe default).
        """
        self._upload_photo = photo_cdn_upload_fn

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Token required for Microsoft resolver")

        data = await get_json(_ME_URL, token, self.provider_name)

        # Email resolution: corporate accounts use mail or userPrincipalName
        email = (
            data.get("mail")
            or data.get("userPrincipalName")
            or ""
        ).lower() or None

        # Fallback display name from given + surname
        display_name = data.get("displayName") or (
            f"{data.get('givenName', '')} {data.get('surname', '')}".strip() or None
        )

        # Phone — mobilePhone is a string or None
        phone = data.get("mobilePhone") or None

        # Profile photo — attempt fetch; skip gracefully if not available
        photo_url: Optional[str] = None
        if self._upload_photo:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        _PHOTO_VALUE_URL,
                        headers={"Authorization": f"Bearer {token}"},
                    )
                if resp.status_code == 200:
                    content_type = resp.headers.get("Content-Type", "image/jpeg")
                    photo_url = await self._upload_photo(resp.content, content_type)
            except Exception:
                pass  # photo is optional

        # Resolve Azure AD tenant from JWT tid claim
        claims = await self.introspect_token(token)
        tid = claims.get("tid")

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=data.get("id", ""),
            email=email,
            email_verified=True,  # corporate Entra accounts are always verified
            phone=phone,
            display_name=display_name,
            profile_photo_url=photo_url,
            bio=data.get("jobTitle"),
            org=data.get("companyName"),
            location=data.get("officeLocation"),
            raw_profile={**data, "_tid": tid} if tid else data,
        )
        node.normalize_email()
        return node

    async def introspect_token(self, token: str) -> dict:
        """Decode JWT claims from Entra ID token (no network call needed for JWT)."""
        return await super().introspect_token(token)

    async def health_check(self) -> bool:
        return await head_check(_HEALTH_URL, self.provider_name)
