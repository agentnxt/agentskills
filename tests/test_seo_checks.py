import json

from tests.mock_audit import mock_audit
from tools.seo_checks import run_checks


def test_checks_score_in_range():
    aud = mock_audit("https://example.com")
    res = run_checks(aud)
    assert isinstance(res, dict)
    assert "score" in res
    score = res["score"]
    assert isinstance(score, int) or isinstance(score, float)
    assert 0 <= score <= 100


def test_competitor_insights_present():
    aud = mock_audit("https://example.com")
    res = run_checks(aud)
    assert "competitor_insights" in res
    ci = res["competitor_insights"]
    assert isinstance(ci, dict)
    # Expect keys we defined (even if mocked None in some runs)
    for k in [
        "overlap_percent",
        "top_pages_overlap_percent",
        "backlink_quality",
        "content_gap",
    ]:
        assert k in ci


def test_competitor_non_dict_input_is_safe():
    aud = mock_audit("https://example.com")
    aud["competitor"] = "unexpected-non-dict"

    res = run_checks(aud)
    ci = res["competitor_insights"]

    assert ci["keyword_overlap_percent"] is None
    assert ci["traffic_overlap_percent"] is None
    assert ci["content_gap_topics"] is None
    assert ci["backlink_toxicity"] is None
    assert ci["domain_authority_gap"] is None
