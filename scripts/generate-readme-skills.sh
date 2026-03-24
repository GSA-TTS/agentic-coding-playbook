#!/bin/sh
# generate-readme-skills.sh — Inject generated skills table into README.md

set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

# shellcheck source=scripts/lib/common.sh
. "${SCRIPT_DIR}/lib/common.sh"

CHECK_MODE="false"
[ "${1:-}" = "--check" ] && CHECK_MODE="true"

README="${REPO_ROOT}/README.md"
START_MARKER='<!-- GENERATED:SKILLS_TABLE:START -->'
END_MARKER='<!-- GENERATED:SKILLS_TABLE:END -->'

require_marker_file "$README" "$START_MARKER" "$END_MARKER"

TMP_DIR=$(create_temp_dir)
SKILL_DIRS="${TMP_DIR}/skill-dirs.list"
GENERATED_BLOCK="${TMP_DIR}/skills-block.md"
UPDATED_README="${TMP_DIR}/README.updated.md"

cleanup() {
	rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

if [ -d "${REPO_ROOT}/skills" ]; then
	find "${REPO_ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort > "$SKILL_DIRS"
else
	: > "$SKILL_DIRS"
fi

build_skills_block() {
	printf '%s\n' "$START_MARKER"
	printf '%s\n' '<!-- do not edit manually; run: sh scripts/generate-readme-skills.sh -->'
	printf '%s\n' '| Skill | Purpose | Scripts? |'
	printf '%s\n' '|-------|---------|----------|'

	if [ -s "$SKILL_DIRS" ]; then
		while IFS= read -r skill_dir || [ -n "$skill_dir" ]; do
			[ -n "$skill_dir" ] || continue

			local_name=$(basename -- "$skill_dir")
			skill_file="${skill_dir}/SKILL.md"
			[ -f "$skill_file" ] || continue

			local_desc=$(get_field "$skill_file" "description" || true)
			short_desc=$(printf '%s' "$local_desc" | sed 's/\. [A-Z].*//')

			desc_len=$(printf '%s' "$short_desc" | wc -c | tr -d '[:space:]')
			if [ "$desc_len" -gt 90 ]; then
				short_desc=$(printf '%s' "$short_desc" | cut -c 1-87 | sed 's/ [^ ]*$//')
				short_desc="${short_desc}..."
			fi

			if [ -d "${skill_dir}/scripts" ] && find "${skill_dir}/scripts" -type f \( -name '*.sh' -o -name '*.py' \) | grep -q .; then
				has_scripts="Yes"
			else
				has_scripts="No"
			fi

			printf "| \`%s\` | %s | %s |\n" "$local_name" "$short_desc" "$has_scripts"
		done < "$SKILL_DIRS"
	fi

	printf '%s\n' "$END_MARKER"
}

build_skills_block > "$GENERATED_BLOCK"
replace_marker_block "$README" "$START_MARKER" "$END_MARKER" "$GENERATED_BLOCK" "$UPDATED_README"

check_or_update_file \
	"$CHECK_MODE" \
	"$README" \
	"$UPDATED_README" \
	"README.md skills table is out of date. Run: sh scripts/generate-readme-skills.sh" \
	"OK: README.md skills table is up to date" \
	"Injected skills table into README.md"
