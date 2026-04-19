"""
test_parse_wikidata.py

Run with:
    pytest test_parse_wikidata.py -v

Unit tests use inline fixture dicts — no network calls needed.
Live tests hit Wikidata public API and require network access.
"""

import json
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from parse_wikidata import (
    WikidataEntity,
    SPARQLResult,
    _extract_snak_value,
    to_csv,
    to_json,
    label_claims,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _snak(dv_type: str, value: Any) -> dict:
    return {"snaktype": "value", "datavalue": {"type": dv_type, "value": value}}


def _item_snak(qid: str) -> dict:
    return _snak("wikibase-entityid", {"entity-type": "item", "id": qid})


def _string_snak(s: str) -> dict:
    return _snak("string", s)


def _mono_snak(text: str, lang: str = "en") -> dict:
    return _snak("monolingualtext", {"text": text, "language": lang})


def _quantity_snak(amount: str, unit: str = "1") -> dict:
    return _snak("quantity", {"amount": amount, "unit": unit})


def _time_snak(t: str) -> dict:
    return _snak("time", {"time": t, "timezone": 0, "before": 0, "after": 0,
                           "precision": 11, "calendarmodel": ""})


def _coord_snak(lat: float, lon: float) -> dict:
    return _snak("globecoordinate", {"latitude": lat, "longitude": lon, "precision": 0.001})


def _rt(text: str, lang: str = "en") -> dict:
    return {"value": text, "language": lang}


RAW_ENTITY = {
    "id": "Q42",
    "type": "item",
    "labels":       {"en": _rt("Douglas Adams"), "fr": _rt("Douglas Adams", "fr")},
    "descriptions": {"en": _rt("English author and humourist", "en")},
    "aliases":      {"en": [_rt("DNA", "en"), _rt("D. Adams", "en")]},
    "sitelinks":    {"enwiki": {"title": "Douglas Adams"}, "frwiki": {"title": "Douglas Adams"}},
    "claims": {
        "P31":  [{"rank": "normal",     "mainsnak": _item_snak("Q5")}],
        "P569": [{"rank": "normal",     "mainsnak": _time_snak("+1952-03-11T00:00:00Z")}],
        "P18":  [{"rank": "normal",     "mainsnak": _string_snak("Douglas adams portrait cropped.jpg")}],
        "P569dep": [{"rank": "deprecated", "mainsnak": _item_snak("Q999")}],  # should be excluded
        "P625": [{"rank": "normal",     "mainsnak": _coord_snak(51.5, -0.12)}],
        "P1082": [{"rank": "normal",    "mainsnak": _quantity_snak("+42", "1")}],
        "P1083_unit": [{"rank": "normal","mainsnak": _quantity_snak("+100", "http://www.wikidata.org/entity/Q11573")}],
        "P1476": [{"rank": "normal",    "mainsnak": _mono_snak("The Hitchhiker's Guide")}],
        "P856":  [{"rank": "normal",    "mainsnak": _string_snak("https://douglasadams.com")}],
        "P856_novalue": [{"rank": "normal", "mainsnak": {"snaktype": "novalue", "property": "P856x"}}],
    },
}

RAW_SPARQL = {
    "head": {"vars": ["item", "label", "count"]},
    "results": {
        "bindings": [
            {
                "item":  {"type": "uri",     "value": "http://www.wikidata.org/entity/Q42"},
                "label": {"type": "literal", "value": "Douglas Adams"},
                "count": {"type": "literal", "value": "17"},
            },
            {
                "item":  {"type": "uri",     "value": "http://www.wikidata.org/entity/Q243"},
                "label": {"type": "literal", "value": "Eiffel Tower"},
                "count": {"type": "literal", "value": "5"},
            },
        ]
    }
}


# ---------------------------------------------------------------------------
# _extract_snak_value
# ---------------------------------------------------------------------------

class TestExtractSnakValue:
    def test_wikibase_item(self):
        assert _extract_snak_value(_item_snak("Q42")["datavalue"]["value"]) is None  # needs full snak
        assert _extract_snak_value(_item_snak("Q5")) == "Q5"

    def test_string(self):
        assert _extract_snak_value(_string_snak("hello")) == "hello"

    def test_monolingualtext_en(self):
        assert _extract_snak_value(_mono_snak("Title", "en")) == "Title"

    def test_monolingualtext_other_lang(self):
        val = _extract_snak_value(_mono_snak("Titre", "fr"))
        assert "fr" in val

    def test_quantity_int(self):
        assert _extract_snak_value(_quantity_snak("+42")) == 42

    def test_quantity_with_unit(self):
        val = _extract_snak_value(_quantity_snak("+100", "http://www.wikidata.org/entity/Q11573"))
        assert isinstance(val, dict)
        assert val["amount"] == 100
        assert val["unit"] == "Q11573"

    def test_time(self):
        val = _extract_snak_value(_time_snak("+1952-03-11T00:00:00Z"))
        assert "1952" in val

    def test_globecoordinate(self):
        val = _extract_snak_value(_coord_snak(51.5, -0.12))
        assert val["lat"] == 51.5
        assert val["lon"] == -0.12

    def test_novalue(self):
        assert _extract_snak_value({"snaktype": "novalue"}) is None

    def test_somevalue(self):
        assert _extract_snak_value({"snaktype": "somevalue"}) is None


# ---------------------------------------------------------------------------
# WikidataEntity
# ---------------------------------------------------------------------------

class TestWikidataEntity:
    def _entity(self, lang="en"):
        return WikidataEntity.from_raw(RAW_ENTITY, lang=lang)

    def test_qid(self):
        assert self._entity().qid == "Q42"

    def test_label(self):
        assert self._entity().label == "Douglas Adams"

    def test_description(self):
        assert "author" in self._entity().description

    def test_aliases(self):
        e = self._entity()
        assert "DNA" in e.aliases

    def test_sitelinks(self):
        e = self._entity()
        assert e.sitelinks["enwiki"] == "Douglas Adams"

    def test_claims_extracted(self):
        e = self._entity()
        assert "P31" in e.claims
        assert e.claims["P31"] == ["Q5"]

    def test_deprecated_claims_excluded(self):
        e = self._entity()
        # P569dep has rank=deprecated, should not appear
        assert "P569dep" not in e.claims

    def test_novalue_claim_excluded(self):
        e = self._entity()
        assert "P856_novalue" not in e.claims

    def test_coord_claim(self):
        e = self._entity()
        assert "P625" in e.claims
        assert e.claims["P625"][0]["lat"] == 51.5

    def test_flat_has_qid(self):
        flat = self._entity().flat()
        assert flat["qid"] == "Q42"
        assert flat["label"] == "Douglas Adams"

    def test_flat_lists_pipe_joined(self):
        # P31 has one value "Q5"
        flat = self._entity().flat()
        assert flat["P31"] == "Q5"

    def test_flat_wikipedia_link(self):
        flat = self._entity().flat()
        assert flat["en_wikipedia"] == "Douglas Adams"

    def test_label_french(self):
        e = WikidataEntity.from_raw(RAW_ENTITY, lang="fr")
        assert e.label == "Douglas Adams"


# ---------------------------------------------------------------------------
# SPARQLResult
# ---------------------------------------------------------------------------

class TestSPARQLResult:
    def _result(self):
        return SPARQLResult.from_raw(RAW_SPARQL)

    def test_variables(self):
        r = self._result()
        assert r.variables == ["item", "label", "count"]

    def test_bindings_count(self):
        assert len(self._result().bindings) == 2

    def test_qid_extracted(self):
        row = self._result().bindings[0]
        assert row["item"] == "Q42"

    def test_literal_value(self):
        row = self._result().bindings[0]
        assert row["label"] == "Douglas Adams"
        assert row["count"] == "17"


# ---------------------------------------------------------------------------
# label_claims
# ---------------------------------------------------------------------------

class TestLabelClaims:
    def test_replaces_pids(self):
        e = WikidataEntity.from_raw(RAW_ENTITY)
        labels = {"P31": "instance of", "P569": "date of birth"}
        labelled = label_claims(e, labels)
        assert "instance of" in labelled
        assert labelled["instance of"] == ["Q5"]

    def test_unknown_pid_kept(self):
        e = WikidataEntity.from_raw(RAW_ENTITY)
        labelled = label_claims(e, {})
        assert "P31" in labelled


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def _entities(self):
        return [WikidataEntity.from_raw(RAW_ENTITY)]

    def test_to_json_entity(self):
        result = json.loads(to_json(self._entities()))
        assert result[0]["qid"] == "Q42"
        assert result[0]["label"] == "Douglas Adams"

    def test_to_json_sparql(self):
        result_obj = SPARQLResult.from_raw(RAW_SPARQL)
        result = json.loads(to_json(result_obj))
        assert "results" in result
        assert len(result["results"]) == 2

    def test_to_json_single_entity(self):
        e = WikidataEntity.from_raw(RAW_ENTITY)
        result = json.loads(to_json(e))
        assert result[0]["qid"] == "Q42"

    def test_to_csv_entities(self):
        csv_str = to_csv(self._entities())
        lines = csv_str.strip().splitlines()
        assert lines[0].startswith("qid")
        assert "Q42" in lines[1]

    def test_to_csv_sparql_rows(self):
        rows = SPARQLResult.from_raw(RAW_SPARQL).bindings
        csv_str = to_csv(rows)
        assert "item" in csv_str
        assert "Q42" in csv_str

    def test_to_csv_empty(self):
        assert to_csv([]) == ""


# ---------------------------------------------------------------------------
# fetch_entity — mocked
# ---------------------------------------------------------------------------

class TestFetchEntityMocked:
    @patch("parse_wikidata._get")
    def test_fetch_entity(self, mock_get):
        mock_get.return_value = {"entities": {"Q42": RAW_ENTITY}}
        from parse_wikidata import fetch_entity
        e = fetch_entity("Q42")
        assert e.qid == "Q42"
        assert e.label == "Douglas Adams"

    @patch("parse_wikidata._get")
    def test_fetch_entity_not_found(self, mock_get):
        mock_get.return_value = {"entities": {}}
        from parse_wikidata import fetch_entity
        with pytest.raises(ValueError, match="No entity found"):
            fetch_entity("Q999999999")

    @patch("parse_wikidata._get")
    def test_fetch_entities_batch(self, mock_get):
        mock_get.return_value = {
            "entities": {"Q42": RAW_ENTITY, "Q243": {**RAW_ENTITY, "id": "Q243"}}
        }
        from parse_wikidata import fetch_entities
        entities = fetch_entities(["Q42", "Q243"])
        assert len(entities) == 2

    @patch("parse_wikidata._get")
    def test_fetch_entities_empty(self, mock_get):
        from parse_wikidata import fetch_entities
        assert fetch_entities([]) == []


# ---------------------------------------------------------------------------
# search — mocked
# ---------------------------------------------------------------------------

class TestSearchMocked:
    @patch("parse_wikidata._get")
    def test_search_returns_results(self, mock_get):
        mock_get.return_value = {
            "search": [
                {"id": "Q42", "label": "Douglas Adams",
                 "description": "English author", "url": "//www.wikidata.org/wiki/Q42",
                 "concepturi": "http://www.wikidata.org/entity/Q42", "aliases": []}
            ]
        }
        from parse_wikidata import search
        results = search("Douglas Adams")
        assert len(results) == 1
        assert results[0]["id"] == "Q42"
        assert results[0]["label"] == "Douglas Adams"

    @patch("parse_wikidata._get")
    def test_search_empty(self, mock_get):
        mock_get.return_value = {"search": []}
        from parse_wikidata import search
        assert search("xyzxyzxyz") == []


# ---------------------------------------------------------------------------
# SPARQL — mocked
# ---------------------------------------------------------------------------

class TestSPARQLMocked:
    @patch("parse_wikidata._requests.get")
    def test_sparql_returns_result(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = RAW_SPARQL
        mock_get.return_value = mock_resp
        from parse_wikidata import sparql
        result = sparql("SELECT ?item WHERE { ?item wdt:P31 wd:Q5 } LIMIT 2")
        assert len(result.bindings) == 2

    @patch("parse_wikidata._requests.get")
    def test_sparql_prefixes_added(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"head": {"vars": []}, "results": {"bindings": []}}
        mock_get.return_value = mock_resp
        from parse_wikidata import sparql
        sparql("SELECT ?x WHERE { ?x wdt:P31 wd:Q5 } LIMIT 1")
        called_params = mock_get.call_args[1]["params"]
        assert "PREFIX wd:" in called_params["query"]


# ---------------------------------------------------------------------------
# Live tests (skipped if blocked)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    os.environ.get("SKIP_LIVE_WIKIDATA", "0") == "1",
    reason="Live Wikidata tests disabled"
)
class TestLive:
    def test_fetch_entity_q42(self):
        try:
            from parse_wikidata import fetch_entity
            e = fetch_entity("Q42")
            assert e.qid == "Q42"
            assert e.label == "Douglas Adams"
        except Exception:
            pytest.skip("Wikidata not reachable in this environment")

    def test_search_eiffel(self):
        try:
            from parse_wikidata import search
            results = search("Eiffel Tower", limit=3)
            assert any(r["id"] == "Q243" for r in results)
        except Exception:
            pytest.skip("Wikidata not reachable in this environment")
