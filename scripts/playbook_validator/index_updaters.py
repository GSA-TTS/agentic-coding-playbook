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
    return splice_generated_block(readme_path, "SKILLS_TABLE", table)


def splice_generated_block(path: Path, marker_id: str, body: str) -> bool:
    """Replace the content between ``GENERATED:<marker_id>:START/END`` markers.

    Generic marker-splice used by all generated-doc regions (skills table,
    landscape summary, …). Text outside the marker pair is preserved verbatim;
    only the region between them is regenerated. Returns True if the markers
    exist (and the block was written/kept in sync), False if absent (no-op).
    """
    if not path.is_file():
        return False

    start_marker = f"<!-- GENERATED:{marker_id}:START"
    end_marker = f"<!-- GENERATED:{marker_id}:END -->"

    content = path.read_text(encoding="utf-8")
    if start_marker not in content:
        return False

    start_line = f"{start_marker} — do not edit, run: make generate -->"
    replacement = f"{start_line}\n{body}\n{end_marker}"

    pattern = re.compile(
        re.escape(start_marker) + r"[^\n]*\n.*?" + re.escape(end_marker),
        re.DOTALL,
    )
    new_content = pattern.sub(replacement, content)

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
    return True


# ── Federal AI landscape Status Summary (#142) ────────────────────────

# Category → display label + fixed row order for the Status Summary table.
_LANDSCAPE_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("executive_order", "Executive Orders"),
    ("omb_memo", "OMB Memoranda"),
    ("nist_standard", "NIST Standards"),
    ("legislation", "Federal Legislation"),
    ("agency_strategy", "Agency Strategies"),
    ("agency_report", "Agency Reports"),
    ("industry_standard", "Industry Standards"),
    ("white_house_plan", "White House Plans"),
)
# status → summary column. "final" counts as Active (both denote in-effect).
_STATUS_COLUMN = {
    "active": "active",
    "final": "active",
    "revoked": "revoked",
    "rescinded": "revoked",
    "draft": "draft",
}


def compute_landscape_summary(root: Path) -> tuple[dict[str, dict[str, int]], int] | None:
    """Return ({category: {active,revoked,draft}}, total_entries) from the YAML.

    Single source of truth for the Status Summary counts, shared by the
    generator and the drift guard (#142). None if the registry is absent.
    """
    landscape = root / "data" / "federal-ai-landscape.yaml"
    if not landscape.is_file():
        return None
    import yaml

    data = yaml.safe_load(landscape.read_text(encoding="utf-8")) or {}
    entries = data.get("entries", [])
    counts: dict[str, dict[str, int]] = {
        cat: {"active": 0, "revoked": 0, "draft": 0} for cat, _ in _LANDSCAPE_CATEGORIES
    }
    for entry in entries:
        cat = entry.get("category")
        col = _STATUS_COLUMN.get(entry.get("status"))
        if cat in counts and col is not None:
            counts[cat][col] += 1
    return counts, len(entries)


def render_landscape_summary_table(counts: dict[str, dict[str, int]]) -> str:
    """Render the Status Summary markdown table from computed counts (#142)."""
    lines = [
        "| Category | Active | Revoked/Rescinded | Draft |",
        "|---|---|---|---|",
    ]
    ta = tr = td = 0
    for cat, label in _LANDSCAPE_CATEGORIES:
        b = counts[cat]
        ta += b["active"]
        tr += b["revoked"]
        td += b["draft"]
        lines.append(f"| {label} | {b['active']} | {b['revoked']} | {b['draft']} |")
    lines.append(f"| **Total** | **{ta}** | **{tr}** | **{td}** |")
    return "\n".join(lines)


def update_landscape_summary(root: Path) -> None:
    """Regenerate the Status Summary table in docs/FEDERAL-AI-LANDSCAPE.md (#142).

    No-op if the doc lacks the GENERATED:LANDSCAPE_SUMMARY markers or the
    registry is absent. Prose outside the markers is untouched.
    """
    result = compute_landscape_summary(root)
    if result is None:
        return
    counts, _ = result
    table = render_landscape_summary_table(counts)
    splice_generated_block(root / "docs" / "FEDERAL-AI-LANDSCAPE.md", "LANDSCAPE_SUMMARY", table)


# ── Federal AI landscape Playbook Phase Mapping (#142) ────────────────

# Phase id → display label. Phase names are editorial (not in the registry);
# membership is derived from each entry's `playbook_phases`. Order is the
# playbook's lifecycle order, with 0.5 between 0 and 1.
_PHASE_LABELS: tuple[tuple[str, str], ...] = (
    ("0", "Phase 0: Project Plan"),
    ("0.5", "Phase 0.5: Environment Doctor"),
    ("1", "Phase 1: Repo Setup"),
    ("2", "Phase 2: Agent Config"),
    ("3", "Phase 3: Write Code"),
    ("4", "Phase 4: Document Decisions"),
    ("5", "Phase 5: Assess Risk"),
    ("6", "Phase 6: Pre-Deploy Check"),
    ("7", "Phase 7: Deploy"),
)


def _landscape_short_ref(entry: dict) -> str:
    """A compact reference label for a landscape entry in the phase table.

    Prefers a clean short code for the well-known id shapes:
      eo-14179     → EO 14179
      m-25-21      → M-25-21
      nist-ai-100-1→ NIST AI 100-1  (nist-sp-800-218a → NIST SP 800-218A)
    For ids that don't match those shapes (e.g. slsa, mitre-atlas,
    ai-action-plan-2025), fall back to the entry title so the cell stays
    human-readable rather than a shouting slug.
    """
    eid = str(entry.get("id", "")).strip()
    if not eid:
        return str(entry.get("title", ""))[:48]
    low = eid.lower()
    if low.startswith("eo-"):
        return "EO " + eid[3:]
    if low.startswith("m-"):
        return eid.upper()
    if low.startswith("nist-"):
        # nist-sp-800-218a → NIST SP 800-218A ; nist-ai-100-1 → NIST AI 100-1
        return "NIST " + eid[5:].upper().replace("-", " ", 1)
    # Non-coded ids: use a clean short label from the title — drop any
    # parenthetical, then trim to a word boundary so the cell stays readable
    # (no mid-word truncation) without needing a schema field.
    title = str(entry.get("title", "")).strip()
    if not title:
        return eid
    title = title.split(" (", 1)[0].split(": ", 1)[0].strip()
    if len(title) > 46:
        cut = title[:46].rsplit(" ", 1)[0]
        title = f"{cut}…"
    return title


def compute_phase_mapping(root: Path) -> dict[str, list[str]] | None:
    """Return {phase_id: [short_ref, ...]} derived from `playbook_phases` (#142)."""
    landscape = root / "data" / "federal-ai-landscape.yaml"
    if not landscape.is_file():
        return None
    import yaml

    data = yaml.safe_load(landscape.read_text(encoding="utf-8")) or {}
    mapping: dict[str, list[str]] = {pid: [] for pid, _ in _PHASE_LABELS}
    for entry in data.get("entries", []):
        for pid in entry.get("playbook_phases", []) or []:
            if pid in mapping:
                mapping[pid].append(_landscape_short_ref(entry))
    return mapping


def render_phase_mapping_table(mapping: dict[str, list[str]]) -> str:
    """Render the Playbook Phase Mapping markdown table from the mapping (#142).

    Every phase member assigned in the registry is listed; a phase with no
    assigned entries shows an em dash.
    """
    lines = ["| Phase | References (from registry `playbook_phases`) |", "|---|---|"]
    for pid, label in _PHASE_LABELS:
        refs = mapping.get(pid, [])
        cell = ", ".join(refs) if refs else "—"
        lines.append(f"| **{label}** | {cell} |")
    return "\n".join(lines)


def update_phase_mapping(root: Path) -> None:
    """Regenerate the Playbook Phase Mapping table in the landscape doc (#142).

    No-op if the GENERATED:LANDSCAPE_PHASES markers or registry are absent.
    """
    mapping = compute_phase_mapping(root)
    if mapping is None:
        return
    table = render_phase_mapping_table(mapping)
    splice_generated_block(root / "docs" / "FEDERAL-AI-LANDSCAPE.md", "LANDSCAPE_PHASES", table)


# ── Neutral document inventory (#199) ─────────────────────────────────
#
# A single generated "all documents" table sourced from INDEX.yaml — the
# machine inventory. Per the #199 consensus, this does NOT collapse the three
# distinct tier taxonomies (INDEX machine-inventory `tier`, docs/README human
# onboarding order, CONTEXT-GUIDE context-budget loading): those are different
# semantic axes and stay independently curated. This neutral inventory is the
# de-drift win — one generated list of every doc with its INDEX tier + purpose —
# without flattening the editorial views. It lives at the end of docs/README.md
# under GENERATED:DOC_INVENTORY markers.

_DOC_INVENTORY_REL = "docs/README.md"


def _load_index_documents(root: Path) -> list[dict] | None:
    """Return INDEX.yaml's `documents` list (path/title/description/tier/…), or None."""
    index = root / "INDEX.yaml"
    if not index.is_file():
        return None
    import yaml

    data = yaml.safe_load(index.read_text(encoding="utf-8")) or {}
    docs = data.get("documents")
    return docs if isinstance(docs, list) else None


def render_doc_inventory_table(documents: list[dict]) -> str:
    """Render the neutral all-documents inventory table from INDEX docs (#199).

    Columns: Document (path), Tier (INDEX machine tier), Purpose (INDEX
    description). Sorted by tier then path for a stable, diffable order.
    """
    rows = sorted(
        documents,
        key=lambda d: (d.get("tier", 99), str(d.get("path", ""))),
    )
    lines = [
        "| Document | Tier | Purpose |",
        "|----------|------|---------|",
    ]
    for doc in rows:
        path = str(doc.get("path", "")).strip()
        tier = doc.get("tier", "—")
        # description is the INDEX machine description; collapse whitespace.
        purpose = " ".join(str(doc.get("description", "")).split())
        lines.append(f"| `{path}` | {tier} | {purpose} |")
    return "\n".join(lines)


def update_doc_inventory(root: Path) -> None:
    """Regenerate the neutral document inventory in docs/README.md (#199).

    No-op if the GENERATED:DOC_INVENTORY markers or INDEX.yaml are absent. The
    hand-curated tier tables above the markers are untouched.
    """
    documents = _load_index_documents(root)
    if documents is None:
        return
    table = render_doc_inventory_table(documents)
    splice_generated_block(root / _DOC_INVENTORY_REL, "DOC_INVENTORY", table)


# ── TRACEABILITY §1 control matrix (#197) ─────────────────────────────
#
# The Control + Name columns are generated from source: the control row-set is
# the union of `nist_controls:` frontmatter across the matrix's document
# columns, and the Name is the authoritative NIST title from the derived OSCAL
# map (data/nist-800-53-control-names.json, refreshed by refresh_oscal_control_names).
# The per-document presence cells (§-anchors / checklist numbers) are EDITORIAL
# and preserved verbatim across regeneration — only Control+Name are rebuilt.

_TRACEABILITY_REL = "docs/TRACEABILITY.md"
_OSCAL_NAMES_REL = "data/nist-800-53-control-names.json"
# The matrix's document columns, in header order. Each is a repo-relative path
# whose frontmatter nist_controls contributes to the row-set and whose header
# label must be reproduced verbatim.
_TRACEABILITY_COLUMNS: tuple[tuple[str, str], ...] = (
    ("AGENTS.md", "AGENTS.md"),
    ("docs/CODING_PRACTICES.md", "docs/CODING_PRACTICES.md"),
    ("docs/SECURITY-CONTROLS.md", "SECURITY-CONTROLS.md"),
    ("docs/AGENT-IDENTITY.md", "AGENT-IDENTITY.md"),
)
_TRACEABILITY_START = "<!-- GENERATED:TRACEABILITY_MATRIX:START"
_TRACEABILITY_END = "<!-- GENERATED:TRACEABILITY_MATRIX:END -->"


def load_oscal_control_names(root: Path) -> dict[str, str] | None:
    """Load the derived NIST control id→title map, or None if absent."""
    path = root / _OSCAL_NAMES_REL
    if not path.is_file():
        return None
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    controls = data.get("controls")
    return controls if isinstance(controls, dict) else None


def _control_sort_key(control_id: str) -> tuple[str, int]:
    """Sort AC-2 before AC-12 before AU-2 (family alpha, then numeric)."""
    family, _, num = control_id.partition("-")
    try:
        return (family, int(num))
    except ValueError:
        return (family, 0)


def _extract_traceability_editorial(root: Path) -> dict[str, list[str]]:
    """Parse the CURRENT §1 rows to preserve each control's editorial cells.

    Returns {control_id: [doc1, doc2, doc3, doc4, checklist]} — the 5 non-derived
    cells. Missing controls default to all em dashes. Only reads the region
    between the TRACEABILITY markers if present, else the whole file (first-run
    adoption, before markers exist)."""
    doc = root / _TRACEABILITY_REL
    if not doc.is_file():
        return {}
    text = doc.read_text(encoding="utf-8")
    if _TRACEABILITY_START in text and _TRACEABILITY_END in text:
        text = text.split(_TRACEABILITY_START, 1)[1].split(_TRACEABILITY_END, 1)[0]
    editorial: dict[str, list[str]] = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*([A-Z]{2}-\d{1,2})\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # cells: [Control, Name, doc1, doc2, doc3, doc4, checklist]
        if len(cells) >= 7:
            editorial[m.group(1)] = cells[2:7]
    return editorial


def compute_traceability_rows(root: Path) -> tuple[list[str], dict[str, str]] | None:
    """Return (sorted control_ids, id→name) for the §1 matrix (#197).

    Row-set = union of nist_controls frontmatter across the matrix's document
    columns. Names from the derived OSCAL map. None if the OSCAL map is absent.
    """
    from playbook_validator.frontmatter import get_array_field

    names = load_oscal_control_names(root)
    if names is None:
        return None
    control_ids: set[str] = set()
    for rel, _label in _TRACEABILITY_COLUMNS:
        for ctrl in get_array_field(root / rel, "nist_controls") or []:
            if isinstance(ctrl, str) and re.fullmatch(r"[A-Z]{2}-\d{1,2}", ctrl):
                control_ids.add(ctrl)
    return sorted(control_ids, key=_control_sort_key), names


def render_traceability_matrix(control_ids: list[str], names: dict[str, str], editorial: dict[str, list[str]]) -> str:
    """Render the §1 matrix. Control+Name derived; presence cells preserved."""
    header_labels = [label for _rel, label in _TRACEABILITY_COLUMNS]
    header = "| Control | Name | " + " | ".join(header_labels) + " | Checklist |"
    sep = "|" + "|".join(["---"] * (len(header_labels) + 3)) + "|"
    lines = [header, sep]
    blank = ["—", "—", "—", "—", "—"]
    for cid in control_ids:
        name = names.get(cid, "")
        cells = editorial.get(cid, blank)
        # pad/truncate defensively to exactly 5 editorial cells
        cells = (cells + blank)[:5]
        lines.append(f"| {cid} | {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def update_traceability_matrix(root: Path) -> None:
    """Regenerate the TRACEABILITY §1 Control+Name columns (#197).

    No-op if the GENERATED:TRACEABILITY_MATRIX markers or the OSCAL map are
    absent. Editorial presence cells are preserved verbatim.
    """
    computed = compute_traceability_rows(root)
    if computed is None:
        return
    control_ids, names = computed
    editorial = _extract_traceability_editorial(root)
    table = render_traceability_matrix(control_ids, names, editorial)
    splice_generated_block(root / _TRACEABILITY_REL, "TRACEABILITY_MATRIX", table)


# ── Repo-root llms.txt (#212) ─────────────────────────────────────────
#
# The llmstxt.org convention: a curated, link-based map at the repo root that
# lets an agent navigate the repo without loading everything. This is the
# agent-facing projection of INDEX.yaml — fully generated (whole file), so it
# cannot drift; a fail-closed guard (validate-docs) requires it match.

_LLMS_TXT_REL = "llms.txt"
_LLMS_TXT_HEADER = "<!-- GENERATED by `make generate` from INDEX.yaml — do not edit by hand. -->"


def render_llms_txt(index: dict) -> str:
    """Render llms.txt (llmstxt.org format) from the INDEX.yaml document set.

    Structure: H1 (repo) + blockquote summary, then an H2 section per tier with
    ``- [title](path): description`` links. Registries under a Data section.
    Sorted (tier, path) for a stable, diffable file.
    """
    repo = str(index.get("repo", "")).strip()
    scope = str(index.get("scope", "")).strip()
    documents = index.get("documents") or []

    name = repo.split("/")[-1] if repo else "repository"
    lines = [_LLMS_TXT_HEADER, "", f"# {name}", ""]
    summary = "Federal AI agent behavioral playbook and standards."
    if scope:
        summary += f" Scope: {scope}."
    lines += [f"> {summary}", ""]
    lines += [
        "This file follows the [llms.txt](https://llmstxt.org/) convention: a "
        "curated map of the repository for AI agents. Paths are repo-relative.",
        "",
    ]

    tier_titles = {
        1: "Core (always load)",
        2: "Supporting",
        3: "Templates & checklists",
    }
    by_tier: dict[int, list[dict]] = {}
    for doc in documents:
        by_tier.setdefault(doc.get("tier", 99), []).append(doc)

    for tier in sorted(by_tier):
        heading = tier_titles.get(tier, f"Tier {tier}")
        lines.append(f"## {heading}")
        lines.append("")
        for doc in sorted(by_tier[tier], key=lambda d: str(d.get("path", ""))):
            path = str(doc.get("path", "")).strip()
            title = str(doc.get("title", path)).strip()
            desc = " ".join(str(doc.get("description", "")).split())
            lines.append(f"- [{title}]({path}): {desc}" if desc else f"- [{title}]({path})")
        lines.append("")

    lines += [
        "## Data",
        "",
        "- [INDEX.yaml](INDEX.yaml): machine-readable document + skill inventory (source of truth).",
        "- [data/federal-ai-landscape.yaml](data/federal-ai-landscape.yaml): federal AI guidance registry.",
        "- [data/frameworks.yaml](data/frameworks.yaml): canonical framework references.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def update_llms_txt(root: Path) -> None:
    """Regenerate the repo-root llms.txt from INDEX.yaml (#212). No-op if INDEX absent."""
    index_path = root / "INDEX.yaml"
    if not index_path.is_file():
        return
    import yaml

    index = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    (root / _LLMS_TXT_REL).write_text(render_llms_txt(index), encoding="utf-8")


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


def count_landscape_entries(root: Path) -> int | None:
    """Return the number of ``entries:`` in the landscape registry, or None.

    Single source of truth for the landscape count, shared by the generator
    (this module) and the drift guard (validate_docs) so they cannot disagree.
    """
    landscape_path = root / "data" / "federal-ai-landscape.yaml"
    if not landscape_path.is_file():
        return None
    content = landscape_path.read_text(encoding="utf-8")
    return len(re.findall(r"^\s+- id:", content, re.MULTILINE))


def count_security_controls(root: Path) -> int | None:
    """Return the count of distinct documented NIST controls, or None.

    Counts the unique ``| **XX-N** |`` control rows in docs/SECURITY-CONTROLS.md
    — the same body-row source the #121 integrity guard uses (raw rows may
    duplicate a control across families, so distinct is authoritative). Shared
    with the drift guard so prose rewrites and the CI check agree.
    """
    doc = root / "docs" / "SECURITY-CONTROLS.md"
    if not doc.is_file():
        return None
    text = doc.read_text(encoding="utf-8")
    body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
    rows = re.findall(r"^\|\s*\*\*([A-Z]{2}-\d{1,2})\*\*\s*\|", body, re.MULTILINE)
    return len(set(rows))


# Landscape-catalog "N entries" span. The count must not be part of a larger
# token (no preceding word char / dot / hyphen). Matches "39 entries".
_LANDSCAPE_ENTRIES_RE = re.compile(r"(?<![\w.\-])(\d+)(\s+entries\b)")
# "N controls" count span (issues #121, #184). The COUNT is a standalone integer
# (negative lookbehind rejects the "53" in "800-53" and "2" in "Rev 5.2"),
# optionally followed by a "security" or "NIST [SP] 800-53 [Rev 5.x]" qualifier,
# then "controls". Because the framework number itself ("800-53") is excluded
# from the count group by the lookbehind, "NIST 800-53 controls" (no leading
# tally) cannot match, while "36 NIST 800-53 controls" captures 36 as the count.
_CONTROLS_QUALIFIER = r"(?:security\s+|NIST\s+(?:SP\s+)?800-53\s+(?:Rev\s+5(?:\.\d+)?\s+)?)?"
_CONTROLS_RE = re.compile(rf"(?<![\w.\-])(\d+)(\s+{_CONTROLS_QUALIFIER}controls\b)")


def update_hardcoded_counts(root: Path, stats: IndexStats, skills: list[SkillInfo]) -> None:
    """Update hardcoded counts in markdown files to match actual data.

    Replaces patterns like "N tests", "N skills", "N federal AI guidance",
    "N entries" (landscape catalog), and "N controls" with computed values from
    source data. Prevents count drift (issues #121, #184).
    """
    test_count = _collect_test_count(root)
    landscape_count = count_landscape_entries(root)
    controls_count = count_security_controls(root)

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
            text = _LANDSCAPE_ENTRIES_RE.sub(rf"{landscape_count}\2", text)

        if controls_count is not None:
            text = _CONTROLS_RE.sub(rf"{controls_count}\2", text)
            # "N controls mapped" prose (README/CONTRIBUTING) — the count is the
            # same documented-control total; keep it in sync too (#142).
            text = re.sub(
                r"(?<![\w.\-])\d+(\s+(?:NIST\s+(?:SP\s+)?800-53\s+)?controls\s+mapped\b)",
                rf"{controls_count}\1",
                text,
            )

        if text != original:
            md_file.write_text(text, encoding="utf-8")


def render_roadmap_metrics_table(root: Path, stats: IndexStats) -> str:
    """Render the ROADMAP 'Current State' metrics table from live sources (#142).

    Every cell is derived: documents/skills/controls from the index stats,
    landscape entries from the registry, tests from pytest collection, and
    checklist items by counting checkbox lines under checklists/.
    """
    landscape_count = count_landscape_entries(root)
    controls_count = count_security_controls(root)
    test_count = _collect_test_count(root)
    checklist_count = _count_checklist_items(root)
    rows = [
        ("Documents", stats.total_documents),
        ("Skills", stats.total_skills),
        ("Tests", test_count),
        ("Checklist items", checklist_count),
        ("Landscape entries", landscape_count),
        ("NIST controls mapped", controls_count),
    ]
    lines = ["| Metric | Count |", "|--------|-------|"]
    for label, value in rows:
        lines.append(f"| {label} | {value if value is not None else '—'} |")
    return "\n".join(lines)


def _count_checklist_items(root: Path) -> int | None:
    """Count numbered checklist item rows (``| N.N | … |``) under checklists/.

    The pre-deployment checklist enumerates items as ``| 1.1 | … |`` table rows
    (Pass/Fail/N/A columns), not markdown checkboxes — count those rows.
    """
    checklists = root / "checklists"
    if not checklists.is_dir():
        return None
    total = 0
    for md in checklists.glob("*.md"):
        total += len(re.findall(r"^\|\s*\d+\.\d+\s*\|", md.read_text(encoding="utf-8"), re.MULTILINE))
    return total or None


def update_roadmap_metrics(root: Path, stats: IndexStats) -> None:
    """Regenerate the ROADMAP metrics table (#142). No-op without the markers."""
    table = render_roadmap_metrics_table(root, stats)
    splice_generated_block(root / "docs" / "ROADMAP.md", "ROADMAP_METRICS", table)


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
