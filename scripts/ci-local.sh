#!/usr/bin/env bash
# ci-local.sh — run the CI — Documentation Quality gate locally.
#
# Mirrors .github/workflows/ci.yml so contributors can validate a branch WITHOUT
# waiting on GitHub Actions (useful during Actions outages, or for a fast inner
# loop). It runs the same steps: ruff lint+format, markdownlint, pytest, the
# playbook_validator suite, INDEX freshness, Semgrep SAST, and pip-audit SCA.
#
# CORPORATE TLS-INTERCEPTING PROXY (e.g. ZScaler)
# ----------------------------------------------
# Behind a proxy that re-signs TLS with a corporate root CA, tools that bundle
# their own CA store (Python `requests`, Node, Semgrep) fail with
# `CERTIFICATE_VERIFY_FAILED`. This script builds a *throwaway, invocation-scoped*
# CA bundle from the certs your OS already trusts (macOS keychains + certifi) and
# exports it via the standard CA env vars for the duration of THIS process only.
# It does NOT modify any global trust store, pip/npm/git config, or your shell
# environment — nothing persists after the script exits. We are reusing the root
# your device is already provisioned with, not adding new trust.
#
# Usage:
#   scripts/ci-local.sh            # run everything
#   scripts/ci-local.sh --no-net   # skip the steps that need network (Semgrep, pip-audit)
#   SKIP_SEMGREP=1 scripts/ci-local.sh
#
# Exit code is non-zero if any required step fails.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

NO_NET=0
[[ "${1:-}" == "--no-net" ]] && NO_NET=1

# --- result tracking -------------------------------------------------------
FAILED=()
SKIPPED=()
PASSED=()

step() {
  local name="$1"; shift
  printf '\n\033[1m==> %s\033[0m\n' "$name"
  if "$@"; then
    PASSED+=("$name")
  else
    printf '\033[31m    FAILED: %s\033[0m\n' "$name"
    FAILED+=("$name")
  fi
}

skip() {
  printf '\n\033[33m==> SKIP: %s\033[0m\n    %s\n' "$1" "${2:-}"
  SKIPPED+=("$1")
}

# --- corporate CA bundle (invocation-scoped, never persisted) --------------
# Build a temp bundle = certifi + macOS System + SystemRoots keychains. This
# lets Python/Node/curl validate through a re-signing proxy using roots the OS
# already trusts. Cleaned up on exit.
setup_ca_bundle() {
  local bundle
  bundle="$(mktemp -t ci-local-cabundle.XXXXXX.pem)"
  # Base: certifi if available, else system cert.pem.
  if python3 -c "import certifi" >/dev/null 2>&1; then
    cat "$(python3 -c 'import certifi; print(certifi.where())')" > "$bundle" 2>/dev/null
  elif [[ -f /etc/ssl/cert.pem ]]; then
    cat /etc/ssl/cert.pem > "$bundle"
  fi
  # Append OS-trusted roots (macOS). On Linux these paths won't exist; the
  # base bundle already covers the standard roots there.
  if [[ "$(uname)" == "Darwin" ]]; then
    security find-certificate -a -p /Library/Keychains/System.keychain >> "$bundle" 2>/dev/null || true
    security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain >> "$bundle" 2>/dev/null || true
  fi
  echo "$bundle"
}

CA_BUNDLE=""
if [[ "$NO_NET" -eq 0 ]]; then
  CA_BUNDLE="$(setup_ca_bundle)"
  # Scope to THIS process only — exported here, gone when the script exits.
  export REQUESTS_CA_BUNDLE="$CA_BUNDLE"
  export SSL_CERT_FILE="$CA_BUNDLE"
  export CURL_CA_BUNDLE="$CA_BUNDLE"
  export NODE_EXTRA_CA_CERTS="$CA_BUNDLE"
  trap '[[ -n "$CA_BUNDLE" && -f "$CA_BUNDLE" ]] && rm -f "$CA_BUNDLE"' EXIT
  printf 'Using invocation-scoped CA bundle: %s (%s certs)\n' \
    "$CA_BUNDLE" "$(grep -c "BEGIN CERTIFICATE" "$CA_BUNDLE" 2>/dev/null || echo '?')"
fi

step "Ruff lint"            ruff check scripts/
step "Ruff format check"    ruff format --check scripts/
step "Markdown lint"        npx --prefix .github/linters markdownlint-cli2 \
                              "**/*.md" "#node_modules" "#.github/linters/node_modules" "#CHANGELOG.md"
step "Pytest"               env PYTHONPATH=scripts python3 -m pytest scripts/tests/ -q
step "Validate frontmatter" env PYTHONPATH=scripts python3 -m playbook_validator validate-docs --root .
step "Validate landscape"   env PYTHONPATH=scripts python3 -m playbook_validator validate-landscape --path data/federal-ai-landscape.yaml
step "Validate skills"      env PYTHONPATH=scripts python3 -m playbook_validator validate-skills --root .
step "INDEX.yaml freshness" env PYTHONPATH=scripts python3 -m playbook_validator generate-index --check --root .

# --- Semgrep SAST (mirrors ci.yml `semgrep` job) ---------------------------
# Semgrep's bundled requests client ignores REQUESTS_CA_BUNDLE, so behind a
# proxy we fetch the rulesets with curl (which honors CURL_CA_BUNDLE) and run
# Semgrep offline against the local YAML — identical rules, no live fetch.
# shellcheck disable=SC2329  # invoked indirectly via `step "Semgrep SAST" run_semgrep`
run_semgrep() {
  local rules_dir; rules_dir="$(mktemp -d -t ci-local-semgrep.XXXXXX)"
  local ok=1
  for rs in python security-audit; do
    if ! curl ${CA_BUNDLE:+--cacert "$CA_BUNDLE"} -fsSL \
          "https://semgrep.dev/c/p/${rs}" -o "$rules_dir/${rs}.yaml"; then
      echo "    could not fetch ruleset p/${rs}"; ok=0
    fi
  done
  if [[ "$ok" -eq 1 ]]; then
    SEMGREP_ENABLE_VERSION_CHECK=0 semgrep scan --metrics=off --error \
      --config "$rules_dir/python.yaml" \
      --config "$rules_dir/security-audit.yaml" \
      scripts/
    local rc=$?
    rm -rf "$rules_dir"
    return "$rc"
  fi
  rm -rf "$rules_dir"
  return 1
}

if [[ "$NO_NET" -eq 1 ]]; then
  skip "Semgrep SAST" "--no-net"
elif [[ "${SKIP_SEMGREP:-0}" == "1" ]]; then
  skip "Semgrep SAST" "SKIP_SEMGREP=1"
elif ! command -v semgrep >/dev/null 2>&1; then
  skip "Semgrep SAST" "semgrep not installed (pip install semgrep / brew install semgrep)"
else
  step "Semgrep SAST" run_semgrep
fi

# --- SCA: pip-audit (mirrors ci.yml SCA step) ------------------------------
# CI runs pip-audit in a FRESH runner where only this project's `[dev]` deps are
# installed, so it audits the project's own dependency tree. Auditing the
# developer's ambient interpreter instead would surface unrelated packages from
# other projects (false positives). We therefore build an ephemeral venv with
# `pip install -e ".[dev]"` and audit THAT — matching CI's isolation. The venv
# lives under a temp dir and is removed on exit.
# shellcheck disable=SC2329  # invoked indirectly via `step "pip-audit (SCA)" run_pip_audit`
run_pip_audit() {
  local venv pip_bin
  venv="$(mktemp -d -t ci-local-venv.XXXXXX)"
  if ! python3 -m venv "$venv"; then
    echo "    could not create venv"; rm -rf "$venv"; return 1
  fi
  pip_bin="$venv/bin/pip"
  # Upgrade pip first (CI does this to avoid the pip self-advisory PYSEC-2026-196).
  "$pip_bin" install --quiet --upgrade pip >/dev/null 2>&1
  if ! "$pip_bin" install --quiet -e ".[dev]" >/dev/null 2>&1; then
    echo "    could not install project[dev] into venv"; rm -rf "$venv"; return 1
  fi
  "$pip_bin" install --quiet pip-audit >/dev/null 2>&1
  # Audit the isolated env; skip the editable project itself (matches CI).
  "$venv/bin/pip-audit" --skip-editable
  local rc=$?
  rm -rf "$venv"
  return "$rc"
}

if [[ "$NO_NET" -eq 1 ]]; then
  skip "pip-audit (SCA)" "--no-net"
else
  step "pip-audit (SCA)" run_pip_audit
fi

# --- summary ---------------------------------------------------------------
printf '\n\033[1m==================== ci-local summary ====================\033[0m\n'
printf '  \033[32mpassed:\033[0m  %d\n' "${#PASSED[@]}"
[[ "${#SKIPPED[@]}" -gt 0 ]] && printf '  \033[33mskipped:\033[0m %s\n' "${SKIPPED[*]}"
if [[ "${#FAILED[@]}" -gt 0 ]]; then
  printf '  \033[31mfailed:\033[0m  %s\n' "${FAILED[*]}"
  exit 1
fi
printf '  \033[32mAll executed checks passed.\033[0m\n'
exit 0
