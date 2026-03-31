"""
test_parse_github_api.py

Run with:
    pytest test_parse_github_api.py -v

Unit tests use inline fixture dicts — no network calls, no token needed.
Integration tests (marked live) hit the real API and require GITHUB_TOKEN.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from parse_github_api import (
    Commit,
    Issue,
    PullRequest,
    Release,
    Repo,
    _detect_type,
    _to_dict,
    parse_raw,
    to_csv,
    to_json,
    to_flat_records,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

RAW_REPO = {
    "id": 1, "name": "agentskills", "full_name": "agentnxxt/agentskills",
    "owner": {"login": "agentnxxt"}, "private": False,
    "description": "Skills repo", "html_url": "https://github.com/agentnxxt/agentskills",
    "homepage": None, "language": "Python", "stargazers_count": 42,
    "forks_count": 5, "open_issues_count": 3, "default_branch": "main",
    "topics": ["ai", "mcp"], "license": {"spdx_id": "MIT"}, "archived": False,
    "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-06-01T00:00:00Z",
    "pushed_at": "2024-06-01T00:00:00Z",
}

RAW_ISSUE = {
    "id": 10, "number": 42, "title": "Fix parser", "state": "open",
    "user": {"login": "chinmay"}, "body": "Parser fails on edge case.",
    "labels": [{"name": "bug"}, {"name": "priority"}],
    "assignees": [{"login": "chinmay"}],
    "html_url": "https://github.com/agentnxxt/agentskills/issues/42",
    "created_at": "2024-03-01T10:00:00Z", "updated_at": "2024-03-02T10:00:00Z",
    "closed_at": None, "comments": 2,
}

RAW_PR = {
    "id": 20, "number": 7, "title": "Add GitHub parser", "state": "open",
    "user": {"login": "chinmay"}, "body": "Adds parse_github_api.py",
    "base": {"ref": "main"}, "head": {"ref": "feat/github-parser"},
    "html_url": "https://github.com/agentnxxt/agentskills/pull/7",
    "draft": False, "merged": False, "merged_at": None,
    "created_at": "2024-04-01T00:00:00Z", "updated_at": "2024-04-02T00:00:00Z",
    "labels": [{"name": "enhancement"}], "requested_reviewers": [],
    "additions": 300, "deletions": 10, "changed_files": 2,
    "pull_request": {},  # presence triggers PR detection
}

RAW_RELEASE = {
    "id": 30, "tag_name": "v1.0.0", "name": "First release", "body": "Initial.",
    "draft": False, "prerelease": False,
    "author": {"login": "chinmay"},
    "html_url": "https://github.com/agentnxxt/agentskills/releases/tag/v1.0.0",
    "tarball_url": "https://...", "zipball_url": "https://...",
    "assets": [], "created_at": "2024-05-01T00:00:00Z",
    "published_at": "2024-05-01T00:00:00Z",
}

RAW_COMMIT = {
    "sha": "abc123def456",
    "commit": {
        "message": "feat: add GitHub API parser",
        "author": {"name": "Chinmay", "email": "c@example.com", "date": "2024-06-01T12:00:00Z"},
        "committer": {"name": "GitHub", "email": "noreply@github.com", "date": "2024-06-01T12:00:00Z"},
    },
    "html_url": "https://github.com/agentnxxt/agentskills/commit/abc123",
    "stats": {"additions": 150, "deletions": 20, "total": 170},
    "parents": [{"sha": "parent1"}],
}


# ---------------------------------------------------------------------------
# _detect_type
# ---------------------------------------------------------------------------

class TestDetectType:
    def test_repo(self):
        assert _detect_type(RAW_REPO) == "repo"

    def test_issue(self):
        assert _detect_type(RAW_ISSUE) == "issue"

    def test_pull_request(self):
        assert _detect_type(RAW_PR) == "pull_request"

    def test_release(self):
        assert _detect_type(RAW_RELEASE) == "release"

    def test_commit(self):
        assert _detect_type(RAW_COMMIT) == "commit"

    def test_unknown(self):
        assert _detect_type({"foo": "bar"}) == "unknown"


# ---------------------------------------------------------------------------
# Repo
# ---------------------------------------------------------------------------

class TestRepo:
    def test_fields(self):
        r = Repo.from_raw(RAW_REPO)
        assert r.name == "agentskills"
        assert r.owner == "agentnxxt"
        assert r.stars == 42
        assert r.language == "Python"
        assert r.license == "MIT"
        assert "ai" in r.topics

    def test_datetime_parsing(self):
        r = Repo.from_raw(RAW_REPO)
        assert isinstance(r.created_at, datetime)

    def test_none_homepage(self):
        r = Repo.from_raw(RAW_REPO)
        assert r.homepage == ""

    def test_missing_license(self):
        raw = {**RAW_REPO, "license": None}
        r = Repo.from_raw(raw)
        assert r.license == ""


# ---------------------------------------------------------------------------
# Issue
# ---------------------------------------------------------------------------

class TestIssue:
    def test_fields(self):
        i = Issue.from_raw(RAW_ISSUE)
        assert i.number == 42
        assert i.title == "Fix parser"
        assert i.author == "chinmay"
        assert "bug" in i.labels
        assert i.is_pull_request is False
        assert i.comments == 2

    def test_pull_request_flag(self):
        raw = {**RAW_ISSUE, "pull_request": {}}
        i = Issue.from_raw(raw)
        assert i.is_pull_request is True

    def test_closed_at_none(self):
        i = Issue.from_raw(RAW_ISSUE)
        assert i.closed_at is None


# ---------------------------------------------------------------------------
# PullRequest
# ---------------------------------------------------------------------------

class TestPullRequest:
    def test_fields(self):
        pr = PullRequest.from_raw(RAW_PR)
        assert pr.number == 7
        assert pr.base_branch == "main"
        assert pr.head_branch == "feat/github-parser"
        assert pr.additions == 300
        assert pr.draft is False
        assert pr.merged is False

    def test_labels(self):
        pr = PullRequest.from_raw(RAW_PR)
        assert "enhancement" in pr.labels


# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------

class TestRelease:
    def test_fields(self):
        r = Release.from_raw(RAW_RELEASE)
        assert r.tag_name == "v1.0.0"
        assert r.asset_count == 0
        assert r.prerelease is False
        assert r.author == "chinmay"

    def test_published_at(self):
        r = Release.from_raw(RAW_RELEASE)
        assert isinstance(r.published_at, datetime)


# ---------------------------------------------------------------------------
# Commit
# ---------------------------------------------------------------------------

class TestCommit:
    def test_fields(self):
        c = Commit.from_raw(RAW_COMMIT)
        assert c.sha == "abc123def456"
        assert c.author_name == "Chinmay"
        assert c.additions == 150
        assert c.total == 170
        assert c.parents == ["parent1"]

    def test_message_stripped(self):
        raw = {**RAW_COMMIT, "commit": {**RAW_COMMIT["commit"], "message": "  msg  "}}
        c = Commit.from_raw(raw)
        assert c.message == "msg"


# ---------------------------------------------------------------------------
# parse_raw
# ---------------------------------------------------------------------------

class TestParseRaw:
    def test_mixed_list(self):
        records = [RAW_REPO, RAW_ISSUE, RAW_RELEASE, RAW_COMMIT, RAW_PR]
        parsed = parse_raw(records)
        types = [type(o).__name__ for o in parsed]
        assert "Repo" in types
        assert "Issue" in types
        assert "Release" in types
        assert "Commit" in types
        assert "PullRequest" in types

    def test_unknown_passthrough(self):
        parsed = parse_raw([{"foo": "bar"}])
        assert parsed[0] == {"foo": "bar"}

    def test_empty(self):
        assert parse_raw([]) == []


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def _repo(self):
        return Repo.from_raw(RAW_REPO)

    def test_to_flat_records(self):
        records = to_flat_records([self._repo()])
        assert isinstance(records[0], dict)
        assert records[0]["name"] == "agentskills"

    def test_topics_pipe_joined(self):
        records = to_flat_records([self._repo()])
        assert "|" in records[0]["topics"] or records[0]["topics"] in ("ai", "mcp", "ai|mcp")

    def test_to_json(self):
        import json
        result = json.loads(to_json([self._repo()]))
        assert result[0]["name"] == "agentskills"

    def test_to_csv(self):
        csv_str = to_csv([self._repo()])
        lines = csv_str.strip().splitlines()
        assert lines[0].startswith("id,")
        assert len(lines) == 2

    def test_to_csv_empty(self):
        assert to_csv([]) == ""


# ---------------------------------------------------------------------------
# Integration (live, skipped without token)
# ---------------------------------------------------------------------------

import os

# ---------------------------------------------------------------------------
# fetch_file / fetch_file_as_csv
# ---------------------------------------------------------------------------

class TestFetchFile:
    """Unit tests using mocked HTTP responses."""

    def _mock_response(self, content_str: str, name: str = "data.tsv") -> MagicMock:
        import base64
        encoded = base64.b64encode(content_str.encode()).decode() + "\n"
        mock = MagicMock()
        mock.json.return_value = {
            "name": name, "path": f"dir/{name}", "sha": "abc",
            "size": len(content_str), "html_url": "https://github.com/...",
            "download_url": f"https://raw.githubusercontent.com/.../{name}",
            "content": encoded, "encoding": "base64", "type": "file",
        }
        mock.raise_for_status = MagicMock()
        return mock

    @patch("parse_github_api._get")
    def test_fetch_file_returns_content(self, mock_get):
        mock_get.return_value = self._mock_response("col1\tcol2\nval1\tval2")
        from parse_github_api import fetch_file
        result = fetch_file("owner", "repo", "dir/data.tsv")
        assert "col1" in result["content"]
        assert result["name"] == "data.tsv"
        assert result["size"] > 0

    @patch("parse_github_api._get")
    def test_fetch_file_as_csv_tsv(self, mock_get):
        tsv = "id\tname\n1\tAlpha\n2\tBeta\n"
        mock_get.return_value = self._mock_response(tsv, "data.tsv")
        from parse_github_api import fetch_file_as_csv
        rows = fetch_file_as_csv("owner", "repo", "dir/data.tsv")
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["name"] == "Alpha"

    @patch("parse_github_api._get")
    def test_fetch_file_as_csv_csv(self, mock_get):
        csv_content = "id,name\n1,Alpha\n2,Beta\n"
        mock_get.return_value = self._mock_response(csv_content, "data.csv")
        from parse_github_api import fetch_file_as_csv
        rows = fetch_file_as_csv("owner", "repo", "dir/data.csv")
        assert len(rows) == 2
        assert rows[1]["name"] == "Beta"

    @patch("parse_github_api._get")
    def test_fetch_file_directory_raises(self, mock_get):
        mock = MagicMock()
        mock.json.return_value = [{"name": "file1.tsv"}, {"name": "file2.tsv"}]
        mock.raise_for_status = MagicMock()
        mock_get.return_value = mock
        from parse_github_api import fetch_file
        with pytest.raises(ValueError, match="is a directory"):
            fetch_file("owner", "repo", "some/dir")

    @patch("parse_github_api._get")
    def test_blank_rows_skipped(self, mock_get):
        tsv = "id\tname\n1\tAlpha\n\t\n2\tBeta\n"
        mock_get.return_value = self._mock_response(tsv, "data.tsv")
        from parse_github_api import fetch_file_as_csv
        rows = fetch_file_as_csv("owner", "repo", "dir/data.tsv")
        assert len(rows) == 2


@pytest.mark.skipif(not os.environ.get("GITHUB_TOKEN") and False,
                    reason="Public repo — always runs")
class TestLiveIAB:
    """Live test against the public IAB Taxonomies repo — no token needed."""

    def test_fetch_iab_content_taxonomy(self):
        from parse_github_api import fetch_file_as_csv
        rows = fetch_file_as_csv(
            "InteractiveAdvertisingBureau",
            "Taxonomies",
            "Content Taxonomies/Content Taxonomy 3.1.tsv",
            ref="develop",
        )
        assert len(rows) > 700
        # header row becomes dict keys
        first = rows[0]
        assert any("ID" in k or "Tier" in k or "Name" in k for k in first.keys())

    def test_fetch_iab_content_raw(self):
        from parse_github_api import fetch_file
        result = fetch_file(
            "InteractiveAdvertisingBureau",
            "Taxonomies",
            "Content Taxonomies/Content Taxonomy 3.1.tsv",
            ref="develop",
        )
        assert result["name"].endswith(".tsv")
        assert result["size"] > 0
        assert "\t" in result["content"]



    def test_fetch_repo(self):
        from parse_github_api import fetch_repo
        repo = fetch_repo("agentnxxt", "agentskills")
        assert repo.full_name == "agentnxxt/agentskills"
        assert repo.stars >= 0

    def test_fetch_releases(self):
        from parse_github_api import fetch_releases
        releases = fetch_releases("agentnxxt", "agentskills")
        assert isinstance(releases, list)

    def test_search_repos(self):
        from parse_github_api import search_repos
        results = search_repos("autonomyx mcp", sort="stars")
        assert isinstance(results, list)
