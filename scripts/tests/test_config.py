"""Tests for config module — schema constants and validation helpers."""

from playbook_validator.config import (
    ADR_STATUS_VALUES,
    DOC_LOAD_PRIORITY_VALUES,
    DOC_STATUS_VALUES,
    DOC_TIER_VALUES,
    FILE_MAX_LINES,
    FUNCTION_MAX_LINES,
    REQUIRED_FRONTMATTER_FIELDS,
    is_valid_nist_control,
    is_valid_skill_name,
    is_valid_status,
    is_valid_tier,
)


class TestConstants:
    """Verify schema constants are correct."""

    def test_doc_status_values(self):
        assert "canonical" in DOC_STATUS_VALUES
        assert "draft" in DOC_STATUS_VALUES
        assert "deprecated" in DOC_STATUS_VALUES
        assert len(DOC_STATUS_VALUES) == 3

    def test_doc_tier_values(self):
        assert {1, 2, 3} == DOC_TIER_VALUES

    def test_load_priority_values(self):
        assert "always" in DOC_LOAD_PRIORITY_VALUES
        assert "on-demand" in DOC_LOAD_PRIORITY_VALUES
        assert "reference-only" in DOC_LOAD_PRIORITY_VALUES

    def test_required_frontmatter_fields(self):
        assert "title" in REQUIRED_FRONTMATTER_FIELDS
        assert "description" in REQUIRED_FRONTMATTER_FIELDS
        assert "status" in REQUIRED_FRONTMATTER_FIELDS
        assert "tier" in REQUIRED_FRONTMATTER_FIELDS

    def test_adr_status_values(self):
        assert "proposed" in ADR_STATUS_VALUES
        assert "accepted" in ADR_STATUS_VALUES

    def test_size_limits(self):
        assert FUNCTION_MAX_LINES == 50
        assert FILE_MAX_LINES == 400


class TestValidators:
    """Test validation helper functions."""

    def test_valid_statuses(self):
        assert is_valid_status("canonical") is True
        assert is_valid_status("draft") is True
        assert is_valid_status("invalid") is False
        assert is_valid_status("") is False

    def test_valid_tiers(self):
        assert is_valid_tier(1) is True
        assert is_valid_tier(2) is True
        assert is_valid_tier(3) is True
        assert is_valid_tier(0) is False
        assert is_valid_tier(4) is False

    def test_valid_nist_controls(self):
        assert is_valid_nist_control("AC-3") is True
        assert is_valid_nist_control("SI-10") is True
        assert is_valid_nist_control("AC-3(1)") is True
        assert is_valid_nist_control("CM-7(5)") is True
        assert is_valid_nist_control("invalid") is False
        assert is_valid_nist_control("ac-3") is False  # lowercase
        assert is_valid_nist_control("") is False

    def test_valid_skill_names(self):
        assert is_valid_skill_name("federal-repo-setup") is True
        assert is_valid_skill_name("agent-permissions") is True
        assert is_valid_skill_name("a") is True
        assert is_valid_skill_name("") is False
        assert is_valid_skill_name("Has Spaces") is False
        assert is_valid_skill_name("UPPERCASE") is False
        assert is_valid_skill_name("-leading-hyphen") is False
        assert is_valid_skill_name("trailing-hyphen-") is False
        assert is_valid_skill_name("a" * 65) is False  # too long


class TestVersionSatisfies:
    """Dependency-free contract version-range comparator (#153)."""

    def _vs(self):
        from playbook_validator.config import version_satisfies

        return version_satisfies

    def test_gte_range(self):
        vs = self._vs()
        assert vs("1.0.0", ">=1.0") is True
        assert vs("0.4.0", ">=1.0") is False  # the #191 case
        assert vs("1.0.0", ">=1.0.0") is True

    def test_gt_lt_lte(self):
        vs = self._vs()
        assert vs("1.2.0", ">1.0") is True
        assert vs("1.0.0", ">1.0") is False
        assert vs("1.0.0", "<=1.0") is True
        assert vs("0.9.0", "<1.0") is True
        assert vs("1.0.0", "<1.0") is False

    def test_exact(self):
        vs = self._vs()
        assert vs("1.0.0", "==1.0.0") is True
        assert vs("1.0.1", "==1.0.0") is False
        assert vs("1.0.0", "=1.0") is True
        assert vs("1.0.0", "1.0") is True  # bare == exact
        assert vs("1.0.1", "1.0.0") is False

    def test_caret(self):
        vs = self._vs()
        assert vs("1.5.0", "^1.0") is True
        assert vs("2.0.0", "^1.0") is False
        assert vs("1.0.0", "^1.2") is False  # below the floor
        # major 0 pins the minor
        assert vs("0.4.9", "^0.4") is True
        assert vs("0.5.0", "^0.4") is False

    def test_missing_patch_defaults_zero(self):
        vs = self._vs()
        assert vs("1.0", "1.0.0") is True
        assert vs("1.0.0", "1.0") is True

    def test_fail_closed_on_bad_input(self):
        vs = self._vs()
        assert vs(None, ">=1.0") is False
        assert vs("1.0.0", None) is False
        assert vs("1.0.0", "garbage") is False
        assert vs("not-a-version", ">=1.0") is False
        assert vs("", "") is False

    def test_whitespace_tolerant(self):
        vs = self._vs()
        assert vs("1.0.0", ">= 1.0") is True
        assert vs(" 1.0.0 ", ">=1.0") is True
