"""
test_parse_airtable.py

Run with:
    pytest test_parse_airtable.py -v

Unit tests use pyairtable's built-in FakeAirtable testing mock — no real token needed.
Live tests require AIRTABLE_TOKEN + TEST_AIRTABLE_BASE_ID + TEST_AIRTABLE_TABLE env vars.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from parse_airtable import (
    AirtableRecord,
    AirtableSchema,
    to_csv,
    to_flat_records,
    to_json,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

RAW_RECORD = {
    "id": "recABC123",
    "createdTime": "2024-01-15T10:00:00.000Z",
    "fields": {
        "Name": "Alice",
        "Age": 30,
        "Tags": ["python", "ai"],
        "Active": True,
        "Notes": None,
    },
}

RAW_RECORD_2 = {
    "id": "recDEF456",
    "createdTime": "2024-02-01T09:00:00.000Z",
    "fields": {
        "Name": "Bob",
        "Age": 25,
        "Tags": ["data"],
        "Active": False,
        "Score": 99.5,
    },
}


# ---------------------------------------------------------------------------
# AirtableRecord
# ---------------------------------------------------------------------------

class TestAirtableRecord:
    def test_from_raw(self):
        r = AirtableRecord.from_raw(RAW_RECORD)
        assert r.id == "recABC123"
        assert r.created_time == "2024-01-15T10:00:00.000Z"
        assert r.fields["Name"] == "Alice"

    def test_flat_includes_id_and_created(self):
        r = AirtableRecord.from_raw(RAW_RECORD)
        flat = r.flat()
        assert flat["_id"] == "recABC123"
        assert flat["_created"] == "2024-01-15T10:00:00.000Z"
        assert flat["Name"] == "Alice"

    def test_flat_includes_all_fields(self):
        r = AirtableRecord.from_raw(RAW_RECORD)
        flat = r.flat()
        assert "Age" in flat
        assert "Tags" in flat
        assert "Active" in flat

    def test_missing_fields_defaults(self):
        r = AirtableRecord.from_raw({})
        assert r.id == ""
        assert r.fields == {}

    def test_none_field_value(self):
        r = AirtableRecord.from_raw(RAW_RECORD)
        assert r.fields["Notes"] is None


# ---------------------------------------------------------------------------
# to_flat_records
# ---------------------------------------------------------------------------

class TestToFlatRecords:
    def test_basic(self):
        records = [AirtableRecord.from_raw(RAW_RECORD),
                   AirtableRecord.from_raw(RAW_RECORD_2)]
        flat = to_flat_records(records)
        assert len(flat) == 2
        assert flat[0]["Name"] == "Alice"
        assert flat[1]["Name"] == "Bob"

    def test_empty(self):
        assert to_flat_records([]) == []


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------

class TestToJson:
    def test_list_of_records(self):
        records = [AirtableRecord.from_raw(RAW_RECORD)]
        result = json.loads(to_json(records))
        assert result[0]["Name"] == "Alice"
        assert result[0]["_id"] == "recABC123"

    def test_tags_list_preserved(self):
        records = [AirtableRecord.from_raw(RAW_RECORD)]
        result = json.loads(to_json(records))
        assert result[0]["Tags"] == ["python", "ai"]

    def test_dict_input(self):
        result = json.loads(to_json({"key": "value"}))
        assert result["key"] == "value"

    def test_empty(self):
        result = json.loads(to_json([]))
        assert result == []


# ---------------------------------------------------------------------------
# to_csv
# ---------------------------------------------------------------------------

class TestToCsv:
    def test_basic(self):
        records = [AirtableRecord.from_raw(RAW_RECORD),
                   AirtableRecord.from_raw(RAW_RECORD_2)]
        csv_str = to_csv(records)
        lines = csv_str.strip().splitlines()
        assert lines[0].startswith("_id,_created")
        assert len(lines) == 3

    def test_lists_stringified(self):
        records = [AirtableRecord.from_raw(RAW_RECORD)]
        csv_str = to_csv(records)
        assert "python" in csv_str  # JSON-serialised list

    def test_none_becomes_empty(self):
        import csv as _csv
        records = [AirtableRecord.from_raw(RAW_RECORD)]
        csv_str = to_csv(records)
        reader = _csv.DictReader(csv_str.splitlines())
        row = next(reader)
        assert row["Notes"] == ""

    def test_union_of_fields_across_records(self):
        # RAW_RECORD has Notes, RAW_RECORD_2 has Score — both should appear
        records = [AirtableRecord.from_raw(RAW_RECORD),
                   AirtableRecord.from_raw(RAW_RECORD_2)]
        csv_str = to_csv(records)
        assert "Notes" in csv_str
        assert "Score" in csv_str

    def test_empty(self):
        assert to_csv([]) == ""


# ---------------------------------------------------------------------------
# AirtableSchema
# ---------------------------------------------------------------------------

class TestAirtableSchema:
    def _schema(self):
        return AirtableSchema(
            base_id="appXXX",
            tables=[
                {"id": "tbl1", "name": "Contacts",
                 "fields": [{"id": "fld1", "name": "Name", "type": "singleLineText"},
                             {"id": "fld2", "name": "Email", "type": "email"}],
                 "views": []},
                {"id": "tbl2", "name": "Tasks",
                 "fields": [{"id": "fld3", "name": "Title", "type": "singleLineText"}],
                 "views": []},
            ]
        )

    def test_table_names(self):
        s = self._schema()
        assert s.table_names() == ["Contacts", "Tasks"]

    def test_fields_for_by_name(self):
        s = self._schema()
        fields = s.fields_for("Contacts")
        assert len(fields) == 2
        assert fields[0]["name"] == "Name"

    def test_fields_for_missing(self):
        s = self._schema()
        assert s.fields_for("Nonexistent") == []


# ---------------------------------------------------------------------------
# fetch_all — mocked
# ---------------------------------------------------------------------------

class TestFetchAllMocked:
    def _mock_table(self, records):
        mock = MagicMock()
        mock.all.return_value = records
        return mock

    @patch("parse_airtable._table")
    def test_returns_records(self, mock_table_fn):
        mock_table_fn.return_value = self._mock_table([RAW_RECORD, RAW_RECORD_2])
        from parse_airtable import fetch_all
        records = fetch_all("appXXX", "Contacts")
        assert len(records) == 2
        assert records[0].id == "recABC123"

    @patch("parse_airtable._table")
    def test_formula_passed(self, mock_table_fn):
        mock_tbl = self._mock_table([])
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import fetch_all
        fetch_all("appXXX", "Contacts", formula="{Active}=1")
        mock_tbl.all.assert_called_once_with(formula="{Active}=1")

    @patch("parse_airtable._table")
    def test_fields_passed(self, mock_table_fn):
        mock_tbl = self._mock_table([])
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import fetch_all
        fetch_all("appXXX", "Contacts", fields=["Name", "Email"])
        call_kwargs = mock_tbl.all.call_args[1]
        assert call_kwargs["fields"] == ["Name", "Email"]

    @patch("parse_airtable._table")
    def test_empty_result(self, mock_table_fn):
        mock_table_fn.return_value = self._mock_table([])
        from parse_airtable import fetch_all
        assert fetch_all("appXXX", "Contacts") == []


# ---------------------------------------------------------------------------
# search — mocked
# ---------------------------------------------------------------------------

class TestSearchMocked:
    @patch("parse_airtable._table")
    def test_search(self, mock_table_fn):
        mock_tbl = MagicMock()
        mock_tbl.search.return_value = [RAW_RECORD]
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import search
        results = search("appXXX", "Contacts", "Name", "Alice")
        assert len(results) == 1
        assert results[0].fields["Name"] == "Alice"
        mock_tbl.search.assert_called_once_with("Name", "Alice")


# ---------------------------------------------------------------------------
# create / update / delete — mocked
# ---------------------------------------------------------------------------

class TestWritesMocked:
    @patch("parse_airtable._table")
    def test_create_single(self, mock_table_fn):
        mock_tbl = MagicMock()
        mock_tbl.batch_create.return_value = [RAW_RECORD]
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import create
        results = create("appXXX", "Contacts", {"Name": "Alice"})
        assert results[0].id == "recABC123"

    @patch("parse_airtable._table")
    def test_create_batch(self, mock_table_fn):
        mock_tbl = MagicMock()
        mock_tbl.batch_create.return_value = [RAW_RECORD, RAW_RECORD_2]
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import create
        results = create("appXXX", "Contacts", [{"Name": "Alice"}, {"Name": "Bob"}])
        assert len(results) == 2

    @patch("parse_airtable._table")
    def test_update(self, mock_table_fn):
        updated = {**RAW_RECORD, "fields": {**RAW_RECORD["fields"], "Name": "Alice Updated"}}
        mock_tbl = MagicMock()
        mock_tbl.update.return_value = updated
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import update
        result = update("appXXX", "Contacts", "recABC123", {"Name": "Alice Updated"})
        assert result.fields["Name"] == "Alice Updated"

    @patch("parse_airtable._table")
    def test_delete(self, mock_table_fn):
        mock_tbl = MagicMock()
        mock_tbl.batch_delete.return_value = ["recABC123"]
        mock_table_fn.return_value = mock_tbl
        from parse_airtable import delete
        deleted = delete("appXXX", "Contacts", "recABC123")
        assert "recABC123" in deleted


# ---------------------------------------------------------------------------
# missing token
# ---------------------------------------------------------------------------

class TestMissingToken:
    def test_raises_without_token(self, monkeypatch):
        monkeypatch.delenv("AIRTABLE_TOKEN", raising=False)
        from parse_airtable import _token
        with pytest.raises(EnvironmentError, match="AIRTABLE_TOKEN"):
            _token()


# ---------------------------------------------------------------------------
# Live tests (skipped without credentials)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not os.environ.get("AIRTABLE_TOKEN"),
    reason="AIRTABLE_TOKEN not set"
)
class TestLive:
    BASE_ID = os.environ.get("TEST_AIRTABLE_BASE_ID", "")
    TABLE = os.environ.get("TEST_AIRTABLE_TABLE", "")

    def test_fetch_schema(self):
        from parse_airtable import fetch_schema
        schema = fetch_schema(self.BASE_ID)
        assert len(schema.tables) > 0

    def test_fetch_all(self):
        from parse_airtable import fetch_all
        records = fetch_all(self.BASE_ID, self.TABLE)
        assert isinstance(records, list)

    def test_to_csv_roundtrip(self):
        from parse_airtable import fetch_all
        records = fetch_all(self.BASE_ID, self.TABLE)
        csv_str = to_csv(records)
        assert isinstance(csv_str, str)
