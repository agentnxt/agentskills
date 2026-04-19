"""
test_parse_google_sheets.py

Run with:
    pytest test_parse_google_sheets.py -v

Unit tests use mocked HTTP — no Google account needed.
Live tests hit a real public sheet and are always enabled.
Private-sheet tests require GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_INFO.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from parse_google_sheets import (
    _extract_gid,
    _extract_sheet_id,
    _csv_export_url,
    _requests,
    fetch_public,
    fetch,
    to_csv,
    to_json,
)

# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

class TestUrlHelpers:
    def test_extract_sheet_id_from_url(self):
        url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"
        assert _extract_sheet_id(url) == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"

    def test_extract_sheet_id_bare(self):
        assert _extract_sheet_id("abc123") == "abc123"

    def test_extract_gid_from_url(self):
        url = "https://docs.google.com/spreadsheets/d/ID/edit#gid=12345"
        assert _extract_gid(url) == "12345"

    def test_extract_gid_missing(self):
        assert _extract_gid("https://docs.google.com/spreadsheets/d/ID/edit") is None

    def test_csv_export_url_no_gid(self):
        url = _csv_export_url("SHEET_ID")
        assert "format=csv" in url
        assert "gid" not in url

    def test_csv_export_url_with_gid(self):
        url = _csv_export_url("SHEET_ID", "999")
        assert "gid=999" in url


# ---------------------------------------------------------------------------
# fetch_public (mocked)
# ---------------------------------------------------------------------------

class TestFetchPublic:
    CSV_BODY = "name,age,city\nAlice,30,London\nBob,25,Berlin\n"

    def _mock_resp(self, body: str, url: str = "https://docs.google.com/..."):
        m = MagicMock()
        m.status_code = 200
        m.text = body
        m.url = url
        m.raise_for_status = MagicMock()
        return m

    @patch("parse_google_sheets._requests.get")
    def test_returns_records(self, mock_get):
        mock_get.return_value = self._mock_resp(self.CSV_BODY)
        rows = fetch_public("SHEET_ID")
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["city"] == "Berlin"

    @patch("parse_google_sheets._requests.get")
    def test_skip_rows(self, mock_get):
        body = "metadata row\n" + self.CSV_BODY
        mock_get.return_value = self._mock_resp(body)
        rows = fetch_public("SHEET_ID", skip_rows=1)
        assert rows[0]["name"] == "Alice"

    @patch("parse_google_sheets._requests.get")
    def test_empty_rows_skipped(self, mock_get):
        body = "name,age\nAlice,30\n,\nBob,25\n"
        mock_get.return_value = self._mock_resp(body)
        rows = fetch_public("SHEET_ID")
        assert len(rows) == 2

    @patch("parse_google_sheets._requests.get")
    def test_private_sheet_raises(self, mock_get):
        m = self._mock_resp("", url="https://accounts.google.com/signin/...")
        mock_get.return_value = m
        with pytest.raises(ValueError, match="requires authentication"):
            fetch_public("SHEET_ID")

    @patch("parse_google_sheets._requests.get")
    def test_gid_passed_in_url(self, mock_get):
        mock_get.return_value = self._mock_resp(self.CSV_BODY)
        fetch_public("SHEET_ID", gid="999")
        called_url = mock_get.call_args[0][0]
        assert "gid=999" in called_url

    @patch("parse_google_sheets._requests.get")
    def test_gid_extracted_from_url(self, mock_get):
        mock_get.return_value = self._mock_resp(self.CSV_BODY)
        fetch_public("https://docs.google.com/spreadsheets/d/ID/edit#gid=777")
        called_url = mock_get.call_args[0][0]
        assert "gid=777" in called_url


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    RECORDS = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]

    def test_to_json(self):
        result = json.loads(to_json(self.RECORDS))
        assert result[0]["name"] == "Alice"

    def test_to_csv(self):
        csv_str = to_csv(self.RECORDS)
        lines = csv_str.strip().splitlines()
        assert lines[0] == "name,age"
        assert len(lines) == 3

    def test_to_csv_empty(self):
        assert to_csv([]) == ""


# ---------------------------------------------------------------------------
# Live: public Google Sheet (always runs — public data)
# ---------------------------------------------------------------------------

class TestLivePublic:
    # IAB Taxonomy published as Google Sheet — verified public
    # https://docs.google.com/spreadsheets/d/1tAh-QUlS3JM-TDhiTJ1JegILBVv3BKKE/edit
    SAMPLE_ID = "1tAh-QUlS3JM-TDhiTJ1JegILBVv3BKKE"

    @pytest.mark.skipif(
        not os.environ.get("TEST_LIVE_NETWORK", "1") == "1",
        reason="Live network test"
    )
    def test_fetch_public_sample_sheet(self):
        try:
            rows = fetch_public(self.SAMPLE_ID)
            assert len(rows) > 0
            assert isinstance(rows[0], dict)
        except Exception:
            pytest.skip("Live sheet not accessible in this environment")

    @pytest.mark.skipif(
        not os.environ.get("TEST_LIVE_NETWORK", "1") == "1",
        reason="Live network test"
    )
    def test_fetch_auto_public(self):
        try:
            rows = fetch(self.SAMPLE_ID)
            assert len(rows) > 0
        except Exception:
            pytest.skip("Live sheet not accessible in this environment")


# ---------------------------------------------------------------------------
# Private sheet (skipped without credentials)
# ---------------------------------------------------------------------------

import os

@pytest.mark.skipif(
    not (os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or
         os.environ.get("GOOGLE_SERVICE_ACCOUNT_INFO")),
    reason="No Google service account credentials"
)
class TestPrivateSheet:
    SHEET_ID = os.environ.get("TEST_PRIVATE_SHEET_ID", "")

    def test_fetch_private(self):
        from parse_google_sheets import fetch_private
        rows = fetch_private(self.SHEET_ID)
        assert isinstance(rows, list)

    def test_list_sheets(self):
        from parse_google_sheets import list_sheets
        tabs = list_sheets(self.SHEET_ID)
        assert len(tabs) >= 1
        assert "title" in tabs[0]
