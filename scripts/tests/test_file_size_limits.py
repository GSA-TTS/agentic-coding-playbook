"""Enforce config.FILE_MAX_LINES on production source (#261).

ruff has no file-length rule, so the playbook's mandated file-size ceiling
(config.FILE_MAX_LINES, mirroring AGENTS.md §15.2 / CODING_PRACTICES §13.3) was
one of the five config constants that no code referenced. This test wires it in:
every production `.py` under scripts/ must be <= FILE_MAX_LINES, except a frozen
waiver set of pre-existing offenders that are tracked for burn-down.

Test files are exempt (fixtures + table-driven cases legitimately run long); the
limit targets shipped production modules.
"""

from __future__ import annotations

from pathlib import Path

from playbook_validator.config import FILE_MAX_LINES

REPO = Path(__file__).resolve().parents[2]

# Pre-existing offenders, frozen and tracked for refactor (follow-up issue).
# A file may be REMOVED from this set (once it drops under the ceiling) but a
# NEW file must never be ADDED — see test_no_new_oversized_files.
_WAIVED = {
    "scripts/playbook_validator/index_updaters.py",  # 917 — the headline refactor target
    "scripts/playbook_validator/validate_docs.py",
    "scripts/playbook_validator/generate_index.py",
    "scripts/landscape_monitor.py",
    "scripts/playbook_validator/__main__.py",
}


def _production_py_files() -> list[Path]:
    files: list[Path] = []
    for p in (REPO / "scripts").rglob("*.py"):
        rel = p.relative_to(REPO).as_posix()
        if "/tests/" in rel or Path(rel).name.startswith("test_"):
            continue
        files.append(p)
    return files


def test_production_files_within_limit_or_waived():
    """Every production .py is <= FILE_MAX_LINES, or explicitly waived (#261)."""
    violations = []
    for p in _production_py_files():
        rel = p.relative_to(REPO).as_posix()
        n = len(p.read_text(encoding="utf-8").splitlines())
        if n > FILE_MAX_LINES and rel not in _WAIVED:
            violations.append(f"{rel} ({n} > {FILE_MAX_LINES})")
    assert not violations, (
        "Production files exceed config.FILE_MAX_LINES and are not waived (#261): "
        + ", ".join(violations)
        + ". Split the module, or (only for a tracked pre-existing case) add it to _WAIVED."
    )


def test_waiver_list_has_no_stale_entries():
    """A waived file that dropped under the ceiling (or was deleted) must be
    removed from _WAIVED, so the waiver set shrinks toward zero and never hides a
    file that no longer needs waiving."""
    stale = []
    for rel in sorted(_WAIVED):
        p = REPO / rel
        if not p.is_file():
            stale.append(f"{rel} (missing)")
            continue
        n = len(p.read_text(encoding="utf-8").splitlines())
        if n <= FILE_MAX_LINES:
            stale.append(f"{rel} (now {n} <= {FILE_MAX_LINES})")
    assert not stale, "Remove these stale _WAIVED entries (#261): " + ", ".join(stale)
