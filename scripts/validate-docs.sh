#!/usr/bin/env bash
# validate-docs.sh — Validate frontmatter and INDEX.yaml consistency
# Runs in CI to catch documentation quality issues.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

ERRORS=0
WARNINGS=0

echo "=== Frontmatter Validation ==="

# Content directories to check (exclude meta-docs and skills which have their own validation)
# Use NUL-delimited find + mapfile for safe handling of filenames with spaces
mapfile -d '' CONTENT_FILES < <(find . -name '*.md' \
	-not -path './.git/*' \
	-not -path './.github/*' \
	-not -path './node_modules/*' \
	-not -path './skills/*' \
	-not -name 'CONTRIBUTING.md' \
	-not -name 'CHANGELOG.md' \
	-not -name 'README.md' \
	-not -name 'SECURITY.md' \
	-not -name 'LICENSE' \
	-print0 | sort -z)

REQUIRED_FIELDS=("${REQUIRED_FRONTMATTER_FIELDS[@]}")

for file in "${CONTENT_FILES[@]}"; do
	# Check if file starts with frontmatter delimiter
	if ! head -1 "$file" | grep -q '^---$'; then
		echo "ERROR: $file — missing YAML frontmatter (no opening ---)"
		ERRORS=$((ERRORS + 1))
		continue
	fi

	# Extract frontmatter (between first and second ---)
	FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$file" | tail -n +2 | sed '$ d')

	for field in "${REQUIRED_FIELDS[@]}"; do
		if ! grep -q "^${field}:" <<<"$FRONTMATTER"; then
			echo "ERROR: $file — missing required frontmatter field: $field"
			ERRORS=$((ERRORS + 1))
		fi
	done

	# Check status value
	STATUS=$(grep '^status:' <<<"$FRONTMATTER" | sed 's/status: *//' || true)
	if [ -n "$STATUS" ] && [[ ! "$STATUS" =~ $DOC_STATUS_REGEX ]]; then
		echo "ERROR: $file — invalid status: '$STATUS' (must be ${DOC_STATUS_VALUES[*]})"
		ERRORS=$((ERRORS + 1))
	fi

	# Check tier value
	TIER=$(grep '^tier:' <<<"$FRONTMATTER" | sed 's/tier: *//' || true)
	if [ -n "$TIER" ] && [[ ! "$TIER" =~ $DOC_TIER_REGEX ]]; then
		echo "ERROR: $file — invalid tier: '$TIER' (must be ${DOC_TIER_VALUES[*]})"
		ERRORS=$((ERRORS + 1))
	fi

	# Check load_priority value (optional field)
	LOAD_PRIORITY=$(grep '^load_priority:' <<<"$FRONTMATTER" | sed 's/load_priority: *"\{0,1\}//' | sed 's/"\{0,1\}$//' || true)
	if [ -n "$LOAD_PRIORITY" ] && [[ ! "$LOAD_PRIORITY" =~ $DOC_LOAD_PRIORITY_REGEX ]]; then
		echo "ERROR: $file — invalid load_priority: '$LOAD_PRIORITY' (must be ${DOC_LOAD_PRIORITY_VALUES[*]})"
		ERRORS=$((ERRORS + 1))
	fi

	echo "  OK: $file"
done

echo ""
echo "=== INDEX.yaml Validation ==="

if [ ! -f "INDEX.yaml" ]; then
	echo "ERROR: INDEX.yaml not found"
	ERRORS=$((ERRORS + 1))
else
	# Check that all content files are listed in INDEX.yaml
	for file in "${CONTENT_FILES[@]}"; do
		# Normalize path (remove leading ./)
		NORMALIZED="${file#./}"
		if ! grep -q "path: \"${NORMALIZED}\"" INDEX.yaml; then
			echo "WARNING: $NORMALIZED — not listed in INDEX.yaml"
			WARNINGS=$((WARNINGS + 1))
		fi
	done

	# Check that all document paths in INDEX.yaml point to existing files
	# (skills paths are validated by validate-skills.sh)
	while IFS= read -r path; do
		if [ ! -f "$path" ]; then
			echo "ERROR: INDEX.yaml references non-existent file: $path"
			ERRORS=$((ERRORS + 1))
		fi
	done < <(grep 'path:' INDEX.yaml | grep -v 'skills/' | sed 's/.*path: "\(.*\)"/\1/')

	echo "  INDEX.yaml validation complete"
fi

echo ""
echo "=== Related Files Validation ==="

# Check that related_files in frontmatter point to existing files
for file in "${CONTENT_FILES[@]}"; do
	FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$file" | tail -n +2 | sed '$ d')
	RELATED=$(grep -A50 '^related_files:' <<<"$FRONTMATTER" | grep '^ *- "' | sed 's/.*"\(.*\)"/\1/' || true)
	while IFS= read -r related; do
		[ -z "$related" ] && continue
		if [ ! -f "$related" ]; then
			echo "WARNING: $file — related_files references non-existent: $related"
			WARNINGS=$((WARNINGS + 1))
		fi
	done <<<"$RELATED"
done

echo ""
echo "=== Summary ==="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
	echo "FAILED — $ERRORS error(s) found"
	exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
	echo "PASSED with $WARNINGS warning(s)"
fi

echo "All validations passed."
