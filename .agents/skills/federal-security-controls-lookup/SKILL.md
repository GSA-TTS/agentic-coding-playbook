---
name: federal-security-controls-lookup
title: "Federal Security Controls Lookup"
description: "Look up NIST SP 800-53 controls, OWASP LLM/Agentic risks, or security keywords to find relevant guidance"
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "isso", "agents"]
triggers: ["NIST control", "OWASP", "security", "AC-", "SI-", "CM-", "control lookup"]
dependencies: []
---

# Federal Security Controls Lookup

This skill navigates the federal agentic AI guidance repository to find relevant
policy documents, checklist items, and remediation guidance for a given security
control, OWASP risk, or keyword.

## When to Use

- User asks about a specific NIST control (e.g., "What does AC-6 require?")
- User asks about an OWASP risk (e.g., "How do we handle LLM01 prompt injection?")
- User asks a security question (e.g., "How should we handle secrets?")
- User needs to trace a checklist failure back to guidance
- User needs to understand which controls apply to a topic

## Lookup Procedure

### Step 1: Classify the Query

Determine which type of lookup the user needs:

| Query Pattern | Type | Example |
|---------------|------|---------|
| `AC-*`, `AU-*`, `CM-*`, `IA-*`, `IR-*`, `RA-*`, `SA-*`, `SC-*`, `SI-*`, `SR-*` | NIST Control ID | "AC-6", "SI-10" |
| `LLM01`-`LLM10` | OWASP LLM Risk | "LLM01" |
| `Agentic-01`-`Agentic-10` | OWASP Agentic Risk | "Agentic-05" |
| Checklist number like `1.1`, `5.3` | Checklist Item | "item 2.5" |
| Free text | Keyword Search | "secrets", "input validation" |

### Step 2: Read the Traceability Matrix

Read `docs/TRACEABILITY.md` — this is the navigation index for the entire repository.

It contains five mapping tables:
1. **NIST Control -> Document sections** (Table 1)
2. **OWASP LLM Risk -> Controls and sections** (Table 2a)
3. **OWASP Agentic Risk -> Controls and sections** (Table 2b)
4. **Checklist Item -> Control and guidance** (Table 3, items 1.1-10.6)
5. **AI RMF Function -> Documents** (Table 4)

### Step 3: Follow the Lookup Path

#### For NIST Control IDs (e.g., AC-6)

1. Find the control in Table 1 of `docs/TRACEABILITY.md`
2. Note which document sections are referenced (e.g., `AGENTS.md §3.1`, `SECURITY-CONTROLS.md §3.1`)
3. Note which checklist items verify this control
4. Read the referenced sections from those documents
5. Present: control name, where guidance lives, what the checklist verifies, key requirements

#### For OWASP LLM Risks (e.g., LLM01)

1. Find the risk in Table 2a of `docs/TRACEABILITY.md`
2. Note the primary NIST controls that address this risk
3. Note which document sections contain guidance
4. Read the referenced sections
5. Present: risk description, mapped controls, guidance locations, checklist items

#### For OWASP Agentic Risks (e.g., Agentic-05)

1. Find the risk in Table 2b of `docs/TRACEABILITY.md`
2. Follow the same pattern as OWASP LLM risks
3. Note any "Out of scope (MVP)" entries and state them explicitly

#### For Checklist Items (e.g., 2.5)

1. Find the item in Table 3 of `docs/TRACEABILITY.md`
2. Note the NIST control it satisfies
3. Read the playbook location referenced
4. Present: checklist requirement, control mapping, remediation guidance

#### For Keyword Searches

1. Search `docs/TRACEABILITY.md` for the keyword first
2. If found in control names or risk descriptions, follow the appropriate lookup path
3. If not found, read `INDEX.yaml` to get the current document inventory,
   then search across all listed documents in tier order (Tier 1 first):
   - Tier 1 documents (core standards and controls)
   - Tier 2 documents (setup and reference)
   - Tier 3 documents (checklists and templates)
4. Present: matching sections with document paths, related controls

### Step 4: Present Results

Structure your response as:

```
## [Control/Risk/Topic]: [Name]

**Source:** [document path and section]
**Related Controls:** [NIST control IDs]
**Checklist Items:** [item numbers, if any]

### Guidance Summary
[Key requirements from the referenced sections]

### Where to Find More
- [Document]: [Section] — [brief description]
- [Document]: [Section] — [brief description]
```

## Document Inventory

Read `INDEX.yaml` at the repository root for the current document inventory.
It lists all documents with their paths, titles, descriptions, tiers, and
NIST control counts. This is the single source of truth — it is auto-generated
by `make generate` from document frontmatter, so it is always
up to date.

Key entry points for this skill:

- **Start here:** `docs/TRACEABILITY.md` — cross-reference index mapping controls, risks, and checklist items
- **Control details:** `docs/SECURITY-CONTROLS.md` — full 800-53 overlay with implementation guidance
- **All other documents:** listed in `INDEX.yaml` under `documents:` with tier classification

## Important Notes

- This is a **read-only** skill. It navigates and presents existing guidance — it does not modify any files.
- All guidance references NIST SP 800-53 Rev 5.2 controls at FIPS Moderate impact level.
- The traceability matrix covers NIST SP 800-53 controls, OWASP Top 10 for LLM risks, and OWASP Top 10 for Agentic risks. See `INDEX.yaml` stats and `docs/TRACEABILITY.md` for current counts.
- Items marked "Out of scope (MVP)" in the traceability matrix are explicitly excluded from current guidance (e.g., multi-agent communication, vector/embedding security).
- When presenting guidance, always cite the specific document path and section number.
