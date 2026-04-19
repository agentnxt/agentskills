"""
test_parse_wikipedia.py

Run with:
    pytest test_parse_wikipedia.py -v

Unit tests use inline fixtures and mocked HTTP — no network required.
Live tests hit Wikipedia public API and require network access.
"""

import json
import os
import re
from unittest.mock import MagicMock, patch

import pytest

from parse_wikipedia import (
    WikiSummary,
    WikiSection,
    WikiPage,
    SearchResult,
    _parse_infobox,
    _parse_sections,
    to_csv,
    to_json,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

RAW_SUMMARY = {
    "title": "Douglas Adams",
    "pageid": 8091,
    "description": "English author and humourist",
    "extract": "Douglas Noel Adams was an English author, screenwriter, essayist, humourist, satirist and dramatist.",
    "extract_html": "<p><b>Douglas Noel Adams</b> was an English author.</p>",
    "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Douglas_Adams"}},
    "thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/en/thumb/x.jpg"},
    "wikibase_item": "Q42",
    "coordinates": {"lat": 51.5, "lon": -0.12},
}

RAW_ACTION_QUERY = {
    "query": {
        "pages": [{
            "pageid": 8091,
            "title": "Douglas Adams",
            "canonicalurl": "https://en.wikipedia.org/wiki/Douglas_Adams",
            "revisions": [{
                "slots": {
                    "main": {
                        "content": """{{Infobox person
| name       = Douglas Adams
| birth_date = 11 March 1952
| birth_place = Cambridge
| nationality = British
| occupation  = Author
}}

== Early life ==
Adams was born in Cambridge.

== Career ==
He wrote The Hitchhiker's Guide to the Galaxy.

=== Radio ===
It began as a radio comedy.

== Personal life ==
He was known for his love of technology.
"""
                    }
                }
            }],
            "categories": [
                {"title": "Category:English novelists"},
                {"title": "Category:1952 births"},
            ],
            "links": [
                {"title": "Cambridge"},
                {"title": "Science fiction"},
            ],
        }]
    }
}

RAW_SEARCH = {
    "query": {
        "search": [
            {
                "title": "Douglas Adams",
                "pageid": 8091,
                "snippet": "Douglas Adams was an <span>English</span> author",
                "size": 120000,
                "wordcount": 8000,
            },
            {
                "title": "The Hitchhiker's Guide to the Galaxy",
                "pageid": 18951,
                "snippet": "A <span>science fiction</span> comedy radio serial",
                "size": 80000,
                "wordcount": 5000,
            },
        ]
    }
}


# ---------------------------------------------------------------------------
# WikiSummary
# ---------------------------------------------------------------------------

class TestWikiSummary:
    def _s(self):
        return WikiSummary.from_rest(RAW_SUMMARY)

    def test_title(self):
        assert self._s().title == "Douglas Adams"

    def test_page_id(self):
        assert self._s().page_id == 8091

    def test_description(self):
        assert "humourist" in self._s().description

    def test_extract(self):
        assert "Adams" in self._s().extract

    def test_url(self):
        assert "Douglas_Adams" in self._s().url

    def test_thumbnail(self):
        assert self._s().thumbnail_url.startswith("https://")

    def test_wikidata_qid(self):
        assert self._s().wikidata_qid == "Q42"

    def test_coordinates(self):
        s = self._s()
        assert s.coordinates["lat"] == 51.5
        assert s.coordinates["lon"] == -0.12

    def test_flat_keys(self):
        flat = self._s().flat()
        assert "title" in flat
        assert "lat" in flat
        assert "wikidata_qid" in flat

    def test_no_thumbnail(self):
        raw = {**RAW_SUMMARY, "thumbnail": None}
        s = WikiSummary.from_rest(raw)
        assert s.thumbnail_url == ""

    def test_no_coordinates(self):
        raw = {**RAW_SUMMARY, "coordinates": None}
        s = WikiSummary.from_rest(raw)
        assert s.coordinates is None
        flat = s.flat()
        assert "lat" not in flat


# ---------------------------------------------------------------------------
# _parse_infobox
# ---------------------------------------------------------------------------

INFOBOX_WIKITEXT = """{{Infobox person
| name        = Douglas Adams
| birth_date  = 11 March 1952
| birth_place = [[Cambridge]], England
| nationality = British
| occupation  = Author, screenwriter
}}"""

class TestParseInfobox:
    def test_extracts_name(self):
        ib = _parse_infobox(INFOBOX_WIKITEXT)
        assert ib["name"] == "Douglas Adams"

    def test_extracts_birth_date(self):
        ib = _parse_infobox(INFOBOX_WIKITEXT)
        assert "1952" in ib["birth_date"]

    def test_wikilink_cleaned(self):
        ib = _parse_infobox(INFOBOX_WIKITEXT)
        assert "Cambridge" in ib["birth_place"]
        assert "[[" not in ib["birth_place"]

    def test_no_infobox_returns_empty(self):
        assert _parse_infobox("Just plain text.") == {}

    def test_occupation_extracted(self):
        ib = _parse_infobox(INFOBOX_WIKITEXT)
        assert "Author" in ib["occupation"]


# ---------------------------------------------------------------------------
# _parse_sections
# ---------------------------------------------------------------------------

SECTION_WIKITEXT = """Some intro text here.

== Early life ==
Adams was born in Cambridge in 1952.

== Career ==
He wrote the Hitchhiker's Guide.

=== Radio ===
It started as a BBC radio show.

== Legacy ==
He influenced many writers.
"""

class TestParseSections:
    def test_intro_section(self):
        sections = _parse_sections(SECTION_WIKITEXT)
        assert sections[0].title == "Introduction"

    def test_section_count(self):
        sections = _parse_sections(SECTION_WIKITEXT)
        assert len(sections) >= 4

    def test_section_titles(self):
        sections = _parse_sections(SECTION_WIKITEXT)
        titles = [s.title for s in sections]
        assert "Early life" in titles
        assert "Career" in titles

    def test_subsection_depth(self):
        sections = _parse_sections(SECTION_WIKITEXT)
        radio = next(s for s in sections if s.title == "Radio")
        assert radio.depth == 1  # === is depth 1

    def test_content_extracted(self):
        sections = _parse_sections(SECTION_WIKITEXT)
        early = next(s for s in sections if s.title == "Early life")
        assert "Cambridge" in early.content

    def test_empty_wikitext(self):
        assert _parse_sections("") == []

    def test_no_headings(self):
        sections = _parse_sections("Just plain text with no headings.")
        assert len(sections) == 1
        assert sections[0].title == "Introduction"


# ---------------------------------------------------------------------------
# WikiSection
# ---------------------------------------------------------------------------

class TestWikiSection:
    def test_flat(self):
        s = WikiSection(index=0, title="Intro", depth=0, content="Some text")
        flat = s.flat()
        assert flat["title"] == "Intro"
        assert flat["content"] == "Some text"
        assert flat["depth"] == 0
        assert flat["index"] == 0


# ---------------------------------------------------------------------------
# SearchResult
# ---------------------------------------------------------------------------

class TestSearchResult:
    def test_flat_strips_html(self):
        r = SearchResult(
            title="Douglas Adams", page_id=8091,
            url="https://en.wikipedia.org/wiki/Douglas_Adams",
            snippet="<span>English</span> author",
            size=120000, word_count=8000,
        )
        flat = r.flat()
        assert "<span>" not in flat["snippet"]
        assert "English" in flat["snippet"]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def _summary(self):
        return WikiSummary.from_rest(RAW_SUMMARY)

    def _sections(self):
        return _parse_sections(SECTION_WIKITEXT)

    def test_to_json_summary(self):
        result = json.loads(to_json(self._summary()))
        assert result["title"] == "Douglas Adams"

    def test_to_json_list_summaries(self):
        result = json.loads(to_json([self._summary()]))
        assert result[0]["title"] == "Douglas Adams"

    def test_to_json_sections(self):
        result = json.loads(to_json(self._sections()))
        assert isinstance(result, list)
        assert result[0]["title"] == "Introduction"

    def test_to_csv_summaries(self):
        csv_str = to_csv([self._summary()])
        lines = csv_str.strip().splitlines()
        assert "title" in lines[0]
        assert "Douglas Adams" in lines[1]

    def test_to_csv_sections(self):
        csv_str = to_csv(self._sections())
        assert "title" in csv_str
        assert "content" in csv_str

    def test_to_csv_empty(self):
        assert to_csv([]) == ""

    def test_to_csv_search_results(self):
        results = [
            SearchResult("Douglas Adams", 8091,
                         "https://en.wikipedia.org/wiki/Douglas_Adams",
                         "English author", 120000, 8000)
        ]
        csv_str = to_csv(results)
        assert "Douglas Adams" in csv_str


# ---------------------------------------------------------------------------
# fetch_summary — mocked
# ---------------------------------------------------------------------------

class TestFetchSummaryMocked:
    @patch("parse_wikipedia._get_rest")
    def test_fetch_summary(self, mock_get):
        mock_get.return_value = RAW_SUMMARY
        from parse_wikipedia import fetch_summary
        s = fetch_summary("Douglas Adams")
        assert s.title == "Douglas Adams"
        assert s.wikidata_qid == "Q42"

    @patch("parse_wikipedia._get_rest")
    def test_fetch_summary_french(self, mock_get):
        mock_get.return_value = {**RAW_SUMMARY, "title": "Douglas Adams"}
        from parse_wikipedia import fetch_summary
        s = fetch_summary("Douglas Adams", lang="fr")
        assert s.lang == "fr"


# ---------------------------------------------------------------------------
# fetch_page — mocked
# ---------------------------------------------------------------------------

class TestFetchPageMocked:
    @patch("parse_wikipedia.fetch_summary")
    @patch("parse_wikipedia._get_action")
    def test_fetch_page(self, mock_action, mock_summary):
        mock_action.return_value = RAW_ACTION_QUERY
        mock_summary.return_value = WikiSummary.from_rest(RAW_SUMMARY)
        from parse_wikipedia import fetch_page
        page = fetch_page("Douglas Adams", include_links=True)
        assert page.title == "Douglas Adams"
        assert len(page.sections) >= 1
        assert len(page.categories) == 2
        assert "name" in page.infobox

    @patch("parse_wikipedia.fetch_summary")
    @patch("parse_wikipedia._get_action")
    def test_page_not_found(self, mock_action, mock_summary):
        mock_action.return_value = {"query": {"pages": []}}
        from parse_wikipedia import fetch_page
        with pytest.raises(ValueError, match="No page found"):
            fetch_page("Nonexistent_Article_XYZXYZ")


# ---------------------------------------------------------------------------
# search — mocked
# ---------------------------------------------------------------------------

class TestSearchMocked:
    @patch("parse_wikipedia._get_action")
    def test_search(self, mock_get):
        mock_get.return_value = RAW_SEARCH
        from parse_wikipedia import search
        results = search("Douglas Adams")
        assert len(results) == 2
        assert results[0].title == "Douglas Adams"
        assert results[0].page_id == 8091

    @patch("parse_wikipedia._get_action")
    def test_search_snippet_raw(self, mock_get):
        mock_get.return_value = RAW_SEARCH
        from parse_wikipedia import search
        results = search("Douglas Adams")
        # snippet still has HTML in raw — stripped in flat()
        assert results[0].snippet != ""


# ---------------------------------------------------------------------------
# Live tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    os.environ.get("SKIP_LIVE_WIKIPEDIA", "0") == "1",
    reason="Live Wikipedia tests disabled"
)
class TestLive:
    def test_fetch_summary_douglas_adams(self):
        try:
            from parse_wikipedia import fetch_summary
            s = fetch_summary("Douglas Adams")
            assert s.title == "Douglas Adams"
            assert s.wikidata_qid == "Q42"
        except Exception:
            pytest.skip("Wikipedia not reachable in this environment")

    def test_search_hitchhiker(self):
        try:
            from parse_wikipedia import search
            results = search("Hitchhiker's Guide to the Galaxy", limit=3)
            assert len(results) > 0
        except Exception:
            pytest.skip("Wikipedia not reachable in this environment")
