"""End-to-end self-coherence test for `new-project` bootstrap.

This runs the real ``new_project`` against the real playbook repository root
(not a synthetic fixture) and asserts that the resulting project is
*self-coherent*:

- the emitted project ``AGENTS.md`` is the thin project layer that declares the
  universal contract as a prerequisite, references the playbook repo URL, and
  requires the user's affirmative permission to proceed when the universal
  contract is unavailable;
- the emitted ``AGENTS.md`` does NOT duplicate the universal behavioral prose
  (no drift);
- every relative markdown link and every path-like reference in the generated
  files resolves to a file that actually exists inside the generated project
  (no dangling references to playbook-only files).

A human can run this directly:

    PYTHONPATH=scripts python3 -m pytest \
        scripts/tests/test_e2e_new_project.py -v
"""

import re
from pathlib import Path

import pytest
from playbook_validator.new_project import FILES_TO_COPY, new_project

# Repository root = two levels up from scripts/tests/
PLAYBOOK_ROOT = Path(__file__).resolve().parents[2]

# Universal-prose fingerprints that MUST NOT appear in a thin project AGENTS.md.
# Their presence would mean the universal contract was copied in (drift risk).
UNIVERSAL_PROSE_FINGERPRINTS = (
    "Federal AI Agent Behavioral Best Practices",  # universal doc title
    "## 1. Core Principles",
    "## 14. Agent Meta-Constraints",
    "## 15. Engineering Discipline Enforcement",
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
    """All declared template destinations plus skills/ exist in the project."""
    for _src, dest in FILES_TO_COPY:
        assert (bootstrapped_project / dest).is_file(), f"missing {dest}"
    assert (bootstrapped_project / "skills").is_dir()
    assert list((bootstrapped_project / "skills").glob("*/SKILL.md")), "no skills copied"


def test_universal_agents_md_not_copied(bootstrapped_project: Path):
    """The project must NOT receive a copy of the universal AGENTS.md."""
    agents = (bootstrapped_project / "AGENTS.md").read_text(encoding="utf-8")
    for fingerprint in UNIVERSAL_PROSE_FINGERPRINTS:
        assert fingerprint not in agents, f"project AGENTS.md appears to duplicate universal prose: {fingerprint!r}"


def test_project_agents_md_states_prerequisite(bootstrapped_project: Path):
    """The thin project AGENTS.md self-documents the universal prerequisite,
    points to the repo URL, and requires affirmative permission to proceed."""
    agents = (bootstrapped_project / "AGENTS.md").read_text(encoding="utf-8")
    assert "Prerequisite" in agents
    assert "github.com/GSA-TTS/agentic-coding-playbook" in agents
    assert "STOP" in agents
    assert "affirmatively" in agents.lower()


def test_no_dangling_markdown_links(bootstrapped_project: Path):
    """Every relative markdown link in the generated project's own docs resolves
    to a file that exists inside the project (no links to playbook-only paths).

    Scope: the top-level docs that new-project authors/emits from templates. The
    vendored ``skills/`` tree is maintained wholesale by the playbook and may
    reference playbook-internal data files; those are validated in the playbook
    repo itself, not here.
    """
    project_docs = [bootstrapped_project / dest for _src, dest in FILES_TO_COPY if dest.endswith(".md")]
    dangling: list[str] = []
    for md_file in project_docs:
        text = md_file.read_text(encoding="utf-8")
        for target in _MD_LINK_RE.findall(text):
            link = target.strip()
            # Skip external, anchor, and mail links.
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Strip any anchor fragment.
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
    # Backtick-quoted repo-relative paths, e.g. `docs/CODING_PRACTICES.md`.
    referenced = re.findall(r"`([A-Za-z0-9_./-]+\.(?:md|yaml|yml))`", guide)
    missing = [ref for ref in referenced if not (bootstrapped_project / ref).exists()]
    assert not missing, (
        f"CONTEXT-GUIDE.md references files not present in the bootstrapped project: {sorted(set(missing))}"
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
