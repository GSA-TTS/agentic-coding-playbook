"""Tests for the federal-AI landscape RSS monitor.

Covers the #182 precision work (source-aware relevance gate + scoped Federal
Register query) and the previously-untested diff/relevance logic. Network is
never hit: feedparser.parse is mocked and RSS_FEEDS is patched.
"""

from datetime import datetime, timedelta
from unittest import mock

import landscape_monitor as lm
import pytest

# ── Relevance gate (#182) ─────────────────────────────────────────────────────


class TestIsAiRelevant:
    """Source-aware AI relevance gate — the core #182 precision fix."""

    def test_strong_phrase_matches_any_source(self):
        assert lm._is_ai_relevant("New artificial intelligence rule", "Federal Register - AI")
        assert lm._is_ai_relevant("NIST AI RMF update", "Federal Register - AI")
        assert lm._is_ai_relevant("Guidance on automated decision-making", "White House")

    def test_bare_token_rejected_on_broad_federal_register_feed(self):
        # These are exactly the false positives #182 targets: a grant/committee
        # notice that merely contains "AI" or "algorithm" must NOT surface from
        # the broad Federal Register feed.
        assert not lm._is_ai_relevant("Notice of funding: AI Corridor transportation grant", "Federal Register - AI")
        assert not lm._is_ai_relevant(
            "Advisory committee meeting; algorithm for quota allocation", "Federal Register - AI"
        )
        assert not lm._is_ai_relevant("ML export classification notice", "Federal Register - AI")

    def test_bare_token_allowed_only_for_source_scoped_feed(self):
        # The NIST CSRC feed's corpus is already on-topic, so a bare token is OK.
        assert lm._is_ai_relevant("AI publication draft", "NIST CSRC")
        # ...but the same bare token on the broad feed is rejected.
        assert not lm._is_ai_relevant("AI publication draft", "Federal Register - AI")

    def test_non_ai_content_rejected_everywhere(self):
        assert not lm._is_ai_relevant("Quarterly budget report", "Federal Register - AI")
        assert not lm._is_ai_relevant("Quarterly budget report", "NIST CSRC")


class TestFederalRegisterQueryScoping:
    """#182: the Federal Register feed URL is document-type scoped."""

    def _fr_url(self):
        return next(f["url"] for f in lm.RSS_FEEDS if f["name"] == "Federal Register - AI")

    def test_query_is_type_scoped(self):
        url = self._fr_url()
        # Presidential documents + rules + proposed rules + notices, not an
        # unscoped term-only query.
        assert "conditions%5Btype%5D%5B%5D=PRESDOCU" in url
        assert "conditions%5Btype%5D%5B%5D=RULE" in url
        assert "per_page=50" in url

    def test_still_targets_documents_endpoint(self):
        assert "federalregister.gov/api/v1/documents.rss" in self._fr_url()


# ── fetch_rss_feeds (mocked feedparser) ───────────────────────────────────────


def _mock_feed(entries, *, bozo=False):
    feed = mock.MagicMock()
    feed.bozo = bozo
    feed.bozo_exception = Exception("bad") if bozo else None
    feed.entries = entries
    return feed


def _entry(title, *, summary="", link="https://example.gov/x", days_ago=1):
    published = (datetime.utcnow() - timedelta(days=days_ago)).timetuple()[:9]
    e = mock.MagicMock()
    e.title = title
    e.summary = summary
    e.link = link
    e.published_parsed = published
    # attribute presence matters (getattr / hasattr checks in code)
    del e.updated_parsed
    return e


class TestFetchRssFeeds:
    @pytest.fixture(autouse=True)
    def _require_feedparser(self, monkeypatch):
        monkeypatch.setattr(lm, "FEEDPARSER_AVAILABLE", True)

    def test_filters_out_irrelevant_broad_feed_items(self, monkeypatch):
        feed = _mock_feed(
            [
                _entry("Removing barriers to artificial intelligence", link="https://a.gov/1"),
                _entry("AI Corridor highway grant notice", link="https://a.gov/2"),
            ]
        )
        monkeypatch.setattr(lm.feedparser, "parse", lambda url: feed)
        monkeypatch.setattr(
            lm,
            "RSS_FEEDS",
            [{"name": "Federal Register - AI", "url": "x", "category_hint": "legislation"}],
        )
        out = lm.fetch_rss_feeds(lm.RSS_FEEDS)
        titles = [e.title for e in out]
        assert "Removing barriers to artificial intelligence" in titles
        assert "AI Corridor highway grant notice" not in titles

    def test_skips_entries_older_than_lookback(self, monkeypatch):
        feed = _mock_feed([_entry("NIST AI RMF profile released", days_ago=lm.LOOKBACK_DAYS + 10)])
        monkeypatch.setattr(lm.feedparser, "parse", lambda url: feed)
        monkeypatch.setattr(
            lm,
            "RSS_FEEDS",
            [{"name": "NIST CSRC", "url": "x", "category_hint": "nist_standard"}],
        )
        assert lm.fetch_rss_feeds(lm.RSS_FEEDS) == []

    def test_bozo_feed_skipped_without_raising(self, monkeypatch):
        monkeypatch.setattr(lm.feedparser, "parse", lambda url: _mock_feed([], bozo=True))
        monkeypatch.setattr(
            lm,
            "RSS_FEEDS",
            [{"name": "Federal Register - AI", "url": "x", "category_hint": "legislation"}],
        )
        assert lm.fetch_rss_feeds(lm.RSS_FEEDS) == []

    def test_no_feedparser_returns_empty(self, monkeypatch):
        monkeypatch.setattr(lm, "FEEDPARSER_AVAILABLE", False)
        assert lm.fetch_rss_feeds(lm.RSS_FEEDS) == []


# ── generate_diff (previously untested) ───────────────────────────────────────


class TestGenerateDiff:
    def test_new_publication_detected(self):
        rss = [
            lm.RSSEntry(
                title="New AI EO",
                url="https://new.gov/eo",
                published=datetime.utcnow(),
                source="White House",
                category_hint="executive_order",
            )
        ]
        report = lm.generate_diff([], {}, rss)
        assert len(report.new_publications) == 1
        assert report.new_publications[0].url == "https://new.gov/eo"

    def test_known_url_not_flagged_new(self):
        known = lm.RegistryEntry(
            id="eo-1",
            title="Known",
            url="https://known.gov/eo",
            date="2025-01-01",
            status="active",
            category="executive_order",
            relevance="r",
        )
        rss = [
            lm.RSSEntry(
                title="Known",
                url="https://known.gov/eo",
                published=datetime.utcnow(),
                source="White House",
                category_hint="executive_order",
            )
        ]
        report = lm.generate_diff([known], {known.url: known}, rss)
        assert report.new_publications == []

    def test_approaching_deadline_flagged(self):
        soon = (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d")
        entry = lm.RegistryEntry(
            id="m-1",
            title="Deadline soon",
            url="https://d.gov/1",
            date="2025-01-01",
            status="active",
            category="omb_memo",
            relevance="r",
            compliance_deadline=soon,
        )
        report = lm.generate_diff([entry], {entry.url: entry}, [])
        assert len(report.approaching_deadlines) == 1
        assert report.approaching_deadlines[0][0].id == "m-1"

    def test_far_deadline_not_flagged(self):
        far = (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d")
        entry = lm.RegistryEntry(
            id="m-2",
            title="Deadline far",
            url="https://d.gov/2",
            date="2025-01-01",
            status="active",
            category="omb_memo",
            relevance="r",
            compliance_deadline=far,
        )
        report = lm.generate_diff([entry], {entry.url: entry}, [])
        assert report.approaching_deadlines == []
