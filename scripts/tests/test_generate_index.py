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


# ── Landscape doc generation + guards (#142) ──────────────────────────────────


class TestLandscapeSummaryGeneration:
    """Status Summary + Phase Mapping generated from the registry (#142)."""

    def _write_registry(self, root, entries):
        (root / "data").mkdir(exist_ok=True)
        import yaml as _yaml

        (root / "data" / "federal-ai-landscape.yaml").write_text(
            _yaml.safe_dump({"total_entries": len(entries), "entries": entries})
        )

    def test_summary_counts_by_category_and_status(self, tmp_path):
        from playbook_validator.index_updaters import (
            compute_landscape_summary,
            render_landscape_summary_table,
        )

        self._write_registry(
            tmp_path,
            [
                {"id": "eo-1", "category": "executive_order", "status": "active"},
                {"id": "eo-2", "category": "executive_order", "status": "revoked"},
                {"id": "n-1", "category": "nist_standard", "status": "final"},  # → Active
                {"id": "n-2", "category": "nist_standard", "status": "draft"},
            ],
        )
        counts, total = compute_landscape_summary(tmp_path)
        assert total == 4
        assert counts["executive_order"] == {"active": 1, "revoked": 1, "draft": 0}
        assert counts["nist_standard"] == {"active": 1, "revoked": 0, "draft": 1}
        table = render_landscape_summary_table(counts)
        assert "| **Total** | **2** | **1** | **1** |" in table  # final counts as active

    def test_phase_mapping_derived_from_playbook_phases(self, tmp_path):
        from playbook_validator.index_updaters import (
            compute_phase_mapping,
            render_phase_mapping_table,
        )

        self._write_registry(
            tmp_path,
            [
                {"id": "eo-14179", "category": "executive_order", "status": "active", "playbook_phases": ["0"]},
                {"id": "m-25-22", "category": "omb_memo", "status": "active", "playbook_phases": ["0.5", "7"]},
                {
                    "id": "slsa",
                    "title": "SLSA (Supply-chain Levels)",
                    "category": "industry_standard",
                    "status": "active",
                    "playbook_phases": ["1"],
                },
            ],
        )
        mapping = compute_phase_mapping(tmp_path)
        assert mapping["0"] == ["EO 14179"]
        assert mapping["0.5"] == ["M-25-22"]
        assert mapping["7"] == ["M-25-22"]
        assert mapping["1"] == ["SLSA"]  # non-coded id → title, parenthetical dropped
        table = render_phase_mapping_table(mapping)
        assert "**Phase 4: Document Decisions** | —" in table  # empty phase → em dash

    def test_short_ref_shapes(self, tmp_path):
        from playbook_validator.index_updaters import _landscape_short_ref

        assert _landscape_short_ref({"id": "eo-14179"}) == "EO 14179"
        assert _landscape_short_ref({"id": "m-25-21"}) == "M-25-21"
        assert _landscape_short_ref({"id": "nist-ai-100-1"}) == "NIST AI 100-1"
        assert _landscape_short_ref({"id": "nist-sp-800-218a"}) == "NIST SP 800-218A"
        assert (
            _landscape_short_ref({"id": "gao-ai-framework", "title": "GAO AI Accountability Framework"})
            == "GAO AI Accountability Framework"
        )


class TestRoadmapMetricsGeneration:
    def test_metrics_table_derives_all_cells(self, tmp_path, monkeypatch):
        from playbook_validator import index_updaters as iu
        from playbook_validator.generate_index import IndexStats

        (tmp_path / "data").mkdir()
        # count_landscape_entries matches "^\s+- id:" (indented list), so emit
        # the same 2-space-indented shape the real registry uses.
        entry_lines = "\n".join(f"  - id: e-{i}\n    category: omb_memo\n    status: active" for i in range(5))
        (tmp_path / "data" / "federal-ai-landscape.yaml").write_text(f"total_entries: 5\nentries:\n{entry_lines}\n")
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "SECURITY-CONTROLS.md").write_text(
            "---\ntitle: SC\nstatus: canonical\ntier: 1\n---\n"
            "| **AC-2** | n | P1 | d | i | v | x |\n| **AC-3** | n | P1 | d | i | v | x |\n"
        )
        (tmp_path / "checklists").mkdir()
        (tmp_path / "checklists" / "pre-deployment.md").write_text(
            "| 1.1 | a | [ ] Pass | |\n| 1.2 | b | [ ] Pass | |\n| 2.1 | c | [ ] Pass | |\n"
        )
        monkeypatch.setattr(iu, "_collect_test_count", lambda root: 100)
        stats = IndexStats(total_documents=7, total_skills=3)
        table = iu.render_roadmap_metrics_table(tmp_path, stats)
        assert "| Documents | 7 |" in table
        assert "| Skills | 3 |" in table
        assert "| Tests | 100 |" in table
        assert "| Checklist items | 3 |" in table
        assert "| Landscape entries | 5 |" in table
        assert "| NIST controls mapped | 2 |" in table


class TestLandscapeDocGuard:
    """validate_landscape_doc_summary fails closed on generated-block drift."""

    def _setup(self, root, summary_table, phases_table):
        (root / "data").mkdir(exist_ok=True)
        import yaml as _yaml

        entries = [
            {"id": "eo-1", "category": "executive_order", "status": "active", "playbook_phases": ["0"]},
        ]
        (root / "data" / "federal-ai-landscape.yaml").write_text(
            _yaml.safe_dump({"total_entries": 1, "entries": entries})
        )
        (root / "docs").mkdir(exist_ok=True)
        (root / "docs" / "FEDERAL-AI-LANDSCAPE.md").write_text(
            "# L\n\n"
            "<!-- GENERATED:LANDSCAPE_SUMMARY:START -->\n"
            + summary_table
            + "\n<!-- GENERATED:LANDSCAPE_SUMMARY:END -->\n\n"
            "<!-- GENERATED:LANDSCAPE_PHASES:START -->\n" + phases_table + "\n<!-- GENERATED:LANDSCAPE_PHASES:END -->\n"
        )

    def test_in_sync_passes(self, tmp_path):
        from playbook_validator.index_updaters import (
            compute_landscape_summary,
            compute_phase_mapping,
            render_landscape_summary_table,
            render_phase_mapping_table,
        )
        from playbook_validator.validate_landscape import validate_landscape_doc_summary

        # build the registry first so we can render the correct expected tables
        (tmp_path / "data").mkdir()
        import yaml as _yaml

        entries = [
            {"id": "eo-1", "category": "executive_order", "status": "active", "playbook_phases": ["0"]},
        ]
        (tmp_path / "data" / "federal-ai-landscape.yaml").write_text(
            _yaml.safe_dump({"total_entries": 1, "entries": entries})
        )
        summary = render_landscape_summary_table(compute_landscape_summary(tmp_path)[0])
        phases = render_phase_mapping_table(compute_phase_mapping(tmp_path))
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "FEDERAL-AI-LANDSCAPE.md").write_text(
            "# L\n\n<!-- GENERATED:LANDSCAPE_SUMMARY:START -->\n"
            + summary
            + "\n<!-- GENERATED:LANDSCAPE_SUMMARY:END -->\n\n"
            "<!-- GENERATED:LANDSCAPE_PHASES:START -->\n" + phases + "\n<!-- GENERATED:LANDSCAPE_PHASES:END -->\n"
        )
        assert validate_landscape_doc_summary(tmp_path) == []

    def test_drifted_summary_fails(self, tmp_path):
        from playbook_validator.validate_landscape import validate_landscape_doc_summary

        self._setup(
            tmp_path,
            summary_table=(
                "| Category | Active | Revoked/Rescinded | Draft |\n"
                "|---|---|---|---|\n"
                "| **Total** | **99** | **0** | **0** |"
            ),
            phases_table="| Phase | x |\n|---|---|",
        )
        errors = validate_landscape_doc_summary(tmp_path)
        assert errors and "out of sync" in errors[0]


# ── TRACEABILITY §1 matrix generation + guard (#197) ──────────────────────────


class TestTraceabilityMatrix:
    _HDR = (
        "| Control | Name | AGENTS.md | docs/CODING_PRACTICES.md | "
        "SECURITY-CONTROLS.md | AGENT-IDENTITY.md | Checklist |\n"
        "|---|---|---|---|---|---|---|\n"
    )

    def _setup(self, root, *, names, agents_controls, coding_controls):
        (root / "data").mkdir(exist_ok=True)
        import json as _json

        (root / "data" / "nist-800-53-control-names.json").write_text(
            _json.dumps({"_provenance": {}, "controls": names})
        )
        (root / "docs").mkdir(exist_ok=True)

        def _doc(path, controls):
            arr = ", ".join(f'"{c}"' for c in controls)
            path.write_text(f"---\ntitle: t\nstatus: canonical\ntier: 1\nnist_controls: [{arr}]\n---\n# x\n")

        _doc(root / "AGENTS.md", agents_controls)
        _doc(root / "docs" / "CODING_PRACTICES.md", coding_controls)
        _doc(root / "docs" / "SECURITY-CONTROLS.md", [])
        _doc(root / "docs" / "AGENT-IDENTITY.md", [])

    def test_rowset_is_union_sorted(self, tmp_path):
        from playbook_validator.index_updaters import compute_traceability_rows

        self._setup(
            tmp_path,
            names={
                "AC-2": "Account Management",
                "AC-12": "Session Termination",
                "SI-10": "Information Input Validation",
            },
            agents_controls=["AC-2", "SI-10"],
            coding_controls=["AC-12", "AC-2"],
        )
        ids, names = compute_traceability_rows(tmp_path)
        # union, family-alpha then numeric (AC-2 before AC-12)
        assert ids == ["AC-2", "AC-12", "SI-10"]
        assert names["SI-10"] == "Information Input Validation"

    def test_names_from_oscal_map(self, tmp_path):
        from playbook_validator.index_updaters import (
            compute_traceability_rows,
            render_traceability_matrix,
        )

        self._setup(
            tmp_path,
            names={"SI-10": "Information Input Validation"},
            agents_controls=["SI-10"],
            coding_controls=[],
        )
        ids, names = compute_traceability_rows(tmp_path)
        table = render_traceability_matrix(ids, names, {"SI-10": ["§5.1", "§2", "§3.9", "—", "3.1"]})
        assert "| SI-10 | Information Input Validation | §5.1 | §2 | §3.9 | — | 3.1 |" in table

    def test_editorial_cells_preserved(self, tmp_path):
        from playbook_validator.index_updaters import (
            render_traceability_matrix,
        )

        # a control with no editorial entry gets all em dashes
        table = render_traceability_matrix(["AC-2"], {"AC-2": "Account Management"}, {})
        assert "| AC-2 | Account Management | — | — | — | — | — |" in table

    def test_missing_oscal_map_returns_none(self, tmp_path):
        from playbook_validator.index_updaters import compute_traceability_rows

        (tmp_path / "AGENTS.md").write_text(
            '---\ntitle: t\nstatus: canonical\ntier: 1\nnist_controls: ["AC-2"]\n---\n# x\n'
        )
        assert compute_traceability_rows(tmp_path) is None

    def test_guard_flags_wrong_name(self, tmp_path):
        from playbook_validator.validate_docs import _validate_traceability_matrix

        self._setup(
            tmp_path,
            names={"AC-2": "Account Management"},
            agents_controls=["AC-2"],
            coding_controls=[],
        )
        (tmp_path / "docs" / "TRACEABILITY.md").write_text(
            "# T\n\n<!-- GENERATED:TRACEABILITY_MATRIX:START -->\n"
            + self._HDR
            + "| AC-2 | WRONG NAME | — | — | — | — | — |\n"
            "<!-- GENERATED:TRACEABILITY_MATRIX:END -->\n"
        )
        errors = _validate_traceability_matrix(tmp_path)
        assert errors and "AC-2" in errors[0] and "Account Management" in errors[0]

    def test_guard_flags_missing_control(self, tmp_path):
        from playbook_validator.validate_docs import _validate_traceability_matrix

        self._setup(
            tmp_path,
            names={"AC-2": "Account Management", "AC-3": "Access Enforcement"},
            agents_controls=["AC-2", "AC-3"],
            coding_controls=[],
        )
        (tmp_path / "docs" / "TRACEABILITY.md").write_text(
            "# T\n\n<!-- GENERATED:TRACEABILITY_MATRIX:START -->\n"
            + self._HDR
            + "| AC-2 | Account Management | — | — | — | — | — |\n"  # AC-3 missing
            "<!-- GENERATED:TRACEABILITY_MATRIX:END -->\n"
        )
        errors = _validate_traceability_matrix(tmp_path)
        assert errors and "control set is out of sync" in errors[0]


class TestOscalControlNames:
    def test_derive_map_skips_enhancements(self):
        from pathlib import Path

        from playbook_validator.index_updaters import load_oscal_control_names

        # sanity on the real committed map: base controls only, known values
        root = Path(__file__).resolve().parents[2]
        names = load_oscal_control_names(root)
        assert names is not None
        assert names["SI-10"] == "Information Input Validation"
        assert names["SR-3"] == "Supply Chain Controls and Processes"
        # no enhancement ids like AC-2.1 leaked in
        assert not any("." in cid for cid in names)


# ── Neutral document inventory generation + guard (#199) ──────────────────────


class TestDocInventory:
    def _write_index(self, root, docs):
        import yaml as _yaml

        (root / "INDEX.yaml").write_text(_yaml.safe_dump({"documents": docs}))

    def test_render_sorts_by_tier_then_path(self):
        from playbook_validator.index_updaters import render_doc_inventory_table

        docs = [
            {"path": "docs/z.md", "tier": 2, "description": "Zed"},
            {"path": "AGENTS.md", "tier": 1, "description": "Contract"},
            {"path": "docs/a.md", "tier": 1, "description": "Ay"},
        ]
        table = render_doc_inventory_table(docs)
        lines = [ln for ln in table.splitlines() if ln.startswith("| `")]
        assert lines[0].startswith("| `AGENTS.md` | 1 |")
        assert lines[1].startswith("| `docs/a.md` | 1 |")
        assert lines[2].startswith("| `docs/z.md` | 2 |")

    def test_description_whitespace_collapsed(self):
        from playbook_validator.index_updaters import render_doc_inventory_table

        table = render_doc_inventory_table([{"path": "x.md", "tier": 1, "description": "multi\n  line   desc"}])
        assert "| `x.md` | 1 | multi line desc |" in table

    def test_update_is_noop_without_markers(self, tmp_path):
        from playbook_validator.index_updaters import update_doc_inventory

        self._write_index(tmp_path, [{"path": "a.md", "tier": 1, "description": "d"}])
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "README.md").write_text("# no markers here\n")
        update_doc_inventory(tmp_path)  # must not raise / not add anything
        assert "GENERATED:DOC_INVENTORY" not in (tmp_path / "docs" / "README.md").read_text()

    def test_update_fills_marked_block(self, tmp_path):
        from playbook_validator.index_updaters import update_doc_inventory

        self._write_index(tmp_path, [{"path": "AGENTS.md", "tier": 1, "description": "Contract"}])
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "README.md").write_text(
            "# R\n\n<!-- GENERATED:DOC_INVENTORY:START -->\nold\n<!-- GENERATED:DOC_INVENTORY:END -->\n"
        )
        update_doc_inventory(tmp_path)
        out = (tmp_path / "docs" / "README.md").read_text()
        assert "| `AGENTS.md` | 1 | Contract |" in out

    def test_guard_flags_drift(self, tmp_path):
        from playbook_validator.validate_docs import _validate_doc_inventory

        self._write_index(tmp_path, [{"path": "AGENTS.md", "tier": 1, "description": "Contract"}])
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "README.md").write_text(
            "# R\n\n<!-- GENERATED:DOC_INVENTORY:START -->\n"
            "| Document | Tier | Purpose |\n|----------|------|---------|\n"
            "| `AGENTS.md` | 9 | Contract |\n"  # wrong tier
            "<!-- GENERATED:DOC_INVENTORY:END -->\n"
        )
        errors = _validate_doc_inventory(tmp_path)
        assert errors and "out of sync" in errors[0]

    def test_real_repo_inventory_consistent(self):
        from pathlib import Path

        from playbook_validator.validate_docs import _validate_doc_inventory

        root = Path(__file__).resolve().parents[2]
        assert _validate_doc_inventory(root) == []


# ── Framework references generation + guards (#198) ───────────────────────────


class TestFrameworkRefs:
    def _write_frameworks(self, root, entries):
        import yaml as _yaml

        (root / "data").mkdir(exist_ok=True)
        (root / "data" / "frameworks.yaml").write_text(_yaml.safe_dump({"version": "1.0", "frameworks": entries}))

    def test_render_featured_in_order_with_dates(self):
        from playbook_validator.index_updaters import render_framework_refs

        body = render_framework_refs(
            [
                {"id": "a", "name": "Framework A", "date": "2025", "featured": True},
                {"id": "b", "name": "Framework B", "featured": True},  # no date
                {"id": "c", "name": "Framework C"},  # not featured → excluded
            ]
        )
        assert body == "- Framework A (2025)\n- Framework B"

    def test_name_index_includes_aliases(self):
        from playbook_validator.index_updaters import framework_name_index

        idx = framework_name_index([{"id": "x", "name": "Canonical Name", "aliases": ["Short", "Alt"]}])
        assert idx["Canonical Name"] == "Canonical Name"
        assert idx["Short"] == "Canonical Name"
        assert idx["Alt"] == "Canonical Name"

    def test_update_fills_marked_block(self, tmp_path):
        from playbook_validator.index_updaters import update_framework_refs

        self._write_frameworks(tmp_path, [{"id": "a", "name": "NIST X", "date": "2024", "featured": True}])
        (tmp_path / "AGENTS.md").write_text(
            "# A\n\n<!-- GENERATED:FRAMEWORK_REFS:START -->\nold\n<!-- GENERATED:FRAMEWORK_REFS:END -->\n"
        )
        update_framework_refs(tmp_path)
        assert "- NIST X (2024)" in (tmp_path / "AGENTS.md").read_text()

    def test_refs_guard_flags_drift(self, tmp_path):
        from playbook_validator.validate_docs import _validate_framework_refs

        self._write_frameworks(tmp_path, [{"id": "a", "name": "NIST X", "date": "2024", "featured": True}])
        (tmp_path / "AGENTS.md").write_text(
            "# A\n\n<!-- GENERATED:FRAMEWORK_REFS:START -->\n- Stale Y\n<!-- GENERATED:FRAMEWORK_REFS:END -->\n"
        )
        errors = _validate_framework_refs(tmp_path)
        assert errors and "out of sync" in errors[0]

    def test_frontmatter_guard_flags_unknown(self, tmp_path):
        from playbook_validator.validate_docs import _validate_framework_frontmatter

        self._write_frameworks(tmp_path, [{"id": "a", "name": "NIST X", "aliases": ["NX"]}])
        d = tmp_path / "docs"
        d.mkdir()
        (d / "thing.md").write_text(
            "---\ntitle: t\ndescription: d\nstatus: canonical\ntier: 2\n"
            'frameworks: ["NX", "Bogus Framework"]\n---\n# x\n'
        )
        errors = _validate_framework_frontmatter(tmp_path)
        assert errors and "Bogus Framework" in errors[0]
        # the alias "NX" is accepted (not flagged)
        assert not any("NX" in e for e in errors)

    def test_real_repo_frameworks_consistent(self):
        from pathlib import Path

        from playbook_validator.validate_docs import (
            _validate_framework_frontmatter,
            _validate_framework_refs,
        )

        root = Path(__file__).resolve().parents[2]
        assert _validate_framework_refs(root) == []
        assert _validate_framework_frontmatter(root) == []
