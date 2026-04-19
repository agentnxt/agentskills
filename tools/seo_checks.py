import os
from urllib.parse import urlparse
from typing import Dict, Any, List


def _score_lighthouse(value: int) -> int:
    # Map lighthouse_score (0-100) to a 0-20 contribution
    try:
        v = int(value)
    except Exception:
        v = 0
    if v < 0:
        v = 0
    if v > 100:
        v = 100
    return max(0, min(20, v // 5))


def compute_seo_score(audit: Dict[str, Any]) -> int:
    """Compute an overall SEO score (0-100) from the audit payload.

    Weight distribution (examples):
      technical: 40
      on-page: 20
      content: 20
      misc: 20
    This is a starting point and can be tuned as needed.
    """
    SEO_AMP_SIGNAL_ENABLED = os.getenv("SEO_AMP_SIGNAL_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    weights = {
        "crawlable": 10,
        "lighthouse_score": 20,
        "schema_present": 6,
        "index_coverage_ok": 6,
        "mobile_friendly": 6,
        "amp_pages_present": 2,
        "canonical_present": 6,
        "title_present": 4,
        "meta_description_present": 4,
        "h1_present": 3,
        "content_length_ok": 4,
        "readability_ok": 3,
    }

    tech = audit.get("technical", {})
    on_page = audit.get("on_page", {})
    content = audit.get("content", {})

    score = 0
    # Technical signals
    score += weights["crawlable"] if tech.get("crawlable", False) else 0
    score += _score_lighthouse(tech.get("lighthouse_score", 0))
    score += weights["schema_present"] if tech.get("schema_present", False) else 0
    score += weights["index_coverage_ok"] if tech.get("index_coverage_ok", False) else 0
    score += weights["mobile_friendly"] if tech.get("mobile_friendly", False) else 0
    amp_present = (
        tech.get("amp_pages_present", False) if SEO_AMP_SIGNAL_ENABLED else False
    )
    score += weights["amp_pages_present"] if amp_present else 0

    # On-page signals
    score += weights["canonical_present"] if on_page.get("canonical") else 0
    score += weights["title_present"] if on_page.get("title") else 0
    score += (
        weights["meta_description_present"] if on_page.get("meta_description") else 0
    )
    score += weights["h1_present"] if on_page.get("h1") else 0

    # Content signals
    score += weights["content_length_ok"] if (content.get("length", 0) >= 800) else 0
    score += weights["readability_ok"] if (content.get("readability", 0) >= 50) else 0

    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return score


def run_checks(audit: Dict[str, Any]) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    tech = audit.get("technical", {})
    on_page = audit.get("on_page", {})
    content = audit.get("content", {})

    # Technical checks
    results.append(
        {
            "name": "crawlable",
            "passed": bool(tech.get("crawlable", False)),
            "notes": "Crawl access available"
            if tech.get("crawlable", False)
            else "Crawl not allowed",
        }
    )
    results.append(
        {
            "name": "lighthouse_score",
            "passed": bool(tech.get("lighthouse_score", 0) >= 80),
            "notes": f"Score {tech.get('lighthouse_score', 0)}",
        }
    )
    results.append(
        {
            "name": "schema_present",
            "passed": bool(tech.get("schema_present", False)),
            "notes": "Schema present"
            if tech.get("schema_present", False)
            else "Schema missing",
        }
    )

    # Additional technical checks
    results.append(
        {
            "name": "index_coverage_ok",
            "passed": bool(tech.get("index_coverage_ok", False)),
            "notes": "Index coverage OK"
            if tech.get("index_coverage_ok", False)
            else "Index coverage issues",
        }
    )
    results.append(
        {
            "name": "mobile_friendly",
            "passed": bool(tech.get("mobile_friendly", False)),
            "notes": "Mobile friendly"
            if tech.get("mobile_friendly", False)
            else "Not mobile-friendly",
        }
    )
    results.append(
        {
            "name": "amp_pages_present",
            "passed": bool(tech.get("amp_pages_present", False)),
            "notes": "AMP pages present"
            if tech.get("amp_pages_present", False)
            else "AMP pages not present",
        }
    )

    # On-page checks
    results.append(
        {
            "name": "title_present",
            "passed": bool(on_page.get("title")),
            "notes": "Title present" if on_page.get("title") else "Missing title",
        }
    )
    results.append(
        {
            "name": "meta_description_present",
            "passed": bool(on_page.get("meta_description")),
            "notes": "Meta description present"
            if on_page.get("meta_description")
            else "Missing meta description",
        }
    )
    results.append(
        {
            "name": "h1_present",
            "passed": bool(on_page.get("h1")),
            "notes": "H1 present" if on_page.get("h1") else "Missing H1",
        }
    )

    # Canonical check (per-page basis)
    canonical_val = on_page.get("canonical")
    results.append(
        {
            "name": "canonical_present",
            "passed": bool(canonical_val),
            "notes": f"Canonical: {canonical_val}"
            if canonical_val
            else "No canonical provided",
        }
    )

    # Content checks
    results.append(
        {
            "name": "content_length_ok",
            "passed": bool(content.get("length", 0) >= 800),
            "notes": f"Length {content.get('length', 0)}",
        }
    )
    results.append(
        {
            "name": "readability_ok",
            "passed": bool(content.get("readability", 0) >= 50),
            "notes": f"Readability {content.get('readability', 0)}",
        }
    )

    overall_pass = all(r["passed"] for r in results)
    # Competitor signals (mocked for now) integrated as a separate insight bundle
    comp = {}
    live = os.getenv("SEO_COMPETITOR_LIVE", "false").lower() in ("1", "true", "yes")
    if live:
        try:
            from tools.competitor_analysis_tool import CompetitorAnalysisTool

            parsed = urlparse(audit.get("url", ""))
            domain = parsed.netloc or audit.get("domain")
            if domain:
                tool = CompetitorAnalysisTool(domain=domain)
                signals = tool.fetch_signals()
                comp = signals
        except Exception:
            comp = {}
    if not comp and isinstance(audit.get("competitor"), dict):
        comp = audit.get("competitor") or {}
    overlap = comp.get("overlap_percent") if isinstance(comp, dict) else None
    top_pages_overlap = (
        comp.get("top_pages_overlap_percent") if isinstance(comp, dict) else None
    )
    backlink_quality = comp.get("backlink_quality") if isinstance(comp, dict) else None
    content_gap = comp.get("content_gap") if isinstance(comp, dict) else None
    competitor_insights = {
        "overlap_percent": overlap,
        "top_pages_overlap_percent": top_pages_overlap,
        "keyword_overlap_percent": comp.get("keyword_overlap_percent")
        if isinstance(comp, dict)
        else None,
        "traffic_overlap_percent": comp.get("traffic_overlap_percent")
        if isinstance(comp, dict)
        else None,
        "content_gap": content_gap,
        "content_gap_topics": comp.get("content_gap_topics")
        if isinstance(comp, dict)
        else None,
        "backlink_quality": backlink_quality,
        "backlink_toxicity": comp.get("backlink_toxicity")
        if isinstance(comp, dict)
        else None,
        "domain_authority_gap": comp.get("domain_authority_gap")
        if isinstance(comp, dict)
        else None,
    }

    # Competitor score aggregation (mocked-based)
    def _toi(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    kw_overlap = comp.get("keyword_overlap_percent") if isinstance(comp, dict) else None
    t_overlap = comp.get("traffic_overlap_percent") if isinstance(comp, dict) else None
    overlap_score = _toi(overlap, 0)
    top_overlap_score = _toi(top_pages_overlap, 0)
    kw_overlap_score = _toi(kw_overlap, 0)
    t_overlap_score = _toi(t_overlap, 0)
    blw_score = _toi(backlink_quality, 0)
    content_gap_score = _toi(content_gap, 0)
    da_gap_score = (
        _toi(comp.get("domain_authority_gap")) if isinstance(comp, dict) else 0
    )
    toxicity = (
        float(comp.get("backlink_toxicity", 0))
        if isinstance(comp, dict) and comp.get("backlink_toxicity") is not None
        else 0.0
    )
    competitor_score = (
        min(25, overlap_score)
        + min(20, top_overlap_score)
        + min(25, kw_overlap_score)
        + min(15, t_overlap_score)
        + min(15, blw_score)
        + min(15, content_gap_score)
        + min(10, da_gap_score)
    )
    penalty = int(min(25, max(0.0, toxicity) * 25))
    competitor_score = max(0, min(100, competitor_score - penalty))
    # Gating (configurable)
    gating_enabled = os.getenv("SEO_GATE_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    gate_threshold = int(os.getenv("SEO_GATE_THRESHOLD", "60"))
    gate = {"enabled": gating_enabled, "threshold": gate_threshold, "triggered": False}
    score = compute_seo_score(audit)
    if gating_enabled and score < gate_threshold:
        gate["triggered"] = True
        overall_pass = False
    return {
        "pass": overall_pass,
        "score": score,
        "competitor_score": int(competitor_score),
        "gate": gate,
        "competitor_insights": competitor_insights,
        "details": results,
    }
