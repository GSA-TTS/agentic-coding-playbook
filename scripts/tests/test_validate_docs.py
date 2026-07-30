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

    def test_invalid_contract_role(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 1
            contract:
              role: bogus
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("contract.role" in e for e in errors)

    def test_universal_role_requires_version(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 1
            contract:
              role: universal
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("contract.version" in e for e in errors)

    def test_contract_block_must_be_mapping(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 1
            contract: "universal"
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert any("'contract' must be a mapping" in e for e in errors)

    def test_valid_project_layer_contract(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            title: "Test"
            description: "A test"
            status: canonical
            tier: 3
            contract:
              role: project-layer
              requires_contract: ">=1.0"
            ---
        """)
        )
        errors, warnings = validate_doc_frontmatter(md)
        assert errors == []


class TestValidateContractRole:
    """Repository-level canonical-designation invariant (#151)."""

    def _write(self, path, role=None, version=None):
        lines = ["---", 'title: "x"', 'description: "d"', "status: canonical", "tier: 1"]
        if role is not None:
            lines.append("contract:")
            lines.append(f"  role: {role}")
            if version is not None:
                lines.append(f'  version: "{version}"')
        lines += ["---", "# body"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")

    def test_universal_and_thin_layers_valid(self, tmp_path):
        from playbook_validator.validate_docs import validate_contract_role

        self._write(tmp_path / "AGENTS.md", role="universal", version="1.0.0")
        self._write(tmp_path / "templates/AGENTS.md.template", role="project-layer")
        self._write(tmp_path / "examples/AGENTS.md.example", role="project-layer")
        errors, _ = validate_contract_role(tmp_path)
        assert errors == []

    def test_universal_missing_role_errors(self, tmp_path):
        from playbook_validator.validate_docs import validate_contract_role

        self._write(tmp_path / "AGENTS.md", role=None)
        errors, _ = validate_contract_role(tmp_path)
        assert any("universal contract MUST declare contract.role" in e for e in errors)

    def test_thin_layer_claiming_universal_errors(self, tmp_path):
        from playbook_validator.validate_docs import validate_contract_role

        self._write(tmp_path / "AGENTS.md", role="universal", version="1.0.0")
        self._write(tmp_path / "templates/AGENTS.md.template", role="universal", version="1.0.0")
        errors, _ = validate_contract_role(tmp_path)
        assert any("thin project layer MUST NOT declare" in e for e in errors)


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


class TestSecurityControlsCount:
    """Guard that SECURITY-CONTROLS.md frontmatter count == documented rows (#121)."""

    def _write(self, tmp_path, controls, rows, prose_n=None):
        docs = tmp_path / "docs"
        docs.mkdir(exist_ok=True)
        arr = ", ".join(f'"{c}"' for c in controls)
        body_rows = "\n".join(f"| **{c}** | Name | P1 | desc | impl | verify | xref |" for c in rows)
        prose = f"\n{prose_n} controls across 10 families.\n" if prose_n is not None else ""
        (docs / "SECURITY-CONTROLS.md").write_text(
            f"---\ntitle: SC\nstatus: canonical\ntier: 1\nnist_controls: [{arr}]\n---\n"
            f"# Security Controls\n{prose}\n"
            "| Control | Name | Priority | Description | Impl | Verify | Xref |\n"
            "|---|---|---|---|---|---|---|\n"
            f"{body_rows}\n"
        )

    def test_matching_counts_pass(self, tmp_path):
        from playbook_validator.validate_docs import validate_security_controls_count

        self._write(tmp_path, ["AC-2", "AC-3", "CM-6"], ["AC-2", "AC-3", "CM-6"], prose_n=3)
        errors, warnings = validate_security_controls_count(tmp_path)
        assert errors == []
        assert warnings == []

    def test_frontmatter_undercount_fails(self, tmp_path):
        from playbook_validator.validate_docs import validate_security_controls_count

        # 2 in frontmatter, 3 documented — the exact #121 drift.
        self._write(tmp_path, ["AC-2", "AC-3"], ["AC-2", "AC-3", "CM-6"])
        errors, _ = validate_security_controls_count(tmp_path)
        assert errors and "CM-6" in errors[0]

    def test_frontmatter_overcount_fails(self, tmp_path):
        from playbook_validator.validate_docs import validate_security_controls_count

        self._write(tmp_path, ["AC-2", "AC-3", "SI-99"], ["AC-2", "AC-3"])
        errors, _ = validate_security_controls_count(tmp_path)
        assert errors and "SI-99" in errors[0]

    def test_prose_count_mismatch_warns(self, tmp_path):
        from playbook_validator.validate_docs import validate_security_controls_count

        self._write(tmp_path, ["AC-2", "AC-3"], ["AC-2", "AC-3"], prose_n=99)
        errors, warnings = validate_security_controls_count(tmp_path)
        assert errors == []
        assert warnings and "99 controls" in warnings[0]

    def test_absent_doc_is_noop(self, tmp_path):
        from playbook_validator.validate_docs import validate_security_controls_count

        errors, warnings = validate_security_controls_count(tmp_path)
        assert errors == [] and warnings == []

    def test_real_repo_is_consistent(self):
        """The live docs/SECURITY-CONTROLS.md must pass the guard."""
        from pathlib import Path

        from playbook_validator.validate_docs import validate_security_controls_count

        root = Path(__file__).resolve().parents[2]
        errors, _ = validate_security_controls_count(root)
        assert errors == [], f"live SECURITY-CONTROLS.md drift: {errors}"
