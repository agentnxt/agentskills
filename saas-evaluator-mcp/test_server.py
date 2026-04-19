"""Smoke tests for SaaS Evaluator MCP server — no API key required."""
import json
import sys
import os

# Ensure no API key so tests use fallback scoring
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ["EVAL_DATA_DIR"] = "/tmp/saas-evaluator-test"

from server import (
    slugify, calc_u_index, get_verdict, get_blockers,
    start_evaluation, score_metric, get_evaluation_status,
    mark_persona_complete, add_alternative, compare_alternatives,
    get_report, list_evaluations, METRICS, DATA_DIR,
)
import shutil

# Clean test data dir
if DATA_DIR.exists():
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(parents=True)


def test_slugify():
    assert slugify("Notion AI") == "notion-ai"
    assert slugify("Rippling") == "rippling"


def test_calc_u_index_empty():
    assert calc_u_index({}) == 0.0


def test_calc_u_index_all_fives():
    scores = {m["id"]: 5 for m in METRICS}
    assert calc_u_index(scores) == 5.0


def test_calc_u_index_all_threes():
    scores = {m["id"]: 3 for m in METRICS}
    u = calc_u_index(scores)
    assert 2.9 <= u <= 3.1


def test_get_verdict():
    assert get_verdict(4.5)["label"] == "Strong"
    assert get_verdict(3.2)["label"] == "Enterprise Baseline"
    assert get_verdict(2.1)["label"] == "Emerging"
    assert get_verdict(1.0)["label"] == "Not Enterprise-Ready"


def test_start_evaluation():
    result = start_evaluation("TestProduct", "enterprise knowledge management")
    assert result["product"] == "TestProduct"
    assert result["slug"] == "testproduct"
    assert "u_index" in result
    assert "scores" in result
    assert result["total_metrics"] == 38


def test_score_metric():
    start_evaluation("ScoreTest")
    result = score_metric("scoretest", "2.3", 0)
    assert result["score_set"] == 0
    assert result["is_procurement_blocker"] is True
    assert "u_index" in result


def test_score_metric_invalid():
    result = score_metric("scoretest", "2.3", 9)
    assert "error" in result


def test_score_metric_not_found():
    result = score_metric("doesnotexist", "2.3", 3)
    assert "error" in result


def test_get_evaluation_status():
    start_evaluation("StatusTest")
    result = get_evaluation_status("statustest")
    assert result["product"] == "StatusTest"
    assert "stage_breakdown" in result
    assert len(result["stage_breakdown"]) == 7
    assert "blockers" in result


def test_mark_persona_complete():
    start_evaluation("PersonaTest")
    result = mark_persona_complete("personatest", "ciso")
    assert "ciso" in result["completed_personas"]
    assert result["ready_for_report"] is False

    # Mark all 6
    for p in ["it-admin", "procurement", "cto", "legal", "dept-head"]:
        mark_persona_complete("personatest", p)
    status = get_evaluation_status("personatest")
    assert status["ready_for_report"] is True


def test_mark_persona_invalid():
    start_evaluation("PersonaTest2")
    result = mark_persona_complete("personatest2", "cfo")
    assert "error" in result


def test_add_alternative():
    start_evaluation("AltPrimary", "team collaboration")
    result = add_alternative("altprimary", "Confluence")
    assert result["alternative"] == "Confluence"
    assert "u_index" in result
    assert result["scored_metrics"] > 0


def test_compare_alternatives():
    start_evaluation("CompareTest", "knowledge management")
    add_alternative("comparetest", "CompetitorA")
    result = compare_alternatives("comparetest", "all")
    assert "overall_scores" in result
    assert "metric_comparison" in result
    assert "overall_winner" in result
    assert len(result["metric_comparison"]) == 38


def test_compare_alternatives_filter_gaps():
    result = compare_alternatives("comparetest", "gaps")
    assert "metric_comparison" in result
    # gaps filter may return 0 or more — just check it runs
    assert isinstance(result["metric_comparison"], list)


def test_get_report():
    start_evaluation("ReportTest", "HR platform")
    result = get_report("reporttest")
    assert result["product"] == "ReportTest"
    assert "u_index" in result
    assert "recommendation" in result
    assert len(result["stages"]) == 7
    assert result["scored_metrics"] == 38


def test_list_evaluations():
    result = list_evaluations()
    assert "evaluations" in result
    assert result["count"] >= 1
    slugs = [e["slug"] for e in result["evaluations"]]
    assert "testproduct" in slugs


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
