#!/bin/sh
# generate-readme-structure.sh — Inject a compact repository structure block into README.md

set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

# shellcheck source=scripts/lib/common.sh
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/common.sh"

README="${REPO_ROOT}/README.md"
START_MARKER='<!-- GENERATED:REPO_STRUCTURE:START -->'
END_MARKER='<!-- GENERATED:REPO_STRUCTURE:END -->'
CHECK_MODE="false"

[ "${1:-}" = "--check" ] && CHECK_MODE="true"

require_marker_file "$README" "$START_MARKER" "$END_MARKER"

TMP_DIR=$(create_temp_dir)
SCRIPT_FILES="${TMP_DIR}/script-files.list"
SKILL_DIRS="${TMP_DIR}/skill-dirs.list"
GENERATED_BLOCK="${TMP_DIR}/repo-structure-block.md"
UPDATED_README="${TMP_DIR}/README.updated.md"

cleanup() {
	rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

has_path() {
	[ -e "${REPO_ROOT}/$1" ]
}

if has_path "scripts"; then
	(
		cd "${REPO_ROOT}/scripts" || exit 1
		find . -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sed 's#^\./##' | LC_ALL=C sort
	) > "$SCRIPT_FILES"
else
	: > "$SCRIPT_FILES"
fi

if has_path "skills"; then
	(
		cd "${REPO_ROOT}/skills" || exit 1
		find . -mindepth 1 -maxdepth 1 -type d | sed 's#^\./##' | LC_ALL=C sort
	) > "$SKILL_DIRS"
else
	: > "$SKILL_DIRS"
fi

build_tree_block() {
	printf '%s\n' "$START_MARKER"
	printf '%s\n' '<!-- source: scripts/generate-readme-structure.sh -->'
	printf '%s\n' '<!-- do not edit manually -->'
	printf '%s\n' '```text'
	printf '%s\n' 'agentic-ai-playbook/'

	has_path "README.md" && printf '%s\n' '├── README.md'
	has_path "CONTEXT-GUIDE.md" && printf '%s\n' '├── CONTEXT-GUIDE.md'
	has_path "INDEX.yaml" && printf '%s\n' '├── INDEX.yaml'
	has_path "AGENTS.md" && printf '%s\n' '├── AGENTS.md'
	has_path "CHANGELOG.md" && printf '%s\n' '├── CHANGELOG.md'
	has_path "CONTRIBUTING.md" && printf '%s\n' '├── CONTRIBUTING.md'
	has_path "SECURITY.md" && printf '%s\n' '├── SECURITY.md'
	has_path "CODEOWNERS" && printf '%s\n' '├── CODEOWNERS'
	has_path "LICENSE" && printf '%s\n' '├── LICENSE'
	has_path ".pre-commit-config.yaml" && printf '%s\n' '├── .pre-commit-config.yaml'
	has_path ".github/workflows" && printf '%s\n' '├── .github/workflows/'

	if has_path "scripts"; then
		printf '%s\n' '├── scripts/'
		if [ -s "$SCRIPT_FILES" ]; then
			while IFS= read -r line || [ -n "$line" ]; do
				[ -n "$line" ] || continue
				printf '│   ├── %s\n' "$line"
			done < "$SCRIPT_FILES"
		fi
		has_path "scripts/lib/common.sh" && printf '%s\n' '│   └── lib/common.sh'
	fi

	if has_path "docs"; then
		printf '%s\n' '├── docs/'
		has_path "docs/CODING-PRACTICES.md" && printf '%s\n' '│   └── CODING-PRACTICES.md'
	fi

	if has_path "templates"; then
		printf '%s\n' '├── templates/'
		has_path "templates/agent-bundle" && printf '%s\n' '│   └── agent-bundle/'
	fi

	has_path "examples" && printf '%s\n' '├── examples/'
	has_path "checklists" && printf '%s\n' '├── checklists/'

	if has_path "skills"; then
		printf '%s\n' '└── skills/'
		if [ -s "$SKILL_DIRS" ]; then
			total=$(count_lines "$SKILL_DIRS")
			index=0
			while IFS= read -r skill_dir || [ -n "$skill_dir" ]; do
				[ -n "$skill_dir" ] || continue
				index=$((index + 1))
				if [ "$index" -lt "$total" ]; then
					printf '    ├── %s/\n' "$skill_dir"
				else
					printf '    └── %s/\n' "$skill_dir"
				fi
			done < "$SKILL_DIRS"
		fi
	fi

	printf '%s\n' '```'
	printf '%s\n' "$END_MARKER"
}

build_tree_block > "$GENERATED_BLOCK"
replace_marker_block "$README" "$START_MARKER" "$END_MARKER" "$GENERATED_BLOCK" "$UPDATED_README"

check_or_update_file \
	"$CHECK_MODE" \
	"$README" \
	"$UPDATED_README" \
	"README.md repository structure block is out of date. Run: sh scripts/generate-readme-structure.sh" \
	"OK: README.md repository structure block is up to date" \
	"Injected repository structure block into README.md"
