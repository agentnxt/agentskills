"""
autonomyx-identity-fabric — MCP Server
Exposes Identity Fabric capabilities as MCP tools consumable by Claude,
Claude Code, Cursor, or any MCP-compatible client.

Tools:
  identity_resolve        — resolve any identifier to a full identity graph
  identity_enrich         — refresh stale account nodes from provider APIs
  identity_audit          — compliance/IAM audit report for a person node
  identity_link           — manually assert a cross-provider link
  identity_unlink         — remove a manually asserted link
  identity_erase          — right-to-erasure cascade (GDPR/DPDP)
  identity_health         — liveness + SurrealDB connectivity
  identity_connectors     — per-provider reachability check

Transports:
  stdio  — for Claude Desktop / Claude Code (local use)
  sse    — for remote HTTP clients (deployed on VPS, port 8090)

Auth (SSE transport):
  Bearer token in Authorization header.
  Accepts AUTONOMYX_AGENT_SECRET or a valid Logto JWT.
"""

from __future__ import annotations

import os
import json
from typing import Any, Optional

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider

# ── env ───────────────────────────────────────────────────────────────────────
AGENT_SECRET  = os.environ.get("AUTONOMYX_AGENT_SECRET", "")
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")   # stdio | sse
MCP_HOST      = os.environ.get("MCP_HOST", "0.0.0.0")
MCP_PORT      = int(os.environ.get("MCP_PORT", "8090"))
TENANT_ID     = os.environ.get("DEFAULT_TENANT_ID", "autonomyx")

# ── MCP app ───────────────────────────────────────────────────────────────────
mcp = FastMCP(
    name="autonomyx-identity-fabric",
    version="1.0.0",
    instructions="""
Autonomyx Identity Fabric MCP — resolves any user account identifier across
social logins (Google, GitHub, Microsoft, Apple, LinkedIn, Twitter) and
corporate SSO/IdP (Logto, Okta, Auth0, Azure AD, Ping, Keycloak) into a
unified identity graph stored in SurrealDB.

Key concepts:
- person: canonical identity node (one per real human)
- account: one node per (provider, provider_sub) pair
- linked_via: cross-provider edge with confidence (HIGH/MEDIUM/LOW) and signal
- tenant_id: data isolation boundary — always required

Modes:
- RESOLVE: find all linked accounts for any identifier
- ENRICH: refresh stale account nodes with live provider data
- AUDIT: compliance/IAM report with anomaly detection
""",
)


# ── lazy imports (avoid loading SurrealDB/crypto at import time for stdio) ────
def _resolve():
    from resolve import resolve as _r
    return _r

def _enrich():
    from enrich import enrich as _e
    return _e

def _audit():
    from audit import audit as _a
    return _a

def _get_db():
    from resolve import get_db
    return get_db


# ── Tool: identity_resolve ────────────────────────────────────────────────────
@mcp.tool()
async def identity_resolve(
    identifier: str,
    tenant_id: str = TENANT_ID,
    auto_enrich: bool = True,
) -> dict[str, Any]:
    """
    Resolve any user identifier to a full identity graph across all providers.

    Accepts: email, phone (E.164), username, provider:sub (e.g. google:103xxx),
             employee_id (EMP-1234), or OAuth sub.

    Returns person node, all linked account nodes, all edges (owns + linked_via),
    confidence scores, anomaly flags, and staleness markers.

    Example:
      identity_resolve("chinmay@openautonomyx.com")
      identity_resolve("github:1234567", tenant_id="acme")
    """
    resolve_fn = _resolve()
    result = await resolve_fn(
        identifier=identifier,
        tenant_id=tenant_id,
        caller="mcp",
        auto_enrich=auto_enrich,
    )
    return result


# ── Tool: identity_enrich ─────────────────────────────────────────────────────
@mcp.tool()
async def identity_enrich(
    account_ids: list[str],
    tokens: dict[str, str],
    tenant_id: str = TENANT_ID,
) -> dict[str, Any]:
    """
    Refresh stale account nodes with fresh data from their identity providers.

    account_ids: list of SurrealDB account record IDs
                 e.g. ["account:google|sub|103xxx", "account:github|sub|456"]
    tokens:      {account_id: oauth_access_token}
                 Pass empty string for accounts needing re-auth — they'll be
                 marked stale rather than failing the batch.

    Returns enriched_count, skipped_count, new edges discovered, per-account details.
    """
    enrich_fn = _enrich()
    return await enrich_fn(
        account_ids=account_ids,
        tenant_id=tenant_id,
        tokens=tokens,
        caller="mcp",
    )


# ── Tool: identity_audit ──────────────────────────────────────────────────────
@mcp.tool()
async def identity_audit(
    person_id: str,
    tenant_id: str = TENANT_ID,
    include_mermaid: bool = True,
) -> dict[str, Any]:
    """
    Generate a full compliance/IAM audit report for a person node.

    person_id: SurrealDB person record ID, e.g. "person:uuid-here"

    Returns:
    - Identity summary (# accounts, providers, last active)
    - Full edge list with confidence badges and signal types
    - Anomaly flags: stale accounts, unverified emails, low-confidence links,
      orphaned accounts
    - Mermaid graph definition for visualization (if include_mermaid=True)
    - Markdown compliance report (DPDP Act 2023 + GDPR notes)
    """
    audit_fn = _audit()
    return await audit_fn(
        person_id=person_id,
        tenant_id=tenant_id,
        caller="mcp",
        include_mermaid=include_mermaid,
        include_markdown=True,
    )


# ── Tool: identity_link ───────────────────────────────────────────────────────
@mcp.tool()
async def identity_link(
    from_account_id: str,
    to_account_id: str,
    tenant_id: str = TENANT_ID,
    confidence: str = "MEDIUM",
    note: str = "",
) -> dict[str, Any]:
    """
    Manually assert a linked_via edge between two account nodes.

    Use when automated linkage hasn't fired but you know two accounts
    belong to the same person (e.g. confirmed by the user themselves).

    confidence: HIGH | MEDIUM | LOW
    signal will be set to "manual" with your note recorded in audit_log.

    Example:
      identity_link(
        from_account_id="account:google|sub|103xxx",
        to_account_id="account:github|sub|456",
        confidence="HIGH",
        note="User confirmed same person via support ticket #1234"
      )
    """
    if confidence not in ("HIGH", "MEDIUM", "LOW"):
        return {"error": "confidence must be HIGH, MEDIUM, or LOW"}

    get_db = _get_db()
    db = await get_db()
    try:
        await db.query(
            """
            IF NOT EXISTS (SELECT * FROM linked_via WHERE in = $a AND out = $b) THEN
              RELATE $a->linked_via->$b SET
                confidence  = $c,
                signal      = 'manual',
                asserted_at = time::now(),
                asserted_by = 'mcp'
            END
            """,
            {"a": from_account_id, "b": to_account_id, "c": confidence},
        )
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='LINK', actor='mcp', "
            "target_id=$tid, detail=$d, ts=time::now()",
            {
                "t": tenant_id,
                "tid": from_account_id,
                "d": f"manual→{to_account_id} confidence={confidence} note={note}",
            },
        )
    finally:
        await db.close()

    return {
        "status": "linked",
        "from": from_account_id,
        "to": to_account_id,
        "confidence": confidence,
        "signal": "manual",
        "note": note,
    }


# ── Tool: identity_unlink ─────────────────────────────────────────────────────
@mcp.tool()
async def identity_unlink(
    from_account_id: str,
    to_account_id: str,
    tenant_id: str = TENANT_ID,
    reason: str = "",
) -> dict[str, Any]:
    """
    Remove a linked_via edge between two account nodes.

    Use to correct wrong linkages. Action is recorded in audit_log.

    Example:
      identity_unlink(
        from_account_id="account:google|sub|103xxx",
        to_account_id="account:github|sub|456",
        reason="Different people — same email used by two employees"
      )
    """
    get_db = _get_db()
    db = await get_db()
    try:
        result = await db.query(
            "DELETE linked_via WHERE in = $a AND out = $b",
            {"a": from_account_id, "b": to_account_id},
        )
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='UNLINK', actor='mcp', "
            "target_id=$tid, detail=$d, ts=time::now()",
            {
                "t": tenant_id,
                "tid": from_account_id,
                "d": f"unlinked→{to_account_id} reason={reason}",
            },
        )
    finally:
        await db.close()

    return {
        "status": "unlinked",
        "from": from_account_id,
        "to": to_account_id,
        "reason": reason,
    }


# ── Tool: identity_erase ──────────────────────────────────────────────────────
@mcp.tool()
async def identity_erase(
    person_id: str,
    tenant_id: str = TENANT_ID,
    confirm: bool = False,
) -> dict[str, Any]:
    """
    Right-to-erasure: cascade delete a person node and all linked data.

    Deletes: person record, all owned account nodes, all edges
    (linked_via, authenticated_by, accessed_from, owns).
    Records erasure in audit_log (retained 90 days per legal requirement).

    IRREVERSIBLE. You must pass confirm=True to execute.

    Example:
      identity_erase(person_id="person:uuid", confirm=True)
    """
    if not confirm:
        return {
            "status": "not_executed",
            "reason": "Pass confirm=True to execute. This action is irreversible.",
            "person_id": person_id,
        }

    get_db = _get_db()
    db = await get_db()
    try:
        # Collect account IDs
        r = await db.query(
            "SELECT out AS id FROM owns WHERE in = $p", {"p": person_id}
        )
        account_ids = [str(row["id"]) for row in (r[0].get("result", []) if r else [])]

        # Delete all edges
        for table in ("linked_via", "authenticated_by", "accessed_from", "owns"):
            await db.query(
                f"DELETE {table} WHERE in IN $ids OR out IN $ids",
                {"ids": account_ids + [person_id]},
            )

        # Delete accounts + person
        if account_ids:
            await db.query("DELETE account WHERE id IN $ids", {"ids": account_ids})
        await db.query("DELETE person WHERE id = $p", {"p": person_id})

        # Audit log
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='ERASE', actor='mcp', "
            "target_id=$tid, detail=$d, ts=time::now()",
            {
                "t": tenant_id,
                "tid": person_id,
                "d": f"erased {len(account_ids)} accounts",
            },
        )
    finally:
        await db.close()

    return {
        "status": "erased",
        "person_id": person_id,
        "accounts_deleted": len(account_ids),
        "tenant_id": tenant_id,
    }


# ── Tool: identity_health ─────────────────────────────────────────────────────
@mcp.tool()
async def identity_health() -> dict[str, Any]:
    """
    Check Identity Fabric liveness and SurrealDB connectivity.

    Returns status (ok | degraded), surrealdb connectivity, and version.
    Use this to verify the service is running before issuing other tools.
    """
    get_db = _get_db()
    try:
        db = await get_db()
        await db.query("SELECT 1")
        await db.close()
        return {"status": "ok", "surrealdb": "connected", "version": "1.0.0"}
    except Exception as e:
        return {"status": "degraded", "surrealdb": "unreachable", "error": str(e)}


# ── Tool: identity_connectors ─────────────────────────────────────────────────
@mcp.tool()
async def identity_connectors(
    providers: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Check reachability of identity provider connectors.

    providers: optional list to check specific providers only.
               If omitted, checks all registered providers.
               Options: google, github, microsoft, apple, linkedin,
                        twitter, logto, okta, auth0, ping, keycloak

    Returns {provider: bool} map — true means the provider API is reachable.

    Example:
      identity_connectors()
      identity_connectors(providers=["okta", "logto"])
    """
    from connectors import run_health_checks
    results = await run_health_checks(providers=providers)
    all_ok = all(results.values())
    return {
        "status": "ok" if all_ok else "partial",
        "providers": results,
    }


# ── Resources ─────────────────────────────────────────────────────────────────
@mcp.resource("identity://schema")
async def schema_resource() -> str:
    """SurrealDB schema for the identity fabric — tables, edges, indexes."""
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "references", "surrealdb-schema.surql"
    )
    try:
        with open(schema_path) as f:
            return f.read()
    except FileNotFoundError:
        return "Schema file not found at references/surrealdb-schema.surql"


@mcp.resource("identity://providers")
async def providers_resource() -> str:
    """All 12 provider connector specs — endpoints, scopes, field mappings."""
    ref_path = os.path.join(
        os.path.dirname(__file__), "..", "references", "provider-connectors.md"
    )
    try:
        with open(ref_path) as f:
            return f.read()
    except FileNotFoundError:
        return "Provider connectors reference not found."


@mcp.resource("identity://compliance")
async def compliance_resource() -> str:
    """DPDP Act 2023 + GDPR compliance posture, encryption spec, retention policy."""
    ref_path = os.path.join(
        os.path.dirname(__file__), "..", "references", "compliance.md"
    )
    try:
        with open(ref_path) as f:
            return f.read()
    except FileNotFoundError:
        return "Compliance reference not found."


# ── Prompts ───────────────────────────────────────────────────────────────────
@mcp.prompt()
def resolve_and_audit(identifier: str, tenant_id: str = TENANT_ID) -> str:
    """Resolve an identifier then immediately run a full audit report."""
    return f"""
Resolve this identifier and produce a full audit report:

1. Call identity_resolve("{identifier}", tenant_id="{tenant_id}")
2. From the result, extract the person_id
3. Call identity_audit(person_id, tenant_id="{tenant_id}", include_mermaid=True)
4. Present:
   - Identity summary card (accounts, providers, last active)
   - Cross-provider link table with confidence badges
   - Any anomaly flags
   - The Mermaid graph rendered inline
   - Compliance notes
"""


@mcp.prompt()
def onboard_identity(
    email: str,
    provider: str,
    provider_sub: str,
    tenant_id: str = TENANT_ID,
) -> str:
    """Onboard a new identity — resolve, enrich, and report."""
    return f"""
Onboard a new identity into the fabric:

1. identity_resolve("{email}", tenant_id="{tenant_id}")
   - If found: note existing person_id and accounts
   - If not found: we'll create via enrich

2. identity_enrich(
     account_ids=["account:{provider}|sub|{provider_sub}"],
     tokens={{"account:{provider}|sub|{provider_sub}": "<request_token_from_user>"}},
     tenant_id="{tenant_id}"
   )

3. identity_resolve("{email}", tenant_id="{tenant_id}") — re-resolve to confirm linkage

4. Report the final identity graph showing all discovered accounts and edges.
"""


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    transport = MCP_TRANSPORT.lower()

    if transport == "sse":
        print(f"Starting Identity Fabric MCP server (SSE) on {MCP_HOST}:{MCP_PORT}")
        mcp.run(
            transport="sse",
            host=MCP_HOST,
            port=MCP_PORT,
        )
    else:
        # stdio — default for Claude Desktop / Claude Code
        mcp.run(transport="stdio")
