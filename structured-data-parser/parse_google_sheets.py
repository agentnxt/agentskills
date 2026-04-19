"""
parse_google_sheets.py
Generic parser for Google Sheets — read, extract, and convert to flat records.

Two access modes:
  1. Public sheets  — CSV export URL, no auth needed
  2. Private sheets — gspread + Google Service Account JSON

Outputs: list[dict], JSON, CSV.

pip install gspread google-auth requests

Environment (private sheets only):
  GOOGLE_SERVICE_ACCOUNT_JSON — path to service account key file, OR
  GOOGLE_SERVICE_ACCOUNT_INFO — JSON string of service account credentials
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
from typing import Any

try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def _extract_sheet_id(url_or_id: str) -> str:
    """Extract the spreadsheet ID from a Google Sheets URL or return as-is."""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url_or_id)
    return match.group(1) if match else url_or_id


def _extract_gid(url: str) -> str | None:
    """Extract the gid (sheet tab ID) from a Google Sheets URL."""
    match = re.search(r"[#&?]gid=(\d+)", url)
    return match.group(1) if match else None


def _csv_export_url(spreadsheet_id: str, gid: str | None = None) -> str:
    base = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    return f"{base}&gid={gid}" if gid else base


# ---------------------------------------------------------------------------
# Public sheet access (no auth)
# ---------------------------------------------------------------------------

def fetch_public(url_or_id: str, gid: str | None = None,
                 skip_rows: int = 0) -> list[dict]:
    """
    Fetch a public Google Sheet as a list of dicts.

    Parameters
    ----------
    url_or_id : str
        Full Google Sheets URL or bare spreadsheet ID.
    gid : str, optional
        Sheet tab ID. Extracted from URL automatically if present.
    skip_rows : int
        Number of header/metadata rows to skip before the column row.

    Returns
    -------
    list[dict]
        One dict per data row, keyed by column headers.
        Empty rows are skipped.

    Raises
    ------
    ValueError
        If the sheet is not publicly accessible.
    """
    if _requests is None:
        raise ImportError("Run: pip install requests")

    sheet_id = _extract_sheet_id(url_or_id)
    if gid is None:
        gid = _extract_gid(url_or_id)

    url = _csv_export_url(sheet_id, gid)
    resp = _requests.get(url, allow_redirects=True)

    if resp.status_code == 302 or "accounts.google.com" in resp.url:
        raise ValueError(
            "Sheet requires authentication. Use fetch_private() with a service account."
        )
    resp.raise_for_status()

    lines = resp.text.splitlines()
    if skip_rows:
        lines = lines[skip_rows:]

    reader = csv.DictReader(lines)
    return [row for row in reader if any(v.strip() for v in row.values())]


# ---------------------------------------------------------------------------
# Private sheet access (service account)
# ---------------------------------------------------------------------------

def _get_gc():
    """Build an authenticated gspread client from env."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as e:
        raise ImportError("Run: pip install gspread google-auth") from e

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    info_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_INFO")
    json_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

    if info_str:
        info = json.loads(info_str)
        creds = Credentials.from_service_account_info(info, scopes=scopes)
    elif json_path:
        creds = Credentials.from_service_account_file(json_path, scopes=scopes)
    else:
        raise EnvironmentError(
            "Set GOOGLE_SERVICE_ACCOUNT_INFO (JSON string) or "
            "GOOGLE_SERVICE_ACCOUNT_JSON (file path) to authenticate."
        )
    return gspread.authorize(creds)


def fetch_private(url_or_id: str, sheet_name: str | None = None,
                  sheet_index: int = 0, skip_rows: int = 0) -> list[dict]:
    """
    Fetch a private Google Sheet using a service account.

    Parameters
    ----------
    url_or_id : str
        Full Google Sheets URL or bare spreadsheet ID.
    sheet_name : str, optional
        Name of the worksheet tab. If omitted, uses sheet_index.
    sheet_index : int
        Zero-based index of the worksheet tab (used if sheet_name is None).
    skip_rows : int
        Rows to skip before the header row.

    Returns
    -------
    list[dict]
        One dict per data row, keyed by column headers.
    """
    gc = _get_gc()
    sheet_id = _extract_sheet_id(url_or_id)
    spreadsheet = gc.open_by_key(sheet_id)

    ws = (spreadsheet.worksheet(sheet_name) if sheet_name
          else spreadsheet.get_worksheet(sheet_index))

    all_rows = ws.get_all_values()
    if skip_rows:
        all_rows = all_rows[skip_rows:]

    if not all_rows:
        return []

    headers = all_rows[0]
    records = []
    for row in all_rows[1:]:
        # pad short rows
        padded = row + [""] * (len(headers) - len(row))
        d = dict(zip(headers, padded))
        if any(v.strip() for v in d.values()):
            records.append(d)
    return records


def list_sheets(url_or_id: str) -> list[dict]:
    """
    List all worksheet tabs in a spreadsheet (requires service account).

    Returns list of dicts with 'index', 'id', 'title', 'row_count', 'col_count'.
    """
    gc = _get_gc()
    sheet_id = _extract_sheet_id(url_or_id)
    spreadsheet = gc.open_by_key(sheet_id)
    return [
        {
            "index": i,
            "id": ws.id,
            "title": ws.title,
            "row_count": ws.row_count,
            "col_count": ws.col_count,
        }
        for i, ws in enumerate(spreadsheet.worksheets())
    ]


# ---------------------------------------------------------------------------
# Auto-detect: try public first, fall back to private
# ---------------------------------------------------------------------------

def fetch(url_or_id: str, sheet_name: str | None = None,
          gid: str | None = None, skip_rows: int = 0) -> list[dict]:
    """
    Fetch a Google Sheet — tries public CSV export first, then service account.

    Parameters
    ----------
    url_or_id : str
        Full Google Sheets URL or spreadsheet ID.
    sheet_name : str, optional
        Worksheet name (used in private mode only).
    gid : str, optional
        Sheet tab gid (used in public mode only; auto-extracted from URL).
    skip_rows : int
        Rows to skip before the header.

    Returns
    -------
    list[dict]
    """
    try:
        return fetch_public(url_or_id, gid=gid, skip_rows=skip_rows)
    except ValueError:
        return fetch_private(url_or_id, sheet_name=sheet_name, skip_rows=skip_rows)


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(records: list[dict], indent: int = 2) -> str:
    """Serialise records to JSON string."""
    return json.dumps(records, indent=indent, ensure_ascii=False)


def to_csv(records: list[dict]) -> str:
    """Serialise records to CSV string."""
    if not records:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()),
                            extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and parse Google Sheets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Public sheet — auto CSV export
  python parse_google_sheets.py "https://docs.google.com/spreadsheets/d/SHEET_ID/edit" --format csv --out out.csv

  # Specific tab by gid
  python parse_google_sheets.py SHEET_ID --gid 12345 --format json

  # Private sheet — needs GOOGLE_SERVICE_ACCOUNT_JSON set
  python parse_google_sheets.py SHEET_ID --sheet "Sheet2" --format csv

  # Skip metadata rows before the header
  python parse_google_sheets.py SHEET_ID --skip 2 --format csv

  # List all tabs (private only)
  python parse_google_sheets.py SHEET_ID --list-sheets
        """,
    )
    parser.add_argument("sheet", help="Google Sheets URL or spreadsheet ID")
    parser.add_argument("--gid", default=None, help="Sheet tab gid (public mode)")
    parser.add_argument("--sheet-name", default=None, help="Worksheet name (private mode)")
    parser.add_argument("--skip", type=int, default=0, help="Rows to skip before header")
    parser.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    parser.add_argument("--out", default="", help="Output file path")
    parser.add_argument("--list-sheets", action="store_true",
                        help="List worksheet tabs and exit (requires service account)")
    args = parser.parse_args()

    if args.list_sheets:
        tabs = list_sheets(args.sheet)
        for t in tabs:
            print(f"[{t['index']}] {t['title']} — {t['row_count']}r × {t['col_count']}c (gid={t['id']})")
        return

    records = fetch(args.sheet, sheet_name=args.sheet_name,
                    gid=args.gid, skip_rows=args.skip)

    if args.format == "json":
        output = to_json(records)
    elif args.format == "csv":
        output = to_csv(records)
    else:
        print(f"{len(records)} rows, {len(records[0]) if records else 0} columns")
        for r in records[:5]:
            print(" ", dict(list(r.items())[:4]))
        if len(records) > 5:
            print(f"  … {len(records) - 5} more rows")
        return

    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
