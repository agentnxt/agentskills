"""
autonomyx-identity-fabric — ENRICH mode
Fetches fresh profile data via the connector registry for stale account nodes,
re-derives linkage hashes, discovers new linked_via edges, and upserts into SurrealDB.

All provider I/O is delegated to scripts/connectors/.
This module owns: encryption, SurrealDB upsert, linkage detection, audit logging.
"""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from surrealdb import Surreal

from resolve import get_db, hmac_hash
from connectors import get_connector, ConnectorError, IdentityNode
from connectors.base import TokenExpiredError, RateLimitedError

# ── env ───────────────────────────────────────────────────────────────────────
ENC_KEY   = bytes.fromhex(os.environ["IDENTITY_FABRIC_ENC_KEY"])
HMAC_KEY  = os.environ["IDENTITY_FABRIC_HMAC_KEY"].encode()
TTL_HOURS = 24


# ── encryption ────────────────────────────────────────────────────────────────
def encrypt(plaintext: str) -> str:
    """AES-256-GCM encrypt. Returns base64(nonce + ciphertext)."""
    aesgcm = AESGCM(ENC_KEY)
    nonce  = os.urandom(12)
    ct     = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(blob: str) -> str:
    raw   = base64.b64decode(blob)
    nonce = raw[:12]
    ct    = raw[12:]
    return AESGCM(ENC_KEY).decrypt(nonce, ct, None).decode()


# ── SurrealDB upsert ──────────────────────────────────────────────────────────
async def upsert_account(db: Surreal, tenant_id: str, node: IdentityNode) -> str:
    """Upsert an IdentityNode into SurrealDB. Returns the record ID string."""
    record_id = f"account:`{node.provider}|{node.provider_sub}`"

    raw_email = node.email
    raw_phone = node.phone
    h_email   = hmac_hash(raw_email, tenant_id) if raw_email else None
    h_phone   = hmac_hash(raw_phone, tenant_id) if raw_phone else None
    enc_blob  = encrypt(json.dumps(node.raw_profile or {}))
    ttl       = (datetime.now(timezone.utc) + timedelta(hours=TTL_HOURS)).isoformat()

    await db.query(
        """
        UPSERT $id SET
          tenant_id         = $tenant,
          provider          = $provider,
          provider_sub      = $sub,
          email             = $email,
          email_verified    = $ev,
          phone             = $phone,
          username          = $username,
          display_name      = $display_name,
          profile_photo_url = $photo,
          bio               = $bio,
          org               = $org,
          location          = $location,
          hashed_email      = $he,
          hashed_phone      = $hp,
          raw_profile_enc   = $enc,
          stale             = false,
          ttl_refresh_at    = $ttl,
          last_seen         = time::now()
        """,
        {
            "id":           record_id,
            "tenant":       tenant_id,
            "provider":     node.provider,
            "sub":          node.provider_sub,
            "email":        raw_email,
            "ev":           node.email_verified,
            "phone":        raw_phone,
            "username":     node.username,
            "display_name": node.display_name,
            "photo":        node.profile_photo_url,
            "bio":          node.bio,
            "org":          node.org,
            "location":     node.location,
            "he":           h_email,
            "hp":           h_phone,
            "enc":          enc_blob,
            "ttl":          ttl,
        },
    )
    return record_id


# ── linkage discovery ─────────────────────────────────────────────────────────
async def discover_and_write_links(
    db: Surreal,
    tenant_id: str,
    new_account_id: str,
    node: IdentityNode,
) -> list[dict]:
    """
    Find other accounts that share hashed_email, hashed_phone, or provider stubs
    (from Logto/Auth0 identity maps) and write linked_via edges for each match.
    Returns list of new edge dicts created.
    """
    new_edges: list[dict] = []

    # email-based
    if node.email and not node.is_private_relay_email():
        h          = hmac_hash(node.email, tenant_id)
        confidence = "HIGH"  if node.email_verified else "MEDIUM"
        signal     = "verified_email_match" if node.email_verified else "unverified_email_match"
        result     = await db.query(
            "SELECT id FROM account WHERE hashed_email = $h AND id != $me AND tenant_id = $t",
            {"h": h, "me": new_account_id, "t": tenant_id},
        )
        for peer in (result[0].get("result", []) if result else []):
            await _upsert_link(db, new_account_id, str(peer["id"]), confidence, signal)
            new_edges.append(_edge(new_account_id, str(peer["id"]), confidence, signal))

    # phone-based
    if node.phone:
        h      = hmac_hash(node.phone, tenant_id)
        result = await db.query(
            "SELECT id FROM account WHERE hashed_phone = $h AND id != $me AND tenant_id = $t",
            {"h": h, "me": new_account_id, "t": tenant_id},
        )
        for peer in (result[0].get("result", []) if result else []):
            await _upsert_link(db, new_account_id, str(peer["id"]), "HIGH", "phone_match")
            new_edges.append(_edge(new_account_id, str(peer["id"]), "HIGH", "phone_match"))

    # stub-based (Logto / Auth0 identities map)
    for stub in node.linked_account_stubs or []:
        p   = stub.get("provider", "")
        sub = stub.get("provider_sub", "")
        if not p or not sub:
            continue
        result = await db.query(
            "SELECT id FROM account WHERE provider = $p AND provider_sub = $s AND tenant_id = $t",
            {"p": p, "s": sub, "t": tenant_id},
        )
        for row in (result[0].get("result", []) if result else []):
            await _upsert_link(db, new_account_id, str(row["id"]), "HIGH", "logto_session")
            new_edges.append(_edge(new_account_id, str(row["id"]), "HIGH", "logto_session"))

    return new_edges


async def _upsert_link(db, from_id, to_id, confidence, signal):
    await db.query(
        """
        IF NOT EXISTS (SELECT * FROM linked_via WHERE in = $a AND out = $b) THEN
          RELATE $a->linked_via->$b SET
            confidence  = $c,
            signal      = $s,
            asserted_at = time::now(),
            asserted_by = 'system'
        END
        """,
        {"a": from_id, "b": to_id, "c": confidence, "s": signal},
    )


def _edge(from_id, to_id, confidence, signal):
    return {"type": "linked_via", "from": from_id, "to": to_id,
            "confidence": confidence, "signal": signal}


# ── main ENRICH entry point ───────────────────────────────────────────────────
async def enrich(
    account_ids: list[str],
    tenant_id: str,
    tokens: dict[str, str],
    caller: str = "system",
) -> dict:
    """
    Enrich a list of account node IDs with fresh data from their provider.

    tokens: {account_id -> OAuth access token}
            Empty string = no token; node is marked stale.

    Returns:
        {enriched_count, skipped_count, new_edges, details}
    """
    db              = await get_db()
    results:         list[dict] = []
    total_new_edges: list[dict] = []

    try:
        node_result = await db.query("SELECT * FROM $ids", {"ids": account_ids})
        db_nodes    = node_result[0].get("result", []) if node_result else []

        for db_node in db_nodes:
            account_id = str(db_node["id"])
            provider   = db_node.get("provider", "")
            token      = tokens.get(account_id, "")

            # no token
            if not token:
                await db.query("UPDATE $id SET stale = true", {"id": account_id})
                results.append({"account_id": account_id, "status": "skipped_no_token"})
                continue

            # get connector from registry
            try:
                connector = get_connector(provider)
            except ConnectorError:
                results.append({"account_id": account_id, "status": "unsupported_provider", "provider": provider})
                continue

            # call provider API
            identity_node: Optional[IdentityNode] = None
            try:
                identity_node = await connector.resolve(
                    identifier=db_node.get("provider_sub", ""),
                    token=token,
                )
            except TokenExpiredError:
                await db.query("UPDATE $id SET stale = true", {"id": account_id})
                results.append({"account_id": account_id, "status": "token_expired"})
                continue
            except RateLimitedError as e:
                await db.query("UPDATE $id SET stale = true", {"id": account_id})
                results.append({"account_id": account_id, "status": "rate_limited", "retry_after": e.retry_after})
                continue
            except ConnectorError as e:
                await db.query("UPDATE $id SET stale = true", {"id": account_id})
                results.append({"account_id": account_id, "status": "fetch_error", "error": str(e)})
                continue

            if identity_node is None:
                results.append({"account_id": account_id, "status": "not_found_at_provider"})
                continue

            # upsert + link discovery
            upserted_id = await upsert_account(db, tenant_id, identity_node)
            new_edges   = await discover_and_write_links(db, tenant_id, upserted_id, identity_node)
            total_new_edges.extend(new_edges)
            results.append({"account_id": account_id, "status": "enriched", "new_edges": len(new_edges)})

        # audit log
        enriched = [r for r in results if r["status"] == "enriched"]
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='ENRICH', actor=$a, detail=$d, ts=time::now()",
            {"t": tenant_id, "a": caller,
             "d": f"enriched={len(enriched)}/{len(results)}, new_edges={len(total_new_edges)}"},
        )

        return {
            "enriched_count": len(enriched),
            "skipped_count":  len(results) - len(enriched),
            "new_edges":      total_new_edges,
            "details":        results,
        }

    finally:
        await db.close()


if __name__ == "__main__":
    print("ENRICH module — import and call enrich(account_ids, tenant_id, tokens)")
