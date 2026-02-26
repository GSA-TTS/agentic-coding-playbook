---
title: "AGENTS.md Elicitation Guide"
description: "Full question catalog with help text and federal compliance context for AGENTS.md generation"
status: canonical
tier: 3
---

# AGENTS.md Elicitation Guide

This guide provides the full question catalog for the `federal-agents-config` skill.
Each question includes help text, compliance context, and default values.

## Phase 1: System Identification

### Q1: System Name and Agency

**Ask:** "What is the name of this system, and which agency or organization is it for?"

**Why it matters:** The system name and agency appear in the AGENTS.md header and
are used for traceability. Federal systems must be identifiable for ATO purposes.

**Help text:** Use the official system name from your System Security Plan (SSP)
if one exists. If this is a new project, use the working name.

**Config fields:** `system_name` (required), `agency_name` (optional, defaults to "[Agency Name]")

### Q2: System Description

**Ask:** "Briefly describe what this system does (1-2 sentences)."

**Why it matters:** Provides context for agents to understand the system's purpose
and make appropriate security decisions.

**Config field:** `system_description` (optional)

### Q3: FIPS Impact Level

**Ask:** "What is the FIPS impact level? (Low / Moderate / High)"

**Why it matters:** The impact level determines the rigor of security controls:
- **Low:** Minimal controls. Basic security practices.
- **Moderate:** Standard federal controls. Required for most internal systems.
  This guidance is primarily designed for FIPS Moderate.
- **High:** Maximum controls. Required for systems where compromise could cause
  severe harm (e.g., law enforcement, financial, health).

**Help text:** If unsure, check your System Security Plan or ask your ISSO.
Most internal federal enterprise systems are FIPS Moderate.

**Config field:** `impact_level` (defaults to "moderate")

**Impact on generation:**

| Setting | Test Coverage | Branch Protection | CI Checks |
|---------|--------------|-------------------|-----------|
| Low | 60% | 1 review | lint, test, secrets-scan |
| Moderate | 80% | 1 review, no force push | lint, test, sast, sca, secrets-scan |
| High | 90% | 2 reviews, no force push, signed commits | All + DAST, container scan |

## Phase 2: Technical Context

### Q4: Programming Language

**Ask:** "What is the primary programming language? (e.g., Python 3.12, TypeScript 5.x, Go 1.22)"

**Why it matters:** The language determines which security tools, linters, and test
frameworks are recommended in the generated AGENTS.md.

**Language-specific tool defaults:**

| Language | SAST | SCA | Linter | Test |
|----------|------|-----|--------|------|
| Python | bandit, semgrep | pip-audit, safety | ruff | pytest |
| JavaScript/TypeScript | eslint-plugin-security, semgrep | npm audit, snyk | eslint | jest, vitest |
| Go | gosec, semgrep | govulncheck | golangci-lint | go test |
| Java | spotbugs, semgrep | dependency-check | checkstyle | junit |
| .NET | security-code-scan, semgrep | dotnet list --vulnerable | dotnet format | dotnet test |
| Rust | cargo-audit | cargo-audit | clippy | cargo test |

**Config field:** `language` (required)

### Q5: Framework

**Ask:** "What framework does the project use? (e.g., FastAPI, Next.js, Django, Spring Boot, or none)"

**Why it matters:** Frameworks may have specific security considerations (e.g.,
Django's CSRF protection, Next.js server components).

**Config field:** `framework` (optional, defaults to "None")

### Q6: Authorized Agents

**Ask:** "Which AI coding agents are authorized to use this project?"

**Why it matters:** Per NIST SP 800-53 AC-2 (Account Management), all agents
must be identified and authorized. Only listed agents should work on the codebase.

**Common options:**
- Open Code
- GitHub Copilot
- Cursor
- OpenAI Codex CLI
- Gemini CLI

**Config field:** `agent_names` (array)

## Phase 3: Data Classification

### Q7: Data Classification

**Ask:** "What is the highest data classification this system handles?"

**Options and implications:**
- **Public:** No special data handling rules
- **Internal:** Standard access controls, don't expose externally
- **CUI:** Controlled Unclassified Information — requires handling markings,
  access controls, and encryption per 32 CFR 2002
- **PII:** Personally Identifiable Information — requires minimization,
  field-level encryption, masking in logs
- **PHI:** Protected Health Information — requires HIPAA-aligned controls,
  encryption at rest and in transit, audit logging

**Config field:** `data_classification` (defaults to "internal")

### Q8: Sensitive Data Types

**Ask:** "What specific sensitive data types does this system process?"

**Required if:** `data_classification` is CUI, PII, or PHI

**Examples:** SSN, email addresses, health records, financial account numbers,
biometric data, geolocation, authentication credentials

**Config field:** `sensitive_data_types` (array)

### Q9: Approved Data Storage

**Ask:** "Where is data stored?"

**Examples:** PostgreSQL via RDS, S3 with SSE-KMS, Azure SQL, on-premises Oracle

**Config field:** `approved_storage` (array)

### Q10: Secrets Management

**Ask:** "What secrets management tool does the project use?"

**Options:**
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager
- Environment variables only (acceptable for development, not production)

**Why it matters:** Per NIST IA-5, credentials must be managed through approved
mechanisms, not hardcoded or stored in plain text.

**Config field:** `secrets_backend` (optional)

## Phase 4: Boundaries

### Q11: Additional Prohibited Actions

**Ask:** "Are there any project-specific actions the agent should NEVER do?"

**Standard prohibitions (always included):**
1. Access files outside the project directory
2. Access or modify production systems or data
3. Hardcode secrets, API keys, tokens, or passwords
4. Disable security controls, pre-commit hooks, or CI checks
5. Bypass code review or change management processes
6. Process data outside approved systems
7. Access classified systems or networks
8. Execute code downloaded from external sources
9. Modify auth systems without approval
10. Create network listeners or reverse connections

**Config field:** `prohibited_actions` (array, appended to defaults)

### Q12: Additional Permitted Actions

**Ask:** "Are there project-specific actions the agent MAY do without asking?"

**Standard permissions (always included):**
1. Read files within the project directory
2. Generate and modify source code
3. Run tests
4. Run linters and formatters
5. Read documentation and public API references

**Config field:** `permitted_actions` (array, appended to defaults)

### Q13: Network Requirements

**Ask:** "Does the agent need network access? If so, which endpoints?"

**If no endpoints:** The Network Access section is omitted from the generated AGENTS.md.

**Config field:** `network_allowlist` (array, empty = no network section)

## Phase 5: Dependencies and CI

### Q14: Approved Package Registries

**Ask:** "Which package registries are approved?"

**Defaults by language:**
- Python: pypi.org
- JavaScript/TypeScript: npmjs.com
- Go: proxy.golang.org
- Java: Maven Central

**Config field:** `approved_registries` (array)

### Q15: License Restrictions

**Ask:** "Any license restrictions?"

**Default:** No AGPL, GPL requires legal review

**Config field:** `license_restrictions` (array)

### Q16: CI Checks

**Ask:** "What CI checks should be required?"

**Default:** lint, test, sast, sca, secrets-scan

**Config field:** `ci_checks` (array)

## Phase 6: Contacts

### Q17: Contacts

**Ask:** "Who should be listed as contacts?"

**Fields:** project_lead, security_contact, isso_contact (all optional but recommended)

## Skipping Questions

If the user wants to skip questions:
- Required fields (`system_name`, `language`) cannot be skipped
- Optional fields use sensible defaults (documented above)
- The user can always re-run the skill later to fill in skipped fields
