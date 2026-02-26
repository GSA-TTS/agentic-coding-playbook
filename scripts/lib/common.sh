#!/usr/bin/env bash
# common.sh — Shared functions for frontmatter extraction and JSON output
#
# All validation and generation scripts SHOULD source this file to avoid
# duplicating frontmatter parsing logic.
#
# Usage: source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
#        or: source "${REPO_ROOT}/scripts/lib/common.sh"
#
# Prerequisites: None. This file defines ONLY functions. It has no side effects.

# ── Frontmatter Extraction ───────────────────────────────────────────

# Extract a single frontmatter field value from a .md file
# Usage: get_field <file> <field>
# Returns: The field value with quotes stripped, or empty string
get_field() {
	local file="$1"
	local field="$2"
	local fm
	fm=$(sed -n '/^---$/,/^---$/p' "$file" | tail -n +2 | sed '$ d')

	# Handle multiline description (> continuation)
	if [ "$field" = "description" ]; then
		local val
		val=$(grep "^${field}:" <<<"$fm" | head -1 | sed "s/^${field}:[[:space:]]*//" | sed 's/^>//' | sed 's/^[[:space:]]*//' | sed 's/"//g')
		if [ -z "$val" ]; then
			# Try multiline: field followed by indented lines
			val=$(awk "/^${field}:/{found=1; sub(/^${field}:[[:space:]]*>[[:space:]]*/, \"\"); if(\$0) print; next} found && /^[[:space:]]/{sub(/^[[:space:]]+/,\"\"); printf \" %s\", \$0; next} found{exit}" <<<"$fm" | sed 's/^[[:space:]]*//' | sed 's/"//g')
		fi
		printf '%s' "$val"
	elif [ "$field" = "nist_controls" ]; then
		# Return comma-separated list from YAML array (for display)
		local line
		line=$(grep "^${field}:" <<<"$fm" | head -1 || true)
		if [ -n "$line" ]; then
			printf '%s' "$line" | sed "s/^${field}:[[:space:]]*//" | tr -d '[]"' | sed 's/,  */, /g'
		fi
	else
		grep "^${field}:" <<<"$fm" | head -1 | sed "s/^${field}:[[:space:]]*//" | sed 's/"//g' || true
	fi
}

# Extract YAML array field as newline-separated values
# Usage: get_array_field <file> <field>
# Returns: One value per line, with quotes and brackets stripped
get_array_field() {
	local file="$1"
	local field="$2"
	local fm
	fm=$(sed -n '/^---$/,/^---$/p' "$file" | tail -n +2 | sed '$ d')
	# Handle inline array: field: ["val1", "val2"]
	local line
	line=$(grep "^${field}:" <<<"$fm" | head -1 || true)
	if [ -z "$line" ]; then
		return
	fi
	# Extract values from ["a", "b", "c"] format
	printf '%s' "$line" | sed "s/^${field}:[[:space:]]*//" | tr -d '[]"' | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed '/^$/d'
}

# ── JSON Output Helpers ──────────────────────────────────────────────

# Initialize JSON result arrays (call at start of script)
# Usage: json_init
json_init() {
	_JSON_RESULTS=()
	_JSON_WARNINGS=()
	_JSON_ERRORS=()
	_JSON_PASS_COUNT=0
	_JSON_FAIL_COUNT=0
}

# Add a check result
# Usage: json_add_result <file> <check> <pass:true|false> [note]
json_add_result() {
	local file="$1"
	local check="$2"
	local pass="$3"
	local note="${4:-}"

	local filename
	filename=$(basename "$file")

	if [ "$pass" = "true" ]; then
		_JSON_PASS_COUNT=$((_JSON_PASS_COUNT + 1))
		_JSON_RESULTS+=("{\"file\":\"${filename}\",\"check\":\"${check}\",\"pass\":true}")
	else
		_JSON_FAIL_COUNT=$((_JSON_FAIL_COUNT + 1))
		if [ -n "$note" ]; then
			_JSON_RESULTS+=("{\"file\":\"${filename}\",\"check\":\"${check}\",\"pass\":false,\"note\":\"${note}\"}")
		else
			_JSON_RESULTS+=("{\"file\":\"${filename}\",\"check\":\"${check}\",\"pass\":false}")
		fi
	fi
}

# Add a warning message
# Usage: json_add_warning <message>
json_add_warning() {
	_JSON_WARNINGS+=("\"$1\"")
}

# Add an error message
# Usage: json_add_error <message>
json_add_error() {
	_JSON_ERRORS+=("\"$1\"")
}

# Print final JSON output
# Usage: json_output [extra_fields]
#   extra_fields: Optional key:value pairs to include (e.g., "total_adrs:5")
json_output() {
	local status
	if [ "$_JSON_FAIL_COUNT" -eq 0 ]; then
		status="success"
	elif [ "$_JSON_PASS_COUNT" -gt 0 ]; then
		status="partial"
	else
		status="failure"
	fi

	local results_json warnings_json errors_json
	results_json=$(printf '%s,' "${_JSON_RESULTS[@]}" 2>/dev/null | sed 's/,$//')
	warnings_json=$(printf '%s,' "${_JSON_WARNINGS[@]}" 2>/dev/null | sed 's/,$//')
	errors_json=$(printf '%s,' "${_JSON_ERRORS[@]}" 2>/dev/null | sed 's/,$//')

	# Build extra fields string
	local extra=""
	for arg in "$@"; do
		local key="${arg%%:*}"
		local val="${arg#*:}"
		extra="${extra},\"${key}\":${val}"
	done

	printf '{"status":"%s","checks_passed":%d,"checks_failed":%d%s,"results":[%s],"warnings":[%s],"errors":[%s]}\n' \
		"$status" "$_JSON_PASS_COUNT" "$_JSON_FAIL_COUNT" \
		"${extra}" \
		"${results_json:-}" "${warnings_json:-}" "${errors_json:-}"
}
