---
name: federal-decision-records
title: "Federal Decision Records"
description: "Create, validate, and index architectural and security decision records using MADR format with federal compliance extensions."
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["ADR", "architecture decision", "decision record"]
dependencies: []
---

# Federal Decision Records

This skill helps users create, validate, and index architectural and security
decision records using [MADR](https://adr.github.io/madr/) (Markdown Any
Decision Records) format with federal compliance extensions.

Decision records provide an audit trail linking design choices to NIST controls
and risk treatment rationale — required for ATO documentation.

## When to Use

- Documenting a decision about AI agent authorization or capabilities
- Recording data handling or classification decisions
- Capturing deployment or infrastructure security choices
- Documenting cryptographic or authentication design decisions
- Preparing audit trail for ISSO or ATO reviewer
- When the `federal-risk-assessment` skill identifies risks that require
  treatment decisions — document the treatment rationale here

## How It Works

This skill has three modes:

1. **Create** — Guide the user through creating a new decision record
2. **Validate** — Check existing ADRs for format and completeness
3. **Index** — Generate a decision record index from frontmatter

Ask the user which mode they need, or infer from context.

## Mode 1: Create a Decision Record

### Step 1: Determine Decision Category

Ask the user what kind of decision they are documenting. Present the categories
from [references/DECISION_CATEGORIES.md](references/DECISION_CATEGORIES.md):

> "What category does this decision fall into?"

Read `references/DECISION_CATEGORIES.md` to present the current category list
with examples. Each category maps to relevant NIST controls.

### Step 2: Collect Decision Metadata

Ask for the required fields:

> "Let's document this decision. I need:
> 1. **Title** — What is being decided? (Use format: 'Use X for Y')
> 2. **Status** — proposed, accepted, deprecated, or superseded?
> 3. **Decision makers** — Who is involved in this decision?
> 4. **Date** — When was this decided? (Default: today)"

### Step 3: Collect Federal Compliance Fields

These extend standard MADR with federal context:

> "For federal compliance traceability:
> 1. **NIST controls** — Which 800-53 controls does this decision address?
>    (I can suggest controls based on the category you selected)
> 2. **Impact level** — Low, Moderate, or High (FIPS 199)?
> 3. **ATO relevance** — Is this decision relevant to the ATO package?
>    (yes-boundary, yes-internal, no)
> 4. **Risk treatment** — If this addresses a known risk, what treatment?
>    (mitigate, transfer, accept, avoid, or N/A)"

Use the category-to-control mapping from `references/DECISION_CATEGORIES.md`
to suggest relevant NIST controls. The user can accept, modify, or skip.

### Step 4: Document the Decision

Walk through each MADR section. Read the template at
[references/ADR_TEMPLATE.md](references/ADR_TEMPLATE.md) to get the current
section structure. For each section:

**Context and Problem Statement:**
> "Describe the problem or context that led to this decision. What question
> are you trying to answer? (1-3 sentences)"

**Decision Drivers:**
> "What factors influenced this decision? List the key drivers."

Suggest compliance-relevant drivers based on the category:
- For agent authorization: least privilege, audit logging, identity management
- For data handling: data classification, encryption, access controls
- For deployment: separation of duties, change management, CI/CD security
- For cryptography: FIPS 140-2/3 compliance, key management, algorithm selection

**Considered Options:**
> "What options did you evaluate? List 2-4 alternatives."

For each option, ask for a brief description.

**Decision Outcome:**
> "Which option was chosen, and why?"

**Consequences:**
> "What are the positive and negative consequences of this decision?"

Prompt specifically for compliance consequences:
> "Are there any compliance implications? (e.g., additional controls needed,
> ATO documentation updates, monitoring requirements)"

### Step 5: Assign ADR Number

Check the target directory for existing ADRs:

> "Where should decision records be stored? (Default: `docs/decisions/`)"

Scan the directory for existing `NNNN-*.md` files and assign the next
sequential number (zero-padded to 4 digits).

### Step 6: Generate the Record

Produce the complete ADR file using the template from
`references/ADR_TEMPLATE.md` with all collected information filled in.

Present the generated record for review:

> "Here is the generated decision record. Review it and let me know if
> you'd like any changes before I save it."

Save to `{directory}/{NNNN}-{slugified-title}.md`.

### Step 7: Update the Index

After saving, run the index generator:

```bash
make generate
```

This updates `{directory}/README.md` with a table of all decision records
derived from their frontmatter.

### Step 8: Recommend Next Steps

Based on the decision category, suggest follow-up actions:

- **Agent authorization** → "Run `federal-agents-config` to update AGENTS.md
  with the authorized agents and capabilities from this decision"
- **Data handling** → "Update the risk assessment using
  `federal-risk-assessment` if data classification changed"
- **Deployment** → "Run `federal-pre-deployment-check` to verify the
  deployment configuration matches this decision"
- **Any ATO-relevant decision** → "Add this record to your ATO package
  documentation. Your ISSO should review it."

## Mode 2: Validate Decision Records

Run the validation script:

```bash
PYTHONPATH=scripts python3 -m playbook_validator validate-adrs --dir docs/adr
```

The script checks:
- YAML frontmatter has all required fields (title, status, date, nist_controls)
- File naming follows `NNNN-title.md` convention
- No duplicate ADR numbers
- Status values are valid (proposed, accepted, deprecated, superseded)
- NIST control IDs match expected format (`XX-N` or `XX-N(N)`)
- Superseded records reference the superseding record

Output is structured JSON. Present results to the user with remediation
guidance for any failures.

## Mode 3: Generate Index

Run the index generator to rebuild the decision record index:

```bash
make generate
```

This reads frontmatter from all ADR files and generates a `README.md` in the
decisions directory with:
- Table of all records (number, title, status, date, NIST controls)
- Counts by status (accepted, proposed, deprecated, superseded)
- List of all NIST controls referenced across decisions

Present the generated index to the user.

## Important Notes

- This skill generates new files (ADRs, index). It does NOT modify existing
  ADRs, install packages, or make network calls.
- Generated records are **drafts** — they should be reviewed by the decision
  makers listed in the frontmatter before being marked "accepted".
- NIST control suggestions are guidance only — the user should verify
  applicability with their ISSO.
- ADR numbers are sequential and MUST NOT be reused, even for superseded
  records (this preserves the audit trail).
- The federal compliance extensions (nist_controls, impact_level,
  ato_relevance, risk_treatment) are additions to standard MADR — they do
  not break compatibility with MADR tooling.
- **Policy references:** `AGENTS.md` (agent decisions), `docs/CODING_PRACTICES.md`
  (coding decisions), `docs/SECURITY-CONTROLS.md` (control guidance),
  `docs/TRACEABILITY.md` (control mappings).
