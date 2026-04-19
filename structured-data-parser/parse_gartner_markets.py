"""
parse_gartner_markets.py
Extracts Gartner Peer Insights market/category taxonomy from a saved HTML page.

Source: https://www.gartner.com/reviews/markets (Next.js SSR page)
Strategy: Parse the __NEXT_DATA__ JSON payload embedded in <script id="__NEXT_DATA__">
          or, when the id attribute is absent, the largest inline <script> tag that
          contains the pageProps key.

pip install beautifulsoup4 lxml
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Market:
    """A single Gartner Peer Insights market (leaf node)."""
    market_id: int
    market_name: str
    market_seo_name: str
    url: str = field(init=False)

    def __post_init__(self) -> None:
        self.url = f"https://www.gartner.com/reviews/market/{self.market_seo_name}"


@dataclass
class Category:
    """A top-level Gartner Peer Insights category containing markets."""
    category_id: str
    category_name: str
    category_seo_name: str
    markets: List[Market] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core extraction helpers
# ---------------------------------------------------------------------------

def _load_soup(html_path: str | Path):
    """Parse the HTML file with BeautifulSoup, preferring lxml."""
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise ImportError("Run: pip install beautifulsoup4 lxml") from e

    with open(html_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    try:
        return BeautifulSoup(content, "lxml")
    except Exception:
        return BeautifulSoup(content, "html.parser")


def _extract_next_data(soup) -> dict:
    """
    Extract the Next.js __NEXT_DATA__ JSON.

    Tries three strategies in order:
    1. <script id="__NEXT_DATA__"> (canonical Next.js placement)
    2. Largest <script> tag whose text starts with '{"props"'
    3. Largest <script> tag (>100 KB) that contains 'pageProps'
    """
    # Strategy 1: id attribute
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if tag:
        return json.loads(tag.get_text())

    # Strategy 2 & 3: text heuristics
    best = None
    for script in soup.find_all("script"):
        text = script.get_text().strip()
        if text.startswith('{"props"'):
            return json.loads(text)
        if len(text) > 100_000 and "pageProps" in text and (best is None or len(text) > len(best)):
            best = text

    if best:
        return json.loads(best)

    raise ValueError(
        "Could not locate Next.js pageProps JSON in this HTML file. "
        "The page structure may have changed."
    )


def _parse_categories(raw_categories: list) -> List[Category]:
    """Convert the raw SSR list into typed Category / Market objects."""
    categories: List[Category] = []
    for raw_cat in raw_categories:
        markets = [
            Market(
                market_id=m["market_id"],
                market_name=m["market_name"],
                market_seo_name=m["market_seo_name"],
            )
            for m in raw_cat.get("markets", [])
        ]
        categories.append(
            Category(
                category_id=str(raw_cat["category_id"]),
                category_name=raw_cat["category_name"],
                category_seo_name=raw_cat["category_seo_name"],
                markets=markets,
            )
        )
    return categories


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(html_path: str | Path) -> List[Category]:
    """
    Parse a saved Gartner Peer Insights markets page and return a list of
    Category objects, each containing their Market children.

    Parameters
    ----------
    html_path : str | Path
        Path to the saved HTML file.

    Returns
    -------
    List[Category]
        21 categories (as of March 2026) with 902 markets total.

    Raises
    ------
    FileNotFoundError
        If *html_path* does not exist.
    ValueError
        If the expected JSON payload cannot be located in the file.
    json.JSONDecodeError
        If the JSON payload is malformed.
    """
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {html_path}")

    soup = _load_soup(html_path)
    next_data = _extract_next_data(soup)

    try:
        raw_categories = (
            next_data["props"]["pageProps"]["serverSideXHRData"]["categories"]
        )
    except KeyError as e:
        raise ValueError(
            f"Unexpected JSON structure — key {e} not found. "
            "Gartner may have changed their page schema."
        ) from e

    return _parse_categories(raw_categories)


def to_flat_records(categories: List[Category]) -> List[dict]:
    """
    Flatten the category/market hierarchy into a list of dicts, each record
    representing one market with its parent category fields included.

    Useful for writing to CSV / DataFrame / Notion / SurrealDB.
    """
    records = []
    for cat in categories:
        for market in cat.markets:
            records.append({
                "category_id": cat.category_id,
                "category_name": cat.category_name,
                "category_seo_name": cat.category_seo_name,
                "market_id": market.market_id,
                "market_name": market.market_name,
                "market_seo_name": market.market_seo_name,
                "market_url": market.url,
            })
    return records


def to_json(categories: List[Category], indent: int = 2) -> str:
    """Serialise the categories list to a JSON string."""
    return json.dumps([asdict(c) for c in categories], indent=indent)


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    import csv
    import io

    parser = argparse.ArgumentParser(
        description="Extract Gartner Peer Insights market taxonomy from a saved HTML page."
    )
    parser.add_argument("html_file", help="Path to saved Gartner markets HTML")
    parser.add_argument(
        "--format",
        choices=["json", "csv", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument("--out", help="Write output to file instead of stdout")
    args = parser.parse_args()

    categories = parse(args.html_file)

    if args.format == "summary":
        total = sum(len(c.markets) for c in categories)
        lines = [f"{'Category':<55} Markets"]
        lines.append("-" * 65)
        for c in categories:
            lines.append(f"{c.category_name:<55} {len(c.markets):>7}")
        lines.append("-" * 65)
        lines.append(f"{'TOTAL':<55} {total:>7}")
        output = "\n".join(lines)

    elif args.format == "json":
        output = to_json(categories)

    else:  # csv
        records = to_flat_records(categories)
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
        output = buf.getvalue()

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
