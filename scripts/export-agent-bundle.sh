#!/bin/sh
# export-agent-bundle.sh — Export a portable, offline-safe agent bundle

set -eu
umask 077

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH='' cd -- "${SCRIPT_DIR}/.." && pwd -P)

# shellcheck source=scripts/lib/common.sh
. "${SCRIPT_DIR}/lib/common.sh"

DEFAULT_OUTPUT="${REPO_ROOT}/dist/agent-bundle"
DEFAULT_PROFILE="core"
DEFAULT_PROJECT_NAME="Your Project Name"
MANIFEST_VERSION="1"

OUTPUT_DIR="${DEFAULT_OUTPUT}"
PROFILE="${DEFAULT_PROFILE}"
PROJECT_NAME="${DEFAULT_PROJECT_NAME}"
OVERWRITE="false"
LIST_SKILLS="false"
DRY_RUN="false"

TMP_WORKDIR=$(create_temp_dir)
SKILLS_FILE="${TMP_WORKDIR}/skills.list"
INCLUDES_FILE="${TMP_WORKDIR}/includes.list"
SORTED_FILE="${TMP_WORKDIR}/sorted.list"

: > "$SKILLS_FILE"
: > "$INCLUDES_FILE"
: > "$SORTED_FILE"

cleanup() {
	rm -rf "$TMP_WORKDIR"
}
trap cleanup EXIT HUP INT TERM

usage() {
	cat <<'EOF'
Usage:
  sh scripts/export-agent-bundle.sh [options]

Options:
  --output <dir>          Output directory (default: ./dist/agent-bundle)
  --profile <name>        Export profile: minimal | core | all (default: core)
  --project-name <name>   Replace [Your Project Name] in exported templates
  --skill <name>          Add a specific skill (repeatable)
  --include <path>        Add a supporting file from templates/ or checklists/ (repeatable)
  --overwrite             Replace output directory if it already exists
  --dry-run               Preview what would be exported without writing files
  --list-skills           List available skills and exit
  --help                  Show this help text
EOF
}

list_available_skills() {
	find "${REPO_ROOT}/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | LC_ALL=C sort
}

validate_skill_exists() {
	skill_name=$1
	skill_path="${REPO_ROOT}/skills/${skill_name}"

	[ -d "$skill_path" ] || die "Skill not found: ${skill_name}"
	[ -f "${skill_path}/SKILL.md" ] || die "Skill missing SKILL.md: ${skill_name}"
}

validate_include_path() {
	rel_path=$1
	abs_path="${REPO_ROOT}/${rel_path}"

	ensure_safe_rel_path "$rel_path" || die "Unsafe include path: ${rel_path}"

	case "$rel_path" in
		templates/*|checklists/*) ;;
		*) die "Unsupported include path: ${rel_path} (must be under templates/ or checklists/)" ;;
	esac

	[ -f "$abs_path" ] || die "Include file not found: ${rel_path}"
}

load_profile() {
	case "$PROFILE" in
		minimal)
			;;
		core)
			append_unique_line "$SKILLS_FILE" "federal-agents-config"
			append_unique_line "$SKILLS_FILE" "federal-pre-deployment-check"
			append_unique_line "$SKILLS_FILE" "federal-repo-setup"
			append_unique_line "$INCLUDES_FILE" "templates/risk-assessment.md"
			append_unique_line "$INCLUDES_FILE" "checklists/pre-deployment.md"
			;;
		all)
			list_available_skills | while IFS= read -r skill_name; do
				[ -n "$skill_name" ] || continue
				append_unique_line "$SKILLS_FILE" "$skill_name"
			done
			append_unique_line "$INCLUDES_FILE" "templates/risk-assessment.md"
			append_unique_line "$INCLUDES_FILE" "checklists/pre-deployment.md"
			;;
		*)
			die "Invalid profile: ${PROFILE} (expected: minimal, core, all)"
			;;
	esac
}

copy_skill() {
	skill_name=$1
	src="${REPO_ROOT}/skills/${skill_name}"
	dest="${OUTPUT_DIR}/.agent-skills/skills/${skill_name}"

	mkdir -p "${OUTPUT_DIR}/.agent-skills/skills" || die "Failed to create skills directory"
	cp -R "$src" "$dest" || die "Failed to copy skill: ${skill_name}"
}

copy_include() {
	rel_path=$1
	src="${REPO_ROOT}/${rel_path}"
	dest="${OUTPUT_DIR}/.agent-skills/${rel_path}"

	mkdir -p "$(dirname -- "$dest")" || die "Failed to create include directory"
	cp "$src" "$dest" || die "Failed to copy include: ${rel_path}"
}

render_agents_md() {
	render_template_file \
		"${REPO_ROOT}/templates/AGENTS.md.template" \
		"${OUTPUT_DIR}/AGENTS.md" \
		"${PROJECT_NAME}"
}

render_bundle_readme() {
	render_template_file \
		"${REPO_ROOT}/templates/agent-bundle/README.md.template" \
		"${OUTPUT_DIR}/.agent-skills/README.md" \
		"${PROJECT_NAME}"
}

render_bundle_coding_practices() {
	render_template_file \
		"${REPO_ROOT}/templates/agent-bundle/CODING-PRACTICES.md.template" \
		"${OUTPUT_DIR}/.agent-skills/docs/CODING-PRACTICES.md" \
		"${PROJECT_NAME}"
}

write_manifest() {
	manifest_path="${OUTPUT_DIR}/.agent-skills/manifest.json"
	repo_name=$(basename -- "$REPO_ROOT")
	source_commit=""

	if command -v git >/dev/null 2>&1; then
		if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
			source_commit=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || printf '')
		fi
	fi

	{
		printf '{\n'
		printf '  "bundle_format_version": "%s",\n' "$(json_escape "$MANIFEST_VERSION")"
		printf '  "profile": "%s",\n' "$(json_escape "$PROFILE")"
		printf '  "project_name": "%s",\n' "$(json_escape "$PROJECT_NAME")"
		printf '  "source": {\n'
		printf '    "repository_name": "%s",\n' "$(json_escape "$repo_name")"
		printf '    "source_commit": "%s"\n' "$(json_escape "$source_commit")"
		printf '  },\n'
		printf '  "paths": {\n'
		printf '    "agents_md": "AGENTS.md",\n'
		printf '    "bundle_root": ".agent-skills",\n'
		printf '    "bundle_readme": ".agent-skills/README.md",\n'
		printf '    "coding_practices": ".agent-skills/docs/CODING-PRACTICES.md",\n'
		printf '    "skills_root": ".agent-skills/skills"\n'
		printf '  },\n'

		printf '  "skills": [\n'
		first="true"
		if [ -s "$SKILLS_FILE" ]; then
			while IFS= read -r skill_name || [ -n "$skill_name" ]; do
				[ -n "$skill_name" ] || continue
				if [ "$first" = "true" ]; then
					first="false"
				else
					printf ',\n'
				fi

				has_scripts="false"
				has_references="false"
				[ -d "${REPO_ROOT}/skills/${skill_name}/scripts" ] && has_scripts="true"
				[ -d "${REPO_ROOT}/skills/${skill_name}/references" ] && has_references="true"

				printf '    {\n'
				printf '      "name": "%s",\n' "$(json_escape "$skill_name")"
				printf '      "path": ".agent-skills/skills/%s",\n' "$(json_escape "$skill_name")"
				printf '      "entrypoint": ".agent-skills/skills/%s/SKILL.md",\n' "$(json_escape "$skill_name")"
				printf '      "has_scripts": %s,\n' "$has_scripts"
				printf '      "has_references": %s\n' "$has_references"
				printf '    }'
			done < "$SKILLS_FILE"
		fi
		printf '\n  ],\n'

		printf '  "supporting_files": [\n'
		printf '    {\n'
		printf '      "source": "templates/agent-bundle/CODING-PRACTICES.md.template",\n'
		printf '      "path": ".agent-skills/docs/CODING-PRACTICES.md"\n'
		printf '    }'

		if [ -s "$INCLUDES_FILE" ]; then
			while IFS= read -r include_path || [ -n "$include_path" ]; do
				[ -n "$include_path" ] || continue
				printf ',\n'
				printf '    {\n'
				printf '      "source": "%s",\n' "$(json_escape "$include_path")"
				printf '      "path": ".agent-skills/%s"\n' "$(json_escape "$include_path")"
				printf '    }'
			done < "$INCLUDES_FILE"
		fi

		printf '\n  ]\n'
		printf '}\n'
	} > "$manifest_path" || die "Failed to write manifest"
}

print_summary() {
	skill_count=$(count_lines "$SKILLS_FILE")
	include_count=$(count_lines "$INCLUDES_FILE")
	supporting_total=$((include_count + 1))

	log "Export complete."
	log "  Output: ${OUTPUT_DIR}"
	log "  Profile: ${PROFILE}"
	log "  Project name: ${PROJECT_NAME}"
	log "  Skills exported: ${skill_count}"
	log "  Supporting files exported: ${supporting_total}"
}

print_dry_run_summary() {
	log "Dry run only. No files were written."
	log "  Output: ${OUTPUT_DIR}"
	log "  Profile: ${PROFILE}"
	log "  Project name: ${PROJECT_NAME}"
	log ""
	log "Would generate:"
	log "  ${OUTPUT_DIR}/AGENTS.md"
	log "  ${OUTPUT_DIR}/.agent-skills/README.md"
	log "  ${OUTPUT_DIR}/.agent-skills/docs/CODING-PRACTICES.md"
	log "  ${OUTPUT_DIR}/.agent-skills/manifest.json"
	log ""
	log "Would copy skills:"

	if [ -s "$SKILLS_FILE" ]; then
		while IFS= read -r skill_name || [ -n "$skill_name" ]; do
			[ -n "$skill_name" ] || continue
			log "  ${REPO_ROOT}/skills/${skill_name} -> ${OUTPUT_DIR}/.agent-skills/skills/${skill_name}"
		done < "$SKILLS_FILE"
	else
		log "  (none)"
	fi

	log ""
	log "Would copy supporting files:"
	log "  ${REPO_ROOT}/templates/agent-bundle/CODING-PRACTICES.md.template -> ${OUTPUT_DIR}/.agent-skills/docs/CODING-PRACTICES.md"

	if [ -s "$INCLUDES_FILE" ]; then
		while IFS= read -r include_path || [ -n "$include_path" ]; do
			[ -n "$include_path" ] || continue
			log "  ${REPO_ROOT}/${include_path} -> ${OUTPUT_DIR}/.agent-skills/${include_path}"
		done < "$INCLUDES_FILE"
	fi
}

while [ "$#" -gt 0 ]; do
	case "$1" in
		--output)
			[ "$#" -ge 2 ] || die "Missing value for --output"
			OUTPUT_DIR=$2
			shift 2
			;;
		--profile)
			[ "$#" -ge 2 ] || die "Missing value for --profile"
			PROFILE=$2
			shift 2
			;;
		--project-name)
			[ "$#" -ge 2 ] || die "Missing value for --project-name"
			PROJECT_NAME=$2
			shift 2
			;;
		--skill)
			[ "$#" -ge 2 ] || die "Missing value for --skill"
			append_unique_line "$SKILLS_FILE" "$2"
			shift 2
			;;
		--include)
			[ "$#" -ge 2 ] || die "Missing value for --include"
			append_unique_line "$INCLUDES_FILE" "$2"
			shift 2
			;;
		--overwrite)
			OVERWRITE="true"
			shift
			;;
		--dry-run)
			DRY_RUN="true"
			shift
			;;
		--list-skills)
			LIST_SKILLS="true"
			shift
			;;
		--help|-h)
			usage
			exit 0
			;;
		*)
			die "Unknown argument: $1"
			;;
	esac
done

if [ "$LIST_SKILLS" = "true" ]; then
	list_available_skills
	exit 0
fi

need_cmd find
need_cmd sort
need_cmd cp
need_cmd awk
need_cmd sed
need_cmd dirname
need_cmd basename

load_profile

if [ -s "$SKILLS_FILE" ]; then
	LC_ALL=C sort "$SKILLS_FILE" > "$SORTED_FILE"
	while IFS= read -r skill_name || [ -n "$skill_name" ]; do
		[ -n "$skill_name" ] || continue
		validate_skill_exists "$skill_name"
	done < "$SORTED_FILE"
	sort_unique_file "$SKILLS_FILE" "${TMP_WORKDIR}/skills.sorted"
	mv "${TMP_WORKDIR}/skills.sorted" "$SKILLS_FILE"
fi

if [ -s "$INCLUDES_FILE" ]; then
	LC_ALL=C sort "$INCLUDES_FILE" > "$SORTED_FILE"
	while IFS= read -r include_path || [ -n "$include_path" ]; do
		[ -n "$include_path" ] || continue
		validate_include_path "$include_path"
	done < "$SORTED_FILE"
	sort_unique_file "$INCLUDES_FILE" "${TMP_WORKDIR}/includes.sorted"
	mv "${TMP_WORKDIR}/includes.sorted" "$INCLUDES_FILE"
fi

if [ "$DRY_RUN" = "true" ]; then
	print_dry_run_summary
	exit 0
fi

if [ -e "$OUTPUT_DIR" ]; then
	if [ "$OVERWRITE" = "true" ]; then
		rm -rf "$OUTPUT_DIR" || die "Failed to remove existing output directory"
	else
		die "Output directory already exists: ${OUTPUT_DIR} (use --overwrite to replace it)"
	fi
fi

mkdir -p "${OUTPUT_DIR}/.agent-skills" || die "Failed to create output directory"

render_agents_md
render_bundle_readme
render_bundle_coding_practices

if [ -s "$SKILLS_FILE" ]; then
	while IFS= read -r skill_name || [ -n "$skill_name" ]; do
		[ -n "$skill_name" ] || continue
		copy_skill "$skill_name"
	done < "$SKILLS_FILE"
fi

if [ -s "$INCLUDES_FILE" ]; then
	while IFS= read -r include_path || [ -n "$include_path" ]; do
		[ -n "$include_path" ] || continue
		copy_include "$include_path"
	done < "$INCLUDES_FILE"
fi

write_manifest
print_summary
