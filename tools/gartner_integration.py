import os
from typing import List, Dict


def fetch_gartner_mentions(domain: str, num_results: int = 3) -> List[Dict[str, str]]:
    """Return Gartner mentions for a domain. This is a mock/guarded implementation.

    In mock mode (GARTNER_MOCK=true), return synthetic results to keep tests offline.
    In live mode, attempt to fetch Gartner results (best-effort) and gracefully degrade.
    """
    domain = domain or "example.com"
    use_mock = os.getenv("GARTNER_MOCK", "true").lower() in ("1", "true", "yes")
    results: List[Dict[str, str]] = []
    if use_mock:
        base = [
            {
                "title": f"Gartner SEO insights for {domain}",
                "url": f"https://www.gartner.com/doc/{domain}-seo-1",
                "snippet": "Market overview and top performers in SEO tools.",
            },
            {
                "title": f"Competitor landscape: SEO tools for {domain}",
                "url": f"https://www.gartner.com/doc/{domain}-seo-competitors",
                "snippet": "Competitor feature analysis and gaps.",
            },
            {
                "title": "SEO technology trends 2026",
                "url": "https://www.gartner.com/doc/seo-trends-2026",
                "snippet": "AI-assisted SEO and data surface innovations.",
            },
        ]
        results = base[:num_results]
    else:
        # Lightweight live fetch: attempt to pull a small, non-auth content snippet if possible
        try:
            import requests

            # This is a best-effort; Gartner pages may be paywalled. We fetch a generic search results page if accessible.
            query = f"site:gartner.com SEO {domain}"
            url = f"https://www.google.com/search?q={query}"
            resp = requests.get(url, timeout=5)
            if resp.ok:
                # Very naive: return a single synthetic item describing the fetch attempt
                results = [
                    {
                        "title": "Gartner SEO result (live)",
                        "url": url,
                        "snippet": "Live Gartner data fetch attempted.",
                    }
                ]
        except Exception:
            results = []
    return results[:num_results]


def get_gartner_mentions(domain: str, num_results: int = 3) -> List[Dict[str, str]]:
    """Backward-compatible wrapper to fetch Gartner mentions for a domain.
    This allows the rest of the pipeline to call a stable API surface.
    """
    return fetch_gartner_mentions(domain, num_results=num_results)
