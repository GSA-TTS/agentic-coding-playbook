#!/usr/bin/env python3
"""Validate a generated AGENTS.md against required sections.

Usage:
    python3 validate-agents-md.py <agents-md-path>

Outputs structured JSON with pass/fail results.
Exit code: 0 if all checks pass, 1 if any check fails.
"""

import json
import re
import sys
from pathlib import Path

MAX_FILE_SIZE = 1024 * 500  # 500KB

REQUIRED_SECTIONS = [
    "Core Principles",
    "Project Context",
    "Agent Identity",
    "Permitted Actions",
    "Actions Requiring Approval",
    "Prohibited Actions",
    "Data Handling",
    "Coding Standards",
    "Dependencies",
    "Testing Requirements",
    "CI/CD Pipeline",
    "Incident Response",
    "Contacts",
]

REQUIRED_FIELDS = [
    ("System:", "System name in header"),
    ("Impact Level:", "FIPS impact level in header"),
    ("Agency:", "Agency name in header"),
    ("Language", "Programming language in Project Context"),
    ("Data Classification:", "Data classification in Project Context"),
]


def validate(file_path: str) -> dict:
    """Validate an AGENTS.md file."""
    resolved = Path(file_path).resolve()
    results = []
    warnings = []
    errors = []

    # Check file exists
    if not resolved.is_file():
        return {
            "status": "error",
            "results": [],
            "warnings": [],
            "errors": [f"File not found: {file_path}"],
        }

    # Check file size
    size = resolved.stat().st_size
    if size > MAX_FILE_SIZE:
        return {
            "status": "error",
            "results": [],
            "warnings": [],
            "errors": [f"File too large: {size} bytes (max {MAX_FILE_SIZE})"],
        }

    try:
        content = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "status": "error",
            "results": [],
            "warnings": [],
            "errors": ["File is not valid UTF-8"],
        }

    # Check required sections (## headings)
    for section in REQUIRED_SECTIONS:
        pattern = rf"^## {re.escape(section)}"
        if re.search(pattern, content, re.MULTILINE):
            results.append({"check": f"section:{section}", "pass": True})
        else:
            results.append(
                {
                    "check": f"section:{section}",
                    "pass": False,
                    "suggestion": f"Add '## {section}' section",
                }
            )

    # Check required fields appear somewhere in content
    for field, desc in REQUIRED_FIELDS:
        if field in content:
            results.append({"check": f"field:{desc}", "pass": True})
        else:
            results.append(
                {
                    "check": f"field:{desc}",
                    "pass": False,
                    "suggestion": f"Add {desc} to the document",
                }
            )

    # Check for unfilled placeholders
    placeholders = re.findall(r"\[(?:Your |Specify |Name|Agency|Add )[^\]]*\]", content)
    if placeholders:
        unique = list(set(placeholders))[:10]
        warnings.append(f"Found {len(placeholders)} unfilled placeholder(s): {', '.join(unique)}")

    # Check priority order is correct
    if "safety > correctness > compliance > simplicity > performance" not in content:
        warnings.append("Core Principles priority order may be missing or modified")

    # Check for prohibited actions section content
    prohibited_section = re.search(
        r"## Prohibited Actions\n(.*?)(?=\n---|\n## |\Z)",
        content,
        re.DOTALL,
    )
    if prohibited_section:
        prohibited_text = prohibited_section.group(1)
        must_have = ["secrets", "security controls", "classified"]
        for term in must_have:
            if term.lower() not in prohibited_text.lower():
                warnings.append(f"Prohibited Actions may be missing standard prohibition: {term}")

    # Calculate pass/fail
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = sum(1 for r in results if not r["pass"])

    status = "success"
    if fail_count > 0:
        status = "partial"
    if errors:
        status = "failure"

    return {
        "status": status,
        "passed": pass_count,
        "failed": fail_count,
        "results": results,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: validate-agents-md.py <agents-md-path>", file=sys.stderr)
        sys.exit(1)

    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))

    if result["status"] == "failure" or result.get("failed", 0) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
