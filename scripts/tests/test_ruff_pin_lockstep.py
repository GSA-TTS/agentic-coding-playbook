"""Guard: the pyproject `ruff==` pin and the .pre-commit-config ruff-pre-commit
rev must stay in lockstep.

Divergent ruff versions mean the pre-commit hook lints/formats differently from
CI, so files can pass `git commit` locally yet fail `ruff` in CI (or vice-versa).
This test fails if the two pins drift, closing the gap even before the dependabot
pre-commit ecosystem bumps the hook.

Ported from agentic-coding-patterns (its #339) because this repo carries the
SAME dual pin with no guard at all. Kept deliberately close to that version so
the two do not themselves drift; the one addition is
``test_precommit_rev_is_sha_pinned_with_version_comment``.

KNOWN LIMIT, stated rather than implied: the pre-commit side is read from the
``# vX.Y.Z`` COMMENT, not from the pinned SHA. A SHA bumped with a stale comment
would pass this test. Resolving a SHA to its tag needs network, and pre-commit's
own cached clones carry no tags (it fetches a single rev), so there is no offline
way to do better here. What the extra test below does cover is the shape: a rev
that is not a full SHA, or a SHA with no version comment, now fails loudly
instead of making the lockstep check silently unverifiable.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_PRECOMMIT_RUFF_BLOCK = re.compile(
    r"astral-sh/ruff-pre-commit\s+rev:\s*(?P<rev>\S+)\s*#\s*v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)"
)


def _pyproject_ruff_version() -> str:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'"ruff==([0-9]+\.[0-9]+\.[0-9]+)"', text)
    assert m, "could not find the ruff== pin in pyproject.toml"
    return m.group(1)


def _precommit_ruff_match() -> re.Match[str]:
    text = (REPO / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    m = _PRECOMMIT_RUFF_BLOCK.search(text)
    assert m, (
        "could not find a ruff-pre-commit block of the form "
        "`rev: <sha>  # vX.Y.Z` in .pre-commit-config.yaml. The lockstep check "
        "cannot run without it -- fix the pin shape rather than skipping."
    )
    return m


def test_ruff_pins_match():
    py = _pyproject_ruff_version()
    pc = _precommit_ruff_match().group("version")
    assert py == pc, (
        f"ruff version drift: pyproject={py} vs ruff-pre-commit={pc}. "
        "Bump .pre-commit-config.yaml rev (SHA + `# vX.Y.Z` comment) to match the "
        "pyproject ruff pin."
    )


def test_precommit_rev_is_sha_pinned_with_version_comment():
    """The rev must be a full 40-hex SHA, not a tag.

    A tag is mutable, so `rev: v0.16.8` would let the hook's actual contents
    change without any file in this repo changing. This also guarantees the
    version comment that `test_ruff_pins_match` reads actually exists -- without
    it that test would fail on the assert in `_precommit_ruff_match` rather than
    quietly comparing against nothing.
    """
    rev = _precommit_ruff_match().group("rev")
    assert re.fullmatch(r"[0-9a-f]{40}", rev), (
        f"ruff-pre-commit rev {rev!r} is not a full 40-hex SHA. Pin by SHA with a "
        "`# vX.Y.Z` comment so the hook contents cannot change under a mutable tag."
    )
