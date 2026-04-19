"""
autonomyx-identity-fabric — AUDIT mode
Generates a structured compliance/IAM audit report for a given person node.
Outputs: identity summary, full edge list with confidence badges, anomaly flags,
Mermaid graph definition, and Markdown report.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from surrealdb import Surreal
from resolve import get_db


# ── helpers ───────────────────────────────────────────────────────────────────
CONFIDENCE_BADGE = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}
SIGNAL_LABEL = {
    "verified_email_match":   "Verified email match",
    "unverified_email_match": "Unverified email match",
    "phone_match":            "Phone match",
    "oauth_token_claim":      "OAuth token claim",
    "logto_session":          "Logto session join",
    "manual":                 "Admin-asserted",
    "username_heuristic":     "Username heuristic",
}


def _flag_label(code: str) -> str:
    return {
        "STALE_ACCOUNT":       "⚠️  Stale account — data not refreshed within 24h",
        "UNVERIFIED_EMAIL":    "⚠️  Unverified email — cannot be used for HIGH-confidence linkage",
        "LOW_CONFIDENCE_LINK": "🔴 Low-confidence identity link — review manually",
        "ORPHANED_ACCOUNT":    "⚠️  Orphaned account — no owns edge to any person node",
    }.get(code, code)


# ── SurrealDB queries ─────────────────────────────────────────────────────────
async def load_person(db: Surreal, person_id: str, tenant_id: str) -> dict | None:
    result = await db.query(
        "SELECT * FROM $id WHERE tenant_id=$t",
        {"id": person_id, "t": tenant_id},
    )
    rows = result[0].get("result", []) if result else []
    return rows[0] if rows else None


async def load_all_edges(db: Surreal, person_id: str) -> dict:
    """Load all four edge types for a person."""
    owns_r = await db.query(
        "SELECT *, ->owns AS edges FROM $id FETCH edges",
        {"id": person_id},
    )
    owns_rows = owns_r[0].get("result", [{}])[0].get("edges", []) if owns_r else []
    account_ids = [str(e.get("out")) for e in owns_rows if e.get("out")]

    linked_r = await db.query(
        "SELECT * FROM linked_via WHERE in IN $ids OR out IN $ids",
        {"ids": account_ids},
    )
    linked_rows = linked_r[0].get("result", []) if linked_r else []

    auth_r = await db.query(
        "SELECT *, ->authenticated_by AS edges FROM $ids FETCH edges",
        {"ids": account_ids},
    )
    auth_rows = []
    for row in (auth_r[0].get("result", []) if auth_r else []):
        auth_rows.extend(row.get("edges", []))

    session_r = await db.query(
        "SELECT *, ->accessed_from AS edges FROM $ids FETCH edges",
        {"ids": account_ids},
    )
    session_rows = []
    for row in (session_r[0].get("result", []) if session_r else []):
        session_rows.extend(row.get("edges", []))

    return {
        "owns": owns_rows,
        "account_ids": account_ids,
        "linked_via": linked_rows,
        "authenticated_by": auth_rows,
        "accessed_from": session_rows,
    }


async def load_account_details(db: Surreal, account_ids: list[str]) -> list[dict]:
    if not account_ids:
        return []
    result = await db.query(
        "SELECT id, provider, email, email_verified, phone, username, display_name, "
        "profile_photo_url, org, location, stale, last_seen, ttl_refresh_at "
        "FROM $ids",
        {"ids": account_ids},
    )
    return result[0].get("result", []) if result else []


# ── anomaly detection ─────────────────────────────────────────────────────────
def detect_anomalies(
    accounts: list[dict],
    edges: dict,
    owns_account_ids: set[str],
) -> list[dict]:
    flags = []
    account_map = {str(a["id"]): a for a in accounts}

    for acc in accounts:
        if acc.get("stale"):
            flags.append({"code": "STALE_ACCOUNT", "account_id": str(acc["id"]),
                          "provider": acc.get("provider")})
        if acc.get("email") and not acc.get("email_verified"):
            flags.append({"code": "UNVERIFIED_EMAIL", "account_id": str(acc["id"]),
                          "provider": acc.get("provider")})
        if str(acc["id"]) not in owns_account_ids:
            flags.append({"code": "ORPHANED_ACCOUNT", "account_id": str(acc["id"])})

    for edge in edges["linked_via"]:
        if edge.get("confidence") == "LOW":
            flags.append({
                "code": "LOW_CONFIDENCE_LINK",
                "from": str(edge.get("in")),
                "to": str(edge.get("out")),
                "signal": edge.get("signal"),
            })

    return flags


# ── Mermaid graph builder ─────────────────────────────────────────────────────
def build_mermaid(person: dict, accounts: list[dict], edges: dict) -> str:
    lines = ["graph LR"]

    # Person node
    pid = str(person["id"]).replace(":", "_").replace("|", "_")
    pname = person.get("display_name") or person.get("canonical_email") or "Person"
    lines.append(f'  {pid}(["👤 {pname}"])')

    # Account nodes
    for acc in accounts:
        aid = str(acc["id"]).replace(":", "_").replace("|", "_")
        provider = acc.get("provider", "?")
        label = acc.get("email") or acc.get("username") or acc.get("provider_sub", "?")
        stale_mark = " ⚠" if acc.get("stale") else ""
        lines.append(f'  {aid}["{provider}: {label}{stale_mark}"]')

    # owns edges
    for edge in edges["owns"]:
        src = pid
        dst = str(edge.get("out", "")).replace(":", "_").replace("|", "_")
        lines.append(f"  {src} -->|owns| {dst}")

    # linked_via edges
    for edge in edges["linked_via"]:
        src = str(edge.get("in", "")).replace(":", "_").replace("|", "_")
        dst = str(edge.get("out", "")).replace(":", "_").replace("|", "_")
        conf = edge.get("confidence", "?")
        sig = edge.get("signal", "?")
        lines.append(f'  {src} -.->|"{conf}: {sig}"| {dst}')

    return "\n".join(lines)


# ── Markdown report builder ───────────────────────────────────────────────────
def build_markdown_report(
    person: dict,
    accounts: list[dict],
    edges: dict,
    flags: list[dict],
    tenant_id: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Identity Audit Report",
        f"",
        f"**Tenant:** `{tenant_id}`  ",
        f"**Person ID:** `{person['id']}`  ",
        f"**Generated:** {now}",
        f"",
        f"---",
        f"",
        f"## Identity Summary",
        f"",
        f"| Field | Value |",
        f"|---|---|",
        f"| Display name | {person.get('display_name') or '—'} |",
        f"| Canonical email | {person.get('canonical_email') or '—'} |",
        f"| Canonical phone | {person.get('canonical_phone') or '—'} |",
        f"| Linked accounts | {len(accounts)} |",
        f"| Providers | {', '.join(sorted({a.get('provider','?') for a in accounts}))} |",
        f"| Cross-provider links | {len(edges['linked_via'])} |",
        f"| Anomaly flags | {len(flags)} |",
        f"",
        f"---",
        f"",
        f"## Linked Accounts",
        f"",
        f"| Provider | Email | Username | Verified | Last seen | Stale |",
        f"|---|---|---|---|---|---|",
    ]
    for acc in accounts:
        verified = "✓" if acc.get("email_verified") else "✗"
        last = str(acc.get("last_seen", "—"))[:10]
        stale = "⚠️" if acc.get("stale") else "—"
        lines.append(
            f"| {acc.get('provider','?')} | {acc.get('email') or '—'} "
            f"| {acc.get('username') or '—'} | {verified} | {last} | {stale} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Identity Links (linked_via edges)",
        "",
        "| From | To | Confidence | Signal | Asserted |",
        "|---|---|---|---|---|",
    ]
    for edge in edges["linked_via"]:
        badge = CONFIDENCE_BADGE.get(edge.get("confidence", ""), "?")
        sig = SIGNAL_LABEL.get(edge.get("signal", ""), edge.get("signal", "?"))
        asserted = str(edge.get("asserted_at", "—"))[:10]
        lines.append(
            f"| `{edge.get('in')}` | `{edge.get('out')}` "
            f"| {badge} {edge.get('confidence')} | {sig} | {asserted} |"
        )

    if flags:
        lines += ["", "---", "", "## Anomaly Flags", ""]
        for f in flags:
            lines.append(f"- {_flag_label(f['code'])}")
            detail = {k: v for k, v in f.items() if k != "code"}
            if detail:
                lines.append(f"  ```\n  {detail}\n  ```")
    else:
        lines += ["", "---", "", "## Anomaly Flags", "", "✅ No anomalies detected."]

    lines += [
        "",
        "---",
        "",
        "## Compliance Notes",
        "",
        "- Data stored per DPDP Act 2023 (AWS ap-south-1, India residency)",
        "- Raw profile fields encrypted at rest (AES-256-GCM)",
        "- Hashed identifiers use per-tenant HMAC-SHA256",
        "- Right-to-erasure cascade available via `DELETE person:<id> FETCH account, identity_link`",
    ]

    return "\n".join(lines)


# ── main AUDIT entry point ────────────────────────────────────────────────────
async def audit(
    person_id: str,
    tenant_id: str,
    caller: str = "system",
    include_mermaid: bool = True,
    include_markdown: bool = True,
) -> dict:
    """
    Generate a full identity audit report for a person node.

    Returns:
        {
            "person": {...},
            "accounts": [...],
            "edges": {...},
            "anomaly_flags": [...],
            "mermaid": "graph LR ...",   # if include_mermaid
            "markdown": "# Identity ...", # if include_markdown
            "audited_at": "ISO timestamp",
        }
    """
    db = await get_db()
    try:
        # Load person
        person = await load_person(db, person_id, tenant_id)
        if not person:
            return {"error": "person_not_found", "person_id": person_id}

        # Load all edge sets
        edges = await load_all_edges(db, person_id)
        account_ids = edges["account_ids"]
        owns_account_ids = set(account_ids)

        # Load account details
        accounts = await load_account_details(db, account_ids)

        # Anomaly detection
        flags = detect_anomalies(accounts, edges, owns_account_ids)

        # Outputs
        result: dict[str, Any] = {
            "person": {
                "id": str(person["id"]),
                "display_name": person.get("display_name"),
                "canonical_email": person.get("canonical_email"),
                "canonical_phone": person.get("canonical_phone"),
            },
            "accounts": [
                {k: v for k, v in a.items() if k not in ("raw_profile_enc", "hashed_email", "hashed_phone")}
                for a in accounts
            ],
            "edges": {
                "owns":             [{"from": str(e.get("in")), "to": str(e.get("out"))} for e in edges["owns"]],
                "linked_via":       [{"from": str(e.get("in")), "to": str(e.get("out")),
                                      "confidence": e.get("confidence"), "signal": e.get("signal"),
                                      "asserted_at": str(e.get("asserted_at",""))} for e in edges["linked_via"]],
                "authenticated_by": [{"account": str(e.get("in")), "provider": str(e.get("out"))} for e in edges["authenticated_by"]],
                "accessed_from":    [{"account": str(e.get("in")), "session": str(e.get("out"))} for e in edges["accessed_from"]],
            },
            "anomaly_flags": flags,
            "audited_at": datetime.now(timezone.utc).isoformat(),
        }

        if include_mermaid:
            result["mermaid"] = build_mermaid(person, accounts, edges)

        if include_markdown:
            result["markdown"] = build_markdown_report(person, accounts, edges, flags, tenant_id)

        # Audit log
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='AUDIT', actor=$a, target_id=$tid, "
            "detail=$d, ts=time::now()",
            {"t": tenant_id, "a": caller, "tid": person_id,
             "d": f"{len(accounts)} accounts, {len(flags)} flags"},
        )

        return result

    finally:
        await db.close()


if __name__ == "__main__":
    import asyncio, json, sys
    if len(sys.argv) < 3:
        print("Usage: python audit.py <person_id> <tenant_id>")
        sys.exit(1)
    result = asyncio.run(audit(sys.argv[1], sys.argv[2]))
    # Print markdown if present, else JSON
    if "markdown" in result:
        print(result["markdown"])
        print("\n---\n")
        result.pop("markdown")
    print(json.dumps(result, indent=2, default=str))
