"""Repository audit — federal compliance baseline checks.

Checks git init, .gitignore secret patterns, pre-commit secrets hooks,
.env not committed, CI/CD pipeline, AGENTS.md, and lock file presence.
"""

import re
import subprocess
from pathlib import Path

from playbook_validator.config import LOCK_FILES
from playbook_validator.output import ResultCollector

# Patterns that must appear in .gitignore for federal compliance
REQUIRED_GITIGNORE_PATTERNS = [".env", "*.key", "*.pem", "credentials.*"]

# Secrets scanning hooks recognized in .pre-commit-config.yaml
SECRETS_HOOK_PATTERN = re.compile(r"(gitleaks|detect-secrets|trufflehog)")

# Acceptable agent configuration files (checked in order)
AGENTS_FILES = ["AGENTS.md", "CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md"]

AUDIT_FILE = "repo"


def check_git_init(repo: Path, rc: ResultCollector) -> None:
    """Check 1: .git directory exists."""
    if (repo / ".git").is_dir():
        rc.add_result(AUDIT_FILE, "git-repo", passed=True)
    else:
        rc.add_result(
            AUDIT_FILE,
            "git-repo",
            passed=False,
            note=f"Initialize git: cd {repo} && git init",
        )


def check_gitignore(repo: Path, rc: ResultCollector) -> None:
    """Check 2: .gitignore exists with federal-required secret patterns."""
    gitignore = repo / ".gitignore"
    if not gitignore.is_file():
        rc.add_result(
            AUDIT_FILE, "gitignore-exists", passed=False, note="Create .gitignore with federal security patterns"
        )
        rc.add_result(AUDIT_FILE, "gitignore-secrets-patterns", passed=False, note="Create .gitignore first")
        return

    rc.add_result(AUDIT_FILE, "gitignore-exists", passed=True)

    content = gitignore.read_text(encoding="utf-8")
    missing = [p for p in REQUIRED_GITIGNORE_PATTERNS if p not in content]

    if not missing:
        rc.add_result(AUDIT_FILE, "gitignore-secrets-patterns", passed=True)
    else:
        rc.add_result(
            AUDIT_FILE,
            "gitignore-secrets-patterns",
            passed=False,
            note=f"Add missing patterns to .gitignore: {' '.join(missing)}",
        )


def check_precommit(repo: Path, rc: ResultCollector) -> None:
    """Check 3: .pre-commit-config.yaml exists with secrets scanning hook."""
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        rc.add_result(
            AUDIT_FILE,
            "pre-commit-config",
            passed=False,
            note="Create .pre-commit-config.yaml with secrets scanning hook",
        )
        rc.add_result(AUDIT_FILE, "secrets-scanner-hook", passed=False, note="Create .pre-commit-config.yaml first")
        return

    rc.add_result(AUDIT_FILE, "pre-commit-config", passed=True)

    content = config.read_text(encoding="utf-8")
    if SECRETS_HOOK_PATTERN.search(content):
        rc.add_result(AUDIT_FILE, "secrets-scanner-hook", passed=True)
    else:
        rc.add_result(
            AUDIT_FILE,
            "secrets-scanner-hook",
            passed=False,
            note="Add gitleaks or detect-secrets to .pre-commit-config.yaml",
        )


def check_env_not_committed(repo: Path, rc: ResultCollector) -> None:
    """Check 4: .env is not tracked by git."""
    if not (repo / ".git").is_dir():
        return  # Skip if not a git repo

    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--error-unmatch", ".env"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            # .env IS tracked — fail
            rc.add_result(
                AUDIT_FILE, "env-not-committed", passed=False, note="Remove .env from git: git rm --cached .env"
            )
            rc.add_error("CRITICAL: .env file is tracked by git. Secrets may be exposed in history.")
        else:
            rc.add_result(AUDIT_FILE, "env-not-committed", passed=True)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        rc.add_result(AUDIT_FILE, "env-not-committed", passed=True)


def check_ci_pipeline(repo: Path, rc: ResultCollector) -> None:
    """Check 5: CI/CD pipeline exists (GitHub Actions, GitLab CI, or Jenkinsfile)."""
    workflows = repo / ".github" / "workflows"
    has_ci = (
        (workflows.is_dir() and any(workflows.iterdir()))
        or (repo / ".gitlab-ci.yml").is_file()
        or (repo / "Jenkinsfile").is_file()
    )

    if has_ci:
        rc.add_result(AUDIT_FILE, "ci-pipeline", passed=True)
    else:
        rc.add_result(AUDIT_FILE, "ci-pipeline", passed=False, note="Create a CI/CD pipeline with security stages")


def check_agents_md(repo: Path, rc: ResultCollector) -> None:
    """Check 6: AGENTS.md or equivalent agent config exists."""
    for agents_file in AGENTS_FILES:
        if (repo / agents_file).is_file():
            rc.add_result(AUDIT_FILE, "agents-config", passed=True)
            return

    rc.add_result(AUDIT_FILE, "agents-config", passed=False, note="Create AGENTS.md with federal compliance rules")


def _is_git_tracked(repo: Path, name: str) -> bool:
    """True if `name` is tracked by git in `repo`. A lock file that exists on
    disk but is untracked (e.g. hidden by a global gitignore) does NOT satisfy
    "commit them" (§7.1) — the check must verify tracking, not mere presence
    (#259)."""
    if not (repo / ".git").is_dir():
        # Not a git repo (or a worktree without .git dir here) — fall back to
        # on-disk presence so non-git consumers aren't penalized.
        return (repo / name).is_file()
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--error-unmatch", name],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # git unavailable — fall back to on-disk presence rather than failing hard.
        return (repo / name).is_file()


def check_lock_file(repo: Path, rc: ResultCollector) -> None:
    """Check 7: A dependency lock file is present AND git-tracked (#259)."""
    for lock_file in LOCK_FILES:
        if _is_git_tracked(repo, lock_file):
            rc.add_result(AUDIT_FILE, "lock-file", passed=True)
            return
        if (repo / lock_file).is_file():
            # Present but untracked — the exact gap #259 hit (uv.lock hidden by a
            # global gitignore). Surface it rather than passing on presence alone.
            rc.add_warning(
                f"Dependency lock file '{lock_file}' exists but is not git-tracked. "
                f"Commit it for reproducible builds: git add -f {lock_file}"
            )
            return

    rc.add_warning("No dependency lock file found. Commit a lock file for reproducible builds.")


def audit_repo(repo_path: Path) -> ResultCollector:
    """Run all repo audit checks and return a ResultCollector."""
    rc = ResultCollector()
    check_git_init(repo_path, rc)
    check_gitignore(repo_path, rc)
    check_precommit(repo_path, rc)
    check_env_not_committed(repo_path, rc)
    check_ci_pipeline(repo_path, rc)
    check_agents_md(repo_path, rc)
    check_lock_file(repo_path, rc)
    return rc
