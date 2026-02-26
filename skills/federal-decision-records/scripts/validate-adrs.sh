#!/usr/bin/env bash
# validate-adrs.sh — Validate decision record format and completeness
#
# Checks all NNNN-*.md files in a decisions directory for:
# - Required YAML frontmatter fields
# - Valid status values
# - NIST control ID format
# - Sequential numbering (no duplicates)
# - Superseded records reference the superseding record
# - File naming convention
#
# Usage: bash validate-adrs.sh [directory]
#   directory: Path to the decisions directory (default: docs/decisions)
#
# Output: Structured JSON to stdout
#   {"status":"success|failure|partial","results":[...],"warnings":[...],"errors":[...]}
#
# This script is READ-ONLY. It does not modify files, install packages,
# or make network calls.

set -euo pipefail

# Source shared libraries (resolve from skill script → repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_SCRIPTS="${SCRIPT_DIR}/../../../scripts"
# shellcheck source=../../../scripts/lib/common.sh
source "${REPO_SCRIPTS}/lib/common.sh"
# shellcheck source=../../../scripts/config.sh
source "${REPO_SCRIPTS}/config.sh"

ADR_DIR="${1:-docs/decisions}"

# Validate directory path
ADR_DIR="$(realpath -- "$ADR_DIR" 2>/dev/null)" || {
    printf '{"status":"error","results":[],"warnings":[],"errors":["Invalid directory path: %s"]}\n' "$ADR_DIR"
    exit 1
}

if [ ! -d "$ADR_DIR" ]; then
    printf '{"status":"error","results":[],"warnings":[],"errors":["Directory does not exist: %s"]}\n' "$ADR_DIR"
    exit 1
fi

# Initialize JSON output helpers from common.sh
json_init

# ── Collect ADR files ────────────────────────────────────────────────

ADR_FILES=()
while IFS= read -r f; do
    ADR_FILES+=("$f")
done < <(find "$ADR_DIR" -maxdepth 1 -name '[0-9][0-9][0-9][0-9]-*.md' -type f | sort)

if [ ${#ADR_FILES[@]} -eq 0 ]; then
    printf '{"status":"success","results":[{"check":"adr_count","pass":true,"note":"No ADR files found"}],"warnings":[],"errors":[]}\n'
    exit 0
fi

# ── Check for duplicate numbers ──────────────────────────────────────

NUMBERS=()
for file in "${ADR_FILES[@]}"; do
    filename=$(basename "$file")
    number="${filename%%-*}"
    NUMBERS+=("$number")
done

DUPES=$(printf '%s\n' "${NUMBERS[@]}" | sort | uniq -d)
if [ -n "$DUPES" ]; then
    for dupe in $DUPES; do
        json_add_error "Duplicate ADR number: ${dupe}"
    done
fi

# ── Validate each ADR ───────────────────────────────────────────────

for file in "${ADR_FILES[@]}"; do
    filename=$(basename "$file")

    # Check: has frontmatter
    if ! head -1 "$file" | grep -q '^---$'; then
        json_add_result "$file" "has_frontmatter" "false" "Missing YAML frontmatter"
        continue
    fi

    # Check: required fields (from config.sh)
    for field in "${REQUIRED_ADR_FIELDS[@]}"; do
        val=$(get_field "$file" "$field")
        if [ -z "$val" ]; then
            json_add_result "$file" "required_field_${field}" "false" "Missing required field: ${field}"
        else
            json_add_result "$file" "required_field_${field}" "true"
        fi
    done

    # Check: valid status (from config.sh)
    status=$(get_field "$file" "status")
    if [ -n "$status" ]; then
        if [[ "$status" =~ $ADR_STATUS_REGEX ]]; then
            json_add_result "$file" "valid_status" "true"
        else
            json_add_result "$file" "valid_status" "false" "Invalid status: ${status} (expected: ${ADR_STATUS_VALUES[*]})"
        fi
    fi

    # Check: NIST control format (from config.sh)
    controls_raw=$(get_field "$file" "nist_controls")
    if [ -n "$controls_raw" ]; then
        # Parse inline YAML array
        controls=$(printf '%s' "$controls_raw" | tr -d '[]"' | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed '/^$/d')
        all_valid=true
        while IFS= read -r ctrl; do
            if ! printf '%s' "$ctrl" | grep -qE "$NIST_CONTROL_REGEX"; then
                json_add_result "$file" "nist_format" "false" "Invalid NIST control format: ${ctrl}"
                all_valid=false
            fi
        done <<< "$controls"
        if [ "$all_valid" = true ]; then
            json_add_result "$file" "nist_format" "true"
        fi
    fi

    # Check: date format (YYYY-MM-DD)
    date_val=$(get_field "$file" "date")
    if [ -n "$date_val" ]; then
        if printf '%s' "$date_val" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
            json_add_result "$file" "date_format" "true"
        else
            json_add_result "$file" "date_format" "false" "Invalid date format: ${date_val} (expected: YYYY-MM-DD)"
        fi
    fi

    # Check: filename convention (from config.sh)
    if printf '%s' "$filename" | grep -qE "$ADR_FILENAME_REGEX"; then
        json_add_result "$file" "filename_convention" "true"
    else
        json_add_result "$file" "filename_convention" "false" "Filename should match NNNN-lowercase-title.md"
    fi

    # Check: superseded records reference superseding record
    if [ "$status" = "superseded" ]; then
        superseded_by=$(get_field "$file" "superseded_by")
        if [ -z "$superseded_by" ]; then
            json_add_result "$file" "superseded_ref" "false" "Status is superseded but missing superseded_by field"
        else
            if [ -f "${ADR_DIR}/${superseded_by}" ]; then
                json_add_result "$file" "superseded_ref" "true"
            else
                json_add_result "$file" "superseded_ref" "false" "superseded_by references non-existent file: ${superseded_by}"
            fi
        fi
    fi

    # Check: category field present
    category=$(get_field "$file" "category")
    if [ -z "$category" ]; then
        json_add_warning "${filename}: Missing optional field: category"
    fi

    # Check: impact_level field present
    impact=$(get_field "$file" "impact_level")
    if [ -z "$impact" ]; then
        json_add_warning "${filename}: Missing optional field: impact_level"
    fi

    # Check: ato_relevance field present
    ato=$(get_field "$file" "ato_relevance")
    if [ -z "$ato" ]; then
        json_add_warning "${filename}: Missing optional field: ato_relevance"
    fi
done

# ── Build JSON output (using common.sh helpers) ─────────────────────

json_output "\"total_adrs\":${#ADR_FILES[@]}"

# Exit with non-zero if any failures
if [ "$_JSON_FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
