"""PROJECT_PLAN.md validation.

Validates that a PROJECT_PLAN.md has required sections filled in
(not still placeholder comments) before bootstrap can proceed.
"""

import re
from pathlib import Path

# Sections that MUST exist and have content (not just placeholders)
REQUIRED_SECTIONS = {
    "project identity",
    "business objective",
    "tech stack",
    "compliance level",
}

# Sections that SHOULD exist (warnings if missing)
OPTIONAL_SECTIONS = {
    "data classification",
    "key requirements",
    "constraints",
    "team",
    "agent environment",
    "implementation approach",
}

# Patterns that indicate unfilled placeholder content
PLACEHOLDER_PATTERNS = [
    re.compile(r"<!--.*?-->"),  # HTML comments (template hints)
    re.compile(r"\{\{.*?\}\}"),  # Mustache-style placeholders
]

# Compliance level must have at least one checked checkbox
CHECKED_CHECKBOX = re.compile(r"^\s*-\s*\[x\]", re.MULTILINE | re.IGNORECASE)


def _extract_sections(text: str) -> dict[str, str]:
    """Extract markdown sections (## headings) and their content."""
    sections: dict[str, str] = {}
    current_heading = ""
    current_content: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading:
                sections[current_heading] = "\n".join(current_content).strip()
            current_heading = line[3:].strip().lower()
            current_content = []
        else:
            current_content.append(line)

    if current_heading:
        sections[current_heading] = "\n".join(current_content).strip()

    return sections


def _is_placeholder_only(text: str) -> bool:
    """Check if text is only placeholder content (HTML comments, empty)."""
    stripped = text.strip()
    if not stripped:
        return True
    # Remove all placeholder patterns
    cleaned = stripped
    for pattern in PLACEHOLDER_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    # Remove markdown table headers/separators and whitespace
    cleaned = re.sub(r"\|[- |]*\|", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    return len(cleaned) == 0


def validate_project_plan(path: Path) -> tuple[list[str], list[str]]:
    """Validate a PROJECT_PLAN.md file.

    Returns (errors, warnings) as lists of human-readable messages.
    Errors = must fix before bootstrap. Warnings = should fix but not blocking.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        errors.append(f"File not found: {path}")
        return errors, warnings

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        errors.append(f"{path.name}: file is empty")
        return errors, warnings

    sections = _extract_sections(text)

    # Check required sections exist and have content
    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"{path.name}: missing required section: ## {section.title()}")
        elif _is_placeholder_only(sections[section]):
            errors.append(f"{path.name}: ## {section.title()} has only placeholder content — fill it in")

    # Check compliance level has a checked checkbox
    if "compliance level" in sections:
        content = sections["compliance level"]
        if not _is_placeholder_only(content) and not CHECKED_CHECKBOX.search(content):
            errors.append(f"{path.name}: ## Compliance Level — no FIPS level selected (check a box with [x])")

    # Check business objective is not just a comment
    if "business objective" in sections:
        content = sections["business objective"]
        if content and not _is_placeholder_only(content):
            # Content exists and isn't just placeholders — good
            pass
        elif content:
            errors.append(f"{path.name}: ## Business Objective has only placeholder content — fill it in")

    # Check for unfilled table placeholders in Project Identity
    if "project identity" in sections:
        identity = sections["project identity"]
        if "<!-- e.g." in identity or "<!-- " in identity:
            errors.append(f"{path.name}: ## Project Identity has unfilled placeholder values")

    # Check for unfilled table placeholders in Tech Stack
    if "tech stack" in sections:
        stack = sections["tech stack"]
        if "<!-- e.g." in stack or "<!-- " in stack:
            errors.append(f"{path.name}: ## Tech Stack has unfilled placeholder values")

    # Warn about missing optional sections
    for section in OPTIONAL_SECTIONS:
        if section not in sections:
            warnings.append(f"{path.name}: optional section missing: ## {section.title()} — consider adding it")

    return errors, warnings
