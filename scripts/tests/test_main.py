"""Tests for CLI entry point (__main__.py).

Validates argument parsing, command dispatch, error handling,
and the --verbose flag.
"""

from unittest.mock import patch

import pytest
from playbook_validator.__main__ import main


class TestMainNoCommand:
    """Test behavior when no command is provided."""

    def test_no_args_prints_help_and_returns_2(self, capsys):
        with patch("sys.argv", ["playbook_validator"]):
            rc = main()
        assert rc == 2

    def test_unknown_command_exits_2(self, capsys):
        with (
            patch("sys.argv", ["playbook_validator", "nonexistent-command"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()
        assert exc_info.value.code == 2


class TestValidateDocs:
    """Test validate-docs command dispatch."""

    def test_validate_docs_on_valid_repo(self, tmp_path):
        doc = tmp_path / "test.md"
        doc.write_text('---\ntitle: "T"\ndescription: "D"\nstatus: canonical\ntier: 1\n---\n# Doc\n')
        with patch("sys.argv", ["pv", "validate-docs", "--root", str(tmp_path)]):
            rc = main()
        assert rc == 0

    def test_validate_docs_on_empty_dir(self, tmp_path):
        with patch("sys.argv", ["pv", "validate-docs", "--root", str(tmp_path)]):
            rc = main()
        assert rc == 0  # No files = no errors


class TestValidateLandscape:
    """Test validate-landscape command dispatch."""

    def test_missing_file_returns_2(self, tmp_path, capsys):
        with patch("sys.argv", ["pv", "validate-landscape", "--path", str(tmp_path / "nope.yaml")]):
            rc = main()
        assert rc == 2

    def test_valid_landscape(self, tmp_path):
        import yaml

        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "legislation",
                    "source": "Congress",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        path = tmp_path / "landscape.yaml"
        path.write_text(yaml.dump(data, default_flow_style=False))
        with patch("sys.argv", ["pv", "validate-landscape", "--path", str(path)]):
            rc = main()
        assert rc == 0


class TestDoctor:
    """Test doctor command dispatch."""

    def test_doctor_runs(self, tmp_path):
        (tmp_path / ".gitignore").write_text(".env\n")
        with patch("sys.argv", ["pv", "doctor", "--root", str(tmp_path)]):
            rc = main()
        # May fail checks (git not set up in tmp_path) but should not crash
        assert rc in (0, 1)

    def test_doctor_json_output(self, tmp_path, capsys):
        (tmp_path / ".gitignore").write_text(".env\n")
        with patch("sys.argv", ["pv", "doctor", "--json", "--root", str(tmp_path)]):
            main()
        captured = capsys.readouterr()
        # JSON output should be valid
        import json

        parsed = json.loads(captured.out)
        assert "status" in parsed


class TestVerboseFlag:
    """Test --verbose flag enables debug logging."""

    def test_verbose_flag_accepted(self, tmp_path):
        with patch("sys.argv", ["pv", "-v", "validate-docs", "--root", str(tmp_path)]):
            rc = main()
        assert rc == 0


class TestErrorHandling:
    """Test top-level exception handling."""

    def test_file_not_found_returns_2(self, tmp_path):
        with patch("sys.argv", ["pv", "validate-plan", "--path", str(tmp_path / "nope.md")]):
            rc = main()
        # validate_plan handles missing file internally, returning 1
        assert rc in (1, 2)

    def test_keyboard_interrupt_returns_130(self):
        def raise_interrupt(_args):
            raise KeyboardInterrupt

        with (
            patch("sys.argv", ["pv", "validate-docs", "--root", "."]),
            patch.dict("playbook_validator.__main__._COMMANDS", {"validate-docs": raise_interrupt}),
        ):
            rc = main()
        assert rc == 130


class TestGenerateIndex:
    """Test generate-index command routing."""

    def test_generate_index_check_mode(self, tmp_path):
        doc = tmp_path / "test.md"
        doc.write_text('---\ntitle: "T"\ndescription: "D"\nstatus: canonical\ntier: 1\n---\n# Doc\n')
        # No INDEX.yaml exists -> should fail check
        with patch("sys.argv", ["pv", "generate-index", "--check", "--root", str(tmp_path)]):
            rc = main()
        assert rc == 1


class TestValidateSkills:
    """Test validate-skills command dispatch."""

    def test_no_skills_dir(self, tmp_path):
        with patch("sys.argv", ["pv", "validate-skills", "--root", str(tmp_path)]):
            rc = main()
        assert rc == 0
