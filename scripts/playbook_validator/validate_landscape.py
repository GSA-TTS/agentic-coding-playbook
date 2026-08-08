"""Federal AI landscape registry validation.

Validates data/federal-ai-landscape.yaml structure, field values,
cross-references, and entry count consistency.
"""

import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

VALID_CATEGORIES = frozenset(
    {
        "executive_order",
        "omb_memo",
        "nist_standard",
        "legislation",
        "agency_strategy",
        "agency_report",
        "industry_standard",
        "white_house_plan",
    }
)
VALID_STATUSES = frozenset({"active", "revoked", "rescinded", "draft", "final"})
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED_FIELDS = frozenset({"id", "title", "category", "source", "date", "status", "relevance", "url"})

LIST_REF_FIELDS = ("revokes", "replaces", "implemented_by")
SINGLE_REF_FIELDS = ("revoked_by", "replaced_by", "implements")


def validate_landscape(path: Path) -> tuple[list[str], list[str], int]:
    """Validate a federal AI landscape YAML registry.

    Returns (errors, warnings, entry_count) as lists of human-readable messages
    and the number of entries found.
    """
    errors: list[str] = []
    warnings: list[str] = []

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors, warnings, 0

    if not data or "entries" not in data:
        errors.append("Missing 'entries' key in YAML")
        return errors, warnings, 0

    if not isinstance(data["entries"], list):
        errors.append("'entries' must be a list")
        return errors, warnings, 0

    entries: list[dict[str, Any]] = data["entries"]

    # Collect all IDs
    all_ids: set[str] = set()
    id_counts: Counter[str] = Counter()
    for entry in entries:
        eid = entry.get("id", "<missing>")
        all_ids.add(eid)
        id_counts[eid] += 1

    # Duplicate IDs
    for eid, count in id_counts.items():
        if count > 1:
            errors.append(f"Duplicate ID: {eid} (appears {count} times)")

    # Validate each entry
    for i, entry in enumerate(entries):
        entry_id = entry.get("id", f"entry[{i}]")
        prefix = f"[{entry_id}]"

        for field in REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"{prefix} missing required field: {field}")

        cat = entry.get("category", "")
        if cat and cat not in VALID_CATEGORIES:
            errors.append(f"{prefix} invalid category: {cat}")

        status = entry.get("status", "")
        if status and status not in VALID_STATUSES:
            errors.append(f"{prefix} invalid status: {status}")

        date = entry.get("date", "")
        if date and not DATE_PATTERN.match(str(date)):
            errors.append(f"{prefix} invalid date format: {date} (expected YYYY-MM-DD)")

        url = entry.get("url", "")
        if url and not str(url).startswith("http"):
            errors.append(f"{prefix} URL does not start with http: {url}")

        # Cross-reference validation
        for ref_field in LIST_REF_FIELDS:
            refs = entry.get(ref_field, [])
            if isinstance(refs, str):
                refs = [refs]
            for ref in refs:
                if ref not in all_ids:
                    warnings.append(f"{prefix} {ref_field} references unknown ID: {ref}")

        for ref_field in SINGLE_REF_FIELDS:
            ref = entry.get(ref_field, "")
            if ref and ref not in all_ids:
                warnings.append(f"{prefix} {ref_field} references unknown ID: {ref}")

    # Entry count check
    declared = data.get("total_entries", 0)
    actual = len(entries)
    if declared != actual:
        errors.append(f"total_entries declares {declared} but found {actual} entries")

    return errors, warnings, actual


def validate_landscape_doc_summary(root: Path) -> list[str]:
    """Guard the generated blocks in docs/FEDERAL-AI-LANDSCAPE.md (#142).

    Fails closed if the Status Summary table or the Playbook Phase Mapping table
    (between their ``GENERATED:LANDSCAPE_SUMMARY`` / ``GENERATED:LANDSCAPE_PHASES``
    markers) disagrees with what the YAML registry would generate — so the doc
    can't drift even if hand-edited or `make generate` is skipped. No-op for a
    block whose markers are absent. Returns a list of error strings.
    """
    doc = root / "docs" / "FEDERAL-AI-LANDSCAPE.md"
    if not doc.is_file():
        return []
    text = doc.read_text(encoding="utf-8")

    from playbook_validator.index_updaters import (
        compute_landscape_summary,
        compute_phase_mapping,
        render_landscape_summary_table,
        render_phase_mapping_table,
    )

    errors: list[str] = []

    summary = compute_landscape_summary(root)
    if summary is not None:
        expected = render_landscape_summary_table(summary[0])
        errors += _check_generated_block(doc, text, "LANDSCAPE_SUMMARY", expected, "Status Summary table")

    mapping = compute_phase_mapping(root)
    if mapping is not None:
        expected = render_phase_mapping_table(mapping)
        errors += _check_generated_block(doc, text, "LANDSCAPE_PHASES", expected, "Playbook Phase Mapping table")

    return errors


def _check_generated_block(doc: Path, text: str, marker_id: str, expected: str, label: str) -> list[str]:
    """Compare the body between GENERATED:<marker_id> markers to ``expected``."""
    start = f"<!-- GENERATED:{marker_id}:START"
    end = f"<!-- GENERATED:{marker_id}:END -->"
    if start not in text or end not in text:
        return []  # markers not adopted — not this guard's job to require them
    block = text.split(start, 1)[1].split(end, 1)[0]
    body = block.split("\n", 1)[1].strip() if "\n" in block else ""
    if body != expected.strip():
        return [f"{doc} — {label} is out of sync with data/federal-ai-landscape.yaml. Run `make generate` (#142)."]
    return []
