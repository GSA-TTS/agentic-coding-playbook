"""Tests for risk assessment validation module."""

import textwrap

from playbook_validator.validate_risk_assessment import validate_risk_assessment


def _write_file(path, content):
    """Helper to write a file with dedented content."""
    path.write_text(textwrap.dedent(content))


# --- Minimal valid assessment for reuse across tests ---

VALID_ASSESSMENT = """\
# AI Agent Risk Assessment Worksheet

## Section 1: System Identification

| Field | Value |
|-------|-------|
| **System Name** | ACME Portal |
| **System Owner** | Jane Doe |

## Section 2: AI Agent Identification

### Agent Capabilities

- [x] Code generation and modification
- [x] File system read access

## Section 3: Data Classification

| Data Type | Present? | Classification | Agent Needs Access? |
|-----------|----------|---------------|-------------------|
| Source code | [x] Yes | Internal | [x] Yes |

## Section 4: Threat Analysis

| # | Threat | OWASP Ref | Likelihood (1-5) | Impact (1-5) | Risk Score |
|---|--------|-----------|-------------------|--------------|------------|
| T1 | Prompt injection | LLM01 | 3 | 4 | 12 |
| T2 | Data disclosure | LLM02 | 2 | 5 | 10 |

## Section 5: Control Assessment

| Control Area | Status | Notes |
|-------------|--------|-------|
| **Agent Identity** | [x] Implemented | Uses SA account AC-2 |
| **Least Privilege** | [x] Implemented | Scoped to repo CM-7 |

NIST controls: RA-3, RA-5, AC-2, CM-7

## Section 6: Risk Treatment Plan

| Field | Value |
|-------|-------|
| **Risk Score** | 12 |
| **Treatment** | [x] Mitigate |
| **Planned Controls** | Input validation SI-10 |

## Section 7: Acceptance and Sign-Off

### Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **System Owner** | Jane Doe | J. Doe | 2026-03-01 |
| **ISSO** | John Smith | J. Smith | 2026-03-01 |
"""


class TestValidAssessment:
    """A fully valid risk assessment should pass with no errors."""

    def test_valid_assessment_passes(self, tmp_path):
        md = tmp_path / "risk-assessment.md"
        _write_file(md, VALID_ASSESSMENT)
        errors, warnings = validate_risk_assessment(md)
        assert errors == [], f"Expected no errors, got: {errors}"


class TestMissingSections:
    """Each of the 7 required sections must be present."""

    def test_missing_system_identification(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 1: System Identification",
            "## Removed Section 1",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("System Identification" in e for e in errors)

    def test_missing_agent_capabilities(self, tmp_path):
        # Remove Section 2 which contains Agent Capabilities
        content = VALID_ASSESSMENT.replace(
            "## Section 2: AI Agent Identification",
            "## Removed Section 2",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Agent" in e for e in errors)

    def test_missing_data_classification(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 3: Data Classification",
            "## Removed Section 3",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Data Classification" in e for e in errors)

    def test_missing_threat_analysis(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 4: Threat Analysis",
            "## Removed Section 4",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Threat Analysis" in e for e in errors)

    def test_missing_control_assessment(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 5: Control Assessment",
            "## Removed Section 5",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Control Assessment" in e for e in errors)

    def test_missing_risk_treatment(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 6: Risk Treatment Plan",
            "## Removed Section 6",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Risk Treatment" in e for e in errors)

    def test_missing_sign_off(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "## Section 7: Acceptance and Sign-Off",
            "## Removed Section 7",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("Sign-Off" in e or "Sign-off" in e for e in errors)


class TestEdgeCases:
    """Empty file, file not found, and partial content."""

    def test_empty_file(self, tmp_path):
        md = tmp_path / "empty.md"
        _write_file(md, "")
        errors, _ = validate_risk_assessment(md)
        assert len(errors) > 0
        assert any("empty" in e.lower() or "section" in e.lower() for e in errors)

    def test_file_not_found(self, tmp_path):
        md = tmp_path / "nonexistent.md"
        errors, _ = validate_risk_assessment(md)
        assert len(errors) == 1
        assert any("not found" in e.lower() or "does not exist" in e.lower() for e in errors)

    def test_partial_assessment_some_sections_empty(self, tmp_path):
        """Sections present as headings but with no content should warn."""
        content = """\
# AI Agent Risk Assessment Worksheet

## Section 1: System Identification

## Section 2: AI Agent Identification

### Agent Capabilities

## Section 3: Data Classification

## Section 4: Threat Analysis

## Section 5: Control Assessment

## Section 6: Risk Treatment Plan

## Section 7: Acceptance and Sign-Off

### Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **System Owner** | | | |
| **ISSO** | | | |
"""
        md = tmp_path / "partial.md"
        _write_file(md, content)
        errors, warnings = validate_risk_assessment(md)
        # Should have warnings about unfilled template content
        assert len(warnings) > 0


class TestRiskScores:
    """Likelihood and Impact values must be integers 1-5."""

    def test_risk_score_out_of_range_high(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "| T1 | Prompt injection | LLM01 | 3 | 4 | 12 |", "| T1 | Prompt injection | LLM01 | 6 | 4 | 24 |"
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("likelihood" in e.lower() or "1-5" in e or "range" in e.lower() for e in errors)

    def test_risk_score_out_of_range_zero(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "| T2 | Data disclosure | LLM02 | 2 | 5 | 10 |", "| T2 | Data disclosure | LLM02 | 0 | 5 | 0 |"
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("likelihood" in e.lower() or "1-5" in e or "range" in e.lower() for e in errors)

    def test_risk_score_non_numeric(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "| T1 | Prompt injection | LLM01 | 3 | 4 | 12 |", "| T1 | Prompt injection | LLM01 | HIGH | 4 | 12 |"
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, _ = validate_risk_assessment(md)
        assert any("numeric" in e.lower() or "1-5" in e or "likelihood" in e.lower() for e in errors)


class TestNistControls:
    """Control Assessment section must reference NIST controls in XX-N format."""

    def test_missing_nist_references(self, tmp_path):
        # Remove all NIST control references from section 5
        content = (
            VALID_ASSESSMENT.replace(
                "NIST controls: RA-3, RA-5, AC-2, CM-7",
                "No controls documented",
            )
            .replace("AC-2", "uses service account")
            .replace("CM-7", "scoped")
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        errors, warnings = validate_risk_assessment(md)
        assert any("nist" in e.lower() or "control" in e.lower() for e in errors + warnings)


class TestSignOff:
    """Sign-off section must have actual names, not placeholders."""

    def test_unsigned_placeholder_names(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "| **System Owner** | Jane Doe | J. Doe | 2026-03-01 |",
            "| **System Owner** | | | |",
        ).replace(
            "| **ISSO** | John Smith | J. Smith | 2026-03-01 |",
            "| **ISSO** | | | |",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        _, warnings = validate_risk_assessment(md)
        assert any("sign" in w.lower() or "unsigned" in w.lower() or "name" in w.lower() for w in warnings)

    def test_placeholder_bracket_names(self, tmp_path):
        content = VALID_ASSESSMENT.replace(
            "| **System Owner** | Jane Doe | J. Doe | 2026-03-01 |",
            "| **System Owner** | [Name] | [Signature] | [Date] |",
        )
        md = tmp_path / "risk.md"
        _write_file(md, content)
        _, warnings = validate_risk_assessment(md)
        assert any("placeholder" in w.lower() or "sign" in w.lower() for w in warnings)
