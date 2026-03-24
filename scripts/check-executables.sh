#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

TMP_DIR=$(
	if command -v mktemp >/dev/null 2>&1; then
		mktemp -d "${TMPDIR:-/tmp}/check-executables.XXXXXX" 2>/dev/null || printf '%s\n' "${TMPDIR:-/tmp}/check-executables.$$"
	else
		printf '%s\n' "${TMPDIR:-/tmp}/check-executables.$$"
	fi
)

mkdir -p "$TMP_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM

FILES_LIST="${TMP_DIR}/files.list"
FAILED_LIST="${TMP_DIR}/failed.list"

: > "$FAILED_LIST"

find "${REPO_ROOT}/scripts" "${REPO_ROOT}/skills" -type f \( -name '*.sh' -o -name '*.py' \) | LC_ALL=C sort > "$FILES_LIST"

while IFS= read -r file || [ -n "$file" ]; do
	[ -n "$file" ] || continue
	if [ ! -x "$file" ]; then
		rel_path=$(printf '%s\n' "$file" | sed "s#^${REPO_ROOT}/##")
		printf 'Not executable: %s\n' "$rel_path"
		printf '%s\n' "$rel_path" >> "$FAILED_LIST"
	fi
done < "$FILES_LIST"

if [ -s "$FAILED_LIST" ]; then
	exit 1
fi

exit 0
