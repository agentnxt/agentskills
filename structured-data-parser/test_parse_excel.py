"""
test_parse_excel.py

Run with:
    pytest test_parse_excel.py -v

All tests use synthetic in-memory workbooks — no real Excel file needed.
"""

import io
import json
from pathlib import Path

import pytest
import openpyxl

from parse_excel import (
    SheetInfo,
    list_sheets,
    parse,
    parse_all_sheets,
    to_csv,
    to_json,
    _coerce,
)


# ---------------------------------------------------------------------------
# Helpers — build synthetic xlsx in memory
# ---------------------------------------------------------------------------

def _make_xlsx(sheets: dict[str, list[list]], tmp_path: Path) -> Path:
    """
    Build a .xlsx file from a dict of {sheet_name: [[row], [row], ...]}.
    Returns the file path.
    """
    wb = openpyxl.Workbook()
    first = True
    for name, rows in sheets.items():
        ws = wb.active if first else wb.create_sheet(name)
        if first:
            ws.title = name
            first = False
        for row in rows:
            ws.append(row)
    path = tmp_path / "test.xlsx"
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# _coerce
# ---------------------------------------------------------------------------

class TestCoerce:
    def test_none_to_empty(self):
        assert _coerce(None) == ""

    def test_int_float(self):
        assert _coerce(1.0) == 1
        assert _coerce(1.5) == 1.5

    def test_bool(self):
        assert _coerce(True) is True
        assert _coerce(False) is False

    def test_string_stripped(self):
        assert _coerce("  hello  ") == "hello"

    def test_datetime_isoformat(self):
        from datetime import datetime
        dt = datetime(2024, 1, 15, 10, 30)
        result = _coerce(dt)
        assert "2024-01-15" in result


# ---------------------------------------------------------------------------
# list_sheets
# ---------------------------------------------------------------------------

class TestListSheets:
    def test_single_sheet(self, tmp_path):
        p = _make_xlsx({"Sheet1": [["a", "b"], [1, 2]]}, tmp_path)
        sheets = list_sheets(p)
        assert len(sheets) == 1
        assert sheets[0].name == "Sheet1"
        assert isinstance(sheets[0], SheetInfo)

    def test_multiple_sheets(self, tmp_path):
        p = _make_xlsx({
            "Alpha": [["x"], [1]],
            "Beta":  [["y"], [2]],
            "Gamma": [["z"], [3]],
        }, tmp_path)
        sheets = list_sheets(p)
        assert len(sheets) == 3
        names = [s.name for s in sheets]
        assert "Alpha" in names and "Beta" in names

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            list_sheets("/no/such/file.xlsx")


# ---------------------------------------------------------------------------
# parse — single sheet
# ---------------------------------------------------------------------------

class TestParse:
    def test_basic(self, tmp_path):
        p = _make_xlsx({"Data": [
            ["name", "age", "city"],
            ["Alice", 30, "London"],
            ["Bob", 25, "Berlin"],
        ]}, tmp_path)
        rows = parse(p)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["city"] == "Berlin"

    def test_by_sheet_name(self, tmp_path):
        p = _make_xlsx({
            "Sheet1": [["a"], [1]],
            "Revenue": [["amount", "month"], [1000, "Jan"], [2000, "Feb"]],
        }, tmp_path)
        rows = parse(p, sheet="Revenue")
        assert len(rows) == 2
        assert rows[0]["amount"] == 1000

    def test_by_sheet_index(self, tmp_path):
        p = _make_xlsx({
            "First": [["x"], [1]],
            "Second": [["y"], [2]],
        }, tmp_path)
        rows = parse(p, sheet=1)
        assert rows[0]["y"] == 2

    def test_skip_rows(self, tmp_path):
        p = _make_xlsx({"Sheet1": [
            ["Report: Q1 2024"],
            ["Generated: 2024-01-01"],
            ["name", "value"],
            ["Alpha", 100],
        ]}, tmp_path)
        rows = parse(p, skip_rows=2)
        assert len(rows) == 1
        assert rows[0]["name"] == "Alpha"

    def test_empty_rows_skipped(self, tmp_path):
        p = _make_xlsx({"Sheet1": [
            ["name", "value"],
            ["Alpha", 100],
            [None, None],
            ["Beta", 200],
        ]}, tmp_path)
        rows = parse(p)
        assert len(rows) == 2

    def test_sheet_not_found_raises(self, tmp_path):
        p = _make_xlsx({"Sheet1": [["a"], [1]]}, tmp_path)
        with pytest.raises(ValueError, match="not found"):
            parse(p, sheet="NonExistent")

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse("/no/such/file.xlsx")

    def test_numeric_types_preserved(self, tmp_path):
        p = _make_xlsx({"Sheet1": [
            ["int_col", "float_col", "bool_col"],
            [42, 3.14, True],
        ]}, tmp_path)
        rows = parse(p)
        assert rows[0]["int_col"] == 42
        assert rows[0]["float_col"] == 3.14
        assert rows[0]["bool_col"] is True

    def test_missing_column_values_empty_string(self, tmp_path):
        p = _make_xlsx({"Sheet1": [
            ["a", "b", "c"],
            [1, 2],        # row shorter than header
            [3, 4, 5],
        ]}, tmp_path)
        rows = parse(p)
        assert rows[0]["c"] == ""

    def test_unnamed_columns_get_col_n(self, tmp_path):
        p = _make_xlsx({"Sheet1": [
            ["name", None, "value"],
            ["Alice", "x", 100],
        ]}, tmp_path)
        rows = parse(p)
        assert "col_1" in rows[0]


# ---------------------------------------------------------------------------
# parse_all_sheets
# ---------------------------------------------------------------------------

class TestParseAllSheets:
    def test_all_sheets_returned(self, tmp_path):
        p = _make_xlsx({
            "Alpha": [["x", "y"], [1, 2]],
            "Beta":  [["a", "b"], [3, 4]],
        }, tmp_path)
        result = parse_all_sheets(p)
        assert set(result.keys()) == {"Alpha", "Beta"}
        assert result["Alpha"][0]["x"] == 1
        assert result["Beta"][0]["a"] == 3

    def test_skip_rows_applied_to_all(self, tmp_path):
        p = _make_xlsx({
            "Sheet1": [["meta"], ["col1", "col2"], ["val1", "val2"]],
            "Sheet2": [["meta"], ["colA", "colB"], ["valA", "valB"]],
        }, tmp_path)
        result = parse_all_sheets(p, skip_rows=1)
        assert result["Sheet1"][0]["col1"] == "val1"
        assert result["Sheet2"][0]["colA"] == "valA"


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    RECORDS = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

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

    def test_to_json_multi_sheet(self):
        data = {"Sheet1": self.RECORDS, "Sheet2": [{"x": 1}]}
        result = json.loads(to_json(data))
        assert "Sheet1" in result
        assert result["Sheet2"][0]["x"] == 1
