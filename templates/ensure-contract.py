#!/usr/bin/env python3
"""Ensure the universal Federal AI Agent Behavioral Contract is available.

SELF-CONTAINED — this script has NO third-party dependencies and does NOT
require the ``playbook-validator`` package to be installed. It is emitted into
downstream projects by ``new-project`` so the contract prerequisite can be
enforced (session start, pre-commit hook, and CI) without installing anything.

It mirrors ``playbook_validator/ensure_contract.py`` in the agentic-coding
playbook. Keep the two in sync; the playbook is the source of truth.

Precedence (first match wins), all deterministic filesystem facts:

  1. Home (environment-provided): $AGENTIC_CODING_PLAYBOOK_HOME/AGENTS.md,
     else ~/.agentic-coding-playbook/AGENTS.md
  2. Fresh cache: .agents/cache/AGENTS.universal.md whose sibling .stamp
     records the pinned release tag
  3. Fetch the pinned release into the cache
  4. Halt (fail-closed) — the contract is genuinely unobtainable

Exit code 0 means the contract is present (by an acceptable means). Non-zero is
the fail-closed halt: DO NOT proceed. There is no "proceed without" path.

The fetch URL is hard-coded to the canonical repository's pinned release and is
NEVER derived from repository, file, or issue content (prompt-injection safety).
"""

import argparse
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HOME = Path.home() / ".agentic-coding-playbook"
HOME_OVERRIDE_ENV = "AGENTIC_CODING_PLAYBOOK_HOME"
CONTRACT_FILENAME = "AGENTS.md"

CACHE_RELPATH = Path(".agents/cache/AGENTS.universal.md")
STAMP_RELPATH = Path(".agents/cache/AGENTS.universal.stamp")

# Pinned release the cache is fetched from and measured against. Hard-coded.
PINNED_RELEASE_TAG = "v0.13.0"
CONTRACT_RAW_URL = (
    "https://raw.githubusercontent.com/GSA-TTS/agentic-coding-playbook/"
    f"{PINNED_RELEASE_TAG}/AGENTS.md"
)
_FETCH_TIMEOUT_SECONDS = 15


def _home_contract_path() -> Path:
    override = os.environ.get(HOME_OVERRIDE_ENV)
    base = Path(override).expanduser() if override else DEFAULT_HOME
    return base / CONTRACT_FILENAME


def _is_present(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def _read_stamp_tag(stamp_path: Path) -> str | None:
    if not stamp_path.is_file():
        return None
    try:
        for line in stamp_path.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "release_tag":
                return value.strip()
    except OSError:
        return None
    return None


def _write_cache(cache_path: Path, stamp_path: Path, content: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(content, encoding="utf-8")
    stamp = (
        f"source_url={CONTRACT_RAW_URL}\n"
        f"release_tag={PINNED_RELEASE_TAG}\n"
        f"fetched_at={datetime.now(timezone.utc).isoformat()}\n"
    )
    stamp_path.write_text(stamp, encoding="utf-8")


def _fetch_contract() -> str | None:
    try:
        req = urllib.request.Request(CONTRACT_RAW_URL, method="GET")  # noqa: S310
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT_SECONDS) as resp:  # noqa: S310
            if resp.status != 200:
                return None
            data = resp.read().decode("utf-8")
            return data if data.strip() else None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def ensure_contract(repo_root: Path, *, allow_fetch: bool = True) -> int:
    """Return 0 if the contract is available, non-zero to halt (fail-closed)."""
    home_path = _home_contract_path()
    if _is_present(home_path):
        print(f"present-home: universal contract at {home_path}")
        return 0

    cache_path = repo_root / CACHE_RELPATH
    stamp_path = repo_root / STAMP_RELPATH
    warn = (
        f"WARNING: using cached universal contract ({cache_path}). This is a "
        "fallback — the canonical way to provide it is documented in the "
        "project README. Remove the cache once your environment provides the "
        "contract at the home path."
    )

    if _is_present(cache_path):
        if _read_stamp_tag(stamp_path) == PINNED_RELEASE_TAG:
            print(warn, file=sys.stderr)
            print(f"present-cache-fresh: universal contract in cache ({cache_path})")
            return 0
        if not allow_fetch:
            print(warn, file=sys.stderr)
            print(f"present-cache-stale: cached contract not {PINNED_RELEASE_TAG}; fetch disabled")
            return 0

    if allow_fetch:
        content = _fetch_contract()
        if content is not None:
            _write_cache(cache_path, stamp_path, content)
            print(warn, file=sys.stderr)
            print(f"fetched-to-cache: universal contract ({PINNED_RELEASE_TAG}) -> {cache_path}")
            return 0

    print(
        "absent: universal behavioral contract is NOT available and could not be "
        f"obtained. Expected at {home_path} (or the git-ignored cache). Do NOT "
        "proceed. Provide the contract per the project README, then retry.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure the universal behavioral contract is available")
    parser.add_argument("--root", default=".", help="Working project root (where the cache lives)")
    parser.add_argument("--no-fetch", action="store_true", help="Do not fetch; use only home path or existing cache")
    args = parser.parse_args()
    return ensure_contract(Path(args.root), allow_fetch=not args.no_fetch)


if __name__ == "__main__":
    sys.exit(main())
