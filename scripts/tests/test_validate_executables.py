"""Tests for Git-recorded executable-mode validation."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from playbook_validator.validate_executables import (
    validate_git_executable_modes,
    validate_working_tree_modes,
)

PATH = "scripts/tool.py"


def _write_executable_candidate(root: Path, mode: int = 0o644) -> Path:
    path = root / PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env python3\n")
    path.chmod(mode)
    return path


def _stage(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "add", PATH], check=True)


def test_git_index_rejects_644_even_if_working_tree_is_executable(git_repo: Path):
    path = _write_executable_candidate(git_repo)
    _stage(git_repo)
    path.chmod(0o755)

    assert validate_git_executable_modes(git_repo, [PATH]) == [
        f"{PATH}: Git index must record mode 100755 at stage 0; found [('100644', '0')]"
    ]
    assert validate_working_tree_modes(git_repo, [PATH]) == []


def test_git_helper_passes_when_mount_lacks_execute_permission(git_repo: Path):
    path = _write_executable_candidate(git_repo, 0o755)
    _stage(git_repo)
    path.chmod(0o644)

    assert validate_git_executable_modes(git_repo, [PATH]) == []
    assert validate_working_tree_modes(git_repo, [PATH]) == [f"{PATH}: not executable in the working tree"]


def test_git_index_rejects_untracked_inventory_path(git_repo: Path):
    _write_executable_candidate(git_repo, 0o755)

    assert validate_git_executable_modes(git_repo, [PATH]) == [f"{PATH}: not tracked in the Git index"]


def test_git_index_rejects_unmerged_inventory_path(git_repo: Path):
    _write_executable_candidate(git_repo, 0o755)
    object_id = subprocess.run(
        ["git", "-C", str(git_repo), "hash-object", "-w", PATH],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(git_repo), "update-index", "--index-info"],
        input=f"100755 {object_id} 1\t{PATH}\n",
        check=True,
        capture_output=True,
        text=True,
    )

    assert validate_git_executable_modes(git_repo, [PATH]) == [
        f"{PATH}: Git index must record mode 100755 at stage 0; found [('100755', '1')]"
    ]


def test_working_tree_rejects_missing_tracked_path(git_repo: Path):
    path = _write_executable_candidate(git_repo, 0o755)
    _stage(git_repo)
    path.unlink()

    assert validate_working_tree_modes(git_repo, [PATH]) == [f"{PATH}: missing from the working tree"]


def test_git_index_errors_are_reported(git_repo: Path):
    with patch("playbook_validator.validate_executables.subprocess.run") as run:
        run.side_effect = subprocess.CalledProcessError(128, ["git"], stderr="fatal: index unavailable")

        with pytest.raises(ValueError, match="could not read Git index: fatal: index unavailable"):
            validate_git_executable_modes(git_repo, [PATH])


def test_empty_inventory_is_rejected(git_repo: Path):
    with pytest.raises(ValueError, match="executable inventory is empty"):
        validate_git_executable_modes(git_repo, [])
