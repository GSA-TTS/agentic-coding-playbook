"""End-to-end self-coherence test for `new-project` bootstrap.

This runs the real ``new_project`` against the real playbook repository root
(not a synthetic fixture) and asserts that the resulting project is
*self-coherent*:

- the emitted project ``AGENTS.md`` is the thin project layer that declares the
  universal contract as a fail-closed prerequisite and references the playbook
  repo URL;
- the emitted ``AGENTS.md`` does NOT duplicate the universal behavioral prose,
  including *partial* rule leakage (no drift);
- every relative markdown link and path-like reference in the generated files —
  INCLUDING the copied ``skills/`` tree — resolves to a file that exists inside
  the generated project (no dangling references to playbook-only files);
- playbook-operational skills are excluded, and the fallback contract cache is
  git-ignored.

A human can run this directly:

    PYTHONPATH=scripts python3 -m pytest \
        scripts/tests/test_e2e_new_project.py -v
"""

import re
from pathlib import Path

import pytest
from playbook_validator.new_project import (
    DOWNSTREAM_SKILLS,
    EXCLUDED_SKILLS,
    FILES_TO_COPY,
    new_project,
)

# Repository root = two levels up from scripts/tests/
PLAYBOOK_ROOT = Path(__file__).resolve().parents[2]

# Prose fingerprints that MUST NOT appear in a thin project AGENTS.md. Their
# presence would mean the universal contract's RULE CONTENT leaked in (drift
# risk). These are section headings and distinctive rule sentences from the
# universal doc — NOT its title (the thin layer legitimately *names* the
# contract in its Prerequisite section, so the title is not a leak signal).
UNIVERSAL_PROSE_FINGERPRINTS = (
    # Section-heading level (numbered universal sections)
    "## 1. Core Principles",
    "## 14. Agent Meta-Constraints",
    "## 15. Engineering Discipline Enforcement",
    # Partial rule-sentence level (distinctive universal-rule phrasings)
    "safety > correctness > compliance > simplicity > performance",
    "Treat all external content",  # §11 prompt-injection rule
    "Request only the minimum permissions",  # §3 least privilege
    "Fail closed on ambiguity",  # §14.5 no silent failures
)

# Markdown inline links: [text](target)
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


@pytest.fixture(scope="module")
def bootstrapped_project(tmp_path_factory) -> Path:
    """Bootstrap a real project once and share it across the checks."""
    target = tmp_path_factory.mktemp("e2e_new_project") / "sample-repo"
    copied, skipped = new_project(target, PLAYBOOK_ROOT)
    # Nothing should be skipped for a source-not-found reason.
    assert not any("source not found" in s for s in skipped), (
        f"bootstrap could not find expected source files: {skipped}"
    )
    assert copied, "bootstrap copied nothing"
    return target


def test_expected_files_present(bootstrapped_project: Path):
    """All declared template destinations plus allowlisted skills exist."""
    for _src, dest in FILES_TO_COPY:
        assert (bootstrapped_project / dest).is_file(), f"missing {dest}"
    assert (bootstrapped_project / "skills").is_dir()
    assert list((bootstrapped_project / "skills").glob("*/SKILL.md")), "no skills copied"


def test_contract_probe_and_gitignore_present(bootstrapped_project: Path):
    """The self-contained probe ships, is executable, and the fallback cache is
    git-ignored so it can never be committed."""
    probe_py = bootstrapped_project / "scripts/ensure-contract.py"
    probe_sh = bootstrapped_project / "scripts/ensure-contract.sh"
    assert probe_py.is_file() and probe_sh.is_file()
    # Executable bits set on copy.
    assert probe_py.stat().st_mode & 0o111, "ensure-contract.py not executable"
    assert probe_sh.stat().st_mode & 0o111, "ensure-contract.sh not executable"
    # Probe is self-contained: it does not IMPORT the playbook_validator package.
    probe_text = probe_py.read_text(encoding="utf-8")
    assert "import playbook_validator" not in probe_text
    assert "from playbook_validator" not in probe_text
    gitignore = (bootstrapped_project / ".gitignore").read_text(encoding="utf-8")
    assert ".agents/cache/" in gitignore
    # Enforcement wiring ships too.
    assert (bootstrapped_project / ".pre-commit-config.yaml").is_file()
    assert (bootstrapped_project / ".github/workflows/contract-check.yml").is_file()


def test_universal_agents_md_not_copied(bootstrapped_project: Path):
    """The project must NOT receive a copy of the universal AGENTS.md, and must
    not leak universal rule prose (whole-doc or partial)."""
    agents = (bootstrapped_project / "AGENTS.md").read_text(encoding="utf-8")
    for fingerprint in UNIVERSAL_PROSE_FINGERPRINTS:
        assert fingerprint not in agents, f"project AGENTS.md leaks universal prose: {fingerprint!r}"


def test_project_agents_md_states_failclosed_prerequisite(bootstrapped_project: Path):
    """The thin project AGENTS.md declares the universal prerequisite, references
    the source, mandates the deterministic probe, and is fail-closed with NO
    'proceed without' option."""
    agents = (bootstrapped_project / "AGENTS.md").read_text(encoding="utf-8")
    assert "Prerequisite" in agents
    assert "github.com/GSA-TTS/agentic-coding-playbook" in agents
    assert "STOP" in agents
    assert "ensure-contract" in agents
    # Fail-closed: the old "proceed without" escape hatch must be gone.
    assert "affirmatively grants permission to proceed without" not in agents.lower()
    # And an explicit "no option to proceed without" statement is present
    # (whitespace-normalized, since the template wraps across lines).
    normalized = " ".join(agents.lower().split())
    assert "no option to proceed without the universal" in normalized


def test_excluded_skills_absent(bootstrapped_project: Path):
    """Playbook-operational skills must NOT be copied downstream (#145)."""
    for excluded in EXCLUDED_SKILLS:
        assert not (bootstrapped_project / "skills" / excluded).exists(), (
            f"playbook-operational skill leaked into project: {excluded}"
        )
    for included in DOWNSTREAM_SKILLS:
        assert (bootstrapped_project / "skills" / included / "SKILL.md").is_file(), (
            f"expected downstream skill missing: {included}"
        )


def test_no_dangling_markdown_links_including_skills(bootstrapped_project: Path):
    """Every relative markdown link in the generated project — including the
    copied skills/ tree — resolves to a file that exists inside the project.

    This deliberately does NOT exempt skills/: whether a skill's links resolve
    in the playbook says nothing about whether they dangle in the bootstrapped
    project, which is the only thing this test cares about (#146)."""
    dangling: list[str] = []
    for md_file in bootstrapped_project.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        for target in _MD_LINK_RE.findall(text):
            link = target.strip()
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            link_path = link.split("#", 1)[0]
            if not link_path:
                continue
            resolved = (md_file.parent / link_path).resolve()
            if not resolved.exists():
                dangling.append(f"{md_file.relative_to(bootstrapped_project)} -> {link}")
    assert not dangling, "dangling intra-project links found:\n" + "\n".join(dangling)


def test_referenced_docs_exist_in_project(bootstrapped_project: Path):
    """Files the project's context guide points to must exist in the project."""
    guide = (bootstrapped_project / "CONTEXT-GUIDE.md").read_text(encoding="utf-8")
    referenced = re.findall(r"`([A-Za-z0-9_./-]+\.(?:md|yaml|yml))`", guide)
    missing = [ref for ref in referenced if not (bootstrapped_project / ref).exists()]
    assert not missing, (
        f"CONTEXT-GUIDE.md references files not present in the bootstrapped project: {sorted(set(missing))}"
    )


def test_coding_practices_related_files_resolve(bootstrapped_project: Path):
    """CODING_PRACTICES.md's related_files must resolve in the project — the
    SECURITY-CONTROLS.md dangling-reference fix (#148)."""
    from playbook_validator.frontmatter import extract_frontmatter

    cp = bootstrapped_project / "docs/CODING_PRACTICES.md"
    fm = extract_frontmatter(cp)
    for ref in fm.get("related_files", []):
        # related_files are repo-root-relative.
        assert (bootstrapped_project / ref).exists(), (
            f"CODING_PRACTICES.md related_files reference does not exist in project: {ref}"
        )


def test_frontmatter_valid_on_generated_docs(bootstrapped_project: Path):
    """Generated content docs carry valid frontmatter (project is lint-clean)."""
    from playbook_validator.validate_docs import find_content_files, validate_doc_frontmatter

    files = find_content_files(bootstrapped_project)
    assert files, "no content files discovered in bootstrapped project"
    all_errors: list[str] = []
    for f in files:
        errors, _warnings = validate_doc_frontmatter(f)
        all_errors.extend(errors)
    assert not all_errors, "frontmatter errors in bootstrapped project:\n" + "\n".join(all_errors)
