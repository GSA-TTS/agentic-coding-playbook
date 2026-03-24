#!/bin/sh
# common.sh — Shared functions for shell scripts in this repository
#
# This file is intentionally POSIX sh compatible.
# It defines helper functions only and should be sourced by other scripts.
#
# Usage:
#   . "${SCRIPT_DIR}/lib/common.sh"

# ── Basic Logging / Errors ───────────────────────────────────────────

log() {
	printf '%s\n' "$*"
}

warn() {
	printf 'Warning: %s\n' "$*" >&2
}

die() {
	printf 'Error: %s\n' "$*" >&2
	exit 1
}

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

# ── Path Helpers ─────────────────────────────────────────────────────

resolve_script_dir() {
	CDPATH='' cd -- "$(dirname -- "$1")" && pwd -P
}

resolve_repo_root_from_script() {
	CDPATH='' cd -- "$(dirname -- "$1")/.." && pwd -P
}

# ── Temp Directory Helpers ───────────────────────────────────────────

create_temp_dir() {
	if command -v mktemp >/dev/null 2>&1; then
		tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/repo-scripts.XXXXXX" 2>/dev/null) && {
			printf '%s\n' "$tmp_dir"
			return 0
		}
	fi

	tmp_dir="${TMPDIR:-/tmp}/repo-scripts.$$.$(date +%s)"
	(umask 077 && mkdir -p "$tmp_dir") || die "Failed to create temporary directory"
	printf '%s\n' "$tmp_dir"
}

# ── File List Helpers ────────────────────────────────────────────────

append_unique_line() {
	target_file=$1
	value=$2

	[ -n "$value" ] || return 0

	if [ -f "$target_file" ] && grep -F -x -q -- "$value" "$target_file"; then
		return 0
	fi

	printf '%s\n' "$value" >> "$target_file"
}

sort_unique_file() {
	input_file=$1
	output_file=$2

	if [ ! -s "$input_file" ]; then
		: > "$output_file"
		return 0
	fi

	LC_ALL=C sort -u "$input_file" > "$output_file"
}

count_lines() {
	if [ ! -s "$1" ]; then
		printf '0\n'
	else
		wc -l < "$1" | tr -d '[:space:]'
	fi
}

# ── String / JSON Helpers ────────────────────────────────────────────

trim_quotes() {
	printf '%s' "$1" | sed 's/^"//' | sed 's/"$//'
}

json_escape() {
	printf '%s' "$1" | awk '
	BEGIN { ORS="" }
	{
		gsub(/\\/,"\\\\")
		gsub(/"/,"\\\"")
		gsub(/\t/,"\\t")
		gsub(/\r/,"\\r")
		gsub(/\n/,"\\n")
		printf "%s", $0
	}
	'
}

# ── Frontmatter Extraction ───────────────────────────────────────────

frontmatter_content() {
	file=$1
	awk '
	BEGIN { count = 0 }
	/^---$/ {
		count++
		if (count == 1) next
		if (count == 2) exit
	}
	count == 1 { print }
	' "$file"
}

frontmatter_has_field() {
	file=$1
	field=$2

	frontmatter_content "$file" | grep -q "^${field}:"
}

get_field() {
	file=$1
	field=$2
	fm=$(frontmatter_content "$file")

	if [ "$field" = "description" ]; then
		printf '%s\n' "$fm" | awk -v field="$field" '
		BEGIN {
			found = 0
			first = 1
		}
		$0 ~ ("^" field ":") {
			found = 1
			line = $0
			sub("^" field ":[[:space:]]*", "", line)
			sub(/^>[[:space:]]*/, "", line)
			gsub(/"/, "", line)
			if (length(line) > 0) {
				printf "%s", line
				first = 0
			}
			next
		}
		found && /^[[:space:]]+/ {
			line = $0
			sub(/^[[:space:]]+/, "", line)
			gsub(/"/, "", line)
			if (!first) {
				printf " "
			}
			printf "%s", line
			first = 0
			next
		}
		found {
			exit
		}
		'
	elif [ "$field" = "nist_controls" ]; then
		line=$(printf '%s\n' "$fm" | grep "^${field}:" | head -n 1 || true)
		if [ -n "$line" ]; then
			printf '%s' "$line" | sed "s/^${field}:[[:space:]]*//" | tr -d '[]"' | sed 's/,  */, /g'
		fi
	else
		printf '%s\n' "$fm" | grep "^${field}:" | head -n 1 | sed "s/^${field}:[[:space:]]*//" | sed 's/"//g' || true
	fi
}

get_array_field() {
	file=$1
	field=$2
	fm=$(frontmatter_content "$file")
	line=$(printf '%s\n' "$fm" | grep "^${field}:" | head -n 1 || true)

	[ -n "$line" ] || return 0

	printf '%s' "$line" |
		sed "s/^${field}:[[:space:]]*//" |
		tr -d '[]"' |
		tr ',' '\n' |
		sed 's/^[[:space:]]*//' |
		sed '/^$/d'
}

# ── Validation Helpers ───────────────────────────────────────────────

value_in_list() {
	needle=$1
	list_values=$2

	printf '%s\n' "$list_values" | grep -F -x -q -- "$needle"
}

ensure_safe_rel_path() {
	case "$1" in
		""|/*|../*|*/../*|..|*/..)
			return 1
			;;
		*)
			return 0
			;;
	esac
}

# ── README Marker Block Helpers ──────────────────────────────────────

require_marker_file() {
	file=$1
	start_marker=$2
	end_marker=$3

	[ -f "$file" ] || die "File not found: $file"
	grep -F -q "$start_marker" "$file" || die "Missing start marker in $file: $start_marker"
	grep -F -q "$end_marker" "$file" || die "Missing end marker in $file: $end_marker"
}

replace_marker_block() {
	target_file=$1
	start_marker=$2
	end_marker=$3
	block_file=$4
	output_file=$5

	awk -v blockfile="$block_file" -v start="$start_marker" -v end="$end_marker" '
	BEGIN { skip = 0 }
	$0 == start {
		skip = 1
		while ((getline line < blockfile) > 0) print line
		close(blockfile)
		next
	}
	$0 == end {
		skip = 0
		next
	}
	!skip { print }
	' "$target_file" > "$output_file" || die "Failed to update $target_file"
}

check_or_update_file() {
	check_mode=$1
	current_file=$2
	updated_file=$3
	error_message=$4
	ok_message=$5
	success_message=$6

	if [ "$check_mode" = "true" ]; then
		if ! diff -u "$current_file" "$updated_file" >/dev/null 2>&1; then
			printf 'Error: %s\n' "$error_message" >&2
			diff -u "$current_file" "$updated_file" || true
			exit 1
		fi
		log "$ok_message"
		return 0
	fi

	mv "$updated_file" "$current_file" || die "Failed to update $current_file"
	log "$success_message"
}

# ── Template Rendering ───────────────────────────────────────────────

render_template_file() {
	template_path=$1
	output_path=$2
	project_name=$3

	[ -f "$template_path" ] || die "Missing template: $template_path"

	output_dir=$(dirname -- "$output_path")
	mkdir -p "$output_dir" || die "Failed to create directory: $output_dir"

	PROJECT_NAME_ENV=$project_name awk '
	{
		gsub(/\[Your Project Name\]/, ENVIRON["PROJECT_NAME_ENV"])
		print
	}
	' "$template_path" > "$output_path" || die "Failed to render template: $template_path"
}
