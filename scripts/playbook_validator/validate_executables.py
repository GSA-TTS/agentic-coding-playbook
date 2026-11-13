"""Validate executable modes that a fresh Git checkout must preserve.

The inventory is deliberately explicit. It contains repository tool entry
points, rather than treating every shebang or code example as an executable.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path
from shutil import which

EXECUTABLE_PATHS = (
    ".github/linters/run-markdownlint.mjs",
    "scripts/check_federal_landscape_rss.py",
    "scripts/ci-local.sh",
    "scripts/compare_landscape_versions.py",
)


def _expected_paths(paths: Iterable[str] = EXECUTABLE_PATHS) -> tuple[str, ...]:
    """Return a non-empty, duplicate-free executable inventory."""
    expected = tuple(paths)
    if not expected:
        raise ValueError("executable inventory is empty")
    if len(expected) != len(set(expected)):
        raise ValueError("executable inventory contains duplicate paths")
    return expected


def _git_index_modes(root: Path) -> dict[str, list[tuple[str, str]]]:
    """Read staged modes without relying on filesystem mode bits."""
    git = which("git")
    if git is None:
        raise ValueError("git is required to verify recorded executable modes")
    try:
        result = subprocess.run(  # noqa: S603 -- fixed Git executable and constant arguments
            [git, "-C", str(root), "ls-files", "--stage", "-z"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise ValueError(f"could not read Git index: {detail}") from error

    records: dict[str, list[tuple[str, str]]] = {}
    for record in result.stdout.split("\0"):
        if not record:
            continue
        try:
            metadata, path = record.split("\t", 1)
            mode, _object_id, stage = metadata.split()
        except ValueError as error:
            raise ValueError(f"could not parse Git index record: {record!r}") from error
        records.setdefault(path, []).append((mode, stage))
    return records


def validate_git_executable_modes(root: Path, paths: Iterable[str] = EXECUTABLE_PATHS) -> list[str]:
    """Return Git-index errors for intended executable paths only.

    This check intentionally does not inspect local permissions. A shared mount
    can present different mode bits than Git records; callers that need local
    executability should also call ``validate_working_tree_modes``.
    """
    expected = _expected_paths(paths)
    records = _git_index_modes(root)
    errors = []
    for path in expected:
        entries = records.get(path)
        if entries is None:
            errors.append(f"{path}: not tracked in the Git index")
        elif entries != [("100755", "0")]:
            errors.append(f"{path}: Git index must record mode 100755 at stage 0; found {entries}")
    return errors


def validate_working_tree_modes(root: Path, paths: Iterable[str] = EXECUTABLE_PATHS) -> list[str]:
    """Return local filesystem errors independently from Git-index results."""
    errors = []
    for relative_path in _expected_paths(paths):
        path = root / relative_path
        if not path.is_file():
            errors.append(f"{relative_path}: missing from the working tree")
        elif not path.stat().st_mode & 0o111:
            errors.append(f"{relative_path}: not executable in the working tree")
    return errors


def validate_executable_modes(root: Path) -> tuple[list[str], list[str]]:
    """Return fatal Git-index errors and local working-tree warnings separately."""
    return validate_git_executable_modes(root), validate_working_tree_modes(root)
