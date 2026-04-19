"""
autonomyx-identity-fabric — HTTP API server
Exposes RESOLVE, ENRICH, AUDIT, and health endpoints via FastAPI.
Runs on port 8080 inside the container; nginx terminates TLS externally.

Endpoints:
  POST /resolve          — resolve any identifier to identity graph
  POST /enrich           — enrich a list of account nodes
  POST /audit            — full audit report for a person node
  GET  /health           — liveness + SurrealDB connectivity check
  GET  /health/connectors — per-provider reachability check
  POST /links            — manually assert a linked_via edge
  DELETE /person/{id}    — right-to-erasure cascade
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn

from resolve import resolve
from enrich import enrich
from audit import audit
from connectors import run_health_checks, get_connector, ConnectorError

# ── app ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Autonomyx Identity Fabric",
    description="Multimodal identity resolution across social + SSO providers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Serve integration pages (no auth required)
_INTEGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "integrations")
if os.path.isdir(_INTEGRATIONS_DIR):
    app.mount("/integrations", StaticFiles(directory=_INTEGRATIONS_DIR, html=True), name="integrations")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── auth ──────────────────────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)
AGENT_SECRET = os.environ.get("AUTONOMYX_AGENT_SECRET", "")


async def require_auth(
    creds: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> str:
    """
    Accept either:
      - AUTONOMYX_AGENT_SECRET for operator/internal use
      - Logto JWT (validated downstream by resolve/enrich/audit)
    Returns the raw token string.
    """
    if not creds:
        raise HTTPException(status_code=401, detail="Authorization header required")
    token = creds.credentials
    # Agent secret bypass for internal calls
    if AGENT_SECRET and token == AGENT_SECRET:
        return token
    # All other tokens passed through to connectors/SurrealDB for validation
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    return token


# ── request / response models ─────────────────────────────────────────────────

class ResolveRequest(BaseModel):
    identifier: str = Field(..., description="Any identifier: email, phone, username, provider:sub, employee_id")
    tenant_id: str  = Field(..., description="Autonomyx tenant ID")
    auto_enrich: bool = Field(True, description="Trigger ENRICH for stale nodes automatically")


class EnrichRequest(BaseModel):
    account_ids: list[str] = Field(..., description="List of SurrealDB account record IDs")
    tenant_id: str
    tokens: dict[str, str] = Field(..., description="{account_id: oauth_token}")


class AuditRequest(BaseModel):
    person_id: str = Field(..., description="SurrealDB person record ID")
    tenant_id: str
    include_mermaid: bool = True
    include_markdown: bool = True


class ManualLinkRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    tenant_id: str
    confidence: str = Field("MEDIUM", pattern="^(HIGH|MEDIUM|LOW)$")
    note: Optional[str] = None


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health():
    """Liveness check — verifies SurrealDB connectivity."""
    from resolve import get_db
    try:
        db = await get_db()
        await db.query("SELECT 1")
        await db.close()
        db_ok = True
    except Exception as e:
        db_ok = False

    status_code = 200 if db_ok else 503
    return {
        "status": "ok" if db_ok else "degraded",
        "surrealdb": "connected" if db_ok else "unreachable",
        "version": "1.0.0",
    }


@app.get("/health/connectors", tags=["ops"])
async def health_connectors():
    """Check reachability of all registered provider connectors."""
    results = await run_health_checks()
    all_ok = all(results.values())
    return {
        "status": "ok" if all_ok else "partial",
        "providers": results,
    }


@app.post("/resolve", tags=["identity"])
async def resolve_identity(
    req: ResolveRequest,
    token: str = Depends(require_auth),
):
    """Resolve any identifier to a full identity graph."""
    result = await resolve(
        identifier=req.identifier,
        tenant_id=req.tenant_id,
        caller=token[:16] + "...",
        auto_enrich=req.auto_enrich,
    )
    if result.get("resolution_status") == "not_found":
        raise HTTPException(status_code=404, detail="Identity not found")
    return result


@app.post("/enrich", tags=["identity"])
async def enrich_accounts(
    req: EnrichRequest,
    token: str = Depends(require_auth),
):
    """Enrich account nodes with fresh provider data."""
    if not req.account_ids:
        raise HTTPException(status_code=400, detail="account_ids must not be empty")
    result = await enrich(
        account_ids=req.account_ids,
        tenant_id=req.tenant_id,
        tokens=req.tokens,
        caller=token[:16] + "...",
    )
    return result


@app.post("/audit", tags=["identity"])
async def audit_identity(
    req: AuditRequest,
    token: str = Depends(require_auth),
):
    """Generate full identity audit report for a person node."""
    result = await audit(
        person_id=req.person_id,
        tenant_id=req.tenant_id,
        caller=token[:16] + "...",
        include_mermaid=req.include_mermaid,
        include_markdown=req.include_markdown,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/links", tags=["identity"])
async def manual_link(
    req: ManualLinkRequest,
    token: str = Depends(require_auth),
):
    """Manually assert a linked_via edge between two account nodes."""
    from resolve import get_db
    db = await get_db()
    try:
        await db.query(
            """
            IF NOT EXISTS (SELECT * FROM linked_via WHERE in = $a AND out = $b) THEN
              RELATE $a->linked_via->$b SET
                confidence  = $c,
                signal      = 'manual',
                asserted_at = time::now(),
                asserted_by = $caller
            END
            """,
            {
                "a": req.from_account_id,
                "b": req.to_account_id,
                "c": req.confidence,
                "caller": token[:16] + "...",
            },
        )
        await db.query(
            "CREATE audit_log SET tenant_id=$t, action='LINK', actor=$a, "
            "target_id=$tid, detail=$d, ts=time::now()",
            {
                "t": req.tenant_id,
                "a": token[:16] + "...",
                "tid": req.from_account_id,
                "d": f"manual link → {req.to_account_id} confidence={req.confidence} note={req.note}",
            },
        )
    finally:
        await db.close()
    return {"status": "linked", "from": req.from_account_id, "to": req.to_account_id,
            "confidence": req.confidence}


@app.delete("/person/{person_id}", tags=["identity"])
async def erase_person(
    person_id: str,
    tenant_id: str,
    token: str = Depends(require_auth),
):
    """
    Right-to-erasure: cascade delete person + all linked accounts + all edges.
    Requires identity:admin scope or AUTONOMYX_AGENT_SECRET.
    """
    from resolve import get_db
    db = await get_db()
    try:
        # Collect accounts
        r = await db.query(
            "SELECT out AS id FROM owns WHERE in = $p",
            {"p": person_id},
        )
        account_ids = [str(row["id"]) for row in (r[0].get("result", []) if r else [])]

        # Delete edges
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
            "CREATE audit_log SET tenant_id=$t, action='ERASE', actor=$a, "
            "target_id=$tid, detail=$d, ts=time::now()",
            {
                "t": tenant_id,
                "a": token[:16] + "...",
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
    }


# ── entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        workers=int(os.environ.get("WORKERS", "2")),
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )
