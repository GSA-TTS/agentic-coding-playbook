"""JSON result collection and human-readable text formatting.

Replaces the hand-rolled JSON assembly in lib/common.sh with proper
json.dumps() for safe escaping of all special characters.
"""

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class CheckResult:
    """A single check result."""

    file: str
    check: str
    passed: bool
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"file": self.file, "check": self.check, "pass": self.passed}
        if self.note is not None:
            d["note"] = self.note
        return d


class ResultCollector:
    """Collect check results and produce JSON or text output.

    Replaces json_init/json_add_result/json_output from common.sh.
    Uses json.dumps() for proper escaping — no hand-rolled string interpolation.
    """

    def __init__(self) -> None:
        self._results: list[CheckResult] = []
        self._warnings: list[str] = []
        self._errors: list[str] = []

    def add_result(self, file: str, check: str, *, passed: bool, note: str | None = None) -> None:
        """Add a check result (pass or fail)."""
        self._results.append(CheckResult(file=file, check=check, passed=passed, note=note))

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self._warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self._errors.append(message)

    @property
    def checks_passed(self) -> int:
        return sum(1 for r in self._results if r.passed)

    @property
    def checks_failed(self) -> int:
        return sum(1 for r in self._results if not r.passed)

    @property
    def status(self) -> str:
        if self.checks_failed == 0:
            return "success"
        elif self.checks_passed > 0:
            return "partial"
        else:
            return "failure"

    @property
    def exit_code(self) -> int:
        return 1 if self.checks_failed > 0 else 0

    def to_dict(self, **extra: Any) -> dict[str, Any]:
        """Return results as a dictionary."""
        d: dict[str, Any] = {
            "status": self.status,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
        }
        d.update(extra)
        d["results"] = [r.to_dict() for r in self._results]
        d["warnings"] = list(self._warnings)
        d["errors"] = list(self._errors)
        return d

    def to_json(self, **extra: Any) -> str:
        """Return results as a JSON string with proper escaping."""
        return json.dumps(self.to_dict(**extra), ensure_ascii=False)

    def format_text(self) -> str:
        """Return results as human-readable text."""
        lines: list[str] = []
        for r in self._results:
            tag = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {tag} {r.check}")
            if not r.passed and r.note:
                lines.append(f"         {r.note}")

        for w in self._warnings:
            lines.append(f"  [WARN] {w}")

        for e in self._errors:
            lines.append(f"  [ERROR] {e}")

        lines.append("")
        lines.append(f"  Passed: {self.checks_passed}  |  Failed: {self.checks_failed}")
        return "\n".join(lines)
