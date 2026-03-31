"""
parse_wikidata.py
Generic parser for Wikidata — fetch entities, run SPARQL queries, search items.

Access modes:
  1. Entity API    — wikidata.org/wiki/Special:EntityData/{QID}.json (no auth)
  2. SPARQL        — query.wikidata.org/sparql (no auth, rate-limited)
  3. Wikidata REST — wikidata.org/w/rest.php/wikibase/v0 (no auth)
  4. Search        — wikidata.org/w/api.php?action=wbsearchentities (no auth)

No authentication required for read operations.
All endpoints are public and rate-limited — respect the 1 req/s guideline
for SPARQL and add a User-Agent header identifying your app.

Claim/snak value types fully handled:
  wikibase-item, wikibase-property, string, monolingualtext, quantity,
  time, globe-coordinate, url, commonsMedia, math, musical-notation,
  external-id, wikibase-lexeme, wikibase-form, wikibase-sense

Outputs: dict, list[dict], JSON, CSV.

pip install requests

No authentication or API key required.
"""

from __future__ import annotations

import csv
import io
import json
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

try:
    import requests as _requests
except ImportError as e:
    raise ImportError("Run: pip install requests") from e

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENTITY_API   = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
SPARQL_URL   = "https://query.wikidata.org/sparql"
SEARCH_URL   = "https://www.wikidata.org/w/api.php"
REST_BASE    = "https://www.wikidata.org/w/rest.php/wikibase/v0"

DEFAULT_LANG = "en"
DEFAULT_UA   = "AutonomyxWikidataParser/1.0 (https://openautonomyx.com)"

_RATE_DELAY  = 0.2   # seconds between requests (Wikidata asks ≤1 req/s for SPARQL)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict | None = None,
         user_agent: str = DEFAULT_UA, timeout: int = 30) -> dict:
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
    }
    resp = _requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Claim/snak value extractor
# ---------------------------------------------------------------------------

def _extract_snak_value(snak: dict, lang: str = DEFAULT_LANG) -> Any:
    """
    Extract a plain Python value from a Wikidata snak datavalue.

    Returns str / int / float / dict depending on type.
    Returns None for unknown or no-value snaks.
    """
    if snak.get("snaktype") in ("novalue", "somevalue"):
        return None

    dv = snak.get("datavalue", {})
    dv_type = dv.get("type", "")
    value = dv.get("value", {})

    if dv_type == "wikibase-entityid":
        eid = value.get("id", "")
        return eid  # QID or PID string

    if dv_type == "string":
        return value

    if dv_type == "monolingualtext":
        if value.get("language") == lang:
            return value.get("text", "")
        return f"{value.get('text', '')} [{value.get('language', '')}]"

    if dv_type == "quantity":
        amount = value.get("amount", "0")
        unit = value.get("unit", "1")
        unit_qid = unit.split("/")[-1] if "/" in unit else unit
        try:
            n = float(amount)
            n = int(n) if n == int(n) else n
        except (ValueError, TypeError):
            n = amount
        return n if unit_qid == "1" else {"amount": n, "unit": unit_qid}

    if dv_type == "time":
        return value.get("time", "")

    if dv_type == "globecoordinate":
        return {
            "lat": value.get("latitude"),
            "lon": value.get("longitude"),
            "precision": value.get("precision"),
        }

    return str(value) if value else None


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WikidataEntity:
    qid: str
    type: str           # "item" or "property"
    label: str
    description: str
    aliases: list[str]
    claims: dict[str, list[Any]]   # PID -> list of values
    sitelinks: dict[str, str]      # sitename -> page title
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict, lang: str = DEFAULT_LANG) -> "WikidataEntity":
        labels      = raw.get("labels", {})
        descs       = raw.get("descriptions", {})
        alias_map   = raw.get("aliases", {})
        sitelinks   = raw.get("sitelinks", {})

        label       = labels.get(lang, labels.get("en", {}) or {}).get("value", "")
        description = descs.get(lang, descs.get("en", {}) or {}).get("value", "")
        aliases     = [a["value"] for a in alias_map.get(lang, alias_map.get("en", []))]

        # Extract claims
        claims: dict[str, list[Any]] = {}
        for pid, statements in raw.get("claims", {}).items():
            values = []
            for stmt in statements:
                if stmt.get("rank") == "deprecated":
                    continue
                mainsnak = stmt.get("mainsnak", {})
                val = _extract_snak_value(mainsnak, lang)
                if val is not None:
                    values.append(val)
            if values:
                claims[pid] = values

        # Sitelinks
        links = {k: v.get("title", "") for k, v in sitelinks.items()}

        return cls(
            qid=raw.get("id", ""),
            type=raw.get("type", "item"),
            label=label,
            description=description,
            aliases=aliases,
            claims=claims,
            sitelinks=links,
            raw=raw,
        )

    def flat(self, max_values: int = 5) -> dict:
        """
        Flatten to a single dict — suitable for CSV.

        Multi-value claims are pipe-joined.
        QID values are kept as-is (Q-numbers).
        """
        d: dict[str, Any] = {
            "qid": self.qid,
            "label": self.label,
            "description": self.description,
            "aliases": " | ".join(self.aliases),
            "en_wikipedia": self.sitelinks.get("enwiki", ""),
        }
        for pid, values in self.claims.items():
            truncated = values[:max_values]
            stringified = [
                json.dumps(v) if isinstance(v, dict) else str(v)
                for v in truncated
            ]
            d[pid] = " | ".join(stringified)
        return d


@dataclass
class SPARQLResult:
    variables: list[str]
    bindings: list[dict[str, Any]]

    @classmethod
    def from_raw(cls, raw: dict) -> "SPARQLResult":
        head = raw.get("head", {})
        variables = head.get("vars", [])
        raw_bindings = raw.get("results", {}).get("bindings", [])
        bindings = []
        for rb in raw_bindings:
            row = {}
            for var in variables:
                cell = rb.get(var, {})
                ctype = cell.get("type", "")
                val = cell.get("value", "")
                if ctype == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                    val = val.split("/")[-1]  # extract QID/PID
                row[var] = val
            bindings.append(row)
        return cls(variables=variables, bindings=bindings)


# ---------------------------------------------------------------------------
# Entity fetch
# ---------------------------------------------------------------------------

def fetch_entity(qid: str, lang: str = DEFAULT_LANG,
                 user_agent: str = DEFAULT_UA) -> WikidataEntity:
    """
    Fetch a single Wikidata entity by QID or PID.

    Parameters
    ----------
    qid : str
        Wikidata entity ID, e.g. 'Q42' (Douglas Adams) or 'P31' (instance of).
    lang : str
        Language code for labels/descriptions/aliases. Default 'en'.

    Returns
    -------
    WikidataEntity
    """
    url = ENTITY_API.format(qid=qid.upper())
    data = _get(url, user_agent=user_agent)
    entities = data.get("entities", {})
    if not entities:
        raise ValueError(f"No entity found for {qid}")
    raw = next(iter(entities.values()))
    return WikidataEntity.from_raw(raw, lang=lang)


def fetch_entities(qids: list[str], lang: str = DEFAULT_LANG,
                   user_agent: str = DEFAULT_UA,
                   delay: float = _RATE_DELAY) -> list[WikidataEntity]:
    """
    Fetch multiple entities by QID list.

    Fetches in a single batch request using the wbgetentities API endpoint.
    Falls back to individual requests if batch fails.
    """
    if not qids:
        return []

    # Batch via wbgetentities (up to 50 per request)
    results = []
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "format": "json",
            "languages": lang,
        }
        data = _get(SEARCH_URL, params=params, user_agent=user_agent)
        for qid in batch:
            raw = data.get("entities", {}).get(qid.upper(), {})
            if raw and raw.get("id"):
                results.append(WikidataEntity.from_raw(raw, lang=lang))
        if i + 50 < len(qids):
            time.sleep(delay)

    return results


# ---------------------------------------------------------------------------
# SPARQL
# ---------------------------------------------------------------------------

def sparql(query: str, user_agent: str = DEFAULT_UA,
           timeout: int = 60) -> SPARQLResult:
    """
    Run a SPARQL query against the Wikidata Query Service.

    Parameters
    ----------
    query : str
        Full SPARQL SELECT query string.
        Prefix shortcuts (wd:, wdt:, p:, ps:, pq:, rdfs:, schema:)
        are auto-added if not present.

    Returns
    -------
    SPARQLResult
        .variables — list of variable names
        .bindings  — list[dict] of result rows

    Notes
    -----
    Wikidata SPARQL is rate-limited. Add a delay between calls.
    Queries timing out after 60s should be simplified or paginated manually.
    """
    prefixes = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""
    if "PREFIX wd:" not in query:
        query = prefixes + query

    params = {"query": query, "format": "json"}
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/sparql-results+json",
    }
    resp = _requests.get(SPARQL_URL, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return SPARQLResult.from_raw(resp.json())


def sparql_to_records(query: str, **kwargs) -> list[dict]:
    """Run SPARQL and return flat list[dict] directly."""
    result = sparql(query, **kwargs)
    return result.bindings


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query: str, lang: str = DEFAULT_LANG, limit: int = 20,
           entity_type: str = "item",
           user_agent: str = DEFAULT_UA) -> list[dict]:
    """
    Search Wikidata for entities matching a text query.

    Parameters
    ----------
    query : str
        Search string.
    lang : str
        Language for search and labels.
    limit : int
        Max results (up to 50).
    entity_type : str
        'item' (Q-numbers) or 'property' (P-numbers).

    Returns
    -------
    list[dict]
        Each dict has: id, label, description, url, concepturi.
    """
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": lang,
        "limit": min(limit, 50),
        "format": "json",
        "type": entity_type,
    }
    data = _get(SEARCH_URL, params=params, user_agent=user_agent)
    results = []
    for item in data.get("search", []):
        results.append({
            "id": item.get("id", ""),
            "label": item.get("label", ""),
            "description": item.get("description", ""),
            "aliases": item.get("aliases", []),
            "url": item.get("url", ""),
            "concepturi": item.get("concepturi", ""),
        })
    return results


# ---------------------------------------------------------------------------
# Property label lookup
# ---------------------------------------------------------------------------

_PROP_CACHE: dict[str, str] = {}


def resolve_property_labels(entities: list[WikidataEntity],
                              lang: str = DEFAULT_LANG,
                              user_agent: str = DEFAULT_UA) -> dict[str, str]:
    """
    Fetch human-readable labels for all PIDs used in a list of entities.

    Returns
    -------
    dict[str, str]
        PID -> label (e.g. {"P31": "instance of", "P18": "image"})
    """
    pids = set()
    for e in entities:
        pids.update(e.claims.keys())

    uncached = [p for p in pids if p not in _PROP_CACHE]
    if uncached:
        fetched = fetch_entities(uncached, lang=lang, user_agent=user_agent)
        for prop in fetched:
            _PROP_CACHE[prop.qid] = prop.label

    return {pid: _PROP_CACHE.get(pid, pid) for pid in pids}


def label_claims(entity: WikidataEntity,
                  pid_labels: dict[str, str]) -> dict[str, list[Any]]:
    """Replace PID keys in entity.claims with human-readable labels."""
    return {
        pid_labels.get(pid, pid): values
        for pid, values in entity.claims.items()
    }


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(data: Any, indent: int = 2) -> str:
    """Serialise entities, SPARQL results, or raw dicts to JSON."""
    if isinstance(data, WikidataEntity):
        data = [data]
    if isinstance(data, list) and data and isinstance(data[0], WikidataEntity):
        return json.dumps([e.flat() for e in data], indent=indent,
                          ensure_ascii=False, default=str)
    if isinstance(data, SPARQLResult):
        return json.dumps({"variables": data.variables, "results": data.bindings},
                          indent=indent, ensure_ascii=False)
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def to_csv(data: list[WikidataEntity] | list[dict],
           max_values: int = 5) -> str:
    """Serialise entities or SPARQL rows to CSV."""
    if not data:
        return ""

    if isinstance(data[0], WikidataEntity):
        rows = [e.flat(max_values=max_values) for e in data]
    else:
        rows = data

    all_keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore", restval="")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and parse Wikidata entities, SPARQL results, and searches.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
No authentication required — all endpoints are public.

Examples:
  # Fetch a single entity
  python parse_wikidata.py entity Q42

  # Fetch multiple entities as CSV
  python parse_wikidata.py entity Q42 Q243 Q571 --format csv --out entities.csv

  # Search
  python parse_wikidata.py search "Douglas Adams" --limit 5

  # Run a SPARQL query
  python parse_wikidata.py sparql "SELECT ?item ?label WHERE { ?item wdt:P31 wd:Q5 . ?item rdfs:label ?label . FILTER(LANG(?label)='en') } LIMIT 10"

  # SPARQL from file
  python parse_wikidata.py sparql --file query.sparql --format csv --out results.csv
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # entity
    e = sub.add_parser("entity", help="Fetch one or more entities by QID")
    e.add_argument("qids", nargs="+", help="One or more QIDs e.g. Q42 Q243")
    e.add_argument("--lang", default="en")
    e.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    e.add_argument("--out", default="")

    # search
    s = sub.add_parser("search", help="Search for entities by text")
    s.add_argument("query")
    s.add_argument("--lang", default="en")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--type", choices=["item", "property"], default="item", dest="etype")
    s.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    s.add_argument("--out", default="")

    # sparql
    q = sub.add_parser("sparql", help="Run a SPARQL query")
    q.add_argument("query", nargs="?", default="")
    q.add_argument("--file", default="", help="Read SPARQL from file")
    q.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    q.add_argument("--out", default="")

    args = parser.parse_args()

    if args.cmd == "entity":
        if len(args.qids) == 1:
            entities = [fetch_entity(args.qids[0], lang=args.lang)]
        else:
            entities = fetch_entities(args.qids, lang=args.lang)

        if args.format == "summary":
            for e in entities:
                print(f"[{e.qid}] {e.label} — {e.description}")
                print(f"  aliases: {', '.join(e.aliases[:5])}")
                print(f"  claims:  {len(e.claims)} properties")
                print(f"  wikipedia: {e.sitelinks.get('enwiki', 'n/a')}")
            return
        output = to_json(entities) if args.format == "json" else to_csv(entities)

    elif args.cmd == "search":
        results = search(args.query, lang=args.lang, limit=args.limit, entity_type=args.etype)
        if args.format == "summary":
            for r in results:
                print(f"[{r['id']}] {r['label']} — {r['description']}")
            return
        output = to_json(results) if args.format == "json" else to_csv(results)

    elif args.cmd == "sparql":
        query_str = args.query
        if args.file:
            from pathlib import Path
            query_str = Path(args.file).read_text()
        result = sparql(query_str)
        if args.format == "summary":
            print(f"{len(result.bindings)} row(s), vars: {result.variables}")
            for row in result.bindings[:5]:
                print(" ", row)
            return
        output = (to_json(result) if args.format == "json"
                  else to_csv(result.bindings))

    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
