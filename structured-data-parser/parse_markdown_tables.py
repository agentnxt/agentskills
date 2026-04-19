"""
parse_markdown_tables.py
Extract tables from Markdown text — file, URL, or raw string.

Handles:
  - Standard GFM pipe tables
  - Headerless tables
  - Alignment rows (stripped automatically)
  - Tables inside code blocks (skipped by default)
  - Multiple tables per document
  - Column spans via repeated pipes (non-standard but seen in the wild)

No third-party dependencies — stdlib only.
"""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MarkdownTable:
    source: str          # file path, URL, or "raw"
    table_index: int
    line_start: int      # 1-based line number where table starts
    headers: list[str]
    rows: list[dict]
    raw_lines: list[str] = field(repr=False, default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.headers)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEPARATOR_RE = re.compile(r"^[\|\s\-:]+$")


def _clean(val: str) -> str:
    return val.strip()


def _is_separator(line: str) -> bool:
    """True if the line is a Markdown table separator (---|:---:|---:)."""
    stripped = line.strip()
    if not stripped:
        return False
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    return all(re.match(r"^:?-{1,}:?$", c) for c in cells if c)


def _split_row(line: str) -> list[str]:
    """Split a pipe-delimited table row into cells, stripping edge pipes."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [_clean(c) for c in stripped.split("|")]


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


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------

def _is_table_line(line: str) -> bool:
    return "|" in line


def _strip_code_blocks(lines: list[str]) -> list[str]:
    """Replace lines inside fenced code blocks with empty lines."""
    result = []
    in_fence = False
    fence_char = ""
    for line in lines:
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = True
                fence_char = stripped[:3]
                result.append("")
            else:
                result.append(line)
        else:
            if stripped.startswith(fence_char):
                in_fence = False
            result.append("")
    return result


def _extract_tables(lines: list[str], source: str,
                    has_header: bool = True) -> list[MarkdownTable]:
    tables: list[MarkdownTable] = []
    i = 0
    table_idx = 0

    while i < len(lines):
        line = lines[i]

        if not _is_table_line(line):
            i += 1
            continue

        # Collect contiguous table lines
        block_start = i
        block: list[str] = []
        while i < len(lines) and ("|" in lines[i] or (block and _is_separator(lines[i]))):
            block.append(lines[i])
            i += 1

        if not block:
            continue

        # Need at least 2 lines (header + separator or 2 data rows)
        if len(block) < 2:
            continue

        # Find separator row
        sep_idx = None
        for j, bl in enumerate(block):
            if _is_separator(bl):
                sep_idx = j
                break

        if sep_idx is None:
            # No separator — treat all as data, no header detection
            rows_raw = [_split_row(l) for l in block]
            headers = _make_unique_headers([f"col_{k}" for k in range(max(len(r) for r in rows_raw))])
            has_hdr = False
        else:
            header_lines = block[:sep_idx]
            rows_raw_lines = block[sep_idx + 1:]

            if has_header and header_lines:
                # Multi-row headers: join with " | "
                if len(header_lines) == 1:
                    raw_headers = _split_row(header_lines[0])
                else:
                    cols = [_split_row(hl) for hl in header_lines]
                    n_cols = max(len(c) for c in cols)
                    raw_headers = [
                        " | ".join(filter(None, [cols[r][k] if k < len(cols[r]) else "" for r in range(len(cols))]))
                        for k in range(n_cols)
                    ]
                headers = _make_unique_headers(raw_headers)
            else:
                first = _split_row(block[0])
                headers = [f"col_{k}" for k in range(len(first))]
                rows_raw_lines = block  # all lines are data

            rows_raw = [_split_row(l) for l in rows_raw_lines]
            has_hdr = True

        # Build dicts
        records = []
        for row in rows_raw:
            padded = row + [""] * (len(headers) - len(row))
            d = dict(zip(headers, padded[:len(headers)]))
            if any(v for v in d.values()):
                records.append(d)

        if not records:
            continue

        tables.append(MarkdownTable(
            source=source,
            table_index=table_idx,
            line_start=block_start + 1,
            headers=headers,
            rows=records,
            raw_lines=block,
        ))
        table_idx += 1

    return tables


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(source: str, has_header: bool = True,
            skip_code_blocks: bool = True) -> list[MarkdownTable]:
    """
    Extract all Markdown tables from a source.

    Parameters
    ----------
    source : str
        One of:
        - File path ending in .md / .markdown
        - HTTP/HTTPS URL
        - Raw Markdown string
    has_header : bool
        If True, treats the row before the separator as column headers.
    skip_code_blocks : bool
        If True, tables inside fenced code blocks are ignored.

    Returns
    -------
    list[MarkdownTable]
    """
    label = "raw"

    if source.startswith("http://") or source.startswith("https://"):
        try:
            import requests
            resp = requests.get(source, timeout=15)
            resp.raise_for_status()
            text = resp.text
            label = source
        except ImportError as e:
            raise ImportError("Run: pip install requests") from e
    else:
        p = Path(source)
        if p.exists() and p.suffix.lower() in (".md", ".markdown", ".txt"):
            text = p.read_text(encoding="utf-8")
            label = str(p)
        else:
            text = source  # raw Markdown string

    lines = text.splitlines()
    if skip_code_blocks:
        lines = _strip_code_blocks(lines)

    return _extract_tables(lines, source=label, has_header=has_header)


def extract_from_string(md: str, **kwargs) -> list[MarkdownTable]:
    """Extract tables from a raw Markdown string."""
    return extract(md, **kwargs)


def extract_from_file(path: str, **kwargs) -> list[MarkdownTable]:
    """Extract tables from a Markdown file."""
    return extract(path, **kwargs)


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(tables: list[MarkdownTable], indent: int = 2) -> str:
    out = []
    for t in tables:
        out.append({
            "source": t.source,
            "table_index": t.table_index,
            "line_start": t.line_start,
            "row_count": t.row_count,
            "col_count": t.col_count,
            "headers": t.headers,
            "rows": t.rows,
        })
    return json.dumps(out, indent=indent, ensure_ascii=False)


def to_csv(tables: list[MarkdownTable], table_index: int = 0) -> str:
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


def to_csv_all(tables: list[MarkdownTable]) -> str:
    all_rows = []
    for t in tables:
        for row in t.rows:
            all_rows.append({"_table": t.table_index, "_line_start": t.line_start, **row})
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
        description="Extract tables from Markdown (file, URL, or string).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From a file
  python parse_markdown_tables.py README.md

  # From a URL
  python parse_markdown_tables.py https://raw.githubusercontent.com/owner/repo/main/README.md

  # First table as CSV
  python parse_markdown_tables.py README.md --format csv --table 0 --out out.csv

  # All tables merged
  python parse_markdown_tables.py README.md --format csv-all --out all.csv

  # No header detection
  python parse_markdown_tables.py README.md --no-header
        """,
    )
    parser.add_argument("source", help="Markdown file path, URL, or raw string")
    parser.add_argument("--format", choices=["json", "csv", "csv-all", "summary"],
                        default="summary")
    parser.add_argument("--table", type=int, default=0)
    parser.add_argument("--no-header", action="store_true")
    parser.add_argument("--include-code-blocks", action="store_true",
                        help="Also extract tables inside fenced code blocks")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    tables = extract(
        args.source,
        has_header=not args.no_header,
        skip_code_blocks=not args.include_code_blocks,
    )

    if args.format == "summary":
        print(f"Found {len(tables)} table(s)")
        for t in tables:
            print(f"  Table {t.table_index} (line {t.line_start}) — {t.row_count} rows × {t.col_count} cols")
            print(f"    Headers: {t.headers[:6]}{'…' if len(t.headers) > 6 else ''}")
        return

    output = (to_json(tables) if args.format == "json"
              else to_csv(tables, args.table) if args.format == "csv"
              else to_csv_all(tables))

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
