"""Tests for landscape registry validation."""

import yaml
from playbook_validator.validate_landscape import validate_landscape


def _write_yaml(tmp_path, data):
    """Helper to write a YAML file for testing."""
    yaml_file = tmp_path / "landscape.yaml"
    yaml_file.write_text(yaml.dump(data, default_flow_style=False))
    return yaml_file


class TestValidateLandscape:
    """Test the landscape YAML validator."""

    def test_valid_registry(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test-entry",
                    "title": "Test Entry",
                    "category": "executive_order",
                    "source": "White House",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test relevance",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert errors == []

    def test_missing_required_field(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test-entry",
                    "title": "Test",
                    # missing: category, source, date, status, relevance, url
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert len(errors) >= 5  # multiple missing fields

    def test_invalid_category(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "invalid_category",
                    "source": "Test",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("category" in e for e in errors)

    def test_agency_report_category_is_valid(self, tmp_path):
        """agency_report is an accepted category (GAO/USCO-style reports)."""
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "usco-test",
                    "title": "Copyright and Artificial Intelligence, Part 2",
                    "category": "agency_report",
                    "source": "U.S. Copyright Office",
                    "date": "2025-01-29",
                    "status": "active",
                    "relevance": "Agency position for context; not legal advice.",
                    "url": "https://www.copyright.gov/ai/",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert not any("category" in e for e in errors)

    def test_invalid_status(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "legislation",
                    "source": "Congress",
                    "date": "2025-01-01",
                    "status": "invalid_status",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("status" in e for e in errors)

    def test_invalid_date_format(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "legislation",
                    "source": "Congress",
                    "date": "Jan 2025",  # wrong format
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("date" in e for e in errors)

    def test_duplicate_ids(self, tmp_path):
        entry = {
            "id": "duplicate-id",
            "title": "Test",
            "category": "legislation",
            "source": "Congress",
            "date": "2025-01-01",
            "status": "active",
            "relevance": "Test",
            "url": "https://example.com",
        }
        data = {"version": "1.0", "total_entries": 2, "entries": [entry, entry]}
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("duplicate" in e.lower() for e in errors)

    def test_wrong_total_entries(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 5,  # wrong count
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "legislation",
                    "source": "Congress",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("total_entries" in e for e in errors)

    def test_entries_not_a_list(self, tmp_path):
        data = {"version": "1.0", "entries": "not a list"}
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("must be a list" in e for e in errors)

    def test_returns_entry_count(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "legislation",
                    "source": "Congress",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                }
            ],
        }
        errors, warnings, count = validate_landscape(_write_yaml(tmp_path, data))
        assert count == 1
        assert errors == []

    def test_cross_reference_warning(self, tmp_path):
        data = {
            "version": "1.0",
            "total_entries": 1,
            "entries": [
                {
                    "id": "test",
                    "title": "Test",
                    "category": "executive_order",
                    "source": "White House",
                    "date": "2025-01-01",
                    "status": "active",
                    "relevance": "Test",
                    "url": "https://example.com",
                    "revokes": ["nonexistent-id"],
                }
            ],
        }
        errors, warnings, _count = validate_landscape(_write_yaml(tmp_path, data))
        assert any("nonexistent-id" in w for w in warnings)
