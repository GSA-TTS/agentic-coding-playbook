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

# Files copied from playbook to new project.
#
# The bootstrapped project deliberately does NOT receive a copy of the universal
# AGENTS.md. Instead it gets the thin, project-specific AGENTS.md template (which
# declares the universal contract as a prerequisite), keeping a single source of
# truth for the universal rules and avoiding drift. See ADR-0002.
#
# CONTEXT-GUIDE is sourced from templates/CONTEXT-GUIDE.project.md — a trimmed
# guide that references only the files a bootstrapped project actually contains,
# so a fresh project has no dangling references.
#
# SECURITY-CONTROLS.md is copied because CODING_PRACTICES.md's related_files
# references it; without it the reference would dangle in the project (#148).
#
# The self-contained contract probe (scripts/ensure-contract.py + .sh) is copied
# so the project can enforce the universal-contract prerequisite (ADR-0003)
# without installing the playbook-validator package.
FILES_TO_COPY = [
    ("templates/PROJECT_PLAN.md", "PROJECT_PLAN.md"),
    ("templates/AGENTS.md.template", "AGENTS.md"),
    ("docs/CODING_PRACTICES.md", "docs/CODING_PRACTICES.md"),
    ("docs/CODING_STANDARDS_COMPACT.md", "docs/CODING_STANDARDS_COMPACT.md"),
    ("docs/SECURITY-CONTROLS.md", "docs/SECURITY-CONTROLS.md"),
    ("templates/CONTEXT-GUIDE.project.md", "CONTEXT-GUIDE.md"),
    ("templates/risk-assessment.md", "docs/risk-assessment.md"),
    ("checklists/pre-deployment.md", "checklists/pre-deployment.md"),
    ("templates/ensure-contract.py", "scripts/ensure-contract.py"),
    ("templates/ensure-contract.sh", "scripts/ensure-contract.sh"),
    ("templates/pre-commit-config.project.yaml", ".pre-commit-config.yaml"),
    ("templates/contract-check.workflow.yaml", ".github/workflows/contract-check.yml"),
]

# Skills copied into a downstream project. This is an ALLOWLIST of
# downstream-relevant skills. Playbook-OPERATIONAL skills are deliberately
# excluded (see ADR-0002 / issue #145): they run *this* repo, not a downstream
# one, and reference playbook-only paths (data/, INDEX.yaml, playbook_validator):
#   - federal-landscape-update  (monitors the playbook's own RSS registry)
#   - project-bootstrap         (bootstraps *from* the playbook)
#   - federal-agents-config     (generates this very layer from playbook templates)
# A downstream project that needs to bootstrap sub-projects uses the playbook
# directly rather than a vendored copy of these skills.
DOWNSTREAM_SKILLS = (
    "agent-permissions",
    "ato-package",
    "cloudgov-deploy",
    "code-review",
    "federal-decision-records",
    "federal-pre-deployment-check",
    "federal-risk-assessment",
)

# Excluded (playbook-operational) skills, kept explicit for the e2e test and
# for auditability.
EXCLUDED_SKILLS = (
    "federal-agents-config",
    "federal-landscape-update",
    "project-bootstrap",
    # Playbook-doc NAVIGATORS (#189): these skills exist to navigate the
    # playbook's own reference docs (federal-security-controls-lookup reads
    # docs/TRACEABILITY.md + INDEX.yaml; federal-repo-setup converts
    # docs/GETTING-STARTED.md). Those docs are playbook-only and not copied
    # downstream, so the skills are inert / dangling in a bootstrapped project.
    # A downstream project consults the playbook directly instead.
    "federal-security-controls-lookup",
    "federal-repo-setup",
)

# Git-ignore entries written into the bootstrapped project so the fallback
# contract cache is never committed (ADR-0002 / ADR-0003).
GITIGNORE_ENTRIES = (
    "# Fallback cache for the universal behavioral contract — never commit.",
    "# The canonical contract is provided by the environment; see README.",
    ".agents/cache/",
)


def _executable_dests() -> frozenset[str]:
    """Destination paths that should be marked executable after copy."""
    return frozenset({"scripts/ensure-contract.sh", "scripts/ensure-contract.py"})


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
    executable = _executable_dests()
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
        if dest_rel in executable:
            dest.chmod(0o755)
        copied.append(dest_rel)

    # Copy skills — allowlist of downstream-relevant skills only. Playbook-
    # operational skills are excluded (see EXCLUDED_SKILLS / ADR-0002 / #145).
    skills_src = playbook_root / "skills"
    skills_dest = target_dir / "skills"
    if skills_dest.exists():
        skipped.append("skills/ (already exists)")
    elif not skills_src.is_dir():
        skipped.append("skills/ (source not found)")
    else:
        copied_skills = 0
        for skill_name in DOWNSTREAM_SKILLS:
            skill_src = skills_src / skill_name
            if not skill_src.is_dir():
                skipped.append(f"skills/{skill_name} (source not found)")
                continue
            shutil.copytree(skill_src, skills_dest / skill_name)
            copied_skills += 1
        if copied_skills:
            copied.append(f"skills/ ({copied_skills} downstream skills)")
        for excluded in EXCLUDED_SKILLS:
            skipped.append(f"skills/{excluded} (playbook-operational — excluded)")

    # Write the fallback-cache .gitignore so the cached contract is never
    # committed (ADR-0002 / ADR-0003).
    gitignore = target_dir / ".gitignore"
    entries = "\n".join(GITIGNORE_ENTRIES) + "\n"
    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")
        if ".agents/cache/" not in existing:
            sep = "" if existing.endswith("\n") else "\n"
            gitignore.write_text(existing + sep + entries, encoding="utf-8")
            copied.append(".gitignore (appended cache ignore)")
        else:
            skipped.append(".gitignore (cache ignore already present)")
    else:
        gitignore.write_text(entries, encoding="utf-8")
        copied.append(".gitignore")

    return copied, skipped
