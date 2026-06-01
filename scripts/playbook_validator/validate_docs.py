"""Document frontmatter validation.

Validates that all content Markdown files have correct frontmatter
with required fields and valid enum values.
"""

from pathlib import Path

from playbook_validator.config import (
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

    return errors, warnings
