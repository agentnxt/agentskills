"""
Twitter / X connector — OAuth 2.0 Bearer token, v2 API.
Scopes: tweet.read users.read
Note: email NOT available via v2 API without legacy v1.1 + special approval.
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

_ME_URL     = "https://api.twitter.com/2/users/me"
_HEALTH_URL = "https://api.twitter.com/2/openapi.json"
_USER_FIELDS = "id,name,username,description,profile_image_url,location,verified,public_metrics"


class TwitterConnector(BaseConnector):
    provider_name = "twitter"

    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        if not token:
            raise ConnectorError(self.provider_name, "Token required for Twitter resolver")

        data = await get_json(
            _ME_URL,
            token,
            self.provider_name,
            params={"user.fields": _USER_FIELDS},
        )

        user = data.get("data", {})
        if not user:
            raise ConnectorError(self.provider_name, "Empty data object in Twitter /users/me response")

        # Verified blue check — store in raw_profile, not a first-class field
        raw_profile = {**user, "_verified_blue": user.get("verified", False)}

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=str(user.get("id", "")),
            # No email available via v2 API
            email=None,
            email_verified=False,
            username=user.get("username"),
            display_name=user.get("name"),
            bio=user.get("description"),
            profile_photo_url=user.get("profile_image_url"),
            location=user.get("location") or None,
            raw_profile=raw_profile,
        )
        return node

    async def health_check(self) -> bool:
        return await head_check(_HEALTH_URL, self.provider_name)
