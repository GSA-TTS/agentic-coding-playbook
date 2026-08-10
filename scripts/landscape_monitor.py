"""Federal AI landscape RSS monitor.

Fetches RSS feeds from federal sources, compares against the local registry,
and generates diff reports for human review.

Part of the federal-landscape-update skill.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import yaml

try:
    import feedparser  # type: ignore[import-untyped]

    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {
        "name": "White House",
        "url": "https://www.whitehouse.gov/feed/",
        "category_hint": "executive_order",
    },
    {
        "name": "NIST CSRC",
        "url": "https://csrc.nist.gov/csrc/feed/publications",
        "category_hint": "nist_standard",
    },
    {
        "name": "Federal Register - AI",
        # Scoped query (#182): restrict to the document types that carry AI
        # governance (presidential documents, rules, proposed rules, notices)
        # rather than an unscoped free-text term match that also returns grant
        # notices, meeting announcements, and export bulletins. `per_page`
        # bounds the response; `order=newest` keeps the most recent first.
        "url": (
            "https://www.federalregister.gov/api/v1/documents.rss"
            "?conditions%5Bterm%5D=artificial+intelligence"
            "&conditions%5Btype%5D%5B%5D=PRESDOCU"
            "&conditions%5Btype%5D%5B%5D=RULE"
            "&conditions%5Btype%5D%5B%5D=PRORULE"
            "&conditions%5Btype%5D%5B%5D=NOTICE"
            "&order=newest&per_page=50"
        ),
        "category_hint": "legislation",
    },
]

# Strong AI-governance signal (#182). A single loose token like a bare "AI",
# "ML", or "algorithm" is NOT enough on its own — those matched grant notices,
# committee announcements, and unrelated rules. An item is surfaced only if its
# title+summary matches one of these specific phrases. (A bare-token secondary
# pass is applied ONLY to feeds already scoped to an AI/NIST source; see
# `_is_ai_relevant`.)
AI_KEYWORDS = re.compile(
    r"\b("
    r"artificial intelligence|"
    r"machine learning|"
    r"large language model|LLM|"
    r"generative AI|gen(?:erative)?\s?AI|"
    r"foundation model|frontier model|"
    r"neural network|deep learning|"
    r"automated decision|automated decision-?making|"
    r"NIST AI|AI RMF|AI risk management|"
    r"agentic|AI safety|AI governance|"
    r"algorithmic (?:accountability|impact|bias)"
    r")\b",
    re.IGNORECASE,
)

# Weak tokens that only count when the feed is ALREADY AI/NIST-scoped by source
# (e.g. the NIST CSRC feed). On the broad Federal Register feed a bare "AI"/"ML"
# is too noisy to surface on its own.
_WEAK_AI_TOKENS = re.compile(r"\b(AI|ML|algorithm)\b")
# Feeds whose SOURCE already narrows the topic — the weak token pass is allowed
# for these because the surrounding corpus is on-topic.
_SOURCE_SCOPED_FEEDS = frozenset({"NIST CSRC"})

# How far back to look in RSS feeds (days)
LOOKBACK_DAYS = 90

# Deadline warning threshold (days)
DEADLINE_WARNING_DAYS = 30


# ─────────────────────────────────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RSSEntry:
    """Represents an entry from an RSS feed."""

    title: str
    url: str
    published: datetime | None
    source: str
    category_hint: str
    summary: str = ""


@dataclass
class RegistryEntry:
    """Represents an entry from the federal AI landscape registry."""

    id: str
    title: str
    url: str
    date: str
    status: str
    category: str
    relevance: str
    compliance_deadline: str | None = None


@dataclass
class DiffReport:
    """Aggregated diff report data."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    registry_path: str = ""
    feeds_checked: int = 0
    new_publications: list[RSSEntry] = field(default_factory=list)
    approaching_deadlines: list[tuple[RegistryEntry, int]] = field(default_factory=list)
    staleness_warnings: list[RegistryEntry] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Registry Loading
# ─────────────────────────────────────────────────────────────────────────────


def load_registry(path: Path) -> tuple[list[RegistryEntry], dict[str, RegistryEntry]]:
    """Load the federal AI landscape registry from YAML.

    Returns (list of entries, dict keyed by URL for quick lookup).
    """
    entries: list[RegistryEntry] = []
    url_index: dict[str, RegistryEntry] = {}

    if not path.exists():
        return entries, url_index

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "entries" not in data:
        return entries, url_index

    for item in data["entries"]:
        entry = RegistryEntry(
            id=item.get("id", ""),
            title=item.get("title", ""),
            url=item.get("url", ""),
            date=item.get("date", ""),
            status=item.get("status", ""),
            category=item.get("category", ""),
            relevance=item.get("relevance", ""),
            compliance_deadline=item.get("compliance_deadline"),
        )
        entries.append(entry)
        if entry.url:
            url_index[entry.url] = entry

    return entries, url_index


# ─────────────────────────────────────────────────────────────────────────────
# RSS Feed Fetching
# ─────────────────────────────────────────────────────────────────────────────


def _is_ai_relevant(text: str, source: str) -> bool:
    """True if ``text`` (title+summary) is AI-governance relevant for ``source``.

    Precision gate for #182: a strong-phrase match always qualifies. A weak bare
    token ("AI"/"ML"/"algorithm") qualifies ONLY when the feed source is already
    topic-scoped (e.g. NIST CSRC), so the broad Federal Register feed no longer
    surfaces grant notices / meeting announcements that merely contain "AI".
    """
    if AI_KEYWORDS.search(text):
        return True
    return source in _SOURCE_SCOPED_FEEDS and bool(_WEAK_AI_TOKENS.search(text))


def fetch_rss_feeds(feeds: list[dict[str, str]]) -> list[RSSEntry]:
    """Fetch and parse RSS feeds, filtering for AI-related content."""
    if not FEEDPARSER_AVAILABLE:
        return []

    entries: list[RSSEntry] = []
    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)

    for feed_config in feeds:
        try:
            feed = feedparser.parse(feed_config["url"])
            if feed.bozo and feed.bozo_exception:
                # Feed parsing error - continue with other feeds
                continue

            for item in feed.entries:
                # Parse publication date
                published = None
                if hasattr(item, "published_parsed") and item.published_parsed:
                    published = datetime(*item.published_parsed[:6])
                elif hasattr(item, "updated_parsed") and item.updated_parsed:
                    published = datetime(*item.updated_parsed[:6])

                # Skip old entries
                if published and published < cutoff:
                    continue

                # Get title and summary
                title = getattr(item, "title", "")
                summary = getattr(item, "summary", "")
                link = getattr(item, "link", "")

                # Filter for AI-related content (source-aware precision, #182)
                text_to_check = f"{title} {summary}"
                if not _is_ai_relevant(text_to_check, feed_config["name"]):
                    continue

                entries.append(
                    RSSEntry(
                        title=title,
                        url=link,
                        published=published,
                        source=feed_config["name"],
                        category_hint=feed_config["category_hint"],
                        summary=summary[:500] if summary else "",
                    )
                )
        except Exception:  # noqa: S112 - intentional continue on RSS parsing errors
            # Network or parsing error - continue with other feeds
            continue

    return entries


# ─────────────────────────────────────────────────────────────────────────────
# Diff Generation
# ─────────────────────────────────────────────────────────────────────────────


def generate_diff(
    registry_entries: list[RegistryEntry],
    url_index: dict[str, RegistryEntry],
    rss_entries: list[RSSEntry],
) -> DiffReport:
    """Compare RSS entries against registry and generate diff report."""
    report = DiffReport(feeds_checked=len(RSS_FEEDS))
    today = datetime.utcnow()

    # Find new publications (in RSS but not in registry)
    for rss_entry in rss_entries:
        if rss_entry.url and rss_entry.url not in url_index:
            report.new_publications.append(rss_entry)

    # Check for approaching deadlines
    for entry in registry_entries:
        if entry.compliance_deadline:
            try:
                deadline = datetime.strptime(entry.compliance_deadline, "%Y-%m-%d")
                days_until = (deadline - today).days
                if days_until <= DEADLINE_WARNING_DAYS:
                    report.approaching_deadlines.append((entry, days_until))
            except ValueError:
                pass

    # Sort deadlines by urgency
    report.approaching_deadlines.sort(key=lambda x: x[1])

    return report


# ─────────────────────────────────────────────────────────────────────────────
# Report Rendering
# ─────────────────────────────────────────────────────────────────────────────


def render_report(report: DiffReport, registry_path: str) -> str:
    """Render the diff report as Markdown."""
    lines: list[str] = []

    lines.append("# Federal AI Landscape Diff Report")
    lines.append("")
    lines.append(f"**Generated:** {report.generated_at.isoformat()}Z")
    lines.append(f"**Registry:** {registry_path}")
    lines.append(f"**Feeds Checked:** {report.feeds_checked}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- New publications found: {len(report.new_publications)}")
    lines.append(f"- Deadlines within {DEADLINE_WARNING_DAYS} days: {len(report.approaching_deadlines)}")
    lines.append(f"- Staleness warnings: {len(report.staleness_warnings)}")
    lines.append("")

    # New publications
    if report.new_publications:
        lines.append("## New Publications")
        lines.append("")
        for i, pub in enumerate(report.new_publications, 1):
            lines.append(f"### {i}. {pub.title}")
            lines.append("")
            lines.append(f"- **Source:** {pub.source}")
            if pub.published:
                lines.append(f"- **Date:** {pub.published.strftime('%Y-%m-%d')}")
            lines.append(f"- **URL:** {pub.url}")
            lines.append(f"- **Suggested Category:** {pub.category_hint}")
            if pub.summary:
                lines.append(f"- **Summary:** {pub.summary[:200]}...")
            lines.append("")
            lines.append("**Action Required:** Review for relevance and add to registry if applicable.")
            lines.append("")
    else:
        lines.append("## New Publications")
        lines.append("")
        lines.append("No new AI-related publications found in RSS feeds.")
        lines.append("")

    # Approaching deadlines
    if report.approaching_deadlines:
        lines.append("## Approaching Deadlines")
        lines.append("")
        for entry, days in report.approaching_deadlines:
            status = "PAST DUE" if days < 0 else f"{days} days remaining"
            lines.append(f"### {entry.title}")
            lines.append("")
            lines.append(f"- **Entry ID:** {entry.id}")
            lines.append(f"- **Deadline:** {entry.compliance_deadline}")
            lines.append(f"- **Status:** {status}")
            lines.append("")
            lines.append("**Action Required:** Verify compliance status.")
            lines.append("")
    else:
        lines.append("## Approaching Deadlines")
        lines.append("")
        lines.append("No compliance deadlines within the next 30 days.")
        lines.append("")

    # Staleness warnings
    lines.append("## Staleness Warnings")
    lines.append("")
    if report.staleness_warnings:
        for entry in report.staleness_warnings:
            lines.append(f"- **{entry.id}:** {entry.title} (last updated: {entry.date})")
    else:
        lines.append("None.")
    lines.append("")

    # Errors
    if report.errors:
        lines.append("## Errors")
        lines.append("")
        for error in report.errors:
            lines.append(f"- {error}")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the landscape monitor."""
    parser = argparse.ArgumentParser(description="Monitor RSS feeds for federal AI guidance updates")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/federal-ai-landscape.yaml"),
        help="Path to the federal AI landscape registry YAML",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for the diff report (default: stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be checked without fetching feeds",
    )
    args = parser.parse_args(argv)

    if not FEEDPARSER_AVAILABLE:
        print("Error: feedparser library not installed. Run: pip install feedparser", file=sys.stderr)
        return 1

    # Load registry
    registry_entries, url_index = load_registry(args.registry)
    print(f"Loaded {len(registry_entries)} entries from registry", file=sys.stderr)

    if args.dry_run:
        print("Dry run mode - would check these feeds:", file=sys.stderr)
        for feed in RSS_FEEDS:
            print(f"  - {feed['name']}: {feed['url']}", file=sys.stderr)
        return 0

    # Fetch RSS feeds
    print("Fetching RSS feeds...", file=sys.stderr)
    rss_entries = fetch_rss_feeds(RSS_FEEDS)
    print(f"Found {len(rss_entries)} AI-related entries in feeds", file=sys.stderr)

    # Generate diff
    report = generate_diff(registry_entries, url_index, rss_entries)
    report.registry_path = str(args.registry)

    # Render report
    markdown = render_report(report, str(args.registry))

    # Output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(markdown)

    # Return non-zero if there are items needing review
    if report.new_publications or report.approaching_deadlines:
        return 2  # Signal that review is needed (not an error)

    return 0


if __name__ == "__main__":
    sys.exit(main())
