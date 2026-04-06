"""
autonomyx-identity-fabric — Connector base classes and shared utilities.

Every provider connector:
  - Inherits BaseConnector
  - Implements resolve(identifier, token) -> IdentityNode | None
  - Implements health_check() -> bool
  - Raises TokenExpiredError on 401
  - Raises RateLimitedError on 429
  - Raises ConnectorError on other API failures
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import httpx


# ── Exceptions ────────────────────────────────────────────────────────────────

class ConnectorError(Exception):
    """Generic connector failure."""
    def __init__(self, provider: str, message: str, status_code: int = 0):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message} (HTTP {status_code})")


class TokenExpiredError(ConnectorError):
    """OAuth token is expired or revoked (HTTP 401)."""
    def __init__(self, provider: str, message: str, status_code: int = 401):
        super().__init__(provider, message, status_code)


class TokenInsufficientScopeError(ConnectorError):
    """Token lacks required scopes (HTTP 403)."""


class RateLimitedError(ConnectorError):
    """Provider API rate limit hit (HTTP 429). retry_after in seconds."""
    def __init__(self, provider: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(provider, f"Rate limited. Retry after {retry_after}s", 429)


class ProviderUnavailableError(ConnectorError):
    """Provider API is down (5xx)."""


# ── IdentityNode ──────────────────────────────────────────────────────────────

@dataclass
class IdentityNode:
    """
    Canonical identity representation returned by every connector.
    Maps 1:1 to the SurrealDB `account` table schema.
    """
    provider: str
    provider_sub: str
    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None           # E.164 format when available
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_photo_url: Optional[str] = None  # URL only, no binary
    bio: Optional[str] = None
    org: Optional[str] = None
    location: Optional[str] = None
    raw_profile: dict = field(default_factory=dict)
    linked_account_stubs: list[dict] = field(default_factory=list)
    # [{provider: str, provider_sub: str}] — from Logto/Auth0 identity maps

    def normalize_email(self) -> None:
        """Lowercase and strip email in-place."""
        if self.email:
            self.email = self.email.lower().strip()
            if not self.email:
                self.email = None

    def is_private_relay_email(self) -> bool:
        """True if Apple Private Relay — skip for cross-provider linkage."""
        return bool(self.email and "@privaterelay.appleid.com" in self.email)


# ── HTTP helpers ──────────────────────────────────────────────────────────────

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
_RETRYABLE_5XX = {500, 502, 503, 504}


async def get_json(
    url: str,
    token: str,
    provider: str,
    extra_headers: dict | None = None,
    params: dict | None = None,
    timeout: httpx.Timeout = DEFAULT_TIMEOUT,
) -> dict:
    """
    GET a JSON endpoint with Bearer auth. Raises typed exceptions on errors.
    Does NOT retry — callers handle retry/backoff.
    """
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 401:
        raise TokenExpiredError(provider, "Token expired or revoked")
    if resp.status_code == 403:
        raise TokenInsufficientScopeError(provider, "Insufficient scope")
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", "60"))
        raise RateLimitedError(provider, retry_after)
    if resp.status_code in _RETRYABLE_5XX:
        raise ProviderUnavailableError(provider, f"Provider returned {resp.status_code}")
    raise ConnectorError(provider, f"Unexpected status {resp.status_code}", resp.status_code)


async def post_form(
    url: str,
    provider: str,
    data: dict,
    auth: tuple[str, str] | None = None,
    timeout: httpx.Timeout = DEFAULT_TIMEOUT,
) -> dict:
    """POST application/x-www-form-urlencoded and return JSON."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, data=data, auth=auth)
    if resp.status_code in (200, 201):
        return resp.json()
    if resp.status_code == 401:
        raise TokenExpiredError(provider, "Token introspection failed — invalid credentials")
    raise ConnectorError(provider, f"POST failed with {resp.status_code}", resp.status_code)


async def head_check(url: str, provider: str, timeout: float = 5.0) -> bool:
    """HEAD request for health check. Returns True if reachable (2xx/3xx)."""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            resp = await client.head(url)
        return resp.status_code < 500
    except Exception:
        return False


# ── BaseConnector ─────────────────────────────────────────────────────────────

class BaseConnector(ABC):
    """
    Abstract base for all 12 identity provider connectors.

    Subclasses must implement:
      resolve(identifier, token) -> IdentityNode | None
      health_check() -> bool

    Subclasses may optionally implement:
      introspect_token(token) -> dict   # returns claims dict
    """

    provider_name: str  # must be set on subclass; matches `account.provider` in SurrealDB

    @abstractmethod
    async def resolve(
        self,
        identifier: str,
        token: Optional[str] = None,
    ) -> Optional[IdentityNode]:
        """
        Resolve any identifier (email, sub, username, phone) to an IdentityNode.
        Returns None if the identifier is not found at the provider.
        Raises TokenExpiredError if the token is expired/revoked.
        Raises ConnectorError on API failures.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Return True if the provider API is reachable.
        Should not raise — catch all exceptions and return False.
        """
        ...

    async def introspect_token(self, token: str) -> dict:
        """
        Optional: introspect an opaque or JWT token and return claims.
        Default implementation decodes JWT payload without verification.
        Subclasses with introspection endpoints should override this.
        """
        import base64, json as _json
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return {}
            padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
            return _json.loads(base64.urlsafe_b64decode(padded))
        except Exception:
            return {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.provider_name!r}>"
