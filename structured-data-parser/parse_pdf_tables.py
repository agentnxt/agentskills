"""
parse_pdf_tables.py
Extract tables from any PDF — text-based or scanned.

Strategy (in priority order):
  1. pdfplumber  — best for text-based PDFs with ruled/borderless tables
  2. camelot     — best for bordered tables (lattice) or stream-based
  3. pymupdf     — fast fallback for simple text-based PDFs
  4. tabula-py   — JVM-based fallback (requires Java)

Auto-selects the best engine based on file content.
Outputs: list[list[dict]] (one list per table), JSON, CSV.

pip install pdfplumber camelot-py pymupdf tabula-py
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PDFTable:
    page: int
    table_index: int
    engine: str
    headers: list[str]
    rows: list[dict]
    raw: list[list[str | None]] = field(repr=False, default_factory=list)

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
    return str(val).strip().replace("\n", " ")


def _make_headers(row: list) -> list[str]:
    """Build unique column names from a raw header row."""
    seen: dict[str, int] = {}
    headers = []
    for i, cell in enumerate(row):
        name = _clean(cell) or f"col_{i}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        headers.append(name)
    return headers


def _rows_to_dicts(raw_rows: list[list], skip_header: bool = True) -> tuple[list[str], list[dict]]:
    """Convert raw 2D list to (headers, list[dict]), skipping empty rows."""
    rows = [[_clean(c) for c in r] for r in raw_rows]
    rows = [r for r in rows if any(c for c in r)]
    if not rows:
        return [], []
    headers = _make_headers(rows[0]) if skip_header else [f"col_{i}" for i in range(len(rows[0]))]
    data_rows = rows[1:] if skip_header else rows
    result = []
    for row in data_rows:
        padded = row + [""] * (len(headers) - len(row))
        d = dict(zip(headers, padded[:len(headers)]))
        if any(v for v in d.values()):
            result.append(d)
    return headers, result


# ---------------------------------------------------------------------------
# Engine: pdfplumber
# ---------------------------------------------------------------------------

def _extract_pdfplumber(path: Path, pages: list[int] | None = None,
                        flavor: str = "auto") -> list[PDFTable]:
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError("Run: pip install pdfplumber") from e

    tables: list[PDFTable] = []
    with pdfplumber.open(path) as pdf:
        page_iter = (pdf.pages[i - 1] for i in pages) if pages else pdf.pages
        for page in page_iter:
            page_num = page.page_number
            raw_tables = page.extract_tables()
            for ti, raw in enumerate(raw_tables):
                if not raw:
                    continue
                headers, rows = _rows_to_dicts(raw)
                if not headers:
                    continue
                tables.append(PDFTable(
                    page=page_num, table_index=ti,
                    engine="pdfplumber", headers=headers, rows=rows, raw=raw
                ))
    return tables


# ---------------------------------------------------------------------------
# Engine: camelot
# ---------------------------------------------------------------------------

def _extract_camelot(path: Path, pages: str = "all",
                     flavor: str = "lattice") -> list[PDFTable]:
    try:
        import camelot
    except ImportError as e:
        raise ImportError("Run: pip install camelot-py") from e

    tables: list[PDFTable] = []
    try:
        result = camelot.read_pdf(str(path), pages=pages, flavor=flavor)
    except Exception:
        result = camelot.read_pdf(str(path), pages=pages, flavor="stream")

    for i, tbl in enumerate(result):
        df = tbl.df
        if df.empty:
            continue
        raw = df.values.tolist()
        headers, rows = _rows_to_dicts([[str(c) for c in row] for row in raw])
        if not headers:
            continue
        tables.append(PDFTable(
            page=tbl.page, table_index=i,
            engine=f"camelot-{flavor}", headers=headers, rows=rows, raw=raw
        ))
    return tables


# ---------------------------------------------------------------------------
# Engine: pymupdf
# ---------------------------------------------------------------------------

def _extract_pymupdf(path: Path, pages: list[int] | None = None) -> list[PDFTable]:
    try:
        import fitz  # pymupdf
    except ImportError as e:
        raise ImportError("Run: pip install pymupdf") from e

    tables: list[PDFTable] = []
    doc = fitz.open(str(path))
    page_nums = [p - 1 for p in pages] if pages else range(len(doc))

    for pn in page_nums:
        page = doc[pn]
        try:
            raw_tables = page.find_tables()
        except AttributeError:
            continue
        for ti, tbl in enumerate(raw_tables):
            raw = tbl.extract()
            if not raw:
                continue
            headers, rows = _rows_to_dicts(raw)
            if not headers:
                continue
            tables.append(PDFTable(
                page=pn + 1, table_index=ti,
                engine="pymupdf", headers=headers, rows=rows, raw=raw
            ))
    doc.close()
    return tables


# ---------------------------------------------------------------------------
# Engine: tabula (JVM, last resort)
# ---------------------------------------------------------------------------

def _extract_tabula(path: Path, pages: str = "all") -> list[PDFTable]:
    try:
        import tabula
    except ImportError as e:
        raise ImportError("Run: pip install tabula-py (also requires Java)") from e

    import pandas as pd
    dfs = tabula.read_pdf(str(path), pages=pages, multiple_tables=True)
    tables: list[PDFTable] = []
    for i, df in enumerate(dfs):
        if df.empty:
            continue
        headers = [str(c) for c in df.columns.tolist()]
        rows = [
            {headers[j]: _clean(v) for j, v in enumerate(row)}
            for row in df.values.tolist()
            if any(_clean(v) for v in row)
        ]
        tables.append(PDFTable(
            page=i + 1, table_index=0,
            engine="tabula", headers=headers, rows=rows
        ))
    return tables


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(path: str | Path, engine: str = "auto",
            pages: list[int] | None = None,
            camelot_flavor: str = "lattice") -> list[PDFTable]:
    """
    Extract all tables from a PDF file.

    Parameters
    ----------
    path : str | Path
        Path to the PDF file.
    engine : str
        One of: 'auto', 'pdfplumber', 'camelot', 'pymupdf', 'tabula'.
        'auto' tries pdfplumber → pymupdf → camelot → tabula.
    pages : list[int] | None
        1-based page numbers to extract from. None = all pages.
    camelot_flavor : str
        'lattice' (bordered tables) or 'stream' (whitespace-separated).
        Only used when engine='camelot'.

    Returns
    -------
    list[PDFTable]
        One PDFTable per detected table across all pages.

    Raises
    ------
    FileNotFoundError
        If the PDF does not exist.
    ValueError
        If no tables are found and all engines fail.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if engine == "pdfplumber":
        return _extract_pdfplumber(path, pages)
    if engine == "camelot":
        return _extract_camelot(path, pages="all" if not pages else ",".join(str(p) for p in pages), flavor=camelot_flavor)
    if engine == "pymupdf":
        return _extract_pymupdf(path, pages)
    if engine == "tabula":
        return _extract_tabula(path, pages="all" if not pages else ",".join(str(p) for p in pages))

    # auto: try each engine in order
    errors = []
    for fn, kwargs in [
        (_extract_pdfplumber, {"path": path, "pages": pages}),
        (_extract_pymupdf,    {"path": path, "pages": pages}),
        (_extract_camelot,    {"path": path, "pages": "all" if not pages else ",".join(str(p) for p in pages), "flavor": camelot_flavor}),
        (_extract_tabula,     {"path": path, "pages": "all" if not pages else ",".join(str(p) for p in pages)}),
    ]:
        try:
            tables = fn(**kwargs)
            if tables:
                return tables
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")

    return []  # no tables found — not an error, just an empty PDF


def extract_page(path: str | Path, page: int, **kwargs) -> list[PDFTable]:
    """Extract tables from a single page (1-based)."""
    return extract(path, pages=[page], **kwargs)


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(tables: list[PDFTable], indent: int = 2) -> str:
    """Serialise all tables to JSON."""
    out = []
    for t in tables:
        out.append({
            "page": t.page,
            "table_index": t.table_index,
            "engine": t.engine,
            "row_count": t.row_count,
            "col_count": t.col_count,
            "headers": t.headers,
            "rows": t.rows,
        })
    return json.dumps(out, indent=indent, ensure_ascii=False)


def to_csv(tables: list[PDFTable], table_index: int = 0) -> str:
    """Serialise a single table to CSV. Use table_index to select which."""
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


def to_csv_all(tables: list[PDFTable]) -> str:
    """Concatenate all tables into one CSV, adding page/table_index columns."""
    if not tables:
        return ""
    all_rows = []
    for t in tables:
        for row in t.rows:
            all_rows.append({"_page": t.page, "_table": t.table_index, **row})
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
        description="Extract tables from a PDF file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect engine, summarise tables
  python parse_pdf_tables.py report.pdf

  # Extract all tables as JSON
  python parse_pdf_tables.py report.pdf --format json --out tables.json

  # First table as CSV
  python parse_pdf_tables.py report.pdf --format csv --table 0 --out table0.csv

  # All tables merged into one CSV
  python parse_pdf_tables.py report.pdf --format csv-all --out all_tables.csv

  # Specific pages, camelot lattice engine
  python parse_pdf_tables.py report.pdf --pages 1,3,5 --engine camelot --flavor lattice
        """,
    )
    parser.add_argument("file", help="Path to PDF file")
    parser.add_argument("--engine", choices=["auto", "pdfplumber", "camelot", "pymupdf", "tabula"],
                        default="auto")
    parser.add_argument("--pages", default="", help="Comma-separated 1-based page numbers")
    parser.add_argument("--flavor", choices=["lattice", "stream"], default="lattice",
                        help="Camelot flavor (default: lattice)")
    parser.add_argument("--format", choices=["json", "csv", "csv-all", "summary"],
                        default="summary")
    parser.add_argument("--table", type=int, default=0,
                        help="Table index for --format csv (default: 0)")
    parser.add_argument("--out", default="", help="Output file path")
    args = parser.parse_args()

    pages = [int(p) for p in args.pages.split(",") if p.strip()] if args.pages else None
    tables = extract(args.file, engine=args.engine, pages=pages, camelot_flavor=args.flavor)

    if args.format == "summary":
        print(f"Found {len(tables)} table(s)")
        for t in tables:
            print(f"  Page {t.page} Table {t.table_index} [{t.engine}] — {t.row_count} rows × {t.col_count} cols")
            print(f"    Headers: {t.headers[:6]}{'…' if len(t.headers) > 6 else ''}")
        return

    if args.format == "json":
        output = to_json(tables)
    elif args.format == "csv":
        output = to_csv(tables, args.table)
    else:
        output = to_csv_all(tables)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
