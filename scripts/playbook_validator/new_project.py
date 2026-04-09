"""Bootstrap a new project from the playbook governance templates.

Creates a new project directory with AGENTS.md (the universal standard),
skills, coding standards, and compliance templates.

AGENTS.md is read natively by 25+ tools (Codex, Copilot, Cursor, Windsurf,
Amp, Devin). No agent-specific config files are needed for most tools.
If a specific tool needs a config file, see AGENTS.md for instructions.

Usage:
    python -m playbook_validator new-project --dir /path/to/new-repo
"""

import shutil
from pathlib import Path

# Files copied from playbook to new project
FILES_TO_COPY = [
    ("templates/PROJECT_PLAN.md", "PROJECT_PLAN.md"),
    ("templates/AGENTS.md.template", "AGENTS.md"),
    ("docs/CODING_PRACTICES.md", "docs/CODING_PRACTICES.md"),
    ("docs/CODING_STANDARDS_COMPACT.md", "docs/CODING_STANDARDS_COMPACT.md"),
    ("CONTEXT-GUIDE.md", "CONTEXT-GUIDE.md"),
    ("templates/risk-assessment.md", "docs/risk-assessment.md"),
    ("checklists/pre-deployment.md", "checklists/pre-deployment.md"),
]


def new_project(target_dir: Path, playbook_root: Path) -> tuple[list[str], list[str]]:
    """Bootstrap a new project directory with playbook governance files and skills.

    Copies AGENTS.md (universal, read by 25+ tools), skills, coding standards,
    and compliance templates. No agent-specific config files are created —
    AGENTS.md is the single instruction file for all tools.

    Returns (copied_files, skipped_files).
    """
    copied: list[str] = []
    skipped: list[str] = []

    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy template files
    for src_rel, dest_rel in FILES_TO_COPY:
        src = playbook_root / src_rel
        dest = target_dir / dest_rel

        if not src.exists():
            skipped.append(f"{src_rel} (source not found)")
            continue

        if dest.exists():
            skipped.append(f"{dest_rel} (already exists)")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(dest_rel)

    # Copy skills (entire directory tree)
    skills_src = playbook_root / "skills"
    skills_dest = target_dir / "skills"
    if skills_src.is_dir() and not skills_dest.exists():
        shutil.copytree(skills_src, skills_dest)
        skill_count = len(list(skills_dest.glob("*/SKILL.md")))
        copied.append(f"skills/ ({skill_count} skills)")
    elif skills_dest.exists():
        skipped.append("skills/ (already exists)")
    else:
        skipped.append("skills/ (source not found)")

    return copied, skipped
