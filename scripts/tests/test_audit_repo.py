"""Tests for repository audit module — federal compliance baseline checks."""

import os
import subprocess

from playbook_validator.audit_repo import (
    audit_repo,
    check_agents_md,
    check_ci_pipeline,
    check_env_not_committed,
    check_git_init,
    check_gitignore,
    check_lock_file,
    check_precommit,
)
from playbook_validator.output import ResultCollector


def _git_init(path):
    """Initialize a git repo at the given path."""
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)


class TestCheckGitInit:
    """Check 1: .git directory exists."""

    def test_pass_when_git_dir_exists(self, tmp_path):
        _git_init(tmp_path)
        rc = ResultCollector()
        check_git_init(tmp_path, rc)
        assert rc.checks_passed == 1
        assert rc.checks_failed == 0

    def test_fail_when_no_git_dir(self, tmp_path):
        rc = ResultCollector()
        check_git_init(tmp_path, rc)
        assert rc.checks_passed == 0
        assert rc.checks_failed == 1


class TestCheckGitignore:
    """Check 2: .gitignore exists with secret patterns."""

    def test_pass_with_all_patterns(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".env\n*.key\n*.pem\ncredentials.*\n")
        rc = ResultCollector()
        check_gitignore(tmp_path, rc)
        assert rc.checks_passed == 2  # gitignore-exists + gitignore-secrets-patterns
        assert rc.checks_failed == 0

    def test_fail_missing_patterns(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".env\n")
        rc = ResultCollector()
        check_gitignore(tmp_path, rc)
        assert rc.checks_passed == 1  # gitignore-exists passes
        assert rc.checks_failed == 1  # secrets-patterns fails

    def test_fail_no_gitignore(self, tmp_path):
        rc = ResultCollector()
        check_gitignore(tmp_path, rc)
        assert rc.checks_failed == 2  # both checks fail


class TestCheckPrecommit:
    """Check 3: .pre-commit-config.yaml with secrets scanning hook."""

    def test_pass_with_gitleaks(self, tmp_path):
        cfg = tmp_path / ".pre-commit-config.yaml"
        cfg.write_text("repos:\n  - repo: https://github.com/gitleaks/gitleaks\n")
        rc = ResultCollector()
        check_precommit(tmp_path, rc)
        assert rc.checks_passed == 2  # config exists + secrets hook
        assert rc.checks_failed == 0

    def test_pass_with_detect_secrets(self, tmp_path):
        cfg = tmp_path / ".pre-commit-config.yaml"
        cfg.write_text("repos:\n  - repo: https://github.com/Yelp/detect-secrets\n")
        rc = ResultCollector()
        check_precommit(tmp_path, rc)
        assert rc.checks_passed == 2

    def test_fail_no_secrets_hook(self, tmp_path):
        cfg = tmp_path / ".pre-commit-config.yaml"
        cfg.write_text("repos:\n  - repo: https://github.com/pre-commit/mirrors-prettier\n")
        rc = ResultCollector()
        check_precommit(tmp_path, rc)
        assert rc.checks_passed == 1  # config exists
        assert rc.checks_failed == 1  # no secrets hook

    def test_fail_no_config(self, tmp_path):
        rc = ResultCollector()
        check_precommit(tmp_path, rc)
        assert rc.checks_failed == 2


class TestCheckEnvNotCommitted:
    """Check 4: .env is not tracked by git."""

    def test_pass_env_not_tracked(self, tmp_path):
        _git_init(tmp_path)
        rc = ResultCollector()
        check_env_not_committed(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_env_tracked(self, tmp_path):
        _git_init(tmp_path)
        env_file = tmp_path / ".env"
        env_file.write_text("SECRET=oops\n")
        subprocess.run(
            ["git", "-C", str(tmp_path), "add", ".env"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(tmp_path), "commit", "-m", "add env", "--no-gpg-sign"],
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "test",
                "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "test",
                "GIT_COMMITTER_EMAIL": "t@t",
            },
        )
        rc = ResultCollector()
        check_env_not_committed(tmp_path, rc)
        assert rc.checks_failed == 1

    def test_skip_when_not_git_repo(self, tmp_path):
        rc = ResultCollector()
        check_env_not_committed(tmp_path, rc)
        # No result added when not a git repo
        assert rc.checks_passed == 0
        assert rc.checks_failed == 0


class TestCheckCiPipeline:
    """Check 5: CI/CD pipeline presence."""

    def test_pass_github_actions(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("name: CI\n")
        rc = ResultCollector()
        check_ci_pipeline(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_pass_gitlab_ci(self, tmp_path):
        (tmp_path / ".gitlab-ci.yml").write_text("stages:\n  - test\n")
        rc = ResultCollector()
        check_ci_pipeline(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_no_ci(self, tmp_path):
        rc = ResultCollector()
        check_ci_pipeline(tmp_path, rc)
        assert rc.checks_failed == 1


class TestCheckAgentsMd:
    """Check 6: AGENTS.md or equivalent exists."""

    def test_pass_agents_md(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# Agents\n")
        rc = ResultCollector()
        check_agents_md(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_pass_agent_config(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# Agent Config\n")
        rc = ResultCollector()
        check_agents_md(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_fail_no_agents_file(self, tmp_path):
        rc = ResultCollector()
        check_agents_md(tmp_path, rc)
        assert rc.checks_failed == 1


class TestCheckLockFile:
    """Check 7: Dependency lock file present."""

    def test_pass_package_lock(self, tmp_path):
        (tmp_path / "package-lock.json").write_text("{}\n")
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_pass_poetry_lock(self, tmp_path):
        (tmp_path / "poetry.lock").write_text("[metadata]\n")
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        assert rc.checks_passed == 1

    def test_warn_no_lock_file(self, tmp_path):
        rc = ResultCollector()
        check_lock_file(tmp_path, rc)
        # Lock file is a warning, not a hard fail
        assert rc.checks_passed == 0
        assert rc.checks_failed == 0
        d = rc.to_dict()
        assert len(d["warnings"]) == 1


class TestAuditRepo:
    """Integration: audit_repo runs all checks and returns ResultCollector."""

    def test_fully_compliant_repo(self, tmp_path):
        _git_init(tmp_path)
        (tmp_path / ".gitignore").write_text(".env\n*.key\n*.pem\ncredentials.*\n")
        precommit = tmp_path / ".pre-commit-config.yaml"
        precommit.write_text("repos:\n  - repo: https://github.com/gitleaks/gitleaks\n")
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("name: CI\n")
        (tmp_path / "AGENTS.md").write_text("# Agents\n")
        (tmp_path / "package-lock.json").write_text("{}\n")

        rc = audit_repo(tmp_path)
        assert isinstance(rc, ResultCollector)
        assert rc.checks_failed == 0
        assert rc.status == "success"
        assert rc.exit_code == 0

    def test_empty_dir_has_failures(self, tmp_path):
        rc = audit_repo(tmp_path)
        assert rc.checks_failed > 0
        assert rc.status in ("partial", "failure")
        assert rc.exit_code == 1

    def test_output_format(self, tmp_path):
        _git_init(tmp_path)
        rc = audit_repo(tmp_path)
        d = rc.to_dict()
        assert "status" in d
        assert "checks_passed" in d
        assert "checks_failed" in d
        assert "results" in d
        assert "warnings" in d
        assert "errors" in d
        # Each result has required keys
        for r in d["results"]:
            assert "file" in r
            assert "check" in r
            assert "pass" in r
