---
name: federal-agents-config
title: "Federal AGENTS.md Configuration"
description: "Generate a project-specific AGENTS.md through interactive decision-tree elicitation."
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["AGENTS.md", "agent rules", "behavioral", "compliance"]
dependencies: []
---

# Federal AGENTS.md Configuration

This skill generates a project-specific AGENTS.md by walking the user through
compliance-relevant questions and producing a customized behavioral contract.

## When to Use

- User needs to create an AGENTS.md for a new federal project
- User wants to update their existing AGENTS.md for compliance
- User asks "how do I configure my AI agent for federal requirements"
- User mentions FIPS, ATO, or federal compliance in the context of agent setup

## How It Works

1. Ask the user compliance-relevant questions (elicitation sequence below)
2. Accumulate answers into a JSON configuration object
3. Run `scripts/generate-agents-md.py` with the config to produce AGENTS.md
4. Present the output for human review
5. Iterate if the user wants changes

## Configuration Object

Track this JSON structure as you collect answers. Fields marked `required` must
be filled before generation. Fields marked `optional` have sensible defaults.

```json
{
  "system_name": null,
  "agency_name": null,
  "system_description": null,
  "impact_level": "moderate",
  "language": null,
  "framework": null,
  "data_classification": "internal",
  "ato_status": "pre-ato",
  "agent_names": [],
  "prohibited_actions": [],
  "permitted_actions": [],
  "approval_required_actions": [],
  "sensitive_data_types": [],
  "approved_storage": [],
  "secrets_backend": null,
  "approved_registries": [],
  "license_restrictions": [],
  "network_allowlist": [],
  "test_command": null,
  "test_coverage_target": "80",
  "ci_checks": ["lint", "test", "sast", "sca", "secrets-scan"],
  "branch_protection": "1 review, no force push",
  "project_lead": null,
  "security_contact": null,
  "isso_contact": null,
  "reviewed_by": null
}
```

## Elicitation Sequence

Ask these questions in order. For each question, explain why it matters for
compliance when the user seems unsure.

### Phase 1: System Identification (required)

**Q1: System name and agency**
> "What is the name of this system, and which agency or organization is it for?"

Sets: `system_name`, `agency_name`

**Q2: System description**
> "Briefly describe what this system does (1-2 sentences)."

Sets: `system_description`

**Q3: FIPS impact level**
> "What is the FIPS impact level? (Low / Moderate / High)"
>
> - **Low**: Minimal adverse effect from loss of confidentiality, integrity, or availability
> - **Moderate**: Serious adverse effect (most federal internal systems)
> - **High**: Severe or catastrophic adverse effect

Sets: `impact_level`

Default: `moderate` (covers most federal internal systems)

If "high": add follow-up questions about additional data handling controls and
note that this playbook primarily targets FIPS Moderate.

### Phase 2: Technical Context (required)

**Q4: Programming language**
> "What is the primary programming language? (e.g., Python 3.12, TypeScript 5.x, Go 1.22)"

Sets: `language`

Use this to pre-populate language-specific defaults:
- **Python** -> bandit (SAST), pip-audit (SCA), ruff (linter), pytest (test)
- **JavaScript/TypeScript** -> eslint-plugin-security (SAST), npm audit (SCA), eslint (linter), jest/vitest (test)
- **Go** -> gosec (SAST), govulncheck (SCA), golangci-lint (linter), go test (test)
- **Java** -> spotbugs (SAST), dependency-check (SCA), checkstyle (linter), junit (test)

See [references/ELICITATION_GUIDE.md](references/ELICITATION_GUIDE.md) for the full tool mapping.

**Q5: Framework (if any)**
> "What framework does the project use? (e.g., FastAPI, Next.js, Django, Spring Boot, or none)"

Sets: `framework`

**Q6: Authorized agents**
> "Which AI coding agents are authorized to use this project? (e.g., GitHub Copilot, Cursor, Codex, Cursor)"

Sets: `agent_names` (array)

### Phase 3: Data Classification (required)

**Q7: Data classification**
> "What is the highest data classification this system handles?"
>
> - **Public**: No restrictions
> - **Internal**: Not for public release
> - **CUI**: Controlled Unclassified Information
> - **PII**: Personally Identifiable Information
> - **PHI**: Protected Health Information

Sets: `data_classification`

**Q8: Sensitive data types**
> "What specific sensitive data types does this system process? (e.g., SSN, email addresses, health records, financial data)"

Sets: `sensitive_data_types` (array)

If data_classification is CUI, PII, or PHI, this question is required. Otherwise optional.

**Q9: Approved data storage**
> "Where is data stored? (e.g., PostgreSQL via RDS, S3 with SSE-KMS, Azure SQL)"

Sets: `approved_storage` (array)

**Q10: Secrets management**
> "What secrets management tool does the project use? (e.g., AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, environment variables only)"

Sets: `secrets_backend`

### Phase 4: Boundaries (optional — has defaults)

**Q11: Additional prohibited actions**
> "Are there any project-specific actions the agent should NEVER do, beyond the standard federal prohibitions?"
>
> Standard prohibitions (already included): access outside project directory, production access, hardcoded secrets, disable security controls, bypass code review, access classified systems.

Sets: `prohibited_actions` (array, appended to defaults)

**Q12: Additional permitted actions**
> "Are there any project-specific actions the agent MAY do without asking? (Beyond reading files, generating code, running tests and linters)"

Sets: `permitted_actions` (array, appended to defaults)

**Q13: Network requirements**
> "Does the agent need network access? If so, which endpoints?"
>
> If none: the Network Access section will be omitted from the generated AGENTS.md.

Sets: `network_allowlist` (array, empty = no network section)

### Phase 5: Dependencies and CI (optional — has defaults)

**Q14: Approved package registries**
> "Which package registries are approved? (Default: the standard public registry for your language)"

Sets: `approved_registries` (array)

**Q15: License restrictions**
> "Any license restrictions? (Default: No AGPL, GPL requires legal review)"

Sets: `license_restrictions` (array)

Default: `["No AGPL", "GPL requires legal review"]`

**Q16: CI checks**
> "What CI checks should be required? (Default: lint, test, SAST, SCA, secrets scan)"

Sets: `ci_checks` (array)

### Phase 6: Contacts (optional but recommended)

**Q17: Contacts**
> "Who should be listed as contacts? (Project lead, security contact, ISSO — name and email)"

Sets: `project_lead`, `security_contact`, `isso_contact`

### Phase 7: Review and Generate

After collecting all answers:

1. Present the completed JSON config for review
2. Ask: "Does this look correct? Any changes?"
3. If changes needed, update the config and re-present
4. When confirmed, write the config to a temporary JSON file
5. Run: `python3 skills/federal-agents-config/scripts/generate-agents-md.py <config.json> <output-path>`
6. Present the generated AGENTS.md for final review
7. Optionally run: `python3 skills/federal-agents-config/scripts/validate-agents-md.py <output-path>`

## Defaults by Impact Level

| Field | Low | Moderate | High |
|-------|-----|----------|------|
| `test_coverage_target` | 60% | 80% | 90% |
| `branch_protection` | 1 review | 1 review, no force push | 2 reviews, no force push, signed commits |
| `ci_checks` | lint, test, secrets-scan | lint, test, sast, sca, secrets-scan | All + DAST, container scan |

## Important Notes

- This skill generates a **draft** AGENTS.md. It explicitly requires human review and sign-off.
- The generated AGENTS.md is a **compliance document**, not a development guide.
- All content traces back to `templates/AGENTS.md.template` and `AGENTS.md` (the master rules).
- The generation script (`scripts/generate-agents-md.py`) reads the config JSON and produces markdown. It does not make network calls, install packages, or modify git state.
- The validation script (`scripts/validate-agents-md.py`) checks that required sections and fields are present.
- See [references/PLACEHOLDER_SCHEMA.json](references/PLACEHOLDER_SCHEMA.json) for the formal JSON Schema.
- See [references/ELICITATION_GUIDE.md](references/ELICITATION_GUIDE.md) for detailed question help text.
