"""
parse_airtable.py
Generic parser for Airtable — fetch, flatten, filter, and export any base/table.

Covers:
  - List records (all pages, auto-paginated)
  - Filter by formula
  - Sort by fields
  - Select specific fields
  - Fetch base schema (tables + field definitions)
  - Search records (field value match)
  - Upsert / create / update / delete records
  - Batch operations (chunked automatically)

Outputs: list[dict], JSON, CSV.

pip install pyairtable

Environment:
  AIRTABLE_TOKEN — Personal Access Token from airtable.com/account
"""

from __future__ import annotations

import csv
import io
import json
import os
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _token() -> str:
    token = os.environ.get("AIRTABLE_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "Set AIRTABLE_TOKEN to your Airtable Personal Access Token. "
            "Get one at: https://airtable.com/account"
        )
    return token


def _api(token: str | None = None):
    try:
        from pyairtable import Api
    except ImportError as e:
        raise ImportError("Run: pip install pyairtable") from e
    return Api(token or _token())


def _table(base_id: str, table_name: str, token: str | None = None):
    return _api(token).table(base_id, table_name)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AirtableRecord:
    id: str
    created_time: str
    fields: dict[str, Any]

    @classmethod
    def from_raw(cls, raw: dict) -> "AirtableRecord":
        return cls(
            id=raw.get("id", ""),
            created_time=raw.get("createdTime", ""),
            fields=raw.get("fields", {}),
        )

    def flat(self) -> dict:
        """Flatten fields into a single dict with id + createdTime prefix."""
        return {"_id": self.id, "_created": self.created_time, **self.fields}


@dataclass
class AirtableSchema:
    base_id: str
    tables: list[dict] = field(default_factory=list)

    def table_names(self) -> list[str]:
        return [t["name"] for t in self.tables]

    def fields_for(self, table_name: str) -> list[dict]:
        for t in self.tables:
            if t["name"] == table_name or t["id"] == table_name:
                return t.get("fields", [])
        return []


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def fetch_all(base_id: str, table_name: str,
              fields: list[str] | None = None,
              formula: str = "",
              sort: list[dict] | None = None,
              view: str = "",
              token: str | None = None) -> list[AirtableRecord]:
    """
    Fetch all records from a table, auto-paginating.

    Parameters
    ----------
    base_id : str
        Airtable base ID (starts with 'app').
    table_name : str
        Table name or table ID.
    fields : list[str] | None
        Field names to include. None = all fields.
    formula : str
        Airtable formula string to filter records.
        e.g. "AND({Status}='Active', {Age}>30)"
    sort : list[dict] | None
        Sort spec: [{"field": "Name", "direction": "asc"}]
    view : str
        View name or ID to use.
    token : str | None
        Override token (else reads AIRTABLE_TOKEN env var).

    Returns
    -------
    list[AirtableRecord]
    """
    tbl = _table(base_id, table_name, token)
    kwargs: dict[str, Any] = {}
    if fields:
        kwargs["fields"] = fields
    if formula:
        kwargs["formula"] = formula
    if sort:
        kwargs["sort"] = sort
    if view:
        kwargs["view"] = view

    raw_records = tbl.all(**kwargs)
    return [AirtableRecord.from_raw(r) for r in raw_records]


def fetch_record(base_id: str, table_name: str, record_id: str,
                 token: str | None = None) -> AirtableRecord:
    """Fetch a single record by its record ID."""
    tbl = _table(base_id, table_name, token)
    raw = tbl.get(record_id)
    return AirtableRecord.from_raw(raw)


def search(base_id: str, table_name: str, field_name: str, value: str,
           token: str | None = None) -> list[AirtableRecord]:
    """
    Search records where field_name exactly matches value.

    Uses Airtable formula: {field_name}='value'
    """
    tbl = _table(base_id, table_name, token)
    raw_records = tbl.search(field_name, value)
    return [AirtableRecord.from_raw(r) for r in raw_records]


def fetch_schema(base_id: str, token: str | None = None) -> AirtableSchema:
    """
    Fetch the schema of a base — all tables and their field definitions.

    Returns
    -------
    AirtableSchema
        Contains table names, IDs, and field metadata.
    """
    api = _api(token)
    base = api.base(base_id)
    schema = base.schema()
    tables = []
    for tbl in schema.tables:
        tables.append({
            "id": tbl.id,
            "name": tbl.name,
            "fields": [
                {"id": f.id, "name": f.name, "type": f.type}
                for f in tbl.fields
            ],
            "views": [{"id": v.id, "name": v.name, "type": v.type}
                      for v in tbl.views],
        })
    return AirtableSchema(base_id=base_id, tables=tables)


def list_bases(token: str | None = None) -> list[dict]:
    """
    List all bases accessible with the current token.

    Returns list of dicts with 'id', 'name', 'permissionLevel'.
    """
    api = _api(token)
    workspaces = api.workspaces()
    bases = []
    for ws in workspaces:
        for b in ws.bases:
            bases.append({
                "workspace_id": ws.id,
                "workspace_name": ws.name,
                "base_id": b.id,
                "base_name": b.name,
                "permission_level": b.permission_level,
            })
    return bases


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def create(base_id: str, table_name: str,
           fields: dict | list[dict],
           token: str | None = None) -> list[AirtableRecord]:
    """
    Create one or more records.

    Parameters
    ----------
    fields : dict | list[dict]
        A single record's fields dict, or a list of field dicts.

    Returns
    -------
    list[AirtableRecord]
        Created records (with assigned IDs).
    """
    tbl = _table(base_id, table_name, token)
    if isinstance(fields, dict):
        fields = [fields]
    # pyairtable batch-creates automatically in chunks of 10
    created = tbl.batch_create(fields)
    return [AirtableRecord.from_raw(r) for r in created]


def update(base_id: str, table_name: str, record_id: str,
           fields: dict, token: str | None = None) -> AirtableRecord:
    """Update a single record by ID (PATCH — only specified fields changed)."""
    tbl = _table(base_id, table_name, token)
    raw = tbl.update(record_id, fields)
    return AirtableRecord.from_raw(raw)


def batch_update(base_id: str, table_name: str,
                 updates: list[dict],
                 token: str | None = None) -> list[AirtableRecord]:
    """
    Batch update records.

    Parameters
    ----------
    updates : list[dict]
        Each dict must have 'id' and 'fields' keys.
        e.g. [{"id": "recXXX", "fields": {"Status": "Done"}}]
    """
    tbl = _table(base_id, table_name, token)
    updated = tbl.batch_update(updates)
    return [AirtableRecord.from_raw(r) for r in updated]


def upsert(base_id: str, table_name: str,
           records: list[dict], key_fields: list[str],
           token: str | None = None) -> dict:
    """
    Upsert records — update if matching key_fields exist, else create.

    Parameters
    ----------
    records : list[dict]
        List of field dicts (no 'id' needed).
    key_fields : list[str]
        Fields used to match existing records.

    Returns
    -------
    dict with 'created', 'updated' counts and 'records' list.
    """
    tbl = _table(base_id, table_name, token)
    result = tbl.batch_upsert(records, key_fields=key_fields)
    return {
        "created": result.created_records,
        "updated": result.updated_records,
        "records": [AirtableRecord.from_raw(r) for r in result.records],
    }


def delete(base_id: str, table_name: str,
           record_ids: str | list[str],
           token: str | None = None) -> list[str]:
    """
    Delete one or more records by ID.

    Returns list of deleted record IDs.
    """
    tbl = _table(base_id, table_name, token)
    if isinstance(record_ids, str):
        record_ids = [record_ids]
    return tbl.batch_delete(record_ids)


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_flat_records(records: list[AirtableRecord]) -> list[dict]:
    """Flatten records to list[dict] — suitable for CSV/DataFrame/SurrealDB."""
    return [r.flat() for r in records]


def to_json(records: list[AirtableRecord] | dict, indent: int = 2) -> str:
    """Serialise records or schema dict to JSON string."""
    if isinstance(records, dict):
        return json.dumps(records, indent=indent, ensure_ascii=False, default=str)
    return json.dumps([r.flat() for r in records], indent=indent,
                      ensure_ascii=False, default=str)


def to_csv(records: list[AirtableRecord]) -> str:
    """Serialise records to CSV. All field values are stringified."""
    flat = to_flat_records(records)
    if not flat:
        return ""
    # collect all keys across all records (fields can differ between records)
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in flat:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore",
                            restval="")
    writer.writeheader()
    for row in flat:
        # stringify lists/dicts for CSV compat
        str_row = {
            k: (json.dumps(v) if isinstance(v, (list, dict)) else "" if v is None else str(v))
            for k, v in row.items()
        }
        writer.writerow(str_row)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and parse Airtable bases, tables, and records.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment:
  AIRTABLE_TOKEN  Personal Access Token (required)

Examples:
  # List all accessible bases
  python parse_airtable.py bases

  # Fetch base schema
  python parse_airtable.py schema appXXXXXXXX

  # Fetch all records from a table
  python parse_airtable.py records appXXXXXXXX "My Table" --format csv --out out.csv

  # Filter records
  python parse_airtable.py records appXXXXXXXX "Tasks" --formula "AND({Status}='Open')" --format json

  # Fetch specific fields only
  python parse_airtable.py records appXXXXXXXX "Contacts" --fields "Name,Email,Company"

  # Search for a value
  python parse_airtable.py search appXXXXXXXX "Contacts" "Email" "alice@example.com"
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # bases
    sub.add_parser("bases", help="List all accessible bases")

    # schema
    s = sub.add_parser("schema", help="Fetch base schema")
    s.add_argument("base_id")

    # records
    r = sub.add_parser("records", help="Fetch all records from a table")
    r.add_argument("base_id")
    r.add_argument("table")
    r.add_argument("--fields", default="", help="Comma-separated field names")
    r.add_argument("--formula", default="")
    r.add_argument("--view", default="")
    r.add_argument("--sort", default="", help="field:asc,field2:desc")
    r.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    r.add_argument("--out", default="")

    # search
    se = sub.add_parser("search", help="Search records by field value")
    se.add_argument("base_id")
    se.add_argument("table")
    se.add_argument("field")
    se.add_argument("value")
    se.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    se.add_argument("--out", default="")

    args = parser.parse_args()

    if args.cmd == "bases":
        bases = list_bases()
        for b in bases:
            print(f"[{b['base_id']}] {b['base_name']} (workspace: {b['workspace_name']})")
        return

    if args.cmd == "schema":
        schema = fetch_schema(args.base_id)
        for t in schema.tables:
            print(f"  [{t['id']}] {t['name']} — {len(t['fields'])} fields")
            for f in t["fields"]:
                print(f"    {f['name']} ({f['type']})")
        return

    if args.cmd == "records":
        fields = [f.strip() for f in args.fields.split(",") if f.strip()] or None
        sort = None
        if args.sort:
            sort = []
            for part in args.sort.split(","):
                if ":" in part:
                    fname, direction = part.split(":", 1)
                    sort.append({"field": fname.strip(), "direction": direction.strip()})
                else:
                    sort.append({"field": part.strip(), "direction": "asc"})
        records = fetch_all(args.base_id, args.table, fields=fields,
                            formula=args.formula, sort=sort, view=args.view)
        _output(records, args.format, getattr(args, "out", ""))
        return

    if args.cmd == "search":
        records = search(args.base_id, args.table, args.field, args.value)
        _output(records, args.format, getattr(args, "out", ""))


def _output(records: list[AirtableRecord], fmt: str, out: str) -> None:
    if fmt == "summary":
        print(f"{len(records)} record(s)")
        for r in records[:10]:
            preview = dict(list(r.fields.items())[:4])
            print(f"  [{r.id}] {preview}")
        if len(records) > 10:
            print(f"  … {len(records) - 10} more")
        return
    output = to_json(records) if fmt == "json" else to_csv(records)
    if out:
        from pathlib import Path
        Path(out).write_text(output, encoding="utf-8")
        print(f"Written to {out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
