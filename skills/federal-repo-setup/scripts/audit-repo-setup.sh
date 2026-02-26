#!/usr/bin/env bash
# audit-repo-setup.sh — Verify federal compliance baseline in a repository
#
# Outputs structured JSON with pass/fail results for each check.
# Exit code: 0 if all checks pass, 1 if any check fails.
#
# Usage: bash audit-repo-setup.sh [repo-path]
#   repo-path: Path to the repository to audit (default: current directory)
#
# Policy reference: docs/GETTING-STARTED.md

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

# Initialize results
RESULTS=()
WARNINGS=()
ERRORS=()
PASS_COUNT=0
FAIL_COUNT=0

add_result() {
    local check="$1"
    local pass="$2"
    local suggestion="${3:-}"

    if [ "$pass" = "true" ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        RESULTS+=("{\"check\":\"$check\",\"pass\":true}")
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [ -n "$suggestion" ]; then
            RESULTS+=("{\"check\":\"$check\",\"pass\":false,\"suggestion\":\"$suggestion\"}")
        else
            RESULTS+=("{\"check\":\"$check\",\"pass\":false}")
        fi
    fi
}

add_warning() {
    WARNINGS+=("\"$1\"")
}

# --- Check 1: Git repository ---
if [ -d "$REPO_PATH/.git" ]; then
    add_result "git-repo" "true"
else
    add_result "git-repo" "false" "Initialize git: cd $REPO_PATH && git init"
fi

# --- Check 2: .gitignore exists ---
if [ -f "$REPO_PATH/.gitignore" ]; then
    add_result "gitignore-exists" "true"

    # Check for federal-required secret patterns
    SECRETS_PATTERNS=('.env' '*.key' '*.pem' 'credentials.*')
    MISSING_PATTERNS=()
    for pattern in "${SECRETS_PATTERNS[@]}"; do
        if ! grep -qF "$pattern" "$REPO_PATH/.gitignore" 2>/dev/null; then
            MISSING_PATTERNS+=("$pattern")
        fi
    done

    if [ ${#MISSING_PATTERNS[@]} -eq 0 ]; then
        add_result "gitignore-secrets-patterns" "true"
    else
        add_result "gitignore-secrets-patterns" "false" "Add missing patterns to .gitignore: ${MISSING_PATTERNS[*]}"
    fi
else
    add_result "gitignore-exists" "false" "Create .gitignore with federal security patterns"
    add_result "gitignore-secrets-patterns" "false" "Create .gitignore first"
fi

# --- Check 3: .editorconfig exists ---
if [ -f "$REPO_PATH/.editorconfig" ]; then
    add_result "editorconfig" "true"
else
    add_result "editorconfig" "false" "Create .editorconfig for consistent formatting"
fi

# --- Check 4: Pre-commit config exists ---
if [ -f "$REPO_PATH/.pre-commit-config.yaml" ]; then
    add_result "pre-commit-config" "true"

    # Check for secrets scanning hook
    if grep -qE '(gitleaks|detect-secrets|trufflehog)' "$REPO_PATH/.pre-commit-config.yaml" 2>/dev/null; then
        add_result "secrets-scanner-hook" "true"
    else
        add_result "secrets-scanner-hook" "false" "Add gitleaks or detect-secrets to .pre-commit-config.yaml"
    fi
else
    add_result "pre-commit-config" "false" "Create .pre-commit-config.yaml with secrets scanning hook"
    add_result "secrets-scanner-hook" "false" "Create .pre-commit-config.yaml first"
fi

# --- Check 5: Pre-commit hooks installed ---
if [ -f "$REPO_PATH/.git/hooks/pre-commit" ] && grep -q 'pre-commit' "$REPO_PATH/.git/hooks/pre-commit" 2>/dev/null; then
    add_result "pre-commit-installed" "true"
else
    if [ -f "$REPO_PATH/.pre-commit-config.yaml" ]; then
        add_result "pre-commit-installed" "false" "Run: cd $REPO_PATH && pre-commit install"
    else
        add_result "pre-commit-installed" "false" "Create .pre-commit-config.yaml first, then run: pre-commit install"
    fi
fi

# --- Check 6: .env.example exists (if .env patterns in .gitignore) ---
if [ -f "$REPO_PATH/.gitignore" ] && grep -qF '.env' "$REPO_PATH/.gitignore" 2>/dev/null; then
    if [ -f "$REPO_PATH/.env.example" ]; then
        add_result "env-example" "true"
    else
        add_warning "No .env.example found. If the project uses environment variables, create .env.example with placeholder values."
    fi
fi

# --- Check 7: .env is not committed ---
if [ -d "$REPO_PATH/.git" ] && command -v git >/dev/null 2>&1; then
    if git -C "$REPO_PATH" ls-files --error-unmatch .env >/dev/null 2>&1; then
        add_result "env-not-committed" "false" "Remove .env from git: git rm --cached .env"
        ERRORS+=("\"CRITICAL: .env file is tracked by git. Secrets may be exposed in history.\"")
    else
        add_result "env-not-committed" "true"
    fi
fi

# --- Check 8: CI/CD pipeline exists ---
CI_FOUND="false"
if [ -d "$REPO_PATH/.github/workflows" ] && [ -n "$(ls -A "$REPO_PATH/.github/workflows/" 2>/dev/null)" ]; then
    CI_FOUND="true"
elif [ -f "$REPO_PATH/.gitlab-ci.yml" ]; then
    CI_FOUND="true"
elif [ -f "$REPO_PATH/Jenkinsfile" ]; then
    CI_FOUND="true"
fi

if [ "$CI_FOUND" = "true" ]; then
    add_result "ci-pipeline" "true"
else
    add_result "ci-pipeline" "false" "Create a CI/CD pipeline with security stages (lint, test, SAST, dependency scan, secrets scan)"
fi

# --- Check 9: AGENTS.md or equivalent exists ---
AGENTS_FOUND="false"
for agents_file in "AGENTS.md" "CLAUDE.md" ".cursorrules" ".github/copilot-instructions.md"; do
    if [ -f "$REPO_PATH/$agents_file" ]; then
        AGENTS_FOUND="true"
        break
    fi
done

if [ "$AGENTS_FOUND" = "true" ]; then
    add_result "agents-config" "true"
else
    add_result "agents-config" "false" "Create AGENTS.md with federal compliance rules. Use the federal-agents-config skill."
fi

# --- Check 10: Lock file committed ---
LOCK_FOUND="false"
for lock_file in "package-lock.json" "yarn.lock" "pnpm-lock.yaml" "Pipfile.lock" "poetry.lock" "go.sum" "Cargo.lock" "Gemfile.lock"; do
    if [ -f "$REPO_PATH/$lock_file" ]; then
        LOCK_FOUND="true"
        break
    fi
done

if [ "$LOCK_FOUND" = "true" ]; then
    add_result "lock-file" "true"
else
    add_warning "No dependency lock file found. If the project has dependencies, commit the lock file for reproducible builds."
fi

# --- Build JSON output ---
STATUS="success"
if [ "$FAIL_COUNT" -gt 0 ]; then
    STATUS="partial"
fi
if [ ${#ERRORS[@]} -gt 0 ]; then
    STATUS="failure"
fi

# Join arrays
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

printf '{"status":"%s","passed":%d,"failed":%d,"results":%s,"warnings":%s,"errors":%s}\n' \
    "$STATUS" "$PASS_COUNT" "$FAIL_COUNT" "$RESULTS_JSON" "$WARNINGS_JSON" "$ERRORS_JSON"

# Exit with appropriate code
if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
