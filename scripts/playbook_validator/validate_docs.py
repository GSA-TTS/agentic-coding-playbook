"""Document frontmatter validation.

Validates that all content Markdown files have correct frontmatter
with required fields and valid enum values.
"""

from pathlib import Path

from playbook_validator.config import (
    CONTRACT_ROLE_FIELD,
    CONTRACT_ROLE_UNIVERSAL,
    CONTRACT_ROLE_VALUES,
    DOC_LOAD_PRIORITY_VALUES,
    DOC_STATUS_VALUES,
    DOC_TIER_VALUES,
    REQUIRED_FRONTMATTER_FIELDS,
)
from playbook_validator.frontmatter import extract_frontmatter

# Files excluded from frontmatter validation
EXCLUDED_FILENAMES = frozenset(
    {
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "LICENSE",
        "TRANSFER.md",
    }
)

# Directories excluded from content file discovery
EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".github",
        ".claude",
        "node_modules",
        "skills",
        "data",
        "templates",
        "decisions",
    }
)


def find_content_files(root: Path) -> list[Path]:
    """Find all Markdown content files that need frontmatter validation.

    Excludes meta-files (README, CONTRIBUTING, etc.), skills directory,
    and hidden/build directories.
    """
    results: list[Path] = []
    for md_file in sorted(root.rglob("*.md")):
        # Skip excluded directories
        parts = md_file.relative_to(root).parts
        if any(part in EXCLUDED_DIRS for part in parts):
            continue
        # Skip excluded filenames
        if md_file.name in EXCLUDED_FILENAMES:
            continue
        results.append(md_file)
    return results


def validate_doc_frontmatter(path: Path) -> tuple[list[str], list[str]]:
    """Validate frontmatter of a single document.

    Returns (errors, warnings) as lists of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    fm = extract_frontmatter(path)
    if not fm:
        errors.append(f"{path} — missing YAML frontmatter")
        return errors, warnings

    # Required fields
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fm:
            errors.append(f"{path} — missing required field: {field}")

    # Status validation
    status = fm.get("status")
    if status is not None and status not in DOC_STATUS_VALUES:
        errors.append(f"{path} — invalid status: '{status}' (must be one of {sorted(DOC_STATUS_VALUES)})")

    # Tier validation
    tier = fm.get("tier")
    if tier is not None and tier not in DOC_TIER_VALUES:
        errors.append(f"{path} — invalid tier: '{tier}' (must be one of {sorted(DOC_TIER_VALUES)})")

    # Load priority validation (optional field)
    load_priority = fm.get("load_priority")
    if load_priority is not None and load_priority not in DOC_LOAD_PRIORITY_VALUES:
        errors.append(
            f"{path} — invalid load_priority: '{load_priority}' (must be one of {sorted(DOC_LOAD_PRIORITY_VALUES)})"
        )

    # Behavioral-contract role validation (optional field). When present it must
    # be a recognized value; the universal-vs-thin invariant is checked in
    # validate_contract_role() at the repository level.
    contract_role = fm.get(CONTRACT_ROLE_FIELD)
    if contract_role is not None and contract_role not in CONTRACT_ROLE_VALUES:
        errors.append(
            f"{path} — invalid {CONTRACT_ROLE_FIELD}: '{contract_role}' (must be one of {sorted(CONTRACT_ROLE_VALUES)})"
        )

    return errors, warnings


# Paths (repo-root-relative) that MUST NOT claim the canonical universal role —
# they are thin project layers that only *reference* the universal contract.
_THIN_LAYER_PATHS = (
    "templates/AGENTS.md.template",
    "examples/AGENTS.md.example",
)


def validate_contract_role(root: Path) -> tuple[list[str], list[str]]:
    """Enforce the canonical-designation invariant across the repository.

    The universal behavioral contract (repo-root ``AGENTS.md``) MUST declare
    ``agents_contract: universal`` so tooling recognizes it by an explicit,
    version-controlled marker (issue #151, ADR-0003). The thin project layers
    (template and example) MUST NOT claim that role — otherwise a bootstrapped
    project's own AGENTS.md could self-satisfy the contract probe.

    Returns (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    universal = root / "AGENTS.md"
    if universal.is_file():
        role = extract_frontmatter(universal).get(CONTRACT_ROLE_FIELD)
        if role != CONTRACT_ROLE_UNIVERSAL:
            errors.append(
                f"{universal} — universal contract MUST declare "
                f"{CONTRACT_ROLE_FIELD}: {CONTRACT_ROLE_UNIVERSAL} (found: {role!r})"
            )

    for rel in _THIN_LAYER_PATHS:
        thin = root / rel
        if not thin.is_file():
            continue
        role = extract_frontmatter(thin).get(CONTRACT_ROLE_FIELD)
        if role == CONTRACT_ROLE_UNIVERSAL:
            errors.append(
                f"{thin} — thin project layer MUST NOT declare "
                f"{CONTRACT_ROLE_FIELD}: {CONTRACT_ROLE_UNIVERSAL} "
                "(only the universal contract may); this would let a bootstrapped "
                "project self-satisfy the contract probe (#151)"
            )

    return errors, warnings
