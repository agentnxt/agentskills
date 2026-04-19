"""
parse_github_api.py
Generic parser for GitHub REST API v3 responses.

Covers the most common resource types used in practice:
  - Repos        /repos/{owner}/{repo}
  - Issues       /repos/{owner}/{repo}/issues
  - Pull Requests /repos/{owner}/{repo}/pulls
  - Releases     /repos/{owner}/{repo}/releases
  - Commits      /repos/{owner}/{repo}/commits
  - Contents     /repos/{owner}/{repo}/contents/{path}
  - Search       /search/repositories, /search/code, /search/issues

Auto-detects resource type from response shape — no manual config needed.
Handles pagination transparently (Link header).
Outputs typed dataclasses, flat dicts, JSON, or CSV.

pip install requests

Environment:
  GITHUB_TOKEN — optional but strongly recommended (higher rate limits)
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
from typing import Any, Generator, Iterator
from urllib.parse import urlencode

try:
    import requests
except ImportError as e:
    raise ImportError("Run: pip install requests") from e


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.github.com"
DEFAULT_PER_PAGE = 100


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------

def _session() -> requests.Session:
    """Build a requests Session with auth and Accept headers."""
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    return s


def _get(url: str, params: dict | None = None, session: requests.Session | None = None) -> requests.Response:
    s = session or _session()
    resp = s.get(url, params=params)
    resp.raise_for_status()
    return resp


def _paginate(url: str, params: dict | None = None) -> Generator[list, None, None]:
    """
    Yield pages of results, following GitHub's Link header pagination.

    Each page is the raw list returned by the API.
    """
    s = _session()
    p = {"per_page": DEFAULT_PER_PAGE, **(params or {})}
    next_url: str | None = url
    while next_url:
        resp = _get(next_url, params=p if next_url == url else None, session=s)
        data = resp.json()
        # Search responses wrap items
        if isinstance(data, dict) and "items" in data:
            yield data["items"]
        elif isinstance(data, list):
            yield data
        else:
            yield [data]
        # Follow Link: <url>; rel="next"
        link = resp.headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        next_url = match.group(1) if match else None
        p = None  # params already encoded in next_url


def fetch_all(url: str, params: dict | None = None) -> list[dict]:
    """Fetch all pages and return a flat list of raw dicts."""
    result = []
    for page in _paginate(url, params):
        result.extend(page)
    return result


# ---------------------------------------------------------------------------
# Resource detection
# ---------------------------------------------------------------------------

def _detect_type(record: dict) -> str:
    """Infer the GitHub resource type from a raw dict's fields."""
    keys = set(record.keys())
    if "pull_request" in keys or "diff_url" in keys:
        return "pull_request"
    if "commit" in keys and "sha" in keys and "parents" in keys:
        return "commit"
    if "tag_name" in keys and "assets" in keys:
        return "release"
    if "title" in keys and "state" in keys and "body" in keys and "user" in keys:
        return "issue"
    if "full_name" in keys and "stargazers_count" in keys:
        return "repo"
    if "content" in keys and "encoding" in keys:
        return "file_content"
    if "path" in keys and "type" in keys and "sha" in keys:
        return "tree_entry"
    return "unknown"


# ---------------------------------------------------------------------------
# Typed dataclasses
# ---------------------------------------------------------------------------

def _dt(val: str | None) -> datetime | None:
    return datetime.fromisoformat(val.replace("Z", "+00:00")) if val else None


def _user(raw: dict | None) -> str:
    return raw.get("login", "") if raw else ""


@dataclass
class Repo:
    id: int
    name: str
    full_name: str
    owner: str
    private: bool
    description: str
    url: str
    homepage: str
    language: str
    stars: int
    forks: int
    open_issues: int
    default_branch: str
    topics: list[str]
    license: str
    archived: bool
    created_at: datetime | None
    updated_at: datetime | None
    pushed_at: datetime | None

    @classmethod
    def from_raw(cls, r: dict) -> "Repo":
        return cls(
            id=r["id"], name=r["name"], full_name=r["full_name"],
            owner=_user(r.get("owner")), private=r.get("private", False),
            description=r.get("description") or "",
            url=r.get("html_url", ""), homepage=r.get("homepage") or "",
            language=r.get("language") or "", stars=r.get("stargazers_count", 0),
            forks=r.get("forks_count", 0), open_issues=r.get("open_issues_count", 0),
            default_branch=r.get("default_branch", "main"),
            topics=r.get("topics", []),
            license=r.get("license", {}).get("spdx_id", "") if r.get("license") else "",
            archived=r.get("archived", False),
            created_at=_dt(r.get("created_at")), updated_at=_dt(r.get("updated_at")),
            pushed_at=_dt(r.get("pushed_at")),
        )


@dataclass
class Issue:
    id: int
    number: int
    title: str
    state: str
    author: str
    body: str
    labels: list[str]
    assignees: list[str]
    url: str
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    is_pull_request: bool
    comments: int

    @classmethod
    def from_raw(cls, r: dict) -> "Issue":
        return cls(
            id=r["id"], number=r["number"], title=r.get("title", ""),
            state=r.get("state", ""), author=_user(r.get("user")),
            body=r.get("body") or "",
            labels=[lb["name"] for lb in r.get("labels", [])],
            assignees=[_user(a) for a in r.get("assignees", [])],
            url=r.get("html_url", ""),
            created_at=_dt(r.get("created_at")), updated_at=_dt(r.get("updated_at")),
            closed_at=_dt(r.get("closed_at")),
            is_pull_request="pull_request" in r,
            comments=r.get("comments", 0),
        )


@dataclass
class PullRequest:
    id: int
    number: int
    title: str
    state: str
    author: str
    body: str
    base_branch: str
    head_branch: str
    url: str
    draft: bool
    merged: bool
    merged_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    labels: list[str]
    reviewers: list[str]
    additions: int
    deletions: int
    changed_files: int

    @classmethod
    def from_raw(cls, r: dict) -> "PullRequest":
        return cls(
            id=r["id"], number=r["number"], title=r.get("title", ""),
            state=r.get("state", ""), author=_user(r.get("user")),
            body=r.get("body") or "",
            base_branch=r.get("base", {}).get("ref", ""),
            head_branch=r.get("head", {}).get("ref", ""),
            url=r.get("html_url", ""), draft=r.get("draft", False),
            merged=r.get("merged", False),
            merged_at=_dt(r.get("merged_at")),
            created_at=_dt(r.get("created_at")), updated_at=_dt(r.get("updated_at")),
            labels=[lb["name"] for lb in r.get("labels", [])],
            reviewers=[_user(rv) for rv in r.get("requested_reviewers", [])],
            additions=r.get("additions", 0), deletions=r.get("deletions", 0),
            changed_files=r.get("changed_files", 0),
        )


@dataclass
class Release:
    id: int
    tag_name: str
    name: str
    body: str
    draft: bool
    prerelease: bool
    author: str
    url: str
    tarball_url: str
    zipball_url: str
    asset_count: int
    created_at: datetime | None
    published_at: datetime | None

    @classmethod
    def from_raw(cls, r: dict) -> "Release":
        return cls(
            id=r["id"], tag_name=r.get("tag_name", ""), name=r.get("name") or "",
            body=r.get("body") or "", draft=r.get("draft", False),
            prerelease=r.get("prerelease", False), author=_user(r.get("author")),
            url=r.get("html_url", ""), tarball_url=r.get("tarball_url", ""),
            zipball_url=r.get("zipball_url", ""),
            asset_count=len(r.get("assets", [])),
            created_at=_dt(r.get("created_at")), published_at=_dt(r.get("published_at")),
        )


@dataclass
class Commit:
    sha: str
    message: str
    author_name: str
    author_email: str
    author_date: datetime | None
    committer_name: str
    committer_date: datetime | None
    url: str
    additions: int
    deletions: int
    total: int
    parents: list[str]

    @classmethod
    def from_raw(cls, r: dict) -> "Commit":
        c = r.get("commit", r)
        author = c.get("author") or {}
        committer = c.get("committer") or {}
        stats = r.get("stats", {})
        return cls(
            sha=r.get("sha", ""),
            message=c.get("message", "").strip(),
            author_name=author.get("name", ""),
            author_email=author.get("email", ""),
            author_date=_dt(author.get("date")),
            committer_name=committer.get("name", ""),
            committer_date=_dt(committer.get("date")),
            url=r.get("html_url", ""),
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            total=stats.get("total", 0),
            parents=[p["sha"] for p in r.get("parents", [])],
        )


# ---------------------------------------------------------------------------
# Public API — fetch + parse
# ---------------------------------------------------------------------------

def parse_raw(records: list[dict]) -> list[Any]:
    """
    Auto-detect type and parse a list of raw GitHub API dicts into typed objects.

    Supports mixed lists — each record is detected independently.
    Unknown types are returned as-is (raw dict).
    """
    result = []
    for r in records:
        t = _detect_type(r)
        if t == "repo":
            result.append(Repo.from_raw(r))
        elif t == "issue":
            result.append(Issue.from_raw(r))
        elif t == "pull_request":
            result.append(PullRequest.from_raw(r))
        elif t == "release":
            result.append(Release.from_raw(r))
        elif t == "commit":
            result.append(Commit.from_raw(r))
        else:
            result.append(r)
    return result


def fetch_repo(owner: str, repo: str) -> Repo:
    """Fetch a single repo and return a typed Repo."""
    raw = _get(f"{BASE_URL}/repos/{owner}/{repo}").json()
    return Repo.from_raw(raw)


def fetch_issues(owner: str, repo: str, state: str = "open",
                 labels: str = "", since: str = "") -> list[Issue]:
    """Fetch all issues (excluding PRs) from a repo."""
    params = {"state": state}
    if labels:
        params["labels"] = labels
    if since:
        params["since"] = since
    raw = fetch_all(f"{BASE_URL}/repos/{owner}/{repo}/issues", params)
    return [Issue.from_raw(r) for r in raw if "pull_request" not in r]


def fetch_pulls(owner: str, repo: str, state: str = "open") -> list[PullRequest]:
    """Fetch all pull requests from a repo."""
    raw = fetch_all(f"{BASE_URL}/repos/{owner}/{repo}/pulls", {"state": state})
    return [PullRequest.from_raw(r) for r in raw]


def fetch_releases(owner: str, repo: str) -> list[Release]:
    """Fetch all releases from a repo."""
    raw = fetch_all(f"{BASE_URL}/repos/{owner}/{repo}/releases")
    return [Release.from_raw(r) for r in raw]


def fetch_commits(owner: str, repo: str, branch: str = "",
                  since: str = "", until: str = "", path: str = "") -> list[Commit]:
    """Fetch commits from a repo with optional filters."""
    params: dict = {}
    if branch:
        params["sha"] = branch
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if path:
        params["path"] = path
    raw = fetch_all(f"{BASE_URL}/repos/{owner}/{repo}/commits", params)
    return [Commit.from_raw(r) for r in raw]


def fetch_file(owner: str, repo: str, path: str, ref: str = "") -> dict:
    """
    Fetch a single file from a GitHub repo and return its decoded content.

    Parameters
    ----------
    owner : str
        Repository owner / org (e.g. 'InteractiveAdvertisingBureau').
    repo : str
        Repository name (e.g. 'Taxonomies').
    path : str
        File path within the repo (e.g. 'Content Taxonomies/Content Taxonomy 3.1.tsv').
        Spaces are encoded automatically.
    ref : str, optional
        Branch, tag, or commit SHA (e.g. 'develop'). Defaults to the repo's default branch.

    Returns
    -------
    dict with keys:
        name        — filename
        path        — full path in repo
        sha         — blob SHA
        size        — size in bytes
        url         — GitHub HTML URL
        download_url — direct raw download URL
        content     — decoded file content as str (UTF-8)
        encoding    — original encoding field from API ('base64')

    Raises
    ------
    ValueError
        If the path points to a directory, not a file.
    requests.HTTPError
        On 404 or other HTTP errors.
    """
    import base64
    from urllib.parse import quote

    encoded_path = "/".join(quote(part, safe="") for part in path.split("/"))
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{encoded_path}"
    params = {"ref": ref} if ref else {}
    resp = _get(url, params=params or None)
    raw = resp.json()

    if isinstance(raw, list):
        raise ValueError(f"'{path}' is a directory. Use a file path.")

    content_b64 = raw.get("content", "")
    decoded = base64.b64decode(content_b64).decode("utf-8")

    return {
        "name": raw.get("name", ""),
        "path": raw.get("path", ""),
        "sha": raw.get("sha", ""),
        "size": raw.get("size", 0),
        "url": raw.get("html_url", ""),
        "download_url": raw.get("download_url", ""),
        "content": decoded,
        "encoding": raw.get("encoding", ""),
    }


def fetch_file_as_csv(owner: str, repo: str, path: str, ref: str = "",
                      delimiter: str = "\t") -> list[dict]:
    """
    Fetch a CSV or TSV file from GitHub and return it as a list of dicts.

    Auto-detects delimiter from file extension if not specified:
    .tsv → tab, .csv → comma.

    Parameters
    ----------
    delimiter : str
        Column separator. Default is tab (TSV). Pass ',' for CSV.

    Returns
    -------
    list[dict]
        One dict per data row, keyed by header column names.
        Skips blank rows.
    """
    import csv as _csv

    file = fetch_file(owner, repo, path, ref)

    # auto-detect from extension
    ext = file["name"].rsplit(".", 1)[-1].lower()
    if ext == "csv":
        delimiter = ","
    elif ext == "tsv":
        delimiter = "\t"

    reader = _csv.DictReader(file["content"].splitlines(), delimiter=delimiter)
    return [row for row in reader if any(v.strip() for v in row.values())]


def search_repos(query: str, sort: str = "stars", order: str = "desc") -> list[Repo]:
    """Search GitHub repos and return typed Repo objects."""
    raw = fetch_all(f"{BASE_URL}/search/repositories",
                    {"q": query, "sort": sort, "order": order})
    return [Repo.from_raw(r) for r in raw]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def _to_dict(obj: Any) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        d = asdict(obj)
        # flatten lists to pipe-separated strings for CSV compat
        for k, v in d.items():
            if isinstance(v, list):
                d[k] = "|".join(str(i) for i in v)
            elif isinstance(v, datetime):
                d[k] = v.isoformat()
        return d
    return obj if isinstance(obj, dict) else {"value": str(obj)}


def to_flat_records(objects: list[Any]) -> list[dict]:
    """Flatten typed objects to a list of dicts (CSV-ready)."""
    return [_to_dict(o) for o in objects]


def to_json(objects: list[Any], indent: int = 2) -> str:
    """Serialise to JSON string."""
    def _serial(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Not serialisable: {type(o)}")
    return json.dumps([_to_dict(o) for o in objects], indent=indent, default=_serial)


def to_csv(objects: list[Any]) -> str:
    """Serialise to CSV string."""
    records = to_flat_records(objects)
    if not records:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and parse GitHub API resources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch repo metadata
  python parse_github_api.py repo agentnxxt agentskills

  # Fetch all open issues as CSV
  python parse_github_api.py issues agentnxxt agentskills --state open --format csv --out issues.csv

  # Fetch all releases as JSON
  python parse_github_api.py releases agentnxxt agentskills --format json

  # Fetch commits on a branch
  python parse_github_api.py commits agentnxxt agentskills --branch main

  # Search repos
  python parse_github_api.py search "topic:mcp language:python" --format csv
        """,
    )
    sub = parser.add_subparsers(dest="resource", required=True)

    for res in ("repo", "issues", "pulls", "releases", "commits", "file"):
        p = sub.add_parser(res)
        if res != "search":
            p.add_argument("owner")
            p.add_argument("repo")
        if res == "issues":
            p.add_argument("--state", default="open", choices=["open", "closed", "all"])
            p.add_argument("--labels", default="")
            p.add_argument("--since", default="")
        if res == "pulls":
            p.add_argument("--state", default="open", choices=["open", "closed", "all"])
        if res == "file":
            p.add_argument("file_path", help="File path within the repo")
            p.add_argument("--ref", default="", help="Branch/tag/SHA")
            p.add_argument("--delimiter", default="", help="Force delimiter (default: auto)")
            p.add_argument("--branch", default="")
            p.add_argument("--since", default="")
            p.add_argument("--until", default="")
            p.add_argument("--path", default="")

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--sort", default="stars")
    s.add_argument("--order", default="desc")

    for p in sub.choices.values():
        p.add_argument("--format", choices=["json", "csv", "summary"], default="summary")
        p.add_argument("--out", default="")

    args = parser.parse_args()

    if args.resource == "repo":
        objects = [fetch_repo(args.owner, args.repo)]
    elif args.resource == "issues":
        objects = fetch_issues(args.owner, args.repo, args.state, args.labels, args.since)
    elif args.resource == "pulls":
        objects = fetch_pulls(args.owner, args.repo, args.state)
    elif args.resource == "releases":
        objects = fetch_releases(args.owner, args.repo)
    elif args.resource == "commits":
        objects = fetch_commits(args.owner, args.repo, args.branch, args.since, args.until, args.path)
    elif args.resource == "file":
        from parse_github_api import fetch_file, fetch_file_as_csv
        if args.format == "csv":
            kw = {"delimiter": args.delimiter} if args.delimiter else {}
            objects = fetch_file_as_csv(args.owner, args.repo, args.file_path, args.ref, **kw)
            output = to_csv(objects) if objects and isinstance(objects[0], dict) else "\n".join(str(r) for r in objects)
        else:
            result = fetch_file(args.owner, args.repo, args.file_path, args.ref)
            output = result["content"] if args.format == "summary" else to_json([result])
        if args.out:
            from pathlib import Path
            Path(args.out).write_text(output, encoding="utf-8")
            print(f"Written to {args.out}")
        else:
            print(output[:2000] + ("\n…truncated" if len(output) > 2000 else ""))
        return


    if args.format == "json":
        output = to_json(objects)
    elif args.format == "csv":
        output = to_csv(objects)
    else:
        lines = [f"{type(objects[0]).__name__} — {len(objects)} record(s)"]
        for o in objects[:20]:
            d = _to_dict(o)
            lines.append("  " + "  ".join(f"{k}={v}" for k, v in list(d.items())[:4]))
        if len(objects) > 20:
            lines.append(f"  … {len(objects) - 20} more")
        output = "\n".join(lines)

    if args.out:
        from pathlib import Path
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
