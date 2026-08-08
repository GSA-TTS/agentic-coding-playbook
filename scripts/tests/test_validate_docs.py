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

    def _write(self, path, role=None, version=None, banner=None):
        lines = ["---", 'title: "x"', 'description: "d"', "status: canonical", "tier: 1"]
        if role is not None:
            lines.append("contract:")
            lines.append(f"  role: {role}")
            if version is not None:
                lines.append(f'  version: "{version}"')
        lines += ["---", "# body"]
        if banner is not None:
            lines.append(f"> **Version:** {banner} | **Impact Level:** FIPS Moderate")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")

    def test_universal_and_thin_layers_valid(self, tmp_path):
        from playbook_validator.validate_docs import validate_contract_role

        self._write(tmp_path / "AGENTS.md", role="universal", version="1.0.0", banner="1.0.0")
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

        self._write(tmp_path / "AGENTS.md", role="universal", version="1.0.0", banner="1.0.0")
        self._write(tmp_path / "templates/AGENTS.md.template", role="universal", version="1.0.0")
        errors, _ = validate_contract_role(tmp_path)
        assert any("thin project layer MUST NOT declare" in e for e in errors)

    def test_frontmatter_version_mismatch_config_errors(self, tmp_path):
        """#191: contract.version must equal config.CURRENT_CONTRACT_VERSION."""
        from playbook_validator.validate_docs import validate_contract_role

        self._write(tmp_path / "AGENTS.md", role="universal", version="0.4.0", banner="0.4.0")
        errors, _ = validate_contract_role(tmp_path)
        assert any("CURRENT_CONTRACT_VERSION" in e and "#191" in e for e in errors)

    def test_banner_version_mismatch_frontmatter_errors(self, tmp_path):
        """#191: the body banner Version must equal contract.version."""
        from playbook_validator.config import CURRENT_CONTRACT_VERSION
        from playbook_validator.validate_docs import validate_contract_role

        self._write(
            tmp_path / "AGENTS.md",
            role="universal",
            version=CURRENT_CONTRACT_VERSION,
            banner="0.3.0",
        )
        errors, _ = validate_contract_role(tmp_path)
        assert any("body banner Version" in e and "#191" in e for e in errors)

    def test_version_consistent_passes(self, tmp_path):
        """All three version copies agree → no error."""
        from playbook_validator.config import CURRENT_CONTRACT_VERSION
        from playbook_validator.validate_docs import validate_contract_role

        self._write(
            tmp_path / "AGENTS.md",
            role="universal",
            version=CURRENT_CONTRACT_VERSION,
            banner=CURRENT_CONTRACT_VERSION,
        )
        errors, _ = validate_contract_role(tmp_path)
        assert errors == []

    def test_real_repo_contract_version_consistent(self):
        """The live AGENTS.md must have frontmatter == banner == config version."""
        from pathlib import Path

        from playbook_validator.validate_docs import validate_contract_role

        root = Path(__file__).resolve().parents[2]
        errors, _ = validate_contract_role(root)
        assert errors == [], f"live contract-version drift: {errors}"


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

    def test_excludes_community_health_files(self, tmp_path):
        # GitHub-recognized community-health files are kept in their standard
        # form (GitHub renders them specially) and MUST NOT require content-doc
        # frontmatter.
        (tmp_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct")
        (tmp_path / "SUPPORT.md").write_text("# Support")
        (tmp_path / "GOVERNANCE.md").write_text("# Governance")
        files = find_content_files(tmp_path)
        filenames = [f.name for f in files]
        assert "CODE_OF_CONDUCT.md" not in filenames
        assert "SUPPORT.md" not in filenames
        assert "GOVERNANCE.md" not in filenames

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


class TestCountDriftGuard:
    """Guard that prose landscape/control counts match their source lists (#184)."""

    def _setup(self, tmp_path, *, entries, controls, prose_files):
        """Write a landscape YAML (entries), SECURITY-CONTROLS.md (controls),
        and the given {relpath: text} prose files. Returns tmp_path (root)."""
        data = tmp_path / "data"
        data.mkdir(exist_ok=True)
        entry_block = "\n".join(
            f"  - id: e-{i}\n    title: T{i}\n    category: omb_memo\n"
            f"    source: OMB\n    date: 2025-01-0{i % 9 + 1}\n    status: active\n"
            f"    relevance: r\n    url: https://x/{i}"
            for i in range(entries)
        )
        (data / "federal-ai-landscape.yaml").write_text(
            f"version: '1'\ntotal_entries: {entries}\nentries:\n{entry_block}\n"
        )
        docs = tmp_path / "docs"
        docs.mkdir(exist_ok=True)
        rows = "\n".join(f"| **{c}** | Name | P1 | d | i | v | x |" for c in controls)
        (docs / "SECURITY-CONTROLS.md").write_text(
            f"---\ntitle: SC\nstatus: canonical\ntier: 1\n"
            f"nist_controls: [{', '.join(repr(c) for c in controls)}]\n---\n"
            f"# Controls\n\n{rows}\n"
        )
        for rel, text in prose_files.items():
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return tmp_path

    def test_matching_counts_pass(self, tmp_path):
        from playbook_validator.validate_docs import validate_count_drift

        self._setup(
            tmp_path,
            entries=2,
            controls=["AC-2", "AC-3"],
            prose_files={
                "README.md": "Full catalog of 2 federal AI guidance documents.\n"
                "The landscape catalog has 2 entries.\n"
                "We map 2 NIST 800-53 controls here.\n",
            },
        )
        errors, _ = validate_count_drift(tmp_path)
        assert errors == []

    def test_stale_landscape_entries_fails(self, tmp_path):
        from playbook_validator.validate_docs import validate_count_drift

        # source has 2 entries; prose says 39 (the real drift this fixes)
        self._setup(
            tmp_path,
            entries=2,
            controls=["AC-2"],
            prose_files={
                "docs/README.md": "Federal AI guidance catalog (39 entries)\n",
            },
        )
        errors, _ = validate_count_drift(tmp_path)
        assert errors and "39 entries" in errors[0] and "2" in errors[0]

    def test_stale_control_count_fails(self, tmp_path):
        from playbook_validator.validate_docs import validate_count_drift

        self._setup(
            tmp_path,
            entries=1,
            controls=["AC-2", "AC-3"],
            prose_files={
                "README.md": "36 NIST 800-53 controls mapped\n",
            },
        )
        errors, _ = validate_count_drift(tmp_path)
        assert errors and "36" in errors[0] and "2 controls" in errors[0]

    def test_framework_name_not_flagged(self, tmp_path):
        """A bare 'NIST 800-53 controls' phrase (no tally) must NOT be flagged."""
        from playbook_validator.validate_docs import validate_count_drift

        self._setup(
            tmp_path,
            entries=1,
            controls=["AC-2", "AC-3"],
            prose_files={
                "README.md": "Maps risks to NIST 800-53 controls.\n"
                "cloud.gov inherits ~80% of NIST 800-53 controls.\n"
                "NIST SP 800-53 Rev 5.2 controls (the compliance framework).\n",
            },
        )
        errors, _ = validate_count_drift(tmp_path)
        assert errors == []

    def test_entries_outside_landscape_context_not_flagged(self, tmp_path):
        """'N entries' without a landscape context word is ignored."""
        from playbook_validator.validate_docs import validate_count_drift

        self._setup(
            tmp_path,
            entries=2,
            controls=["AC-2"],
            prose_files={
                "README.md": "The changelog has 99 entries.\n",
            },
        )
        errors, _ = validate_count_drift(tmp_path)
        assert errors == []

    def test_real_repo_is_consistent(self):
        """The live repo prose counts must pass after `make generate`."""
        from pathlib import Path

        from playbook_validator.validate_docs import validate_count_drift

        root = Path(__file__).resolve().parents[2]
        errors, _ = validate_count_drift(root)
        assert errors == [], f"live count drift: {errors}"


class TestUpdateHardcodedCounts:
    """Guard the generator rewrites the right count spans and nothing else (#184)."""

    def _setup(self, tmp_path, *, entries, controls):
        data = tmp_path / "data"
        data.mkdir(exist_ok=True)
        entry_block = "\n".join(f"  - id: e-{i}\n    title: T{i}" for i in range(entries))
        (data / "federal-ai-landscape.yaml").write_text(
            f"version: '1'\ntotal_entries: {entries}\nentries:\n{entry_block}\n"
        )
        docs = tmp_path / "docs"
        docs.mkdir(exist_ok=True)
        rows = "\n".join(f"| **{c}** | N | P1 | d | i | v | x |" for c in controls)
        (docs / "SECURITY-CONTROLS.md").write_text(f"---\ntitle: SC\nstatus: canonical\ntier: 1\n---\n# C\n\n{rows}\n")

    def test_rewrites_stale_counts(self, tmp_path, monkeypatch):
        from playbook_validator import index_updaters

        self._setup(tmp_path, entries=42, controls=["AC-2", "AC-3", "CM-6"])
        readme = tmp_path / "README.md"
        readme.write_text(
            "Catalog of 39 federal AI guidance documents.\n"
            "The landscape has 39 entries.\n"
            "We document 36 NIST 800-53 controls.\n"
            "Framework: NIST 800-53 controls apply.\n"  # must NOT change
        )
        # No test-count subprocess in the unit test.
        monkeypatch.setattr(index_updaters, "_collect_test_count", lambda root: None)
        index_updaters.update_hardcoded_counts(tmp_path, None, [])
        out = readme.read_text()
        assert "42 federal AI guidance" in out
        assert "42 entries" in out
        assert "3 NIST 800-53 controls" in out
        # the bare framework phrase is untouched
        assert "Framework: NIST 800-53 controls apply." in out
        # the standard's own number is never mangled
        assert "800-53" in out and "800-3" not in out
