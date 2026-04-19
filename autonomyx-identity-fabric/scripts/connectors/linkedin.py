"""
LinkedIn connector — OpenID Connect userinfo endpoint.
Scopes: openid profile email
Rate limit: 500 calls/day per app — caller must track externally.
"""

from __future__ import annotations

import os
from typing import Optional

from .base import (
    BaseConnector,
    ConnectorError,
    IdentityNode,
    get_json,
    head_check,
)

_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
_HEALTH_URL   = "https://api.linkedin.com/v2/userinfo"   # HEAD is fine


class LinkedInConnector(BaseConnector):
    provider_name = "linkedin"

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Token required for LinkedIn resolver")

        data = await get_json(
            _USERINFO_URL,
            token,
            self.provider_name,
            extra_headers={"LinkedIn-Version": "202401"},
        )

        # Prefer `name`; fall back to given_name + family_name
        display_name = data.get("name") or (
            f"{data.get('given_name', '')} {data.get('family_name', '')}".strip() or None
        )

        # LinkedIn headline / locale come via /v2/me with r_liteprofile scope
        # but that scope is largely deprecated for third-party apps; skip here.

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=data.get("sub", ""),
            email=(data.get("email") or "").lower() or None,
            email_verified=bool(data.get("email_verified")),
            display_name=display_name,
            profile_photo_url=data.get("picture"),
            raw_profile=data,
        )
        node.normalize_email()
        return node

    async def health_check(self) -> bool:
        # LinkedIn 401 means reachable but unauthenticated — that's fine for health
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.head(_HEALTH_URL)
            return resp.status_code < 500
        except Exception:
            return False
