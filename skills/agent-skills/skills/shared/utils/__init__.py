"""Shared utilities for agent skills."""

import os
import json
from datetime import datetime


def get_env(key: str, default: str = "") -> str:
    """Get environment variable with fallback."""
    return os.environ.get(key, default)


def format_results_as_markdown_table(headers: list, rows: list) -> str:
    """Format data as a markdown table."""
    header = " | ".join(headers)
    separator = " | ".join("---" for _ in headers)
    body = "\n".join(" | ".join(str(val) for val in row) for row in rows)
    return f"{header}\n{separator}\n{body}"


def timestamp() -> str:
    """Return ISO timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def safe_json_loads(text: str, default=None):
    """Parse JSON with fallback."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default
