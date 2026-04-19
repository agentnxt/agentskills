"""
parse_html_tables.py
Extract tables from any HTML — file, URL, or raw string.

Handles:
  - <table> with <thead>/<tbody>/<tr>/<th>/<td>
  - colspan / rowspan expansion
  - Nested tables (optional — skip or flatten)
  - Multi-row headers (merged into single header string)
  - HTML from files, URLs, or raw strings

pip install beautifulsoup4 lxml requests
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class HTMLTable:
    source: str          # file path, URL, or "raw"
    table_index: int
    caption: str
    headers: list[str]
    rows: list[dict]
    raw: list[list[str]] = field(repr=False, default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.headers)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(val: Any) -> str:
    if val is None:
        return ""
    return " ".join(str(val).split()).strip()


def _make_unique_headers(headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for h in headers:
        name = h or f"col_{len(result)}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.append(name)
    return result


def _expand_spans(table_tag) -> list[list[str]]:
    """
    Expand a BeautifulSoup <table> element into a 2D list of strings,
    handling colspan and rowspan correctly.
    """
    from bs4 import Tag

    # First pass — collect all rows
    tr_tags = table_tag.find_all("tr", recursive=True)
    # Remove rows belonging to nested tables
    tr_tags = [
        tr for tr in tr_tags
        if not any(p.name == "table" and p is not table_tag
                   for p in tr.parents)
    ]

    if not tr_tags:
        return []

    # Determine grid size
    n_cols = 0
    for tr in tr_tags:
        cols = sum(
            int(c.get("colspan", 1))
            for c in tr.find_all(["th", "td"], recursive=False)
        )
        n_cols = max(n_cols, cols)

    n_rows = len(tr_tags)
    grid: list[list[str | None]] = [[None] * n_cols for _ in range(n_rows)]
    spans: dict[tuple[int, int], int] = {}  # (row, col) -> remaining rowspan

    for ri, tr in enumerate(tr_tags):
        ci = 0
        for cell in tr.find_all(["th", "td"], recursive=False):
            # skip cells filled by rowspan from above
            while ci < n_cols and grid[ri][ci] is not None:
                ci += 1
            if ci >= n_cols:
                break

            text = _clean(cell.get_text(separator=" "))
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            for dc in range(colspan):
                for dr in range(rowspan):
                    if ri + dr < n_rows and ci + dc < n_cols:
                        grid[ri + dr][ci + dc] = text

            ci += colspan

    # Replace any remaining None with ""
    return [[c if c is not None else "" for c in row] for row in grid]


def _parse_table(table_tag, source: str, idx: int,
                 has_header: bool = True) -> HTMLTable | None:
    """Parse a single <table> BeautifulSoup tag into an HTMLTable."""
    caption_tag = table_tag.find("caption")
    caption = _clean(caption_tag.get_text()) if caption_tag else ""

    grid = _expand_spans(table_tag)
    if not grid:
        return None

    # Detect header rows: <thead> rows or rows of all <th>
    from bs4 import Tag

    tr_tags = table_tag.find_all("tr", recursive=False)
    # also include rows inside <thead>
    thead = table_tag.find("thead")
    thead_rows = set()
    if thead:
        for tr in thead.find_all("tr"):
            thead_rows.add(id(tr))

    all_tr = table_tag.find_all("tr", recursive=True)
    all_tr = [tr for tr in all_tr
              if not any(p.name == "table" and p is not table_tag
                         for p in tr.parents)]

    # identify header rows (all cells are <th> or row is in <thead>)
    header_row_count = 0
    if has_header:
        for tr in all_tr:
            cells = tr.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            if id(tr) in thead_rows or all(c.name == "th" for c in cells):
                header_row_count += 1
            else:
                break

    if header_row_count == 0 and has_header:
        header_row_count = 1  # assume first row is header

    # Build headers from header rows (merge multi-row headers)
    if header_row_count > 0 and grid:
        header_rows = grid[:header_row_count]
        if header_row_count == 1:
            raw_headers = header_rows[0]
        else:
            raw_headers = [
                " | ".join(filter(None, [header_rows[r][c] for r in range(header_row_count)]))
                for c in range(len(header_rows[0]))
            ]
        headers = _make_unique_headers(raw_headers)
        data_grid = grid[header_row_count:]
    else:
        headers = [f"col_{i}" for i in range(len(grid[0]) if grid else 0)]
        data_grid = grid

    rows = []
    for row in data_grid:
        padded = row + [""] * (len(headers) - len(row))
        d = dict(zip(headers, padded[:len(headers)]))
        if any(v for v in d.values()):
            rows.append(d)

    return HTMLTable(
        source=source, table_index=idx,
        caption=caption, headers=headers, rows=rows, raw=grid
    )


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _get_soup(html: str):
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise ImportError("Run: pip install beautifulsoup4 lxml") from e
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def _load_html_from_url(url: str) -> str:
    try:
        import requests
    except ImportError as e:
        raise ImportError("Run: pip install requests") from e
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(source: str, has_header: bool = True,
            skip_nested: bool = True) -> list[HTMLTable]:
    """
    Extract all tables from an HTML source.

    Parameters
    ----------
    source : str
        One of:
        - File path ending in .html / .htm
        - HTTP/HTTPS URL
        - Raw HTML string
    has_header : bool
        If True, treats the first row (or <thead>) as column headers.
    skip_nested : bool
        If True, skips tables nested inside other tables.

    Returns
    -------
    list[HTMLTable]
        One HTMLTable per <table> element found.
    """
    from pathlib import Path

    label = "raw"
    if source.startswith("http://") or source.startswith("https://"):
        html = _load_html_from_url(source)
        label = source
    else:
        p = Path(source)
        if p.exists() and p.suffix.lower() in (".html", ".htm"):
            html = p.read_text(encoding="utf-8")
            label = str(p)
        else:
            html = source  # treat as raw HTML string

    soup = _get_soup(html)
    all_tables = soup.find_all("table")

    if skip_nested:
        all_tables = [
            t for t in all_tables
            if not any(p.name == "table" for p in t.parents)
        ]

    tables = []
    for i, tag in enumerate(all_tables):
        parsed = _parse_table(tag, label, i, has_header=has_header)
        if parsed:
            tables.append(parsed)
    return tables


def extract_from_string(html: str, **kwargs) -> list[HTMLTable]:
    """Extract tables from a raw HTML string."""
    return extract(html, **kwargs)


def extract_from_file(path: str, **kwargs) -> list[HTMLTable]:
    """Extract tables from an HTML file."""
    from pathlib import Path
    return extract(Path(path).read_text(encoding="utf-8"), **kwargs)


def extract_from_url(url: str, **kwargs) -> list[HTMLTable]:
    """Extract tables from a URL."""
    return extract(url, **kwargs)


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(tables: list[HTMLTable], indent: int = 2) -> str:
    out = []
    for t in tables:
        out.append({
            "source": t.source,
            "table_index": t.table_index,
            "caption": t.caption,
            "row_count": t.row_count,
            "col_count": t.col_count,
            "headers": t.headers,
            "rows": t.rows,
        })
    return json.dumps(out, indent=indent, ensure_ascii=False)


def to_csv(tables: list[HTMLTable], table_index: int = 0) -> str:
    if not tables:
        return ""
    t = tables[table_index]
    if not t.rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=t.headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(t.rows)
    return buf.getvalue()


def to_csv_all(tables: list[HTMLTable]) -> str:
    """Merge all tables into one CSV with _source and _table columns."""
    all_rows = []
    for t in tables:
        for row in t.rows:
            all_rows.append({"_table": t.table_index, "_caption": t.caption, **row})
    if not all_rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(all_rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_rows)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract tables from HTML (file, URL, or string).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From a file
  python parse_html_tables.py page.html

  # From a URL, all tables as JSON
  python parse_html_tables.py https://en.wikipedia.org/wiki/G2_(software) --format json

  # First table as CSV
  python parse_html_tables.py page.html --format csv --table 0 --out out.csv

  # Include nested tables
  python parse_html_tables.py page.html --include-nested
        """,
    )
    parser.add_argument("source", help="HTML file path, URL, or raw HTML string")
    parser.add_argument("--format", choices=["json", "csv", "csv-all", "summary"],
                        default="summary")
    parser.add_argument("--table", type=int, default=0,
                        help="Table index for --format csv (default: 0)")
    parser.add_argument("--no-header", action="store_true",
                        help="Treat all rows as data (no header detection)")
    parser.add_argument("--include-nested", action="store_true",
                        help="Include tables nested inside other tables")
    parser.add_argument("--out", default="", help="Output file path")
    args = parser.parse_args()

    tables = extract(
        args.source,
        has_header=not args.no_header,
        skip_nested=not args.include_nested,
    )

    if args.format == "summary":
        print(f"Found {len(tables)} table(s)")
        for t in tables:
            cap = f" '{t.caption}'" if t.caption else ""
            print(f"  Table {t.table_index}{cap} — {t.row_count} rows × {t.col_count} cols")
            print(f"    Headers: {t.headers[:6]}{'…' if len(t.headers) > 6 else ''}")
        return

    output = (to_json(tables) if args.format == "json"
              else to_csv(tables, args.table) if args.format == "csv"
              else to_csv_all(tables))

    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
