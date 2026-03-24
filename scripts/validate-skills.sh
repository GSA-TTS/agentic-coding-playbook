#!/bin/sh
# validate-skills.sh — Validate Agent Skills format and structure

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
SKILLS_DIR="${REPO_ROOT}/skills"

TMP_DIR=$(create_temp_dir)
SKILL_DIRS="${TMP_DIR}/skill-dirs.list"
SHELL_SCRIPTS="${TMP_DIR}/shell-scripts.list"
PYTHON_SCRIPTS="${TMP_DIR}/python-scripts.list"
REFERENCE_FILES="${TMP_DIR}/reference-files.list"

cleanup() {
	rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

printf '%s\n' '=== Agent Skills Validation ==='

if [ ! -d "$SKILLS_DIR" ]; then
	printf '%s\n' 'No skills/ directory found — skipping skills validation.'
	exit 0
fi

find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort > "$SKILL_DIRS"

if [ ! -s "$SKILL_DIRS" ]; then
	printf 'No skill directories found in %s/\n' "$SKILLS_DIR"
	exit 0
fi

while IFS= read -r skill_dir || [ -n "$skill_dir" ]; do
	[ -n "$skill_dir" ] || continue

	SKILL_NAME=$(basename -- "$skill_dir")
	SKILL_FILE="${skill_dir}/SKILL.md"

	printf '\n--- Validating skill: %s ---\n' "$SKILL_NAME"

	if [ ! -f "$SKILL_FILE" ]; then
		printf 'ERROR: %s — missing SKILL.md\n' "$skill_dir"
		ERRORS=$((ERRORS + 1))
		continue
	fi

	if ! head -n 1 "$SKILL_FILE" | grep -q '^---$'; then
		printf 'ERROR: %s — missing YAML frontmatter (no opening ---)\n' "$SKILL_FILE"
		ERRORS=$((ERRORS + 1))
		continue
	fi

	if ! frontmatter_has_field "$SKILL_FILE" "name"; then
		printf 'ERROR: %s — missing required frontmatter field: name\n' "$SKILL_FILE"
		ERRORS=$((ERRORS + 1))
	fi

	if ! frontmatter_has_field "$SKILL_FILE" "description"; then
		printf 'ERROR: %s — missing required frontmatter field: description\n' "$SKILL_FILE"
		ERRORS=$((ERRORS + 1))
	fi

	SKILL_NAME_FIELD=$(trim_quotes "$(get_field "$SKILL_FILE" "name" || true)")
	if [ -n "$SKILL_NAME_FIELD" ] && [ "$SKILL_NAME_FIELD" != "$SKILL_NAME" ]; then
		printf "ERROR: %s — name field '%s' does not match directory name '%s'\n" \
			"$SKILL_FILE" "$SKILL_NAME_FIELD" "$SKILL_NAME"
		ERRORS=$((ERRORS + 1))
	fi

	if [ -n "$SKILL_NAME_FIELD" ]; then
		printf '%s' "$SKILL_NAME_FIELD" | grep -Eq "$SKILL_NAME_INVALID_CHARS_REGEX" && {
			printf 'ERROR: %s — name contains invalid characters\n' "$SKILL_FILE"
			ERRORS=$((ERRORS + 1))
		}

		case "$SKILL_NAME_FIELD" in
			-*|*-)
				printf 'ERROR: %s — name must not start or end with a hyphen\n' "$SKILL_FILE"
				ERRORS=$((ERRORS + 1))
				;;
		esac

		case "$SKILL_NAME_FIELD" in
			*--*)
				printf 'ERROR: %s — name must not contain consecutive hyphens\n' "$SKILL_FILE"
				ERRORS=$((ERRORS + 1))
				;;
		esac

		name_len=$(printf '%s' "$SKILL_NAME_FIELD" | wc -c | tr -d '[:space:]')
		if [ "$name_len" -gt "$SKILL_NAME_MAX_LENGTH" ]; then
			printf 'ERROR: %s — name exceeds %s characters\n' "$SKILL_FILE" "$SKILL_NAME_MAX_LENGTH"
			ERRORS=$((ERRORS + 1))
		fi
	fi

	LINE_COUNT=$(wc -l < "$SKILL_FILE" | tr -d '[:space:]')
	if [ "$LINE_COUNT" -gt "$SKILL_MAX_LINES" ]; then
		printf 'WARNING: %s — %s lines (recommended: <%s)\n' "$SKILL_FILE" "$LINE_COUNT" "$SKILL_MAX_LINES"
		WARNINGS=$((WARNINGS + 1))
	fi

	printf '  OK: %s (%s lines)\n' "$SKILL_FILE" "$LINE_COUNT"

	: > "$SHELL_SCRIPTS"
	: > "$PYTHON_SCRIPTS"
	: > "$REFERENCE_FILES"

	if [ -d "$skill_dir/scripts" ]; then
		find "$skill_dir/scripts" -type f -name '*.sh' | LC_ALL=C sort > "$SHELL_SCRIPTS"
		find "$skill_dir/scripts" -type f -name '*.py' | LC_ALL=C sort > "$PYTHON_SCRIPTS"

		if [ -s "$SHELL_SCRIPTS" ]; then
			while IFS= read -r script || [ -n "$script" ]; do
				[ -n "$script" ] || continue
				printf '  Checking script: %s\n' "$script"
				if command -v shellcheck >/dev/null 2>&1; then
					if ! shellcheck -x -e SC1091 "$script"; then
						printf 'ERROR: %s — ShellCheck failed\n' "$script"
						ERRORS=$((ERRORS + 1))
					else
						printf '    OK: %s (ShellCheck passed)\n' "$script"
					fi
				else
					printf '%s\n' '    SKIP: shellcheck not installed'
				fi
			done < "$SHELL_SCRIPTS"
		fi

		if [ -s "$PYTHON_SCRIPTS" ]; then
			while IFS= read -r script || [ -n "$script" ]; do
				[ -n "$script" ] || continue
				printf '  Checking script: %s\n' "$script"
				if command -v python3 >/dev/null 2>&1; then
					if ! python3 -m py_compile "$script"; then
						printf 'ERROR: %s — Python syntax check failed\n' "$script"
						ERRORS=$((ERRORS + 1))
					else
						printf '    OK: %s (py_compile passed)\n' "$script"
					fi
				else
					printf '%s\n' '    SKIP: python3 not installed'
				fi
			done < "$PYTHON_SCRIPTS"
		fi
	fi

	if [ -d "$skill_dir/references" ]; then
		find "$skill_dir/references" -type f -name '*.md' | LC_ALL=C sort > "$REFERENCE_FILES"
		if [ -s "$REFERENCE_FILES" ]; then
			while IFS= read -r ref_file || [ -n "$ref_file" ]; do
				[ -n "$ref_file" ] || continue
				if ! head -n 1 "$ref_file" | grep -q '^---$'; then
					printf 'WARNING: %s — reference .md file missing frontmatter\n' "$ref_file"
					WARNINGS=$((WARNINGS + 1))
				else
					printf '  OK: %s\n' "$ref_file"
				fi
			done < "$REFERENCE_FILES"
		fi
	fi
done < "$SKILL_DIRS"

printf '\n%s\n' '=== INDEX.yaml Cross-Validation ==='

cd "$REPO_ROOT" || die "Failed to enter repo root"

if [ -f "INDEX.yaml" ]; then
	while IFS= read -r skill_dir || [ -n "$skill_dir" ]; do
		[ -n "$skill_dir" ] || continue
		SKILL_NAME=$(basename -- "$skill_dir")
		if ! grep -Eq "^[[:space:]]*-[[:space:]]+name:[[:space:]]+\"${SKILL_NAME}\"$" INDEX.yaml; then
			printf "ERROR: skill '%s' exists on disk but is missing from INDEX.yaml\n" "$SKILL_NAME"
			printf '%s\n' '  Run: sh scripts/generate-index.sh'
			ERRORS=$((ERRORS + 1))
		else
			printf '  OK: %s listed in INDEX.yaml\n' "$SKILL_NAME"
		fi
	done < "$SKILL_DIRS"
else
	printf '%s\n' 'WARNING: INDEX.yaml not found — cannot cross-validate skills'
	WARNINGS=$((WARNINGS + 1))
fi

SKILL_COUNT=$(count_lines "$SKILL_DIRS")

printf '\n%s\n' '=== Skills Validation Summary ==='
printf 'Skills checked: %s\n' "$SKILL_COUNT"
printf 'Errors:         %s\n' "$ERRORS"
printf 'Warnings:       %s\n' "$WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
	printf 'FAILED — %s error(s) found\n' "$ERRORS"
	exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
	printf 'PASSED with %s warning(s)\n' "$WARNINGS"
else
	printf '%s\n' 'All skills validations passed.'
fi
