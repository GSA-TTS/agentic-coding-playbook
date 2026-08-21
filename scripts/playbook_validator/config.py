"""Schema constants and validation helpers for the agentic-coding-playbook.

Single source of truth for validation rules, enum values, and limits.
"""

import re

# ── Document Frontmatter Schema ──────────────────────────────────────

REQUIRED_FRONTMATTER_FIELDS = frozenset({"title", "description", "status", "tier"})

OPTIONAL_FRONTMATTER_FIELDS = frozenset(
    {
        "last_updated",
        "stale_after",
        "nist_controls",
        "frameworks",
        "audience",
        "keywords",
        "related_files",
        "load_priority",
        "review_cycle",
        "contract",
    }
)

DOC_STATUS_VALUES = frozenset({"canonical", "draft", "deprecated"})
DOC_TIER_VALUES = frozenset({1, 2, 3})
DOC_AUDIENCE_VALUES = frozenset({"developers", "isso", "managers", "agents", "all"})
DOC_LOAD_PRIORITY_VALUES = frozenset({"always", "task-context", "on-demand", "reference-only"})
DOC_REVIEW_CYCLE_VALUES = frozenset({"quarterly", "semi-annually", "annually"})

# ── Structural (non-content) files & dirs excluded from doc scanning ──
#
# SINGLE SOURCE OF TRUTH (#248). Both the frontmatter validator
# (validate_docs) and the index generator (generate_index) exclude these, and
# they MUST agree — otherwise a file can be indexed by one and never validated
# by the other (a real gap: a tier-3 template shipped an invalid enum value that
# was indexed into INDEX.yaml but structurally unreachable by validation).
#
# Repository meta-files: standard OSS/community health files that legitimately
# carry no frontmatter. The AGENTS.md §13.2 exemption prose is reconciled to
# THIS list (#247) — keep the two in lockstep.
STRUCTURAL_EXCLUDED_FILENAMES = frozenset(
    {
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "SUPPORT.md",
        "GOVERNANCE.md",
        "ACCESSIBILITY.md",
        "LICENSE",
        "TRANSFER.md",
    }
)

# Directories excluded from *content* discovery. `.agents` holds the canonical
# skills tree (validated by validate-skills, not validate-docs); the rest are
# VCS/CI/build/data dirs with no frontmatter-bearing content docs.
STRUCTURAL_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".github",
        ".claude",
        ".agents",
        "node_modules",
        "skills",
        "data",
        "decisions",
    }
)

# ── Behavioral-Contract Designation (canonical, versioned) ───────────
#
# The universal behavioral contract (this repo's own AGENTS.md) declares its
# identity EXPLICITLY in a structured, versioned frontmatter block, so tooling
# recognizes it by a deliberate signal rather than by fragile content detection
# (a title substring or section heading, which the thin project layer
# legitimately reproduces):
#
#     contract:
#       role: universal
#       version: "1.0.0"
#
# The thin project layer carries `contract.role: project-layer` (and a
# `requires_contract` range), so a downstream project's own AGENTS.md can never
# be mistaken for the universal contract even if it *names* the contract in its
# prose. `contract.version` is an INDEPENDENT semver for the behavioral rules
# (decoupled from the repo/release version): it bumps only when the rules change
# in a compatibility-relevant way, enabling future `requires_contract` checks.
# See issue #151 and ADR-0003.
CONTRACT_FIELD = "contract"
CONTRACT_ROLE_KEY = "role"
CONTRACT_VERSION_KEY = "version"
CONTRACT_REQUIRES_KEY = "requires_contract"
CONTRACT_ROLE_UNIVERSAL = "universal"
CONTRACT_ROLE_PROJECT = "project-layer"
CONTRACT_ROLE_VALUES = frozenset({CONTRACT_ROLE_UNIVERSAL, CONTRACT_ROLE_PROJECT})

# The current behavioral-contract version carried by the universal AGENTS.md.
# Bump when the universal rules change compatibly/incompatibly (its own semver,
# NOT the repo/release version).
CURRENT_CONTRACT_VERSION = "1.0.0"


def contract_block(frontmatter: dict) -> dict:
    """Return the ``contract`` mapping from parsed frontmatter, or {} if absent
    or malformed. Never raises on unexpected shapes."""
    block = frontmatter.get(CONTRACT_FIELD)
    return block if isinstance(block, dict) else {}


def contract_role(frontmatter: dict) -> str | None:
    """Return ``contract.role`` from parsed frontmatter, or None."""
    role = contract_block(frontmatter).get(CONTRACT_ROLE_KEY)
    return role if isinstance(role, str) else None


def contract_version(frontmatter: dict) -> str | None:
    """Return ``contract.version`` from parsed frontmatter, or None."""
    version = contract_block(frontmatter).get(CONTRACT_VERSION_KEY)
    return version if isinstance(version, str) else None


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

# NOTE: these four limits are enforced (#261) — CYCLOMATIC_COMPLEXITY_MAX and
# MAX_PARAMETERS via ruff (C901 / PLR0913, configured in pyproject.toml), and
# FILE_MAX_LINES via scripts/tests/test_file_size_limits.py. FUNCTION_MAX_LINES
# is enforced as a statement ceiling via ruff PLR0915 (max-statements). Keep the
# ruff config's numeric values in sync with these constants.


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
