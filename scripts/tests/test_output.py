"""Tests for output module — JSON result collection and text formatting."""

import json

from playbook_validator.output import ResultCollector


class TestResultCollector:
    """Test the JSON result collector."""

    def test_empty_collector(self):
        rc = ResultCollector()
        result = rc.to_dict()
        assert result["status"] == "success"
        assert result["checks_passed"] == 0
        assert result["checks_failed"] == 0
        assert result["results"] == []
        assert result["warnings"] == []
        assert result["errors"] == []

    def test_add_pass(self):
        rc = ResultCollector()
        rc.add_result("test.md", "has title", passed=True)
        result = rc.to_dict()
        assert result["checks_passed"] == 1
        assert result["checks_failed"] == 0
        assert result["status"] == "success"
        assert result["results"][0]["file"] == "test.md"
        assert result["results"][0]["check"] == "has title"
        assert result["results"][0]["pass"] is True

    def test_add_fail(self):
        rc = ResultCollector()
        rc.add_result("test.md", "has title", passed=False, note="missing title field")
        result = rc.to_dict()
        assert result["checks_passed"] == 0
        assert result["checks_failed"] == 1
        assert result["status"] == "failure"
        assert result["results"][0]["pass"] is False
        assert result["results"][0]["note"] == "missing title field"

    def test_mixed_results(self):
        rc = ResultCollector()
        rc.add_result("a.md", "check1", passed=True)
        rc.add_result("b.md", "check2", passed=False)
        result = rc.to_dict()
        assert result["status"] == "partial"
        assert result["checks_passed"] == 1
        assert result["checks_failed"] == 1

    def test_add_warning(self):
        rc = ResultCollector()
        rc.add_warning("something looks off")
        result = rc.to_dict()
        assert result["warnings"] == ["something looks off"]

    def test_add_error(self):
        rc = ResultCollector()
        rc.add_error("something broke")
        result = rc.to_dict()
        assert result["errors"] == ["something broke"]

    def test_extra_fields(self):
        rc = ResultCollector()
        rc.add_result("x.md", "check", passed=True)
        result = rc.to_dict(skipped=3, total_files=10)
        assert result["skipped"] == 3
        assert result["total_files"] == 10

    def test_to_json_is_valid(self):
        rc = ResultCollector()
        rc.add_result("test.md", 'check with "quotes"', passed=True)
        rc.add_result("test.md", "check with \\backslash", passed=False, note="path: C:\\Users")
        rc.add_warning('warning with "quotes"')
        rc.add_error("error with\nnewline")
        json_str = rc.to_json()
        # Must be valid JSON
        parsed = json.loads(json_str)
        assert parsed["checks_passed"] == 1
        assert parsed["checks_failed"] == 1

    def test_to_json_special_chars(self):
        """Verify special characters don't break JSON output."""
        rc = ResultCollector()
        rc.add_result("file.md", 'check: "value"', passed=False, note="fix: use \\ not /")
        json_str = rc.to_json()
        parsed = json.loads(json_str)
        assert parsed["results"][0]["check"] == 'check: "value"'
        assert parsed["results"][0]["note"] == "fix: use \\ not /"

    def test_exit_code(self):
        rc = ResultCollector()
        assert rc.exit_code == 0  # no results = success

        rc.add_result("a.md", "ok", passed=True)
        assert rc.exit_code == 0

        rc.add_result("b.md", "fail", passed=False)
        assert rc.exit_code == 1


class TestTextOutput:
    """Test human-readable text formatting."""

    def test_format_pass(self):
        rc = ResultCollector()
        rc.add_result("test.md", "has title", passed=True)
        text = rc.format_text()
        assert "[PASS]" in text
        assert "has title" in text

    def test_format_fail_with_note(self):
        rc = ResultCollector()
        rc.add_result("test.md", "has title", passed=False, note="add title field")
        text = rc.format_text()
        assert "[FAIL]" in text
        assert "add title field" in text

    def test_format_summary(self):
        rc = ResultCollector()
        rc.add_result("a.md", "c1", passed=True)
        rc.add_result("b.md", "c2", passed=False)
        text = rc.format_text()
        assert "Passed: 1" in text
        assert "Failed: 1" in text
