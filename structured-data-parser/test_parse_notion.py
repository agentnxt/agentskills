"""
test_parse_notion.py

Run with:
    pytest test_parse_notion.py -v

Unit tests use inline fixture dicts — no token needed.
Live tests require NOTION_TOKEN + TEST_NOTION_DATABASE_ID env vars.
"""

import json
import os
from unittest.mock import MagicMock, patch, call

import pytest

from parse_notion import (
    NotionPage,
    NotionBlock,
    NotionDatabase,
    _extract_property,
    _extract_rich_text,
    to_csv,
    to_flat_records,
    to_json,
    blocks_to_markdown,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _rt(text: str) -> list:
    """Build a minimal rich_text list."""
    return [{"plain_text": text, "text": {"content": text}}]


RAW_PAGE = {
    "id": "page-id-001",
    "object": "page",
    "url": "https://notion.so/page-id-001",
    "created_time": "2024-01-15T10:00:00.000Z",
    "last_edited_time": "2024-03-01T12:00:00.000Z",
    "archived": False,
    "parent": {"type": "database_id", "database_id": "db-id-001"},
    "properties": {
        "Name":        {"type": "title",       "title": _rt("Alice")},
        "Notes":       {"type": "rich_text",   "rich_text": _rt("Some notes")},
        "Age":         {"type": "number",      "number": 30},
        "Status":      {"type": "select",      "select": {"name": "Active"}},
        "Tags":        {"type": "multi_select","multi_select": [{"name": "ai"}, {"name": "python"}]},
        "Done":        {"type": "checkbox",    "checkbox": True},
        "Due":         {"type": "date",        "date": {"start": "2024-06-01", "end": None}},
        "URL":         {"type": "url",         "url": "https://example.com"},
        "Email":       {"type": "email",       "email": "alice@example.com"},
        "Phone":       {"type": "phone_number","phone_number": "+44 7700 900123"},
        "UID":         {"type": "unique_id",   "unique_id": {"prefix": "TASK", "number": 42}},
        "Created":     {"type": "created_time","created_time": "2024-01-15T10:00:00.000Z"},
        "Edited":      {"type": "last_edited_time","last_edited_time": "2024-03-01T12:00:00.000Z"},
        "Empty":       {"type": "select",      "select": None},
        "EmptyText":   {"type": "rich_text",   "rich_text": []},
        "People":      {"type": "people",      "people": [{"name": "Bob"}, {"name": "Carol"}]},
        "Relations":   {"type": "relation",    "relation": [{"id": "rel-1"}, {"id": "rel-2"}]},
        "Files":       {"type": "files",       "files": [
            {"type": "external", "external": {"url": "https://example.com/file.pdf"}}
        ]},
    },
}

RAW_PAGE_2 = {
    "id": "page-id-002",
    "object": "page",
    "url": "https://notion.so/page-id-002",
    "created_time": "2024-02-01T00:00:00.000Z",
    "last_edited_time": "2024-02-01T00:00:00.000Z",
    "archived": False,
    "parent": {"type": "database_id", "database_id": "db-id-001"},
    "properties": {
        "Name":   {"type": "title",  "title": _rt("Bob")},
        "Score":  {"type": "number", "number": 99.5},
    },
}

RAW_DATABASE = {
    "id": "db-id-001",
    "object": "database",
    "url": "https://notion.so/db-id-001",
    "title": _rt("My Database"),
    "properties": {
        "Name":   {"id": "fld1", "type": "title"},
        "Status": {"id": "fld2", "type": "select"},
        "Score":  {"id": "fld3", "type": "number"},
    },
}

RAW_BLOCK_PARA = {
    "id": "blk-001",
    "type": "paragraph",
    "paragraph": {"rich_text": _rt("Hello world")},
    "has_children": False,
}

RAW_BLOCK_H1 = {
    "id": "blk-002",
    "type": "heading_1",
    "heading_1": {"rich_text": _rt("Introduction")},
    "has_children": False,
}

RAW_BLOCK_BULLET = {
    "id": "blk-003",
    "type": "bulleted_list_item",
    "bulleted_list_item": {"rich_text": _rt("Item one")},
    "has_children": False,
}

RAW_BLOCK_CODE = {
    "id": "blk-004",
    "type": "code",
    "code": {"rich_text": _rt("print('hello')")},
    "has_children": False,
}


# ---------------------------------------------------------------------------
# _extract_rich_text
# ---------------------------------------------------------------------------

class TestExtractRichText:
    def test_single(self):
        assert _extract_rich_text(_rt("hello")) == "hello"

    def test_multiple(self):
        rt = [{"plain_text": "Hello "}, {"plain_text": "world"}]
        assert _extract_rich_text(rt) == "Hello world"

    def test_empty(self):
        assert _extract_rich_text([]) == ""

    def test_none(self):
        assert _extract_rich_text(None) == ""


# ---------------------------------------------------------------------------
# _extract_property
# ---------------------------------------------------------------------------

class TestExtractProperty:
    def test_title(self):
        assert _extract_property({"type": "title", "title": _rt("Alice")}) == "Alice"

    def test_rich_text(self):
        assert _extract_property({"type": "rich_text", "rich_text": _rt("note")}) == "note"

    def test_number(self):
        assert _extract_property({"type": "number", "number": 42}) == 42

    def test_number_float(self):
        assert _extract_property({"type": "number", "number": 3.14}) == 3.14

    def test_select(self):
        assert _extract_property({"type": "select", "select": {"name": "Active"}}) == "Active"

    def test_select_none(self):
        assert _extract_property({"type": "select", "select": None}) is None

    def test_multi_select(self):
        val = _extract_property({"type": "multi_select",
                                  "multi_select": [{"name": "a"}, {"name": "b"}]})
        assert val == ["a", "b"]

    def test_status(self):
        assert _extract_property({"type": "status", "status": {"name": "Done"}}) == "Done"

    def test_checkbox_true(self):
        assert _extract_property({"type": "checkbox", "checkbox": True}) is True

    def test_date_start_only(self):
        val = _extract_property({"type": "date", "date": {"start": "2024-01-01", "end": None}})
        assert val == "2024-01-01"

    def test_date_range(self):
        val = _extract_property({"type": "date", "date": {"start": "2024-01-01", "end": "2024-01-31"}})
        assert "→" in val

    def test_date_none(self):
        assert _extract_property({"type": "date", "date": None}) is None

    def test_url(self):
        assert _extract_property({"type": "url", "url": "https://x.com"}) == "https://x.com"

    def test_email(self):
        assert _extract_property({"type": "email", "email": "a@b.com"}) == "a@b.com"

    def test_phone(self):
        assert _extract_property({"type": "phone_number", "phone_number": "+1234"}) == "+1234"

    def test_people(self):
        val = _extract_property({"type": "people", "people": [{"name": "Bob"}]})
        assert val == ["Bob"]

    def test_relation(self):
        val = _extract_property({"type": "relation", "relation": [{"id": "abc"}, {"id": "def"}]})
        assert val == ["abc", "def"]

    def test_unique_id_with_prefix(self):
        val = _extract_property({"type": "unique_id", "unique_id": {"prefix": "TASK", "number": 7}})
        assert val == "TASK7"

    def test_unique_id_no_prefix(self):
        val = _extract_property({"type": "unique_id", "unique_id": {"prefix": None, "number": 3}})
        assert val == "3"

    def test_files_external(self):
        val = _extract_property({"type": "files", "files": [
            {"type": "external", "external": {"url": "https://x.com/f.pdf"}}
        ]})
        assert val == ["https://x.com/f.pdf"]

    def test_created_time(self):
        val = _extract_property({"type": "created_time", "created_time": "2024-01-01T00:00:00Z"})
        assert val == "2024-01-01T00:00:00Z"

    def test_unknown_type(self):
        assert _extract_property({"type": "button"}) is None


# ---------------------------------------------------------------------------
# NotionPage
# ---------------------------------------------------------------------------

class TestNotionPage:
    def _page(self):
        return NotionPage.from_raw(RAW_PAGE)

    def test_id(self):
        assert self._page().id == "page-id-001"

    def test_properties_extracted(self):
        p = self._page()
        assert p.properties["Name"] == "Alice"
        assert p.properties["Age"] == 30
        assert p.properties["Done"] is True
        assert p.properties["Tags"] == ["ai", "python"]
        assert p.properties["UID"] == "TASK42"

    def test_empty_select_is_none(self):
        assert self._page().properties["Empty"] is None

    def test_empty_rich_text_is_empty_string(self):
        assert self._page().properties["EmptyText"] == ""

    def test_flat_has_meta_prefix(self):
        flat = self._page().flat()
        assert "_id" in flat
        assert "_url" in flat
        assert "_created" in flat

    def test_flat_includes_properties(self):
        flat = self._page().flat()
        assert flat["Name"] == "Alice"
        assert flat["Age"] == 30

    def test_parent_type(self):
        assert self._page().parent_type == "database_id"

    def test_archived_false(self):
        assert self._page().archived is False


# ---------------------------------------------------------------------------
# NotionDatabase
# ---------------------------------------------------------------------------

class TestNotionDatabase:
    def test_title(self):
        db = NotionDatabase.from_raw(RAW_DATABASE)
        assert db.title == "My Database"

    def test_properties(self):
        db = NotionDatabase.from_raw(RAW_DATABASE)
        assert "Name" in db.properties
        assert db.properties["Status"]["type"] == "select"


# ---------------------------------------------------------------------------
# NotionBlock
# ---------------------------------------------------------------------------

class TestNotionBlock:
    def test_paragraph(self):
        b = NotionBlock.from_raw(RAW_BLOCK_PARA)
        assert b.type == "paragraph"
        assert b.text == "Hello world"

    def test_heading_markdown(self):
        b = NotionBlock.from_raw(RAW_BLOCK_H1)
        assert b.to_markdown().startswith("# Introduction")

    def test_bullet_markdown(self):
        b = NotionBlock.from_raw(RAW_BLOCK_BULLET)
        assert b.to_markdown().startswith("- Item one")

    def test_code_markdown(self):
        b = NotionBlock.from_raw(RAW_BLOCK_CODE)
        md = b.to_markdown()
        assert "```" in md
        assert "print" in md

    def test_nested_markdown_indented(self):
        parent = NotionBlock.from_raw(RAW_BLOCK_PARA)
        child = NotionBlock.from_raw(RAW_BLOCK_BULLET)
        parent.children = [child]
        md = parent.to_markdown()
        assert "  -" in md  # child indented


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def _pages(self):
        return [NotionPage.from_raw(RAW_PAGE), NotionPage.from_raw(RAW_PAGE_2)]

    def test_to_flat_records(self):
        flat = to_flat_records(self._pages())
        assert len(flat) == 2
        assert flat[0]["Name"] == "Alice"
        assert flat[1]["Name"] == "Bob"

    def test_to_json(self):
        result = json.loads(to_json(self._pages()))
        assert result[0]["Name"] == "Alice"
        assert result[0]["_id"] == "page-id-001"

    def test_to_csv_basic(self):
        csv_str = to_csv(self._pages())
        lines = csv_str.strip().splitlines()
        assert lines[0].startswith("_id")
        assert len(lines) == 3

    def test_to_csv_lists_pipe_joined(self):
        csv_str = to_csv([NotionPage.from_raw(RAW_PAGE)])
        assert "ai | python" in csv_str

    def test_to_csv_none_empty(self):
        import csv as _csv
        pages = [NotionPage.from_raw(RAW_PAGE)]
        reader = _csv.DictReader(to_csv(pages).splitlines())
        row = next(reader)
        assert row["Empty"] == ""

    def test_to_csv_union_of_fields(self):
        # RAW_PAGE has many fields, RAW_PAGE_2 has Score not in RAW_PAGE
        csv_str = to_csv(self._pages())
        assert "Score" in csv_str
        assert "Name" in csv_str

    def test_to_csv_empty(self):
        assert to_csv([]) == ""

    def test_blocks_to_markdown(self):
        blocks = [NotionBlock.from_raw(b) for b in [RAW_BLOCK_H1, RAW_BLOCK_PARA]]
        md = blocks_to_markdown(blocks)
        assert "# Introduction" in md
        assert "Hello world" in md


# ---------------------------------------------------------------------------
# query_database — mocked
# ---------------------------------------------------------------------------

class TestQueryDatabaseMocked:
    @patch("parse_notion._client")
    def test_returns_pages(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.request.return_value = {
            "results": [RAW_PAGE, RAW_PAGE_2],
            "has_more": False,
        }
        mock_client_fn.return_value = mock_client
        from parse_notion import query_database
        pages = query_database("db-id-001")
        assert len(pages) == 2
        assert pages[0].properties["Name"] == "Alice"

    @patch("parse_notion._client")
    def test_pagination(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.request.side_effect = [
            {"results": [RAW_PAGE], "has_more": True, "next_cursor": "cur1"},
            {"results": [RAW_PAGE_2], "has_more": False},
        ]
        mock_client_fn.return_value = mock_client
        from parse_notion import query_database
        pages = query_database("db-id-001")
        assert len(pages) == 2

    @patch("parse_notion._client")
    def test_filter_passed(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.request.return_value = {"results": [], "has_more": False}
        mock_client_fn.return_value = mock_client
        from parse_notion import query_database
        filt = {"property": "Status", "select": {"equals": "Active"}}
        query_database("db-id-001", filter=filt)
        call_body = mock_client.request.call_args[1]["body"]
        assert call_body["filter"] == filt


# ---------------------------------------------------------------------------
# missing token
# ---------------------------------------------------------------------------

class TestMissingToken:
    def test_raises(self, monkeypatch):
        monkeypatch.delenv("NOTION_TOKEN", raising=False)
        from parse_notion import _token
        with pytest.raises(EnvironmentError, match="NOTION_TOKEN"):
            _token()


# ---------------------------------------------------------------------------
# Live tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not os.environ.get("NOTION_TOKEN"),
    reason="NOTION_TOKEN not set"
)
class TestLive:
    DB_ID = os.environ.get("TEST_NOTION_DATABASE_ID", "")

    def test_fetch_schema(self):
        from parse_notion import fetch_database_schema
        db = fetch_database_schema(self.DB_ID)
        assert db.id
        assert len(db.properties) > 0

    def test_query_database(self):
        from parse_notion import query_database
        pages = query_database(self.DB_ID)
        assert isinstance(pages, list)

    def test_csv_roundtrip(self):
        from parse_notion import query_database
        pages = query_database(self.DB_ID)
        csv_str = to_csv(pages)
        assert isinstance(csv_str, str)
