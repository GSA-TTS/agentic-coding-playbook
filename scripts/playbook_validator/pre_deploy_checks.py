"""Pre-deployment security checks — Python equivalent of run-checks.sh.

Scans a repository for hardcoded secrets, SQL injection patterns, unsafe API
usage, floating dependency versions, missing lock files, empty catch blocks,
and CI security tooling (SAST/SCA).  Returns results via ResultCollector.

Policy reference: checklists/pre-deployment.md
"""

import re
from pathlib import Path

from playbook_validator.config import LOCK_FILES
from playbook_validator.output import ResultCollector

# ── File extensions to scan per check category ───────────────────────────

SOURCE_EXTS = {".py", ".js", ".ts", ".go", ".java", ".jsx", ".tsx"}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".env"}
ALL_EXTS = SOURCE_EXTS | CONFIG_EXTS

# Directories always excluded from scanning
EXCLUDED_DIRS = {".git", "node_modules", ".venv", "__pycache__", "venv"}

AUDIT_FILE = "pre-deploy"

# ── Patterns ─────────────────────────────────────────────────────────────

SECRET_PATTERN = re.compile(
    r"(password|secret|api_key|apikey|token|private_key)"
    r"\s*[:=]\s*[\"'][^\"']{8,}",
    re.IGNORECASE,
)

SQL_CONCAT_PATTERN = re.compile(
    r"(execute|query|cursor\.)\s*\(\s*[\"'].*(%s|\+|\.format|f[\"'])",
    re.IGNORECASE,
)

UNSAFE_API_PATTERN = re.compile(
    r"(eval\s*\(|innerHTML\s*=|dangerouslySetInnerHTML|exec\s*\(|os\.system\s*\()",
)

EMPTY_CATCH_PATTERN = re.compile(
    r"catch\s*\([^)]*\)\s*\{\s*\}|except\s*:\s*\n\s*pass",
)

CRYPTO_KEY_PATTERN = re.compile(
    r"(BEGIN (RSA |DSA |EC )?PRIVATE KEY|AAAA[A-Za-z0-9+/]{40,})",
)

SAST_TOOLS = re.compile(r"(semgrep|bandit|gosec|spotbugs|security-code-scan|codeql)")
SCA_TOOLS = re.compile(r"(npm audit|pip-audit|safety|snyk|trivy|dependency-check|govulncheck|cargo-audit)")


# ── Helpers ──────────────────────────────────────────────────────────────


def _iter_files(repo: Path, extensions: set[str]) -> list[Path]:
    """Yield files matching *extensions*, skipping excluded directories."""
    results: list[Path] = []
    for path in repo.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in extensions:
            results.append(path)
    return results


def _scan_files(repo: Path, pattern: re.Pattern[str], extensions: set[str]) -> list[Path]:
    """Return files whose content matches *pattern*."""
    hits: list[Path] = []
    for path in _iter_files(repo, extensions):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if pattern.search(text):
            hits.append(path)
    return hits


# ── Individual checks ────────────────────────────────────────────────────


def check_secrets(repo: Path, rc: ResultCollector) -> None:
    """2.1: No hardcoded secrets in source or config files."""
    hits = _scan_files(repo, SECRET_PATTERN, ALL_EXTS)
    if hits:
        rc.add_result(
            AUDIT_FILE,
            "No secrets in source code",
            passed=False,
            note=f"Potential secrets in {len(hits)} file(s)",
        )
    else:
        rc.add_result(AUDIT_FILE, "No secrets in source code", passed=True)


def check_sql_injection(repo: Path, rc: ResultCollector) -> None:
    """3.2: No string-concatenated SQL queries."""
    hits = _scan_files(repo, SQL_CONCAT_PATTERN, SOURCE_EXTS)
    if hits:
        rc.add_result(
            AUDIT_FILE,
            "No string-concatenated SQL",
            passed=False,
            note=f"Potential SQL injection in {len(hits)} file(s)",
        )
    else:
        rc.add_result(AUDIT_FILE, "No string-concatenated SQL", passed=True)


def check_unsafe_apis(repo: Path, rc: ResultCollector) -> None:
    """3.5: No eval/innerHTML/exec with untrusted data."""
    hits = _scan_files(repo, UNSAFE_API_PATTERN, SOURCE_EXTS)
    if hits:
        rc.add_result(
            AUDIT_FILE,
            "No unsafe APIs (eval/innerHTML/exec)",
            passed=False,
            note=f"Unsafe API usage in {len(hits)} file(s)",
        )
    else:
        rc.add_result(AUDIT_FILE, "No unsafe APIs (eval/innerHTML/exec)", passed=True)


def check_dependency_pinning(repo: Path, rc: ResultCollector) -> None:
    """5.1: Dependencies pinned to exact versions (no ^ or ~ ranges)."""
    pkg_json = repo / "package.json"
    requirements = repo / "requirements.txt"

    if pkg_json.is_file():
        text = pkg_json.read_text(errors="ignore")
        if re.search(r'"\^|"~', text):
            rc.add_result(
                AUDIT_FILE,
                "Dependencies pinned to exact versions",
                passed=False,
                note="Found floating version ranges in package.json",
            )
        else:
            rc.add_result(AUDIT_FILE, "Dependencies pinned to exact versions", passed=True)
    elif requirements.is_file():
        text = requirements.read_text(errors="ignore")
        # All non-comment, non-empty lines should use ==
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        unpinned = [ln for ln in lines if "==" not in ln]
        if unpinned:
            rc.add_result(
                AUDIT_FILE,
                "Dependencies pinned to exact versions",
                passed=False,
                note="Found unpinned dependencies in requirements.txt",
            )
        else:
            rc.add_result(AUDIT_FILE, "Dependencies pinned to exact versions", passed=True)
    elif (repo / "pyproject.toml").is_file():
        text = (repo / "pyproject.toml").read_text(errors="ignore")
        # Check [project.dependencies] and [project.optional-dependencies] for unpinned versions
        unpinned_re = re.compile(r'"[a-zA-Z][a-zA-Z0-9_-]*[>~^]|"[a-zA-Z][a-zA-Z0-9_-]*"')
        if re.search(r"\bdependencies\s*=", text) and unpinned_re.search(text):
            rc.add_result(
                AUDIT_FILE,
                "Dependencies pinned to exact versions",
                passed=False,
                note="Found unpinned dependencies in pyproject.toml (use == for exact pinning)",
            )
        else:
            rc.add_result(AUDIT_FILE, "Dependencies pinned to exact versions", passed=True)
    else:
        # No dependency manifest — nothing to check
        rc.add_result(
            AUDIT_FILE,
            "Dependencies pinned to exact versions",
            passed=True,
            note="No dependency manifest found",
        )


def check_lock_file(repo: Path, rc: ResultCollector) -> None:
    """5.2: A dependency lock file is committed."""
    for name in LOCK_FILES:
        if (repo / name).is_file():
            rc.add_result(AUDIT_FILE, "Lock file committed", passed=True)
            return
    rc.add_result(
        AUDIT_FILE,
        "Lock file committed",
        passed=False,
        note="No lock file found",
    )


def check_empty_catches(repo: Path, rc: ResultCollector) -> None:
    """6.1: No empty catch/except blocks."""
    hits = _scan_files(repo, EMPTY_CATCH_PATTERN, SOURCE_EXTS)
    if hits:
        rc.add_result(
            AUDIT_FILE,
            "No empty catch/except blocks",
            passed=False,
            note=f"Empty catch blocks in {len(hits)} file(s)",
        )
    else:
        rc.add_result(AUDIT_FILE, "No empty catch/except blocks", passed=True)


def check_crypto_keys(repo: Path, rc: ResultCollector) -> None:
    """7.6: No hardcoded crypto keys or PEM blocks."""
    hits = _scan_files(repo, CRYPTO_KEY_PATTERN, ALL_EXTS)
    if hits:
        rc.add_result(
            AUDIT_FILE,
            "No hardcoded crypto keys",
            passed=False,
            note=f"Potential hardcoded keys in {len(hits)} file(s)",
        )
    else:
        rc.add_result(AUDIT_FILE, "No hardcoded crypto keys", passed=True)


def check_ci_security(repo: Path, rc: ResultCollector) -> None:
    """9.4 + 9.5: SAST and SCA scanning configured in CI."""
    ci_dir = repo / ".github" / "workflows"
    gitlab_ci = repo / ".gitlab-ci.yml"

    ci_text = ""
    if ci_dir.is_dir():
        for wf in ci_dir.iterdir():
            if wf.suffix in {".yml", ".yaml"} and wf.is_file():
                ci_text += wf.read_text(errors="ignore") + "\n"
    elif gitlab_ci.is_file():
        ci_text = gitlab_ci.read_text(errors="ignore")

    has_sast = bool(SAST_TOOLS.search(ci_text)) if ci_text else False
    has_sca = bool(SCA_TOOLS.search(ci_text)) if ci_text else False

    if has_sast:
        rc.add_result(AUDIT_FILE, "SAST scan in CI", passed=True)
    else:
        rc.add_result(
            AUDIT_FILE,
            "SAST scan in CI",
            passed=False,
            note="No SAST scanning found in CI pipeline",
        )

    if has_sca:
        rc.add_result(AUDIT_FILE, "SCA scan in CI", passed=True)
    else:
        rc.add_result(
            AUDIT_FILE,
            "SCA scan in CI",
            passed=False,
            note="No SCA scanning found in CI pipeline",
        )


# ── Orchestrator ─────────────────────────────────────────────────────────


def run_pre_deploy_checks(repo_path: str | Path) -> ResultCollector:
    """Run all pre-deployment checks and return a ResultCollector."""
    repo = Path(repo_path).resolve()
    if not repo.is_dir():
        rc = ResultCollector()
        rc.add_error(f"Directory does not exist: {repo}")
        return rc

    rc = ResultCollector()
    check_secrets(repo, rc)
    check_sql_injection(repo, rc)
    check_unsafe_apis(repo, rc)
    check_dependency_pinning(repo, rc)
    check_lock_file(repo, rc)
    check_empty_catches(repo, rc)
    check_crypto_keys(repo, rc)
    check_ci_security(repo, rc)
    return rc
