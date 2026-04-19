#!/usr/bin/env python3
import json


def mock_audit(url: str) -> dict:
    return {
        "url": url,
        "technical": {
            "crawlable": True,
            "lighthouse_score": 88,
            "schema_present": True,
            "index_coverage_ok": True,
            "index_coverage_per_url": [
                {"url": "https://example.com/", "index_status": "Indexed"}
            ],
            "mobile_friendly": True,
            "amp_pages_present": False,
            "gbp_health": {"status": "Good"},
            "canonical_matches": True,
        },
        "on_page": {
            "title": "Example Title",
            "meta_description": "Description of the page for SEO audit.",
            "h1": "Example H1 Heading",
            "canonical": "https://example.com/",
        },
        "content": {
            "length": 1200,
            "readability": 62.5,
        },
        "summary": "Mock audit complete. Key issues: none.",
        "competitor": {
            "overlap_percent": 25,
            "top_pages_overlap_percent": 15,
            "keyword_overlap_percent": 40,
            "traffic_overlap_percent": 30,
            "content_gap": 10,
            "backlink_quality": 68,
            "backlink_toxicity": 0.05,
            "domain_authority_gap": 12,
            "content_gap_topics": ["topic A", "topic B"],
            "backlink_toxicity": 0.05,
        },
    }


def main():
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    aud = mock_audit(url)
    try:
        from tools.seo_checks import run_checks

        checks = run_checks(aud)
        print(json.dumps({"audit": aud, "checks": checks}, indent=2))
    except Exception:
        print(json.dumps(aud, indent=2))


if __name__ == "__main__":
    main()
