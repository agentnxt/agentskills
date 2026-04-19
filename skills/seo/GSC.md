---
name: google-search-console
description: "Wrapper for Google Search Console API to fetch site performance data and per-page analytics."
---

The Google Search Console (GSC) integration enables programmatic access to site performance data via the official API. This wrapper allows listing sites and querying performance metrics by dimensions such as QUERY and PAGE.

Usage example:
```python
from tools.google_search_console_tool import GoogleSearchConsoleTool

gsc = GoogleSearchConsoleTool(site_url="https://example.com", credentials_path="/path/to/creds.json")
sites = gsc.list_sites()
report = gsc.query(
  start_date="2024-01-01",
  end_date="2024-01-31",
  dimensions=["QUERY", "PAGE"],
  row_limit=1000,
)
```
