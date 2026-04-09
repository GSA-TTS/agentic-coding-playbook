"""Tests for INDEX.yaml generation module."""

import textwrap

import yaml
from playbook_validator.generate_index import (
    DocumentInfo,
    SkillInfo,
    check_mode,
    collect_documents,
    collect_skills,
    compute_stats,
    render_index_yaml,
)
from playbook_validator.index_updaters import (
    inject_readme_table,
    render_skills_table,
    update_context_guide_word_counts,
)

# ── Helpers ────────────────────────────────────────────────────────


def _write_md(
    path,
    tier=1,
    title="Test",
    description="A test doc",
    status="canonical",
    nist_controls=None,
    frameworks=None,
    extra="",
):
    """Write a minimal frontmatter markdown file."""
    fm_lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f"status: {status}",
        f"tier: {tier}",
    ]
    if nist_controls:
        fm_lines.append(f"nist_controls: {nist_controls}")
    if frameworks:
        fm_lines.append(f"frameworks: {frameworks}")
    if extra:
        fm_lines.append(extra)
    fm_lines.append("---")
    fm_lines.append("# Content")
    path.write_text("\n".join(fm_lines) + "\n")


def _make_skill(skills_dir, name, description="A skill", scripts=None):
    """Create a skill directory with SKILL.md and optional scripts."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        textwrap.dedent(f"""\
        ---
        name: {name}
        description: "{description}"
        status: canonical
        tier: 2
        ---
        # Skill: {name}
    """)
    )
    if scripts:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        for s in scripts:
            (scripts_dir / s).write_text("#!/bin/bash\n")
    return skill_dir


# ── Document collection tests ─────────────────────────────────────


class TestCollectDocuments:
    """Test document collection and tier classification."""

    def test_collects_md_files_with_frontmatter(self, tmp_path):
        _write_md(tmp_path / "doc.md", tier=1)
        docs = collect_documents(tmp_path)
        assert len(docs) == 1
        assert docs[0].path == "doc.md"
        assert docs[0].tier == 1

    def test_classifies_tiers_correctly(self, tmp_path):
        _write_md(tmp_path / "core.md", tier=1)
        _write_md(tmp_path / "guide.md", tier=2)
        _write_md(tmp_path / "template.md", tier=3)
        docs = collect_documents(tmp_path)
        tiers = {d.path: d.tier for d in docs}
        assert tiers == {"core.md": 1, "guide.md": 2, "template.md": 3}

    def test_excludes_readme_and_changelog(self, tmp_path):
        _write_md(tmp_path / "README.md", tier=1)
        _write_md(tmp_path / "CHANGELOG.md", tier=1)
        _write_md(tmp_path / "CONTRIBUTING.md", tier=1)
        _write_md(tmp_path / "real-doc.md", tier=2)
        docs = collect_documents(tmp_path)
        assert len(docs) == 1
        assert docs[0].path == "real-doc.md"

    def test_excludes_skills_directory(self, tmp_path):
        (tmp_path / "skills").mkdir()
        _write_md(tmp_path / "skills" / "someskill.md", tier=1)
        _write_md(tmp_path / "real-doc.md", tier=1)
        docs = collect_documents(tmp_path)
        assert len(docs) == 1
        assert docs[0].path == "real-doc.md"

    def test_excludes_git_directory(self, tmp_path):
        (tmp_path / ".git").mkdir()
        _write_md(tmp_path / ".git" / "internal.md", tier=1)
        _write_md(tmp_path / "real.md", tier=1)
        docs = collect_documents(tmp_path)
        assert len(docs) == 1

    def test_collects_template_and_example_files(self, tmp_path):
        (tmp_path / "templates").mkdir()
        _write_md(tmp_path / "templates" / "AGENTS.md.template", tier=3)
        (tmp_path / "examples").mkdir()
        _write_md(tmp_path / "examples" / "AGENTS.md.example", tier=3)
        docs = collect_documents(tmp_path)
        assert len(docs) == 2
        paths = {d.path for d in docs}
        assert "templates/AGENTS.md.template" in paths
        assert "examples/AGENTS.md.example" in paths

    def test_skips_files_without_frontmatter(self, tmp_path):
        (tmp_path / "no-fm.md").write_text("# Just a heading\nNo frontmatter.\n")
        _write_md(tmp_path / "with-fm.md", tier=1)
        docs = collect_documents(tmp_path)
        assert len(docs) == 1
        assert docs[0].path == "with-fm.md"

    def test_sorted_by_path(self, tmp_path):
        _write_md(tmp_path / "zebra.md", tier=1)
        (tmp_path / "docs").mkdir()
        _write_md(tmp_path / "docs" / "alpha.md", tier=2)
        _write_md(tmp_path / "beta.md", tier=1)
        docs = collect_documents(tmp_path)
        paths = [d.path for d in docs]
        assert paths == sorted(paths)


# ── Skill collection tests ────────────────────────────────────────


class TestCollectSkills:
    """Test skill metadata extraction."""

    def test_collects_skill_with_metadata(self, tmp_path):
        (tmp_path / "skills").mkdir()
        _make_skill(tmp_path / "skills", "test-skill", description="Does testing")
        skills = collect_skills(tmp_path)
        assert len(skills) == 1
        assert skills[0].name == "test-skill"
        assert skills[0].description == "Does testing"
        assert skills[0].has_scripts is False
        assert skills[0].scripts == []

    def test_detects_scripts(self, tmp_path):
        (tmp_path / "skills").mkdir()
        _make_skill(
            tmp_path / "skills",
            "with-scripts",
            description="Has scripts",
            scripts=["check.sh", "validate.py"],
        )
        skills = collect_skills(tmp_path)
        assert len(skills) == 1
        assert skills[0].has_scripts is True
        assert len(skills[0].scripts) == 2
        assert any("check.sh" in s for s in skills[0].scripts)
        assert any("validate.py" in s for s in skills[0].scripts)

    def test_skips_dirs_without_skill_md(self, tmp_path):
        (tmp_path / "skills").mkdir()
        (tmp_path / "skills" / "empty-skill").mkdir()
        _make_skill(tmp_path / "skills", "valid-skill")
        skills = collect_skills(tmp_path)
        assert len(skills) == 1
        assert skills[0].name == "valid-skill"

    def test_no_skills_directory(self, tmp_path):
        skills = collect_skills(tmp_path)
        assert skills == []

    def test_sorted_by_name(self, tmp_path):
        (tmp_path / "skills").mkdir()
        _make_skill(tmp_path / "skills", "zebra-skill")
        _make_skill(tmp_path / "skills", "alpha-skill")
        skills = collect_skills(tmp_path)
        names = [s.name for s in skills]
        assert names == ["alpha-skill", "zebra-skill"]


# ── Stats computation tests ───────────────────────────────────────


class TestComputeStats:
    """Test stats computation (counts, unique controls, frameworks)."""

    def test_counts_documents_and_skills(self, tmp_path):
        docs = [
            DocumentInfo.from_frontmatter("a.md", {"title": "A", "description": "A", "status": "canonical", "tier": 1}),
            DocumentInfo.from_frontmatter("b.md", {"title": "B", "description": "B", "status": "canonical", "tier": 2}),
            DocumentInfo.from_frontmatter("c.md", {"title": "C", "description": "C", "status": "canonical", "tier": 3}),
        ]
        skills = [SkillInfo("s1", "skills/s1/SKILL.md", "Skill 1", False, [])]
        stats = compute_stats(docs, skills)
        assert stats.total_documents == 3
        assert stats.total_skills == 1
        assert stats.tier_1_core == 1
        assert stats.tier_2_supporting == 1
        assert stats.tier_3_templates == 1

    def test_unique_nist_controls(self):
        docs = [
            DocumentInfo.from_frontmatter(
                "a.md",
                {
                    "title": "A",
                    "description": "A",
                    "status": "canonical",
                    "tier": 1,
                    "nist_controls": ["AC-3", "CM-7", "SI-10"],
                },
            ),
            DocumentInfo.from_frontmatter(
                "b.md",
                {
                    "title": "B",
                    "description": "B",
                    "status": "canonical",
                    "tier": 2,
                    "nist_controls": ["AC-3", "AU-6"],  # AC-3 is duplicate
                },
            ),
        ]
        stats = compute_stats(docs, [])
        assert stats.total_nist_controls_referenced == 4  # AC-3, CM-7, SI-10, AU-6

    def test_unique_frameworks(self):
        docs = [
            DocumentInfo.from_frontmatter(
                "a.md",
                {
                    "title": "A",
                    "description": "A",
                    "status": "canonical",
                    "tier": 1,
                    "frameworks": ["NIST 800-53", "OWASP LLM"],
                },
            ),
            DocumentInfo.from_frontmatter(
                "b.md",
                {
                    "title": "B",
                    "description": "B",
                    "status": "canonical",
                    "tier": 2,
                    "frameworks": ["NIST 800-53", "FedRAMP"],  # 800-53 dup
                },
            ),
        ]
        stats = compute_stats(docs, [])
        assert stats.frameworks_covered == 3  # NIST 800-53, OWASP LLM, FedRAMP

    def test_empty_inputs(self):
        stats = compute_stats([], [])
        assert stats.total_documents == 0
        assert stats.total_skills == 0
        assert stats.total_nist_controls_referenced == 0
        assert stats.frameworks_covered == 0


# ── YAML generation tests ─────────────────────────────────────────


class TestRenderIndexYaml:
    """Test INDEX.yaml generation (verify YAML structure)."""

    def test_valid_yaml_output(self):
        docs = [
            DocumentInfo.from_frontmatter(
                "doc.md",
                {
                    "title": "Test",
                    "description": "A test",
                    "status": "canonical",
                    "tier": 1,
                },
            )
        ]
        stats = compute_stats(docs, [])
        output = render_index_yaml(docs, [], stats, generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        assert parsed["schema_version"] == "1.0"
        assert parsed["generated"] == "2026-01-01"
        assert len(parsed["documents"]) == 1
        assert parsed["documents"][0]["path"] == "doc.md"

    def test_contains_frontmatter_schema(self):
        output = render_index_yaml([], [], compute_stats([], []), generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        assert "frontmatter_schema" in parsed
        schema = parsed["frontmatter_schema"]
        assert "required" in schema
        assert "optional" in schema
        assert "status_values" in schema
        assert "tier_values" in schema

    def test_documents_grouped_by_tier(self):
        t3_fm = {"title": "T3", "description": "T3", "status": "canonical", "tier": 3}
        t1_fm = {"title": "T1", "description": "T1", "status": "canonical", "tier": 1}
        docs = [
            DocumentInfo.from_frontmatter("t3.md", t3_fm),
            DocumentInfo.from_frontmatter("t1.md", t1_fm),
        ]
        stats = compute_stats(docs, [])
        output = render_index_yaml(docs, [], stats, generated_date="2026-01-01")
        # Tier 1 header should appear before Tier 3 header in the output
        assert output.index("Tier 1") < output.index("Tier 3")

    def test_skills_section_rendered(self):
        skills = [
            SkillInfo("my-skill", "skills/my-skill/SKILL.md", "Does stuff", True, ["skills/my-skill/scripts/run.sh"])
        ]
        output = render_index_yaml([], skills, compute_stats([], skills), generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        assert "skills" in parsed
        assert parsed["skills"][0]["name"] == "my-skill"
        assert parsed["skills"][0]["has_scripts"] is True
        assert "skills/my-skill/scripts/run.sh" in parsed["skills"][0]["scripts"]

    def test_stats_section(self):
        docs = [
            DocumentInfo.from_frontmatter("a.md", {"title": "A", "description": "A", "status": "canonical", "tier": 1}),
            DocumentInfo.from_frontmatter("b.md", {"title": "B", "description": "B", "status": "canonical", "tier": 2}),
        ]
        stats = compute_stats(docs, [])
        output = render_index_yaml(docs, [], stats, generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        assert parsed["stats"]["total_documents"] == 2
        assert parsed["stats"]["tier_1_core"] == 1
        assert parsed["stats"]["tier_2_supporting"] == 1

    def test_optional_fields_included(self):
        docs = [
            DocumentInfo.from_frontmatter(
                "doc.md",
                {
                    "title": "T",
                    "description": "D",
                    "status": "canonical",
                    "tier": 1,
                    "load_priority": "always",
                    "last_updated": "2026-01-01",
                    "audience": "developers",
                    "review_cycle": "quarterly",
                    "nist_controls": ["AC-3", "SI-10"],
                },
            )
        ]
        stats = compute_stats(docs, [])
        output = render_index_yaml(docs, [], stats, generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        doc = parsed["documents"][0]
        assert doc["load_priority"] == "always"
        assert doc["last_updated"] == "2026-01-01"
        assert doc["audience"] == "developers"
        assert doc["review_cycle"] == "quarterly"
        assert doc["nist_controls_count"] == 2


# ── Check mode tests ──────────────────────────────────────────────


class TestCheckMode:
    """Test --check mode: match returns True (exit 0), diff returns False (exit 1)."""

    def test_matching_index_returns_true(self, tmp_path):
        _write_md(tmp_path / "doc.md", tier=1, title="Doc", description="Desc")
        # Generate first
        docs = collect_documents(tmp_path)
        skills = collect_skills(tmp_path)
        stats = compute_stats(docs, skills)
        content = render_index_yaml(docs, skills, stats)
        (tmp_path / "INDEX.yaml").write_text(content)
        assert check_mode(tmp_path) is True

    def test_different_index_returns_false(self, tmp_path):
        _write_md(tmp_path / "doc.md", tier=1, title="Doc", description="Desc")
        (tmp_path / "INDEX.yaml").write_text("schema_version: old\n")
        assert check_mode(tmp_path) is False

    def test_missing_index_returns_false(self, tmp_path):
        _write_md(tmp_path / "doc.md", tier=1)
        assert check_mode(tmp_path) is False

    def test_date_difference_ignored(self, tmp_path):
        _write_md(tmp_path / "doc.md", tier=1, title="Doc", description="Desc")
        docs = collect_documents(tmp_path)
        skills = collect_skills(tmp_path)
        stats = compute_stats(docs, skills)
        # Generate with a different date
        content = render_index_yaml(docs, skills, stats, generated_date="1999-01-01")
        (tmp_path / "INDEX.yaml").write_text(content)
        # check_mode generates with today's date, but should still match
        assert check_mode(tmp_path) is True


# ── README.md skills table injection tests ─────────────────────────


class TestInjectReadmeTable:
    """Test skills table injection into README.md."""

    def test_injects_table_between_markers(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            textwrap.dedent("""\
            # Title
            <!-- GENERATED:SKILLS_TABLE:START — do not edit -->
            | old | table |
            <!-- GENERATED:SKILLS_TABLE:END -->
            Footer
        """)
        )
        table = "| Skill | Purpose | Scripts? |\n|-------|---------|----------|\n| `test` | A test | No |"
        result = inject_readme_table(readme, table)
        assert result is True
        content = readme.read_text()
        assert "| `test` | A test | No |" in content
        assert "| old | table |" not in content
        assert "Footer" in content

    def test_no_markers_returns_false(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# Title\nNo markers here.\n")
        result = inject_readme_table(readme, "table")
        assert result is False

    def test_no_readme_returns_false(self, tmp_path):
        result = inject_readme_table(tmp_path / "README.md", "table")
        assert result is False


class TestRenderSkillsTable:
    """Test markdown skills table rendering."""

    def test_renders_header_and_rows(self):
        skills = [
            SkillInfo("alpha", "skills/alpha/SKILL.md", "Alpha skill", False, []),
            SkillInfo("beta", "skills/beta/SKILL.md", "Beta skill with scripts", True, ["scripts/run.sh"]),
        ]
        table = render_skills_table(skills)
        lines = table.strip().splitlines()
        assert lines[0] == "| Skill | Purpose | Scripts? |"
        assert lines[1] == "|-------|---------|----------|"
        assert "| `alpha` |" in lines[2]
        assert "| No |" in lines[2]
        assert "| `beta` |" in lines[3]
        assert "| Yes |" in lines[3]

    def test_truncates_long_descriptions(self):
        long_desc = "A" * 120 + ". Second sentence."
        skills = [SkillInfo("s", "skills/s/SKILL.md", long_desc, False, [])]
        table = render_skills_table(skills)
        # Should be truncated with ...
        assert "..." in table
        # Each row should be under a reasonable length
        for line in table.splitlines()[2:]:
            # The purpose column should not exceed ~93 chars (87 + "...")
            parts = line.split("|")
            purpose = parts[2].strip()
            assert len(purpose) <= 93


# ── Integration: end-to-end with tmp_path ──────────────────────────


class TestEndToEnd:
    """Integration test: full collect -> render -> check cycle."""

    def test_full_cycle(self, tmp_path):
        # Set up a mini repo
        _write_md(tmp_path / "core.md", tier=1, title="Core", description="Core doc", nist_controls='["AC-3", "SI-10"]')
        _write_md(tmp_path / "guide.md", tier=2, title="Guide", description="Guide doc", frameworks='["NIST 800-53"]')
        (tmp_path / "skills").mkdir()
        _make_skill(tmp_path / "skills", "my-skill", "My skill desc", scripts=["run.sh"])

        # Collect
        docs = collect_documents(tmp_path)
        skills = collect_skills(tmp_path)
        stats = compute_stats(docs, skills)

        assert stats.total_documents == 2
        assert stats.total_skills == 1
        assert stats.tier_1_core == 1
        assert stats.tier_2_supporting == 1
        assert stats.total_nist_controls_referenced == 2
        assert stats.frameworks_covered == 1

        # Render and verify valid YAML
        output = render_index_yaml(docs, skills, stats, generated_date="2026-01-01")
        parsed = yaml.safe_load(output)
        assert len(parsed["documents"]) == 2
        assert len(parsed["skills"]) == 1
        assert parsed["stats"]["total_documents"] == 2

        # Write and check
        (tmp_path / "INDEX.yaml").write_text(output)
        assert check_mode(tmp_path) is True


# ── Word count auto-update tests ──────────────────────────────────


class TestUpdateContextGuideWordCounts:
    """Test auto-updating word counts in CONTEXT-GUIDE.md."""

    def test_updates_word_count(self, tmp_path):
        # Create a doc file with known word count
        doc = tmp_path / "test.md"
        doc.write_text("one two three four five six seven eight nine ten")  # 10 words

        guide = tmp_path / "CONTEXT-GUIDE.md"
        guide.write_text("## Tier 1 — Always Load (~0 words)\n\n| `test.md` | 999 | A test doc |\n")

        update_context_guide_word_counts(tmp_path)

        content = guide.read_text()
        assert "| `test.md` | 10 |" in content
        assert "999" not in content

    def test_updates_tier_sum(self, tmp_path):
        doc1 = tmp_path / "a.md"
        doc1.write_text(" ".join(["word"] * 100))  # 100 words
        doc2 = tmp_path / "b.md"
        doc2.write_text(" ".join(["word"] * 200))  # 200 words

        guide = tmp_path / "CONTEXT-GUIDE.md"
        guide.write_text("## Tier 1 — Always Load (~0 words)\n\n| `a.md` | 0 | Doc A |\n| `b.md` | 0 | Doc B |\n")

        update_context_guide_word_counts(tmp_path)

        content = guide.read_text()
        assert "(~300 words)" in content

    def test_skips_missing_files(self, tmp_path):
        guide = tmp_path / "CONTEXT-GUIDE.md"
        guide.write_text("| `nonexistent.md` | 999 | Missing |\n")

        update_context_guide_word_counts(tmp_path)

        content = guide.read_text()
        assert "999" in content  # unchanged since file doesn't exist

    def test_no_guide_file(self, tmp_path):
        # Should not crash when CONTEXT-GUIDE.md doesn't exist
        update_context_guide_word_counts(tmp_path)
