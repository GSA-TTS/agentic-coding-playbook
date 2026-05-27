#!/usr/bin/env python3
"""
compare_landscape_versions.py — Detect version changes in federal AI landscape

Compares entries in data/federal-ai-landscape.yaml against RSS feed data from
check_federal_landscape_rss.py to detect:
- Version updates (e.g., draft → final)
- Status changes (e.g., active → revoked)
- New publications not yet in the registry

Usage:
    python scripts/compare_landscape_versions.py [--landscape-file <path>] [--rss-data <path>]

    Or pipe RSS data from stdin:
    python scripts/check_federal_landscape_rss.py | python scripts/compare_landscape_versions.py

Dependencies:
    - PyYAML (already in pyproject.toml)

Output:
    JSON structure with detected changes
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Install it with: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

DEFAULT_LANDSCAPE_FILE = Path(__file__).parent.parent / "data" / "federal-ai-landscape.yaml"


def load_landscape(landscape_file: Path) -> dict[str, Any]:
    """Load the federal AI landscape YAML registry."""
    try:
        with open(landscape_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        print(f"Error: Could not load landscape file: {e}", file=sys.stderr)
        sys.exit(1)


def load_rss_data(rss_data_path: Path | None) -> dict[str, Any]:
    """Load RSS data from file or stdin."""
    if rss_data_path:
        try:
            with open(rss_data_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error: Could not load RSS data file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse RSS data from stdin: {e}", file=sys.stderr)
            sys.exit(1)


def extract_version(text: str) -> str | None:
    """Extract version number from title or summary text."""
    # Match patterns like "v1.0", "version 2.0", "V1.1", etc.
    version_patterns = [
        r"v\.?\s*(\d+\.\d+(?:\.\d+)?)",
        r"version\s+(\d+\.\d+(?:\.\d+)?)",
        r"rev\.?\s*(\d+)",
    ]

    for pattern in version_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_status(text: str) -> str | None:
    """Extract status keywords from title or summary text."""
    text_lower = text.lower()

    status_keywords = {
        "final": "final",
        "draft": "draft",
        "preliminary": "draft",
        "ipd": "draft",  # Initial Public Draft
        "active": "active",
        "revoked": "revoked",
        "rescinded": "rescinded",
        "superseded": "superseded",
    }

    for keyword, status in status_keywords.items():
        if keyword in text_lower:
            return status
    return None


def normalize_title(title: str) -> str:
    """Normalize title for comparison (lowercase, remove special chars)."""
    # Remove version numbers, punctuation, extra whitespace
    normalized = re.sub(r"v\.?\s*\d+\.\d+(?:\.\d+)?", "", title, flags=re.IGNORECASE)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def find_entry_in_landscape(rss_entry: dict[str, Any], landscape: dict[str, Any]) -> dict[str, Any] | None:
    """Find a matching entry in the landscape registry based on title similarity."""
    rss_title_normalized = normalize_title(rss_entry["title"])

    for entry in landscape.get("entries", []):
        entry_title_normalized = normalize_title(entry["title"])

        # Check for substantial title overlap (80% threshold)
        if similarity_score(rss_title_normalized, entry_title_normalized) > 0.8:
            return entry

    return None


def similarity_score(s1: str, s2: str) -> float:
    """Calculate simple word-based similarity score between two strings."""
    words1 = set(s1.split())
    words2 = set(s2.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def compare_versions(landscape: dict[str, Any], rss_data: dict[str, Any]) -> dict[str, Any]:
    """Compare landscape registry with RSS feed data and detect changes."""
    changes = []

    for rss_entry in rss_data.get("new_entries", []):
        existing = find_entry_in_landscape(rss_entry, landscape)

        if existing:
            # Check for version or status changes
            rss_version = extract_version(rss_entry["title"] + " " + rss_entry["summary"])
            rss_status = extract_status(rss_entry["title"] + " " + rss_entry["summary"])

            existing_version = existing.get("version") or existing.get("publication_id", "")
            existing_status = existing.get("status")

            version_changed = rss_version and rss_version not in existing_version
            status_changed = rss_status and rss_status != existing_status

            if version_changed or status_changed:
                changes.append(
                    {
                        "type": "update",
                        "id": existing["id"],
                        "title": existing["title"],
                        "change": {
                            "old_version": existing_version,
                            "new_version": rss_version,
                            "old_status": existing_status,
                            "new_status": rss_status,
                        },
                        "feed": rss_entry["feed"],
                        "url": rss_entry["url"],
                    }
                )
        else:
            # New publication not in registry
            changes.append(
                {
                    "type": "new_publication",
                    "title": rss_entry["title"],
                    "url": rss_entry["url"],
                    "published": rss_entry["published"],
                    "summary": rss_entry["summary"],
                    "feed": rss_entry["feed"],
                    "suggested_version": extract_version(rss_entry["title"] + " " + rss_entry["summary"]),
                    "suggested_status": extract_status(rss_entry["title"] + " " + rss_entry["summary"]),
                }
            )

    return {
        "comparison_date": rss_data.get("check_date"),
        "changes_detected": len(changes),
        "changes": changes,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Compare federal AI landscape registry with RSS feed data")
    parser.add_argument(
        "--landscape-file",
        type=Path,
        default=DEFAULT_LANDSCAPE_FILE,
        help=f"Path to landscape YAML file (default: {DEFAULT_LANDSCAPE_FILE})",
    )
    parser.add_argument(
        "--rss-data",
        type=Path,
        help="Path to RSS data JSON file (default: read from stdin)",
    )
    args = parser.parse_args()

    landscape = load_landscape(args.landscape_file)
    rss_data = load_rss_data(args.rss_data)

    result = compare_versions(landscape, rss_data)

    # Output JSON
    print(json.dumps(result, indent=2))

    # Exit with code 0 if changes detected, 1 if none
    sys.exit(0 if result["changes_detected"] > 0 else 1)


if __name__ == "__main__":
    main()
