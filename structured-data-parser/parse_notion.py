"""
parse_notion.py
Generic parser for the Notion API — fetch, flatten, and export any database,
page, or block tree.

Covers:
  - Database query (all rows, filters, sorts, paginated)
  - Database schema (property definitions)
  - Page metadata + properties
  - Block tree (recursive — all content blocks)
  - Search across workspace
  - Create / update pages
  - Append blocks to a page

Property types fully handled:
  title, rich_text, number, select, multi_select, status, date, checkbox,
  url, email, phone_number, people, relation, rollup, formula, files,
  created_time, last_edited_time, created_by, last_edited_by, unique_id,
  button (ignored)

Outputs: list[dict], JSON, CSV.

pip install notion-client

Environment:
  NOTION_TOKEN — Integration token from https://www.notion.so/my-integrations
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
    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "Set NOTION_TOKEN to your Notion integration token. "
            "Create one at: https://www.notion.so/my-integrations"
        )
    return token


def _client(token: str | None = None):
    try:
        from notion_client import Client
    except ImportError as e:
        raise ImportError("Run: pip install notion-client") from e
    return Client(auth=token or _token())


# ---------------------------------------------------------------------------
# Property value extractor
# ---------------------------------------------------------------------------

def _extract_rich_text(rt: list) -> str:
    return "".join(t.get("plain_text", "") for t in (rt or []))


def _extract_property(prop: dict) -> Any:
    """Extract a plain Python value from any Notion property dict."""
    ptype = prop.get("type", "")

    if ptype == "title":
        return _extract_rich_text(prop.get("title", []))
    if ptype == "rich_text":
        return _extract_rich_text(prop.get("rich_text", []))
    if ptype == "number":
        return prop.get("number")
    if ptype == "select":
        s = prop.get("select")
        return s["name"] if s else None
    if ptype == "multi_select":
        return [s["name"] for s in prop.get("multi_select", [])]
    if ptype == "status":
        s = prop.get("status")
        return s["name"] if s else None
    if ptype == "date":
        d = prop.get("date")
        if not d:
            return None
        return d.get("start") if not d.get("end") else f"{d['start']} → {d['end']}"
    if ptype == "checkbox":
        return prop.get("checkbox", False)
    if ptype == "url":
        return prop.get("url")
    if ptype == "email":
        return prop.get("email")
    if ptype == "phone_number":
        return prop.get("phone_number")
    if ptype == "people":
        return [p.get("name", p.get("id", "")) for p in prop.get("people", [])]
    if ptype == "relation":
        return [r["id"] for r in prop.get("relation", [])]
    if ptype == "rollup":
        ru = prop.get("rollup", {})
        ru_type = ru.get("type", "")
        if ru_type == "number":
            return ru.get("number")
        if ru_type == "array":
            return [_extract_property(item) for item in ru.get("array", [])]
        return str(ru)
    if ptype == "formula":
        f = prop.get("formula", {})
        ft = f.get("type", "")
        return f.get(ft)
    if ptype == "files":
        files = prop.get("files", [])
        urls = []
        for fi in files:
            if fi.get("type") == "external":
                urls.append(fi["external"]["url"])
            elif fi.get("type") == "file":
                urls.append(fi["file"]["url"])
        return urls
    if ptype in ("created_time", "last_edited_time"):
        return prop.get(ptype)
    if ptype in ("created_by", "last_edited_by"):
        person = prop.get(ptype, {})
        return person.get("name", person.get("id", ""))
    if ptype == "unique_id":
        uid = prop.get("unique_id", {})
        prefix = uid.get("prefix") or ""
        num = uid.get("number", "")
        return f"{prefix}{num}" if prefix else str(num)

    return None  # button, unknown


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class NotionPage:
    id: str
    url: str
    created_time: str
    last_edited_time: str
    archived: bool
    parent_type: str
    parent_id: str
    properties: dict[str, Any]  # extracted plain values
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "NotionPage":
        props = {
            name: _extract_property(prop)
            for name, prop in raw.get("properties", {}).items()
        }
        parent = raw.get("parent", {})
        parent_type = parent.get("type", "")
        parent_id = parent.get(parent_type, "") if parent_type else ""
        return cls(
            id=raw.get("id", ""),
            url=raw.get("url", ""),
            created_time=raw.get("created_time", ""),
            last_edited_time=raw.get("last_edited_time", ""),
            archived=raw.get("archived", False),
            parent_type=parent_type,
            parent_id=parent_id,
            properties=props,
            raw=raw,
        )

    def flat(self) -> dict:
        base = {
            "_id": self.id,
            "_url": self.url,
            "_created": self.created_time,
            "_edited": self.last_edited_time,
            "_archived": self.archived,
        }
        base.update(self.properties)
        return base


@dataclass
class NotionBlock:
    id: str
    type: str
    text: str
    children: list["NotionBlock"] = field(default_factory=list)
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "NotionBlock":
        btype = raw.get("type", "unknown")
        block_data = raw.get(btype, {})
        rich_text = block_data.get("rich_text", [])
        text = _extract_rich_text(rich_text)
        return cls(id=raw.get("id", ""), type=btype, text=text, raw=raw)

    def to_markdown(self, depth: int = 0) -> str:
        indent = "  " * depth
        prefix = {
            "heading_1": "# ", "heading_2": "## ", "heading_3": "### ",
            "bulleted_list_item": "- ", "numbered_list_item": "1. ",
            "to_do": "- [ ] ", "quote": "> ", "code": "```\n",
            "divider": "---",
        }.get(self.type, "")
        suffix = "\n```" if self.type == "code" else ""
        line = f"{indent}{prefix}{self.text}{suffix}"
        child_lines = "\n".join(c.to_markdown(depth + 1) for c in self.children)
        return f"{line}\n{child_lines}" if child_lines else line


@dataclass
class NotionDatabase:
    id: str
    title: str
    url: str
    properties: dict[str, dict]  # name -> {type, id, ...}

    @classmethod
    def from_raw(cls, raw: dict) -> "NotionDatabase":
        title = _extract_rich_text(raw.get("title", []))
        props = {}
        for name, prop in raw.get("properties", {}).items():
            props[name] = {"id": prop.get("id", ""), "type": prop.get("type", "")}
        return cls(
            id=raw.get("id", ""),
            title=title,
            url=raw.get("url", ""),
            properties=props,
        )


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def _paginate_request(client, path: str, method: str = "POST",
                      body: dict | None = None) -> list[dict]:
    """Paginate a Notion API endpoint, returning all results."""
    results = []
    cursor = None
    while True:
        payload = dict(body or {})
        if cursor:
            payload["start_cursor"] = cursor
        resp = client.request(path=path, method=method, body=payload if method == "POST" else None)
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return results


def _paginate_get(client, path: str) -> list[dict]:
    results = []
    cursor = None
    while True:
        params = f"?start_cursor={cursor}" if cursor else ""
        resp = client.request(path=f"{path}{params}", method="GET")
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return results


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def fetch_database_schema(database_id: str,
                           token: str | None = None) -> NotionDatabase:
    """
    Fetch a database's schema — title and property definitions.

    Parameters
    ----------
    database_id : str
        Notion database ID (with or without hyphens).

    Returns
    -------
    NotionDatabase
    """
    client = _client(token)
    raw = client.databases.retrieve(database_id=database_id)
    return NotionDatabase.from_raw(raw)


def query_database(database_id: str,
                   filter: dict | None = None,
                   sorts: list[dict] | None = None,
                   token: str | None = None) -> list[NotionPage]:
    """
    Query all rows from a Notion database, auto-paginating.

    Parameters
    ----------
    database_id : str
        Notion database ID.
    filter : dict | None
        Notion filter object.
        e.g. {"property": "Status", "select": {"equals": "Active"}}
    sorts : list[dict] | None
        Notion sort specs.
        e.g. [{"property": "Name", "direction": "ascending"}]

    Returns
    -------
    list[NotionPage]
        One NotionPage per database row.
    """
    client = _client(token)
    body: dict[str, Any] = {}
    if filter:
        body["filter"] = filter
    if sorts:
        body["sorts"] = sorts

    raw_pages = _paginate_request(
        client, f"databases/{database_id}/query", method="POST", body=body
    )
    return [NotionPage.from_raw(p) for p in raw_pages]


def fetch_page(page_id: str, token: str | None = None) -> NotionPage:
    """Fetch a single Notion page by ID."""
    client = _client(token)
    raw = client.pages.retrieve(page_id=page_id)
    return NotionPage.from_raw(raw)


def fetch_blocks(block_id: str, recursive: bool = True,
                 token: str | None = None) -> list[NotionBlock]:
    """
    Fetch all blocks under a page or block, optionally recursing into children.

    Parameters
    ----------
    block_id : str
        Page ID or parent block ID.
    recursive : bool
        If True, fetch children of children (full tree).

    Returns
    -------
    list[NotionBlock]
    """
    client = _client(token)
    raw_blocks = _paginate_get(client, f"blocks/{block_id}/children")
    blocks = [NotionBlock.from_raw(b) for b in raw_blocks]

    if recursive:
        for block in blocks:
            if block.raw.get("has_children"):
                block.children = fetch_blocks(block.id, recursive=True, token=token)

    return blocks


def search_pages(query: str = "", filter_type: str = "page",
                 token: str | None = None) -> list[NotionPage]:
    """
    Search across the workspace.

    Parameters
    ----------
    query : str
        Text to search for. Empty string returns all accessible pages.
    filter_type : str
        'page' or 'database'.

    Returns
    -------
    list[NotionPage]
    """
    client = _client(token)
    body: dict[str, Any] = {
        "filter": {"value": filter_type, "property": "object"},
    }
    if query:
        body["query"] = query

    raw = _paginate_request(client, "search", method="POST", body=body)
    return [NotionPage.from_raw(p) for p in raw]


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def create_page(parent_id: str, properties: dict[str, Any],
                is_database: bool = True,
                children: list[dict] | None = None,
                token: str | None = None) -> NotionPage:
    """
    Create a new page in a database or as a child of another page.

    Parameters
    ----------
    parent_id : str
        Database ID (if is_database=True) or parent page ID.
    properties : dict
        Property values as Notion API format.
        For a title-only page: {"Name": {"title": [{"text": {"content": "My Page"}}]}}
    is_database : bool
        True if parent is a database, False if parent is a page.
    children : list[dict] | None
        Optional list of block objects to add as page content.

    Returns
    -------
    NotionPage
    """
    client = _client(token)
    parent = ({"database_id": parent_id} if is_database
              else {"page_id": parent_id})
    body: dict[str, Any] = {"parent": parent, "properties": properties}
    if children:
        body["children"] = children
    raw = client.pages.create(**body)
    return NotionPage.from_raw(raw)


def update_page(page_id: str, properties: dict[str, Any],
                archived: bool | None = None,
                token: str | None = None) -> NotionPage:
    """
    Update a page's properties (PATCH — only specified properties changed).

    Parameters
    ----------
    properties : dict
        Notion API property format.
    archived : bool | None
        Set to True to archive (soft-delete) the page.
    """
    client = _client(token)
    kwargs: dict[str, Any] = {"page_id": page_id, "properties": properties}
    if archived is not None:
        kwargs["archived"] = archived
    raw = client.pages.update(**kwargs)
    return NotionPage.from_raw(raw)


def append_blocks(page_id: str, blocks: list[dict],
                  token: str | None = None) -> list[NotionBlock]:
    """
    Append block content to a page.

    Parameters
    ----------
    blocks : list[dict]
        Notion block objects.
        e.g. [{"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}]
    """
    client = _client(token)
    raw = client.blocks.children.append(block_id=page_id, children=blocks)
    return [NotionBlock.from_raw(b) for b in raw.get("results", [])]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_flat_records(pages: list[NotionPage]) -> list[dict]:
    """Flatten pages to list[dict] — CSV/DataFrame/SurrealDB ready."""
    return [p.flat() for p in pages]


def to_json(data: list[NotionPage] | list[NotionBlock] | dict,
            indent: int = 2) -> str:
    """Serialise pages, blocks, or raw dict to JSON string."""
    if isinstance(data, dict):
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    if data and isinstance(data[0], NotionBlock):
        def _block_dict(b: NotionBlock) -> dict:
            return {"id": b.id, "type": b.type, "text": b.text,
                    "children": [_block_dict(c) for c in b.children]}
        return json.dumps([_block_dict(b) for b in data], indent=indent)
    return json.dumps(
        [p.flat() for p in data], indent=indent,
        ensure_ascii=False, default=str
    )


def to_csv(pages: list[NotionPage]) -> str:
    """Serialise pages to CSV. Lists/dicts are pipe-joined / JSON-stringified."""
    flat = to_flat_records(pages)
    if not flat:
        return ""
    # union of all keys
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in flat:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore", restval="")
    writer.writeheader()
    for row in flat:
        str_row = {}
        for k, v in row.items():
            if isinstance(v, list):
                str_row[k] = " | ".join(str(i) for i in v)
            elif isinstance(v, dict):
                str_row[k] = json.dumps(v)
            elif v is None:
                str_row[k] = ""
            else:
                str_row[k] = str(v)
        writer.writerow(str_row)
    return buf.getvalue()


def blocks_to_markdown(blocks: list[NotionBlock]) -> str:
    """Convert a block tree to Markdown string."""
    return "\n".join(b.to_markdown() for b in blocks)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and parse Notion databases, pages, and blocks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment:
  NOTION_TOKEN  Integration token (required)

Examples:
  # Query all rows from a database as CSV
  python parse_notion.py query DATABASE_ID --format csv --out rows.csv

  # Query with filter
  python parse_notion.py query DATABASE_ID --filter '{"property":"Status","select":{"equals":"Active"}}'

  # Fetch database schema
  python parse_notion.py schema DATABASE_ID

  # Fetch page properties
  python parse_notion.py page PAGE_ID --format json

  # Fetch page content as Markdown
  python parse_notion.py blocks PAGE_ID --format markdown

  # Search workspace
  python parse_notion.py search "meeting notes" --format json
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # query
    q = sub.add_parser("query", help="Query a database")
    q.add_argument("database_id")
    q.add_argument("--filter", default="", help="JSON filter object")
    q.add_argument("--sort", default="", help='JSON sorts array e.g. [{"property":"Name","direction":"ascending"}]')
    q.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    q.add_argument("--out", default="")

    # schema
    s = sub.add_parser("schema", help="Fetch database schema")
    s.add_argument("database_id")

    # page
    p = sub.add_parser("page", help="Fetch a page")
    p.add_argument("page_id")
    p.add_argument("--format", choices=["json", "summary"], default="summary")

    # blocks
    b = sub.add_parser("blocks", help="Fetch page content blocks")
    b.add_argument("page_id")
    b.add_argument("--format", choices=["json", "markdown", "summary"], default="markdown")
    b.add_argument("--no-recurse", action="store_true")
    b.add_argument("--out", default="")

    # search
    se = sub.add_parser("search", help="Search workspace")
    se.add_argument("query", nargs="?", default="")
    se.add_argument("--type", choices=["page", "database"], default="page")
    se.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    se.add_argument("--out", default="")

    args = parser.parse_args()

    if args.cmd == "schema":
        db = fetch_database_schema(args.database_id)
        print(f"{db.title} [{db.id}]")
        for name, info in db.properties.items():
            print(f"  {name} ({info['type']})")
        return

    if args.cmd == "page":
        page = fetch_page(args.page_id)
        if args.format == "json":
            print(to_json([page]))
        else:
            print(f"[{page.id}] {page.url}")
            for k, v in page.properties.items():
                print(f"  {k}: {v}")
        return

    if args.cmd == "blocks":
        blocks = fetch_blocks(args.page_id, recursive=not args.no_recurse)
        if args.format == "markdown":
            output = blocks_to_markdown(blocks)
        elif args.format == "json":
            output = to_json(blocks)
        else:
            print(f"{len(blocks)} top-level block(s)")
            for b in blocks[:10]:
                print(f"  [{b.type}] {b.text[:60]}")
            return
        if args.out:
            from pathlib import Path
            Path(args.out).write_text(output, encoding="utf-8")
            print(f"Written to {args.out}")
        else:
            print(output)
        return

    if args.cmd == "query":
        filt = json.loads(args.filter) if args.filter else None
        sorts = json.loads(args.sort) if args.sort else None
        pages = query_database(args.database_id, filter=filt, sorts=sorts)
        _output_pages(pages, args.format, getattr(args, "out", ""))
        return

    if args.cmd == "search":
        pages = search_pages(args.query, filter_type=args.type)
        _output_pages(pages, args.format, getattr(args, "out", ""))


def _output_pages(pages: list[NotionPage], fmt: str, out: str) -> None:
    if fmt == "summary":
        print(f"{len(pages)} page(s)")
        for p in pages[:10]:
            title = next((v for v in p.properties.values() if isinstance(v, str) and v), p.id)
            print(f"  [{p.id}] {title}")
        if len(pages) > 10:
            print(f"  … {len(pages) - 10} more")
        return
    output = to_json(pages) if fmt == "json" else to_csv(pages)
    if out:
        from pathlib import Path
        Path(out).write_text(output, encoding="utf-8")
        print(f"Written to {out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
