#!/usr/bin/env python3
"""
Autonomyx Web Crawler — powered by Firecrawl API
Supports: cloud (api.firecrawl.dev) or self-hosted Firecrawl instance.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

EXT_MAP = {
    "jpg": "images", "jpeg": "images", "png": "images",
    "gif": "images", "webp": "images", "svg": "images", "ico": "images",
    "pdf": "pdfs",
    "mp4": "videos", "webm": "videos", "mov": "videos", "mkv": "videos",
    "mp3": "audio", "wav": "audio", "ogg": "audio", "aac": "audio",
    "docx": "documents", "xlsx": "documents", "pptx": "documents",
    "doc": "documents", "xls": "documents", "ppt": "documents", "csv": "documents",
}

YOUTUBE_PATTERNS = [
    r"youtube\.com/watch", r"youtu\.be/",
    r"youtube\.com/embed/", r"vimeo\.com/",
]

SUBFOLDERS = ["text", "images", "pdfs", "videos", "audio", "documents", "other"]
DEFAULT_CLOUD_URL = "https://api.firecrawl.dev"


class FirecrawlClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def scrape(self, url, formats=None):
        payload = {"url": url, "formats": formats or ["html", "markdown", "links"]}
        r = self.session.post(f"{self.base_url}/v1/scrape", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def map(self, url, limit=5000):
        r = self.session.post(f"{self.base_url}/v1/map", json={"url": url, "limit": limit}, timeout=60)
        r.raise_for_status()
        return r.json().get("links", [])

    def crawl_async(self, url, options):
        r = self.session.post(f"{self.base_url}/v1/crawl", json=options, timeout=60)
        r.raise_for_status()
        return r.json()["id"]

    def crawl_status(self, job_id):
        r = self.session.get(f"{self.base_url}/v1/crawl/{job_id}", timeout=30)
        r.raise_for_status()
        return r.json()

    def crawl_cancel(self, job_id):
        self.session.delete(f"{self.base_url}/v1/crawl/{job_id}", timeout=10)


def url_to_slug(url, ext=""):
    p = urlparse(url)
    slug = (p.netloc + p.path).replace("/", "__").strip("_")
    slug = re.sub(r"[^\w\-.]", "_", slug)[:180]
    if ext and not slug.endswith(f".{ext}"):
        slug = f"{slug}.{ext}"
    return slug or url[-32:].replace("/", "_")


def get_ext(url):
    return Path(urlparse(url).path).suffix.lstrip(".").lower()


def route_asset(url):
    return EXT_MAP.get(get_ext(url), "other")


def is_embedded_video(url):
    return any(re.search(p, url) for p in YOUTUBE_PATTERNS)


def safe_filename(output_dir, subfolder, slug):
    target = output_dir / subfolder / slug
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 2
    while True:
        c = target.parent / f"{stem}__{i}{suffix}"
        if not c.exists():
            return c
        i += 1


def download_binary(url, output_dir, dl_session, max_mb, manifest):
    try:
        head = dl_session.head(url, timeout=10, allow_redirects=True)
        cl = int(head.headers.get("content-length", 0))
        if cl and cl > max_mb * 1024 * 1024:
            mb = cl / (1024 * 1024)
            print(f"  [SKIP]  {url}  ({mb:.1f} MB > {max_mb} MB limit)")
            manifest["skipped"].append({"url": url, "reason": f"size {mb:.1f}MB > limit"})
            return False

        subfolder = route_asset(url)
        ext = get_ext(url)
        dest = safe_filename(output_dir, subfolder, url_to_slug(url, ext))

        downloaded = 0
        with dl_session.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    downloaded += len(chunk)
                    if downloaded > max_mb * 1024 * 1024:
                        dest.unlink(missing_ok=True)
                        manifest["skipped"].append({"url": url, "reason": "size limit mid-download"})
                        return False
                    f.write(chunk)

        print(f"  [ASSET] {subfolder}/{dest.name}  ({downloaded/1024/1024:.2f} MB)")
        manifest["downloaded"].append({
            "url": url, "path": str(dest.relative_to(output_dir)),
            "size_bytes": downloaded, "type": subfolder,
        })
        return True
    except Exception as e:
        print(f"  [ERR]   {url} — {e}")
        manifest["errors"].append({"url": url, "error": str(e)})
        return False


def run_crawl(args):
    output_dir = Path(args.output).expanduser().resolve()
    for sub in SUBFOLDERS:
        (output_dir / sub).mkdir(parents=True, exist_ok=True)

    base_url = args.firecrawl_url or os.environ.get("FIRECRAWL_URL", DEFAULT_CLOUD_URL)
    api_key  = args.api_key or os.environ.get("FIRECRAWL_API_KEY", "")

    if not api_key and base_url == DEFAULT_CLOUD_URL:
        print("[ERR] FIRECRAWL_API_KEY is required for the cloud API.")
        print("      export FIRECRAWL_API_KEY=fc-YOUR-KEY")
        print("      For self-hosted with no auth: --api-key dummy")
        sys.exit(1)

    fc = FirecrawlClient(base_url, api_key or "self-hosted")
    dl_session = requests.Session()
    dl_session.headers.update({"User-Agent": "AutonomyxCrawler/1.0"})

    print(f"\n🔥 Firecrawl : {base_url}")
    print(f"   URL       : {args.url}")
    print(f"   Output    : {output_dir}\n")

    manifest = {
        "seed_url": args.url, "firecrawl_url": base_url,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "pages_visited": [], "downloaded": [],
        "skipped": [], "errors": [],
        "embedded_video_urls": [], "stats": {},
    }
    embedded_videos = []

    # Step 1: Map
    if not args.skip_map:
        print("📍 Step 1: Mapping site URLs ...")
        try:
            urls = fc.map(args.url, limit=args.max_pages or 5000)
            print(f"   Found {len(urls)} URLs in site map.\n")
        except Exception as e:
            print(f"   [WARN] Map failed ({e}), continuing.\n")

    # Step 2: Crawl async
    print("🕷️  Step 2: Starting async crawl ...")
    options = {
        "url": args.url,
        "scrapeOptions": {"formats": ["html", "markdown", "links"]},
    }
    if args.max_pages:   options["limit"]    = args.max_pages
    if args.max_depth:   options["maxDepth"] = args.max_depth
    if args.include_patterns: options["includePaths"] = args.include_patterns.split(",")
    if args.exclude_patterns: options["excludePaths"] = args.exclude_patterns.split(",")

    try:
        job_id = fc.crawl_async(args.url, options)
        print(f"   Job ID: {job_id}\n")
    except Exception as e:
        print(f"[ERR] Failed to start crawl: {e}")
        sys.exit(1)

    # Step 3: Poll
    print("⏳ Step 3: Polling ...")
    pages_data = []
    while True:
        try:
            resp = fc.crawl_status(job_id)
        except Exception as e:
            print(f"  [WARN] Poll error: {e}. Retrying...")
            time.sleep(5)
            continue

        status    = resp.get("status", "unknown")
        completed = resp.get("completed", 0)
        total     = resp.get("total", "?")
        print(f"  [{status.upper()}] {completed}/{total} pages ...")

        if status == "completed":
            pages_data = resp.get("data", [])
            break
        elif status in ("failed", "cancelled"):
            print(f"[ERR] Crawl {status}.")
            manifest["errors"].append({"url": args.url, "error": f"Crawl {status}"})
            break
        time.sleep(5)

    print(f"\n✅ {len(pages_data)} pages received.\n")

    # Step 4: Save pages + download assets
    print("💾 Step 4: Saving pages and assets ...")
    seen_assets = set()

    for i, page in enumerate(pages_data, 1):
        source_url = page.get("metadata", {}).get("sourceURL", "") or page.get("url", "")
        html_content = page.get("html", "")
        md_content   = page.get("markdown", "")
        page_links   = page.get("links", [])

        print(f"\n  [{i}/{len(pages_data)}] {source_url}")

        if html_content:
            dest = safe_filename(output_dir, "text", url_to_slug(source_url, "html"))
            dest.write_text(html_content, encoding="utf-8")

        if md_content:
            dest_md = safe_filename(output_dir, "text", url_to_slug(source_url, "md"))
            dest_md.write_text(md_content, encoding="utf-8")
            print(f"  [TEXT]  text/{dest_md.name}  ({len(md_content.encode())/1024:.1f} KB)")

        manifest["pages_visited"].append({
            "url": source_url,
            "html_path": f"text/{url_to_slug(source_url, 'html')}",
            "md_path":   f"text/{url_to_slug(source_url, 'md')}",
        })

        if args.download_assets and page_links:
            for link in page_links:
                if is_embedded_video(link):
                    if link not in embedded_videos:
                        embedded_videos.append(link)
                        print(f"  [EMBED] {link}")
                    continue
                ext = get_ext(link)
                if not ext or ext in ("html", "htm", "php", "asp", "aspx", ""):
                    continue
                if link in seen_assets:
                    continue
                seen_assets.add(link)
                if args.include_types and args.include_types != "all":
                    allowed = [e.strip().lstrip(".") for e in args.include_types.split(",")]
                    if ext not in allowed:
                        continue
                download_binary(link, output_dir, dl_session, args.max_file_size, manifest)

    # Step 5: Embedded videos file
    if embedded_videos:
        (output_dir / "embedded_video_urls.txt").write_text("\n".join(embedded_videos) + "\n")
        manifest["embedded_video_urls"] = embedded_videos
        print(f"\n📋 {len(embedded_videos)} embedded video URLs saved.")

    # Step 6: Manifest
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["stats"] = {
        "pages_visited":          len(manifest["pages_visited"]),
        "files_downloaded":       len(manifest["downloaded"]),
        "files_skipped":          len(manifest["skipped"]),
        "errors":                 len(manifest["errors"]),
        "embedded_videos":        len(embedded_videos),
        "total_bytes_downloaded": sum(d.get("size_bytes", 0) for d in manifest["downloaded"]),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    s = manifest["stats"]
    total_mb = s["total_bytes_downloaded"] / (1024 * 1024)
    print(f"""
╔══════════════════════════════════════════╗
║         CRAWL COMPLETE 🔥                ║
╠══════════════════════════════════════════╣
║  Pages scraped:      {str(s['pages_visited']):<21}║
║  Assets downloaded:  {str(s['files_downloaded']):<5}  ({total_mb:.1f} MB)        ║
║  Assets skipped:     {str(s['files_skipped']):<21}║
║  Errors:             {str(s['errors']):<21}║
║  Embedded videos:    {str(s['embedded_videos']):<5}  (URLs saved)        ║
╚══════════════════════════════════════════╝
  Manifest → {manifest_path}
""")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomyx Web Crawler — powered by Firecrawl API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Env vars:
  FIRECRAWL_URL       Base URL (default: https://api.firecrawl.dev)
  FIRECRAWL_API_KEY   API key (required for cloud; use 'dummy' for self-hosted no-auth)

Self-hosted example (your Coolify VPS):
  export FIRECRAWL_URL=http://vps.agnxxt.com:3002
  export FIRECRAWL_API_KEY=dummy
  python scripts/crawl.py --url https://example.com --output ./output

Cloud example:
  export FIRECRAWL_API_KEY=fc-YOUR-KEY
  python scripts/crawl.py --url https://example.com --output ./output
        """
    )
    parser.add_argument("--url",               required=True)
    parser.add_argument("--output",            required=True)
    parser.add_argument("--firecrawl-url",     default=None, dest="firecrawl_url",
                        help="Firecrawl base URL (overrides FIRECRAWL_URL)")
    parser.add_argument("--api-key",           default=None, dest="api_key",
                        help="API key (overrides FIRECRAWL_API_KEY)")
    parser.add_argument("--max-pages",         type=int, default=None, dest="max_pages")
    parser.add_argument("--max-depth",         type=int, default=None, dest="max_depth")
    parser.add_argument("--max-file-size",     type=int, default=200,  dest="max_file_size",
                        help="Max asset size in MB (default: 200)")
    parser.add_argument("--include-types",     default="all", dest="include_types",
                        help="Asset extensions to download, e.g. pdf,jpg")
    parser.add_argument("--include-patterns",  default=None, dest="include_patterns",
                        help="URL path patterns to include (comma-separated)")
    parser.add_argument("--exclude-patterns",  default=None, dest="exclude_patterns",
                        help="URL path patterns to exclude (comma-separated)")
    parser.add_argument("--no-assets",         action="store_false", dest="download_assets",
                        default=True, help="Skip downloading binary assets")
    parser.add_argument("--skip-map",          action="store_true", dest="skip_map",
                        help="Skip the /map discovery step")
    args = parser.parse_args()
    run_crawl(args)


if __name__ == "__main__":
    main()
