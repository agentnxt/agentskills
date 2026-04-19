"""
parse_wordpress.py
Generic parser for the WordPress REST API — any self-hosted or WordPress.com site.

Covers:
  Posts, Pages, Categories, Tags, Authors, Media, Comments, Custom Post Types.

Two site modes:
  1. Self-hosted WP  — https://yoursite.com/wp-json/wp/v2/
  2. WordPress.com   — https://public-api.wordpress.com/wp/v2/sites/{site}/

Authentication:
  - Public content  — no auth needed
  - Private/draft   — Application Password (WP 5.6+) or JWT token

pip install requests beautifulsoup4

Environment (optional — only for authenticated operations):
  WP_URL      Base URL of your WordPress site
  WP_USER     WordPress username
  WP_APP_PASS Application Password (Settings > Users > Application Passwords)
"""

from __future__ import annotations

import csv
import io
import json
import os
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

WP_JSON_PATH  = "/wp-json/wp/v2"
WPCOM_BASE    = "https://public-api.wordpress.com/wp/v2/sites/{site}"
DEFAULT_UA    = "AutonomyxWPParser/1.0 (https://openautonomyx.com)"
_RATE_DELAY   = 0.1   # seconds between paginated requests


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class WPClient:
    """
    Thin WordPress REST API client — handles auth, base URL, pagination.

    Parameters
    ----------
    site : str
        Either a full base URL (self-hosted):
          'https://myblog.com'
        Or a WordPress.com site identifier:
          'myblog.wordpress.com' or 'myblog'
    username : str, optional
        WP username for authenticated requests.
    app_password : str, optional
        Application Password (WP 5.6+). Generate at:
        Settings → Users → Your Profile → Application Passwords.
    wpcom : bool
        Force WordPress.com API mode.
    user_agent : str
        User-Agent header value.
    """

    def __init__(self, site: str, username: str = "", app_password: str = "",
                 wpcom: bool = False, user_agent: str = DEFAULT_UA):
        self.user_agent = user_agent
        self._auth: tuple[str, str] | None = None

        if username and app_password:
            self._auth = (username, app_password)

        # Determine base URL
        if wpcom or ("wordpress.com" in site and not site.startswith("http")):
            # WordPress.com mode
            slug = site.replace("https://", "").replace("http://", "").rstrip("/")
            self.base = WPCOM_BASE.format(site=slug)
        elif site.startswith("http"):
            # Self-hosted
            self.base = site.rstrip("/") + WP_JSON_PATH
        else:
            # Assume WordPress.com subdomain
            self.base = WPCOM_BASE.format(site=site)

    def get(self, endpoint: str, params: dict | None = None,
            timeout: int = 20) -> Any:
        url = f"{self.base}/{endpoint.lstrip('/')}"
        headers = {"User-Agent": self.user_agent}
        resp = _requests.get(url, params=params or {}, headers=headers,
                              auth=self._auth, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict, timeout: int = 20) -> Any:
        url = f"{self.base}/{endpoint.lstrip('/')}"
        headers = {"User-Agent": self.user_agent, "Content-Type": "application/json"}
        resp = _requests.post(url, json=data, headers=headers,
                               auth=self._auth, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def patch(self, endpoint: str, data: dict, timeout: int = 20) -> Any:
        url = f"{self.base}/{endpoint.lstrip('/')}"
        headers = {"User-Agent": self.user_agent, "Content-Type": "application/json"}
        resp = _requests.patch(url, json=data, headers=headers,
                                auth=self._auth, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def delete(self, endpoint: str, params: dict | None = None, timeout: int = 20) -> Any:
        url = f"{self.base}/{endpoint.lstrip('/')}"
        headers = {"User-Agent": self.user_agent}
        resp = _requests.delete(url, params=params or {}, headers=headers,
                                 auth=self._auth, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def paginate(self, endpoint: str, params: dict | None = None,
                 per_page: int = 100, max_pages: int = 100) -> list[dict]:
        """Fetch all pages of a list endpoint."""
        results = []
        p = {"per_page": per_page, "page": 1, **(params or {})}
        for _ in range(max_pages):
            try:
                batch = self.get(endpoint, params=p)
            except _requests.HTTPError as e:
                if e.response.status_code == 400:
                    break  # no more pages
                raise
            if not batch:
                break
            results.extend(batch)
            if len(batch) < per_page:
                break
            p["page"] += 1
            time.sleep(_RATE_DELAY)
        return results


def _client_from_env() -> WPClient:
    url  = os.environ.get("WP_URL", "")
    user = os.environ.get("WP_USER", "")
    pwd  = os.environ.get("WP_APP_PASS", "")
    if not url:
        raise EnvironmentError(
            "Set WP_URL (and optionally WP_USER + WP_APP_PASS) environment variables."
        )
    return WPClient(url, username=user, app_password=pwd)


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _strip_html(html: str) -> str:
    """Strip HTML tags and decode common entities."""
    text = re.sub(r"<[^>]+>", "", html or "")
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#8217;", "'").replace("&#8220;", '"')
    text = text.replace("&nbsp;", " ").replace("&#8230;", "…")
    return " ".join(text.split()).strip()


def _rendered(field_val: Any) -> str:
    """Extract .rendered from WP rendered field dict, or return as-is."""
    if isinstance(field_val, dict):
        return field_val.get("rendered", "")
    return str(field_val or "")


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WPPost:
    id: int
    slug: str
    status: str
    type: str
    url: str
    title: str
    content: str      # plain text (HTML stripped)
    excerpt: str      # plain text
    author_id: int
    featured_media_id: int
    categories: list[int]
    tags: list[int]
    date: str
    modified: str
    sticky: bool
    format: str
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "WPPost":
        return cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            status=raw.get("status", ""),
            type=raw.get("type", "post"),
            url=raw.get("link", ""),
            title=_strip_html(_rendered(raw.get("title"))),
            content=_strip_html(_rendered(raw.get("content"))),
            excerpt=_strip_html(_rendered(raw.get("excerpt"))),
            author_id=raw.get("author", 0),
            featured_media_id=raw.get("featured_media", 0),
            categories=raw.get("categories", []),
            tags=raw.get("tags", []),
            date=raw.get("date", ""),
            modified=raw.get("modified", ""),
            sticky=raw.get("sticky", False),
            format=raw.get("format", "standard"),
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "status": self.status,
            "type": self.type,
            "url": self.url,
            "title": self.title,
            "excerpt": self.excerpt[:300],
            "author_id": self.author_id,
            "featured_media_id": self.featured_media_id,
            "categories": " | ".join(str(c) for c in self.categories),
            "tags": " | ".join(str(t) for t in self.tags),
            "date": self.date,
            "modified": self.modified,
            "sticky": self.sticky,
            "format": self.format,
        }


@dataclass
class WPPage:
    id: int
    slug: str
    status: str
    url: str
    title: str
    content: str
    excerpt: str
    author_id: int
    parent: int
    menu_order: int
    date: str
    modified: str
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "WPPage":
        return cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            status=raw.get("status", ""),
            url=raw.get("link", ""),
            title=_strip_html(_rendered(raw.get("title"))),
            content=_strip_html(_rendered(raw.get("content"))),
            excerpt=_strip_html(_rendered(raw.get("excerpt"))),
            author_id=raw.get("author", 0),
            parent=raw.get("parent", 0),
            menu_order=raw.get("menu_order", 0),
            date=raw.get("date", ""),
            modified=raw.get("modified", ""),
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id, "slug": self.slug, "status": self.status,
            "url": self.url, "title": self.title,
            "excerpt": self.excerpt[:300],
            "author_id": self.author_id, "parent": self.parent,
            "menu_order": self.menu_order,
            "date": self.date, "modified": self.modified,
        }


@dataclass
class WPTerm:
    id: int
    name: str
    slug: str
    taxonomy: str   # "category" or "post_tag"
    description: str
    count: int
    url: str
    parent: int
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict, taxonomy: str = "category") -> "WPTerm":
        return cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
            slug=raw.get("slug", ""),
            taxonomy=raw.get("taxonomy", taxonomy),
            description=_strip_html(raw.get("description", "")),
            count=raw.get("count", 0),
            url=raw.get("link", ""),
            parent=raw.get("parent", 0),
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id, "name": self.name, "slug": self.slug,
            "taxonomy": self.taxonomy, "description": self.description,
            "count": self.count, "url": self.url, "parent": self.parent,
        }


@dataclass
class WPAuthor:
    id: int
    name: str
    slug: str
    url: str
    description: str
    avatar_url: str
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "WPAuthor":
        avatars = raw.get("avatar_urls", {})
        avatar_url = avatars.get("96", avatars.get("48", ""))
        return cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
            slug=raw.get("slug", ""),
            url=raw.get("link", ""),
            description=_strip_html(raw.get("description", "")),
            avatar_url=avatar_url,
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id, "name": self.name, "slug": self.slug,
            "url": self.url, "description": self.description,
            "avatar_url": self.avatar_url,
        }


@dataclass
class WPMedia:
    id: int
    slug: str
    url: str
    source_url: str
    alt_text: str
    caption: str
    media_type: str
    mime_type: str
    width: int
    height: int
    date: str
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "WPMedia":
        details = raw.get("media_details", {})
        return cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            url=raw.get("link", ""),
            source_url=raw.get("source_url", ""),
            alt_text=raw.get("alt_text", ""),
            caption=_strip_html(_rendered(raw.get("caption"))),
            media_type=raw.get("media_type", ""),
            mime_type=raw.get("mime_type", ""),
            width=details.get("width", 0),
            height=details.get("height", 0),
            date=raw.get("date", ""),
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id, "slug": self.slug, "url": self.url,
            "source_url": self.source_url, "alt_text": self.alt_text,
            "caption": self.caption, "media_type": self.media_type,
            "mime_type": self.mime_type, "width": self.width,
            "height": self.height, "date": self.date,
        }


@dataclass
class WPComment:
    id: int
    post_id: int
    parent: int
    author_name: str
    author_email: str
    author_url: str
    date: str
    content: str
    status: str
    raw: dict = field(repr=False, default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict) -> "WPComment":
        return cls(
            id=raw.get("id", 0),
            post_id=raw.get("post", 0),
            parent=raw.get("parent", 0),
            author_name=raw.get("author_name", ""),
            author_email=raw.get("author_email", ""),
            author_url=raw.get("author_url", ""),
            date=raw.get("date", ""),
            content=_strip_html(_rendered(raw.get("content"))),
            status=raw.get("status", ""),
            raw=raw,
        )

    def flat(self) -> dict:
        return {
            "id": self.id, "post_id": self.post_id, "parent": self.parent,
            "author_name": self.author_name, "author_email": self.author_email,
            "author_url": self.author_url, "date": self.date,
            "content": self.content[:300], "status": self.status,
        }


# ---------------------------------------------------------------------------
# Public API — Read
# ---------------------------------------------------------------------------

def fetch_posts(client: WPClient, status: str = "publish",
                category: int | None = None, tag: int | None = None,
                author: int | None = None, search: str = "",
                after: str = "", before: str = "",
                per_page: int = 100) -> list[WPPost]:
    """
    Fetch all posts, auto-paginated.

    Parameters
    ----------
    status : str
        'publish', 'draft', 'private', 'any'. 'draft'/'private' require auth.
    category : int | None
        Filter by category ID.
    tag : int | None
        Filter by tag ID.
    author : int | None
        Filter by author ID.
    search : str
        Full-text search string.
    after : str
        ISO 8601 date — posts published after this date.
    before : str
        ISO 8601 date — posts published before this date.
    """
    params: dict[str, Any] = {"status": status}
    if category is not None:
        params["categories"] = category
    if tag is not None:
        params["tags"] = tag
    if author is not None:
        params["author"] = author
    if search:
        params["search"] = search
    if after:
        params["after"] = after
    if before:
        params["before"] = before

    raw = client.paginate("posts", params=params, per_page=per_page)
    return [WPPost.from_raw(r) for r in raw]


def fetch_post(client: WPClient, post_id: int) -> WPPost:
    """Fetch a single post by ID."""
    return WPPost.from_raw(client.get(f"posts/{post_id}"))


def fetch_pages(client: WPClient, status: str = "publish",
                per_page: int = 100) -> list[WPPage]:
    """Fetch all pages."""
    raw = client.paginate("pages", params={"status": status}, per_page=per_page)
    return [WPPage.from_raw(r) for r in raw]


def fetch_categories(client: WPClient, per_page: int = 100) -> list[WPTerm]:
    """Fetch all categories."""
    raw = client.paginate("categories", per_page=per_page)
    return [WPTerm.from_raw(r, taxonomy="category") for r in raw]


def fetch_tags(client: WPClient, per_page: int = 100) -> list[WPTerm]:
    """Fetch all tags."""
    raw = client.paginate("tags", per_page=per_page)
    return [WPTerm.from_raw(r, taxonomy="post_tag") for r in raw]


def fetch_authors(client: WPClient, per_page: int = 100) -> list[WPAuthor]:
    """Fetch all authors (requires authentication on most sites)."""
    raw = client.paginate("users", per_page=per_page)
    return [WPAuthor.from_raw(r) for r in raw]


def fetch_media(client: WPClient, media_type: str = "",
                mime_type: str = "", per_page: int = 100) -> list[WPMedia]:
    """
    Fetch media library items (requires authentication on most sites).

    Parameters
    ----------
    media_type : str
        Filter by type: 'image', 'video', 'audio', 'application'.
    mime_type : str
        Filter by MIME type: 'image/jpeg', 'application/pdf', etc.
    """
    params: dict[str, Any] = {}
    if media_type:
        params["media_type"] = media_type
    if mime_type:
        params["mime_type"] = mime_type
    raw = client.paginate("media", params=params, per_page=per_page)
    return [WPMedia.from_raw(r) for r in raw]


def fetch_comments(client: WPClient, post_id: int | None = None,
                   status: str = "approve", per_page: int = 100) -> list[WPComment]:
    """
    Fetch comments, optionally filtered by post.

    Parameters
    ----------
    post_id : int | None
        Filter to a specific post. None = all comments.
    status : str
        'approve', 'hold', 'spam', 'trash'. Non-approve requires auth.
    """
    params: dict[str, Any] = {"status": status}
    if post_id is not None:
        params["post"] = post_id
    raw = client.paginate("comments", params=params, per_page=per_page)
    return [WPComment.from_raw(r) for r in raw]


def search_posts(client: WPClient, query: str,
                 post_type: str = "post") -> list[WPPost]:
    """Full-text search across posts."""
    raw = client.paginate("posts", params={"search": query, "type": post_type})
    return [WPPost.from_raw(r) for r in raw]


def fetch_custom_post_type(client: WPClient, post_type: str,
                            params: dict | None = None,
                            per_page: int = 100) -> list[dict]:
    """
    Fetch any custom post type (CPT) — returns raw dicts.

    Parameters
    ----------
    post_type : str
        The REST API slug of the CPT (e.g. 'products', 'events').
    """
    raw = client.paginate(post_type, params=params, per_page=per_page)
    return raw


# ---------------------------------------------------------------------------
# Public API — Write (requires auth)
# ---------------------------------------------------------------------------

def create_post(client: WPClient, title: str, content: str,
                status: str = "draft", categories: list[int] | None = None,
                tags: list[int] | None = None, excerpt: str = "",
                slug: str = "") -> WPPost:
    """Create a new post (requires auth)."""
    data: dict[str, Any] = {
        "title": title, "content": content, "status": status,
    }
    if categories:
        data["categories"] = categories
    if tags:
        data["tags"] = tags
    if excerpt:
        data["excerpt"] = excerpt
    if slug:
        data["slug"] = slug
    return WPPost.from_raw(client.post("posts", data))


def update_post(client: WPClient, post_id: int, **fields: Any) -> WPPost:
    """
    Update a post's fields (requires auth).

    Pass any WP REST API field as a keyword argument:
    e.g. update_post(client, 42, title="New Title", status="publish")
    """
    return WPPost.from_raw(client.patch(f"posts/{post_id}", fields))


def create_page(client: WPClient, title: str, content: str,
                status: str = "draft", parent: int = 0) -> WPPage:
    """Create a new page (requires auth)."""
    data: dict[str, Any] = {"title": title, "content": content, "status": status}
    if parent:
        data["parent"] = parent
    return WPPage.from_raw(client.post("pages", data))


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def _flat(obj: Any) -> dict:
    if hasattr(obj, "flat"):
        return obj.flat()
    return obj if isinstance(obj, dict) else {"value": str(obj)}


def to_flat_records(items: list) -> list[dict]:
    return [_flat(item) for item in items]


def to_json(items: Any, indent: int = 2) -> str:
    if not isinstance(items, list):
        items = [items]
    return json.dumps([_flat(i) for i in items], indent=indent,
                      ensure_ascii=False, default=str)


def to_csv(items: list) -> str:
    rows = to_flat_records(items)
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
        description="Fetch and parse WordPress REST API content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment:
  WP_URL       WordPress site URL (required)
  WP_USER      Username (optional, for auth)
  WP_APP_PASS  Application Password (optional, for auth)

Examples:
  # Fetch all published posts as CSV
  WP_URL=https://myblog.com python parse_wordpress.py posts --format csv --out posts.csv

  # Fetch from WordPress.com site
  python parse_wordpress.py posts --site techcrunch.wordpress.com --format json

  # Fetch pages
  python parse_wordpress.py pages --site myblog.wordpress.com --format csv

  # Fetch categories
  python parse_wordpress.py categories --site myblog.wordpress.com

  # Search posts
  python parse_wordpress.py search "machine learning" --site myblog.wordpress.com

  # Fetch comments for a post
  python parse_wordpress.py comments --post-id 42 --site myblog.wordpress.com
        """,
    )
    parser.add_argument("resource",
                        choices=["posts", "pages", "categories", "tags",
                                 "authors", "media", "comments", "search"])
    parser.add_argument("--site", default="", help="WordPress site URL or WP.com slug")
    parser.add_argument("--status", default="publish")
    parser.add_argument("--category", type=int, default=None)
    parser.add_argument("--tag", type=int, default=None)
    parser.add_argument("--author", type=int, default=None)
    parser.add_argument("--post-id", type=int, default=None)
    parser.add_argument("--after", default="")
    parser.add_argument("--before", default="")
    parser.add_argument("--query", default="", help="Search query")
    parser.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    site = args.site or os.environ.get("WP_URL", "")
    if not site:
        parser.error("Provide --site or set WP_URL environment variable")

    user = os.environ.get("WP_USER", "")
    pwd  = os.environ.get("WP_APP_PASS", "")
    client = WPClient(site, username=user, app_password=pwd)

    if args.resource == "posts":
        items = fetch_posts(client, status=args.status, category=args.category,
                            tag=args.tag, author=args.author,
                            after=args.after, before=args.before)
    elif args.resource == "pages":
        items = fetch_pages(client, status=args.status)
    elif args.resource == "categories":
        items = fetch_categories(client)
    elif args.resource == "tags":
        items = fetch_tags(client)
    elif args.resource == "authors":
        items = fetch_authors(client)
    elif args.resource == "media":
        items = fetch_media(client)
    elif args.resource == "comments":
        items = fetch_comments(client, post_id=args.post_id)
    elif args.resource == "search":
        query = args.query or input("Search query: ")
        items = search_posts(client, query)

    if args.format == "summary":
        print(f"{len(items)} {args.resource}")
        for item in items[:10]:
            flat = _flat(item)
            title = flat.get("title") or flat.get("name") or flat.get("slug") or str(flat.get("id"))
            print(f"  [{flat.get('id')}] {title}")
        if len(items) > 10:
            print(f"  … {len(items) - 10} more")
        return

    output = to_json(items) if args.format == "json" else to_csv(items)
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
