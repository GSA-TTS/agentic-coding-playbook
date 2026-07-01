"""Tests for the ensure-contract deterministic availability check."""

from pathlib import Path
from unittest import mock

import pytest
from playbook_validator import ensure_contract as ec
from playbook_validator.ensure_contract import (
    PINNED_RELEASE_TAG,
    ContractStatus,
    ensure_contract,
)

CONTRACT_TEXT = "# AGENTS.md — Federal AI Agent Behavioral Best Practices\n\nrules...\n"


@pytest.fixture
def repo(tmp_path) -> Path:
    """A bare working-project root (no cache, no home)."""
    return tmp_path / "project"


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Point the home path at an empty temp dir so tests never see a real
    ~/.agentic-coding-playbook, and clear any override env var."""
    monkeypatch.delenv(ec.HOME_OVERRIDE_ENV, raising=False)
    empty_home = tmp_path / "fake-home"
    empty_home.mkdir()
    monkeypatch.setattr(ec, "DEFAULT_HOME", empty_home)
    return empty_home


# ── 1. Home path short-circuits everything ──────────────────────────────────


def test_home_present_short_circuits(repo, tmp_path, monkeypatch):
    home = tmp_path / "home" / ".agentic-coding-playbook"
    home.mkdir(parents=True)
    (home / "AGENTS.md").write_text(CONTRACT_TEXT)
    monkeypatch.setattr(ec, "DEFAULT_HOME", home)

    # Fetch must NOT be attempted when home is present.
    with mock.patch.object(ec, "_fetch_contract", side_effect=AssertionError("should not fetch")):
        result = ensure_contract(repo)

    assert result.ok
    assert result.status is ContractStatus.HOME
    assert not (repo / ec.CACHE_RELPATH).exists()


def test_home_override_env_respected(repo, tmp_path, monkeypatch):
    override = tmp_path / "custom-home"
    override.mkdir()
    (override / "AGENTS.md").write_text(CONTRACT_TEXT)
    monkeypatch.setenv(ec.HOME_OVERRIDE_ENV, str(override))

    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok
    assert result.status is ContractStatus.HOME
    assert result.path == override / "AGENTS.md"


def test_empty_home_file_is_not_present(repo, tmp_path, monkeypatch):
    home = tmp_path / "home" / ".agentic-coding-playbook"
    home.mkdir(parents=True)
    (home / "AGENTS.md").write_text("")  # empty
    monkeypatch.setattr(ec, "DEFAULT_HOME", home)

    result = ensure_contract(repo, allow_fetch=False)
    # Empty home file does not count as present; no cache either → halt.
    assert not result.ok
    assert result.status is ContractStatus.ABSENT


# ── 2. Fresh cache ──────────────────────────────────────────────────────────


def _seed_cache(repo: Path, tag: str) -> None:
    cache = repo / ec.CACHE_RELPATH
    stamp = repo / ec.STAMP_RELPATH
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(CONTRACT_TEXT)
    stamp.write_text(f"source_url=x\nrelease_tag={tag}\nfetched_at=now\n")


def test_fresh_cache_used_without_fetch(repo):
    _seed_cache(repo, PINNED_RELEASE_TAG)
    with mock.patch.object(ec, "_fetch_contract", side_effect=AssertionError("should not fetch")):
        result = ensure_contract(repo)
    assert result.ok
    assert result.status is ContractStatus.CACHE_FRESH
    assert result.warning is not None  # announces itself as a fallback


# ── 3. Stale cache triggers refetch ─────────────────────────────────────────


def test_stale_cache_refetches(repo):
    _seed_cache(repo, "v0.0.1-old")
    with mock.patch.object(ec, "_fetch_contract", return_value=CONTRACT_TEXT) as m:
        result = ensure_contract(repo)
    m.assert_called_once()
    assert result.ok
    assert result.status is ContractStatus.FETCHED
    assert ec._read_stamp_tag(repo / ec.STAMP_RELPATH) == PINNED_RELEASE_TAG


def test_stale_cache_no_fetch_reports_stale_but_ok(repo):
    _seed_cache(repo, "v0.0.1-old")
    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok
    assert result.status is ContractStatus.STALE


# ── 4. Fetch path ───────────────────────────────────────────────────────────


def test_fetch_populates_cache_and_stamp(repo):
    with mock.patch.object(ec, "_fetch_contract", return_value=CONTRACT_TEXT):
        result = ensure_contract(repo)
    assert result.ok
    assert result.status is ContractStatus.FETCHED
    assert (repo / ec.CACHE_RELPATH).read_text() == CONTRACT_TEXT
    stamp = (repo / ec.STAMP_RELPATH).read_text()
    assert f"release_tag={PINNED_RELEASE_TAG}" in stamp
    assert ec.CONTRACT_RAW_URL in stamp


# ── 5. Halt (fail-closed) ────────────────────────────────────────────────────


def test_absent_and_offline_halts(repo):
    # No home, no cache, fetch disabled → fail-closed halt.
    result = ensure_contract(repo, allow_fetch=False)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT
    assert result.exit_code == 1


def test_fetch_failure_halts(repo):
    with mock.patch.object(ec, "_fetch_contract", return_value=None):
        result = ensure_contract(repo)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT
    assert result.exit_code == 1


# ── 6. §11 safety — the fetch URL is a hard-coded canonical constant ─────────


def test_fetch_url_is_pinned_canonical_constant():
    assert ec.CONTRACT_RAW_URL.startswith("https://raw.githubusercontent.com/GSA-TTS/agentic-coding-playbook/")
    assert PINNED_RELEASE_TAG in ec.CONTRACT_RAW_URL


def test_no_proceed_without_option_exists():
    """There must be no code path where ok=True while the contract is absent."""
    repo = Path("/nonexistent-project-root-xyz")
    result = ensure_contract(repo, allow_fetch=False)
    # Absent contract must never be reported as ok.
    assert not (result.status is ContractStatus.ABSENT and result.ok)


# ── 7. Self-hosting — the playbook's own AGENTS.md satisfies the check ───────


def test_playbook_own_contract_satisfies(repo):
    """Inside the playbook repo, the repo's own AGENTS.md IS the contract."""
    repo.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("---\ntitle: x\n---\n# AGENTS.md — Federal AI Agent Behavioral Best Practices\n")
    with mock.patch.object(ec, "_fetch_contract", side_effect=AssertionError("should not fetch")):
        result = ensure_contract(repo, allow_fetch=False)
    assert result.ok
    assert result.status is ContractStatus.HOME
    assert result.path == repo / "AGENTS.md"


def test_unrelated_agents_md_does_not_satisfy(repo):
    """A downstream project's own thin AGENTS.md must NOT be mistaken for the
    universal contract (it lacks the distinctive title)."""
    repo.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("# AGENTS.md — My Project\n\nProject-specific rules.\n")
    result = ensure_contract(repo, allow_fetch=False)
    # No home, no cache, and the local AGENTS.md is not the contract → halt.
    assert not result.ok
    assert result.status is ContractStatus.ABSENT
