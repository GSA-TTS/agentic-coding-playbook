"""Schema constants and validation helpers for the agentic-coding-playbook.

Single source of truth for validation rules, enum values, and limits.
Replaces scripts/config.sh.
"""

import re

# ── Document Frontmatter Schema ──────────────────────────────────────

REQUIRED_FRONTMATTER_FIELDS = frozenset({"title", "description", "status", "tier"})

OPTIONAL_FRONTMATTER_FIELDS = frozenset(
    {
        "last_updated",
        "nist_controls",
        "frameworks",
        "audience",
        "keywords",
        "related_files",
        "load_priority",
        "review_cycle",
    }
)

DOC_STATUS_VALUES = frozenset({"canonical", "draft", "deprecated"})
DOC_TIER_VALUES = frozenset({1, 2, 3})
DOC_AUDIENCE_VALUES = frozenset({"developers", "isso", "managers", "all"})
DOC_LOAD_PRIORITY_VALUES = frozenset({"always", "task-context", "on-demand", "reference-only"})
DOC_REVIEW_CYCLE_VALUES = frozenset({"quarterly", "semi-annually", "annually"})

# ── ADR (Decision Record) Schema ─────────────────────────────────────

REQUIRED_ADR_FIELDS = frozenset({"title", "status", "date", "nist_controls"})
ADR_STATUS_VALUES = frozenset({"proposed", "accepted", "deprecated", "superseded"})
ADR_FILENAME_PATTERN = re.compile(r"^[0-9]{4}-[a-z0-9-]+\.md$")

# ── NIST Control Format ──────────────────────────────────────────────

NIST_CONTROL_PATTERN = re.compile(r"^[A-Z]{2}-[0-9]+(\([0-9]+\))?$")

# ── Skill Validation ────────────────────────────────────────────────

SKILL_MAX_LINES = 500
SKILL_NAME_MAX_LENGTH = 64
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")

# ── Lock Files (shared by audit_repo and pre_deploy_checks) ────────

LOCK_FILES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Pipfile.lock",
        "poetry.lock",
        "go.sum",
        "Cargo.lock",
        "Gemfile.lock",
        "uv.lock",
    }
)

# ── Size and Complexity Limits ──────────────────────────────────────

FUNCTION_MAX_LINES = 50
FILE_MAX_LINES = 400
CYCLOMATIC_COMPLEXITY_MAX = 10
MAX_PARAMETERS = 5

# ── Framework Version Strings ───────────────────────────────────────

FRAMEWORK_VERSIONS = {
    "nist_sp_800_53": "Rev 5.2",
    "nist_ai_rmf": "1.0",
    "nist_sp_800_218a": "Final",
    "nist_ai_600_1": "1.0",
    "owasp_llm": "2025",
    "owasp_agentic": "2026",
}


# ── Validation Helpers ──────────────────────────────────────────────


def is_valid_status(value: str) -> bool:
    """Check if a document status value is valid."""
    return value in DOC_STATUS_VALUES


def is_valid_tier(value: int) -> bool:
    """Check if a document tier value is valid."""
    return value in DOC_TIER_VALUES


def is_valid_nist_control(value: str) -> bool:
    """Check if a string matches the NIST control ID format (e.g., AC-3, CM-7(5))."""
    return bool(NIST_CONTROL_PATTERN.match(value))


def is_valid_skill_name(value: str) -> bool:
    """Check if a skill name follows conventions (lowercase, hyphens, max 64 chars)."""
    if not value or len(value) > SKILL_NAME_MAX_LENGTH:
        return False
    return bool(SKILL_NAME_PATTERN.match(value))
