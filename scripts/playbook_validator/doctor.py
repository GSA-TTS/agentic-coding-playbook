"""Environment readiness checks for AI coding agents.

Python equivalent of agent-doctor.sh. Detects available credentials,
diagnoses gaps against PROJECT_PLAN.md, and reports actionable fixes.
"""

import importlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from playbook_validator.output import ResultCollector

# Candidate plan file locations (relative to repo root), in priority order.
_PLAN_CANDIDATES = [
    "PROJECT_PLAN.md",
    "project-plan.md",
    "docs/PROJECT_PLAN.md",
]

# AI/LLM API key environment variable names to check.
_AI_KEY_VARS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GOOGLE_AI_API_KEY",
    "OPENROUTER_API_KEY",
]


def detect_plan(repo_root: str, custom_path: str | None = None) -> str | None:
    """Find the PROJECT_PLAN.md file.

    Args:
        repo_root: Repository root directory.
        custom_path: Explicit path to a plan file. If provided and missing,
            raises FileNotFoundError.

    Returns:
        Absolute path to the plan file, or None if not found.
    """
    if custom_path is not None:
        if not Path(custom_path).is_file():
            raise FileNotFoundError(f"Plan file not found: {custom_path}")
        return custom_path

    root = Path(repo_root)
    for candidate in _PLAN_CANDIDATES:
        path = root / candidate
        if path.is_file():
            return str(path)
    return None


def plan_requires(service: str, plan_path: str | None) -> bool:
    """Check if a service is required by the project plan.

    Looks for checked checkboxes (``- [x]``) containing the service name
    (case-insensitive). When no plan exists, returns True (assume needed).
    """
    if plan_path is None:
        return True
    try:
        text = Path(plan_path).read_text(encoding="utf-8")
    except OSError:
        return True
    pattern = re.compile(r"^\s*-\s*\[x\].*" + re.escape(service), re.IGNORECASE | re.MULTILINE)
    return bool(pattern.search(text))


def _run_cmd(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and capture output, suppressing errors."""
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, returncode=1, stdout="", stderr="timed out after 10s")


def _result(name: str, passed: bool, detail: str = "", status: str = "") -> dict[str, object]:
    """Build a check result dict."""
    d: dict[str, object] = {"name": name, "passed": passed}
    if detail:
        d["detail"] = detail
    if status:
        d["status"] = status
    return d


def _skip(name: str, reason: str = "not required") -> dict[str, object]:
    return {"name": name, "passed": True, "status": "skip", "detail": reason}


# ── Individual check functions ──────────────────────────────────────


def check_git(repo_root: str) -> list[dict[str, object]]:
    """Check git installation and remote URL."""
    results: list[dict[str, object]] = []

    if shutil.which("git") is None:
        results.append(_result("git", False, "Install git: https://git-scm.com/downloads"))
        return results

    proc = _run_cmd("git", "--version")
    if proc.returncode == 0:
        results.append(_result("git", True, proc.stdout.strip()))
    else:
        results.append(_result("git", False, "git --version failed"))
        return results

    proc = _run_cmd("git", "-C", repo_root, "remote", "get-url", "origin")
    if proc.returncode == 0:
        url = proc.stdout.strip()
        if "github.com" in url:
            detail = f"GitHub -- {url}"
        elif "gitlab" in url or "workshop.cloud.gov" in url:
            detail = f"GitLab -- {url}"
        else:
            detail = url
        results.append(_result("git remote", True, detail))
    else:
        results.append(_result("git remote", False, "Run: git remote add origin <your-repo-url>"))

    return results


def check_github(plan_path: str | None = None) -> list[dict[str, object]]:
    """Check GitHub CLI auth and GITHUB_TOKEN."""
    if not plan_requires("github", plan_path) and plan_path is not None:
        return [_skip("GitHub", "not required per PROJECT_PLAN.md")]

    results: list[dict[str, object]] = []

    gh_authed = False
    if shutil.which("gh") is not None:
        proc = _run_cmd("gh", "auth", "status")
        if proc.returncode == 0:
            gh_authed = True
            user_proc = _run_cmd("gh", "api", "user", "--jq", ".login")
            user = user_proc.stdout.strip() if user_proc.returncode == 0 else "unknown"
            results.append(_result("gh CLI authenticated", True, f"user: {user}"))
        else:
            results.append(_result("gh CLI authenticated", False, "Run: gh auth login"))
    else:
        results.append(_result("gh CLI installed", False, "Install: https://cli.github.com/"))

    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        results.append(_result("GITHUB_TOKEN", True, "set (value hidden)"))
    elif gh_authed:
        results.append(_result("GITHUB_TOKEN", True, "not set, but gh CLI is authenticated"))
    else:
        results.append(_result("GITHUB_TOKEN", False, "Run: export GITHUB_TOKEN=github_pat_YOUR_TOKEN"))

    return results


def check_cloudgov(plan_path: str | None = None) -> list[dict[str, object]]:
    """Check cloud.gov CF CLI auth."""
    if not plan_requires("cloud.gov", plan_path) and plan_path is not None:
        return [_skip("cloud.gov", "not required per PROJECT_PLAN.md")]

    results: list[dict[str, object]] = []

    if shutil.which("cf") is not None:
        proc = _run_cmd("cf", "target")
        if proc.returncode == 0:
            results.append(_result("cf CLI authenticated", True, proc.stdout.strip()))
        else:
            results.append(_result("cf CLI authenticated", False, "Run: cf login -a api.fr.cloud.gov --sso"))
    else:
        results.append(_result("cf CLI installed", False, "Install: https://docs.cloud.gov/getting-started/setup/"))

    cf_user = os.environ.get("CF_USERNAME", "")
    cf_pass = os.environ.get("CF_PASSWORD", "")
    if cf_user and cf_pass:
        results.append(_result("cloud.gov CI credentials", True, "CF_USERNAME and CF_PASSWORD set"))
    else:
        results.append(_skip("cloud.gov CI credentials", "set CF_USERNAME + CF_PASSWORD for CI/CD deployment"))

    return results


def check_gitlab(plan_path: str | None = None) -> list[dict[str, object]]:
    """Check GitLab token and URL."""
    gitlab_required = plan_requires("gitlab", plan_path) or plan_requires("workshop.cloud.gov", plan_path)
    if not gitlab_required and plan_path is not None:
        return [_skip("GitLab", "not required per PROJECT_PLAN.md")]

    results: list[dict[str, object]] = []

    if os.environ.get("GITLAB_TOKEN", ""):
        results.append(_result("GITLAB_TOKEN", True, "set (value hidden)"))
    else:
        results.append(_result("GITLAB_TOKEN", False, "Run: export GITLAB_TOKEN=glpat-YOUR_TOKEN"))

    gitlab_url = os.environ.get("GITLAB_URL", "")
    if gitlab_url:
        results.append(_result("GITLAB_URL", True, gitlab_url))
    else:
        results.append(_result("GITLAB_URL", False, "Run: export GITLAB_URL=https://your-instance.workshop.cloud.gov"))

    return results


def check_registries(plan_path: str | None = None) -> list[dict[str, object]]:
    """Check NPM and PyPI registry tokens."""
    results: list[dict[str, object]] = []

    if plan_requires("npm", plan_path):
        if os.environ.get("NPM_TOKEN", ""):
            results.append(_result("NPM_TOKEN", True, "set (value hidden)"))
        else:
            results.append(_result("NPM_TOKEN", False, "Run: export NPM_TOKEN=npm_YOUR_TOKEN"))
    else:
        results.append(_skip("npm registry", "not required per PROJECT_PLAN.md"))

    if plan_requires("pypi", plan_path):
        if os.environ.get("PYPI_TOKEN", ""):
            results.append(_result("PYPI_TOKEN", True, "set (value hidden)"))
        else:
            results.append(_result("PYPI_TOKEN", False, "Run: export PYPI_TOKEN=pypi-YOUR_TOKEN"))
    else:
        results.append(_skip("PyPI", "not required per PROJECT_PLAN.md"))

    return results


def check_ai_keys() -> list[dict[str, object]]:
    """Check AI/LLM API key environment variables."""
    results: list[dict[str, object]] = []

    for var in _AI_KEY_VARS:
        if os.environ.get(var, ""):
            results.append(_result(var, True, "set (value hidden)"))

    if not results:
        results.append(_skip("AI API keys", "none detected -- set at least one if agent needs LLM access"))

    return results


def check_security(repo_root: str) -> list[dict[str, object]]:
    """Check .gitignore and .env.example."""
    results: list[dict[str, object]] = []
    root = Path(repo_root)

    gitignore = root / ".gitignore"
    if gitignore.is_file():
        content = gitignore.read_text(encoding="utf-8")
        if re.search(r"\.env($|\s|\.local)", content, re.MULTILINE):
            results.append(_result(".gitignore", True, ".env is protected"))
        else:
            results.append(_result(".gitignore", False, "Add .env and .env.local to .gitignore"))
    else:
        results.append(_result(".gitignore", False, "Create .gitignore with .env, .env.local, *.pem, *.key"))

    env_example = root / ".env.example"
    if env_example.is_file():
        results.append(_result(".env.example", True, "template exists for team onboarding"))
    else:
        results.append(_skip(".env.example", "create one to document required env vars for your team"))

    return results


def check_python_version() -> list[dict[str, object]]:
    """Check that the running Python version meets the minimum requirement (>=3.12)."""
    vi = sys.version_info
    version = f"{vi.major}.{vi.minor}.{vi.micro}"
    if (vi.major, vi.minor) >= (3, 12):
        return [_result("Python version", True, version)]
    return [_result("Python version", False, f"{version} — requires >=3.12")]


def check_dependencies() -> list[dict[str, object]]:
    """Check that required Python packages and dev tools are available."""
    results: list[dict[str, object]] = []

    # PyYAML — hard runtime dependency
    try:
        importlib.import_module("yaml")
        results.append(_result("PyYAML", True, "installed"))
    except ImportError:
        results.append(_result("PyYAML", False, "Run: pip install PyYAML"))

    # ruff — Python linter/formatter
    if shutil.which("ruff") is not None:
        results.append(_result("ruff", True, "installed"))
    else:
        results.append(_skip("ruff", "not found — install with: pip install ruff"))

    # markdownlint-cli2 — Markdown linter (used by pre-commit)
    if shutil.which("markdownlint-cli2") is not None:
        results.append(_result("markdownlint-cli2", True, "installed"))
    else:
        results.append(_skip("markdownlint-cli2", "not found — install with: npm install -g markdownlint-cli2"))

    return results


def check_precommit_hooks(repo_root: str) -> list[dict[str, object]]:
    """Check if pre-commit hooks are installed in the repo."""
    hook = Path(repo_root) / ".git" / "hooks" / "pre-commit"
    if hook.is_file():
        content = hook.read_text(errors="replace")
        if "pre-commit" in content:
            return [_result("pre-commit hooks", True, "installed")]
    return [_result("pre-commit hooks", False, "Run: pre-commit install (or make install-hooks)")]


# ── Orchestrator ────────────────────────────────────────────────────


def run_doctor(repo_root: str, plan_path: str | None = None) -> ResultCollector:
    """Run all environment checks and return a ResultCollector.

    Args:
        repo_root: Repository root directory.
        plan_path: Optional explicit path to PROJECT_PLAN.md.

    Returns:
        A ResultCollector with all check results.
    """
    rc = ResultCollector()
    detected_plan = detect_plan(repo_root, custom_path=plan_path)

    all_checks: list[dict[str, object]] = []
    all_checks.extend(check_python_version())
    all_checks.extend(check_dependencies())
    all_checks.extend(check_precommit_hooks(repo_root))
    all_checks.extend(check_git(repo_root))
    all_checks.extend(check_github(plan_path=detected_plan))
    all_checks.extend(check_cloudgov(plan_path=detected_plan))
    all_checks.extend(check_gitlab(plan_path=detected_plan))
    all_checks.extend(check_registries(plan_path=detected_plan))
    all_checks.extend(check_ai_keys())
    all_checks.extend(check_security(repo_root))

    for check in all_checks:
        name = str(check["name"])
        passed = bool(check["passed"])
        detail = str(check.get("detail", "")) or None
        rc.add_result("env", name, passed=passed, note=detail)

    return rc
