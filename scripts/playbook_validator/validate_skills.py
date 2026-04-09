"""Agent skill directory validation.

Validates that skill directories under skills/ contain a well-formed
SKILL.md with correct frontmatter, naming conventions, and INDEX.yaml
cross-references.

Replaces scripts/validate-skills.sh.
"""

from pathlib import Path

from playbook_validator.config import (
    SKILL_MAX_LINES,
    SKILL_NAME_MAX_LENGTH,
    is_valid_skill_name,
)
from playbook_validator.frontmatter import extract_frontmatter

REQUIRED_SKILL_FIELDS = frozenset({"name", "description"})


def find_skill_dirs(root: Path) -> list[Path]:
    """Discover skill directories containing SKILL.md.

    Returns sorted list of immediate subdirectories under root/skills/
    that are actual directories (not files).
    """
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(d for d in skills_root.iterdir() if d.is_dir())


def validate_skill(
    skill_dir: Path,
    index_skills: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate a single skill directory.

    Args:
        skill_dir: Path to the skill directory (e.g., skills/code-review/).
        index_skills: Optional set of skill names from INDEX.yaml for
            cross-validation. When provided, the skill must appear in the set.

    Returns:
        (errors, warnings) as lists of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []
    skill_name = skill_dir.name
    skill_file = skill_dir / "SKILL.md"

    # Check 1: SKILL.md exists
    if not skill_file.is_file():
        errors.append(f"{skill_dir} — missing SKILL.md")
        return errors, warnings

    # Check 2: YAML frontmatter present
    fm = extract_frontmatter(skill_file)
    if not fm:
        errors.append(f"{skill_file} — missing YAML frontmatter")
        return errors, warnings

    # Check 3: Required frontmatter fields
    for field in sorted(REQUIRED_SKILL_FIELDS):
        if field not in fm:
            errors.append(f"{skill_file} — missing required field: {field}")

    # Check 4: name matches directory name
    name_field = fm.get("name")
    if name_field is not None and name_field != skill_name:
        errors.append(f"{skill_file} — name field '{name_field}' does not match directory name '{skill_name}'")

    # Check 5: name format validation
    if name_field is not None:
        if not is_valid_skill_name(name_field):
            errors.append(
                f"{skill_file} — name '{name_field}' contains invalid characters "
                f"(must be lowercase alphanumeric and hyphens, max {SKILL_NAME_MAX_LENGTH} chars)"
            )
        if "--" in str(name_field):
            errors.append(f"{skill_file} — name '{name_field}' must not contain consecutive hyphens")

    # Check 6: Line count warning
    text = skill_file.read_text(encoding="utf-8")
    line_count = text.count("\n")
    if line_count > SKILL_MAX_LINES:
        warnings.append(f"{skill_file} — {line_count} lines (recommended: <{SKILL_MAX_LINES})")

    # Check 7: INDEX.yaml cross-validation
    if index_skills is not None and skill_name not in index_skills:
        errors.append(f"skill '{skill_name}' exists on disk but is missing from INDEX.yaml")

    return errors, warnings
