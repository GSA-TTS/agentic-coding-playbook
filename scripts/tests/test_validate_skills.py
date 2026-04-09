"""Tests for skill directory validation."""

import yaml
from playbook_validator.validate_skills import find_skill_dirs, validate_skill


def _make_skill(tmp_path, name, frontmatter=None, body="# Skill content\n", lines=None):
    """Helper to create a skill directory with SKILL.md for testing."""
    skill_dir = tmp_path / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"

    if frontmatter is not None:
        fm_text = yaml.dump(frontmatter, default_flow_style=False)
        content = f"---\n{fm_text}---\n{body}"
    else:
        content = body

    if lines is not None:
        # Pad content to reach desired line count
        current = content.count("\n")
        if current < lines:
            content += "\n" * (lines - current)

    skill_file.write_text(content)
    return skill_dir


class TestFindSkillDirs:
    """Test skill directory discovery."""

    def test_finds_skill_dirs(self, tmp_path):
        _make_skill(tmp_path, "code-review", {"name": "code-review", "description": "Review code"})
        _make_skill(tmp_path, "testing", {"name": "testing", "description": "Write tests"})

        dirs = find_skill_dirs(tmp_path)
        names = sorted(d.name for d in dirs)
        assert names == ["code-review", "testing"]

    def test_empty_skills_dir(self, tmp_path):
        (tmp_path / "skills").mkdir()
        assert find_skill_dirs(tmp_path) == []

    def test_no_skills_dir(self, tmp_path):
        assert find_skill_dirs(tmp_path) == []

    def test_ignores_files_in_skills_root(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "README.md").write_text("# Skills\n")
        assert find_skill_dirs(tmp_path) == []


class TestValidateSkill:
    """Test single skill validation."""

    def test_valid_skill(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "code-review",
            {
                "name": "code-review",
                "description": "Automated code review",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert errors == []
        assert warnings == []

    def test_missing_skill_md(self, tmp_path):
        skill_dir = tmp_path / "skills" / "broken"
        skill_dir.mkdir(parents=True)
        errors, warnings = validate_skill(skill_dir)
        assert any("missing SKILL.md" in e for e in errors)

    def test_missing_frontmatter(self, tmp_path):
        skill_dir = _make_skill(tmp_path, "no-fm", frontmatter=None, body="# No frontmatter\n")
        errors, warnings = validate_skill(skill_dir)
        assert any("frontmatter" in e.lower() for e in errors)

    def test_missing_required_field_name(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "no-name",
            {
                "description": "Has description but no name",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("name" in e for e in errors)

    def test_missing_required_field_description(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "no-desc",
            {
                "name": "no-desc",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("description" in e for e in errors)

    def test_name_mismatch(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "actual-name",
            {
                "name": "different-name",
                "description": "Name does not match directory",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("does not match" in e for e in errors)

    def test_name_invalid_uppercase(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "BadName",
            {
                "name": "BadName",
                "description": "Uppercase chars",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("invalid" in e.lower() for e in errors)

    def test_name_leading_hyphen(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "-leading",
            {
                "name": "-leading",
                "description": "Leading hyphen",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("invalid" in e.lower() or "hyphen" in e.lower() for e in errors)

    def test_name_trailing_hyphen(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "trailing-",
            {
                "name": "trailing-",
                "description": "Trailing hyphen",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("invalid" in e.lower() or "hyphen" in e.lower() for e in errors)

    def test_name_consecutive_hyphens(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "bad--name",
            {
                "name": "bad--name",
                "description": "Consecutive hyphens",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("consecutive" in e.lower() for e in errors)

    def test_name_too_long(self, tmp_path):
        long_name = "a" * 65
        skill_dir = _make_skill(
            tmp_path,
            long_name,
            {
                "name": long_name,
                "description": "Name too long",
            },
        )
        errors, warnings = validate_skill(skill_dir)
        assert any("64" in e or "exceeds" in e.lower() for e in errors)

    def test_line_count_warning(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "verbose-skill",
            {
                "name": "verbose-skill",
                "description": "Very long skill file",
            },
            lines=501,
        )
        errors, warnings = validate_skill(skill_dir)
        assert errors == []
        assert any("lines" in w for w in warnings)

    def test_line_count_at_limit_no_warning(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "ok-skill",
            {
                "name": "ok-skill",
                "description": "Exactly at limit",
            },
            lines=500,
        )
        errors, warnings = validate_skill(skill_dir)
        assert warnings == []

    def test_index_cross_validation_present(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "indexed-skill",
            {
                "name": "indexed-skill",
                "description": "In the index",
            },
        )
        index_skills = {"indexed-skill", "other-skill"}
        errors, warnings = validate_skill(skill_dir, index_skills=index_skills)
        assert errors == []

    def test_index_cross_validation_missing(self, tmp_path):
        skill_dir = _make_skill(
            tmp_path,
            "unlisted-skill",
            {
                "name": "unlisted-skill",
                "description": "Not in the index",
            },
        )
        index_skills = {"other-skill"}
        errors, warnings = validate_skill(skill_dir, index_skills=index_skills)
        assert any("INDEX.yaml" in e for e in errors)
