#!/bin/sh
# generate-readme-changelog.sh — Inject latest changelog summary into README.md

set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

# shellcheck source=scripts/lib/common.sh
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/lib/common.sh"

README="${REPO_ROOT}/README.md"
CHANGELOG="${REPO_ROOT}/CHANGELOG.md"

CHECK_MODE="false"
RELEASE_COUNT=1

while [ "$#" -gt 0 ]; do
	case "$1" in
		--check)
			CHECK_MODE="true"
			shift
			;;
		--releases)
			[ "$#" -ge 2 ] || die "Missing value for --releases"
			RELEASE_COUNT=$2
			shift 2
			;;
		*)
			die "Unknown argument: $1"
			;;
	esac
done

START_MARKER='<!-- GENERATED:CHANGELOG_SUMMARY:START -->'
END_MARKER='<!-- GENERATED:CHANGELOG_SUMMARY:END -->'

require_marker_file "$README" "$START_MARKER" "$END_MARKER"
[ -f "$CHANGELOG" ] || die "CHANGELOG.md not found at $CHANGELOG"

TMP_DIR=$(create_temp_dir)
EXTRACTED="${TMP_DIR}/changelog-extracted.md"
GENERATED_BLOCK="${TMP_DIR}/generated-block.md"
UPDATED_README="${TMP_DIR}/README.updated.md"

cleanup() {
	rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

awk -v releases="$RELEASE_COUNT" '
BEGIN {
	count = 0
	in_release = 0
}
$0 ~ /^## \[/ {
	count++
	if (count <= releases) {
		in_release = 1
	} else {
		in_release = 0
	}
}
in_release {
	print
}
' "$CHANGELOG" > "$EXTRACTED"

[ -s "$EXTRACTED" ] || die "Failed to extract any release entries from CHANGELOG.md"

{
	printf '%s\n' "$START_MARKER"
	printf '%s\n' '<!-- do not edit manually; run: sh scripts/generate-readme-changelog.sh -->'
	printf '\n'
	printf '## Recent Changes\n'
	printf '\n'
	cat "$EXTRACTED"
	printf '[View full changelog](./CHANGELOG.md)\n'
	printf '\n'
	printf '%s\n' "$END_MARKER"
} > "$GENERATED_BLOCK"

replace_marker_block "$README" "$START_MARKER" "$END_MARKER" "$GENERATED_BLOCK" "$UPDATED_README"

check_or_update_file \
	"$CHECK_MODE" \
	"$README" \
	"$UPDATED_README" \
	"README.md changelog summary is out of date. Run: sh scripts/generate-readme-changelog.sh" \
	"OK: README.md changelog summary is up to date" \
	"Injected changelog summary into README.md"
