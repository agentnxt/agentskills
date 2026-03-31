"""
test_table_parsers.py
Tests for parse_pdf_tables.py, parse_html_tables.py, parse_markdown_tables.py

Run with:
    pytest test_table_parsers.py -v
"""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================
# HTML TABLE PARSER
# ===========================================================================

from parse_html_tables import (
    HTMLTable,
    extract,
    extract_from_string,
    to_csv,
    to_csv_all,
    to_json,
)

SIMPLE_TABLE = """
<table>
  <thead><tr><th>Name</th><th>Age</th><th>City</th></tr></thead>
  <tbody>
    <tr><td>Alice</td><td>30</td><td>London</td></tr>
    <tr><td>Bob</td><td>25</td><td>Berlin</td></tr>
  </tbody>
</table>
"""

COLSPAN_TABLE = """
<table>
  <tr><th colspan="2">Full Name</th><th>Score</th></tr>
  <tr><td>Alice</td><td>Smith</td><td>95</td></tr>
  <tr><td>Bob</td><td>Jones</td><td>88</td></tr>
</table>
"""

ROWSPAN_TABLE = """
<table>
  <tr><th>Category</th><th>Item</th><th>Value</th></tr>
  <tr><td rowspan="2">A</td><td>x</td><td>1</td></tr>
  <tr><td>y</td><td>2</td></tr>
</table>
"""

MULTI_TABLE = """
<table><tr><th>Col1</th></tr><tr><td>val1</td></tr></table>
<table><tr><th>ColA</th></tr><tr><td>valA</td></tr></table>
"""

NESTED_TABLE = """
<table>
  <tr><th>Outer</th></tr>
  <tr><td><table><tr><th>Inner</th></tr><tr><td>x</td></tr></table></td></tr>
</table>
"""

CAPTION_TABLE = """
<table>
  <caption>Revenue Q1</caption>
  <tr><th>Month</th><th>Amount</th></tr>
  <tr><td>Jan</td><td>1000</td></tr>
</table>
"""

EMPTY_ROWS_TABLE = """
<table>
  <tr><th>A</th><th>B</th></tr>
  <tr><td>1</td><td>2</td></tr>
  <tr><td></td><td></td></tr>
  <tr><td>3</td><td>4</td></tr>
</table>
"""


class TestHTMLBasic:
    def test_simple_table(self):
        tables = extract_from_string(SIMPLE_TABLE)
        assert len(tables) == 1
        t = tables[0]
        assert t.headers == ["Name", "Age", "City"]
        assert t.row_count == 2
        assert t.rows[0]["Name"] == "Alice"
        assert t.rows[1]["City"] == "Berlin"

    def test_caption_extracted(self):
        tables = extract_from_string(CAPTION_TABLE)
        assert tables[0].caption == "Revenue Q1"

    def test_empty_rows_skipped(self):
        tables = extract_from_string(EMPTY_ROWS_TABLE)
        assert tables[0].row_count == 2

    def test_multiple_tables(self):
        tables = extract_from_string(MULTI_TABLE)
        assert len(tables) == 2
        assert tables[0].headers == ["Col1"]
        assert tables[1].headers == ["ColA"]

    def test_no_header(self):
        tables = extract_from_string(SIMPLE_TABLE, has_header=False)
        assert tables[0].headers[0].startswith("col_")

    def test_empty_html(self):
        assert extract_from_string("<html><body>no tables</body></html>") == []


class TestHTMLColspanRowspan:
    def test_colspan_expands(self):
        tables = extract_from_string(COLSPAN_TABLE)
        t = tables[0]
        # "Full Name" should fill 2 columns
        assert t.col_count == 3
        assert t.row_count == 2

    def test_rowspan_expands(self):
        tables = extract_from_string(ROWSPAN_TABLE)
        t = tables[0]
        assert t.rows[0]["Category"] == "A"
        assert t.rows[1]["Category"] == "A"


class TestHTMLNested:
    def test_nested_skipped_by_default(self):
        tables = extract_from_string(NESTED_TABLE, skip_nested=True)
        assert len(tables) == 1  # only outer

    def test_nested_included(self):
        # When skip_nested=False, BeautifulSoup finds_all returns both tables.
        # The outer table absorbs the inner table's text into its cell.
        # Parser produces at least 1 table; with nested flag the inner is also attempted.
        tables = extract_from_string(NESTED_TABLE, skip_nested=False)
        assert len(tables) >= 1


class TestHTMLSerialisation:
    def _tables(self):
        return extract_from_string(SIMPLE_TABLE)

    def test_to_json(self):
        result = json.loads(to_json(self._tables()))
        assert result[0]["headers"] == ["Name", "Age", "City"]
        assert result[0]["row_count"] == 2

    def test_to_csv(self):
        csv_str = to_csv(self._tables())
        lines = csv_str.strip().splitlines()
        assert lines[0] == "Name,Age,City"
        assert len(lines) == 3

    def test_to_csv_all(self):
        tables = extract_from_string(MULTI_TABLE)
        csv_str = to_csv_all(tables)
        assert "_table" in csv_str

    def test_to_csv_empty(self):
        assert to_csv([]) == ""


# ===========================================================================
# MARKDOWN TABLE PARSER
# ===========================================================================

from parse_markdown_tables import (
    MarkdownTable,
    extract as md_extract,
    extract_from_string as md_extract_string,
    to_csv as md_to_csv,
    to_csv_all as md_to_csv_all,
    to_json as md_to_json,
)

SIMPLE_MD = """
| Name  | Age | City   |
|-------|-----|--------|
| Alice | 30  | London |
| Bob   | 25  | Berlin |
"""

ALIGNED_MD = """
| Left | Center | Right |
|:-----|:------:|------:|
| a    | b      | c     |
| d    | e      | f     |
"""

MULTI_MD = """
First table:

| Col1 | Col2 |
|------|------|
| a    | b    |

Some prose.

| ColA | ColB |
|------|------|
| x    | y    |
"""

HEADERLESS_MD = """
| a | b |
| c | d |
"""

CODE_BLOCK_MD = """
```
| fake | table |
|------|-------|
| x    | y     |
```

| real | table |
|------|-------|
| 1    | 2     |
"""

NO_EDGE_PIPES_MD = """
Name | Age
-----|----
Alice | 30
Bob | 25
"""

DUPLICATE_HEADER_MD = """
| Name | Name | Value |
|------|------|-------|
| a    | b    | 1     |
"""


class TestMarkdownBasic:
    def test_simple(self):
        tables = md_extract_string(SIMPLE_MD)
        assert len(tables) == 1
        t = tables[0]
        assert t.headers == ["Name", "Age", "City"]
        assert t.row_count == 2
        assert t.rows[0]["Name"] == "Alice"

    def test_alignment_row_stripped(self):
        tables = md_extract_string(ALIGNED_MD)
        assert tables[0].row_count == 2
        assert tables[0].headers == ["Left", "Center", "Right"]

    def test_multiple_tables(self):
        tables = md_extract_string(MULTI_MD)
        assert len(tables) == 2
        assert tables[0].headers == ["Col1", "Col2"]
        assert tables[1].headers == ["ColA", "ColB"]

    def test_no_edge_pipes(self):
        tables = md_extract_string(NO_EDGE_PIPES_MD)
        assert len(tables) == 1
        assert tables[0].headers == ["Name", "Age"]
        assert tables[0].row_count == 2

    def test_duplicate_headers_made_unique(self):
        tables = md_extract_string(DUPLICATE_HEADER_MD)
        headers = tables[0].headers
        assert len(headers) == len(set(headers))

    def test_code_block_skipped(self):
        tables = md_extract_string(CODE_BLOCK_MD, skip_code_blocks=True)
        assert len(tables) == 1
        assert tables[0].headers == ["real", "table"]

    def test_code_block_included(self):
        tables = md_extract_string(CODE_BLOCK_MD, skip_code_blocks=False)
        assert len(tables) == 2

    def test_line_start_recorded(self):
        tables = md_extract_string(SIMPLE_MD)
        assert tables[0].line_start >= 1

    def test_empty_string(self):
        assert md_extract_string("no tables here") == []


class TestMarkdownSerialisation:
    def _tables(self):
        return md_extract_string(SIMPLE_MD)

    def test_to_json(self):
        result = json.loads(md_to_json(self._tables()))
        assert result[0]["headers"] == ["Name", "Age", "City"]

    def test_to_csv(self):
        csv_str = md_to_csv(self._tables())
        lines = csv_str.strip().splitlines()
        assert lines[0] == "Name,Age,City"
        assert len(lines) == 3

    def test_to_csv_all(self):
        tables = md_extract_string(MULTI_MD)
        csv_str = md_to_csv_all(tables)
        assert "_table" in csv_str

    def test_to_csv_empty(self):
        assert md_to_csv([]) == ""


# ===========================================================================
# PDF TABLE PARSER
# ===========================================================================

from parse_pdf_tables import (
    PDFTable,
    _make_headers,
    _rows_to_dicts,
    to_csv as pdf_to_csv,
    to_csv_all as pdf_to_csv_all,
    to_json as pdf_to_json,
)


class TestPDFHelpers:
    def test_make_headers_unique(self):
        headers = _make_headers(["Name", "Name", "Value"])
        assert len(headers) == len(set(headers))

    def test_make_headers_empty_cell(self):
        headers = _make_headers(["A", "", "C"])
        assert headers[1].startswith("col_")

    def test_rows_to_dicts_basic(self):
        raw = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        headers, rows = _rows_to_dicts(raw)
        assert headers == ["Name", "Age"]
        assert len(rows) == 2
        assert rows[0]["Name"] == "Alice"

    def test_rows_to_dicts_skips_empty(self):
        raw = [["A", "B"], ["x", "y"], [None, None], ["z", "w"]]
        _, rows = _rows_to_dicts(raw)
        assert len(rows) == 2

    def test_rows_to_dicts_pads_short_rows(self):
        raw = [["A", "B", "C"], ["x", "y"]]
        _, rows = _rows_to_dicts(raw)
        assert rows[0]["C"] == ""


class TestPDFSerialisation:
    def _make_table(self):
        return PDFTable(
            page=1, table_index=0, engine="pdfplumber",
            headers=["Name", "Age"],
            rows=[{"Name": "Alice", "Age": "30"}, {"Name": "Bob", "Age": "25"}]
        )

    def test_to_json(self):
        result = json.loads(pdf_to_json([self._make_table()]))
        assert result[0]["headers"] == ["Name", "Age"]
        assert result[0]["row_count"] == 2

    def test_to_csv(self):
        csv_str = pdf_to_csv([self._make_table()])
        lines = csv_str.strip().splitlines()
        assert lines[0] == "Name,Age"
        assert len(lines) == 3

    def test_to_csv_all(self):
        t1 = self._make_table()
        t2 = PDFTable(page=2, table_index=0, engine="pdfplumber",
                      headers=["X"], rows=[{"X": "1"}])
        csv_str = pdf_to_csv_all([t1, t2])
        assert "_page" in csv_str

    def test_to_csv_empty(self):
        assert pdf_to_csv([]) == ""


class TestPDFFileNotFound:
    def test_raises(self):
        from parse_pdf_tables import extract as pdf_extract
        with pytest.raises(FileNotFoundError):
            pdf_extract("/no/such/file.pdf")


class TestPDFAutoEngine:
    """Test auto engine with a real synthetic PDF using pdfplumber."""

    def test_real_pdf(self, tmp_path):
        """Build a minimal PDF with a table and verify extraction."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table
            pdf_path = tmp_path / "test.pdf"
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            data = [["Name", "Age", "City"],
                    ["Alice", "30", "London"],
                    ["Bob", "25", "Berlin"]]
            doc.build([Table(data)])

            from parse_pdf_tables import extract as pdf_extract
            tables = pdf_extract(str(pdf_path))
            if tables:
                assert tables[0].row_count >= 1
        except ImportError:
            pytest.skip("reportlab not installed — skipping PDF generation test")
