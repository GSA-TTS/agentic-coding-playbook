#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

if ! command -v shellcheck >/dev/null 2>&1; then
	printf '%s\n' 'shellcheck is required but not installed.' >&2
	printf '%s\n' 'macOS: brew install shellcheck' >&2
	exit 1
fi

TMP_DIR=$(
	if command -v mktemp >/dev/null 2>&1; then
		mktemp -d "${TMPDIR:-/tmp}/shellcheck.XXXXXX" 2>/dev/null || printf '%s\n' "${TMPDIR:-/tmp}/shellcheck.$$"
	else
		printf '%s\n' "${TMPDIR:-/tmp}/shellcheck.$$"
	fi
)

mkdir -p "$TMP_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM

FILES_LIST="${TMP_DIR}/files.list"

find "${REPO_ROOT}/scripts" "${REPO_ROOT}/skills" -type f -name '*.sh' | LC_ALL=C sort > "$FILES_LIST"

if [ ! -s "$FILES_LIST" ]; then
	printf '%s\n' 'No shell scripts found — skipping'
	exit 0
fi

# Feed paths to shellcheck via xargs.
xargs shellcheck -x -e SC1091 < "$FILES_LIST"
