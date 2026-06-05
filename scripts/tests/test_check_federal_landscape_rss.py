"""Tests for check_federal_landscape_rss.py — RSS/Atom feed monitoring.

GitHub Issue: #83 - Add test coverage for landscape RSS scripts
"""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestLoadState:
    """Tests for load_state function."""

    def test_load_existing_state_file(self, tmp_path):
        """Test loading an existing valid state file."""
        from scripts.check_federal_landscape_rss import load_state

        state_file = tmp_path / "state.json"
        state_file.write_text(
            json.dumps(
                {
                    "last_updated": "2026-01-01T00:00:00Z",
                    "last_seen": {"feed1": ["id1", "id2"], "feed2": ["id3"]},
                }
            )
        )

        result = load_state(state_file)
        assert result == {"feed1": ["id1", "id2"], "feed2": ["id3"]}

    def test_load_missing_state_file(self, tmp_path):
        """Test loading when state file does not exist."""
        from scripts.check_federal_landscape_rss import load_state

        state_file = tmp_path / "nonexistent.json"
        result = load_state(state_file)
        assert result == {}

    def test_load_corrupted_json(self, tmp_path):
        """Test loading a corrupted JSON file."""
        from scripts.check_federal_landscape_rss import load_state

        state_file = tmp_path / "corrupted.json"
        state_file.write_text("{ invalid json }")

        result = load_state(state_file)
        assert result == {}

    def test_load_state_without_last_seen_key(self, tmp_path):
        """Test loading state file without last_seen key."""
        from scripts.check_federal_landscape_rss import load_state

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"last_updated": "2026-01-01T00:00:00Z"}))

        result = load_state(state_file)
        assert result == {}


class TestSaveState:
    """Tests for save_state function."""

    def test_save_creates_parent_dirs(self, tmp_path):
        """Test that save_state creates parent directories."""
        from scripts.check_federal_landscape_rss import save_state

        state_file = tmp_path / "nested" / "dirs" / "state.json"
        last_seen = {"feed1": ["id1"]}

        save_state(state_file, last_seen)

        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["last_seen"] == last_seen

    def test_save_overwrites_existing(self, tmp_path):
        """Test that save_state overwrites existing file."""
        from scripts.check_federal_landscape_rss import save_state

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"old": "data"}))

        new_state = {"feed1": ["new_id"]}
        save_state(state_file, new_state)

        data = json.loads(state_file.read_text())
        assert data["last_seen"] == new_state
        assert "old" not in data

    def test_save_includes_timestamp(self, tmp_path):
        """Test that save_state includes last_updated timestamp."""
        from scripts.check_federal_landscape_rss import save_state

        state_file = tmp_path / "state.json"
        save_state(state_file, {})

        data = json.loads(state_file.read_text())
        assert "last_updated" in data
        # Should be ISO format timestamp
        assert "T" in data["last_updated"]

    def test_save_handles_oserror(self, tmp_path, capsys):
        """Test that save_state handles OSError gracefully."""
        from scripts.check_federal_landscape_rss import save_state

        # Create a directory where we expect a file (will cause OSError)
        state_path = tmp_path / "state.json"
        state_path.mkdir()

        # Should not raise, just print warning
        save_state(state_path, {"feed": ["id"]})

        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "Could not save" in captured.err


class TestFetchFeed:
    """Tests for fetch_feed function."""

    def test_parse_valid_feed(self):
        """Test parsing a valid feed."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            {
                "id": "entry1",
                "title": "Test Entry",
                "link": "https://example.com/1",
                "published": "2026-01-01",
                "summary": "Test summary",
            }
        ]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert len(result) == 1
        assert result[0]["id"] == "entry1"
        assert result[0]["title"] == "Test Entry"

    def test_bozo_error_returns_empty(self, capsys):
        """Test that bozo errors with no entries return empty list."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = Exception("Parse error")
        mock_feed.entries = []

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result == []
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "test_feed" in captured.err  # Should include feed name
        assert "Parse error" in captured.err  # Should include exception message

    def test_extracts_entry_fields(self):
        """Test that all expected fields are extracted from entries."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            {
                "id": "unique-id",
                "title": "Entry Title",
                "link": "https://example.com/entry",
                "published": "2026-01-15T10:00:00Z",
                "summary": "Entry description",
            }
        ]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result[0]["id"] == "unique-id"
        assert result[0]["title"] == "Entry Title"
        assert result[0]["url"] == "https://example.com/entry"
        assert result[0]["published"] == "2026-01-15T10:00:00Z"
        assert result[0]["summary"] == "Entry description"

    def test_truncates_long_summaries(self):
        """Test that summaries longer than 500 chars are truncated."""
        from scripts.check_federal_landscape_rss import fetch_feed

        long_summary = "x" * 1000

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "1", "title": "Test", "summary": long_summary}]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert len(result[0]["summary"]) == 500

    def test_uses_link_when_id_missing(self):
        """Test fallback to link when id is missing."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"title": "No ID", "link": "https://example.com/fallback"}]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result[0]["id"] == "https://example.com/fallback"

    def test_handles_fetch_exception(self, capsys):
        """Test graceful handling of fetch exceptions."""
        from scripts.check_federal_landscape_rss import fetch_feed

        with patch(
            "scripts.check_federal_landscape_rss.feedparser.parse",
            side_effect=Exception("Network error"),
        ):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result == []
        captured = capsys.readouterr()
        assert "Error fetching" in captured.err


class TestCheckFeeds:
    """Tests for check_feeds function."""

    def test_detects_new_entries(self, tmp_path, capsys):
        """Test that new entries are detected correctly."""
        from scripts.check_federal_landscape_rss import check_feeds

        state_file = tmp_path / "state.json"
        # No existing state

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "new-entry", "title": "New Entry", "link": "https://example.com/new"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test_feed": "https://example.com/feed"}),
        ):
            result = check_feeds(state_file)

        # Verify complete result structure
        assert "check_date" in result
        assert "T" in result["check_date"]  # ISO format
        assert result["feeds_checked"] == 1
        assert len(result["new_entries"]) == 1

        # Verify complete entry structure
        entry = result["new_entries"][0]
        assert entry["id"] == "new-entry"
        assert entry["title"] == "New Entry"
        assert entry["feed"] == "test_feed"
        assert "url" in entry

    def test_ignores_seen_entries(self, tmp_path, capsys):
        """Test that previously seen entries are not reported as new."""
        from scripts.check_federal_landscape_rss import check_feeds

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"last_seen": {"test_feed": ["already-seen"]}}))

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "already-seen", "title": "Old Entry", "link": "https://example.com/old"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test_feed": "https://example.com/feed"}),
        ):
            result = check_feeds(state_file)

        assert len(result["new_entries"]) == 0

    def test_limits_to_100_ids_per_feed(self, tmp_path, capsys):
        """Test that only the latest 100 IDs are kept per feed."""
        from scripts.check_federal_landscape_rss import check_feeds

        state_file = tmp_path / "state.json"

        # Create 150 entries
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            {"id": f"entry-{i}", "title": f"Entry {i}", "link": f"https://example.com/{i}"} for i in range(150)
        ]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test_feed": "https://example.com/feed"}),
        ):
            check_feeds(state_file)

        # Verify state file only has 100 IDs
        saved_state = json.loads(state_file.read_text())
        assert len(saved_state["last_seen"]["test_feed"]) == 100

    def test_handles_empty_feeds(self, tmp_path, capsys):
        """Test handling of feeds with no entries."""
        from scripts.check_federal_landscape_rss import check_feeds

        state_file = tmp_path / "state.json"

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = []

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test_feed": "https://example.com/feed"}),
        ):
            result = check_feeds(state_file)

        assert result["new_entries"] == []
        assert result["feeds_checked"] == 1


class TestMain:
    """Tests for main CLI function."""

    def test_exit_code_0_when_new_entries(self, tmp_path, monkeypatch, capsys):
        """Test exit code 0 when new entries are found."""
        from scripts import check_federal_landscape_rss

        state_file = tmp_path / "state.json"
        monkeypatch.setattr(sys, "argv", ["prog", "--state-file", str(state_file)])

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "new", "title": "New", "link": "https://example.com"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test": "https://example.com/feed"}),
            pytest.raises(SystemExit) as exc_info,
        ):
            check_federal_landscape_rss.main()

        assert exc_info.value.code == 0

    def test_exit_code_1_when_no_new_entries(self, tmp_path, monkeypatch, capsys):
        """Test exit code 1 when no new entries are found."""
        from scripts import check_federal_landscape_rss

        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"last_seen": {"test": ["existing"]}}))
        monkeypatch.setattr(sys, "argv", ["prog", "--state-file", str(state_file)])

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "existing", "title": "Old", "link": "https://example.com"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test": "https://example.com/feed"}),
            pytest.raises(SystemExit) as exc_info,
        ):
            check_federal_landscape_rss.main()

        assert exc_info.value.code == 1

    def test_output_json_mode_suppresses_stderr(self, tmp_path, monkeypatch, capsys):
        """Test that --output-json suppresses stderr messages."""
        from scripts import check_federal_landscape_rss

        state_file = tmp_path / "state.json"
        monkeypatch.setattr(sys, "argv", ["prog", "--state-file", str(state_file), "--output-json"])

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "new", "title": "New", "link": "https://example.com"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test": "https://example.com/feed"}),
            pytest.raises(SystemExit),
        ):
            check_federal_landscape_rss.main()

        captured = capsys.readouterr()
        # Stderr should be empty in JSON mode
        assert captured.err == ""
        # Stdout should be valid JSON
        output = json.loads(captured.out)
        assert "new_entries" in output

    def test_cli_custom_state_file(self, tmp_path, monkeypatch, capsys):
        """Test that --state-file argument is respected."""
        from scripts import check_federal_landscape_rss

        custom_state = tmp_path / "custom" / "path" / "state.json"
        monkeypatch.setattr(sys, "argv", ["prog", "--state-file", str(custom_state)])

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [{"id": "new", "title": "New", "link": "https://example.com"}]

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed),
            patch("scripts.check_federal_landscape_rss.FEEDS", {"test": "https://example.com/feed"}),
            pytest.raises(SystemExit),
        ):
            check_federal_landscape_rss.main()

        # State file should be created at custom path
        assert custom_state.exists()

    def test_uses_updated_when_published_missing(self):
        """Test fallback to 'updated' field when 'published' is missing."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            {
                "id": "entry1",
                "title": "Test Entry",
                "link": "https://example.com/1",
                "updated": "2026-01-15T10:00:00Z",  # No 'published', has 'updated'
                "summary": "Test summary",
            }
        ]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result[0]["published"] == "2026-01-15T10:00:00Z"

    def test_uses_description_when_summary_missing(self):
        """Test fallback to 'description' field when 'summary' is missing."""
        from scripts.check_federal_landscape_rss import fetch_feed

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            {
                "id": "entry1",
                "title": "Test Entry",
                "link": "https://example.com/1",
                "description": "Entry description",  # No 'summary', has 'description'
            }
        ]

        with patch("scripts.check_federal_landscape_rss.feedparser.parse", return_value=mock_feed):
            result = fetch_feed("test_feed", "https://example.com/feed")

        assert result[0]["summary"] == "Entry description"

    def test_multiple_feeds(self, tmp_path, capsys):
        """Test checking multiple feeds at once."""
        from scripts.check_federal_landscape_rss import check_feeds

        state_file = tmp_path / "state.json"

        mock_feed1 = MagicMock()
        mock_feed1.bozo = False
        mock_feed1.entries = [{"id": "feed1-entry", "title": "Feed 1", "link": "https://example.com/1"}]

        mock_feed2 = MagicMock()
        mock_feed2.bozo = False
        mock_feed2.entries = [{"id": "feed2-entry", "title": "Feed 2", "link": "https://example.com/2"}]

        def mock_parse(url):
            if "feed1" in url:
                return mock_feed1
            return mock_feed2

        with (
            patch("scripts.check_federal_landscape_rss.feedparser.parse", side_effect=mock_parse),
            patch(
                "scripts.check_federal_landscape_rss.FEEDS",
                {"feed1": "https://example.com/feed1", "feed2": "https://example.com/feed2"},
            ),
        ):
            result = check_feeds(state_file)

        assert result["feeds_checked"] == 2
        assert len(result["new_entries"]) == 2
        feed_names = {e["feed"] for e in result["new_entries"]}
        assert feed_names == {"feed1", "feed2"}
