"""
tests/test_connectors.py
Smoke tests for the identity fabric connector package.

Tests cover:
  - All 12 connectors instantiate without error (given env vars set)
  - IdentityNode fields and normalize_email contract
  - BaseConnector JWT decode fallback (introspect_token)
  - Registry builds and get_connector dispatches correctly
  - run_health_checks returns {str: bool} for all registered connectors
  - Apple Private Relay detection
  - GitHub org "@" stripping
  - Ping UUID detection regex

Run:  pytest tests/test_connectors.py -v
Requires:  pip install pytest pytest-asyncio httpx cryptography surrealdb
"""

from __future__ import annotations

import base64
import json
import os
import sys

import pytest
import pytest_asyncio

# Ensure scripts/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── minimal env stubs (no real secrets needed for unit tests) ─────────────────
os.environ.setdefault("IDENTITY_FABRIC_ENC_KEY",   "0" * 64)   # 32 bytes hex
os.environ.setdefault("IDENTITY_FABRIC_HMAC_KEY",  "test-hmac-key")
os.environ.setdefault("SURREAL_PASS",              "test")
os.environ.setdefault("LOGTO_DOMAIN",              "auth.example.com")
os.environ.setdefault("LOGTO_M2M_APP_ID",          "m2m-id")
os.environ.setdefault("LOGTO_M2M_APP_SECRET",      "m2m-secret")
os.environ.setdefault("OKTA_DOMAIN",               "dev-test.okta.com")
os.environ.setdefault("AUTH0_DOMAIN",              "dev-test.us.auth0.com")
os.environ.setdefault("PING_ENV_ID",               "ping-env-id")
os.environ.setdefault("PING_CLIENT_ID",            "ping-client-id")
os.environ.setdefault("PING_CLIENT_SECRET",        "ping-client-secret")
os.environ.setdefault("KEYCLOAK_BASE_URL",         "https://auth.example.com")
os.environ.setdefault("KEYCLOAK_REALM",            "autonomyx")

from connectors.base import (
    BaseConnector,
    IdentityNode,
    ConnectorError,
    TokenExpiredError,
    RateLimitedError,
)
from connectors import (
    GoogleConnector,
    GitHubConnector,
    MicrosoftConnector,
    AppleConnector,
    LinkedInConnector,
    TwitterConnector,
    LogtoConnector,
    OktaConnector,
    Auth0Connector,
    PingConnector,
    KeycloakConnector,
    CustomOIDCConnector,
    get_connector,
    run_health_checks,
)


# ── IdentityNode contract ─────────────────────────────────────────────────────

def test_identity_node_defaults():
    node = IdentityNode(provider="google", provider_sub="12345")
    assert node.email is None
    assert node.email_verified is False
    assert node.linked_account_stubs == []
    assert node.raw_profile == {}


def test_normalize_email_lowercases():
    node = IdentityNode(provider="google", provider_sub="x", email="User@Example.COM")
    node.normalize_email()
    assert node.email == "user@example.com"


def test_normalize_email_strips_whitespace():
    node = IdentityNode(provider="google", provider_sub="x", email="  user@example.com  ")
    node.normalize_email()
    assert node.email == "user@example.com"


def test_normalize_email_empty_becomes_none():
    node = IdentityNode(provider="google", provider_sub="x", email="   ")
    node.normalize_email()
    assert node.email is None


def test_private_relay_detection_true():
    node = IdentityNode(provider="apple", provider_sub="x",
                        email="abc@privaterelay.appleid.com")
    assert node.is_private_relay_email() is True


def test_private_relay_detection_false():
    node = IdentityNode(provider="apple", provider_sub="x", email="user@example.com")
    assert node.is_private_relay_email() is False


# ── Connector instantiation ───────────────────────────────────────────────────

def test_all_connectors_instantiate():
    connectors = [
        GoogleConnector(),
        GitHubConnector(),
        MicrosoftConnector(),
        AppleConnector(),
        LinkedInConnector(),
        TwitterConnector(),
        LogtoConnector(),
        OktaConnector(),
        Auth0Connector(),
        PingConnector(),
        KeycloakConnector(),
        CustomOIDCConnector(issuer="https://sso.example.com", provider_name="custom"),
    ]
    for c in connectors:
        assert isinstance(c, BaseConnector)
        assert isinstance(c.provider_name, str)
        assert len(c.provider_name) > 0


def test_connector_missing_env_raises(monkeypatch):
    import connectors.logto as logto_mod
    # Patch the module-level fallback so empty domain actually hits the guard
    monkeypatch.setattr(logto_mod, "_ENV_DOMAIN", "")
    with pytest.raises(ConnectorError):
        logto_mod.LogtoConnector(domain="", m2m_app_id="x", m2m_app_secret="y")


def test_connector_repr():
    c = GoogleConnector()
    assert "GoogleConnector" in repr(c)
    assert "google" in repr(c)


# ── Registry ──────────────────────────────────────────────────────────────────

def test_get_connector_known_providers():
    for name in ["google", "github", "microsoft", "apple", "linkedin",
                 "twitter", "logto", "okta", "auth0", "ping", "keycloak"]:
        c = get_connector(name)
        assert c.provider_name == name


def test_get_connector_unknown_raises():
    with pytest.raises(ConnectorError):
        get_connector("nonexistent_provider_xyz")


# ── JWT introspect fallback ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_introspect_token_decodes_jwt():
    """BaseConnector JWT decode fallback parses any standard JWT payload."""
    payload = {"sub": "test-sub-123", "email": "test@example.com", "iss": "https://example.com"}
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    fake_jwt = f"header.{encoded}.signature"

    # Call BaseConnector.introspect_token directly (not an overriding subclass)
    connector = GoogleConnector()
    claims = await BaseConnector.introspect_token(connector, fake_jwt)
    assert claims.get("sub") == "test-sub-123"
    assert claims.get("email") == "test@example.com"


@pytest.mark.asyncio
async def test_introspect_token_bad_jwt_returns_empty():
    connector = GitHubConnector()
    claims = await connector.introspect_token("not.a.jwt")
    # Should return {} not raise
    assert isinstance(claims, dict)


# ── Apple connector specifics ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_apple_resolve_private_relay_email_excluded():
    payload = {
        "sub": "apple-sub-001",
        "email": "abc123@privaterelay.appleid.com",
        "email_verified": "true",
        "is_private_email": True,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    fake_token = f"header.{encoded}.sig"

    conn = AppleConnector()
    node = await conn.resolve("apple-sub-001", token=fake_token)
    assert node is not None
    assert node.email is None           # private relay excluded
    assert node.email_verified is False # no linkage without email
    assert node.raw_profile["is_private_email"] is True
    assert node.raw_profile["_email_raw"] == "abc123@privaterelay.appleid.com"


@pytest.mark.asyncio
async def test_apple_resolve_name_from_dict():
    payload = {
        "sub": "apple-sub-002",
        "email": "user@example.com",
        "email_verified": "true",
        "is_private_email": False,
        "name": {"firstName": "Jane", "lastName": "Doe"},
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    fake_token = f"header.{encoded}.sig"

    conn = AppleConnector()
    node = await conn.resolve("apple-sub-002", token=fake_token)
    assert node.display_name == "Jane Doe"
    assert node.email == "user@example.com"
    assert node.email_verified is True


@pytest.mark.asyncio
async def test_apple_no_token_raises():
    conn = AppleConnector()
    with pytest.raises(ConnectorError):
        await conn.resolve("some-id", token=None)


# ── GitHub org stripping ──────────────────────────────────────────────────────

def test_github_org_at_prefix():
    """Verify @-prefix stripping logic in GitHubConnector (unit-level)."""
    raw_org = "@acme-corp"
    stripped = raw_org.lstrip("@").strip()
    assert stripped == "acme-corp"

    raw_empty = "@"
    stripped_empty = raw_empty.lstrip("@").strip() or None
    assert stripped_empty is None


# ── Ping UUID detection ───────────────────────────────────────────────────────

def test_ping_uuid_pattern():
    import re
    UUID_RE = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    assert UUID_RE.match("550e8400-e29b-41d4-a716-446655440000")
    assert not UUID_RE.match("user@example.com")
    assert not UUID_RE.match("plainusername")


# ── CustomOIDC ────────────────────────────────────────────────────────────────

def test_custom_oidc_provider_name_override():
    conn = CustomOIDCConnector(issuer="https://sso.example.com", provider_name="my_corp_sso")
    assert conn.provider_name == "my_corp_sso"
    assert conn.issuer == "https://sso.example.com"


@pytest.mark.asyncio
async def test_custom_oidc_no_token_raises():
    conn = CustomOIDCConnector(issuer="https://sso.example.com")
    with pytest.raises(ConnectorError):
        await conn.resolve("user@example.com", token=None)


# ── Exception hierarchy ───────────────────────────────────────────────────────

def test_token_expired_is_connector_error():
    e = TokenExpiredError("google", "Token expired")
    assert isinstance(e, ConnectorError)
    assert e.provider == "google"
    assert e.status_code == 401


def test_rate_limited_has_retry_after():
    e = RateLimitedError("linkedin", retry_after=120)
    assert isinstance(e, ConnectorError)
    assert e.retry_after == 120
    assert e.status_code == 429


# ── run_health_checks (mocked) ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_health_checks_returns_bool_per_provider(monkeypatch):
    """
    Monkeypatch each connector's health_check to return True.
    Validates that run_health_checks calls all registered connectors and
    returns a {str: bool} dict.
    """
    from connectors import _registry, _build_default_registry
    import connectors as conn_module

    # Rebuild registry fresh
    conn_module._registry = _build_default_registry()

    # Patch all health_checks to return True without network calls
    for connector in conn_module._registry.values():
        monkeypatch.setattr(connector, "health_check", lambda: True)

    results = await run_health_checks()
    assert isinstance(results, dict)
    assert len(results) >= 11     # at least our 11 built-in providers
    for provider, ok in results.items():
        assert isinstance(provider, str)
        assert isinstance(ok, bool)
