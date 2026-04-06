"""
GitHub OAuth 2 connector.
Scopes: read:user user:email
Hits /user for profile + /user/emails for verified primary email.
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

_PROFILE_URL = "https://api.github.com/user"
_EMAILS_URL  = "https://api.github.com/user/emails"
_HEALTH_URL  = "https://api.github.com"
_GH_HEADERS  = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubConnector(BaseConnector):
    provider_name = "github"

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Token required for GitHub resolver")

        profile = await get_json(_PROFILE_URL, token, self.provider_name, extra_headers=_GH_HEADERS)

        # Fetch verified primary email separately — profile.email can be null if hidden
        email: Optional[str] = None
        email_verified = False
        try:
            emails = await get_json(_EMAILS_URL, token, self.provider_name, extra_headers=_GH_HEADERS)
            # prefer primary + verified; fallback to any verified
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")), None
            ) or next(
                (e for e in emails if e.get("verified")), None
            )
            if primary:
                email = primary["email"].lower()
                email_verified = True
        except ConnectorError:
            # /user/emails requires user:email scope — degrade gracefully
            raw_email = profile.get("email")
            if raw_email:
                email = raw_email.lower()
                email_verified = False

        # Strip "@" prefix from company field (GitHub convention: "@acme")
        org = (profile.get("company") or "").lstrip("@").strip() or None

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=str(profile.get("id", "")),
            email=email,
            email_verified=email_verified,
            username=profile.get("login"),
            display_name=profile.get("name"),
            profile_photo_url=profile.get("avatar_url"),
            bio=profile.get("bio"),
            org=org,
            location=profile.get("location"),
            raw_profile=profile,
        )
        node.normalize_email()
        return node

    async def introspect_token(self, token: str) -> dict:
        """
        GitHub doesn't have a token introspection endpoint.
        Call /user and return id + login as minimal claims.
        """
        try:
            data = await get_json(_PROFILE_URL, token, self.provider_name, extra_headers=_GH_HEADERS)
            return {"sub": str(data.get("id", "")), "login": data.get("login", "")}
        except ConnectorError:
            return {}

    async def health_check(self) -> bool:
        return await head_check(_HEALTH_URL, self.provider_name)
