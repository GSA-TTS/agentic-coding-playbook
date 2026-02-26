#!/usr/bin/env bash
# shellcheck disable=SC2034  # Variables are used by scripts that source this file
# config.sh — Centralized schema constants for federal-agentic-ai-guidance
#
# Single source of truth for validation rules, enum values, and limits.
# All validation and generation scripts SHOULD source this file.
#
# Usage: source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
#        or: source "${REPO_ROOT}/scripts/config.sh"
#
# This file defines ONLY constants. It has no side effects.

# ── Document Frontmatter Schema ──────────────────────────────────────

# Required fields for all content .md files
REQUIRED_FRONTMATTER_FIELDS=("title" "description" "status" "tier")

# Optional fields
OPTIONAL_FRONTMATTER_FIELDS=("last_updated" "nist_controls" "frameworks" "audience" "keywords" "related_files" "load_priority" "review_cycle")

# Valid status values for documents
DOC_STATUS_VALUES=("canonical" "draft" "deprecated")
DOC_STATUS_REGEX="^(canonical|draft|deprecated)$"

# Valid tier values
DOC_TIER_VALUES=(1 2 3)
DOC_TIER_REGEX="^[123]$"

# Valid audience values
DOC_AUDIENCE_VALUES=("developers" "isso" "managers" "all")

# Valid load priority values for LLM context optimization
# always: Load for every task (core behavioral contracts)
# task-context: Load when task matches document keywords
# on-demand: Load only when explicitly relevant
# reference-only: Load only when directly invoked (templates, checklists)
DOC_LOAD_PRIORITY_VALUES=("always" "task-context" "on-demand" "reference-only")
DOC_LOAD_PRIORITY_REGEX="^(always|task-context|on-demand|reference-only)$"

# Valid review cycle values
DOC_REVIEW_CYCLE_VALUES=("quarterly" "semi-annually" "annually")

# ── ADR (Decision Record) Schema ──────────────────────────────────────

# Required fields for ADR frontmatter
REQUIRED_ADR_FIELDS=("title" "status" "date" "nist_controls")

# Valid ADR status values (different domain from document status)
ADR_STATUS_VALUES=("proposed" "accepted" "deprecated" "superseded")
ADR_STATUS_REGEX="^(proposed|accepted|deprecated|superseded)$"

# ADR filename pattern: NNNN-lowercase-with-hyphens.md
ADR_FILENAME_REGEX="^[0-9]{4}-[a-z0-9-]+\.md$"

# ── NIST Control Format ──────────────────────────────────────────────

# NIST control ID regex: XX-NN or XX-NN(NN)
NIST_CONTROL_REGEX='^[A-Z]{2}-[0-9]+(\([0-9]+\))?$'

# ── Skill Validation ──────────────────────────────────────────────────

# Maximum recommended lines for SKILL.md
SKILL_MAX_LINES=500

# Skill name constraints
SKILL_NAME_MAX_LENGTH=64
SKILL_NAME_INVALID_CHARS_REGEX='[^a-z0-9-]'

# ── Size and Complexity Limits ────────────────────────────────────────
# These match CODING_PRACTICES.md §13.3

FUNCTION_MAX_LINES=50
FILE_MAX_LINES=400
CYCLOMATIC_COMPLEXITY_MAX=10
MAX_PARAMETERS=5

# ── Framework Version Strings ─────────────────────────────────────────
# Canonical display forms for framework references

NIST_SP_800_53_VERSION="Rev 5.2"
NIST_AI_RMF_VERSION="1.0"
NIST_SP_800_218A_VERSION="Final"
NIST_AI_600_1_VERSION="1.0"
OWASP_LLM_VERSION="2025"
OWASP_AGENTIC_VERSION="2026"
