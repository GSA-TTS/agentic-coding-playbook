"""Tests for frontmatter extraction module."""

import textwrap

from playbook_validator.frontmatter import extract_frontmatter, get_array_field, get_field


class TestExtractFrontmatter:
    """Test raw frontmatter block extraction."""

    def test_basic_frontmatter(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: Hello\nstatus: canonical\n---\n\n# Body\n")
        fm = extract_frontmatter(md)
        assert fm["title"] == "Hello"
        assert fm["status"] == "canonical"

    def test_no_frontmatter(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Just a heading\n\nSome text.\n")
        fm = extract_frontmatter(md)
        assert fm == {}

    def test_empty_file(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("")
        fm = extract_frontmatter(md)
        assert fm == {}

    def test_multiline_description(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: Test
            description: >
              This is a long
              multiline description
            status: canonical
            ---
            # Body
        """)
        )
        fm = extract_frontmatter(md)
        assert "long" in fm["description"]
        assert "multiline" in fm["description"]

    def test_quoted_values(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('---\ntitle: "Quoted Title"\nstatus: canonical\n---\n')
        fm = extract_frontmatter(md)
        assert fm["title"] == "Quoted Title"

    def test_array_field_inline(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('---\naudience: ["developers", "agents"]\n---\n')
        fm = extract_frontmatter(md)
        assert fm["audience"] == ["developers", "agents"]

    def test_array_field_block(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            triggers:
              - deploy
              - cloud.gov
              - sandbox
            ---
        """)
        )
        fm = extract_frontmatter(md)
        assert fm["triggers"] == ["deploy", "cloud.gov", "sandbox"]

    def test_integer_field(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntier: 2\n---\n")
        fm = extract_frontmatter(md)
        assert fm["tier"] == 2

    def test_colon_in_value(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('---\ntitle: "Phase 0.5: Environment Doctor"\n---\n')
        fm = extract_frontmatter(md)
        assert fm["title"] == "Phase 0.5: Environment Doctor"


class TestGetField:
    """Test single-field extraction convenience function."""

    def test_get_existing_field(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: Hello\nstatus: canonical\n---\n")
        assert get_field(md, "title") == "Hello"
        assert get_field(md, "status") == "canonical"

    def test_get_missing_field(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: Hello\n---\n")
        assert get_field(md, "nonexistent") is None

    def test_get_field_no_frontmatter(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Just a heading\n")
        assert get_field(md, "title") is None


class TestGetArrayField:
    """Test array field extraction convenience function."""

    def test_inline_array(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('---\naudience: ["developers", "agents"]\n---\n')
        assert get_array_field(md, "audience") == ["developers", "agents"]

    def test_block_array(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\nitems:\n  - one\n  - two\n  - three\n---\n")
        assert get_array_field(md, "items") == ["one", "two", "three"]

    def test_missing_array(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: Hello\n---\n")
        assert get_array_field(md, "items") is None

    def test_single_value_not_array(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: Hello\n---\n")
        # Non-list field returns None from get_array_field
        assert get_array_field(md, "title") is None
