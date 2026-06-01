---
name: federal-pre-deployment-check
title: "Federal Pre-Deployment Check"
description: "Run the 62-item federal pre-deployment security checklist against a codebase."
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["deploy", "pre-deploy", "checklist", "security check"]
dependencies: []
---

# Federal Pre-Deployment Check

This skill executes the 62-item pre-deployment security checklist from
`checklists/pre-deployment.md`, combining automated tool checks with
human-verified items to produce a completed checklist report.

## When to Use

- Before deploying code that was generated or modified with AI agent assistance
- As part of a PR review process for AI-assisted changes
- When a user asks "is this code ready to deploy?"
- When performing a security review of the codebase

## Check Classification

See [references/CHECK_AUTOMATION.md](references/CHECK_AUTOMATION.md) for the full
classification of all 60 items. Summary:

| Type | Count | How It Works |
|------|-------|-------------|
| **Automated** | 18 | Agent runs a tool, checks exit code or output |
| **Semi-automated** | 24 | Agent reads files or config, reports findings |
| **Manual** | 18 | Agent asks the human to verify |

## Execution Procedure

### Step 1: Collect Deployment Information

Ask the user for:
- System name
- Release/version being deployed
- AI agent that was used
- Files that were agent-authored (or PR number)

### Step 2: Run Automated Checks

Run `make pre-deploy` to execute all automatable checks:

```bash
make pre-deploy
```

The script checks for:
- Secrets in source code (gitleaks or grep-based fallback)
- Pre-commit hooks installed and configured
- .gitignore with required patterns
- Lock file present
- Dependency vulnerabilities (language-specific audit tool)
- Test suite passes
- SAST scan (if tool available)

Output is structured JSON with pass/fail for each automated check.

### Step 3: Run Semi-Automated Checks

For each semi-automated check, read the relevant files and report findings:

**Category 1 — Code Review and Provenance:**
- Check for AI attribution (PR description, AGENTS.md, or git log for `Co-Authored-By`) (item 1.2)
- Check branch protection config or recent commit history (item 1.4)

**Category 3 — Input Validation:**
- Search for `eval(`, `innerHTML`, string concatenation in SQL (items 3.2, 3.5)
- Search for path handling without validation (item 3.4)

**Category 6 — Error Handling:**
- Search for empty catch/except blocks (item 6.1)
- Search for stack traces in error responses (item 6.2)
- Search for PII patterns in log statements (item 6.3)

**Category 7 — Cryptography:**
- Search for TLS configuration, cert verification settings (items 7.1, 7.2)
- Search for hardcoded keys or IVs (item 7.6)

**Category 8 — API Security:**
- Check for CORS configuration (item 8.3)
- Check for security headers (item 8.4)
- Search for sensitive data in URL construction (item 8.5)

**Category 10 — Infrastructure:**
- Check for IaC files in version control (item 10.1)
- Search for default credentials (item 10.2)

### Step 4: Collect Manual Verification

For items that require human judgment, present them to the user one category
at a time. For each item, explain what to verify and ask for Pass/Fail/N/A.

**Items requiring human verification:**

| Item | Question to Ask |
|------|----------------|
| 1.1 | "Has all AI-generated code been reviewed by someone other than the person who prompted the agent?" |
| 1.3 | "Did all changes go through the standard PR/code review process?" |
| 1.5 | "Does the reviewer understand what the code does and verify it matches intended behavior?" |
| 4.1 | "Are all protected endpoints authenticated?" |
| 4.2 | "Is authorization enforced server-side on every request?" |
| 4.3 | "Is least privilege applied (no excessive permissions)?" |
| 4.4 | "Does session management use secure defaults?" |
| 4.5 | "Are there any hardcoded roles or auth bypasses?" |
| 5.4 | "Have all new dependency licenses been reviewed for compatibility?" |
| 5.7 | "Has the SBOM been generated/updated (if required by agency policy)?" |
| 6.4 | "Does audit logging cover authentication, authorization, and data access events?" |
| 6.5 | "Is the log format structured (JSON) with required fields?" |
| 9.1 | "Are there unit tests for all new functionality?" |
| 9.3 | "Are error paths and edge cases tested?" |
| 9.6 | "Has AI-generated code been reviewed for hallucinated APIs or deprecated methods?" |
| 10.3 | "Are services configured with least-privilege IAM roles?" |
| 10.4 | "Is logging and monitoring enabled for all deployed services?" |
| 10.6 | "Does deployment require a human approval gate for production?" |

### Step 5: Generate Report

Merge all results (automated + semi-automated + manual) into a completed checklist:

```bash
python3 skills/federal-pre-deployment-check/scripts/generate-checklist-report.py \
  --automated-results results.json \
  --manual-results manual.json \
  --output completed-checklist.md
```

Or, construct the completed checklist inline by filling in the Pass/Fail/N/A
status and notes for each of the 60 items in the checklist format from
`checklists/pre-deployment.md`.

### Step 6: Present Results

Present the summary:

```
## Pre-Deployment Check Results

| Category | Pass | Fail | N/A |
|----------|------|------|-----|
| 1. Code Review | X | X | X |
| ... | | | |
| **Total** | XX | XX | XX |

### Failed Items
- [X.X] Description — Suggested remediation
- [X.X] Description — Suggested remediation

### Deployment Recommendation
[Approved / Conditionally Approved / Not Approved]
```

If any items fail, recommend "Not Approved" and list the remediation steps
with references to the relevant policy documents (use the
`federal-security-controls-lookup` skill to find guidance).

## Important Notes

- This skill produces a **draft** checklist report. A human must review and sign off.
- The reviewer MUST NOT be the same person who directed the agent (per checklist instructions).
- Automated checks are best-effort — tool availability varies by environment.
- The automated checks (`make pre-deploy`) are read-only. They do not modify files, install packages, or make network calls.
- All 60 items trace back to NIST SP 800-53 controls via `docs/TRACEABILITY.md` Table 3.
- **Policy reference:** `checklists/pre-deployment.md` for the full checklist, `docs/TRACEABILITY.md` for control mappings.
