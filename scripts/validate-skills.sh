#!/usr/bin/env bash
# validate-skills.sh — Validate Agent Skills format and structure
# Runs in CI to catch skill quality issues.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "${SCRIPT_DIR}/config.sh"

ERRORS=0
WARNINGS=0
SKILLS_DIR="skills"

echo "=== Agent Skills Validation ==="

if [ ! -d "$SKILLS_DIR" ]; then
  echo "No skills/ directory found — skipping skills validation."
  exit 0
fi

SKILL_DIRS=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

if [ -z "$SKILL_DIRS" ]; then
  echo "No skill directories found in $SKILLS_DIR/"
  exit 0
fi

for skill_dir in $SKILL_DIRS; do
  SKILL_NAME=$(basename "$skill_dir")
  echo ""
  echo "--- Validating skill: $SKILL_NAME ---"

  # Check 1: SKILL.md exists
  SKILL_FILE="$skill_dir/SKILL.md"
  if [ ! -f "$SKILL_FILE" ]; then
    echo "ERROR: $skill_dir — missing SKILL.md"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check 2: SKILL.md has YAML frontmatter
  if ! head -1 "$SKILL_FILE" | grep -q '^---$'; then
    echo "ERROR: $SKILL_FILE — missing YAML frontmatter (no opening ---)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$SKILL_FILE" | tail -n +2 | head -n -1)

  # Check 3: Required frontmatter fields (Agent Skills spec)
  if ! grep -q '^name:' <<< "$FRONTMATTER"; then
    echo "ERROR: $SKILL_FILE — missing required frontmatter field: name"
    ERRORS=$((ERRORS + 1))
  fi

  if ! grep -q '^description:' <<< "$FRONTMATTER"; then
    echo "ERROR: $SKILL_FILE — missing required frontmatter field: description"
    ERRORS=$((ERRORS + 1))
  fi

  # Check 4: name matches directory name
  SKILL_NAME_FIELD=$(grep '^name:' <<< "$FRONTMATTER" | sed 's/name: *//' || true)
  if [ -n "$SKILL_NAME_FIELD" ] && [ "$SKILL_NAME_FIELD" != "$SKILL_NAME" ]; then
    echo "ERROR: $SKILL_FILE — name field '$SKILL_NAME_FIELD' does not match directory name '$SKILL_NAME'"
    ERRORS=$((ERRORS + 1))
  fi

  # Check 5: name format (lowercase, hyphens only, no consecutive hyphens)
  if [ -n "$SKILL_NAME_FIELD" ]; then
    if [[ "$SKILL_NAME_FIELD" =~ $SKILL_NAME_INVALID_CHARS_REGEX ]]; then
      echo "ERROR: $SKILL_FILE — name contains invalid characters (must be lowercase alphanumeric and hyphens)"
      ERRORS=$((ERRORS + 1))
    fi
    if [[ "$SKILL_NAME_FIELD" =~ ^- ]] || [[ "$SKILL_NAME_FIELD" =~ -$ ]]; then
      echo "ERROR: $SKILL_FILE — name must not start or end with a hyphen"
      ERRORS=$((ERRORS + 1))
    fi
    if [[ "$SKILL_NAME_FIELD" =~ -- ]]; then
      echo "ERROR: $SKILL_FILE — name must not contain consecutive hyphens"
      ERRORS=$((ERRORS + 1))
    fi
    if [ ${#SKILL_NAME_FIELD} -gt "$SKILL_NAME_MAX_LENGTH" ]; then
      echo "ERROR: $SKILL_FILE — name exceeds ${SKILL_NAME_MAX_LENGTH} characters"
      ERRORS=$((ERRORS + 1))
    fi
  fi

  # Check 6: Line count < 500
  LINE_COUNT=$(wc -l < "$SKILL_FILE")
  if [ "$LINE_COUNT" -gt "$SKILL_MAX_LINES" ]; then
    echo "WARNING: $SKILL_FILE — $LINE_COUNT lines (recommended: <${SKILL_MAX_LINES})"
    WARNINGS=$((WARNINGS + 1))
  fi

  echo "  OK: $SKILL_FILE ($LINE_COUNT lines)"

  # Check 7: ShellCheck on scripts/*.sh
  if [ -d "$skill_dir/scripts" ]; then
    for script in "$skill_dir"/scripts/*.sh; do
      [ -f "$script" ] || continue
      echo "  Checking script: $script"
      if command -v shellcheck >/dev/null 2>&1; then
        if ! shellcheck -x -e SC1091 "$script"; then
          echo "ERROR: $script — ShellCheck failed"
          ERRORS=$((ERRORS + 1))
        else
          echo "    OK: $script (ShellCheck passed)"
        fi
      else
        echo "    SKIP: shellcheck not installed"
      fi
    done
  fi

  # Check 8: Python syntax check on scripts/*.py
  if [ -d "$skill_dir/scripts" ]; then
    for script in "$skill_dir"/scripts/*.py; do
      [ -f "$script" ] || continue
      echo "  Checking script: $script"
      if command -v python3 >/dev/null 2>&1; then
        if ! python3 -m py_compile "$script"; then
          echo "ERROR: $script — Python syntax check failed"
          ERRORS=$((ERRORS + 1))
        else
          echo "    OK: $script (py_compile passed)"
        fi
      else
        echo "    SKIP: python3 not installed"
      fi
    done
  fi

  # Check 9: References files have frontmatter (if they are .md)
  if [ -d "$skill_dir/references" ]; then
    for ref_file in "$skill_dir"/references/*.md; do
      [ -f "$ref_file" ] || continue
      if ! head -1 "$ref_file" | grep -q '^---$'; then
        echo "WARNING: $ref_file — reference .md file missing frontmatter"
        WARNINGS=$((WARNINGS + 1))
      else
        echo "  OK: $ref_file"
      fi
    done
  fi
done

# ── Cross-validation: skills on disk must appear in INDEX.yaml ────

echo ""
echo "=== INDEX.yaml Cross-Validation ==="

if [ -f "INDEX.yaml" ]; then
  for skill_dir in $SKILL_DIRS; do
    SKILL_NAME=$(basename "$skill_dir")
    if ! grep -q "name: ${SKILL_NAME}$" INDEX.yaml; then
      echo "ERROR: skill '$SKILL_NAME' exists on disk but is missing from INDEX.yaml"
      echo "  Run: bash scripts/generate-index.sh"
      ERRORS=$((ERRORS + 1))
    else
      echo "  OK: $SKILL_NAME listed in INDEX.yaml"
    fi
  done
else
  echo "WARNING: INDEX.yaml not found — cannot cross-validate skills"
  WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "=== Skills Validation Summary ==="
SKILL_COUNT=$(echo "$SKILL_DIRS" | wc -l)
echo "Skills found: $SKILL_COUNT"
echo "Errors:       $ERRORS"
echo "Warnings:     $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
  echo "FAILED — $ERRORS error(s) found"
  exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
  echo "PASSED with $WARNINGS warning(s)"
else
  echo "All skills validations passed."
fi
