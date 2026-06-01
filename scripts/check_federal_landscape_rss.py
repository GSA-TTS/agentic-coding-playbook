#!/usr/bin/env python3
"""
check_federal_landscape_rss.py — RSS/Atom feed monitoring for federal AI guidance

Monitors RSS/Atom feeds for new federal AI publications (NIST, Federal Register, White House, OWASP).
Stores last-seen entry IDs to detect new publications since last check.

Usage:
    python scripts/check_federal_landscape_rss.py [--state-file <path>] [--output-json]

Dependencies:
    - feedparser (install via: pip install feedparser)

State:
    Stores last-seen entry IDs in data/.landscape-rss-state.json

Output:
    JSON structure with check_date and new_entries list
"""

import argparse
import json
import os
import sys
from contextlib import redirect_stderr
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import feedparser
except ImportError:
    print("Error: feedparser is not installed. Install it with: pip install feedparser", file=sys.stderr)
    sys.exit(1)

# RSS/Atom feeds to monitor
FEEDS = {
    "federal_register_nist": "https://www.federalregister.gov/api/v1/articles.rss?conditions[agencies][]=national-institute-of-standards-and-technology",
    "whitehouse_actions": "https://www.whitehouse.gov/feed/",
    "nist_csrc": "https://csrc.nist.gov/publications/feed",
    "owasp_genai": "https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/releases.atom",
}

DEFAULT_STATE_FILE = Path(__file__).parent.parent / "data" / ".landscape-rss-state.json"


def load_state(state_file: Path) -> dict[str, list[str]]:
    """Load last-seen entry IDs from state file."""
    if state_file.exists():
        try:
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)
            return state.get("last_seen", {})
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load state file: {e}", file=sys.stderr)
    return {}


def save_state(state_file: Path, last_seen: dict[str, list[str]]) -> None:
    """Save last-seen entry IDs to state file."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "last_updated": datetime.now(UTC).isoformat(),
                    "last_seen": last_seen,
                },
                f,
                indent=2,
            )
    except OSError as e:
        print(f"Warning: Could not save state file: {e}", file=sys.stderr)


def fetch_feed(feed_name: str, feed_url: str) -> list[dict[str, Any]]:
    """Fetch and parse a single feed. Returns list of entries."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            print(f"Warning: Could not parse feed {feed_name}: {feed.bozo_exception}", file=sys.stderr)
            return []

        entries = []
        for entry in feed.entries:
            # Extract common fields
            entry_data = {
                "id": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", "No title"),
                "url": entry.get("link", ""),
                "published": entry.get("published", entry.get("updated", "")),
                "summary": entry.get("summary", entry.get("description", ""))[:500],  # Truncate summary
            }
            entries.append(entry_data)
        return entries
    except Exception as e:  # noqa: BLE001
        print(f"Warning: Error fetching feed {feed_name}: {e}", file=sys.stderr)
        return []


def check_feeds(state_file: Path) -> dict[str, Any]:
    """Check all feeds and return new entries."""
    last_seen = load_state(state_file)
    new_entries = []
    updated_last_seen = {}

    for feed_name, feed_url in FEEDS.items():
        print(f"Checking feed: {feed_name}...", file=sys.stderr)
        entries = fetch_feed(feed_name, feed_url)

        if not entries:
            print(f"  No entries found for {feed_name}", file=sys.stderr)
            updated_last_seen[feed_name] = last_seen.get(feed_name, [])
            continue

        # Get last-seen IDs for this feed
        seen_ids = set(last_seen.get(feed_name, []))
        current_ids = []

        for entry in entries:
            entry_id = entry["id"]
            current_ids.append(entry_id)

            # If this entry is new, add it to the results
            if entry_id not in seen_ids:
                new_entries.append(
                    {
                        "feed": feed_name,
                        **entry,
                    }
                )
                print(f"  New entry: {entry['title']}", file=sys.stderr)

        # Update last-seen to include all current IDs (keep up to 100 per feed)
        updated_last_seen[feed_name] = current_ids[:100]

        new_count = len([e for e in new_entries if e["feed"] == feed_name])
        print(f"  Found {len(entries)} total, {new_count} new", file=sys.stderr)

    # Save updated state
    save_state(state_file, updated_last_seen)

    return {
        "check_date": datetime.now(UTC).isoformat(),
        "new_entries": new_entries,
        "feeds_checked": len(FEEDS),
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor RSS feeds for federal AI guidance updates")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_FILE,
        help=f"Path to state file (default: {DEFAULT_STATE_FILE})",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output only JSON (no stderr messages)",
    )
    args = parser.parse_args()

    if args.output_json:
        # Suppress stderr messages in JSON-only mode using proper context manager
        with open(os.devnull, "w") as devnull, redirect_stderr(devnull):
            result = check_feeds(args.state_file)
    else:
        result = check_feeds(args.state_file)

    # Always output JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with code 0 if new entries found, 1 if none
    sys.exit(0 if result["new_entries"] else 1)


if __name__ == "__main__":
    main()
