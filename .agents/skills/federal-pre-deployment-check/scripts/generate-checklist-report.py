#!/usr/bin/env python3
"""Generate a completed pre-deployment checklist report from check results.

Usage:
    python3 generate-checklist-report.py \
        --automated-results automated.json \
        --manual-results manual.json \
        --system-name "My System" \
        --output completed-checklist.md

automated.json: Output from run-checks.sh
manual.json: Agent-collected manual verification results

If --output is omitted, writes to stdout.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

MAX_FILE_SIZE = 1024 * 100  # 100KB

# All 58 checklist items with their categories
CHECKLIST_ITEMS = {
    "1.1": ("Code Review and Provenance", "All AI-generated code reviewed by human (not prompter)"),
    "1.2": ("Code Review and Provenance", "AI attribution in commit history"),
    "1.3": ("Code Review and Provenance", "Standard PR/review process followed"),
    "1.4": ("Code Review and Provenance", "No direct commits to protected branches"),
    "1.5": ("Code Review and Provenance", "Reviewer understands code and verified behavior"),
    "2.1": ("Secrets and Credentials", "No secrets in source code"),
    "2.2": ("Secrets and Credentials", "No secrets in committed config"),
    "2.3": ("Secrets and Credentials", "No secrets in CI/CD definitions"),
    "2.4": ("Secrets and Credentials", "No internal network info exposed"),
    "2.5": ("Secrets and Credentials", "Secrets scanning hook active"),
    "2.6": ("Secrets and Credentials", "Credentials from approved secrets management"),
    "3.1": ("Input Validation and Output Encoding", "External input validated"),
    "3.2": ("Input Validation and Output Encoding", "Parameterized SQL queries"),
    "3.3": ("Input Validation and Output Encoding", "Context-appropriate output encoding"),
    "3.4": ("Input Validation and Output Encoding", "Path traversal prevention"),
    "3.5": ("Input Validation and Output Encoding", "No unsafe APIs with untrusted data"),
    "3.6": ("Input Validation and Output Encoding", "Redirect URL allowlisting"),
    "4.1": ("Authentication and Authorization", "All protected endpoints authenticated"),
    "4.2": ("Authentication and Authorization", "Server-side authorization enforcement"),
    "4.3": ("Authentication and Authorization", "Least privilege applied"),
    "4.4": ("Authentication and Authorization", "Secure session management"),
    "4.5": ("Authentication and Authorization", "No hardcoded auth bypasses"),
    "5.1": ("Dependency Security", "Dependencies pinned to exact versions"),
    "5.2": ("Dependency Security", "Lock file committed"),
    "5.3": ("Dependency Security", "No critical/high dependency CVEs"),
    "5.4": ("Dependency Security", "Dependency licenses reviewed"),
    "5.5": ("Dependency Security", "Package names verified (typosquatting)"),
    "5.6": ("Dependency Security", "Dependency scanning in CI/CD"),
    "5.7": ("Dependency Security", "SBOM generated/updated"),
    "6.1": ("Error Handling and Logging", "Explicit error handling"),
    "6.2": ("Error Handling and Logging", "No internal details in error messages"),
    "6.3": ("Error Handling and Logging", "No sensitive data in logs"),
    "6.4": ("Error Handling and Logging", "Audit logging for security events"),
    "6.5": ("Error Handling and Logging", "Structured log format"),
    "7.1": ("Cryptography and Data Protection", "TLS 1.2+ for all network comms"),
    "7.2": ("Cryptography and Data Protection", "TLS certificate validation enabled"),
    "7.3": ("Cryptography and Data Protection", "Current FIPS-validated crypto"),
    "7.4": ("Cryptography and Data Protection", "No custom cryptographic implementations"),
    "7.5": ("Cryptography and Data Protection", "Sensitive data encrypted at rest"),
    "7.6": ("Cryptography and Data Protection", "No hardcoded crypto keys"),
    "8.1": ("API and Network Security", "Authenticated API endpoints"),
    "8.2": ("API and Network Security", "Rate limiting on public endpoints"),
    "8.3": ("API and Network Security", "CORS with explicit origin allowlist"),
    "8.4": ("API and Network Security", "Security headers configured"),
    "8.5": ("API and Network Security", "No sensitive data in URL params"),
    "8.6": ("API and Network Security", "Request/response schema validation"),
    "9.1": ("Testing", "Unit tests for new functionality"),
    "9.2": ("Testing", "All existing tests pass"),
    "9.3": ("Testing", "Error paths and edge cases tested"),
    "9.4": ("Testing", "SAST scan passed"),
    "9.5": ("Testing", "SCA scan passed"),
    "9.6": ("Testing", "AI code reviewed for hallucinated APIs"),
    "10.1": ("Infrastructure and Deployment", "Infrastructure changes version-controlled"),
    "10.2": ("Infrastructure and Deployment", "No default credentials"),
    "10.3": ("Infrastructure and Deployment", "Least-privilege IAM roles"),
    "10.4": ("Infrastructure and Deployment", "Logging/monitoring enabled"),
    "10.5": ("Infrastructure and Deployment", "Container images scanned"),
    "10.6": ("Infrastructure and Deployment", "Human approval gate for production"),
}

CATEGORIES = [
    "Code Review and Provenance",
    "Secrets and Credentials",
    "Input Validation and Output Encoding",
    "Authentication and Authorization",
    "Dependency Security",
    "Error Handling and Logging",
    "Cryptography and Data Protection",
    "API and Network Security",
    "Testing",
    "Infrastructure and Deployment",
]


def load_json_file(path: str) -> dict:
    """Load a JSON file with size validation."""
    resolved = Path(path).resolve()
    if not resolved.is_file():
        return {"results": []}

    size = resolved.stat().st_size
    if size > MAX_FILE_SIZE:
        print(f"Error: File too large: {path} ({size} bytes)", file=sys.stderr)
        sys.exit(1)

    try:
        with open(resolved, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def merge_results(automated: dict, manual: dict) -> dict:
    """Merge automated and manual results into a unified status map."""
    status_map = {}

    # Process automated results
    for result in automated.get("results", []):
        item = result.get("item", "")
        if item in CHECKLIST_ITEMS:
            passed = result.get("pass")
            if passed == "skip":
                status_map[item] = ("N/A", result.get("note", "Skipped"))
            elif passed:
                status_map[item] = ("Pass", result.get("note", ""))
            else:
                status_map[item] = ("Fail", result.get("note", ""))

    # Process manual results (override automated if both exist)
    for result in manual.get("results", []):
        item = result.get("item", "")
        if item in CHECKLIST_ITEMS:
            status_map[item] = (result.get("status", "N/A"), result.get("note", ""))

    return status_map


def generate_report(status_map: dict, system_name: str, agent_used: str) -> str:
    """Generate a completed checklist report in markdown."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")

    lines = [
        "# Pre-Deployment Security Checklist — Completed",
        "",
        "---",
        "",
        "## Deployment Information",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **System Name** | {system_name} |",
        f"| **Deployment Date** | {today} |",
        f"| **AI Agent Used** | {agent_used} |",
        f"| **Report Generated** | {today} (draft — requires human review) |",
        "",
        "---",
        "",
    ]

    category_stats = {}
    failed_items = []

    for cat_idx, category in enumerate(CATEGORIES, 1):
        lines.append(f"## {cat_idx}. {category}")
        lines.append("")
        lines.append("| # | Check | Status | Notes |")
        lines.append("|---|-------|--------|-------|")

        cat_pass = 0
        cat_fail = 0
        cat_na = 0

        for item_id, (cat, desc) in sorted(CHECKLIST_ITEMS.items()):
            if cat != category:
                continue

            status, note = status_map.get(item_id, ("Pending", "Not yet verified"))

            if status == "Pass":
                cat_pass += 1
                status_mark = "Pass"
            elif status == "Fail":
                cat_fail += 1
                status_mark = "**FAIL**"
                failed_items.append((item_id, desc, note))
            else:
                cat_na += 1
                status_mark = "N/A"

            lines.append(f"| {item_id} | {desc} | {status_mark} | {note} |")

        lines.append("")
        category_stats[category] = (cat_pass, cat_fail, cat_na)

    # Summary table
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Category | Pass | Fail | N/A |")
    lines.append("|----------|------|------|-----|")

    total_pass = 0
    total_fail = 0
    total_na = 0

    for cat_idx, category in enumerate(CATEGORIES, 1):
        p, f, n = category_stats.get(category, (0, 0, 0))
        total_pass += p
        total_fail += f
        total_na += n
        lines.append(f"| {cat_idx}. {category} | {p} | {f} | {n} |")

    lines.append(f"| **Total** | **{total_pass}** | **{total_fail}** | **{total_na}** |")
    lines.append("")

    # Failed items detail
    if failed_items:
        lines.append("### Failed Items")
        lines.append("")
        for item_id, desc, note in failed_items:
            lines.append(f"- **{item_id}** {desc} — {note}")
        lines.append("")

    # Deployment recommendation
    lines.append("---")
    lines.append("")
    lines.append("## Deployment Recommendation")
    lines.append("")

    if total_fail == 0:
        lines.append("**APPROVED** — All checks pass or N/A.")
    elif total_fail <= 3:
        lines.append("**CONDITIONALLY APPROVED** — Minor findings documented above. Remediate before production.")
    else:
        lines.append(f"**NOT APPROVED** — {total_fail} failed item(s) must be resolved before deployment.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This is a DRAFT report. A human reviewer must verify all results and sign off.*")
    lines.append(f"*Generated: {today} by federal-pre-deployment-check skill*")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate completed pre-deployment checklist report")
    parser.add_argument("--automated-results", required=True, help="Path to automated check results JSON")
    parser.add_argument("--manual-results", default=None, help="Path to manual verification results JSON")
    parser.add_argument("--system-name", default="[System Name]", help="System name")
    parser.add_argument("--agent-used", default="[Agent]", help="AI agent used")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    args = parser.parse_args()

    automated = load_json_file(args.automated_results)
    manual = load_json_file(args.manual_results) if args.manual_results else {"results": []}

    status_map = merge_results(automated, manual)
    report = generate_report(status_map, args.system_name, args.agent_used)

    if args.output:
        out_path = Path(args.output).resolve()
        if out_path.suffix.lower() != ".md":
            print("Error: Output file must have .md extension", file=sys.stderr)
            sys.exit(1)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {args.output}", file=sys.stderr)

        result = {
            "status": "success",
            "output": args.output,
            "passed": sum(1 for s, _ in status_map.values() if s == "Pass"),
            "failed": sum(1 for s, _ in status_map.values() if s == "Fail"),
        }
        print(json.dumps(result), file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
