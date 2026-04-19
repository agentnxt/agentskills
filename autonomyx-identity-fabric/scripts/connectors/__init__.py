"""
autonomyx-identity-fabric — Connector registry.

Single import point for all 12 provider connectors.
Usage:
    from connectors import registry, get_connector, run_health_checks

    connector = get_connector("google")           # uses env-based defaults
    node = await connector.resolve("user@example.com", token="...")

    health = await run_health_checks()            # {provider: True/False}
"""

from __future__ import annotations

import os
from typing import Optional

from .base import BaseConnector, IdentityNode, ConnectorError  # re-export
from .google     import GoogleConnector
from .github     import GitHubConnector
from .microsoft  import MicrosoftConnector
from .apple      import AppleConnector
from .linkedin   import LinkedInConnector
from .twitter    import TwitterConnector
from .logto      import LogtoConnector
from .okta       import OktaConnector
from .auth0      import Auth0Connector
from .ping       import PingConnector
from .keycloak   import KeycloakConnector
from .custom_oidc import CustomOIDCConnector

__all__ = [
    # Base
    "BaseConnector", "IdentityNode", "ConnectorError",
    # Connectors
    "GoogleConnector", "GitHubConnector", "MicrosoftConnector",
    "AppleConnector", "LinkedInConnector", "TwitterConnector",
    "LogtoConnector", "OktaConnector", "Auth0Connector",
    "PingConnector", "KeycloakConnector", "CustomOIDCConnector",
    # Registry helpers
    "registry", "get_connector", "run_health_checks",
]


def _build_default_registry() -> dict[str, BaseConnector]:
    """
    Instantiate all connectors using environment variables.
    Any connector that fails to initialise (missing required env var) is
    skipped with a warning — the registry stays partial, not broken.
    """
    candidates: list[tuple[str, type, dict]] = [
        ("google",    GoogleConnector,    {}),
        ("github",    GitHubConnector,    {}),
        ("microsoft", MicrosoftConnector, {}),
        ("apple",     AppleConnector,     {}),
        ("linkedin",  LinkedInConnector,  {}),
        ("twitter",   TwitterConnector,   {}),
        ("logto",     LogtoConnector,     {
            "domain":        os.environ.get("LOGTO_DOMAIN", ""),
            "m2m_app_id":    os.environ.get("LOGTO_M2M_APP_ID", ""),
            "m2m_app_secret":os.environ.get("LOGTO_M2M_APP_SECRET", ""),
        }),
        ("okta",      OktaConnector,      {
            "domain":    os.environ.get("OKTA_DOMAIN", ""),
            "api_token": os.environ.get("OKTA_API_TOKEN", ""),
        }),
        ("auth0",     Auth0Connector,     {
            "domain":            os.environ.get("AUTH0_DOMAIN", ""),
            "m2m_client_id":     os.environ.get("AUTH0_M2M_CLIENT_ID", ""),
            "m2m_client_secret": os.environ.get("AUTH0_M2M_CLIENT_SECRET", ""),
        }),
        ("ping",      PingConnector,      {
            "env_id":        os.environ.get("PING_ENV_ID", ""),
            "client_id":     os.environ.get("PING_CLIENT_ID", ""),
            "client_secret": os.environ.get("PING_CLIENT_SECRET", ""),
            "region":        os.environ.get("PING_REGION", "NorthAmerica"),
        }),
        ("keycloak",  KeycloakConnector,  {
            "base_url":            os.environ.get("KEYCLOAK_BASE_URL", ""),
            "realm":               os.environ.get("KEYCLOAK_REALM", "master"),
            "admin_client_id":     os.environ.get("KEYCLOAK_ADMIN_CLIENT_ID", ""),
            "admin_client_secret": os.environ.get("KEYCLOAK_ADMIN_CLIENT_SECRET", ""),
        }),
    ]

    # Custom OIDC providers — read from CUSTOM_OIDC_PROVIDERS env var
    # Format: "provider_name=https://issuer.url,provider2=https://issuer2.url"
    custom_raw = os.environ.get("CUSTOM_OIDC_PROVIDERS", "")
    for entry in custom_raw.split(","):
        entry = entry.strip()
        if "=" in entry:
            name, issuer = entry.split("=", 1)
            candidates.append((name.strip(), CustomOIDCConnector, {"issuer": issuer.strip(), "provider_name": name.strip()}))

    built: dict[str, BaseConnector] = {}
    for name, cls, kwargs in candidates:
        try:
            built[name] = cls(**kwargs)
        except ConnectorError as e:
            import warnings
            warnings.warn(f"Connector '{name}' not initialised: {e}", stacklevel=2)
    return built


# Module-level registry — lazy-initialised on first use
_registry: Optional[dict[str, BaseConnector]] = None


@property
def registry() -> dict[str, BaseConnector]:  # type: ignore[misc]
    global _registry
    if _registry is None:
        _registry = _build_default_registry()
    return _registry


def get_connector(provider: str) -> BaseConnector:
    """
    Return the connector for a provider name.
    Raises ConnectorError if provider is unknown or not initialised.
    """
    global _registry
    if _registry is None:
        _registry = _build_default_registry()
    conn = _registry.get(provider)
    if not conn:
        raise ConnectorError(provider, f"No connector registered for provider '{provider}'")
    return conn


def register_connector(provider: str, connector: BaseConnector) -> None:
    """Register a custom connector instance at runtime."""
    global _registry
    if _registry is None:
        _registry = _build_default_registry()
    _registry[provider] = connector


async def run_health_checks(providers: Optional[list[str]] = None) -> dict[str, bool]:
    """
    Run health_check() on all (or selected) registered connectors concurrently.
    Returns {provider_name: bool}.
    """
    import asyncio
    global _registry
    if _registry is None:
        _registry = _build_default_registry()

    targets = (
        {k: v for k, v in _registry.items() if k in providers}
        if providers
        else _registry
    )

    async def _check(name: str, conn: BaseConnector) -> tuple[str, bool]:
        try:
            ok = await conn.health_check()
        except Exception:
            ok = False
        return name, ok

    results = await asyncio.gather(*[_check(n, c) for n, c in targets.items()])
    return dict(results)
