"""Tests for compare_landscape_versions.py — Version change detection.

GitHub Issue: #83 - Add test coverage for landscape RSS scripts
"""

import json
import sys
from io import StringIO

import pytest
import yaml


class TestExtractVersion:
    """Tests for extract_version function."""

    def test_v1_0_format(self):
        """Test extraction of v1.0 format versions."""
        from scripts.compare_landscape_versions import extract_version

        assert extract_version("NIST SP 800-218 v1.0") == "1.0"
        assert extract_version("AI RMF v1.1.0") == "1.1.0"

    def test_version_2_0_format(self):
        """Test extraction of 'version X.Y' format."""
        from scripts.compare_landscape_versions import extract_version

        assert extract_version("Framework Version 2.0 Released") == "2.0"
        assert extract_version("version 3.5.1 final") == "3.5.1"

    def test_rev_format(self):
        """Test extraction of 'rev X' format."""
        from scripts.compare_landscape_versions import extract_version

        assert extract_version("SP 800-53 Rev. 5") == "5"
        assert extract_version("Document rev 3") == "3"

    def test_no_version_returns_none(self):
        """Test that no version pattern returns None."""
        from scripts.compare_landscape_versions import extract_version

        assert extract_version("No version here") is None
        assert extract_version("") is None


class TestExtractStatus:
    """Tests for extract_status function."""

    def test_draft_keyword(self):
        """Test extraction of draft status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("Initial Public Draft Released") == "draft"
        assert extract_status("This is a DRAFT document") == "draft"

    def test_final_keyword(self):
        """Test extraction of final status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("Final Publication Released") == "final"
        assert extract_status("FINAL version available") == "final"

    def test_ipd_maps_to_draft(self):
        """Test that IPD maps to draft status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("IPD released for comment") == "draft"

    def test_revoked_keyword(self):
        """Test extraction of revoked status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("Document has been revoked") == "revoked"
        assert extract_status("REVOKED effective immediately") == "revoked"

    def test_rescinded_keyword(self):
        """Test extraction of rescinded status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("This EO has been rescinded") == "rescinded"

    def test_preliminary_keyword(self):
        """Test extraction of preliminary status (maps to draft)."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("Preliminary version for review") == "draft"

    def test_superseded_keyword(self):
        """Test extraction of superseded status."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("This document is superseded by SP 800-218A") == "superseded"

    def test_no_status_returns_none(self):
        """Test that no status keyword returns None."""
        from scripts.compare_landscape_versions import extract_status

        assert extract_status("No status here") is None
        assert extract_status("") is None


class TestNormalizeTitle:
    """Tests for normalize_title function."""

    def test_removes_version_numbers(self):
        """Test removal of version numbers."""
        from scripts.compare_landscape_versions import normalize_title

        result = normalize_title("NIST SP 800-218 v1.0")
        assert "1.0" not in result
        assert "v" not in result.split()
        # Verify title content is preserved
        assert "nist" in result
        assert "sp" in result
        assert "800" in result
        assert "218" in result

    def test_removes_punctuation(self):
        """Test removal of punctuation."""
        from scripts.compare_landscape_versions import normalize_title

        result = normalize_title("AI (Artificial Intelligence) Framework!")
        assert "(" not in result
        assert ")" not in result
        assert "!" not in result
        # Verify content is preserved
        assert "ai" in result
        assert "artificial" in result
        assert "intelligence" in result
        assert "framework" in result

    def test_lowercases(self):
        """Test that result is lowercased."""
        from scripts.compare_landscape_versions import normalize_title

        result = normalize_title("NIST Artificial Intelligence")
        assert result == result.lower()
        assert "nist" in result


class TestSimilarityScore:
    """Tests for similarity_score function."""

    def test_identical_strings(self):
        """Test identical strings have score 1.0."""
        from scripts.compare_landscape_versions import similarity_score

        assert similarity_score("hello world", "hello world") == 1.0

    def test_no_overlap(self):
        """Test strings with no overlap have score 0.0."""
        from scripts.compare_landscape_versions import similarity_score

        assert similarity_score("hello world", "foo bar") == 0.0

    def test_partial_overlap(self):
        """Test strings with partial overlap."""
        from scripts.compare_landscape_versions import similarity_score

        # "hello" is common, "world" and "there" are different
        # intersection = {hello}, union = {hello, world, there}
        result = similarity_score("hello world", "hello there")
        assert 0.0 < result < 1.0
        assert result == pytest.approx(1 / 3, rel=0.01)

    def test_empty_strings(self):
        """Test empty strings return 0.0."""
        from scripts.compare_landscape_versions import similarity_score

        assert similarity_score("", "") == 0.0
        assert similarity_score("hello", "") == 0.0


class TestFindEntryInLandscape:
    """Tests for find_entry_in_landscape function."""

    def test_exact_match(self):
        """Test finding an entry with exact title match."""
        from scripts.compare_landscape_versions import find_entry_in_landscape

        landscape = {"entries": [{"id": "1", "title": "NIST AI Risk Management Framework"}]}
        rss_entry = {"title": "NIST AI Risk Management Framework"}

        result = find_entry_in_landscape(rss_entry, landscape)
        assert result is not None
        assert result["id"] == "1"

    def test_similar_match_above_threshold(self):
        """Test finding an entry with similar title above threshold."""
        from scripts.compare_landscape_versions import find_entry_in_landscape

        landscape = {"entries": [{"id": "1", "title": "NIST Artificial Intelligence Risk Management Framework v1.0"}]}
        rss_entry = {"title": "NIST Artificial Intelligence Risk Management Framework v2.0"}

        result = find_entry_in_landscape(rss_entry, landscape)
        assert result is not None

    def test_no_match_below_threshold(self):
        """Test no match when similarity is below threshold."""
        from scripts.compare_landscape_versions import find_entry_in_landscape

        landscape = {"entries": [{"id": "1", "title": "Completely Different Document"}]}
        rss_entry = {"title": "NIST AI Framework"}

        result = find_entry_in_landscape(rss_entry, landscape)
        assert result is None


class TestCompareVersions:
    """Tests for compare_versions function."""

    def test_detects_version_change(self):
        """Test detection of version changes."""
        from scripts.compare_landscape_versions import compare_versions

        landscape = {
            "entries": [
                {
                    "id": "nist-ai-rmf",
                    "title": "NIST AI Risk Management Framework",
                    "version": "1.0",
                    "status": "final",
                }
            ]
        }
        rss_data = {
            "check_date": "2026-01-15T00:00:00Z",
            "new_entries": [
                {
                    "title": "NIST AI Risk Management Framework v2.0",
                    "summary": "Version 2.0 now available",
                    "url": "https://example.com",
                    "feed": "nist_csrc",
                }
            ],
        }

        result = compare_versions(landscape, rss_data)
        assert result["changes_detected"] == 1
        assert result["changes"][0]["type"] == "update"
        assert result["changes"][0]["change"]["new_version"] == "2.0"

    def test_detects_status_change(self):
        """Test detection of status changes (returns as new_publication when no existing match)."""
        from scripts.compare_landscape_versions import compare_versions

        # Note: The function only detects status changes when it finds a matching
        # entry in the landscape. If titles differ too much, it's a new_publication.
        landscape = {
            "entries": [
                {
                    "id": "doc-1",
                    "title": "Test Document",
                    "version": "1.0",
                    "status": "draft",
                }
            ]
        }
        rss_data = {
            "check_date": "2026-01-15T00:00:00Z",
            "new_entries": [
                {
                    "title": "Test Document",
                    "summary": "Final version now published",
                    "url": "https://example.com",
                    "published": "2026-01-15",
                    "feed": "test_feed",
                }
            ],
        }

        result = compare_versions(landscape, rss_data)
        assert result["changes_detected"] == 1
        assert result["changes"][0]["type"] == "update"
        assert result["changes"][0]["change"]["new_status"] == "final"

    def test_detects_new_publication(self):
        """Test detection of new publications not in registry."""
        from scripts.compare_landscape_versions import compare_versions

        landscape = {"entries": []}
        rss_data = {
            "check_date": "2026-01-15T00:00:00Z",
            "new_entries": [
                {
                    "title": "Brand New Document v1.0",
                    "summary": "A completely new publication",
                    "url": "https://example.com/new",
                    "published": "2026-01-15",
                    "feed": "test_feed",
                }
            ],
        }

        result = compare_versions(landscape, rss_data)
        assert result["changes_detected"] == 1
        assert result["changes"][0]["type"] == "new_publication"
        assert result["changes"][0]["suggested_version"] == "1.0"

    def test_no_changes(self):
        """Test when there are no changes to detect."""
        from scripts.compare_landscape_versions import compare_versions

        landscape = {"entries": []}
        rss_data = {"check_date": "2026-01-15T00:00:00Z", "new_entries": []}

        result = compare_versions(landscape, rss_data)
        assert result["changes_detected"] == 0
        assert result["changes"] == []


class TestLoadLandscape:
    """Tests for load_landscape function."""

    def test_load_valid_landscape(self, tmp_path):
        """Test loading a valid landscape YAML file."""
        from scripts.compare_landscape_versions import load_landscape

        landscape_file = tmp_path / "landscape.yaml"
        landscape_file.write_text(yaml.dump({"entries": [{"id": "1", "title": "Test"}]}))

        result = load_landscape(landscape_file)
        assert result["entries"][0]["id"] == "1"


class TestLoadRssData:
    """Tests for load_rss_data function."""

    def test_load_from_file(self, tmp_path):
        """Test loading RSS data from a file."""
        from scripts.compare_landscape_versions import load_rss_data

        rss_file = tmp_path / "rss.json"
        rss_file.write_text(json.dumps({"new_entries": [], "check_date": "2026-01-15"}))

        result = load_rss_data(rss_file)
        assert "new_entries" in result

    def test_load_from_stdin(self, monkeypatch):
        """Test loading RSS data from stdin."""
        from scripts.compare_landscape_versions import load_rss_data

        stdin_data = json.dumps({"new_entries": [{"title": "Test"}], "check_date": "2026-01-15"})
        monkeypatch.setattr(sys, "stdin", StringIO(stdin_data))

        result = load_rss_data(None)
        assert len(result["new_entries"]) == 1


class TestMain:
    """Tests for main CLI function."""

    def test_exit_code_0_when_changes(self, tmp_path, monkeypatch):
        """Test exit code 0 when changes are detected."""
        from scripts import compare_landscape_versions

        # Create landscape file
        landscape_file = tmp_path / "landscape.yaml"
        landscape_file.write_text(yaml.dump({"entries": []}))

        # Create RSS data file
        rss_file = tmp_path / "rss.json"
        rss_file.write_text(
            json.dumps(
                {
                    "check_date": "2026-01-15",
                    "new_entries": [
                        {
                            "title": "New Doc",
                            "summary": "",
                            "url": "https://example.com",
                            "published": "2026-01-15",
                            "feed": "test",
                        }
                    ],
                }
            )
        )

        monkeypatch.setattr(
            sys,
            "argv",
            ["prog", "--landscape-file", str(landscape_file), "--rss-data", str(rss_file)],
        )

        with pytest.raises(SystemExit) as exc_info:
            compare_landscape_versions.main()

        assert exc_info.value.code == 0

    def test_exit_code_1_when_no_changes(self, tmp_path, monkeypatch):
        """Test exit code 1 when no changes are detected."""
        from scripts import compare_landscape_versions

        # Create landscape file
        landscape_file = tmp_path / "landscape.yaml"
        landscape_file.write_text(yaml.dump({"entries": []}))

        # Create RSS data file with no entries
        rss_file = tmp_path / "rss.json"
        rss_file.write_text(json.dumps({"check_date": "2026-01-15", "new_entries": []}))

        monkeypatch.setattr(
            sys,
            "argv",
            ["prog", "--landscape-file", str(landscape_file), "--rss-data", str(rss_file)],
        )

        with pytest.raises(SystemExit) as exc_info:
            compare_landscape_versions.main()

        assert exc_info.value.code == 1
