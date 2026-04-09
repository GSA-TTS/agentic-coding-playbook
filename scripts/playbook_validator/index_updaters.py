"""Side-effect operations for INDEX.yaml generation.

Handles injecting generated content into existing files:
- Skills table injection into README.md/AGENTS.md
- Word count updates in CONTEXT-GUIDE.md
- Hardcoded count updates across markdown files

Split from generate_index.py to keep that module under 400 lines.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playbook_validator.generate_index import IndexStats, SkillInfo

# Marker comments in README.md for skills table injection
_START_MARKER = "<!-- GENERATED:SKILLS_TABLE:START"
_END_MARKER = "<!-- GENERATED:SKILLS_TABLE:END -->"


# ── Skills table ──────────────────────────────────────────────────────


def _truncate_description(desc: str, max_len: int = 90) -> str:
    """Truncate description to first sentence, then to max_len at word boundary."""
    short = re.split(r"\. [A-Z]", desc)[0]
    if len(short) > max_len:
        short = short[: max_len - 3]
        last_space = short.rfind(" ")
        if last_space > 0:
            short = short[:last_space]
        short += "..."
    return short


def render_skills_table(skills: list[SkillInfo]) -> str:
    """Generate the markdown skills table rows (including header)."""
    lines: list[str] = []
    lines.append("| Skill | Purpose | Scripts? |")
    lines.append("|-------|---------|----------|")
    for skill in skills:
        short_desc = _truncate_description(skill.description)
        has_scripts = "Yes" if skill.has_scripts else "No"
        lines.append(f"| `{skill.name}` | {short_desc} | {has_scripts} |")
    return "\n".join(lines)


def inject_readme_table(readme_path: Path, table: str) -> bool:
    """Replace skills table between markers in a markdown file.

    Returns True if injection happened, False if markers not found.
    """
    if not readme_path.is_file():
        return False

    content = readme_path.read_text(encoding="utf-8")
    if _START_MARKER not in content:
        return False

    start_line = f"{_START_MARKER} — do not edit, run: make generate -->"
    replacement = f"{start_line}\n{table}\n{_END_MARKER}"

    pattern = re.compile(
        re.escape(_START_MARKER) + r"[^\n]*\n.*?" + re.escape(_END_MARKER),
        re.DOTALL,
    )
    new_content = pattern.sub(replacement, content)

    if new_content != content:
        readme_path.write_text(new_content, encoding="utf-8")
    return True


# ── CONTEXT-GUIDE word counts ─────────────────────────────────────────


def update_context_guide_word_counts(root: Path) -> None:
    """Update word counts in CONTEXT-GUIDE.md from actual file sizes.

    Finds patterns like ``| `path` | NUMBER |`` and replaces NUMBER with wc -w.
    Also updates tier sum headings like `## Tier 1 — Always Load (~N words)`.
    """
    guide_path = root / "CONTEXT-GUIDE.md"
    if not guide_path.is_file():
        return

    content = guide_path.read_text(encoding="utf-8")
    original = content

    def replace_word_count(match: re.Match[str]) -> str:
        path_str = match.group(1)
        rest = match.group(2)
        file_path = root / path_str
        if file_path.is_file():
            words = len(file_path.read_text(encoding="utf-8").split())
            return f"| `{path_str}` | {words:,} |{rest}"
        return match.group(0)

    content = re.sub(
        r"\| `([^`]+\.md)` \| [\d,~]+\.?\d* \|(.+)",
        replace_word_count,
        content,
    )

    tier_sums: dict[str, int] = {}
    current_tier = ""
    for line in content.splitlines():
        tier_match = re.match(r"## (Tier \d)", line)
        if tier_match:
            current_tier = tier_match.group(1)
            tier_sums[current_tier] = 0
        if current_tier:
            wc_match = re.match(r"\| `[^`]+` \| ([\d,]+) \|", line)
            if wc_match:
                tier_sums[current_tier] += int(wc_match.group(1).replace(",", ""))

    for tier_key, total in tier_sums.items():
        content = re.sub(
            rf"(## {re.escape(tier_key)} — [^(]+)\(~[\d,]+ words\)",
            rf"\1(~{total:,} words)",
            content,
        )

    if content != original:
        guide_path.write_text(content, encoding="utf-8")


# ── Hardcoded count updates ───────────────────────────────────────────


def update_hardcoded_counts(root: Path, stats: IndexStats, skills: list[SkillInfo]) -> None:
    """Update hardcoded counts in markdown files to match actual data.

    Replaces patterns like "N tests", "N skills", "N federal AI guidance"
    with computed values from source data. Prevents count drift.
    """
    test_count = _collect_test_count(root)

    landscape_path = root / "data" / "federal-ai-landscape.yaml"
    landscape_count = None
    if landscape_path.is_file():
        content = landscape_path.read_text(encoding="utf-8")
        landscape_count = len(re.findall(r"^\s+- id:", content, re.MULTILINE))

    md_files = list(root.glob("*.md")) + list(root.glob("docs/*.md"))

    for md_file in md_files:
        if md_file.name == "CHANGELOG.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        original = text

        if test_count is not None:
            text = re.sub(r"\d+ tests?\b", f"{test_count} tests", text)

        if landscape_count is not None:
            text = re.sub(
                r"(\d+) federal AI guidance",
                f"{landscape_count} federal AI guidance",
                text,
            )

        if text != original:
            md_file.write_text(text, encoding="utf-8")


def _collect_test_count(root: Path) -> int | None:
    """Count tests by collecting (fast, no execution)."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "scripts/tests/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=30,
            env={**os.environ, "PYTHONPATH": str(root / "scripts")},
        )
        test_match = re.search(r"(\d+) tests? collected", result.stdout)
        return int(test_match.group(1)) if test_match else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
