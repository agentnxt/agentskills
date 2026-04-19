"""
parse_wikipedia.py
Generic parser for Wikipedia — fetch article summaries, full content,
search, sections, links, categories, and infobox-style tables.

Access modes:
  1. REST API v1  — en.wikipedia.org/api/rest_v1  (fast, structured JSON)
  2. Action API   — en.wikipedia.org/w/api.php    (full wikitext, search)
  3. HTML parse   — parse wikitext/HTML for sections, infoboxes, tables

No authentication required — all endpoints are public.
Rate limit: max 200 req/s per IP. Identify your app in User-Agent.

pip install requests beautifulsoup4 lxml

No API key required.
"""

from __future__ import annotations

import csv
import io
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

try:
    import requests as _requests
except ImportError as e:
    raise ImportError("Run: pip install requests") from e

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REST_BASE   = "https://{lang}.wikipedia.org/api/rest_v1"
ACTION_BASE = "https://{lang}.wikipedia.org/w/api.php"
DEFAULT_LANG = "en"
DEFAULT_UA   = "AutonomyxWikipediaParser/1.0 (https://openautonomyx.com)"
_RATE_DELAY  = 0.05   # 50ms between requests


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get_rest(path: str, lang: str = DEFAULT_LANG,
              user_agent: str = DEFAULT_UA, timeout: int = 20) -> dict:
    url = REST_BASE.format(lang=lang) + path
    resp = _requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _get_action(params: dict, lang: str = DEFAULT_LANG,
                user_agent: str = DEFAULT_UA, timeout: int = 20) -> dict:
    url = ACTION_BASE.format(lang=lang)
    params = {"format": "json", "formatversion": "2", **params}
    resp = _requests.get(url, params=params,
                         headers={"User-Agent": user_agent}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WikiSummary:
    title: str
    page_id: int
    lang: str
    url: str
    description: str
    extract: str            # plain-text intro
    extract_html: str       # HTML intro
    thumbnail_url: str
    wikidata_qid: str
    coordinates: dict | None   # {"lat": ..., "lon": ...} or None

    @classmethod
    def from_rest(cls, raw: dict, lang: str = DEFAULT_LANG) -> "WikiSummary":
        thumb = raw.get("thumbnail", {}) or {}
        coords = raw.get("coordinates")
        return cls(
            title=raw.get("title", ""),
            page_id=raw.get("pageid", 0),
            lang=lang,
            url=raw.get("content_urls", {}).get("desktop", {}).get("page", ""),
            description=raw.get("description", ""),
            extract=raw.get("extract", ""),
            extract_html=raw.get("extract_html", ""),
            thumbnail_url=thumb.get("source", ""),
            wikidata_qid=raw.get("wikibase_item", ""),
            coordinates=coords,
        )

    def flat(self) -> dict:
        d = {
            "title": self.title,
            "page_id": self.page_id,
            "lang": self.lang,
            "url": self.url,
            "description": self.description,
            "extract": self.extract,
            "thumbnail_url": self.thumbnail_url,
            "wikidata_qid": self.wikidata_qid,
        }
        if self.coordinates:
            d["lat"] = self.coordinates.get("lat")
            d["lon"] = self.coordinates.get("lon")
        return d


@dataclass
class WikiSection:
    index: int
    title: str
    depth: int      # heading level (1=H2, 2=H3, etc.)
    content: str    # plain-text content of this section

    def flat(self) -> dict:
        return {
            "index": self.index,
            "title": self.title,
            "depth": self.depth,
            "content": self.content,
        }


@dataclass
class WikiPage:
    title: str
    page_id: int
    lang: str
    url: str
    wikidata_qid: str
    summary: WikiSummary | None
    sections: list[WikiSection] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    infobox: dict[str, str] = field(default_factory=dict)
    raw_wikitext: str = ""

    def flat(self) -> dict:
        d: dict[str, Any] = {
            "title": self.title,
            "page_id": self.page_id,
            "lang": self.lang,
            "url": self.url,
            "wikidata_qid": self.wikidata_qid,
            "section_count": len(self.sections),
            "category_count": len(self.categories),
            "link_count": len(self.links),
            "categories": " | ".join(self.categories[:20]),
            "links": " | ".join(self.links[:20]),
        }
        d.update({f"infobox_{k}": v for k, v in list(self.infobox.items())[:30]})
        if self.summary:
            d["description"] = self.summary.description
            d["extract"] = self.summary.extract[:500]
        return d


@dataclass
class SearchResult:
    title: str
    page_id: int
    url: str
    snippet: str
    size: int
    word_count: int

    def flat(self) -> dict:
        return {
            "title": self.title,
            "page_id": self.page_id,
            "url": self.url,
            "snippet": re.sub(r"<[^>]+>", "", self.snippet),  # strip HTML
            "size": self.size,
            "word_count": self.word_count,
        }


# ---------------------------------------------------------------------------
# Infobox parser
# ---------------------------------------------------------------------------

def _parse_infobox(wikitext: str) -> dict[str, str]:
    """
    Extract key-value pairs from a wikitext infobox.

    Handles {{Infobox ...}} templates. Returns a flat dict.
    Only gets the first/outermost infobox.
    """
    # Find the infobox block
    match = re.search(r"\{\{[Ii]nfobox[^{]*", wikitext)
    if not match:
        return {}

    start = match.start()
    depth = 0
    end = start
    for i, ch in enumerate(wikitext[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    block = wikitext[start:end]
    result: dict[str, str] = {}

    # Split on | that are at depth 1 (not inside nested {{ }})
    parts = []
    current = []
    depth = 0
    for ch in block:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == "|" and depth == 2:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        parts.append("".join(current).strip())

    for part in parts[1:]:  # skip infobox header
        if "=" in part:
            k, _, v = part.partition("=")
            k = k.strip()
            # Clean value: remove wikitext markup
            v = re.sub(r"\[\[([^\|\]]+\|)?([^\]]+)\]\]", r"\2", v)  # [[link|text]] -> text
            v = re.sub(r"\{\{[^}]+\}\}", "", v)     # remove nested templates
            v = re.sub(r"<[^>]+>", "", v)           # strip HTML tags
            v = re.sub(r"'{2,}", "", v)              # remove bold/italic
            v = " ".join(v.split()).strip()
            if k and v:
                result[k] = v

    return result


# ---------------------------------------------------------------------------
# Section parser
# ---------------------------------------------------------------------------

def _parse_sections(wikitext: str) -> list[WikiSection]:
    """Parse wikitext into sections based on == Heading == markers."""
    sections = []
    lines = wikitext.splitlines()
    current_title = "Introduction"
    current_depth = 0
    current_lines: list[str] = []
    index = 0

    heading_re = re.compile(r"^(={2,6})\s*(.+?)\s*\1\s*$")

    def _flush():
        nonlocal index
        content = "\n".join(current_lines).strip()
        content = re.sub(r"\[\[([^\|\]]+\|)?([^\]]+)\]\]", r"\2", content)
        content = re.sub(r"\{\{[^}]+\}\}", "", content)
        content = re.sub(r"<[^>]+>", "", content)
        content = re.sub(r"'{2,3}", "", content)
        content = " ".join(content.split())
        if content:
            sections.append(WikiSection(
                index=index,
                title=current_title,
                depth=current_depth,
                content=content,
            ))
            index += 1

    for line in lines:
        m = heading_re.match(line)
        if m:
            _flush()
            current_lines = []
            current_depth = len(m.group(1)) - 2
            current_title = m.group(2).strip()
        else:
            current_lines.append(line)

    _flush()
    return sections


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_summary(title: str, lang: str = DEFAULT_LANG,
                  user_agent: str = DEFAULT_UA) -> WikiSummary:
    """
    Fetch a Wikipedia article summary (intro paragraph + metadata).

    Uses the REST API v1 /page/summary endpoint — fastest option.

    Parameters
    ----------
    title : str
        Article title (spaces or underscores). Case-insensitive.
    lang : str
        Wikipedia language code (e.g. 'en', 'fr', 'de').

    Returns
    -------
    WikiSummary
    """
    slug = title.replace(" ", "_")
    raw = _get_rest(f"/page/summary/{slug}", lang=lang, user_agent=user_agent)
    return WikiSummary.from_rest(raw, lang=lang)


def fetch_page(title: str, lang: str = DEFAULT_LANG,
               include_sections: bool = True,
               include_infobox: bool = True,
               include_links: bool = False,
               include_categories: bool = True,
               user_agent: str = DEFAULT_UA) -> WikiPage:
    """
    Fetch a full Wikipedia article with sections, infobox, categories, links.

    Uses the Action API with wikitext parsing.

    Parameters
    ----------
    title : str
        Article title.
    include_sections : bool
        Parse wikitext into section objects.
    include_infobox : bool
        Extract infobox key-value pairs.
    include_links : bool
        Include all internal wiki links (can be large).
    include_categories : bool
        Include article categories.

    Returns
    -------
    WikiPage
    """
    # Fetch wikitext
    prop_parts = ["revisions", "info"]
    if include_categories:
        prop_parts.append("categories")
    if include_links:
        prop_parts.append("links")

    params: dict[str, Any] = {
        "action": "query",
        "titles": title,
        "prop": "|".join(prop_parts),
        "rvprop": "content",
        "rvslots": "main",
        "inprop": "url",
    }
    if include_categories:
        params["cllimit"] = "500"
    if include_links:
        params["pllimit"] = "500"

    data = _get_action(params, lang=lang, user_agent=user_agent)
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        raise ValueError(f"No page found for: {title}")

    page_raw = pages[0]
    page_id = page_raw.get("pageid", 0)
    canonical_title = page_raw.get("title", title)
    url = page_raw.get("canonicalurl", "")
    wikidata_qid = ""

    # Extract wikitext
    wikitext = ""
    revisions = page_raw.get("revisions", [])
    if revisions:
        slots = revisions[0].get("slots", {})
        wikitext = slots.get("main", {}).get("content", "")

    # Categories
    categories = []
    if include_categories:
        for cat in page_raw.get("categories", []):
            name = cat.get("title", "").replace("Category:", "")
            if name:
                categories.append(name)

    # Links
    links = []
    if include_links:
        for lnk in page_raw.get("links", []):
            lnk_title = lnk.get("title", "")
            if lnk_title:
                links.append(lnk_title)

    # Summary
    try:
        summary = fetch_summary(canonical_title, lang=lang, user_agent=user_agent)
        wikidata_qid = summary.wikidata_qid
        time.sleep(_RATE_DELAY)
    except Exception:
        summary = None

    # Sections
    sections = _parse_sections(wikitext) if include_sections and wikitext else []

    # Infobox
    infobox = _parse_infobox(wikitext) if include_infobox and wikitext else {}

    return WikiPage(
        title=canonical_title,
        page_id=page_id,
        lang=lang,
        url=url,
        wikidata_qid=wikidata_qid,
        summary=summary,
        sections=sections,
        categories=categories,
        links=links,
        infobox=infobox,
        raw_wikitext=wikitext,
    )


def search(query: str, lang: str = DEFAULT_LANG, limit: int = 20,
           namespace: int = 0,
           user_agent: str = DEFAULT_UA) -> list[SearchResult]:
    """
    Full-text search across Wikipedia articles.

    Parameters
    ----------
    query : str
        Search string.
    limit : int
        Max results (up to 500).
    namespace : int
        0 = articles (default), 14 = categories, 10 = templates.

    Returns
    -------
    list[SearchResult]
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": min(limit, 500),
        "srnamespace": namespace,
        "srprop": "snippet|size|wordcount",
    }
    data = _get_action(params, lang=lang, user_agent=user_agent)
    results = []
    base_url = f"https://{lang}.wikipedia.org/wiki/"
    for item in data.get("query", {}).get("search", []):
        results.append(SearchResult(
            title=item.get("title", ""),
            page_id=item.get("pageid", 0),
            url=base_url + item.get("title", "").replace(" ", "_"),
            snippet=item.get("snippet", ""),
            size=item.get("size", 0),
            word_count=item.get("wordcount", 0),
        ))
    return results


def fetch_summaries_batch(titles: list[str], lang: str = DEFAULT_LANG,
                           user_agent: str = DEFAULT_UA,
                           delay: float = _RATE_DELAY) -> list[WikiSummary]:
    """
    Fetch summaries for multiple articles. Rate-limited.

    Parameters
    ----------
    titles : list[str]
        Article titles.
    delay : float
        Seconds between requests. Default 0.05s.
    """
    summaries = []
    for title in titles:
        try:
            s = fetch_summary(title, lang=lang, user_agent=user_agent)
            summaries.append(s)
        except Exception:
            pass
        time.sleep(delay)
    return summaries


def fetch_random(lang: str = DEFAULT_LANG,
                 user_agent: str = DEFAULT_UA) -> WikiSummary:
    """Fetch a random Wikipedia article summary."""
    raw = _get_rest("/page/random/summary", lang=lang, user_agent=user_agent)
    return WikiSummary.from_rest(raw, lang=lang)


def fetch_on_this_day(month: int, day: int, event_type: str = "events",
                       lang: str = DEFAULT_LANG,
                       user_agent: str = DEFAULT_UA) -> list[dict]:
    """
    Fetch 'on this day' events for a given month/day.

    Parameters
    ----------
    event_type : str
        One of: 'events', 'births', 'deaths', 'holidays', 'selected'.
    """
    raw = _get_rest(f"/feed/onthisday/{event_type}/{month:02d}/{day:02d}",
                    lang=lang, user_agent=user_agent)
    items = raw.get(event_type, [])
    results = []
    for item in items:
        pages = item.get("pages", [])
        results.append({
            "year": item.get("year"),
            "text": item.get("text", ""),
            "pages": [p.get("title", "") for p in pages],
        })
    return results


def fetch_categories(title: str, lang: str = DEFAULT_LANG,
                      user_agent: str = DEFAULT_UA) -> list[str]:
    """Fetch all categories for an article."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "categories",
        "cllimit": "500",
    }
    data = _get_action(params, lang=lang, user_agent=user_agent)
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return []
    cats = []
    for cat in pages[0].get("categories", []):
        name = cat.get("title", "").replace("Category:", "")
        if name:
            cats.append(name)
    return cats


def fetch_links(title: str, lang: str = DEFAULT_LANG,
                 user_agent: str = DEFAULT_UA) -> list[str]:
    """Fetch all internal wiki links from an article."""
    links = []
    params: dict[str, Any] = {
        "action": "query",
        "titles": title,
        "prop": "links",
        "pllimit": "500",
        "plnamespace": "0",
    }
    while True:
        data = _get_action(params, lang=lang, user_agent=user_agent)
        pages = data.get("query", {}).get("pages", [])
        if pages:
            for lnk in pages[0].get("links", []):
                links.append(lnk.get("title", ""))
        cont = data.get("continue", {})
        if not cont:
            break
        params["plcontinue"] = cont.get("plcontinue", "")
        time.sleep(_RATE_DELAY)
    return links


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def to_json(data: Any, indent: int = 2) -> str:
    """Serialise summaries, pages, search results, or dicts to JSON."""
    if isinstance(data, WikiSummary):
        return json.dumps(data.flat(), indent=indent, ensure_ascii=False)
    if isinstance(data, WikiPage):
        d = data.flat()
        d["sections"] = [s.flat() for s in data.sections]
        return json.dumps(d, indent=indent, ensure_ascii=False, default=str)
    if isinstance(data, list):
        if data and isinstance(data[0], WikiSummary):
            return json.dumps([s.flat() for s in data], indent=indent, ensure_ascii=False)
        if data and isinstance(data[0], WikiSection):
            return json.dumps([s.flat() for s in data], indent=indent, ensure_ascii=False)
        if data and isinstance(data[0], SearchResult):
            return json.dumps([s.flat() for s in data], indent=indent, ensure_ascii=False)
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def to_csv(data: Any) -> str:
    """Serialise summaries, search results, or sections to CSV."""
    if isinstance(data, WikiPage):
        rows = [s.flat() for s in data.sections]
    elif isinstance(data, list):
        if not data:
            return ""
        if isinstance(data[0], WikiSummary):
            rows = [s.flat() for s in data]
        elif isinstance(data[0], WikiSection):
            rows = [s.flat() for s in data]
        elif isinstance(data[0], SearchResult):
            rows = [s.flat() for s in data]
        elif isinstance(data[0], dict):
            rows = data
        else:
            rows = [{"value": str(x)} for x in data]
    else:
        return ""

    if not rows:
        return ""

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
        description="Fetch and parse Wikipedia articles, search, and metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
No authentication required. Wikipedia is public.

Examples:
  # Fetch article summary
  python parse_wikipedia.py summary "Douglas Adams"

  # Fetch full article (sections + infobox + categories)
  python parse_wikipedia.py page "Douglas Adams" --format json --out page.json

  # Fetch sections as CSV
  python parse_wikipedia.py page "Douglas Adams" --output sections --format csv --out sections.csv

  # Search
  python parse_wikipedia.py search "hitchhiker guide galaxy" --limit 10

  # On this day
  python parse_wikipedia.py onthisday 3 11 --type births

  # Different language
  python parse_wikipedia.py summary "Douglas Adams" --lang fr
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # summary
    s = sub.add_parser("summary", help="Fetch article summary")
    s.add_argument("title")
    s.add_argument("--lang", default="en")
    s.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    s.add_argument("--out", default="")

    # page
    p = sub.add_parser("page", help="Fetch full article")
    p.add_argument("title")
    p.add_argument("--lang", default="en")
    p.add_argument("--output", choices=["page", "sections", "infobox", "categories"],
                   default="page")
    p.add_argument("--no-links", action="store_true")
    p.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    p.add_argument("--out", default="")

    # search
    se = sub.add_parser("search", help="Search articles")
    se.add_argument("query")
    se.add_argument("--lang", default="en")
    se.add_argument("--limit", type=int, default=10)
    se.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    se.add_argument("--out", default="")

    # onthisday
    od = sub.add_parser("onthisday", help="On this day events")
    od.add_argument("month", type=int)
    od.add_argument("day", type=int)
    od.add_argument("--type", default="events",
                    choices=["events", "births", "deaths", "holidays", "selected"])
    od.add_argument("--lang", default="en")
    od.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    od.add_argument("--out", default="")

    args = parser.parse_args()

    if args.cmd == "summary":
        data = fetch_summary(args.title, lang=args.lang)
        if args.format == "summary":
            print(f"[{data.title}] {data.description}")
            print(data.extract[:400])
            return
        output = to_json(data) if args.format == "json" else to_csv([data])

    elif args.cmd == "page":
        page = fetch_page(args.title, lang=args.lang,
                          include_links=not args.no_links)
        if args.format == "summary":
            print(f"[{page.title}] {len(page.sections)} sections, {len(page.categories)} categories")
            for s in page.sections[:5]:
                print(f"  [{s.depth}] {s.title}: {s.content[:80]}…")
            if page.infobox:
                print(f"  infobox: {dict(list(page.infobox.items())[:3])}")
            return
        if args.output == "sections":
            output = to_json(page.sections) if args.format == "json" else to_csv(page.sections)
        elif args.output == "infobox":
            output = to_json(page.infobox) if args.format == "json" else to_csv([page.infobox])
        elif args.output == "categories":
            output = to_json(page.categories) if args.format == "json" else to_csv([{"category": c} for c in page.categories])
        else:
            output = to_json(page) if args.format == "json" else to_csv(page)

    elif args.cmd == "search":
        results = search(args.query, lang=args.lang, limit=args.limit)
        if args.format == "summary":
            for r in results:
                print(f"[{r.page_id}] {r.title} — {re.sub('<[^>]+>', '', r.snippet)[:80]}")
            return
        output = to_json(results) if args.format == "json" else to_csv(results)

    elif args.cmd == "onthisday":
        events = fetch_on_this_day(args.month, args.day, args.type, lang=args.lang)
        if args.format == "summary":
            for e in events[:10]:
                print(f"[{e['year']}] {e['text'][:80]}")
            return
        output = to_json(events) if args.format == "json" else to_csv(events)

    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
