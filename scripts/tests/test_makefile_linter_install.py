"""Verify `make` runs the locked Markdown linter install once, before its consumers."""

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKE = shutil.which("make")

pytestmark = pytest.mark.skipif(MAKE is None, reason="requires make")


def write_stub(path: Path, body: str) -> None:
    """Create an executable shell fixture using only controlled test input."""
    path.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def make_repo(tmp_path):
    """Copy the real Makefile next to stub linters, with recording tool stubs."""
    root = tmp_path / "repo"
    linters = root / ".github/linters"
    (linters / "tests").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "Makefile", root / "Makefile")
    (linters / "package.json").write_text("{}\n", encoding="utf-8")
    (linters / "package-lock.json").write_text("{}\n", encoding="utf-8")
    (linters / "tests/a.test.mjs").write_text("", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    # npm ci mimics the real one: it deletes node_modules, takes time, then repopulates.
    write_stub(
        bin_dir / "npm",
        f"""echo "start npm $*" >> '{log}'
rm -rf '{linters}/node_modules'
sleep 0.5
mkdir -p '{linters}/node_modules'
touch '{linters}/node_modules/.package-lock.json'
echo "end npm $*" >> '{log}'""",
    )
    write_stub(bin_dir / "ruff", f"echo \"ruff $*\" >> '{log}'")
    write_stub(
        bin_dir / "node",
        f"""[ -f '{linters}/node_modules/.package-lock.json' ] || {{ echo 'node ran without install' >&2; exit 1; }}
echo "node $*" >> '{log}'""",
    )
    return root, bin_dir, log


def run_make(make_repo, *args):
    root, bin_dir, log = make_repo
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    result = subprocess.run([MAKE, *args], cwd=root, env=env, capture_output=True, text=True, timeout=30, check=False)
    calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, calls


def test_dry_run_ci_graph_has_single_install(make_repo):
    """From a fresh checkout, `make -n -j4 ci` schedules exactly one linter install."""
    result, _ = run_make(make_repo, "-n", "-j4", "ci")

    installs = [line for line in result.stdout.splitlines() if "npm ci" in line]
    assert len(installs) == 1, result.stdout + result.stderr


@pytest.mark.parametrize("jobs", ["-j1", "-j4"])
def test_lint_and_test_linters_share_one_install(make_repo, jobs):
    result, calls = run_make(make_repo, jobs, "lint", "test-linters")

    assert result.returncode == 0, result.stdout + result.stderr
    starts = [i for i, c in enumerate(calls) if c.startswith("start npm ci")]
    ends = [i for i, c in enumerate(calls) if c.startswith("end npm ci")]
    assert len(starts) == 1 and len(ends) == 1, calls
    assert all(i > ends[0] for i, c in enumerate(calls) if c.startswith("node ")), calls
    assert any(c.startswith("node --test") for c in calls)
    assert any(c.endswith("run-markdownlint.mjs") for c in calls)


def test_up_to_date_install_is_not_repeated(make_repo):
    root, _, _ = make_repo
    marker = root / ".github/linters/node_modules/.package-lock.json"
    marker.parent.mkdir()
    marker.touch()
    future = time.time() + 60
    os.utime(marker, (future, future))

    result, calls = run_make(make_repo, "lint", "test-linters")

    assert result.returncode == 0, result.stdout + result.stderr
    assert not any("npm ci" in c for c in calls), calls


def test_changed_lockfile_triggers_reinstall(make_repo):
    root, _, _ = make_repo
    marker = root / ".github/linters/node_modules/.package-lock.json"
    marker.parent.mkdir()
    marker.touch()
    past = time.time() - 60
    os.utime(marker, (past, past))

    result, calls = run_make(make_repo, "test-linters")

    assert result.returncode == 0, result.stdout + result.stderr
    assert sum(c.startswith("start npm ci") for c in calls) == 1, calls


def test_install_failure_stops_consumers(make_repo):
    root, bin_dir, log = make_repo
    write_stub(bin_dir / "npm", "echo 'fixture npm failure' >&2\nexit 7")

    result, calls = run_make(make_repo, "-j4", "lint", "test-linters")

    assert result.returncode != 0
    assert not any(c.startswith("node ") for c in calls), calls
