---
name: web-crawler
description: >
  Fully recursive web crawler powered by Firecrawl open-source API. Downloads everything from
  a URL into typed local subfolders: HTML/markdown, images, PDFs, videos, audio, documents.
  Supports Firecrawl cloud (api.firecrawl.dev) and self-hosted instances on Coolify/Docker.
  Handles JS-heavy sites natively. Saves YouTube/Vimeo embed URLs separately. Enforces file
  size limits. Produces a full crawl manifest. ALWAYS trigger this skill when a user says:
  "crawl this site", "download everything from", "scrape all assets", "mirror a website",
  "download all PDFs/images/videos from a URL", "web scrape", "archive this site",
  "download all files from", "recursive download", or any request to bulk-download or
  mirror content from a website.
---

# Web Crawler Skill — powered by Firecrawl 🔥

Recursively crawls a URL and downloads all assets into typed subfolders.
Uses [Firecrawl](https://github.com/firecrawl/firecrawl) as the crawl engine — handles JS rendering,
anti-bot mechanisms, clean markdown output, and async polling natively.

Works with **Firecrawl cloud** (`api.firecrawl.dev`) or a **self-hosted Firecrawl instance**
(deploy to your Coolify VPS — see `references/self-host.md`).

---

## Quick Reference

| What you need | Where to go |
|---|---|
| Step-by-step execution | [Execution Steps](#execution-steps) below |
| Script flags | [Scripts](#scripts) section |
| Self-host Firecrawl on Coolify | [references/self-host.md](references/self-host.md) |
| Output folder layout | [Output Structure](#output-structure) below |
| Manifest format | [references/manifest-schema.md](references/manifest-schema.md) |

---

## Inputs

| Parameter | Required | Default | Notes |
|---|---|---|---|
| `url` | ✅ | — | Seed URL to crawl |
| `output_dir` | ✅ | — | Local folder to write into |
| `FIRECRAWL_URL` | ❌ | `https://api.firecrawl.dev` | Set to self-hosted URL if needed |
| `FIRECRAWL_API_KEY` | ✅* | — | Required for cloud; use `dummy` for self-hosted no-auth |
| `max_pages` | ❌ | unlimited | Cap on pages to crawl |
| `max_depth` | ❌ | unlimited | Max link depth |
| `max_file_size_mb` | ❌ | 200 | Skip assets larger than this |
| `include_types` | ❌ | `all` | Comma list of extensions, e.g. `pdf,jpg` |
| `include_patterns` | ❌ | — | URL path patterns to include |
| `exclude_patterns` | ❌ | — | URL path patterns to exclude |

---

## Output Structure

```
<output_dir>/
├── text/           # HTML + Markdown per page (one .html + one .md per URL)
├── images/         # .jpg .png .gif .webp .svg
├── pdfs/           # .pdf
├── videos/         # .mp4 .webm (direct asset links)
├── audio/          # .mp3 .wav
├── documents/      # .docx .xlsx .pptx
├── other/          # All other file types
├── embedded_video_urls.txt   # YouTube/Vimeo URLs (not downloaded)
└── manifest.json             # Full crawl report
```

---

## Execution Steps

### Step 1 — Install dependencies

```bash
pip install requests firecrawl-py --break-system-packages
```

Or run: `bash scripts/install_deps.sh`

### Step 2 — Configure Firecrawl endpoint

**Option A: Cloud (api.firecrawl.dev)**
```bash
export FIRECRAWL_API_KEY=fc-YOUR-KEY
```

**Option B: Self-hosted on Coolify VPS**
```bash
export FIRECRAWL_URL=http://vps.agnxxt.com:3002
export FIRECRAWL_API_KEY=dummy
```
→ See `references/self-host.md` to deploy Firecrawl to Coolify.

### Step 3 — Run the crawler

```bash
python scripts/crawl.py \
  --url "https://example.com" \
  --output "./crawl-output" \
  --max-pages 200 \
  --max-file-size 100
```

### Step 4 — What happens internally

1. **Map** (`/v1/map`) — Firecrawl instantly discovers all URLs on the site
2. **Crawl async** (`/v1/crawl`) — Starts async job; Firecrawl handles JS rendering, rate limits, robots.txt
3. **Poll** (`GET /v1/crawl/{id}`) — Script polls every 5s until `status: completed`
4. **Save** — Each page → `text/<slug>.html` + `text/<slug>.md`; asset links → downloaded to typed subfolders
5. **Manifest** — Full report written to `manifest.json`

### Step 5 — Review results

```
🔥 Firecrawl : https://api.firecrawl.dev
   URL       : https://example.com
   Output    : /home/user/crawl-output

📍 Mapping site URLs ... Found 142 URLs
🕷️  Starting async crawl ... Job ID: abc-123
⏳ [SCRAPING] 45/142 pages ...
⏳ [COMPLETED] 142/142 pages ...
✅ 142 pages received.
💾 Saving pages and assets ...
  [1/142] https://example.com/
  [TEXT]  text/example_com__.md  (12.3 KB)
  [ASSET] images/example_com__hero.jpg  (0.24 MB)
```

---

## Scripts

### `scripts/crawl.py` — main crawler

Key flags:

| Flag | Description |
|---|---|
| `--url` | Seed URL |
| `--output` | Output directory |
| `--firecrawl-url` | Override `FIRECRAWL_URL` env var |
| `--api-key` | Override `FIRECRAWL_API_KEY` env var |
| `--max-pages` | Max pages to crawl |
| `--max-depth` | Max depth |
| `--max-file-size` | MB limit per asset (default: 200) |
| `--include-types` | Extensions to download, e.g. `pdf,jpg,mp4` |
| `--include-patterns` | URL path patterns to include (comma-sep) |
| `--exclude-patterns` | URL path patterns to exclude (comma-sep) |
| `--no-assets` | Skip binary asset downloads (pages only) |
| `--skip-map` | Skip the /map discovery step |

---

## Why Firecrawl vs raw Playwright

| Concern | Raw Playwright | Firecrawl |
|---|---|---|
| JS rendering | Manual setup | Built-in ✅ |
| Anti-bot / 403 bypass | DIY (hard) | Fire-engine (cloud) / partial (self-hosted) ✅ |
| Clean markdown output | DIY parse | Native ✅ |
| robots.txt | Manual | Built-in ✅ |
| Async job management | DIY | Built-in ✅ |
| Self-hosted option | N/A | Full parity ✅ |
| Gartner/LinkedIn bypass | ❌ | Cloud only (Fire-engine) |

> **Note**: Self-hosted Firecrawl does not include Fire-engine (Firecrawl's proprietary proxy/anti-bot layer). For sites like Gartner, use the cloud API with a valid key, or run the script from a residential IP.

---

## Common Problems

| Problem | Fix |
|---|---|
| `FIRECRAWL_API_KEY` missing | Set env var or use `--api-key` |
| 403 on target site | Use cloud API (has Fire-engine); or run from residential IP |
| Crawl job `failed` | Check Firecrawl logs: `docker logs firecrawl-api` |
| Self-hosted connection refused | Verify port 3002 is open; see `references/self-host.md` |
| Assets not downloading | Check `--include-types`; verify links are in page source |
| Empty markdown | Site may require auth — Firecrawl doesn't handle login forms natively |
