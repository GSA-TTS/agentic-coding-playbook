"""Deterministic availability check for the universal behavioral contract.

The universal ``AGENTS.md`` (the *Federal AI Agent Behavioral Best Practices*)
is intentionally NOT vendored into downstream projects — it is expected to be
made available to the agent by the environment. This module lets an agent decide
*deterministically* (a filesystem fact, not an LLM self-attestation and not an
interactive per-session human confirmation) whether the contract is present, and
to populate a git-ignored fallback cache when it is not.

Precedence (first match wins):

1. **Home (environment-provided).** ``$AGENTIC_CODING_PLAYBOOK_HOME/AGENTS.md``
   if the override is set, else ``~/.agentic-coding-playbook/AGENTS.md``.
   Present + non-empty ⇒ satisfied; nothing is fetched or written.
2. **Fresh cache.** ``<repo>/.agents/cache/AGENTS.universal.md`` with a sibling
   ``.stamp`` whose ``release_tag`` matches the pinned release ⇒ satisfied
   (emits a "using cached fallback" warning).
3. **Fetch.** Neither present (or cache stale) ⇒ fetch the contract from the
   pinned release into the cache, write the stamp, warn.
4. **Halt.** Fetch impossible (offline / blocked) ⇒ fail-closed: the contract
   is genuinely unobtainable, so the agent MUST NOT proceed.

Design constraints (from PR #144 review, issues #147 and #151):

- **Fail-closed on outcome.** There is no "proceed without the contract" path.
- **Canonical by declaration, not content.** The playbook's own AGENTS.md is
  recognized as the universal contract by its explicit ``agents_contract:
  universal`` frontmatter marker — never by a title substring or heading that a
  thin project layer legitimately reproduces (issue #151).
- **§11 safety.** The fetch URL is hard-coded to the canonical repository's
  pinned release. It is NEVER derived from repository, file, or issue content.
- **Headless-safe.** No step requires interactive user input, so agents invoked
  non-interactively (``agent -p "..."``) work without a human in the loop.
"""

import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from playbook_validator.config import CONTRACT_ROLE_FIELD, CONTRACT_ROLE_UNIVERSAL
from playbook_validator.frontmatter import extract_frontmatter

# ── Convention constants (single source of truth) ───────────────────────────

# Environment-agnostic canonical home for the universal contract. Any provider
# (the sbx mixin kit, a dotfiles setup, a manual clone) may satisfy it.
DEFAULT_HOME = Path.home() / ".agentic-coding-playbook"
HOME_OVERRIDE_ENV = "AGENTIC_CODING_PLAYBOOK_HOME"
CONTRACT_FILENAME = "AGENTS.md"

# Repo-local, git-ignored fallback cache (flat single file + stamp).
CACHE_RELPATH = Path(".agents/cache/AGENTS.universal.md")
STAMP_RELPATH = Path(".agents/cache/AGENTS.universal.stamp")

# Pinned release the cache is fetched from and measured against. The raw URL is
# hard-coded (never taken from untrusted content) per §11.
PINNED_RELEASE_TAG = "v0.13.0"
CONTRACT_RAW_URL = f"https://raw.githubusercontent.com/GSA-TTS/agentic-coding-playbook/{PINNED_RELEASE_TAG}/AGENTS.md"

_FETCH_TIMEOUT_SECONDS = 15


class ContractStatus(StrEnum):
    """Outcome of an availability check."""

    HOME = "present-home"
    CACHE_FRESH = "present-cache-fresh"
    FETCHED = "fetched-to-cache"
    STALE = "present-cache-stale"
    ABSENT = "absent"


@dataclass
class ContractResult:
    """Result of ``ensure_contract``.

    ``ok`` is True when the contract is present by an acceptable means (home,
    fresh cache, or a successful fetch). It is False only when the contract is
    genuinely unobtainable — the fail-closed halt condition.
    """

    status: ContractStatus
    ok: bool
    path: Path | None
    message: str
    warning: str | None = None

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1


def _home_contract_path() -> Path:
    """Resolve the home contract path, honoring the override env var.

    The override wins; otherwise the module-level ``DEFAULT_HOME`` is used
    (computed from ``Path.home()`` at import, patchable in tests).
    """
    override = os.environ.get(HOME_OVERRIDE_ENV)
    base = Path(override).expanduser() if override else DEFAULT_HOME
    return base / CONTRACT_FILENAME


def _is_present(path: Path) -> bool:
    """A contract file counts as present only if it exists and is non-empty."""
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


# The universal contract declares its canonical role EXPLICITLY in frontmatter
# (`agents_contract: universal`). We recognize it by that deliberate signal —
# NOT by a title substring or section heading, both of which the thin project
# layer legitimately reproduces (it *names* the contract in its Prerequisite
# section). This closes the self-host false-positive in issue #151, where a
# bootstrapped project's own thin AGENTS.md matched a title-substring check.


def _is_playbook_contract(path: Path) -> bool:
    """True if ``path`` is the universal contract itself (the playbook's own
    AGENTS.md), recognized by its explicit ``agents_contract: universal``
    frontmatter marker. This lets the playbook repo satisfy its own prerequisite
    check without a home-path install, while a downstream project's thin
    AGENTS.md (role ``project`` or no marker) never self-satisfies."""
    if not _is_present(path):
        return False
    try:
        return extract_frontmatter(path).get(CONTRACT_ROLE_FIELD) == CONTRACT_ROLE_UNIVERSAL
    except OSError:
        return False


def _read_stamp_tag(stamp_path: Path) -> str | None:
    """Return the ``release_tag`` recorded in the cache stamp, if any."""
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
    """Write the fetched contract and its provenance stamp into the cache."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(content, encoding="utf-8")
    stamp = (
        f"source_url={CONTRACT_RAW_URL}\nrelease_tag={PINNED_RELEASE_TAG}\nfetched_at={datetime.now(UTC).isoformat()}\n"
    )
    stamp_path.write_text(stamp, encoding="utf-8")


def _fetch_contract() -> str | None:
    """Fetch the pinned contract from the hard-coded canonical URL.

    Returns the contract text, or None on any network/HTTP failure. The URL is a
    module constant — never derived from caller input or repository content.
    """
    try:
        # URL is a hard-coded https constant, not caller-supplied (§11).
        req = urllib.request.Request(CONTRACT_RAW_URL, method="GET")  # noqa: S310
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT_SECONDS) as resp:  # noqa: S310
            if resp.status != 200:
                return None
            data = resp.read().decode("utf-8")
            return data if data.strip() else None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def ensure_contract(repo_root: Path, *, allow_fetch: bool = True) -> ContractResult:
    """Deterministically ensure the universal contract is available.

    Args:
        repo_root: Root of the working project (where the cache lives).
        allow_fetch: When False, skip the network fetch step (useful for tests
            and offline environments); a stale/absent cache then halts.

    Returns:
        ContractResult. ``ok`` False is the fail-closed halt signal.
    """
    # 0. Self-hosting: in the playbook repository itself, the repo's own
    #    AGENTS.md *is* the universal contract. This lets the playbook dogfood
    #    the check in its own pre-commit/CI without a home-path install.
    self_contract = repo_root / "AGENTS.md"
    if _is_playbook_contract(self_contract):
        return ContractResult(
            status=ContractStatus.HOME,
            ok=True,
            path=self_contract,
            message=f"Universal contract is this repository's own {self_contract.name}.",
        )

    # 1. Environment-provided home contract short-circuits everything.
    home_path = _home_contract_path()
    if _is_present(home_path):
        return ContractResult(
            status=ContractStatus.HOME,
            ok=True,
            path=home_path,
            message=f"Universal contract present at {home_path}.",
        )

    cache_path = repo_root / CACHE_RELPATH
    stamp_path = repo_root / STAMP_RELPATH
    stale_warning = (
        "Using a cached copy of the universal contract "
        f"({cache_path}). This is a fallback — the canonical way to provide it "
        "is documented in the project README (agentic-coding-patterns sbx "
        "mixin kit). Remove the cache once your environment provides the "
        "contract at the home path."
    )

    # 2. Fresh cache (present and matching the pinned release tag).
    if _is_present(cache_path):
        if _read_stamp_tag(stamp_path) == PINNED_RELEASE_TAG:
            return ContractResult(
                status=ContractStatus.CACHE_FRESH,
                ok=True,
                path=cache_path,
                message=f"Universal contract present in cache ({cache_path}).",
                warning=stale_warning,
            )
        # Cache exists but is behind the pinned release → try to refresh.
        if not allow_fetch:
            return ContractResult(
                status=ContractStatus.STALE,
                ok=True,
                path=cache_path,
                message=f"Cached contract is stale (not {PINNED_RELEASE_TAG}); fetch disabled.",
                warning=stale_warning,
            )

    # 3. Fetch the pinned release into the cache.
    if allow_fetch:
        content = _fetch_contract()
        if content is not None:
            _write_cache(cache_path, stamp_path, content)
            return ContractResult(
                status=ContractStatus.FETCHED,
                ok=True,
                path=cache_path,
                message=f"Fetched universal contract ({PINNED_RELEASE_TAG}) into cache ({cache_path}).",
                warning=stale_warning,
            )

    # 4. Halt — fail-closed. The contract is genuinely unobtainable.
    return ContractResult(
        status=ContractStatus.ABSENT,
        ok=False,
        path=None,
        message=(
            "Universal behavioral contract is NOT available and could not be "
            f"obtained. Expected at {home_path} (or the git-ignored cache). "
            "Do NOT proceed. Provide the contract per the project README "
            "(agentic-coding-patterns sbx mixin kit), then retry."
        ),
    )
