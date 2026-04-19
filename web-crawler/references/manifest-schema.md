# Manifest Schema Reference

The crawler writes `manifest.json` to the root of the output directory on completion.

---

## Full Schema

```json
{
  "seed_url": "https://example.com",
  "started_at": "2026-03-29T10:00:00Z",
  "finished_at": "2026-03-29T10:45:12Z",

  "stats": {
    "pages_visited": 142,
    "files_downloaded": 891,
    "files_skipped": 12,
    "errors": 3,
    "embedded_videos": 8,
    "total_bytes_downloaded": 2471932928
  },

  "pages_visited": [
    {
      "url": "https://example.com/about",
      "depth": 1,
      "path": "text/example_com__about.html"
    }
  ],

  "downloaded": [
    {
      "url": "https://example.com/assets/hero.jpg",
      "path": "images/example_com__assets__hero.jpg",
      "size_bytes": 204800,
      "type": "images"
    }
  ],

  "skipped": [
    {
      "url": "https://cdn.example.com/video_hd.mp4",
      "reason": "size 342.1MB > limit 200MB"
    }
  ],

  "errors": [
    {
      "url": "https://example.com/broken-link",
      "error": "404 Client Error: Not Found"
    }
  ],

  "embedded_video_urls": [
    "https://www.youtube.com/watch?v=abc123",
    "https://vimeo.com/123456789"
  ]
}
```

---

## Field Reference

### Top-level

| Field | Type | Description |
|---|---|---|
| `seed_url` | string | The URL the crawl started from |
| `started_at` | ISO datetime | When crawl began |
| `finished_at` | ISO datetime | When crawl completed |
| `stats` | object | Aggregate counts |

### `stats`

| Field | Description |
|---|---|
| `pages_visited` | Total HTML pages crawled |
| `files_downloaded` | Total asset files saved to disk |
| `files_skipped` | Files not downloaded (size limit, type filter) |
| `errors` | Fetch/download failures |
| `embedded_videos` | YouTube/Vimeo URLs found |
| `total_bytes_downloaded` | Total bytes saved to disk |

### `pages_visited[]`

| Field | Description |
|---|---|
| `url` | Full page URL |
| `depth` | Crawl depth from seed (0 = seed page) |
| `path` | Relative path of saved HTML file |

### `downloaded[]`

| Field | Description |
|---|---|
| `url` | Source URL of the asset |
| `path` | Relative path under output dir |
| `size_bytes` | File size in bytes |
| `type` | Subfolder: `images`, `pdfs`, `videos`, `audio`, `documents`, `other` |

### `skipped[]`

| Field | Description |
|---|---|
| `url` | URL that was skipped |
| `reason` | Human-readable reason |

### `errors[]`

| Field | Description |
|---|---|
| `url` | URL that failed |
| `error` | Error message string |

### `embedded_video_urls[]`

Plain list of YouTube/Vimeo embed URLs found in `<iframe>` tags. Also written to `embedded_video_urls.txt` (one per line).

---

## Querying the manifest

Quick bash one-liners to inspect results:

```bash
# Total files downloaded
jq '.stats.files_downloaded' manifest.json

# List all PDF paths
jq '[.downloaded[] | select(.type=="pdfs") | .path]' manifest.json

# List all errors
jq '.errors[] | .url + " → " + .error' manifest.json

# Total size in MB
jq '.stats.total_bytes_downloaded / 1048576 | round' manifest.json
```
