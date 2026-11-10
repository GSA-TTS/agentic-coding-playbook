"""Exercise local CI's Markdown step without running package managers or linters."""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def write_stub(path: Path, body: str) -> None:
    """Create an executable shell fixture using only controlled test input."""
    path.write_text("#!/bin/sh\nset -eu\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def ci_repo(tmp_path):
    """Copy the real caller and expose only fixtures and local file utilities."""
    root = tmp_path / "repo with spaces"
    (root / "scripts").mkdir(parents=True)
    (root / ".github/linters").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "scripts/ci-local.sh", root / "scripts/ci-local.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("dirname", "env", "mktemp", "cat", "grep", "rm", "mkdir", "cp"):
        executable = shutil.which(name)
        assert executable is not None, f"Test requires {name}"
        (bin_dir / name).symlink_to(executable)
    write_stub(bin_dir / "ruff", "exit 0")
    write_stub(bin_dir / "uname", "echo Linux")
    write_stub(
        bin_dir / "python3",
        """if [ "$1" = "-c" ]; then exit 1; fi
if [ "$1" = "-m" ] && [ "$2" = "venv" ]; then
    mkdir -p "$3/bin"
    cp "$PATH/ruff" "$3/bin/pip"
    cp "$PATH/ruff" "$3/bin/pip-audit"
fi""",
    )
    write_stub(
        bin_dir / "npm",
        """printf 'npm %s\\n' "$*" >> "$CALL_LOG"
[ "$*" = "ci --prefix .github/linters --ignore-scripts" ]
if [ "$NPM_STATUS" -ne 0 ]; then
    echo 'fixture npm failure' >&2
    exit "$NPM_STATUS"
fi
mkdir -p .github/linters/node_modules""",
    )
    write_stub(
        bin_dir / "node",
        """printf 'node %s\\n' "$*" >> "$CALL_LOG"
[ "$*" = ".github/linters/run-markdownlint.mjs" ]
[ -d .github/linters/node_modules ]
exit "$NODE_STATUS"
""",
    )
    assert shutil.which("pnpm", path=str(bin_dir)) is None
    return root, bin_dir


def run_ci(ci_repo, *, offline=False, npm_status=0, node_status=0):
    """Run the unchanged caller with no ambient tools or shell configuration."""
    root, bin_dir = ci_repo
    log = root / "calls.log"
    bash = shutil.which("bash")
    assert bash is not None, "Test requires Bash"
    result = subprocess.run(
        [bash, str(root / "scripts/ci-local.sh"), *(["--no-net"] if offline else [])],
        cwd=root.parent,
        env={
            "PATH": str(bin_dir),
            "HOME": str(root),
            "TMPDIR": str(root),
            "CALL_LOG": str(log),
            "NPM_STATUS": str(npm_status),
            "NODE_STATUS": str(node_status),
            "SKIP_SEMGREP": "1",
        },
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, calls


def test_offline_fresh_checkout_fails_without_invoking_npm(ci_repo):
    result, calls = run_ci(ci_repo, offline=True)

    assert result.returncode == 1
    assert calls == []
    assert "--no-net" in result.stderr
    assert "npm ci --prefix .github/linters --ignore-scripts" in result.stderr
    assert "FAILED: Markdown lint" in result.stdout
    assert "All executed checks passed." not in result.stdout
    assert not (ci_repo[0] / ".github/linters/node_modules").exists()


@pytest.mark.parametrize("npm_status", [0, 23], ids=["success", "failure"])
def test_normal_run_bootstraps_missing_dependencies(ci_repo, npm_status):
    result, calls = run_ci(ci_repo, npm_status=npm_status)

    assert calls[0] == "npm ci --prefix .github/linters --ignore-scripts"
    if npm_status:
        assert result.returncode == 1
        assert len(calls) == 1
        assert "fixture npm failure" in result.stderr
        assert "FAILED: Markdown lint" in result.stdout
        assert "All executed checks passed." not in result.stdout
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        assert calls == [
            "npm ci --prefix .github/linters --ignore-scripts",
            "node .github/linters/run-markdownlint.mjs",
        ]
        assert "All executed checks passed." in result.stdout


@pytest.mark.parametrize("offline", [False, True], ids=["normal", "offline"])
@pytest.mark.parametrize("node_status", [0, 23], ids=["success", "failure"])
def test_installed_dependencies_run_lint_without_npm(ci_repo, offline, node_status):
    (ci_repo[0] / ".github/linters/node_modules").mkdir()

    result, calls = run_ci(ci_repo, offline=offline, node_status=node_status)

    assert calls == ["node .github/linters/run-markdownlint.mjs"]
    assert result.returncode == (1 if node_status else 0), result.stdout + result.stderr
    if node_status:
        assert "FAILED: Markdown lint" in result.stdout
        assert "All executed checks passed." not in result.stdout
    else:
        assert "All executed checks passed." in result.stdout
