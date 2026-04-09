"""Tests for ADR validation module."""

import textwrap

from playbook_validator.validate_adrs import (
    find_adr_files,
    validate_adr,
    validate_adr_directory,
)


def _write_adr(path, content):
    """Helper to write an ADR file with dedented content."""
    path.write_text(textwrap.dedent(content))


class TestFindAdrFiles:
    """Test ADR file discovery."""

    def test_finds_nnnn_pattern_files(self, tmp_path):
        _write_adr(tmp_path / "0001-use-encryption.md", "---\ntitle: t\n---\n")
        _write_adr(tmp_path / "0002-adopt-tls.md", "---\ntitle: t\n---\n")
        # Non-ADR files should be excluded
        _write_adr(tmp_path / "README.md", "# Readme\n")
        _write_adr(tmp_path / "index.md", "# Index\n")
        files = find_adr_files(tmp_path)
        names = [f.name for f in files]
        assert names == ["0001-use-encryption.md", "0002-adopt-tls.md"]

    def test_ignores_non_matching_files(self, tmp_path):
        _write_adr(tmp_path / "notes.md", "stuff")
        _write_adr(tmp_path / "01-too-short.md", "stuff")
        _write_adr(tmp_path / "00001-too-long.md", "stuff")
        assert find_adr_files(tmp_path) == []

    def test_returns_sorted(self, tmp_path):
        _write_adr(tmp_path / "0003-third.md", "---\ntitle: t\n---\n")
        _write_adr(tmp_path / "0001-first.md", "---\ntitle: t\n---\n")
        files = find_adr_files(tmp_path)
        assert [f.name for f in files] == ["0001-first.md", "0003-third.md"]


class TestValidateAdr:
    """Test single ADR validation."""

    def test_valid_adr(self, tmp_path):
        md = tmp_path / "0001-use-encryption.md"
        _write_adr(
            md,
            """\
            ---
            title: "Use Encryption at Rest"
            status: accepted
            date: 2026-01-15
            nist_controls: [SC-28, SC-13]
            ---
            # Use Encryption at Rest
        """,
        )
        errors, warnings = validate_adr(md)
        assert errors == []

    def test_missing_required_fields(self, tmp_path):
        md = tmp_path / "0001-incomplete.md"
        _write_adr(
            md,
            """\
            ---
            title: "Incomplete ADR"
            ---
            # Missing status, date, nist_controls
        """,
        )
        errors, warnings = validate_adr(md)
        assert any("status" in e for e in errors)
        assert any("date" in e for e in errors)
        assert any("nist_controls" in e for e in errors)

    def test_no_frontmatter(self, tmp_path):
        md = tmp_path / "0001-no-fm.md"
        _write_adr(
            md,
            """\
            # No Frontmatter
            Just content.
        """,
        )
        errors, warnings = validate_adr(md)
        assert any("frontmatter" in e.lower() for e in errors)

    def test_valid_status_values(self, tmp_path):
        for status in ("proposed", "accepted", "deprecated", "superseded"):
            md = tmp_path / f"0001-{status}.md"
            _write_adr(
                md,
                f"""\
                ---
                title: "Test"
                status: {status}
                date: 2026-01-01
                nist_controls: [AC-1]
                superseded_by: "0002-replacement.md"
                ---
            """,
            )
            errors, _ = validate_adr(md)
            # No status-related errors (superseded_by ref may fail but that's separate)
            assert not any("invalid status" in e.lower() for e in errors), f"status '{status}' should be valid"

    def test_invalid_status(self, tmp_path):
        md = tmp_path / "0001-bad-status.md"
        _write_adr(
            md,
            """\
            ---
            title: "Bad Status"
            status: rejected
            date: 2026-01-01
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert any("status" in e and "rejected" in e for e in errors)

    def test_valid_nist_controls(self, tmp_path):
        md = tmp_path / "0001-controls.md"
        _write_adr(
            md,
            """\
            ---
            title: "NIST Controls"
            status: accepted
            date: 2026-01-01
            nist_controls: [AC-3, CM-7(5), SC-28, SI-2(1)]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert not any("nist" in e.lower() for e in errors)

    def test_invalid_nist_control_format(self, tmp_path):
        md = tmp_path / "0001-bad-nist.md"
        _write_adr(
            md,
            """\
            ---
            title: "Bad NIST"
            status: accepted
            date: 2026-01-01
            nist_controls: [ac-3, INVALID, 123]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert any("nist" in e.lower() and "ac-3" in e for e in errors)
        assert any("INVALID" in e for e in errors)
        assert any("123" in e for e in errors)

    def test_valid_date_format(self, tmp_path):
        md = tmp_path / "0001-good-date.md"
        _write_adr(
            md,
            """\
            ---
            title: "Good Date"
            status: accepted
            date: 2026-03-24
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert not any("date" in e.lower() and "format" in e.lower() for e in errors)

    def test_invalid_date_format(self, tmp_path):
        md = tmp_path / "0001-bad-date.md"
        _write_adr(
            md,
            """\
            ---
            title: "Bad Date"
            status: accepted
            date: "March 24, 2026"
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert any("date" in e.lower() and "format" in e.lower() for e in errors)

    def test_filename_convention_valid(self, tmp_path):
        md = tmp_path / "0001-use-encryption-at-rest.md"
        _write_adr(
            md,
            """\
            ---
            title: "Valid Filename"
            status: accepted
            date: 2026-01-01
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert not any("filename" in e.lower() for e in errors)

    def test_filename_convention_uppercase_rejected(self, tmp_path):
        md = tmp_path / "0001-Use-Encryption.md"
        _write_adr(
            md,
            """\
            ---
            title: "Bad Filename"
            status: accepted
            date: 2026-01-01
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert any("filename" in e.lower() for e in errors)

    def test_optional_fields_produce_warnings(self, tmp_path):
        md = tmp_path / "0001-no-optionals.md"
        _write_adr(
            md,
            """\
            ---
            title: "Minimal ADR"
            status: accepted
            date: 2026-01-01
            nist_controls: [AC-1]
            ---
        """,
        )
        _, warnings = validate_adr(md)
        assert any("category" in w for w in warnings)

    def test_superseded_missing_superseded_by(self, tmp_path):
        md = tmp_path / "0001-old.md"
        _write_adr(
            md,
            """\
            ---
            title: "Old Decision"
            status: superseded
            date: 2026-01-01
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr(md)
        assert any("superseded_by" in e for e in errors)


class TestValidateAdrDirectory:
    """Test directory-level validation (cross-references, duplicates)."""

    def test_duplicate_adr_numbers(self, tmp_path):
        for name in ("0001-first.md", "0001-duplicate.md"):
            _write_adr(
                tmp_path / name,
                """\
                ---
                title: "ADR"
                status: accepted
                date: 2026-01-01
                nist_controls: [AC-1]
                ---
            """,
            )
        errors, _ = validate_adr_directory(tmp_path)
        assert any("duplicate" in e.lower() and "0001" in e for e in errors)

    def test_superseded_by_reference_integrity(self, tmp_path):
        _write_adr(
            tmp_path / "0001-old.md",
            """\
            ---
            title: "Old"
            status: superseded
            date: 2026-01-01
            nist_controls: [AC-1]
            superseded_by: "0002-new.md"
            ---
        """,
        )
        # 0002-new.md does NOT exist
        errors, _ = validate_adr_directory(tmp_path)
        assert any("superseded_by" in e and "0002-new.md" in e for e in errors)

    def test_superseded_by_valid_reference(self, tmp_path):
        _write_adr(
            tmp_path / "0001-old.md",
            """\
            ---
            title: "Old"
            status: superseded
            date: 2026-01-01
            nist_controls: [AC-1]
            superseded_by: "0002-new.md"
            ---
        """,
        )
        _write_adr(
            tmp_path / "0002-new.md",
            """\
            ---
            title: "New"
            status: accepted
            date: 2026-02-01
            nist_controls: [AC-1]
            ---
        """,
        )
        errors, _ = validate_adr_directory(tmp_path)
        assert not any("superseded_by" in e for e in errors)

    def test_empty_directory(self, tmp_path):
        errors, warnings = validate_adr_directory(tmp_path)
        assert errors == []
        assert warnings == []

    def test_aggregates_per_file_errors(self, tmp_path):
        _write_adr(
            tmp_path / "0001-bad.md",
            """\
            ---
            title: "Bad"
            status: invalid
            date: bad-date
            nist_controls: [bad]
            ---
        """,
        )
        errors, _ = validate_adr_directory(tmp_path)
        assert len(errors) >= 3  # status + date + nist
