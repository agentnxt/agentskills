"""
Ping Identity connector — PingOne API.
Scopes: p1:read:user (Worker app)
API version: PingOne Environment API v1.

Env vars:
  PING_ENV_ID          PingOne Environment ID
  PING_CLIENT_ID       Worker app client_id
  PING_CLIENT_SECRET   Worker app secret
  PING_REGION          e.g. "NorthAmerica" | "Europe" | "AsiaPacific" | "Canada"
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

_ENV_ID        = os.environ.get("PING_ENV_ID", "")
_ENV_CLIENT_ID = os.environ.get("PING_CLIENT_ID", "")
_ENV_CLIENT_SEC= os.environ.get("PING_CLIENT_SECRET", "")
_ENV_REGION    = os.environ.get("PING_REGION", "NorthAmerica")

_REGION_BASE = {
    "NorthAmerica": "https://api.pingone.com",
    "Europe":       "https://api.pingone.eu",
    "AsiaPacific":  "https://api.pingone.asia",
    "Canada":       "https://api.pingone.ca",
}
_AUTH_BASE = {
    "NorthAmerica": "https://auth.pingone.com",
    "Europe":       "https://auth.pingone.eu",
    "AsiaPacific":  "https://auth.pingone.asia",
    "Canada":       "https://auth.pingone.ca",
}


class PingConnector(BaseConnector):
    provider_name = "ping"

    def __init__(
        self,
        env_id: str = "",
        client_id: str = "",
        client_secret: str = "",
        region: str = "",
    ):
        self.env_id = env_id or _ENV_ID
        self.client_id = client_id or _ENV_CLIENT_ID
        self.client_secret = client_secret or _ENV_CLIENT_SEC
        self.region = region or _ENV_REGION

        if not self.env_id:
            raise ConnectorError("ping", "PING_ENV_ID not set")

        self._api_base  = _REGION_BASE.get(self.region, _REGION_BASE["NorthAmerica"])
        self._auth_base = _AUTH_BASE.get(self.region, _AUTH_BASE["NorthAmerica"])

    # ── Worker app token ──────────────────────────────────────────────────────

    async def _get_worker_token(self) -> str:
        if not (self.client_id and self.client_secret):
            raise ConnectorError("ping", "PING_CLIENT_ID / PING_CLIENT_SECRET not set")
        data = await post_form(
            f"{self._auth_base}/{self.env_id}/as/token",
            self.provider_name,
            data={
                "grant_type": "client_credentials",
                "scope": "p1:read:user",
            },
            auth=(self.client_id, self.client_secret),
        )
        token = data.get("access_token")
        if not token:
            raise ConnectorError(self.provider_name, "Failed to obtain PingOne worker token")
        return token

    # ── User API ──────────────────────────────────────────────────────────────

    async def _get_user(self, user_id: str, worker_token: str) -> Optional[dict]:
        try:
            return await get_json(
                f"{self._api_base}/v1/environments/{self.env_id}/users/{user_id}",
                worker_token,
                self.provider_name,
            )
        except ConnectorError as e:
            if e.status_code == 404:
                return None
            raise

    async def _search_users(self, query: str, worker_token: str) -> Optional[dict]:
        """Filter users by email or username."""
        if "@" in query:
            filter_str = f'email eq "{query}"'
        else:
            filter_str = f'username eq "{query}"'
        data = await get_json(
            f"{self._api_base}/v1/environments/{self.env_id}/users",
            worker_token,
            self.provider_name,
            params={"filter": filter_str, "limit": 1},
        )
        embedded = data.get("_embedded", {}).get("users", [])
        return embedded[0] if embedded else None

    # ── IdentityNode builder ──────────────────────────────────────────────────

    def _build_node(self, user: dict) -> IdentityNode:
        # PingOne structures email as an object or string depending on schema
        email_raw = user.get("email", {})
        if isinstance(email_raw, dict):
            email = (email_raw.get("address") or "").lower() or None
        else:
            email = (str(email_raw) or "").lower() or None

        # name.formatted or givenName + familyName
        name_obj = user.get("name", {})
        if isinstance(name_obj, dict):
            display_name = name_obj.get("formatted") or (
                f"{name_obj.get('given','')}{' ' if name_obj.get('family') else ''}{name_obj.get('family','')}".strip() or None
            )
        else:
            display_name = str(name_obj) or None

        # Phone: mobilePhone or primaryPhone
        phone = user.get("mobilePhone") or user.get("primaryPhone") or None

        node = IdentityNode(
            provider=self.provider_name,
            provider_sub=user.get("id", ""),
            email=email,
            email_verified=user.get("lifecycle", {}).get("status") == "ACCOUNT_OK",
            phone=phone,
            username=user.get("username"),
            display_name=display_name,
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
        worker_token = await self._get_worker_token()

        # Looks like a UUID → direct ID lookup
        import re
        if re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", identifier, re.IGNORECASE):
            user = await self._get_user(identifier, worker_token)
        else:
            user = await self._search_users(identifier, worker_token)

        if not user:
            return None
        return self._build_node(user)

    async def health_check(self) -> bool:
        url = f"{self._auth_base}/{self.env_id}/as/.well-known/openid-configuration"
        return await head_check(url, self.provider_name)
