"""Tests for document validation module."""

import textwrap

from playbook_validator.validate_docs import find_content_files, validate_doc_frontmatter


class TestValidateDocFrontmatter:
    """Test frontmatter validation on individual files."""

    def test_valid_doc(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test Doc"
            description: "A test document"
            status: canonical
            tier: 2
            ---
            # Content
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert errors == []
        assert warnings == []

    def test_missing_required_field(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            ---
            # Missing tier
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("tier" in e for e in errors)

    def test_no_frontmatter(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Just a heading\n")
        errors, warnings = validate_doc_frontmatter(md)
        assert any("frontmatter" in e.lower() for e in errors)

    def test_invalid_status(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: invalid_status
            tier: 2
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("status" in e for e in errors)

    def test_invalid_tier(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 5
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("tier" in e for e in errors)

    def test_invalid_load_priority(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 2
            load_priority: invalid
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("load_priority" in e for e in errors)

    def test_valid_optional_fields(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 1
            load_priority: always
            audience: ["developers"]
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert errors == []


class TestFindContentFiles:
    """Test content file discovery."""

    def test_finds_md_files(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("---\ntitle: Guide\n---\n")
        (tmp_path / "PLAYBOOK.md").write_text("---\ntitle: Playbook\n---\n")
        files = find_content_files(tmp_path)
        filenames = [f.name for f in files]
        assert "guide.md" in filenames
        assert "PLAYBOOK.md" in filenames

    def test_excludes_meta_files(self, tmp_path):
        (tmp_path / "README.md").write_text("# Readme")
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
        (tmp_path / "CHANGELOG.md").write_text("# Changelog")
        (tmp_path / "SECURITY.md").write_text("# Security")
        files = find_content_files(tmp_path)
        filenames = [f.name for f in files]
        assert "README.md" not in filenames
        assert "CONTRIBUTING.md" not in filenames

    def test_excludes_skills_dir(self, tmp_path):
        skills = tmp_path / "skills" / "test-skill"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("---\ntitle: Skill\n---\n")
        files = find_content_files(tmp_path)
        filenames = [f.name for f in files]
        assert "SKILL.md" not in filenames

    def test_excludes_git_dir(self, tmp_path):
        git = tmp_path / ".git"
        git.mkdir()
        (git / "config.md").write_text("not a real doc")
        files = find_content_files(tmp_path)
        assert len(files) == 0

    def test_excludes_decisions_dir(self, tmp_path):
        # ADRs in docs/decisions/ use MADR frontmatter (status: accepted, date,
        # decision_makers) and are validated by validate-adrs, not the tiered
        # content-doc rules. They MUST be excluded from find_content_files.
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        (decisions / "0001-some-decision.md").write_text(
            "---\ntitle: A decision\nstatus: accepted\ndate: 2026-06-22\n---\n"
        )
        files = find_content_files(tmp_path)
        assert "0001-some-decision.md" not in [f.name for f in files]
