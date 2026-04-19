"""
autonomyx-identity-fabric — RESOLVE mode
Takes any identifier, normalizes it, queries SurrealDB, traverses linked_via edges,
triggers ENRICH on stale nodes, and returns the full identity graph.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import httpx
from surrealdb import Surreal  # pip install surrealdb

# ── env ──────────────────────────────────────────────────────────────────────
SURREAL_URL   = os.environ.get("SURREAL_URL",  "wss://schemadb-06ehsj292ppah8kbsk9pmnjjbc.aws-aps1.surreal.cloud")
SURREAL_USER  = os.environ.get("SURREAL_USER", "root")
SURREAL_PASS  = os.environ["SURREAL_PASS"]
SURREAL_NS    = "autonomyx"
SURREAL_DB    = "identity_fabric"

HMAC_KEY      = os.environ["IDENTITY_FABRIC_HMAC_KEY"].encode()
AGENT_SECRET  = os.environ.get("AUTONOMYX_AGENT_SECRET")

MAX_EDGE_DEPTH = 3   # max hops through linked_via
TTL_SECONDS    = 86_400  # 24 h cache


# ── identifier types ─────────────────────────────────────────────────────────
class IdentifierType(str, Enum):
    EMAIL        = "email"
    PHONE        = "phone"
    USERNAME     = "username"
    PROVIDER_SUB = "provider_sub"   # format: "provider:sub"
    EMPLOYEE_ID  = "employee_id"
    UNKNOWN      = "unknown"


@dataclass
class NormalizedIdentifier:
    raw: str
    kind: IdentifierType
    value: str   # normalized form


def normalize(raw: str) -> NormalizedIdentifier:
    """Detect and normalize the identifier type."""
    raw = raw.strip()

    # provider:sub format (e.g. "google:103xxx" or "account:google|sub|103")
    if re.match(r"^[a-z]+:[^\s]+$", raw) and not "@" in raw:
        return NormalizedIdentifier(raw, IdentifierType.PROVIDER_SUB, raw)

    # email
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw):
        return NormalizedIdentifier(raw, IdentifierType.EMAIL, raw.lower())

    # E.164 phone
    if re.match(r"^\+?[0-9]{7,15}$", raw.replace(" ", "").replace("-", "")):
        normalized = re.sub(r"[\s\-]", "", raw)
        if not normalized.startswith("+"):
            normalized = "+" + normalized
        return NormalizedIdentifier(raw, IdentifierType.PHONE, normalized)

    # employee ID heuristic (EMP-XXXX, E12345, etc.)
    if re.match(r"^(EMP|E|USR|U|ID)[-_]?[0-9]{3,10}$", raw, re.IGNORECASE):
        return NormalizedIdentifier(raw, IdentifierType.EMPLOYEE_ID, raw.upper())

    # fallback: username
    if re.match(r"^[a-zA-Z0-9_.\-]{2,64}$", raw):
        return NormalizedIdentifier(raw, IdentifierType.USERNAME, raw.lower())

    return NormalizedIdentifier(raw, IdentifierType.UNKNOWN, raw)


def hmac_hash(value: str, tenant_id: str) -> str:
    """HMAC-SHA256 with tenant-scoped key."""
    key = HMAC_KEY + tenant_id.encode()
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()


# ── SurrealDB helpers ─────────────────────────────────────────────────────────
async def get_db() -> Surreal:
    db = Surreal(SURREAL_URL)
    await db.connect()
    await db.signin({"user": SURREAL_USER, "pass": SURREAL_PASS})
    await db.use(SURREAL_NS, SURREAL_DB)
    return db


async def find_accounts_by_identifier(
    db: Surreal,
    ident: NormalizedIdentifier,
    tenant_id: str,
) -> list[dict]:
    """Query SurrealDB for account nodes matching the identifier."""

    if ident.kind == IdentifierType.EMAIL:
        h = hmac_hash(ident.value, tenant_id)
        result = await db.query(
            "SELECT * FROM account WHERE hashed_email = $h AND tenant_id = $t",
            {"h": h, "t": tenant_id},
        )

    elif ident.kind == IdentifierType.PHONE:
        h = hmac_hash(ident.value, tenant_id)
        result = await db.query(
            "SELECT * FROM account WHERE hashed_phone = $h AND tenant_id = $t",
            {"h": h, "t": tenant_id},
        )

    elif ident.kind == IdentifierType.PROVIDER_SUB:
        # format: "provider:sub" or "account:provider|sub|xxx"
        parts = ident.value.split(":", 1)
        provider, sub = (parts[0], parts[1]) if len(parts) == 2 else ("", ident.value)
        result = await db.query(
            "SELECT * FROM account WHERE provider_sub = $sub AND tenant_id = $t"
            + (" AND provider = $p" if provider else ""),
            {"sub": sub, "p": provider, "t": tenant_id},
        )

    elif ident.kind == IdentifierType.USERNAME:
        result = await db.query(
            "SELECT * FROM account WHERE string::lowercase(username) = $u AND tenant_id = $t",
            {"u": ident.value, "t": tenant_id},
        )

    elif ident.kind == IdentifierType.EMPLOYEE_ID:
        # employee IDs live as provider_sub on logto/okta/azuread accounts
        result = await db.query(
            "SELECT * FROM account WHERE provider_sub = $id AND tenant_id = $t",
            {"id": ident.value, "t": tenant_id},
        )

    else:
        return []

    return result[0].get("result", []) if result else []


async def traverse_linked_via(
    db: Surreal,
    account_ids: list[str],
    depth: int = 0,
) -> tuple[list[dict], list[dict]]:
    """
    BFS traversal of linked_via edges up to MAX_EDGE_DEPTH.
    Returns (all_account_nodes, all_edges).
    """
    visited_ids = set(account_ids)
    all_accounts: list[dict] = []
    all_edges: list[dict] = []
    frontier = list(account_ids)

    while frontier and depth < MAX_EDGE_DEPTH:
        result = await db.query(
            """
            SELECT *, ->linked_via AS out_edges, <-linked_via AS in_edges
            FROM $ids
            FETCH out_edges, in_edges
            """,
            {"ids": frontier},
        )
        nodes = result[0].get("result", []) if result else []
        all_accounts.extend(nodes)

        next_frontier = []
        for node in nodes:
            for edge_set in [node.get("out_edges", []), node.get("in_edges", [])]:
                for edge in edge_set:
                    peer_id = edge.get("out") or edge.get("in")
                    if peer_id and str(peer_id) not in visited_ids:
                        visited_ids.add(str(peer_id))
                        next_frontier.append(str(peer_id))
                    all_edges.append({
                        "type": "linked_via",
                        "from": str(edge.get("in")),
                        "to": str(edge.get("out")),
                        "confidence": edge.get("confidence"),
                        "signal": edge.get("signal"),
                        "asserted_at": str(edge.get("asserted_at", "")),
                    })

        frontier = next_frontier
        depth += 1

    return all_accounts, all_edges


async def find_person_for_accounts(
    db: Surreal, account_ids: list[str], tenant_id: str
) -> Optional[dict]:
    """Find the person node that owns any of these accounts."""
    result = await db.query(
        "SELECT * FROM person WHERE id IN (SELECT in FROM owns WHERE out IN $ids) AND tenant_id = $t",
        {"ids": account_ids, "t": tenant_id},
    )
    rows = result[0].get("result", []) if result else []
    return rows[0] if rows else None


async def get_owns_edges(db: Surreal, person_id: str) -> list[dict]:
    result = await db.query(
        "SELECT * FROM owns WHERE in = $p",
        {"p": person_id},
    )
    rows = result[0].get("result", []) if result else []
    return [
        {"type": "owns", "from": str(r["in"]), "to": str(r["out"])}
        for r in rows
    ]


def is_stale(account: dict) -> bool:
    ttl_str = account.get("ttl_refresh_at")
    if not ttl_str:
        return True
    try:
        ttl = datetime.fromisoformat(str(ttl_str).replace("Z", "+00:00"))
        return ttl < datetime.now(timezone.utc)
    except Exception:
        return True


def build_audit_flags(accounts: list[dict], edges: list[dict]) -> list[dict]:
    flags = []
    for acc in accounts:
        if acc.get("stale"):
            flags.append({"code": "STALE_ACCOUNT", "account_id": str(acc["id"]), "provider": acc.get("provider")})
        if acc.get("email") and not acc.get("email_verified"):
            flags.append({"code": "UNVERIFIED_EMAIL", "account_id": str(acc["id"]), "provider": acc.get("provider")})
    for edge in edges:
        if edge.get("confidence") == "LOW":
            flags.append({"code": "LOW_CONFIDENCE_LINK", "from": edge["from"], "to": edge["to"], "signal": edge.get("signal")})
    return flags


async def write_audit_log(db: Surreal, tenant_id: str, actor: str, target_id: str) -> None:
    await db.query(
        "CREATE audit_log SET tenant_id=$t, action='RESOLVE', actor=$a, target_id=$tid, ts=time::now()",
        {"t": tenant_id, "a": actor, "tid": target_id},
    )


# ── main RESOLVE entry point ──────────────────────────────────────────────────
async def resolve(
    identifier: str,
    tenant_id: str,
    caller: str = "system",
    auto_enrich: bool = True,
) -> dict:
    """
    Resolve any identifier to a full identity graph.

    Returns:
        {
            "resolution_status": "found" | "not_found",
            "person": {...} | None,
            "accounts": [...],
            "edges": [...],
            "audit_flags": [...],
            "stale_account_ids": [...],
            "resolved_at": "ISO timestamp",
        }
    """
    ident = normalize(identifier)
    db = await get_db()

    try:
        # 1. Find seed accounts
        seed_accounts = await find_accounts_by_identifier(db, ident, tenant_id)

        if not seed_accounts:
            await write_audit_log(db, tenant_id, caller, identifier)
            return {
                "resolution_status": "not_found",
                "person": None,
                "accounts": [],
                "edges": [],
                "audit_flags": [],
                "stale_account_ids": [],
                "resolved_at": datetime.now(timezone.utc).isoformat(),
            }

        seed_ids = [str(a["id"]) for a in seed_accounts]

        # 2. Traverse linked_via graph
        all_accounts, link_edges = await traverse_linked_via(db, seed_ids)
        all_account_ids = list({str(a["id"]) for a in all_accounts})

        # 3. Find person node
        person = await find_person_for_accounts(db, all_account_ids, tenant_id)
        owns_edges = await get_owns_edges(db, str(person["id"])) if person else []

        all_edges = owns_edges + link_edges

        # 4. Flag stale accounts
        stale_ids = [str(a["id"]) for a in all_accounts if is_stale(a)]

        # 5. Trigger async ENRICH for stale nodes (fire-and-forget pattern)
        if auto_enrich and stale_ids:
            # In production: publish to a queue. Here we note them for the caller.
            pass

        # 6. Build audit flags
        flags = build_audit_flags(all_accounts, link_edges)

        # 7. Audit log
        await write_audit_log(db, tenant_id, caller, str(person["id"]) if person else identifier)

        # 8. Sanitize output (remove encrypted blobs)
        clean_accounts = []
        for a in all_accounts:
            acc = {k: v for k, v in a.items() if k not in ("raw_profile_enc", "hashed_email", "hashed_phone")}
            acc["id"] = str(acc["id"])
            clean_accounts.append(acc)

        return {
            "resolution_status": "found",
            "person": {
                "id": str(person["id"]),
                "canonical_email": person.get("canonical_email"),
                "canonical_phone": person.get("canonical_phone"),
                "display_name": person.get("display_name"),
            } if person else None,
            "accounts": clean_accounts,
            "edges": all_edges,
            "audit_flags": flags,
            "stale_account_ids": stale_ids,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }

    finally:
        await db.close()


# ── CLI usage ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio, json, sys
    if len(sys.argv) < 3:
        print("Usage: python resolve.py <identifier> <tenant_id>")
        sys.exit(1)
    result = asyncio.run(resolve(sys.argv[1], sys.argv[2]))
    print(json.dumps(result, indent=2, default=str))
