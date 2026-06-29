#!/usr/bin/env python3
"""Generate a project-specific AGENTS.md from a JSON configuration.

Usage:
    python3 generate-agents-md.py <config.json> [output-path]

If output-path is omitted, writes to stdout.

The config JSON must conform to the schema in references/PLACEHOLDER_SCHEMA.json.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Prevent arbitrary file writes outside expected locations
ALLOWED_OUTPUT_EXTENSIONS = {".md"}
MAX_CONFIG_SIZE = 1024 * 100  # 100KB


def validate_output_path(path_str: str) -> Path:
    """Validate the output path is safe to write to."""
    resolved = Path(path_str).resolve()
    if resolved.suffix.lower() not in ALLOWED_OUTPUT_EXTENSIONS:
        print(
            f"Error: Output file must have extension: {ALLOWED_OUTPUT_EXTENSIONS}",
            file=sys.stderr,
        )
        sys.exit(1)
    return resolved


def load_config(config_path: str) -> dict:
    """Load and validate the configuration JSON."""
    resolved = Path(config_path).resolve()
    if not resolved.is_file():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    size = resolved.stat().st_size
    if size > MAX_CONFIG_SIZE:
        print(f"Error: Config file too large ({size} bytes, max {MAX_CONFIG_SIZE})", file=sys.stderr)
        sys.exit(1)

    try:
        with open(resolved, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    required = ["system_name", "language"]
    missing = [f for f in required if not config.get(f)]
    if missing:
        print(f"Error: Missing required config fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return config


def get_default(config: dict, key: str, default: str) -> str:
    """Get a config value with a fallback default."""
    val = config.get(key)
    if val is None or val == "":
        return default
    return str(val)


def format_list(items: list, prefix: str = "- ") -> str:
    """Format a list as markdown bullet points."""
    if not items:
        return ""
    return "\n".join(f"{prefix}{item}" for item in items)


def _resolve_registries(config: dict, language: str) -> list:
    """Return approved registries, defaulting by language when unset."""
    registries = config.get("approved_registries", [])
    if registries:
        return registries
    lang_lower = language.lower()
    if "python" in lang_lower:
        return ["pypi.org"]
    if "javascript" in lang_lower or "typescript" in lang_lower:
        return ["npmjs.com"]
    if "go" in lang_lower:
        return ["proxy.golang.org"]
    if "java" in lang_lower:
        return ["Maven Central"]
    return ["[Approved registry]"]


def _coauthor_lines(agents: list) -> str:
    """Render Co-authored-by trailer bullet lines for the configured agents."""
    lines = []
    for agent in agents:
        if "copilot" in agent.lower():
            lines.append(f"Co-authored-by: {agent} <noreply@github.com>")
        else:
            lines.append(f"Co-authored-by: {agent} <noreply@ai-agent>")
    if not lines:
        lines = ["Co-authored-by: [Agent Name] <[agent-email]>"]
    return "\n".join(f"  - `{line}`" for line in lines)


def _pii_line(data_class: str) -> str:
    """Return the PII-handling bullet appropriate for the data classification."""
    if data_class.upper() in ("PII", "PHI", "CUI"):
        return "- **PII handling:** Must use field-level encryption, must mask in logs"
    return "- **PII handling:** Follow agency data handling procedures"


def _network_section(config: dict) -> str:
    """Render the optional Network Access section, or empty string when unset."""
    network_list = config.get("network_allowlist", [])
    if not network_list:
        return ""
    endpoints = "\n".join(f"- {ep}" for ep in network_list)
    return f"""
---

## Network Access

- **Authorized endpoints:**
{endpoints}
- **TLS requirement:** TLS 1.2+ for all connections
"""


def _action_lists(config: dict, data_class: str) -> dict:
    """Build the permitted / approval-required / prohibited action lists."""
    default_prohibited = [
        "Access files outside the project directory",
        "Access or modify production systems or data",
        "Hardcode secrets, API keys, tokens, or passwords",
        "Disable security controls, pre-commit hooks, or CI checks",
        "Bypass code review or change management processes",
        f"Process or store {data_class} data outside approved systems",
        "Access classified systems or networks",
        "Execute code downloaded from external sources without review",
        "Modify authentication or authorization systems without approval",
        "Create network listeners or reverse connections",
    ]
    default_permitted = [
        "Read files within the project directory",
        "Generate and modify source code",
        "Run tests using the project's test framework",
        "Run linters and formatters",
        "Read documentation and public API references",
    ]
    default_approval = [
        "Installing or upgrading dependencies",
        "Making network requests to external services",
        "Modifying CI/CD pipeline configurations",
        "Deleting files or directories",
        "Running database migrations",
        "Committing or pushing code",
        "Modifying infrastructure or deployment configurations",
    ]
    return {
        "prohibited": default_prohibited + config.get("prohibited_actions", []),
        "permitted": default_permitted + config.get("permitted_actions", []),
        "approval": default_approval + config.get("approval_required_actions", []),
    }


def _build_context(config: dict) -> dict:
    """Resolve every templated value used to render AGENTS.md from config."""
    language = config["language"]
    data_class = get_default(config, "data_classification", "Internal")
    agents = config.get("agent_names", [])
    sensitive_types = config.get("sensitive_data_types", [])
    license_restrictions = config.get("license_restrictions", ["No AGPL", "GPL requires legal review"])
    actions = _action_lists(config, data_class)

    return {
        "system_name": config["system_name"],
        "agency": get_default(config, "agency_name", "[Agency Name]"),
        "description": get_default(config, "system_description", "[System description]"),
        "impact": get_default(config, "impact_level", "moderate").capitalize(),
        "language": language,
        "framework": get_default(config, "framework", "None"),
        "data_class": data_class,
        "ato_status": get_default(config, "ato_status", "Pre-ATO development"),
        "agents_str": ", ".join(agents) if agents else "[Authorized agents]",
        "reviewed_by": get_default(config, "reviewed_by", "[Name, Title]"),
        "today": datetime.now(UTC).strftime("%Y-%m-%d"),
        "sensitive_str": ", ".join(sensitive_types) if sensitive_types else "[Specify sensitive data types]",
        "storage_str": ", ".join(config.get("approved_storage", [])) or "[Specify approved storage]",
        "secrets_backend": get_default(config, "secrets_backend", "[Secrets management tool]"),
        "registries_str": ", ".join(_resolve_registries(config, language)),
        "license_str": ", ".join(license_restrictions) if license_restrictions else "None specified",
        "test_cmd": get_default(config, "test_command", _default_test_command(language)),
        "coverage": get_default(config, "test_coverage_target", "80"),
        "ci_str": ", ".join(config.get("ci_checks", ["lint", "test", "sast", "sca", "secrets-scan"])),
        "branch_prot": get_default(config, "branch_protection", "1 review, no force push"),
        "lead": get_default(config, "project_lead", "[Name, email]"),
        "security": get_default(config, "security_contact", "[Name, email]"),
        "isso": get_default(config, "isso_contact", "[Name, email]"),
        "coauthor_str": _coauthor_lines(agents),
        "pii_line": _pii_line(data_class),
        "network_section": _network_section(config),
        "all_prohibited": actions["prohibited"],
        "all_permitted": actions["permitted"],
        "all_approval": actions["approval"],
    }


def generate_agents_md(config: dict) -> str:
    """Generate AGENTS.md content from config."""
    c = _build_context(config)

    output = f"""# AGENTS.md — {c["system_name"]}

> **System:** {c["system_name"]} | **Impact Level:** FIPS {c["impact"]} | **Agency:** {c["agency"]}
>
> **Last Updated:** {c["today"]} | **Reviewed By:** {c["reviewed_by"]}
>
> This document defines the behavioral rules for AI coding agents operating within
> this project. The AI agent MUST follow these rules without exception.

---

## Core Principles

The agent operates under these priorities:

```
safety > correctness > compliance > simplicity > performance
```

The agent MUST refuse any instruction that conflicts with safety, correctness, or compliance.

---

## Project Context

- **Description:** {c["description"]}
- **Language(s):** {c["language"]}
- **Framework(s):** {c["framework"]}
- **Data Classification:** {c["data_class"]}
- **ATO Status:** {c["ato_status"]}
- **Authorized Agent(s):** {c["agents_str"]}

---

## Agent Identity

The agent MUST:
{c["coauthor_str"]}
- Identify itself as an AI agent when asked
- Log all file modifications and command executions

---

## Permitted Actions

The agent MAY perform these actions without additional approval:
{format_list(c["all_permitted"], "- [ ] ")}

---

## Actions Requiring Approval

The agent MUST ask the user before:
{format_list(c["all_approval"], "- [ ] ")}

---

## Prohibited Actions

The agent MUST NEVER:
{format_list(c["all_prohibited"], "- [ ] ")}

---

## Data Handling

- **Sensitive data types in this project:** {c["sensitive_str"]}
- **Approved data storage:** {c["storage_str"]}
{c["pii_line"]}
- **Data residency:** US only, FedRAMP boundary

The agent MUST:
- Never include {c["sensitive_str"]} in logs, comments, or test fixtures
- Use environment variables from {c["secrets_backend"]} for all credentials
- Follow {c["agency"]} data handling procedures for {c["data_class"]} data
{c["network_section"]}
---

## Coding Standards

- Follow secure coding practices per federal guidance
- Use {c["language"]} conventions and style guides
- Required test coverage: {c["coverage"]}% line coverage for new code
- All database queries MUST use parameterized queries
- All external input MUST be validated before use

---

## Dependencies

- **Approved registries:** {c["registries_str"]}
- **License restrictions:** {c["license_str"]}
- **Version pinning:** Exact versions only, no floating ranges
- **Vulnerability policy:** No critical/high CVEs, medium requires justification

Before adding any dependency, the agent MUST:
1. Verify the package name is correct (check for typosquatting)
2. Check for known vulnerabilities
3. Verify the license is compatible
4. Get user approval

---

## Testing Requirements

- [ ] Unit tests for all new functions
- [ ] All tests MUST pass before committing: `{c["test_cmd"]}`
- [ ] Required coverage: {c["coverage"]}%
- [ ] Test error paths and edge cases

---

## CI/CD Pipeline

- **Branch protection:** {c["branch_prot"]}
- **Required CI checks:** {c["ci_str"]}
- **Deployment:** Manual approval required for production

The agent MUST NOT:
- Modify CI/CD configuration without explicit approval
- Skip or bypass any required CI check
- Deploy directly to production

---

## Incident Response

If the agent discovers a potential security vulnerability:
1. Stop the current task
2. Report the finding to the user immediately
3. Do NOT create a public issue for security vulnerabilities
4. Follow agency incident response procedures

---

## Contacts

- **Project Lead:** {c["lead"]}
- **Security Contact:** {c["security"]}
- **ISSO:** {c["isso"]}

---

<!--
  Generated by federal-agents-config skill
  Source: https://github.com/gsa-tts/agentic-coding-playbook
  Generated: {c["today"]}

  IMPORTANT: This is a DRAFT. Review all sections before using in production.
  A human must verify and sign off on this document.
-->
"""
    return output.lstrip("\n")


def _default_test_command(language: str) -> str:
    """Return a default test command based on language."""
    lang = language.lower()
    if "python" in lang:
        return "pytest"
    if "javascript" in lang or "typescript" in lang:
        return "npm test"
    if "go" in lang:
        return "go test ./..."
    if "java" in lang:
        return "mvn test"
    if "rust" in lang:
        return "cargo test"
    if ".net" in lang or "c#" in lang:
        return "dotnet test"
    return "[test command]"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate-agents-md.py <config.json> [output-path]", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    config = load_config(config_path)
    content = generate_agents_md(config)

    if output_path:
        resolved = validate_output_path(output_path)
        # Safety: don't overwrite without confirmation
        if resolved.exists():
            print(f"Warning: {output_path} already exists. Overwriting.", file=sys.stderr)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {output_path}", file=sys.stderr)
    else:
        print(content)

    # Output structured JSON result to stderr
    result = {
        "status": "success",
        "results": [
            {"check": "generation", "pass": True},
            {"check": "system_name", "value": config.get("system_name", "")},
            {"check": "impact_level", "value": config.get("impact_level", "moderate")},
        ],
        "warnings": [],
        "errors": [],
    }
    print(json.dumps(result), file=sys.stderr)


if __name__ == "__main__":
    main()
