"""YAML frontmatter extraction from Markdown files."""

from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter from raw Markdown text.

    Returns parsed YAML as a dict, or empty dict if no frontmatter found.
    Frontmatter must be delimited by --- on its own line at the start.
    """
    if not text.startswith("---"):
        return {}

    # Find the closing ---
    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fm_text = text[4:end]  # skip opening "---\n"
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def extract_frontmatter(path: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from a Markdown file.

    Returns parsed YAML as a dict, or empty dict if no frontmatter found.
    Frontmatter must be delimited by --- on its own line at the start of the file.
    """
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def get_field(path: Path, field: str) -> Any:
    """Extract a single frontmatter field value.

    Returns None if the field doesn't exist or there's no frontmatter.
    """
    fm = extract_frontmatter(path)
    return fm.get(field)


def get_array_field(path: Path, field: str) -> list[str] | None:
    """Extract an array frontmatter field.

    Returns None if the field doesn't exist, isn't a list, or there's no frontmatter.
    """
    fm = extract_frontmatter(path)
    value = fm.get(field)
    if not isinstance(value, list):
        return None
    return value
