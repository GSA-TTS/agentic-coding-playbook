"""Document frontmatter validation.

Validates that all content Markdown files have correct frontmatter
with required fields and valid enum values.
"""

import re
from pathlib import Path

from playbook_validator.config import (
    CONTRACT_REQUIRES_KEY,
    CONTRACT_ROLE_KEY,
    CONTRACT_ROLE_UNIVERSAL,
    CONTRACT_ROLE_VALUES,
    CONTRACT_VERSION_KEY,
    DOC_LOAD_PRIORITY_VALUES,
    DOC_STATUS_VALUES,
    DOC_TIER_VALUES,
    REQUIRED_FRONTMATTER_FIELDS,
    contract_block,
    contract_role,
    contract_version,
)
from playbook_validator.frontmatter import extract_frontmatter

# Files excluded from frontmatter validation
EXCLUDED_FILENAMES = frozenset(
    {
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "SUPPORT.md",
        "GOVERNANCE.md",
        "LICENSE",
        "TRANSFER.md",
    }
)

# Directories excluded from content file discovery
EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".github",
        ".claude",
        "node_modules",
        "skills",
        "data",
        "templates",
        "decisions",
    }
)


def find_content_files(root: Path) -> list[Path]:
    """Find all Markdown content files that need frontmatter validation.

    Excludes meta-files (README, CONTRIBUTING, etc.), skills directory,
    and hidden/build directories.
    """
    results: list[Path] = []
    for md_file in sorted(root.rglob("*.md")):
        # Skip excluded directories
        parts = md_file.relative_to(root).parts
        if any(part in EXCLUDED_DIRS for part in parts):
            continue
        # Skip excluded filenames
        if md_file.name in EXCLUDED_FILENAMES:
            continue
        results.append(md_file)
    return results


def validate_doc_frontmatter(path: Path) -> tuple[list[str], list[str]]:
    """Validate frontmatter of a single document.

    Returns (errors, warnings) as lists of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    fm = extract_frontmatter(path)
    if not fm:
        errors.append(f"{path} — missing YAML frontmatter")
        return errors, warnings

    # Required fields
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fm:
            errors.append(f"{path} — missing required field: {field}")

    # Status validation
    status = fm.get("status")
    if status is not None and status not in DOC_STATUS_VALUES:
        errors.append(f"{path} — invalid status: '{status}' (must be one of {sorted(DOC_STATUS_VALUES)})")

    # Tier validation
    tier = fm.get("tier")
    if tier is not None and tier not in DOC_TIER_VALUES:
        errors.append(f"{path} — invalid tier: '{tier}' (must be one of {sorted(DOC_TIER_VALUES)})")

    # Load priority validation (optional field)
    load_priority = fm.get("load_priority")
    if load_priority is not None and load_priority not in DOC_LOAD_PRIORITY_VALUES:
        errors.append(
            f"{path} — invalid load_priority: '{load_priority}' (must be one of {sorted(DOC_LOAD_PRIORITY_VALUES)})"
        )

    # Behavioral-contract block validation (optional). When present it must be a
    # mapping with a recognized role; the universal-vs-thin invariant is checked
    # in validate_contract_role() at the repository level.
    raw_block = fm.get("contract")
    if raw_block is not None:
        if not isinstance(raw_block, dict):
            errors.append(f"{path} — 'contract' must be a mapping (got {type(raw_block).__name__})")
        else:
            block = contract_block(fm)
            role = contract_role(fm)
            if role is not None and role not in CONTRACT_ROLE_VALUES:
                errors.append(
                    f"{path} — invalid contract.{CONTRACT_ROLE_KEY}: '{role}' "
                    f"(must be one of {sorted(CONTRACT_ROLE_VALUES)})"
                )
            # A universal contract MUST carry a version; a project-layer SHOULD
            # declare which contract versions it requires.
            if role == CONTRACT_ROLE_UNIVERSAL and not contract_version(fm):
                errors.append(f"{path} — universal contract must declare contract.{CONTRACT_VERSION_KEY}")
            for vkey in (CONTRACT_VERSION_KEY, CONTRACT_REQUIRES_KEY):
                vval = block.get(vkey)
                if vval is not None and (not isinstance(vval, str) or not vval.strip()):
                    errors.append(f"{path} — contract.{vkey} must be a non-empty string")

    return errors, warnings


# Control-overlay body rows look like: | **AC-2** | Account Management | ...
# One row per NIST control documented in docs/SECURITY-CONTROLS.md.
_CONTROL_ROW_RE = re.compile(r"^\|\s*\*\*([A-Z]{2}-\d{1,2})\*\*\s*\|", re.MULTILINE)
_SECURITY_CONTROLS_REL = "docs/SECURITY-CONTROLS.md"


def validate_security_controls_count(root: Path) -> tuple[list[str], list[str]]:
    """Assert SECURITY-CONTROLS.md frontmatter matches its documented controls.

    The frontmatter ``nist_controls`` array is what machine consumers (INDEX.yaml,
    traceability) read; the body has one ``| **XX-N** |`` table row per control.
    If they diverge, consumers get a wrong count and the prose "N controls" claim
    drifts (issue #121). This guard fails closed so the two can never silently
    disagree again. It also flags an inline "N controls" prose count that no
    longer matches.

    Returns (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    doc = root / _SECURITY_CONTROLS_REL
    if not doc.is_file():
        # Not every consumer repo ships this doc; absence is not an error here.
        return errors, warnings

    text = doc.read_text(encoding="utf-8")
    fm = extract_frontmatter(doc) or {}
    fm_controls = fm.get("nist_controls") or []
    fm_count = len(fm_controls)

    # Body: distinct controls that actually have a documented row.
    body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
    body_controls = sorted(set(_CONTROL_ROW_RE.findall(body)))
    body_count = len(body_controls)

    if fm_count != body_count:
        fm_set, body_set = set(fm_controls), set(body_controls)
        only_fm = sorted(fm_set - body_set)
        only_body = sorted(body_set - fm_set)
        detail = []
        if only_fm:
            detail.append(f"in frontmatter but not documented: {only_fm}")
        if only_body:
            detail.append(f"documented but not in frontmatter: {only_body}")
        errors.append(
            f"{doc} — nist_controls count ({fm_count}) != documented control rows "
            f"({body_count}). {'; '.join(detail) if detail else 'counts differ'}. "
            "Reconcile the frontmatter array with the body table (issue #121)."
        )

    # Advisory: an inline "N controls" prose claim that disagrees with the truth.
    for m in re.finditer(r"(\d+)\s+controls\b", text):
        claimed = int(m.group(1))
        if claimed != body_count:
            warnings.append(
                f"{doc} — prose says '{claimed} controls' but {body_count} are "
                f"documented; update the prose to match (issue #121)."
            )
            break

    return errors, warnings


# Paths (repo-root-relative) that MUST NOT claim the canonical universal role —
# they are thin project layers that only *reference* the universal contract.
_THIN_LAYER_PATHS = (
    "templates/AGENTS.md.template",
    "examples/AGENTS.md.example",
)


def validate_contract_role(root: Path) -> tuple[list[str], list[str]]:
    """Enforce the canonical-designation invariant across the repository.

    The universal behavioral contract (repo-root ``AGENTS.md``) MUST declare a
    structured ``contract`` block with ``role: universal`` and a ``version`` so
    tooling recognizes it by an explicit, versioned marker (issue #151,
    ADR-0003). The thin project layers (template and example) MUST NOT claim the
    universal role — otherwise a bootstrapped project's own AGENTS.md could
    self-satisfy the contract probe.

    Returns (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    universal = root / "AGENTS.md"
    if universal.is_file():
        fm = extract_frontmatter(universal)
        role = contract_role(fm)
        if role != CONTRACT_ROLE_UNIVERSAL:
            errors.append(
                f"{universal} — universal contract MUST declare contract.{CONTRACT_ROLE_KEY}: "
                f"{CONTRACT_ROLE_UNIVERSAL} (found: {role!r})"
            )
        elif not contract_version(fm):
            errors.append(f"{universal} — universal contract MUST declare contract.{CONTRACT_VERSION_KEY}")

    for rel in _THIN_LAYER_PATHS:
        thin = root / rel
        if not thin.is_file():
            continue
        role = contract_role(extract_frontmatter(thin))
        if role == CONTRACT_ROLE_UNIVERSAL:
            errors.append(
                f"{thin} — thin project layer MUST NOT declare contract.{CONTRACT_ROLE_KEY}: "
                f"{CONTRACT_ROLE_UNIVERSAL} (only the universal contract may); this would let a "
                "bootstrapped project self-satisfy the contract probe (#151)"
            )

    return errors, warnings
