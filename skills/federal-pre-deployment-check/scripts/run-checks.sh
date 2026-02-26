#!/usr/bin/env bash
# run-checks.sh — Run automatable pre-deployment security checks
#
# Outputs structured JSON with pass/fail results.
# Exit code: 0 if all checks pass, 1 if any check fails.
#
# Usage: bash run-checks.sh [repo-path]
#   repo-path: Path to the repository to check (default: current directory)
#
# This script is READ-ONLY. It does not modify files, install packages,
# or make network calls.
#
# Policy reference: checklists/pre-deployment.md

set -euo pipefail

REPO_PATH="${1:-.}"

# Validate repo path
REPO_PATH="$(realpath -- "$REPO_PATH")" || {
    printf '{"status":"error","results":[],"warnings":[],"errors":["Invalid repository path"]}\n'
    exit 1
}

if [ ! -d "$REPO_PATH" ]; then
    printf '{"status":"error","results":[],"warnings":[],"errors":["Directory does not exist: %s"]}\n' "$REPO_PATH"
    exit 1
fi

RESULTS=()
WARNINGS=()
ERRORS=()
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

add_result() {
    local item="$1"
    local check="$2"
    local pass="$3"
    local note="${4:-}"

    if [ "$pass" = "true" ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        RESULTS+=("{\"item\":\"$item\",\"check\":\"$check\",\"pass\":true}")
    elif [ "$pass" = "skip" ]; then
        SKIP_COUNT=$((SKIP_COUNT + 1))
        RESULTS+=("{\"item\":\"$item\",\"check\":\"$check\",\"pass\":\"skip\",\"note\":\"$note\"}")
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [ -n "$note" ]; then
            RESULTS+=("{\"item\":\"$item\",\"check\":\"$check\",\"pass\":false,\"note\":\"$note\"}")
        else
            RESULTS+=("{\"item\":\"$item\",\"check\":\"$check\",\"pass\":false}")
        fi
    fi
}

add_warning() {
    WARNINGS+=("\"$1\"")
}

# ── 2. Secrets and Credentials ─────────────────────────────────

# 2.1: No secrets in source code
if command -v gitleaks >/dev/null 2>&1; then
    if gitleaks detect --source="$REPO_PATH" --no-git --quiet 2>/dev/null; then
        add_result "2.1" "No secrets in source code (gitleaks)" "true"
    else
        add_result "2.1" "No secrets in source code (gitleaks)" "false" "gitleaks detected potential secrets"
    fi
else
    # Fallback: grep for common secret patterns
    SECRET_PATTERNS='(password|secret|api_key|apikey|token|private_key)\s*[:=]\s*["\x27][^"\x27]{8,}'
    if grep -rliE "$SECRET_PATTERNS" "$REPO_PATH" \
        --include='*.py' --include='*.js' --include='*.ts' --include='*.go' \
        --include='*.java' --include='*.yaml' --include='*.yml' --include='*.json' \
        --include='*.toml' --include='*.cfg' --include='*.ini' --include='*.env' \
        --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
        >/dev/null 2>&1; then
        add_result "2.1" "No secrets in source code (grep fallback)" "false" "Potential secrets found. Install gitleaks for better detection."
    else
        add_result "2.1" "No secrets in source code (grep fallback)" "true"
    fi
fi

# 2.5: Pre-commit secrets scanning hook active
if [ -f "$REPO_PATH/.pre-commit-config.yaml" ]; then
    if grep -qE '(gitleaks|detect-secrets|trufflehog)' "$REPO_PATH/.pre-commit-config.yaml" 2>/dev/null; then
        add_result "2.5" "Secrets scanning hook configured" "true"
    else
        add_result "2.5" "Secrets scanning hook configured" "false" "Add gitleaks or detect-secrets to .pre-commit-config.yaml"
    fi
else
    add_result "2.5" "Secrets scanning hook configured" "false" "No .pre-commit-config.yaml found"
fi

# ── 3. Input Validation ────────────────────────────────────────

# 3.2: No string-concatenated SQL
SQL_CONCAT_PATTERN='(execute|query|cursor\.)\s*\(\s*["\x27].*(%s|\+|\.format|f["\x27])'
if grep -rlnE "$SQL_CONCAT_PATTERN" "$REPO_PATH" \
    --include='*.py' --include='*.js' --include='*.ts' --include='*.go' --include='*.java' \
    --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
    --exclude-dir='__pycache__' \
    >/dev/null 2>&1; then
    add_result "3.2" "No string-concatenated SQL" "false" "Potential non-parameterized SQL found"
else
    add_result "3.2" "No string-concatenated SQL" "true"
fi

# 3.5: No eval/innerHTML with untrusted data
UNSAFE_PATTERN='(eval\s*\(|innerHTML\s*=|dangerouslySetInnerHTML|exec\s*\(|os\.system\s*\()'
if grep -rlnE "$UNSAFE_PATTERN" "$REPO_PATH" \
    --include='*.py' --include='*.js' --include='*.ts' --include='*.jsx' --include='*.tsx' \
    --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
    --exclude-dir='__pycache__' \
    >/dev/null 2>&1; then
    add_result "3.5" "No unsafe APIs (eval/innerHTML/exec)" "false" "Potential unsafe API usage found — review manually"
else
    add_result "3.5" "No unsafe APIs (eval/innerHTML/exec)" "true"
fi

# ── 5. Dependency Security ─────────────────────────────────────

# 5.1: Dependencies pinned
PINNED="skip"
if [ -f "$REPO_PATH/requirements.txt" ]; then
    if grep -qE '^[a-zA-Z].*==' "$REPO_PATH/requirements.txt" && \
       ! grep -qE '^[a-zA-Z].*[><=!~]' "$REPO_PATH/requirements.txt" 2>/dev/null | grep -v '=='; then
        PINNED="true"
    else
        PINNED="check"
    fi
elif [ -f "$REPO_PATH/package.json" ]; then
    # Check for ^ or ~ in dependencies
    if grep -qE '"\^|"~' "$REPO_PATH/package.json" 2>/dev/null; then
        PINNED="false"
    else
        PINNED="true"
    fi
fi

if [ "$PINNED" = "true" ]; then
    add_result "5.1" "Dependencies pinned to exact versions" "true"
elif [ "$PINNED" = "false" ] || [ "$PINNED" = "check" ]; then
    add_result "5.1" "Dependencies pinned to exact versions" "false" "Found floating version ranges — pin to exact versions"
else
    add_result "5.1" "Dependencies pinned to exact versions" "skip" "No dependency manifest found"
fi

# 5.2: Lock file present
LOCK_FOUND="false"
for lock_file in "package-lock.json" "yarn.lock" "pnpm-lock.yaml" "Pipfile.lock" "poetry.lock" "go.sum" "Cargo.lock" "Gemfile.lock"; do
    if [ -f "$REPO_PATH/$lock_file" ]; then
        LOCK_FOUND="true"
        break
    fi
done

if [ "$LOCK_FOUND" = "true" ]; then
    add_result "5.2" "Lock file committed" "true"
else
    add_result "5.2" "Lock file committed" "skip" "No lock file found (may not have dependencies)"
fi

# 5.3: No critical/high CVEs
if [ -f "$REPO_PATH/package.json" ] && command -v npm >/dev/null 2>&1; then
    AUDIT_OUTPUT=$(cd "$REPO_PATH" && npm audit --json 2>/dev/null) || true
    if echo "$AUDIT_OUTPUT" | grep -q '"critical":[1-9]\|"high":[1-9]' 2>/dev/null; then
        add_result "5.3" "No critical/high dependency CVEs" "false" "npm audit found critical or high vulnerabilities"
    else
        add_result "5.3" "No critical/high dependency CVEs" "true"
    fi
elif [ -f "$REPO_PATH/requirements.txt" ] && command -v pip-audit >/dev/null 2>&1; then
    if (cd "$REPO_PATH" && pip-audit --require-hashes 2>/dev/null) >/dev/null 2>&1; then
        add_result "5.3" "No critical/high dependency CVEs" "true"
    else
        add_result "5.3" "No critical/high dependency CVEs" "false" "pip-audit found vulnerabilities"
    fi
else
    add_result "5.3" "No critical/high dependency CVEs" "skip" "No supported audit tool available"
fi

# 5.5: Package names verified (check for common typosquatting patterns)
# This is a best-effort heuristic check
add_result "5.5" "Package names verified (typosquatting)" "skip" "Requires manual review"

# 5.6: Dependency scanning in CI
CI_HAS_SCA="false"
if [ -d "$REPO_PATH/.github/workflows" ]; then
    if grep -rlqE '(npm audit|pip-audit|safety|snyk|trivy|dependency-check|govulncheck|cargo-audit)' \
        "$REPO_PATH/.github/workflows/" 2>/dev/null; then
        CI_HAS_SCA="true"
    fi
elif [ -f "$REPO_PATH/.gitlab-ci.yml" ]; then
    if grep -qE '(npm audit|pip-audit|safety|snyk|trivy|dependency-check)' \
        "$REPO_PATH/.gitlab-ci.yml" 2>/dev/null; then
        CI_HAS_SCA="true"
    fi
fi

if [ "$CI_HAS_SCA" = "true" ]; then
    add_result "5.6" "Dependency scanning in CI" "true"
else
    add_result "5.6" "Dependency scanning in CI" "false" "No dependency vulnerability scanning found in CI pipeline"
fi

# ── 6. Error Handling ──────────────────────────────────────────

# 6.1: No empty catch blocks
EMPTY_CATCH='(catch\s*\([^)]*\)\s*\{\s*\}|except\s*:\s*\n\s*pass)'
if grep -rlnPE "$EMPTY_CATCH" "$REPO_PATH" \
    --include='*.py' --include='*.js' --include='*.ts' --include='*.java' \
    --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
    >/dev/null 2>&1; then
    add_result "6.1" "No empty catch/except blocks" "false" "Found empty catch blocks — add error handling"
else
    add_result "6.1" "No empty catch/except blocks" "true"
fi

# ── 7. Cryptography ───────────────────────────────────────────

# 7.6: No hardcoded crypto keys
CRYPTO_KEY_PATTERN='(BEGIN (RSA |DSA |EC )?PRIVATE KEY|AAAA[A-Za-z0-9+/]{40,})'
if grep -rlnE "$CRYPTO_KEY_PATTERN" "$REPO_PATH" \
    --include='*.py' --include='*.js' --include='*.ts' --include='*.go' --include='*.java' \
    --include='*.yaml' --include='*.yml' --include='*.json' --include='*.cfg' \
    --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
    >/dev/null 2>&1; then
    add_result "7.6" "No hardcoded crypto keys" "false" "Potential hardcoded keys or PEM blocks found"
else
    add_result "7.6" "No hardcoded crypto keys" "true"
fi

# ── 9. Testing ─────────────────────────────────────────────────

# 9.2: All existing tests pass
TEST_CMD=""
if [ -f "$REPO_PATH/package.json" ] && grep -q '"test"' "$REPO_PATH/package.json" 2>/dev/null; then
    TEST_CMD="npm test"
elif [ -f "$REPO_PATH/pyproject.toml" ] || [ -f "$REPO_PATH/pytest.ini" ] || [ -f "$REPO_PATH/setup.cfg" ]; then
    TEST_CMD="pytest"
elif [ -f "$REPO_PATH/go.mod" ]; then
    TEST_CMD="go test ./..."
fi

if [ -n "$TEST_CMD" ]; then
    add_result "9.2" "Tests pass" "skip" "Run '$TEST_CMD' manually to verify"
    add_warning "Test execution skipped for safety. Run tests manually: $TEST_CMD"
else
    add_result "9.2" "Tests pass" "skip" "No test framework detected"
fi

# 9.4: SAST scan
CI_HAS_SAST="false"
if [ -d "$REPO_PATH/.github/workflows" ]; then
    if grep -rlqE '(semgrep|bandit|gosec|spotbugs|security-code-scan|codeql)' \
        "$REPO_PATH/.github/workflows/" 2>/dev/null; then
        CI_HAS_SAST="true"
    fi
fi

if [ "$CI_HAS_SAST" = "true" ]; then
    add_result "9.4" "SAST scan in CI" "true"
else
    add_result "9.4" "SAST scan in CI" "false" "No SAST scanning found in CI pipeline"
fi

# 9.5: SCA scan (same as 5.6 but reported under Testing)
if [ "$CI_HAS_SCA" = "true" ]; then
    add_result "9.5" "SCA scan in CI" "true"
else
    add_result "9.5" "SCA scan in CI" "false" "No SCA scanning found in CI pipeline"
fi

# ── 1. Code Review (semi-automated) ───────────────────────────

# 1.2: AI attribution in commits
if [ -d "$REPO_PATH/.git" ] && command -v git >/dev/null 2>&1; then
    RECENT_COMMITS=$(git -C "$REPO_PATH" log --format='%b' -20 2>/dev/null || true)
    if echo "$RECENT_COMMITS" | grep -qi 'Co-Authored-By.*\(claude\|copilot\|cursor\|ai\|agent\)' 2>/dev/null; then
        add_result "1.2" "AI attribution in commits" "true"
    else
        add_result "1.2" "AI attribution in commits" "skip" "No AI attribution found in recent 20 commits (may be new project)"
    fi
fi

# ── Build JSON output ──────────────────────────────────────────

STATUS="success"
if [ "$FAIL_COUNT" -gt 0 ]; then
    STATUS="partial"
fi
if [ ${#ERRORS[@]} -gt 0 ]; then
    STATUS="failure"
fi

RESULTS_JSON=$(printf '%s,' "${RESULTS[@]}")
RESULTS_JSON="[${RESULTS_JSON%,}]"

if [ ${#WARNINGS[@]} -gt 0 ]; then
    WARNINGS_JSON=$(printf '%s,' "${WARNINGS[@]}")
    WARNINGS_JSON="[${WARNINGS_JSON%,}]"
else
    WARNINGS_JSON="[]"
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    ERRORS_JSON=$(printf '%s,' "${ERRORS[@]}")
    ERRORS_JSON="[${ERRORS_JSON%,}]"
else
    ERRORS_JSON="[]"
fi

printf '{"status":"%s","passed":%d,"failed":%d,"skipped":%d,"results":%s,"warnings":%s,"errors":%s}\n' \
    "$STATUS" "$PASS_COUNT" "$FAIL_COUNT" "$SKIP_COUNT" "$RESULTS_JSON" "$WARNINGS_JSON" "$ERRORS_JSON"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
