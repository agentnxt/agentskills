from typing import List, Dict, Any, Optional


class CompetitorAnalysisTool:
    """Mocked competitor analysis tool to surface signals for SEO scoring.

    In a real deployment, this would wrap Semrush/Ahrefs APIs to fetch:
    - keyword overlap with top competitors
    - top page overlap
    - backlink quality gaps
    - content gaps against competitors
    """

    def __init__(
        self,
        domain: str,
        competitors: Optional[List[str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
    ):
        self.domain = domain
        self.competitors = competitors or []
        self.api_keys = api_keys or {}

    def fetch_competitors(self) -> List[str]:
        # Mock: return a deterministic list if none supplied
        if self.competitors:
            return self.competitors
        return ["competitor1.com", "competitor2.com", "competitor3.com"]

    def fetch_signals(self) -> Dict[str, Any]:
        # Mocked signals; in real use, call Semrush/Ahrefs here
        return {
            "overlap_percent": 25,
            "top_pages_overlap_percent": 15,
            "backlink_quality": 68,
            "content_gap": 10,
        }
