"""
test_parse_nextjs_ssr.py

Run with:
    pytest test_parse_nextjs_ssr.py -v

Tests the generic Next.js SSR parser — no Gartner-specific logic.
"""

import json
from pathlib import Path

import pytest

from parse_nextjs_ssr import (
    extract,
    extract_next_data,
    extract_path,
    flatten,
    list_keys,
    load_soup,
    to_csv,
    to_json,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PAYLOAD = {
    "props": {
        "pageProps": {
            "serverSideXHRData": {
                "items": [
                    {"id": 1, "name": "Alpha", "slug": "alpha"},
                    {"id": 2, "name": "Beta", "slug": "beta"},
                ],
                "meta": {"total": 2, "page": 1},
            }
        }
    }
}


def _html(payload: dict, use_id: bool = True) -> str:
    js = json.dumps(payload)
    tag = (
        f'<script id="__NEXT_DATA__" type="application/json">{js}</script>'
        if use_id
        else f"<script>{js}</script>"
    )
    return f"<html><body>{tag}</body></html>"


def _write(tmp_path, payload, use_id=True) -> Path:
    p = tmp_path / "page.html"
    p.write_text(_html(payload, use_id=use_id), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# extract_next_data
# ---------------------------------------------------------------------------

class TestExtractNextData:
    def _soup(self, html):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser")

    def test_id_attribute(self):
        data = extract_next_data(self._soup(_html(PAYLOAD, use_id=True)))
        assert "props" in data

    def test_heuristic_fallback(self):
        data = extract_next_data(self._soup(_html(PAYLOAD, use_id=False)))
        assert "props" in data

    def test_raises_on_no_match(self):
        with pytest.raises(ValueError, match="No Next.js pageProps payload"):
            extract_next_data(self._soup("<html><body><script>var x=1</script></body></html>"))


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

class TestExtract:
    def test_returns_dict(self, tmp_path):
        p = _write(tmp_path, PAYLOAD)
        data = extract(p)
        assert isinstance(data, dict)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract("/no/such/file.html")


# ---------------------------------------------------------------------------
# extract_path
# ---------------------------------------------------------------------------

class TestExtractPath:
    def test_top_level(self, tmp_path):
        p = _write(tmp_path, PAYLOAD)
        result = extract_path(p, "props")
        assert "pageProps" in result

    def test_deep_path(self, tmp_path):
        p = _write(tmp_path, PAYLOAD)
        items = extract_path(p, "props.pageProps.serverSideXHRData.items")
        assert len(items) == 2
        assert items[0]["name"] == "Alpha"

    def test_missing_key_raises(self, tmp_path):
        p = _write(tmp_path, PAYLOAD)
        with pytest.raises(KeyError):
            extract_path(p, "props.pageProps.nonexistent")

    def test_meta_value(self, tmp_path):
        p = _write(tmp_path, PAYLOAD)
        meta = extract_path(p, "props.pageProps.serverSideXHRData.meta")
        assert meta["total"] == 2


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------

class TestToJson:
    def test_list(self):
        result = json.loads(to_json([{"a": 1}]))
        assert result[0]["a"] == 1

    def test_dict(self):
        result = json.loads(to_json({"x": 42}))
        assert result["x"] == 42

    def test_indent(self):
        result = to_json({"k": "v"}, indent=4)
        assert "    " in result


# ---------------------------------------------------------------------------
# to_csv
# ---------------------------------------------------------------------------

class TestToCsv:
    def test_list_of_dicts(self):
        data = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        csv_str = to_csv(data)
        lines = csv_str.strip().splitlines()
        assert lines[0] == "id,name"
        assert len(lines) == 3

    def test_plain_dict(self):
        csv_str = to_csv({"foo": "bar", "baz": 1})
        assert "key,value" in csv_str
        assert "foo" in csv_str

    def test_plain_list(self):
        csv_str = to_csv(["x", "y", "z"])
        assert "value" in csv_str
        assert "x" in csv_str


# ---------------------------------------------------------------------------
# flatten
# ---------------------------------------------------------------------------

class TestFlatten:
    def test_nested_dict(self):
        result = flatten({"a": {"b": {"c": 1}}})
        assert result["a.b.c"] == 1

    def test_list_indexing(self):
        result = flatten({"items": [{"id": 1}, {"id": 2}]})
        assert result["items.0.id"] == 1
        assert result["items.1.id"] == 2

    def test_scalar(self):
        result = flatten({"x": 42})
        assert result["x"] == 42

    def test_custom_sep(self):
        result = flatten({"a": {"b": 1}}, sep="/")
        assert "a/b" in result


# ---------------------------------------------------------------------------
# list_keys
# ---------------------------------------------------------------------------

class TestListKeys:
    def test_depth_1(self):
        keys = list_keys(PAYLOAD, depth=1)
        assert keys == ["props"]

    def test_depth_2(self):
        keys = list_keys(PAYLOAD, depth=2)
        assert any("pageProps" in k for k in keys)

    def test_non_dict_stops(self):
        keys = list_keys({"a": [1, 2, 3]}, depth=3)
        assert keys == ["a"]


# ---------------------------------------------------------------------------
# Integration: real Gartner HTML (skipped if absent)
# ---------------------------------------------------------------------------

REAL_HTML = Path(
    "/mnt/user-data/uploads/"
    "Explore_Enterprise_Software_Categories___Gartner_Peer_Insights.html"
)

@pytest.mark.skipif(not REAL_HTML.exists(), reason="Real HTML not mounted")
class TestIntegrationGartner:
    def test_extract_succeeds(self):
        data = extract(REAL_HTML)
        assert "props" in data

    def test_categories_count(self):
        cats = extract_path(
            REAL_HTML,
            "props.pageProps.serverSideXHRData.categories"
        )
        assert len(cats) == 21

    def test_total_markets(self):
        cats = extract_path(
            REAL_HTML,
            "props.pageProps.serverSideXHRData.categories"
        )
        total = sum(len(c["markets"]) for c in cats)
        assert total == 902

    def test_csv_output(self):
        cats = extract_path(
            REAL_HTML,
            "props.pageProps.serverSideXHRData.categories"
        )
        csv_str = to_csv(cats)
        lines = csv_str.strip().splitlines()
        assert len(lines) == 22  # header + 21 categories

    def test_flatten_top_level(self):
        data = extract(REAL_HTML)
        flat = flatten(data)
        assert any("categories" in k for k in flat)
