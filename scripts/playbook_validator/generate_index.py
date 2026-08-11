"""Generate INDEX.yaml from source files.

Scans content .md files and skill directories to produce a deterministic
INDEX.yaml. This prevents drift by deriving ALL metadata from source files.

Replaces make generate with proper Python/YAML handling.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from playbook_validator.config import (
    DOC_AUDIENCE_VALUES,
    DOC_LOAD_PRIORITY_VALUES,
    DOC_REVIEW_CYCLE_VALUES,
    DOC_STATUS_VALUES,
    OPTIONAL_FRONTMATTER_FIELDS,
    REQUIRED_FRONTMATTER_FIELDS,
)
from playbook_validator.frontmatter import extract_frontmatter

# Files and directories excluded from content scanning (matches generate-index.sh)
_EXCLUDED_DIRS = {".git", ".github", "node_modules", "skills"}
_EXCLUDED_NAMES = {"CONTRIBUTING.md", "CHANGELOG.md", "README.md", "SECURITY.md", "LICENSE"}

# Tier descriptions used in the YAML header
_TIER_DESCRIPTIONS = {
    1: "Core — behavioral best practices, rules, and control mappings",
    2: "Supporting documentation — how-to guides and setup instructions",
    3: "Templates and checklists — reusable artifacts for projects",
}


# ── Data structures ────────────────────────────────────────────────


@dataclass
class DocumentInfo:
    """Parsed metadata for a content document."""

    path: str
    title: str = ""
    description: str = ""
    status: str = ""
    tier: int = 0
    load_priority: str | None = None
    last_updated: str | None = None
    audience: str | list[str] | None = None
    review_cycle: str | None = None
    nist_controls: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)

    @classmethod
    def from_frontmatter(cls, path: str, fm: dict[str, Any]) -> DocumentInfo:
        """Create from a frontmatter dict."""
        return cls(
            path=path,
            title=fm.get("title", ""),
            description=fm.get("description", ""),
            status=fm.get("status", ""),
            tier=fm.get("tier", 0),
            load_priority=fm.get("load_priority"),
            last_updated=fm.get("last_updated"),
            audience=fm.get("audience"),
            review_cycle=fm.get("review_cycle"),
            nist_controls=fm.get("nist_controls") or [],
            frameworks=fm.get("frameworks") or [],
        )


@dataclass
class SkillInfo:
    """Parsed metadata for a skill directory."""

    name: str
    skill_path: str
    description: str
    has_scripts: bool
    scripts: list[str] = field(default_factory=list)


@dataclass
class IndexStats:
    """Computed statistics for the index."""

    total_documents: int = 0
    total_skills: int = 0
    tier_1_core: int = 0
    tier_2_supporting: int = 0
    tier_3_templates: int = 0
    total_nist_controls_referenced: int = 0
    frameworks_covered: int = 0


# ── Collection functions ───────────────────────────────────────────


def collect_documents(root: Path) -> list[DocumentInfo]:
    """Find and parse all content .md files, returning sorted DocumentInfo list."""
    files: list[Path] = []
    for pattern in ("**/*.md", "**/*.md.template", "**/*.md.example"):
        files.extend(root.glob(pattern))

    result: list[DocumentInfo] = []
    seen: set[Path] = set()

    for fpath in files:
        resolved = fpath.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)

        try:
            rel = fpath.relative_to(root)
        except ValueError:
            continue

        if any(p in _EXCLUDED_DIRS for p in rel.parts):
            continue
        if rel.name in _EXCLUDED_NAMES:
            continue

        fm = extract_frontmatter(fpath)
        if not fm or fm.get("tier") not in (1, 2, 3):
            continue

        result.append(DocumentInfo.from_frontmatter(rel.as_posix(), fm))

    result.sort(key=lambda d: d.path)
    return result


def collect_skills(root: Path) -> list[SkillInfo]:
    """Find and parse skill directories under skills/."""
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []

    result: list[SkillInfo] = []
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue

        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue

        fm = extract_frontmatter(skill_file)
        desc = fm.get("description", "")
        name = entry.name
        skill_path = f"skills/{name}/SKILL.md"

        scripts_dir = entry / "scripts"
        script_files: list[str] = []
        if scripts_dir.is_dir():
            for sf in sorted(scripts_dir.iterdir()):
                if sf.is_file() and sf.suffix in (".sh", ".py"):
                    script_files.append(sf.relative_to(root).as_posix())

        result.append(SkillInfo(name, skill_path, desc, len(script_files) > 0, script_files))

    return result


# ── Stats computation ──────────────────────────────────────────────


def compute_stats(documents: list[DocumentInfo], skills: list[SkillInfo]) -> IndexStats:
    """Compute aggregate statistics from documents and skills."""
    unique_controls: set[str] = set()
    unique_frameworks: set[str] = set()

    for doc in documents:
        for ctrl in doc.nist_controls:
            if isinstance(ctrl, str) and re.match(r"^[A-Z]", ctrl):
                unique_controls.add(ctrl)
        for fw in doc.frameworks:
            if isinstance(fw, str) and fw.strip():
                unique_frameworks.add(fw.strip())

    tier_counts = {1: 0, 2: 0, 3: 0}
    for doc in documents:
        if doc.tier in tier_counts:
            tier_counts[doc.tier] += 1

    return IndexStats(
        total_documents=len(documents),
        total_skills=len(skills),
        tier_1_core=tier_counts[1],
        tier_2_supporting=tier_counts[2],
        tier_3_templates=tier_counts[3],
        total_nist_controls_referenced=len(unique_controls),
        frameworks_covered=len(unique_frameworks),
    )


# ── YAML rendering ─────────────────────────────────────────────────


def _yaml_quote(value: str) -> str:
    """Quote a string for YAML output, escaping inner double quotes and backslashes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_audience(audience: str | list[str] | None) -> str:
    """Format audience field — could be string or list."""
    if isinstance(audience, list):
        return "[" + ", ".join(str(a) for a in audience) + "]"
    return str(audience)


def _emit_doc(doc: DocumentInfo) -> str:
    """Render a single document entry as YAML text."""
    lines: list[str] = []
    lines.append(f"  - path: {_yaml_quote(doc.path)}")
    lines.append(f"    title: {_yaml_quote(doc.title)}")
    lines.append(f"    description: {_yaml_quote(doc.description)}")
    lines.append(f"    status: {doc.status}")
    lines.append(f"    tier: {doc.tier}")
    if doc.load_priority:
        lines.append(f"    load_priority: {doc.load_priority}")
    if doc.last_updated:
        lines.append(f"    last_updated: {_yaml_quote(str(doc.last_updated))}")
    if doc.audience is not None:
        lines.append(f"    audience: {_format_audience(doc.audience)}")
    if doc.nist_controls:
        count = sum(1 for c in doc.nist_controls if re.match(r"^[A-Z]", str(c)))
        if count > 0:
            lines.append(f"    nist_controls_count: {count}")
    if doc.review_cycle:
        lines.append(f"    review_cycle: {doc.review_cycle}")
    lines.append("")
    return "\n".join(lines)


def _render_header(today: str) -> list[str]:
    """Render YAML header comments and top-level fields."""
    return [
        "# Agentic Coding Playbook — Document Index",
        "#",
        "# AUTO-GENERATED by make generate",
        "# Do NOT edit manually — run: make generate",
        "#",
        "# Agents SHOULD read this file to understand the repository structure",
        "# before making changes that span multiple documents.",
        "#",
        "# Schema version: 1.0",
        f"# Last generated: {today}",
        "",
        'schema_version: "1.0"',
        f'generated: "{today}"',
        'repo: "GSA-TTS/agentic-coding-playbook"',
        'scope: "FIPS Moderate | Single-agent | Internal enterprise"',
        "",
    ]


def _render_frontmatter_schema() -> list[str]:
    """Render the frontmatter schema section."""
    required_fields = sorted(REQUIRED_FRONTMATTER_FIELDS)
    optional_fields = sorted(OPTIONAL_FRONTMATTER_FIELDS)

    def _quoted_list(items: list[str]) -> str:
        return "[" + ", ".join(f'"{v}"' for v in items) + "]"

    lines: list[str] = []
    lines.append("# Frontmatter schema — all .md content files MUST include at minimum:")
    lines.append(f"#   {', '.join(f'{f} (required)' for f in required_fields)}")
    lines.append(f"# Optional: {', '.join(optional_fields)}")
    lines.append("frontmatter_schema:")
    lines.append(f"  required: {_quoted_list(required_fields)}")
    lines.append(f"  optional: {_quoted_list(optional_fields)}")
    lines.append(f"  status_values: {_quoted_list(sorted(DOC_STATUS_VALUES))}")
    lines.append("  tier_values:")
    for tier_num in (1, 2, 3):
        lines.append(f'    {tier_num}: "{_TIER_DESCRIPTIONS[tier_num]}"')
    lines.append(f"  audience_values: {_quoted_list(sorted(DOC_AUDIENCE_VALUES))}")
    lines.append(f"  load_priority_values: {_quoted_list(sorted(DOC_LOAD_PRIORITY_VALUES))}")
    lines.append(f"  review_cycle_values: {_quoted_list(sorted(DOC_REVIEW_CYCLE_VALUES))}")
    lines.append("")
    return lines


def _render_documents(documents: list[DocumentInfo]) -> list[str]:
    """Render all documents grouped by tier."""
    lines: list[str] = ["# Document inventory", "documents:"]
    tier_docs: dict[int, list[DocumentInfo]] = {1: [], 2: [], 3: []}
    for doc in documents:
        if doc.tier in tier_docs:
            tier_docs[doc.tier].append(doc)

    tier_headers = {
        1: "  # ── Tier 1: Core ─────────────────────────────────────────────────",
        2: "  # ── Tier 2: Supporting Documentation ─────────────────────────────",
        3: "  # ── Tier 3: Templates, Checklists, and Examples ──────────────────",
    }

    for tier_num in (1, 2, 3):
        if tier_docs[tier_num]:
            lines.append(tier_headers[tier_num])
            for doc in tier_docs[tier_num]:
                lines.append(_emit_doc(doc))
    return lines


def _render_skills(skills: list[SkillInfo]) -> list[str]:
    """Render the skills section."""
    if not skills:
        return []
    lines: list[str] = [
        "# Agent Skills — executable compliance procedures (Agent Skills format)",
        "# Skills provide step-by-step workflows agents can follow.",
        "# They reference policy docs by path+section — no policy duplication.",
        "# Format: https://agentskills.io/specification",
        "skills:",
    ]
    for skill in skills:
        lines.append(f"  - name: {skill.name}")
        lines.append(f'    path: "{skill.skill_path}"')
        lines.append(f"    description: {_yaml_quote(skill.description)}")
        if skill.has_scripts:
            lines.append("    has_scripts: true")
            lines.append("    scripts:")
            for script in skill.scripts:
                lines.append(f'      - "{script}"')
        else:
            lines.append("    has_scripts: false")
        lines.append("")
    return lines


def render_index_yaml(
    documents: list[DocumentInfo],
    skills: list[SkillInfo],
    stats: IndexStats,
    generated_date: str | None = None,
) -> str:
    """Generate the full INDEX.yaml content string."""
    today = generated_date or date.today().isoformat()
    lines: list[str] = []
    lines.extend(_render_header(today))
    lines.extend(_render_frontmatter_schema())
    lines.extend(_render_documents(documents))
    lines.extend(_render_skills(skills))
    lines.append("stats:")
    lines.append(f"  total_documents: {stats.total_documents}")
    lines.append(f"  total_skills: {stats.total_skills}")
    lines.append(f"  tier_1_core: {stats.tier_1_core}")
    lines.append(f"  tier_2_supporting: {stats.tier_2_supporting}")
    lines.append(f"  tier_3_templates: {stats.tier_3_templates}")
    lines.append(f"  total_nist_controls_referenced: {stats.total_nist_controls_referenced}")
    lines.append(f"  frameworks_covered: {stats.frameworks_covered}")
    return "\n".join(lines)


# ── Check mode ─────────────────────────────────────────────────────


def check_mode(root: Path) -> bool:
    """Compare generated INDEX.yaml against existing file.

    Returns True if they match (ignoring generated date), False otherwise.
    """
    existing_path = root / "INDEX.yaml"
    if not existing_path.is_file():
        return False

    documents = collect_documents(root)
    skills = collect_skills(root)
    stats = compute_stats(documents, skills)
    generated = render_index_yaml(documents, skills, stats)
    existing = existing_path.read_text(encoding="utf-8")

    def strip_date_lines(text: str) -> str:
        return "\n".join(
            line
            for line in text.splitlines()
            if not line.startswith("generated:") and not line.startswith("# Last generated:")
        )

    return strip_date_lines(generated) == strip_date_lines(existing)


# ── Full generation ────────────────────────────────────────────────


def generate_index(root: Path) -> None:
    """Full generation: write INDEX.yaml and inject skills tables."""
    from playbook_validator.index_updaters import (
        inject_readme_table,
        render_skills_table,
        update_context_guide_word_counts,
        update_doc_inventory,
        update_hardcoded_counts,
        update_landscape_summary,
        update_llms_txt,
        update_phase_mapping,
        update_roadmap_metrics,
    )

    documents = collect_documents(root)
    skills = collect_skills(root)
    stats = compute_stats(documents, skills)

    yaml_content = render_index_yaml(documents, skills, stats)
    (root / "INDEX.yaml").write_text(yaml_content, encoding="utf-8")

    table = render_skills_table(skills)
    # Note: the universal AGENTS.md deliberately carries no skills table — the
    # skills inventory lives in the repo-specific docs/AGENT-INSTRUCTIONS.md.
    for target in ["README.md", "docs/AGENT-INSTRUCTIONS.md"]:
        inject_readme_table(root / target, table)

    update_context_guide_word_counts(root)
    update_hardcoded_counts(root, stats, skills)
    update_landscape_summary(root)
    update_phase_mapping(root)
    update_roadmap_metrics(root, stats)
    update_doc_inventory(root)
    update_llms_txt(root)

    print(
        f"Generated INDEX.yaml "
        f"({stats.total_documents} documents, "
        f"{stats.total_skills} skills, "
        f"{stats.total_nist_controls_referenced} unique NIST controls)"
    )


# ── CLI entry point ────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """CLI entry point matching generate-index.sh interface."""
    parser = argparse.ArgumentParser(description="Generate INDEX.yaml from source files")
    parser.add_argument("--check", action="store_true", help="Compare to existing INDEX.yaml, exit 1 if different")
    parser.add_argument("--root", type=Path, default=None, help="Repository root directory")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent.parent).resolve()

    if args.check:
        if check_mode(root):
            print("OK: INDEX.yaml is up to date")
            return 0
        else:
            print("ERROR: INDEX.yaml is out of date. Run: make generate")
            return 1

    generate_index(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
