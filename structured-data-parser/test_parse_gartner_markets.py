"""
test_parse_gartner_markets.py

Run with:
    pytest test_parse_gartner_markets.py -v

Requires the real HTML file at the path used in the integration test.
Unit tests use a minimal synthetic HTML that mirrors the real page structure.
"""

import json
import textwrap
from pathlib import Path

import pytest

from parse_gartner_markets import (
    Category,
    Market,
    _extract_next_data,
    _load_soup,
    parse,
    to_flat_records,
    to_json,
)

# ---------------------------------------------------------------------------
# Helpers — synthetic HTML fixture
# ---------------------------------------------------------------------------

REAL_HTML = Path(
    "/mnt/user-data/uploads/"
    "Explore_Enterprise_Software_Categories___Gartner_Peer_Insights.html"
)

SYNTHETIC_DATA = {
    "props": {
        "pageProps": {
            "serverSideXHRData": {
                "categories": [
                    {
                        "category_name": "Application Development",
                        "category_seo_name": "application_development",
                        "category_id": "1",
                        "markets": [
                            {
                                "market_name": "Observability Platforms",
                                "market_seo_name": "observability-platforms",
                                "market_id": 21,
                            },
                            {
                                "market_name": "API Management",
                                "market_seo_name": "api-management",
                                "market_id": 641,
                            },
                        ],
                    },
                    {
                        "category_name": "Artificial Intelligence",
                        "category_seo_name": "artificial_intelligence",
                        "category_id": "5",
                        "markets": [
                            {
                                "market_name": "Conversational AI Platforms",
                                "market_seo_name": "conversational-ai-platforms",
                                "market_id": 999,
                            },
                        ],
                    },
                ]
            }
        }
    }
}


def _make_html(payload: dict, use_id: bool = True) -> str:
    """Build a minimal HTML page embedding *payload* as inline JSON."""
    json_str = json.dumps(payload)
    if use_id:
        script_tag = f'<script id="__NEXT_DATA__" type="application/json">{json_str}</script>'
    else:
        script_tag = f"<script>{json_str}</script>"
    return f"<html><head></head><body>{script_tag}</body></html>"


# ---------------------------------------------------------------------------
# Unit: Market dataclass
# ---------------------------------------------------------------------------

class TestMarket:
    def test_url_auto_built(self):
        m = Market(market_id=21, market_name="Observability Platforms", market_seo_name="observability-platforms")
        assert m.url == "https://www.gartner.com/reviews/market/observability-platforms"

    def test_fields_preserved(self):
        m = Market(market_id=641, market_name="API Management", market_seo_name="api-management")
        assert m.market_id == 641
        assert m.market_name == "API Management"


# ---------------------------------------------------------------------------
# Unit: _extract_next_data
# ---------------------------------------------------------------------------

class TestExtractNextData:
    def _soup(self, html: str):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser")

    def test_extracts_via_id_attribute(self):
        html = _make_html(SYNTHETIC_DATA, use_id=True)
        data = _extract_next_data(self._soup(html))
        assert "props" in data

    def test_extracts_via_heuristic(self):
        html = _make_html(SYNTHETIC_DATA, use_id=False)
        data = _extract_next_data(self._soup(html))
        assert "props" in data

    def test_raises_when_no_valid_script(self):
        with pytest.raises(ValueError, match="Could not locate"):
            _extract_next_data(self._soup("<html><body><script>var x=1;</script></body></html>"))


# ---------------------------------------------------------------------------
# Unit: parse() — synthetic HTML
# ---------------------------------------------------------------------------

class TestParseSynthetic:
    def _write_tmp(self, tmp_path, payload, use_id=True):
        p = tmp_path / "test.html"
        p.write_text(_make_html(payload, use_id=use_id), encoding="utf-8")
        return p

    def test_happy_path_category_count(self, tmp_path):
        p = self._write_tmp(tmp_path, SYNTHETIC_DATA)
        cats = parse(p)
        assert len(cats) == 2

    def test_happy_path_market_count(self, tmp_path):
        p = self._write_tmp(tmp_path, SYNTHETIC_DATA)
        cats = parse(p)
        assert len(cats[0].markets) == 2
        assert len(cats[1].markets) == 1

    def test_category_fields(self, tmp_path):
        p = self._write_tmp(tmp_path, SYNTHETIC_DATA)
        cat = parse(p)[0]
        assert cat.category_name == "Application Development"
        assert cat.category_id == "1"
        assert cat.category_seo_name == "application_development"

    def test_market_url_built(self, tmp_path):
        p = self._write_tmp(tmp_path, SYNTHETIC_DATA)
        market = parse(p)[0].markets[0]
        assert market.url == "https://www.gartner.com/reviews/market/observability-platforms"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse("/nonexistent/path/file.html")

    def test_missing_categories_key(self, tmp_path):
        bad_payload = {"props": {"pageProps": {"serverSideXHRData": {}}}}
        p = self._write_tmp(tmp_path, bad_payload)
        with pytest.raises(ValueError, match="Unexpected JSON structure"):
            parse(p)

    def test_empty_markets_list(self, tmp_path):
        payload = json.loads(json.dumps(SYNTHETIC_DATA))
        payload["props"]["pageProps"]["serverSideXHRData"]["categories"][0]["markets"] = []
        p = self._write_tmp(tmp_path, payload)
        cats = parse(p)
        assert cats[0].markets == []


# ---------------------------------------------------------------------------
# Unit: to_flat_records()
# ---------------------------------------------------------------------------

class TestToFlatRecords:
    def _cats(self):
        from bs4 import BeautifulSoup
        from parse_gartner_markets import _extract_next_data, _parse_categories
        soup = BeautifulSoup(_make_html(SYNTHETIC_DATA), "html.parser")
        return _parse_categories(
            _extract_next_data(soup)["props"]["pageProps"]["serverSideXHRData"]["categories"]
        )

    def test_record_count(self):
        records = to_flat_records(self._cats())
        assert len(records) == 3  # 2 + 1 markets

    def test_required_keys_present(self):
        record = to_flat_records(self._cats())[0]
        for key in ("category_id", "category_name", "market_id", "market_name", "market_url"):
            assert key in record

    def test_url_in_record(self):
        record = to_flat_records(self._cats())[0]
        assert record["market_url"].startswith("https://www.gartner.com")


# ---------------------------------------------------------------------------
# Unit: to_json()
# ---------------------------------------------------------------------------

class TestToJson:
    def test_valid_json(self, tmp_path):
        p = tmp_path / "test.html"
        p.write_text(_make_html(SYNTHETIC_DATA), encoding="utf-8")
        cats = parse(p)
        result = json.loads(to_json(cats))
        assert isinstance(result, list)
        assert result[0]["category_name"] == "Application Development"


# ---------------------------------------------------------------------------
# Integration: real HTML file (skipped if file absent)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not REAL_HTML.exists(), reason="Real HTML file not mounted")
class TestIntegrationReal:
    def test_category_count(self):
        cats = parse(REAL_HTML)
        assert len(cats) == 21

    def test_total_market_count(self):
        cats = parse(REAL_HTML)
        total = sum(len(c.markets) for c in cats)
        assert total == 902

    def test_known_category_present(self):
        cats = parse(REAL_HTML)
        names = {c.category_name for c in cats}
        assert "IT Security" in names

    def test_flat_records_length(self):
        cats = parse(REAL_HTML)
        records = to_flat_records(cats)
        assert len(records) == 902

    def test_all_urls_valid_format(self):
        cats = parse(REAL_HTML)
        for cat in cats:
            for m in cat.markets:
                assert m.url.startswith("https://www.gartner.com/reviews/market/")

    def test_no_duplicate_market_ids(self):
        cats = parse(REAL_HTML)
        ids = [m.market_id for c in cats for m in c.markets]
        assert len(ids) == len(set(ids)), "Duplicate market IDs found"
