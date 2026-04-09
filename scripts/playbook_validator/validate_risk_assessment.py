"""Risk assessment validation.

Validates that a completed risk assessment worksheet contains all 7 required
sections, valid risk scores, NIST control references, and proper sign-off.

Aligned with templates/risk-assessment.md structure.
"""

import re
from pathlib import Path

from playbook_validator.config import is_valid_nist_control

# The 7 required sections (matched against ## headings)
REQUIRED_SECTIONS = {
    "System Identification": re.compile(r"^##\s+.*System Identification", re.IGNORECASE),
    "AI Agent Identification": re.compile(r"^##\s+.*Agent Identification", re.IGNORECASE),
    "Data Classification": re.compile(r"^##\s+.*Data Classification", re.IGNORECASE),
    "Threat Analysis": re.compile(r"^##\s+.*Threat Analysis", re.IGNORECASE),
    "Control Assessment": re.compile(r"^##\s+.*Control Assessment", re.IGNORECASE),
    "Risk Treatment": re.compile(r"^##\s+.*Risk Treatment", re.IGNORECASE),
    "Acceptance and Sign-Off": re.compile(r"^##\s+.*Sign-Off", re.IGNORECASE),
}

# Pattern for threat analysis table rows: | T# | description | ref | likelihood | impact | score | ...
_THREAT_ROW_PATTERN = re.compile(
    r"^\|\s*T\d+\s*\|"  # starts with | T<number> |
)

# Pattern to extract pipe-delimited columns from a table row
_TABLE_CELL_SPLIT = re.compile(r"\s*\|\s*")

# NIST control reference anywhere in text (e.g., RA-3, AC-2, CM-7(5))
_NIST_REF_INLINE = re.compile(r"\b[A-Z]{2}-\d+(?:\(\d+\))?\b")

# Placeholder patterns that suggest unfilled template content
_PLACEHOLDER_PATTERNS = [
    re.compile(r"\[Name\]", re.IGNORECASE),
    re.compile(r"\[Signature\]", re.IGNORECASE),
    re.compile(r"\[Date\]", re.IGNORECASE),
    re.compile(r"\[Agent Name\]", re.IGNORECASE),
    re.compile(r"\[System Name\]", re.IGNORECASE),
    re.compile(r"___+"),  # Blank fill-in lines
]


def _find_section_ranges(
    lines: list[str],
) -> dict[str, tuple[int, int]]:
    """Map section names to their (start_line, end_line) ranges.

    Returns only sections that matched a REQUIRED_SECTIONS pattern.
    """
    found: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        for name, pattern in REQUIRED_SECTIONS.items():
            if pattern.search(line):
                found.append((name, i))
                break

    ranges: dict[str, tuple[int, int]] = {}
    for idx, (name, start) in enumerate(found):
        end = found[idx + 1][1] if idx + 1 < len(found) else len(lines)
        ranges[name] = (start, end)
    return ranges


def _validate_threat_scores(lines: list[str], start: int, end: int) -> list[str]:
    """Validate Likelihood and Impact scores in threat analysis table rows."""
    errors: list[str] = []
    for line in lines[start:end]:
        if not _THREAT_ROW_PATTERN.match(line):
            continue
        cells = _TABLE_CELL_SPLIT.split(line.strip())
        # cells layout after split: ['', 'T#', 'Threat', 'OWASP Ref', 'Likelihood', 'Impact', 'Risk Score', ...]
        # Filter out empties from leading/trailing pipes
        cells = [c.strip() for c in cells if c.strip()]
        if len(cells) < 6:
            continue

        threat_id = cells[0]
        likelihood_str = cells[3]
        impact_str = cells[4]

        for label, val_str in [("Likelihood", likelihood_str), ("Impact", impact_str)]:
            # Skip header-like values or empty cells
            if not val_str or val_str == label or val_str.startswith(label):
                continue
            try:
                val = int(val_str)
            except ValueError:
                errors.append(f"{threat_id}: {label} value '{val_str}' is not numeric (must be 1-5)")
                continue
            if val < 1 or val > 5:
                errors.append(f"{threat_id}: {label} value {val} is out of range (must be 1-5)")
    return errors


def _validate_nist_in_control_section(lines: list[str], start: int, end: int) -> list[str]:
    """Check that the Control Assessment section references NIST controls."""
    section_text = "\n".join(lines[start:end])
    refs = _NIST_REF_INLINE.findall(section_text)
    valid_refs = [r for r in refs if is_valid_nist_control(r)]
    if not valid_refs:
        return ["Control Assessment section has no NIST control references (expected format: XX-N, e.g., RA-3, AC-2)"]
    return []


def _validate_sign_off(lines: list[str], start: int, end: int) -> list[str]:
    """Check sign-off table for actual names vs empty or placeholder values."""
    warnings: list[str] = []
    in_sig_table = False
    sig_rows_found = 0
    unsigned_roles: list[str] = []

    for line in lines[start:end]:
        stripped = line.strip()
        # Detect the signatures table by looking for Role/Name header or role rows
        if "| Role |" in stripped or "| **System Owner**" in stripped or "| **ISSO**" in stripped:
            in_sig_table = True

        if not in_sig_table:
            continue

        # Skip separator rows
        if stripped.startswith("|") and set(stripped.replace("|", "").strip()) <= {"-", " "}:
            continue

        # Check role rows (contain ** markers)
        if stripped.startswith("|") and "**" in stripped:
            sig_rows_found += 1
            # Split on | keeping empty cells (don't filter empties)
            raw_cells = stripped.split("|")
            # raw_cells: ['', ' Role ', ' Name ', ' Signature ', ' Date ', '']
            cells = [c.strip() for c in raw_cells]
            # Remove leading/trailing empty strings from pipe boundaries
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            # cells: ['Role', 'Name', 'Signature', 'Date']
            if len(cells) >= 2:
                role = cells[0]
                name = cells[1]
                # Check for placeholder patterns
                has_placeholder = any(p.search(name) for p in _PLACEHOLDER_PATTERNS)
                if has_placeholder:
                    warnings.append(f"Sign-off has placeholder name in {role}")
                elif not name:
                    unsigned_roles.append(role)

    if unsigned_roles:
        warnings.append(f"Sign-off section appears unsigned: {', '.join(unsigned_roles)} missing name")

    return warnings


def _check_section_content_warnings(lines: list[str], section_ranges: dict[str, tuple[int, int]]) -> list[str]:
    """Generate warnings for sections that look like unfilled templates."""
    warnings: list[str] = []

    for name, (start, end) in section_ranges.items():
        section_body = "\n".join(lines[start + 1 : end]).strip()
        if not section_body:
            warnings.append(f"Section '{name}' heading present but has no content")
            continue

        # Check for placeholder patterns
        for line in lines[start + 1 : end]:
            for pat in _PLACEHOLDER_PATTERNS:
                if pat.search(line):
                    warnings.append(f"Section '{name}' appears to contain unfilled placeholder text")
                    break
            else:
                continue
            break

    return warnings


def validate_risk_assessment(path: Path) -> tuple[list[str], list[str]]:
    """Validate a risk assessment markdown file.

    Checks:
    - File exists and is non-empty
    - All 7 required sections present (## headings)
    - Risk scores (Likelihood, Impact) are numeric 1-5
    - NIST controls referenced in Control Assessment section
    - Sign-off section has name fields (not empty/placeholder)
    - Warns about sections that look like unfilled template placeholders

    Args:
        path: Path to the risk assessment markdown file.

    Returns:
        Tuple of (errors, warnings) as lists of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"File does not exist: {path}"], []

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return ["File is empty"], []

    lines = content.splitlines()

    # Check required sections
    section_ranges = _find_section_ranges(lines)
    for name in REQUIRED_SECTIONS:
        if name not in section_ranges:
            errors.append(f"Missing required section: {name}")

    # Validate threat analysis scores
    if "Threat Analysis" in section_ranges:
        start, end = section_ranges["Threat Analysis"]
        errors.extend(_validate_threat_scores(lines, start, end))

    # Validate NIST control references in Control Assessment
    if "Control Assessment" in section_ranges:
        start, end = section_ranges["Control Assessment"]
        errors.extend(_validate_nist_in_control_section(lines, start, end))

    # Validate sign-off
    if "Acceptance and Sign-Off" in section_ranges:
        start, end = section_ranges["Acceptance and Sign-Off"]
        warnings.extend(_validate_sign_off(lines, start, end))

    # Check for unfilled template content
    warnings.extend(_check_section_content_warnings(lines, section_ranges))

    return errors, warnings
