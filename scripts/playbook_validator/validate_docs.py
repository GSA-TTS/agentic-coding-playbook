"""Document frontmatter validation.

Validates that all content Markdown files have correct frontmatter
with required fields and valid enum values.
"""

import datetime
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

    _validate_freshness(path, fm, errors, warnings)

    return errors, warnings


# Freshness fields (#210). Dates are ISO YYYY-MM-DD. `review_cycle` → max age in
# days used to DERIVE staleness from `last_updated` when no explicit `stale_after`
# is set. Staleness is a WARNING (content present, just due for review); a
# malformed date is an ERROR (fail closed — a bad date must never read as fresh).
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REVIEW_CYCLE_DAYS = {"quarterly": 90, "semi-annually": 182, "annually": 365}


def _parse_iso_date(value: str) -> datetime.date | None:
    if not isinstance(value, str) or not _ISO_DATE_RE.match(value.strip()):
        return None
    try:
        return datetime.date.fromisoformat(value.strip())
    except ValueError:
        return None


def _validate_freshness(path: Path, fm: dict, errors: list[str], warnings: list[str]) -> None:
    """Validate last_updated / stale_after formats and surface staleness (#210).

    - `last_updated` and `stale_after`, when present, MUST be ISO YYYY-MM-DD;
      a malformed value is an ERROR (fail closed).
    - If `stale_after` is set and today >= it → WARNING.
    - Else if `last_updated` + `review_cycle` max-age is exceeded → WARNING.
    Staleness is advisory (warning), never a hard failure — the doc still exists.
    """
    today = datetime.date.today()

    raw_updated = fm.get("last_updated")
    updated: datetime.date | None = None
    if raw_updated is not None:
        updated = _parse_iso_date(str(raw_updated))
        if updated is None:
            errors.append(f"{path} — last_updated must be ISO YYYY-MM-DD (got {raw_updated!r})")

    raw_stale = fm.get("stale_after")
    stale_after: datetime.date | None = None
    if raw_stale is not None:
        stale_after = _parse_iso_date(str(raw_stale))
        if stale_after is None:
            errors.append(f"{path} — stale_after must be ISO YYYY-MM-DD (got {raw_stale!r})")

    if stale_after is not None:
        if today >= stale_after:
            warnings.append(
                f"{path} — content is stale: stale_after {stale_after.isoformat()} has passed; "
                "review and refresh, then bump last_updated / stale_after (#210)."
            )
        return  # explicit stale_after takes precedence over derived staleness

    # Derived staleness from last_updated + review_cycle (the prose rule in
    # AGENTS.md §13.1, now enforced as a warning).
    cycle = fm.get("review_cycle")
    if updated is not None and cycle in _REVIEW_CYCLE_DAYS:
        max_age = datetime.timedelta(days=_REVIEW_CYCLE_DAYS[cycle])
        if today - updated > max_age:
            age_days = (today - updated).days
            warnings.append(
                f"{path} — likely stale: last_updated {updated.isoformat()} is {age_days} days "
                f"old, exceeding the {cycle} review cycle ({_REVIEW_CYCLE_DAYS[cycle]} days). "
                "Review and bump last_updated, or set stale_after (#210)."
            )


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
        else:
            errors.extend(_check_contract_version_consistency(universal, fm))

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


# Prose count-drift guard (#184). Prose files copy the landscape-entry count and
# the control count; these are NOT the source of truth and drift silently (docs
# said "39 entries" while the registry held 42). Each numeric span is anchored to
# its noun so an unrelated number is never flagged.
_LANDSCAPE_ENTRIES_PROSE_RE = re.compile(r"(?<![\w.\-])(\d+)\s+entries\b")
# Count group then optional "security"/framework qualifier then "controls". The
# negative lookbehind keeps a number inside "800-53"/"Rev 5.2" out of the count
# group (mirrors index_updaters exactly so generate + guard agree).
_CONTROLS_QUALIFIER = r"(?:security\s+|NIST\s+(?:SP\s+)?800-53\s+(?:Rev\s+5(?:\.\d+)?\s+)?)?"
_CONTROLS_PROSE_RE = re.compile(rf"(?<![\w.\-])(\d+)\s+{_CONTROLS_QUALIFIER}controls\b")
# Only scan files that actually carry a catalog/control count claim. Kept as a
# small explicit list so the guard is deterministic and cheap; `make generate`
# rewrites these same spans, so a synced repo passes with zero edits.
_COUNT_PROSE_FILES = (
    "README.md",
    "docs/README.md",
    "docs/AGENT-INSTRUCTIONS.md",
    "docs/FEDERAL-AI-LANDSCAPE.md",
    "docs/SECURITY-CONTROLS.md",
    "docs/ROADMAP.md",
    "CONTEXT-GUIDE.md",
)
# Contexts where "N entries" is NOT the landscape catalog (avoid false positives).
_LANDSCAPE_CONTEXT_RE = re.compile(r"(?i)(landscape|federal ai guidance catalog|entries total)")


def validate_count_drift(root: Path) -> tuple[list[str], list[str]]:
    """Fail closed when a prose count copy disagrees with its source list (#184).

    Two source-of-truth counts are copied into prose across the repo:
    - landscape entries → ``data/federal-ai-landscape.yaml`` (``entries:`` list)
    - NIST controls → distinct rows in ``docs/SECURITY-CONTROLS.md``

    A stale copy (e.g. "39 entries" when the registry holds 42) passes the
    existing per-file integrity guards, which only check a source's internal
    consistency. This guard scans the known prose files and errors when a count
    token adjacent to its noun differs from the source length, so drift cannot
    ship even if someone forgets ``make generate``. Import kept local to avoid a
    circular dependency with generate_index.

    Returns (errors, warnings).
    """
    from playbook_validator.index_updaters import (
        count_landscape_entries,
        count_security_controls,
    )

    errors: list[str] = []
    warnings: list[str] = []

    landscape_count = count_landscape_entries(root)
    controls_count = count_security_controls(root)

    for rel in _COUNT_PROSE_FILES:
        doc = root / rel
        if not doc.is_file():
            continue
        for line in doc.read_text(encoding="utf-8").splitlines():
            if landscape_count is not None and _LANDSCAPE_CONTEXT_RE.search(line):
                for m in _LANDSCAPE_ENTRIES_PROSE_RE.finditer(line):
                    if int(m.group(1)) != landscape_count:
                        errors.append(
                            f"{rel} — prose says '{m.group(1)} entries' but the landscape "
                            f"registry has {landscape_count} (data/federal-ai-landscape.yaml). "
                            "Run `make generate` or fix the count (#184)."
                        )
            if controls_count is not None:
                for m in _CONTROLS_PROSE_RE.finditer(line):
                    if int(m.group(1)) != controls_count:
                        errors.append(
                            f"{rel} — prose says '{m.group(0).strip()}' but "
                            f"{controls_count} controls are documented in "
                            "docs/SECURITY-CONTROLS.md. Run `make generate` or fix the "
                            "count (#184)."
                        )

    return errors, warnings


# Body banner "> **Version:** X.Y.Z" in the universal contract — must agree with
# the frontmatter contract.version and config.CURRENT_CONTRACT_VERSION so the
# three copies can never drift apart again (#191).
_BANNER_VERSION_RE = re.compile(r">\s*\*\*Version:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)")


def _check_contract_version_consistency(universal: Path, fm: dict) -> list[str]:
    """The universal contract's version appears in three places: the
    ``contract.version`` frontmatter marker, the ``> **Version:**`` body banner,
    and ``config.CURRENT_CONTRACT_VERSION``. They MUST all agree (#191) — a prior
    drift (frontmatter 0.4.0 / banner 0.3.0 / config 1.0.0) meant the shipped
    thin template's ``requires_contract: ">=1.0"`` was unsatisfiable."""
    from playbook_validator.config import CURRENT_CONTRACT_VERSION

    errors: list[str] = []
    fm_version = contract_version(fm)
    if fm_version != CURRENT_CONTRACT_VERSION:
        errors.append(
            f"{universal} — contract.version ({fm_version!r}) != "
            f"config.CURRENT_CONTRACT_VERSION ({CURRENT_CONTRACT_VERSION!r}); "
            "reconcile the two (#191)."
        )
    banner = _BANNER_VERSION_RE.search(universal.read_text(encoding="utf-8"))
    if banner and banner.group(1) != fm_version:
        errors.append(
            f"{universal} — body banner Version ({banner.group(1)!r}) != "
            f"contract.version ({fm_version!r}); reconcile the two (#191)."
        )
    return errors


def validate_frontmatter_crosswalk(root: Path) -> tuple[list[str], list[str]]:
    """Every INDEX.yaml frontmatter_schema key must be crosswalked (#209, ADR 0004).

    Keeps `data/frontmatter-crosswalk.yaml` in sync with the declared schema so a
    newly-added frontmatter key must be mapped to its Dublin Core / schema.org
    equivalent deliberately, rather than drifting outside any standard. No-op if
    either file is absent. Fails closed on a schema key with no crosswalk entry.
    """
    import yaml

    index_path = root / "INDEX.yaml"
    crosswalk_path = root / "data" / "frontmatter-crosswalk.yaml"
    if not index_path.is_file() or not crosswalk_path.is_file():
        return [], []

    errors: list[str] = []
    warnings: list[str] = []

    index = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    schema = index.get("frontmatter_schema", {}) or {}
    schema_keys = set(schema.get("required", []) or []) | set(schema.get("optional", []) or [])

    crosswalk = yaml.safe_load(crosswalk_path.read_text(encoding="utf-8")) or {}
    mapped_keys = {entry.get("key") for entry in (crosswalk.get("crosswalk", []) or []) if isinstance(entry, dict)}

    for key in sorted(schema_keys - mapped_keys):
        errors.append(
            f"data/frontmatter-crosswalk.yaml — frontmatter key '{key}' is declared in "
            "INDEX.yaml frontmatter_schema but has no crosswalk entry. Add its Dublin "
            "Core / schema.org mapping (#209, ADR 0004)."
        )
    for key in sorted(mapped_keys - schema_keys):
        warnings.append(
            f"data/frontmatter-crosswalk.yaml — crosswalk entry '{key}' is not in "
            "INDEX.yaml frontmatter_schema (stale mapping?)."
        )

    return errors, warnings
