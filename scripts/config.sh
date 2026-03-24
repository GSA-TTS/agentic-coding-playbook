#!/bin/sh
# config.sh — Centralized schema constants for agentic-ai-playbook
#
# POSIX sh compatible.
# This file defines constants only and should be sourced.
#
# shellcheck disable=SC2034

# ── Document Frontmatter Schema ──────────────────────────────────────

REQUIRED_FRONTMATTER_FIELDS='
title
description
status
tier
'

OPTIONAL_FRONTMATTER_FIELDS='
last_updated
nist_controls
frameworks
audience
keywords
related_files
load_priority
review_cycle
'

DOC_STATUS_VALUES='
canonical
draft
deprecated
'
DOC_STATUS_REGEX='^(canonical|draft|deprecated)$'

DOC_TIER_VALUES='
1
2
3
'
DOC_TIER_REGEX='^[123]$'

DOC_AUDIENCE_VALUES='
developers
isso
managers
all
'

DOC_LOAD_PRIORITY_VALUES='
always
task-context
on-demand
reference-only
'
DOC_LOAD_PRIORITY_REGEX='^(always|task-context|on-demand|reference-only)$'

DOC_REVIEW_CYCLE_VALUES='
quarterly
semi-annually
annually
'

# ── ADR Schema ───────────────────────────────────────────────────────

REQUIRED_ADR_FIELDS='
title
status
date
nist_controls
'

ADR_STATUS_VALUES='
proposed
accepted
deprecated
superseded
'
ADR_STATUS_REGEX='^(proposed|accepted|deprecated|superseded)$'
ADR_FILENAME_REGEX='^[0-9][0-9][0-9][0-9]-[a-z0-9-][a-z0-9-]*\.md$'

# ── NIST Control Format ──────────────────────────────────────────────

NIST_CONTROL_REGEX='^[A-Z][A-Z]-[0-9][0-9]*\(([0-9][0-9]*)\)\{0,1\}$'

# ── Skill Validation ─────────────────────────────────────────────────

SKILL_MAX_LINES=500
SKILL_NAME_MAX_LENGTH=64
SKILL_NAME_INVALID_CHARS_REGEX='[^a-z0-9-]'

# ── Size / Complexity Limits ─────────────────────────────────────────

FUNCTION_MAX_LINES=50
FILE_MAX_LINES=400
CYCLOMATIC_COMPLEXITY_MAX=10
MAX_PARAMETERS=5

# ── Framework Version Strings ────────────────────────────────────────

NIST_SP_800_53_VERSION='Rev 5.2'
NIST_AI_RMF_VERSION='1.0'
NIST_SP_800_218A_VERSION='Final'
NIST_AI_600_1_VERSION='1.0'
OWASP_LLM_VERSION='2025'
OWASP_AGENTIC_VERSION='2026'
