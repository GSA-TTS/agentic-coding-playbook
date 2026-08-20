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

# Frontmatter carrying the structured, versioned contract block. The thin layer
# legitimately *names* the contract title in prose but declares project-layer.
UNIVERSAL_FM = (
    '---\ntitle: x\ncontract:\n  role: universal\n  version: "1.0.0"\n---\n'
    "# AGENTS.md — Federal AI Agent Behavioral Best Practices\n"
)

# The contract file a valid environment provides IS the universal contract, so it
# must carry the contract.role: universal marker. (Previously this was a bare
# title string; the gate now validates the marker, not mere existence — #235.)
CONTRACT_TEXT = UNIVERSAL_FM

# A file that exists and is non-empty but is NOT the universal contract (no
# contract.role: universal). The gate must fail closed on this, not accept it on
# mere existence — this is the #235 fail-closed defect.
NON_UNIVERSAL_FM = (
    '---\ntitle: x\ncontract:\n  role: project-layer\n  version: "1.0.0"\n---\n# Some project\'s thin AGENTS.md\n'
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


# ── #235 fail-closed: a present-but-not-universal contract must NOT pass ──────


def test_home_present_but_not_universal_fails_closed(repo, tmp_path, monkeypatch):
    """The blocker (#235): a non-empty AGENTS.md at the home path that does NOT
    declare contract.role: universal must fail closed. Existence is not enough —
    otherwise the gate passes green on a contract that cannot satisfy a
    downstream requires_contract."""
    home = tmp_path / "home" / ".agentic-coding-playbook"
    home.mkdir(parents=True)
    (home / "AGENTS.md").write_text(NON_UNIVERSAL_FM)
    monkeypatch.setattr(ec, "DEFAULT_HOME", home)

    result = ensure_contract(repo, allow_fetch=False)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT


def test_stale_cache_not_universal_no_fetch_fails_closed(repo):
    """A cached file whose content is not the universal contract must fail closed
    under --no-fetch, rather than be reported stale-but-ok on tag mismatch."""
    cache = repo / ec.CACHE_RELPATH
    stamp = repo / ec.STAMP_RELPATH
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(NON_UNIVERSAL_FM)
    stamp.write_text("source_url=x\nrelease_tag=v0.0.1-old\nfetched_at=now\n")

    result = ensure_contract(repo, allow_fetch=False)
    assert not result.ok
    assert result.status is ContractStatus.ABSENT


def test_cli_no_fetch_fails_closed_on_non_universal_home(repo, tmp_path, monkeypatch):
    """End-to-end via the module CLI path: --no-fetch with a non-universal home
    file exits non-zero (mirrors the shipped CI workflow's fail-closed step)."""
    home = tmp_path / "home" / ".agentic-coding-playbook"
    home.mkdir(parents=True)
    (home / "AGENTS.md").write_text(NON_UNIVERSAL_FM)
    monkeypatch.setattr(ec, "DEFAULT_HOME", home)

    result = ensure_contract(repo, allow_fetch=False)
    assert result.exit_code == 1


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


# ── 9. Copied probe recognizes inline flow-mapping frontmatter (#154) ─────────

import importlib.util  # noqa: E402


def _load_copied_probe():
    """Import templates/ensure-contract.py as a module to unit-test its parser
    directly (the subprocess tests above cover end-to-end exit codes)."""
    spec = importlib.util.spec_from_file_location(
        "copied_ensure_contract", PLAYBOOK_ROOT / "templates" / "ensure-contract.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _module_declares_universal(text: str) -> bool:
    """Module probe's recognition (real YAML) for the same input."""
    from playbook_validator.config import CONTRACT_ROLE_UNIVERSAL, contract_role
    from playbook_validator.frontmatter import parse_frontmatter

    return contract_role(parse_frontmatter(text)) == CONTRACT_ROLE_UNIVERSAL


# Inputs exercising both YAML forms + the guard cases. The bug this fixes: the
# copied probe used to return False on inline flow-mapping universal (#154).
_PARITY_CASES = {
    "block_universal": '---\ncontract:\n  role: universal\n  version: "1.0.0"\n---\n# x\n',
    "flow_universal": "---\ncontract: {role: universal}\n---\n# x\n",
    "flow_universal_with_version": '---\ncontract: {role: universal, version: "1.0.0"}\n---\n# x\n',
    "flow_universal_double_quoted": '---\ncontract: {role: "universal"}\n---\n# x\n',
    "flow_universal_single_quoted": "---\ncontract: {role: 'universal'}\n---\n# x\n",
    "flow_universal_reversed": "---\ncontract: {version: 1.0.0, role: universal}\n---\n# x\n",
    "flow_project_layer": "---\ncontract: {role: project-layer}\n---\n# x\n",
    "block_project_layer": "---\ncontract:\n  role: project-layer\n---\n# x\n",
    "no_contract_block": "---\ntitle: x\n---\n# x\n",
    # Malformed / decoy forms that must fail closed in BOTH probes.
    "empty_flow": "---\ncontract: {}\n---\n# x\n",
    "flow_missing_space": "---\ncontract:{role: universal}\n---\n# x\n",
    "flow_empty_role": "---\ncontract: {role: }\n---\n# x\n",
    "decoy_field": "---\ncontractor: {role: universal}\n---\n# x\n",
}


@pytest.mark.parametrize("name", list(_PARITY_CASES))
def test_copied_and_module_probes_agree(name):
    """#154: the dependency-free copied probe and the YAML module probe MUST
    return the same verdict for every frontmatter form — especially inline flow
    mappings, where they used to diverge."""
    copied = _load_copied_probe()
    text = _PARITY_CASES[name]
    assert copied._text_declares_universal(text) == _module_declares_universal(text), f"probe divergence on {name!r}"


def test_copied_probe_accepts_flow_mapping_universal():
    """Direct regression for #154: flow-mapping universal is now recognized."""
    copied = _load_copied_probe()
    assert copied._text_declares_universal("---\ncontract: {role: universal}\n---\n# x\n") is True


def test_copied_probe_rejects_flow_mapping_project_layer():
    """A flow-mapping project layer must NOT self-satisfy (fail-closed, #151)."""
    copied = _load_copied_probe()
    assert copied._text_declares_universal("---\ncontract: {role: project-layer}\n---\n# x\n") is False


def test_copied_probe_flow_mapping_end_to_end(repo, tmp_path):
    """End-to-end: a repo whose AGENTS.md uses inline flow-mapping universal is
    accepted by the subprocess-invoked copied probe (exit 0)."""
    repo.mkdir(parents=True)
    (repo / "AGENTS.md").write_text(
        '---\ntitle: x\ncontract: {role: universal, version: "1.0.0"}\n---\n'
        "# AGENTS.md — Federal AI Agent Behavioral Best Practices\n"
    )
    empty_home = tmp_path / "flow-empty-home"
    empty_home.mkdir()
    assert _run_copied_probe(repo, empty_home) == 0
