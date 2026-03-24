#!/bin/sh
# validate-docs.sh — Validate frontmatter and INDEX.yaml consistency

set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

# shellcheck source=scripts/lib/common.sh
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=scripts/config.sh
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/config.sh"

ERRORS=0
WARNINGS=0

TMP_DIR=$(create_temp_dir)
CONTENT_FILES="${TMP_DIR}/content-files.list"
INDEX_PATHS="${TMP_DIR}/index-paths.list"
RELATED_REFS="${TMP_DIR}/related-refs.list"

cleanup() {
	rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

cd "$REPO_ROOT" || die "Failed to enter repo root"

find . -name '*.md' \
	-not -path './.git/*' \
	-not -path './.github/*' \
	-not -path './node_modules/*' \
	-not -path './skills/*' \
	-not -name 'CONTRIBUTING.md' \
	-not -name 'CHANGELOG.md' \
	-not -name 'README.md' \
	-not -name 'SECURITY.md' \
	-not -name 'LICENSE' \
	| LC_ALL=C sort > "$CONTENT_FILES"

printf '%s\n' '=== Frontmatter Validation ==='

required_fields_file="${TMP_DIR}/required-fields.list"
printf '%s\n' "$REQUIRED_FRONTMATTER_FIELDS" | sed '/^$/d' > "$required_fields_file"

if [ -s "$CONTENT_FILES" ]; then
	while IFS= read -r file || [ -n "$file" ]; do
		[ -n "$file" ] || continue

		file_errors=0

		if ! head -n 1 "$file" | grep -q '^---$'; then
			printf 'ERROR: %s — missing YAML frontmatter (no opening ---)\n' "$file"
			ERRORS=$((ERRORS + 1))
			continue
		fi

		while IFS= read -r field || [ -n "$field" ]; do
			[ -n "$field" ] || continue
			if ! frontmatter_has_field "$file" "$field"; then
				printf 'ERROR: %s — missing required frontmatter field: %s\n' "$file" "$field"
				ERRORS=$((ERRORS + 1))
				file_errors=$((file_errors + 1))
			fi
		done < "$required_fields_file"

		STATUS=$(trim_quotes "$(get_field "$file" "status" || true)")
		if [ -n "$STATUS" ] && ! value_in_list "$STATUS" "$DOC_STATUS_VALUES"; then
			printf 'ERROR: %s — invalid status: %s\n' "$file" "$STATUS"
			ERRORS=$((ERRORS + 1))
			file_errors=$((file_errors + 1))
		fi

		TIER=$(trim_quotes "$(get_field "$file" "tier" || true)")
		if [ -n "$TIER" ] && ! value_in_list "$TIER" "$DOC_TIER_VALUES"; then
			printf 'ERROR: %s — invalid tier: %s\n' "$file" "$TIER"
			ERRORS=$((ERRORS + 1))
			file_errors=$((file_errors + 1))
		fi

		LOAD_PRIORITY=$(trim_quotes "$(get_field "$file" "load_priority" || true)")
		if [ -n "$LOAD_PRIORITY" ] && ! value_in_list "$LOAD_PRIORITY" "$DOC_LOAD_PRIORITY_VALUES"; then
			printf 'ERROR: %s — invalid load_priority: %s\n' "$file" "$LOAD_PRIORITY"
			ERRORS=$((ERRORS + 1))
			file_errors=$((file_errors + 1))
		fi

		AUDIENCE=$(trim_quotes "$(get_field "$file" "audience" || true)")
		if [ -n "$AUDIENCE" ] && ! value_in_list "$AUDIENCE" "$DOC_AUDIENCE_VALUES"; then
			printf 'ERROR: %s — invalid audience: %s\n' "$file" "$AUDIENCE"
			ERRORS=$((ERRORS + 1))
			file_errors=$((file_errors + 1))
		fi

		REVIEW_CYCLE=$(trim_quotes "$(get_field "$file" "review_cycle" || true)")
		if [ -n "$REVIEW_CYCLE" ] && ! value_in_list "$REVIEW_CYCLE" "$DOC_REVIEW_CYCLE_VALUES"; then
			printf 'ERROR: %s — invalid review_cycle: %s\n' "$file" "$REVIEW_CYCLE"
			ERRORS=$((ERRORS + 1))
			file_errors=$((file_errors + 1))
		fi

		if [ "$file_errors" -eq 0 ]; then
			printf '  OK: %s\n' "$file"
		fi
	done < "$CONTENT_FILES"
fi

printf '\n%s\n' '=== INDEX.yaml Validation ==='

if [ ! -f "INDEX.yaml" ]; then
	printf '%s\n' 'ERROR: INDEX.yaml not found'
	ERRORS=$((ERRORS + 1))
else
	if [ -s "$CONTENT_FILES" ]; then
		while IFS= read -r file || [ -n "$file" ]; do
			[ -n "$file" ] || continue
			NORMALIZED=${file#./}
			if ! grep -q "path: \"${NORMALIZED}\"" INDEX.yaml; then
				printf 'WARNING: %s — not listed in INDEX.yaml\n' "$NORMALIZED"
				WARNINGS=$((WARNINGS + 1))
			fi
		done < "$CONTENT_FILES"
	fi

	grep 'path:' INDEX.yaml | grep -v 'skills/' | sed 's/.*path: "\(.*\)"/\1/' > "$INDEX_PATHS" || true

	if [ -s "$INDEX_PATHS" ]; then
		while IFS= read -r path || [ -n "$path" ]; do
			[ -n "$path" ] || continue
			if [ ! -f "$path" ]; then
				printf 'ERROR: INDEX.yaml references non-existent file: %s\n' "$path"
				ERRORS=$((ERRORS + 1))
			fi
		done < "$INDEX_PATHS"
	fi

	printf '%s\n' '  INDEX.yaml validation complete'
fi

printf '\n%s\n' '=== Related Files Validation ==='

if [ -s "$CONTENT_FILES" ]; then
	while IFS= read -r file || [ -n "$file" ]; do
		[ -n "$file" ] || continue

		: > "$RELATED_REFS"
		frontmatter_content "$file" |
		awk '
		BEGIN { in_related = 0 }
		/^related_files:/ { in_related = 1; next }
		in_related && /^[^[:space:]-]/ { exit }
		in_related && /^[[:space:]]*-[[:space:]]*"/ {
			line = $0
			sub(/^[[:space:]]*-[[:space:]]*"/, "", line)
			sub(/".*$/, "", line)
			print line
		}
		' > "$RELATED_REFS"

		if [ -s "$RELATED_REFS" ]; then
			while IFS= read -r related || [ -n "$related" ]; do
				[ -n "$related" ] || continue
				if [ ! -f "$related" ]; then
					printf 'WARNING: %s — related_files references non-existent: %s\n' "$file" "$related"
					WARNINGS=$((WARNINGS + 1))
				fi
			done < "$RELATED_REFS"
		fi
	done < "$CONTENT_FILES"
fi

printf '\n%s\n' '=== Summary ==='
printf 'Errors:   %s\n' "$ERRORS"
printf 'Warnings: %s\n' "$WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
	printf 'FAILED — %s error(s) found\n' "$ERRORS"
	exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
	printf 'PASSED with %s warning(s)\n' "$WARNINGS"
else
	printf '%s\n' 'All validations passed.'
fi
