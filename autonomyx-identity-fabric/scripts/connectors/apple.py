"""
Apple Sign In connector.
Apple only returns name + email on FIRST authorization. Subsequent tokens
carry sub only. Private Relay emails are detected and excluded from linkage.

The 'token' passed here is the Apple identity_token (JWT). We decode it
without signature verification (verification requires Apple's public keys —
do that at the auth layer, not here).
"""

from __future__ import annotations

import base64
import json
import os
from typing import Optional

from .base import (
    BaseConnector,
    ConnectorError,
    IdentityNode,
    head_check,
)

_APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
_HEALTH_URL     = "https://appleid.apple.com/.well-known/openid-configuration"
_PRIVATE_RELAY  = "@privaterelay.appleid.com"


def _decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification. Returns {} on failure."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return {}


class AppleConnector(BaseConnector):
    provider_name = "apple"

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        """
        identifier: Apple user ID (sub) or email.
        token: Apple identity_token (JWT).

        Apple does NOT provide a userinfo endpoint — all data comes from the
        identity_token claims. The `name` claim is only present on first auth.
        """
        if not token:
            raise ConnectorError(self.provider_name, "Apple identity_token required")

        claims = _decode_jwt_payload(token)
        if not claims:
            raise ConnectorError(self.provider_name, "Failed to decode Apple identity_token")

        sub = claims.get("sub", "")
        if not sub:
            raise ConnectorError(self.provider_name, "No 'sub' claim in Apple token")

        email = (claims.get("email") or "").lower() or None
        is_private = claims.get("is_private_email") in (True, "true", "True")

        # Apple sends email_verified as string "true" / "false"
        ev_raw = claims.get("email_verified")
        email_verified = ev_raw in (True, "true", "True") and not is_private

        # name only present on first-time sign-in (passed separately by app, not in token)
        # Apps should cache it; we accept it as an optional extra field in raw_profile
        display_name: Optional[str] = None
        if "name" in claims:
            n = claims["name"]
            if isinstance(n, dict):
                parts = [n.get("firstName", ""), n.get("lastName", "")]
                display_name = " ".join(p for p in parts if p).strip() or None
            elif isinstance(n, str):
                display_name = n or None

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=sub,
            # Skip Private Relay emails for cross-provider linkage
            email=None if is_private else email,
            email_verified=email_verified,
            display_name=display_name,
            raw_profile={
                **claims,
                "is_private_email": is_private,
                "_email_raw": email,   # keep original even if skipped for linkage
            },
        )
        return node

    async def introspect_token(self, token: str) -> dict:
        return _decode_jwt_payload(token)

    async def health_check(self) -> bool:
        return await head_check(_HEALTH_URL, self.provider_name)
