"""Tests for the ensure-contract deterministic availability check."""

import subprocess
import sys
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

# Frontmatter carrying the structured, versioned contract block. The thin layer
# legitimately *names* the contract title in prose but declares project-layer.
UNIVERSAL_FM = (
    '---\ntitle: x\ncontract:\n  role: universal\n  version: "1.0.0"\n---\n'
    "# AGENTS.md — Federal AI Agent Behavioral Best Practices\n"
)

# Repository root = two levels up from scripts/tests/
PLAYBOOK_ROOT = Path(__file__).resolve().parents[2]


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


# ── 6a. Fetch self-declaration — fetched bytes must declare the contract ─────


def _mock_urlopen(body: bytes):
    """Build an object usable as a mock urlopen() return (context manager)."""
    resp = mock.MagicMock()
    resp.status = 200
    resp.read.return_value = body
    cm = mock.MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = False
    return cm


def test_fetch_rejects_body_not_declaring_universal(repo):
    """A fetched body that does not self-declare contract.role: universal (wrong
    file, HTML error page, garbage) is treated as unobtainable → fail-closed
    halt (no cache written)."""
    body = b"<html><body>404 Not Found</body></html>\n"
    with mock.patch.object(ec.urllib.request, "urlopen", return_value=_mock_urlopen(body)):
        result = ensure_contract(repo)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT
    assert not (repo / ec.CACHE_RELPATH).exists()


def test_fetch_accepts_body_declaring_universal(repo):
    """A fetched body whose frontmatter declares contract.role: universal is
    accepted and cached."""
    body = UNIVERSAL_FM.encode()
    with mock.patch.object(ec.urllib.request, "urlopen", return_value=_mock_urlopen(body)):
        result = ensure_contract(repo)
    assert result.ok
    assert result.status is ContractStatus.FETCHED
    assert (repo / ec.CACHE_RELPATH).read_text() == body.decode()


def test_real_contract_bytes_declare_universal():
    """The committed universal AGENTS.md self-declares contract.role: universal,
    so the fetch-path acceptance check passes for the real released bytes."""
    text = (PLAYBOOK_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert ec._text_declares_universal(text)


def test_no_proceed_without_option_exists():
    """There must be no code path where ok=True while the contract is absent."""
    repo = Path("/nonexistent-project-root-xyz")
    result = ensure_contract(repo, allow_fetch=False)
    # Absent contract must never be reported as ok.
    assert not (result.status is ContractStatus.ABSENT and result.ok)


# ── 7. Self-hosting — the playbook's own AGENTS.md satisfies the check ───────


def test_playbook_own_contract_satisfies(repo):
    """Inside the playbook repo, the repo's own AGENTS.md IS the contract —
    recognized by its structured contract.role: universal block."""
    repo.mkdir(parents=True)
    (repo / "AGENTS.md").write_text(UNIVERSAL_FM)
    with mock.patch.object(ec, "_fetch_contract", side_effect=AssertionError("should not fetch")):
        result = ensure_contract(repo, allow_fetch=False)
    assert result.ok
    assert result.status is ContractStatus.HOME
    assert result.path == repo / "AGENTS.md"


def test_unrelated_agents_md_does_not_satisfy(repo):
    """A downstream project's own thin AGENTS.md must NOT be mistaken for the
    universal contract (it lacks the canonical marker)."""
    repo.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("# AGENTS.md — My Project\n\nProject-specific rules.\n")
    result = ensure_contract(repo, allow_fetch=False)
    # No home, no cache, and the local AGENTS.md is not the contract → halt.
    assert not result.ok
    assert result.status is ContractStatus.ABSENT


def test_title_substring_alone_does_not_satisfy(repo):
    """Regression for #151: an AGENTS.md that merely *names* the contract title
    (as the thin layer does) but declares contract.role: project-layer must NOT
    self-satisfy the probe."""
    repo.mkdir(parents=True)
    # Title present in body AND in a frontmatter description — but the contract
    # role is project-layer. This mirrors the thin template's shape.
    (repo / "AGENTS.md").write_text(
        "---\n"
        'description: "layers on the Federal AI Agent Behavioral Best Practices"\n'
        "contract:\n"
        "  role: project-layer\n"
        '  requires_contract: ">=1.0"\n'
        "---\n"
        "# AGENTS.md — My Project\n\n"
        "This project layers on the **Federal AI Agent Behavioral Best Practices**.\n"
    )
    result = ensure_contract(repo, allow_fetch=False)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT


@pytest.mark.parametrize(
    "thin_rel",
    ["templates/AGENTS.md.template", "examples/AGENTS.md.example"],
)
def test_real_thin_layer_does_not_self_satisfy(repo, thin_rel):
    """Feed the ACTUAL committed thin template / example through the probe as a
    project's own AGENTS.md and assert it does NOT self-satisfy when the real
    contract is absent (issue #151 acceptance criterion — real output, not a
    hand-written stub)."""
    repo.mkdir(parents=True)
    thin_text = (PLAYBOOK_ROOT / thin_rel).read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(thin_text)
    with mock.patch.object(ec, "_fetch_contract", side_effect=AssertionError("should not fetch")):
        result = ensure_contract(repo, allow_fetch=False)
    assert not result.ok, f"{thin_rel} self-satisfied the contract probe (#151 regression)"
    assert result.status is ContractStatus.ABSENT


def test_real_universal_contract_self_satisfies(repo, monkeypatch):
    """The actual committed universal AGENTS.md, placed as a repo's own
    AGENTS.md, IS recognized as the contract via its canonical marker."""
    repo.mkdir(parents=True)
    universal_text = (PLAYBOOK_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(universal_text)
    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok
    assert result.status is ContractStatus.HOME


# ── 8. Module and copied-template probes behave consistently (#151) ──────────


def _run_copied_probe(repo_root: Path, home: Path) -> int:
    """Run the self-contained templates/ensure-contract.py against repo_root,
    with an isolated (empty) home so only the self-host branch can match."""
    env = {
        "HOME": str(home),
        "PATH": __import__("os").environ.get("PATH", ""),
        ec.HOME_OVERRIDE_ENV: str(home / ".agentic-coding-playbook"),
    }
    proc = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(PLAYBOOK_ROOT / "templates" / "ensure-contract.py"),
            "--root",
            str(repo_root),
            "--no-fetch",
        ],
        capture_output=True,
        env=env,
        text=True,
    )
    return proc.returncode


def test_copied_probe_rejects_thin_layer(repo, tmp_path):
    """The copied self-contained probe must also reject a thin project layer —
    consistent with the module probe (#151 acceptance criterion)."""
    repo.mkdir(parents=True)
    thin_text = (PLAYBOOK_ROOT / "templates/AGENTS.md.template").read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(thin_text)
    empty_home = tmp_path / "copied-empty-home"
    empty_home.mkdir()
    assert _run_copied_probe(repo, empty_home) != 0


def test_copied_probe_accepts_universal_contract(repo, tmp_path):
    """The copied probe recognizes the real universal contract by its marker —
    consistent with the module probe (#151 acceptance criterion)."""
    repo.mkdir(parents=True)
    universal_text = (PLAYBOOK_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(universal_text)
    empty_home = tmp_path / "copied-empty-home2"
    empty_home.mkdir()
    assert _run_copied_probe(repo, empty_home) == 0


# ── 10. requires_contract version-range compatibility (#153) ──────────────────

import importlib.util  # noqa: E402


def _load_copied_probe():
    """Import templates/ensure-contract.py as a module to unit-test its
    dependency-free helpers directly."""
    spec = importlib.util.spec_from_file_location(
        "copied_ensure_contract_153", PLAYBOOK_ROOT / "templates" / "ensure-contract.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_project_layer(repo: Path, requires: str | None) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    fm = "---\ntitle: p\ndescription: d\nstatus: canonical\ntier: 3\ncontract:\n  role: project-layer\n"
    if requires is not None:
        fm += f'  requires_contract: "{requires}"\n'
    fm += "---\n# Project layer\n"
    (repo / "AGENTS.md").write_text(fm)


def _write_home_contract(home_dir: Path, version: str) -> Path:
    home = home_dir / ".agentic-coding-playbook"
    home.mkdir(parents=True, exist_ok=True)
    (home / "AGENTS.md").write_text(
        f'---\ntitle: u\ncontract:\n  role: universal\n  version: "{version}"\n---\n'
        "# AGENTS.md — Federal AI Agent Behavioral Best Practices\n"
    )
    return home


def test_requires_satisfied_no_warning(repo, tmp_path, monkeypatch):
    """Project requires >=1.0, home contract is 1.0.0 → ok, no compat warning."""
    _write_project_layer(repo, ">=1.0")
    home = _write_home_contract(tmp_path / "h1", "1.0.0")
    monkeypatch.setenv(ec.HOME_OVERRIDE_ENV, str(home))
    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok is True
    assert result.status == ContractStatus.HOME
    assert result.warning is None


def test_requires_unsatisfied_warns_but_ok(repo, tmp_path, monkeypatch):
    """Project requires >=1.0, home contract is 0.4.0 → ok (present) BUT a
    compat warning fires (the #153 signal; #191 was exactly this drift)."""
    _write_project_layer(repo, ">=1.0")
    home = _write_home_contract(tmp_path / "h2", "0.4.0")
    monkeypatch.setenv(ec.HOME_OVERRIDE_ENV, str(home))
    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok is True
    assert result.warning and "requires" in result.warning and "0.4.0" in result.warning


def test_no_requires_no_warning(repo, tmp_path, monkeypatch):
    """A project with no requires_contract never gets a compat warning."""
    _write_project_layer(repo, None)
    home = _write_home_contract(tmp_path / "h3", "0.4.0")
    monkeypatch.setenv(ec.HOME_OVERRIDE_ENV, str(home))
    result = ensure_contract(repo, allow_fetch=False)
    assert result.ok is True
    assert result.warning is None


def test_caret_range_unsatisfied_warns(repo, tmp_path, monkeypatch):
    """Caret range enforced: requires ^1.0, contract 2.0.0 → warning."""
    _write_project_layer(repo, "^1.0")
    home = _write_home_contract(tmp_path / "h4", "2.0.0")
    monkeypatch.setenv(ec.HOME_OVERRIDE_ENV, str(home))
    result = ensure_contract(repo, allow_fetch=False)
    assert result.warning and "^1.0" in result.warning


def test_comparator_parity_module_vs_copied():
    """#153/#154: the copied probe's _version_satisfies MUST return the same
    verdict as the module config.version_satisfies for every combination —
    they are duplicated (copied probe is dependency-free) and must not drift."""
    import itertools

    from playbook_validator.config import version_satisfies as module_vs

    copied = _load_copied_probe()
    versions = [None, "", "1.0.0", "0.4.0", "1.0", "1.2.3", "2.0.0", "0.5.0", "bad"]
    ranges = [
        None,
        "",
        ">=1.0",
        ">1.0",
        "<=1.0",
        "<1.0",
        "==1.0.0",
        "=1.0",
        "^1.0",
        "^0.4",
        "1.0.0",
        "garbage",
        ">= 1.0",
    ]
    for v, r in itertools.product(versions, ranges):
        assert copied._version_satisfies(v, r) == module_vs(v, r), f"comparator divergence on ({v!r}, {r!r})"
