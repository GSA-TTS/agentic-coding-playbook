"""Tests for federal-pre-deployment-check generate-checklist-report.py (Issue #84).

The script uses a hyphenated filename, so it's loaded via importlib.
"""

import importlib.util
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "federal-pre-deployment-check" / "scripts"


@pytest.fixture(scope="module")
def report():
    spec = importlib.util.spec_from_file_location(
        "generate_checklist_report", SKILL_DIR / "generate-checklist-report.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_merge_results_maps_pass_fail_skip(report):
    automated = {
        "results": [
            {"item": "2.1", "pass": True, "note": "clean"},
            {"item": "2.2", "pass": False, "note": "leak found"},
            {"item": "2.3", "pass": "skip", "note": "n/a here"},
        ]
    }
    merged = report.merge_results(automated, {"results": []})
    assert merged["2.1"] == ("Pass", "clean")
    assert merged["2.2"] == ("Fail", "leak found")
    assert merged["2.3"] == ("N/A", "n/a here")


def test_merge_results_manual_overrides_automated(report):
    automated = {"results": [{"item": "4.1", "pass": False, "note": "auto fail"}]}
    manual = {"results": [{"item": "4.1", "status": "Pass", "note": "verified by human"}]}
    merged = report.merge_results(automated, manual)
    assert merged["4.1"] == ("Pass", "verified by human")


def test_merge_results_ignores_unknown_items(report):
    merged = report.merge_results({"results": [{"item": "99.9", "pass": True}]}, {"results": []})
    assert "99.9" not in merged


def test_generate_report_approved_when_no_failures(report):
    status_map = {item: ("Pass", "") for item in report.CHECKLIST_ITEMS}
    out = report.generate_report(status_map, "Sys A", "OpenCode")
    assert "# Pre-Deployment Security Checklist — Completed" in out
    assert "Sys A" in out
    assert "**APPROVED**" in out


def test_generate_report_conditionally_approved_with_minor_failures(report):
    status_map = {item: ("Pass", "") for item in report.CHECKLIST_ITEMS}
    # Two failures => conditionally approved (<= 3)
    status_map["2.1"] = ("Fail", "secret found")
    status_map["3.1"] = ("Fail", "no validation")
    out = report.generate_report(status_map, "Sys B", "OpenCode")
    assert "**CONDITIONALLY APPROVED**" in out
    assert "### Failed Items" in out
    assert "secret found" in out


def test_generate_report_not_approved_with_many_failures(report):
    status_map = {item: ("Pass", "") for item in report.CHECKLIST_ITEMS}
    for item in list(report.CHECKLIST_ITEMS)[:5]:
        status_map[item] = ("Fail", "broken")
    out = report.generate_report(status_map, "Sys C", "OpenCode")
    assert "**NOT APPROVED**" in out


def test_generate_report_marks_unverified_items_pending(report):
    # Empty status map => everything pending, counted as N/A in summary
    out = report.generate_report({}, "Sys D", "OpenCode")
    assert "N/A" in out
    assert "**APPROVED**" in out  # no explicit failures


def test_load_json_file_missing_returns_empty_results(report):
    assert report.load_json_file("/nonexistent/auto.json") == {"results": []}


def test_load_json_file_invalid_json_exits(report, tmp_path):
    bad = tmp_path / "auto.json"
    bad.write_text("{nope", encoding="utf-8")
    with pytest.raises(SystemExit):
        report.load_json_file(str(bad))


def test_load_json_file_reads_valid(report, tmp_path):
    good = tmp_path / "auto.json"
    good.write_text('{"results": [{"item": "1.1", "pass": true}]}', encoding="utf-8")
    data = report.load_json_file(str(good))
    assert data["results"][0]["item"] == "1.1"


def test_checklist_items_have_valid_categories(report):
    # Every checklist item's category must be one of the declared CATEGORIES.
    for _item, (category, _desc) in report.CHECKLIST_ITEMS.items():
        assert category in report.CATEGORIES
