"""
parse_nextjs_ssr.py
Extract any nested data from a saved Next.js SSR page (HTML file).

Works with any Next.js app that embeds its server-side data in:
  - <script id="__NEXT_DATA__"> (canonical)
  - Any large inline <script> whose text begins with '{"props"'
  - Any inline <script> >100 KB containing 'pageProps'

Usage — library:
    from parse_nextjs_ssr import extract, extract_path, to_csv, to_json

Usage — CLI:
    python parse_nextjs_ssr.py page.html --path props.pageProps.data --format csv --out out.csv
    python parse_nextjs_ssr.py page.html --path props.pageProps.data --format json
    python parse_nextjs_ssr.py page.html --keys          # list all top-level keys

pip install beautifulsoup4 lxml
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Core: load HTML and pull Next.js payload
# ---------------------------------------------------------------------------

def load_soup(html_path: str | Path):
    """Parse an HTML file with BeautifulSoup (lxml preferred)."""
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise ImportError("Run: pip install beautifulsoup4 lxml") from e

    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {html_path}")

    text = html_path.read_text(encoding="utf-8")
    try:
        return BeautifulSoup(text, "lxml")
    except Exception:
        return BeautifulSoup(text, "html.parser")


def extract_next_data(soup) -> dict:
    """
    Pull the Next.js pageProps JSON from a BeautifulSoup-parsed page.

    Strategy order:
    1. <script id="__NEXT_DATA__"> — canonical Next.js tag
    2. First <script> whose text starts with '{"props"'
    3. Largest <script> >100 KB that contains 'pageProps'

    Raises
    ------
    ValueError
        If no matching script tag is found.
    """
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if tag:
        return json.loads(tag.get_text())

    best: str | None = None
    for script in soup.find_all("script"):
        text = script.get_text().strip()
        if text.startswith('{"props"'):
            return json.loads(text)
        if len(text) > 100_000 and "pageProps" in text:
            if best is None or len(text) > len(best):
                best = text

    if best:
        return json.loads(best)

    raise ValueError(
        "No Next.js pageProps payload found. "
        "The page may be client-rendered or the structure has changed."
    )


def extract(html_path: str | Path) -> dict:
    """
    Extract the full Next.js JSON payload from a saved HTML file.

    Returns the raw dict — callers use extract_path() to drill into it.
    """
    return extract_next_data(load_soup(html_path))


def extract_path(html_path: str | Path, dot_path: str) -> Any:
    """
    Extract a nested value from the Next.js payload using a dot-separated path.

    Parameters
    ----------
    html_path : str | Path
        Path to the saved HTML file.
    dot_path : str
        Dot-separated key path, e.g. 'props.pageProps.serverSideXHRData.categories'.

    Returns
    -------
    Any
        The value at that path (dict, list, str, int, …).

    Raises
    ------
    KeyError
        If any key in the path is missing.
    """
    data = extract(html_path)
    for key in dot_path.split("."):
        if isinstance(data, dict):
            data = data[key]
        else:
            raise KeyError(f"Cannot descend into non-dict with key '{key}'")
    return data


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def to_json(data: Any, indent: int = 2) -> str:
    """Serialise extracted data to a JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False)


def to_csv(data: Any) -> str:
    """
    Serialise extracted data to CSV.

    Accepts:
    - list[dict]  — written directly as rows
    - dict        — each top-level key becomes a row with 'key' and 'value' columns
    - list        — each item stringified into a single 'value' column

    Returns a CSV string.
    """
    buf = io.StringIO()

    if isinstance(data, list) and data and isinstance(data[0], dict):
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    elif isinstance(data, dict):
        writer = csv.DictWriter(buf, fieldnames=["key", "value"])
        writer.writeheader()
        for k, v in data.items():
            writer.writerow({"key": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v})

    else:
        writer = csv.DictWriter(buf, fieldnames=["value"])
        writer.writeheader()
        for item in (data if isinstance(data, list) else [data]):
            writer.writerow({"value": json.dumps(item) if isinstance(item, (dict, list)) else item})

    return buf.getvalue()


def flatten(data: Any, parent_key: str = "", sep: str = ".") -> dict:
    """
    Recursively flatten a nested dict/list into a single-level dict.

    Useful for turning deeply nested JSON into a spreadsheet-friendly structure.
    List items are indexed: 'key.0.field', 'key.1.field', …
    """
    items: dict = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten(v, new_key, sep))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(flatten(v, new_key, sep))
    else:
        items[parent_key] = data
    return items


def list_keys(data: dict, depth: int = 2, _current: int = 0) -> list[str]:
    """
    List keys in a nested dict up to *depth* levels.

    Useful for exploring an unfamiliar payload before extracting.
    """
    result = []
    if not isinstance(data, dict) or _current >= depth:
        return result
    for k, v in data.items():
        result.append("  " * _current + k)
        result.extend(list_keys(v, depth, _current + 1))
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract data from a saved Next.js SSR HTML page.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List top-level keys in the payload
  python parse_nextjs_ssr.py page.html --keys

  # Extract a nested list and write as CSV
  python parse_nextjs_ssr.py page.html \\
      --path props.pageProps.serverSideXHRData.categories \\
      --format csv --out categories.csv

  # Dump the full payload as JSON
  python parse_nextjs_ssr.py page.html --format json
        """,
    )
    parser.add_argument("html_file", help="Path to the saved HTML file")
    parser.add_argument(
        "--path",
        default="",
        help="Dot-separated key path to extract (e.g. props.pageProps.data). "
             "Omit to return the full payload.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "keys"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--keys", action="store_true", help="List payload keys and exit")
    parser.add_argument("--depth", type=int, default=3, help="Key listing depth (default: 3)")
    parser.add_argument("--out", help="Write output to file instead of stdout")
    args = parser.parse_args()

    data = extract(args.html_file)

    if args.keys or args.format == "keys":
        output = "\n".join(list_keys(data, depth=args.depth))
    else:
        if args.path:
            for key in args.path.split("."):
                data = data[key]
        output = to_csv(data) if args.format == "csv" else to_json(data)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
