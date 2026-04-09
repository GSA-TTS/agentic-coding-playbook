"""ADR (Architecture Decision Record) validation.

Validates that all NNNN-*.md files in a decisions directory have correct
frontmatter, valid field values, proper naming conventions, and consistent
cross-references.

Replaces skills/federal-decision-records/scripts/validate-adrs.sh.
"""

import re
from collections import Counter
from pathlib import Path

from playbook_validator.config import (
    ADR_FILENAME_PATTERN,
    ADR_STATUS_VALUES,
    REQUIRED_ADR_FIELDS,
    is_valid_nist_control,
)
from playbook_validator.frontmatter import extract_frontmatter

# Pattern to match ADR filenames: exactly 4 digits followed by hyphen
_ADR_GLOB = "[0-9][0-9][0-9][0-9]-*.md"

# Date format: YYYY-MM-DD
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Optional fields that produce warnings when absent
_OPTIONAL_ADR_FIELDS = ("category", "impact_level", "ato_relevance")


def find_adr_files(adr_dir: Path) -> list[Path]:
    """Find all ADR files matching NNNN-*.md in a directory.

    Returns files sorted by name. Only searches the top-level directory
    (no recursion).
    """
    return sorted(adr_dir.glob(_ADR_GLOB))


def validate_adr(path: Path) -> tuple[list[str], list[str]]:
    """Validate a single ADR file.

    Checks:
    - Has YAML frontmatter
    - Required fields present (title, status, date, nist_controls)
    - Status is a valid ADR status value
    - NIST control IDs match expected format
    - Date is in YYYY-MM-DD format
    - Filename follows NNNN-lowercase-with-hyphens.md convention
    - Superseded ADRs have a superseded_by field

    Returns (errors, warnings) as lists of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []
    filename = path.name

    fm = extract_frontmatter(path)
    if not fm:
        errors.append(f"{filename} -- missing YAML frontmatter")
        return errors, warnings

    # Required fields
    for field in REQUIRED_ADR_FIELDS:
        if field not in fm:
            errors.append(f"{filename} -- missing required field: {field}")

    # Status validation
    status = fm.get("status")
    if status is not None and status not in ADR_STATUS_VALUES:
        errors.append(f"{filename} -- invalid status: '{status}' (must be one of {sorted(ADR_STATUS_VALUES)})")

    # Date format validation
    date_val = fm.get("date")
    if date_val is not None:
        date_str = str(date_val)
        if not _DATE_PATTERN.match(date_str):
            errors.append(f"{filename} -- invalid date format: '{date_val}' (expected YYYY-MM-DD)")

    # NIST control format validation
    controls = fm.get("nist_controls")
    if controls is not None and isinstance(controls, list):
        for ctrl in controls:
            ctrl_str = str(ctrl).strip()
            if not is_valid_nist_control(ctrl_str):
                errors.append(f"{filename} -- invalid NIST control format: {ctrl_str}")

    # Filename convention
    if not ADR_FILENAME_PATTERN.match(filename):
        errors.append(f"{filename} -- filename should match NNNN-lowercase-title.md")

    # Superseded records must reference the superseding record
    if status == "superseded":
        superseded_by = fm.get("superseded_by")
        if not superseded_by:
            errors.append(f"{filename} -- status is superseded but missing superseded_by field")

    # Optional field warnings
    for field in _OPTIONAL_ADR_FIELDS:
        if field not in fm:
            warnings.append(f"{filename} -- missing optional field: {field}")

    return errors, warnings


def validate_adr_directory(adr_dir: Path) -> tuple[list[str], list[str]]:
    """Validate all ADRs in a directory, including cross-references.

    Checks everything from validate_adr() plus:
    - No duplicate ADR numbers
    - superseded_by references point to existing files

    Returns (errors, warnings) as lists of human-readable messages.
    """
    all_errors: list[str] = []
    all_warnings: list[str] = []

    adr_files = find_adr_files(adr_dir)
    if not adr_files:
        return all_errors, all_warnings

    # Check for duplicate ADR numbers
    numbers = [f.name.split("-", 1)[0] for f in adr_files]
    for number, count in Counter(numbers).items():
        if count > 1:
            all_errors.append(f"Duplicate ADR number: {number}")

    # Validate each file and collect cross-reference checks
    existing_filenames = {f.name for f in adr_files}

    for adr_file in adr_files:
        file_errors, file_warnings = validate_adr(adr_file)
        all_errors.extend(file_errors)
        all_warnings.extend(file_warnings)

        # Cross-reference: superseded_by must point to existing file
        fm = extract_frontmatter(adr_file)
        if fm.get("status") == "superseded":
            ref = fm.get("superseded_by")
            if ref and ref not in existing_filenames:
                all_errors.append(f"{adr_file.name} -- superseded_by references non-existent file: {ref}")

    return all_errors, all_warnings
