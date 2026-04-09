"""Tests for doctor module — environment readiness checks for AI coding agents."""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from playbook_validator.doctor import (
    _run_cmd,
    check_ai_keys,
    check_cloudgov,
    check_dependencies,
    check_git,
    check_github,
    check_gitlab,
    check_precommit_hooks,
    check_python_version,
    check_registries,
    check_security,
    detect_plan,
    plan_requires,
    run_doctor,
)


class TestDetectPlan:
    """Test plan file detection."""

    def test_auto_detect_project_plan(self, tmp_path: Path):
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text("# Plan\n- [x] Use GitHub\n")
        result = detect_plan(str(tmp_path))
        assert result == str(plan)

    def test_auto_detect_lowercase(self, tmp_path: Path):
        plan = tmp_path / "project-plan.md"
        plan.write_text("# Plan\n")
        result = detect_plan(str(tmp_path))
        assert result == str(plan)

    def test_auto_detect_docs_subdir(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        plan = docs / "PROJECT_PLAN.md"
        plan.write_text("# Plan\n")
        result = detect_plan(str(tmp_path))
        assert result == str(plan)

    def test_custom_path_valid(self, tmp_path: Path):
        custom = tmp_path / "my-plan.md"
        custom.write_text("# Custom\n")
        result = detect_plan(str(tmp_path), custom_path=str(custom))
        assert result == str(custom)

    def test_custom_path_missing_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            detect_plan(str(tmp_path), custom_path="/nonexistent/plan.md")

    def test_no_plan_returns_none(self, tmp_path: Path):
        result = detect_plan(str(tmp_path))
        assert result is None

    def test_priority_order(self, tmp_path: Path):
        """PROJECT_PLAN.md at root takes priority over docs/ version."""
        root_plan = tmp_path / "PROJECT_PLAN.md"
        root_plan.write_text("# Root plan\n")
        docs = tmp_path / "docs"
        docs.mkdir()
        docs_plan = docs / "PROJECT_PLAN.md"
        docs_plan.write_text("# Docs plan\n")
        result = detect_plan(str(tmp_path))
        assert result == str(root_plan)


class TestPlanRequires:
    """Test service requirement detection from plan checkboxes."""

    def test_checked_checkbox_matches(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("- [x] Deploy to GitHub Pages\n- [ ] Use GitLab\n")
        assert plan_requires("github", str(plan)) is True

    def test_unchecked_checkbox_no_match(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("- [ ] Deploy to GitHub Pages\n")
        assert plan_requires("github", str(plan)) is False

    def test_case_insensitive(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("- [x] Publish to NPM registry\n")
        assert plan_requires("npm", str(plan)) is True

    def test_no_plan_returns_true(self):
        """When no plan exists, assume service is needed."""
        assert plan_requires("github", None) is True

    def test_service_not_mentioned(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("- [x] Build frontend\n")
        assert plan_requires("cloud.gov", str(plan)) is False


class TestCheckGit:
    """Test git availability and remote checks."""

    @patch("shutil.which", return_value="/usr/bin/git")
    @patch("subprocess.run")
    def test_git_installed_with_remote(self, mock_run: MagicMock, mock_which: MagicMock):
        # First call: git --version
        version_result = MagicMock()
        version_result.returncode = 0
        version_result.stdout = "git version 2.43.0"
        # Second call: git remote get-url origin
        remote_result = MagicMock()
        remote_result.returncode = 0
        remote_result.stdout = "https://github.com/user/repo.git"
        mock_run.side_effect = [version_result, remote_result]

        results = check_git("/fake/repo")
        passed = [r for r in results if r["passed"]]
        assert len(passed) == 2
        assert any("github" in r.get("detail", "").lower() for r in passed)

    @patch("shutil.which", return_value=None)
    def test_git_not_installed(self, mock_which: MagicMock):
        results = check_git("/fake/repo")
        assert len(results) >= 1
        assert results[0]["passed"] is False
        assert "git" in results[0]["name"].lower()


class TestCheckGitHub:
    """Test GitHub CLI and token checks."""

    @patch("shutil.which", return_value="/usr/bin/gh")
    @patch("subprocess.run")
    def test_gh_authenticated(self, mock_run: MagicMock, mock_which: MagicMock):
        auth_result = MagicMock()
        auth_result.returncode = 0
        user_result = MagicMock()
        user_result.returncode = 0
        user_result.stdout = "testuser"
        mock_run.side_effect = [auth_result, user_result]

        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_TESTFAKE"}, clear=False):
            results = check_github(plan_path=None)
        passed_names = [r["name"] for r in results if r["passed"]]
        assert "gh CLI authenticated" in passed_names
        assert "GITHUB_TOKEN" in passed_names

    @patch("shutil.which", return_value=None)
    def test_gh_not_installed(self, mock_which: MagicMock):
        with patch.dict(os.environ, {}, clear=False):
            env = os.environ.copy()
            env.pop("GITHUB_TOKEN", None)
            with patch.dict(os.environ, env, clear=True):
                results = check_github(plan_path=None)
        failed = [r for r in results if not r["passed"]]
        assert len(failed) >= 1


class TestCheckCloudGov:
    """Test cloud.gov CLI checks."""

    @patch("shutil.which", return_value="/usr/bin/cf")
    @patch("subprocess.run")
    def test_cf_authenticated(self, mock_run: MagicMock, mock_which: MagicMock):
        target_result = MagicMock()
        target_result.returncode = 0
        target_result.stdout = "org: my-org\nspace: dev"
        mock_run.return_value = target_result

        results = check_cloudgov()
        passed = [r for r in results if r["passed"]]
        assert len(passed) >= 1

    @patch("shutil.which", return_value=None)
    def test_cf_not_installed(self, mock_which: MagicMock):
        results = check_cloudgov()
        failed = [r for r in results if not r["passed"]]
        assert len(failed) >= 1
        assert "cf CLI installed" in failed[0]["name"]


class TestCheckGitLab:
    """Test GitLab token and URL checks."""

    def test_gitlab_tokens_set(self):
        env = {"GITLAB_TOKEN": "glpat-TESTFAKE", "GITLAB_URL": "https://gitlab.example.com"}
        with patch.dict(os.environ, env, clear=False):
            results = check_gitlab()
        passed_names = [r["name"] for r in results if r["passed"]]
        assert "GITLAB_TOKEN" in passed_names
        assert "GITLAB_URL" in passed_names

    def test_gitlab_tokens_missing(self):
        env = os.environ.copy()
        env.pop("GITLAB_TOKEN", None)
        env.pop("GITLAB_URL", None)
        with patch.dict(os.environ, env, clear=True):
            results = check_gitlab()
        failed_names = [r["name"] for r in results if not r["passed"]]
        assert "GITLAB_TOKEN" in failed_names
        assert "GITLAB_URL" in failed_names


class TestCheckRegistries:
    """Test package registry token checks."""

    def test_npm_token_set(self):
        with patch.dict(os.environ, {"NPM_TOKEN": "npm_TESTFAKE"}, clear=False):
            results = check_registries(plan_path=None)
        passed_names = [r["name"] for r in results if r["passed"]]
        assert "NPM_TOKEN" in passed_names

    def test_pypi_token_set(self):
        with patch.dict(os.environ, {"PYPI_TOKEN": "pypi-TESTFAKE"}, clear=False):
            results = check_registries(plan_path=None)
        passed_names = [r["name"] for r in results if r["passed"]]
        assert "PYPI_TOKEN" in passed_names


class TestCheckAIKeys:
    """Test AI/LLM API key detection."""

    def test_anthropic_key_detected(self):
        env = os.environ.copy()
        for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_AI_API_KEY", "OPENROUTER_API_KEY"):
            env.pop(k, None)
        env["ANTHROPIC_API_KEY"] = "sk-ant-TESTFAKE"
        with patch.dict(os.environ, env, clear=True):
            results = check_ai_keys()
        passed_names = [r["name"] for r in results if r["passed"]]
        assert "ANTHROPIC_API_KEY" in passed_names

    def test_no_ai_keys(self):
        env = os.environ.copy()
        for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_AI_API_KEY", "OPENROUTER_API_KEY"):
            env.pop(k, None)
        with patch.dict(os.environ, env, clear=True):
            results = check_ai_keys()
        assert len(results) == 1
        assert results[0]["status"] == "skip"

    def test_multiple_keys(self):
        env = os.environ.copy()
        for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_AI_API_KEY", "OPENROUTER_API_KEY"):
            env.pop(k, None)
        env["ANTHROPIC_API_KEY"] = "sk-ant-TESTFAKE"
        env["OPENAI_API_KEY"] = "sk-TESTFAKE"
        with patch.dict(os.environ, env, clear=True):
            results = check_ai_keys()
        passed = [r for r in results if r["passed"]]
        assert len(passed) == 2


class TestCheckSecurity:
    """Test security file checks."""

    def test_gitignore_protects_env(self, tmp_path: Path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n.env\n.env.local\n")
        results = check_security(str(tmp_path))
        passed_names = [r["name"] for r in results if r["passed"]]
        assert ".gitignore" in passed_names

    def test_gitignore_missing_env(self, tmp_path: Path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        results = check_security(str(tmp_path))
        failed_names = [r["name"] for r in results if not r["passed"]]
        assert ".gitignore" in failed_names

    def test_no_gitignore(self, tmp_path: Path):
        results = check_security(str(tmp_path))
        failed_names = [r["name"] for r in results if not r["passed"]]
        assert ".gitignore" in failed_names

    def test_env_example_exists(self, tmp_path: Path):
        (tmp_path / ".gitignore").write_text(".env\n")
        (tmp_path / ".env.example").write_text("GITHUB_TOKEN=\n")
        results = check_security(str(tmp_path))
        passed_names = [r["name"] for r in results if r["passed"]]
        assert ".env.example" in passed_names


class TestRunDoctor:
    """Test the full run_doctor orchestrator."""

    @patch("shutil.which", return_value="/usr/bin/git")
    @patch("subprocess.run")
    def test_returns_result_collector(self, mock_run: MagicMock, mock_which: MagicMock, tmp_path: Path):
        # Stub all subprocess.run calls to succeed
        success = MagicMock()
        success.returncode = 0
        success.stdout = "git version 2.43.0"
        mock_run.return_value = success

        (tmp_path / ".gitignore").write_text(".env\n")

        rc = run_doctor(str(tmp_path))
        result = rc.to_dict()
        assert "status" in result
        assert "checks_passed" in result
        assert "checks_failed" in result
        assert "results" in result

    @patch("playbook_validator.doctor.shutil.which", return_value="/usr/bin/git")
    @patch("playbook_validator.doctor.subprocess.run")
    def test_exit_code_zero_all_pass(self, mock_run: MagicMock, mock_which: MagicMock, tmp_path: Path):
        success = MagicMock()
        success.returncode = 0
        success.stdout = "git version 2.43.0"
        mock_run.return_value = success

        (tmp_path / ".gitignore").write_text(".env\n")
        (tmp_path / ".env.example").write_text("TOKEN=\n")

        # Create pre-commit hooks file so that check passes
        hooks_dir = tmp_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "pre-commit").write_text("#!/bin/sh\nexec pre-commit run\n")

        # Create a plan that only requires github (so gitlab/cloudgov/npm/pypi skip)
        plan = tmp_path / "PROJECT_PLAN.md"
        plan.write_text("- [x] Use GitHub\n")

        env = {
            "ANTHROPIC_API_KEY": "sk-ant-TESTFAKE",
            "GITHUB_TOKEN": "ghp_TESTFAKE",
        }
        with patch.dict(os.environ, env, clear=True):
            rc = run_doctor(str(tmp_path))
        # No failures means exit_code 0
        assert rc.exit_code == 0

    @patch("shutil.which", return_value=None)
    def test_exit_code_one_on_failure(self, mock_which: MagicMock, tmp_path: Path):
        rc = run_doctor(str(tmp_path))
        assert rc.exit_code == 1

    def test_json_output_valid(self, tmp_path: Path):
        """JSON output is valid and has expected structure."""
        (tmp_path / ".gitignore").write_text(".env\n")
        with patch("shutil.which", return_value=None):
            rc = run_doctor(str(tmp_path))
        import json

        json_str = rc.to_json()
        parsed = json.loads(json_str)
        assert "status" in parsed
        assert isinstance(parsed["results"], list)


class TestCheckPythonVersion:
    """Test Python version check."""

    def test_current_python_passes(self):
        results = check_python_version()
        assert len(results) == 1
        # We're running on >=3.12, so it should pass
        assert results[0]["passed"] is True

    def test_old_python_fails(self):
        fake_version = MagicMock(major=3, minor=10, micro=0)
        with patch("playbook_validator.doctor.sys") as mock_sys:
            mock_sys.version_info = fake_version
            results = check_python_version()
        assert len(results) == 1
        assert results[0]["passed"] is False
        assert "3.12" in str(results[0].get("detail", ""))


class TestCheckDependencies:
    """Test dependency availability checks."""

    def test_yaml_available(self):
        """PyYAML should be available in the test environment."""
        results = check_dependencies()
        yaml_results = [r for r in results if r["name"] == "PyYAML"]
        assert len(yaml_results) == 1
        assert yaml_results[0]["passed"] is True

    @patch("shutil.which", return_value=None)
    def test_missing_tool_skips(self, mock_which):
        results = check_dependencies()
        ruff_results = [r for r in results if r["name"] == "ruff"]
        assert len(ruff_results) == 1
        # Missing tool returns a skip (passed=True with status=skip)
        assert ruff_results[0]["passed"] is True
        assert ruff_results[0].get("status") == "skip"


class TestCheckPrecommitHooks:
    """Test pre-commit hook installation check."""

    def test_hooks_installed(self, tmp_path: Path):
        hooks_dir = tmp_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True)
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\n# pre-commit hook\nexec pre-commit run\n")
        results = check_precommit_hooks(str(tmp_path))
        assert results[0]["passed"] is True

    def test_hooks_not_installed(self, tmp_path: Path):
        results = check_precommit_hooks(str(tmp_path))
        assert results[0]["passed"] is False

    def test_hooks_file_without_precommit(self, tmp_path: Path):
        hooks_dir = tmp_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True)
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\necho hello\n")
        results = check_precommit_hooks(str(tmp_path))
        assert results[0]["passed"] is False


class TestRunCmdTimeout:
    """Test that _run_cmd handles subprocess timeouts gracefully."""

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=10))
    def test_timeout_returns_failed_result(self, mock_run):
        result = _run_cmd("test-cmd")
        assert result.returncode == 1
        assert "timed out" in result.stderr
