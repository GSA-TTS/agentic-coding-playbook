---
title: "Federal ADR Template"
description: "MADR template with federal compliance frontmatter extensions for documenting architectural and security decisions"
status: canonical
tier: 3
last_updated: "2026-06-01"
---

# ADR Template — Federal MADR with Compliance Extensions

This template extends the [MADR](https://adr.github.io/madr/) format with
federal compliance fields. Use this when generating decision records.

## Template

````markdown
---
title: "{TITLE}"
status: "{proposed|accepted|deprecated|superseded}"
date: "{YYYY-MM-DD}"
decision_makers: ["{NAME1}", "{NAME2}"]
category: "{CATEGORY}"
nist_controls: ["{XX-N}", "{XX-N}"]
impact_level: "{low|moderate|high}"
ato_relevance: "{yes-boundary|yes-internal|no}"
risk_treatment: "{mitigate|transfer|accept|avoid|n/a}"
superseded_by: "{NNNN-title.md}"
supersedes: "{NNNN-title.md}"
---

# {TITLE}

## Context and Problem Statement

{Describe the problem or question that requires a decision. What is the
context? What constraints exist? 1-3 sentences.}

## Decision Drivers

- {Driver 1 — e.g., "NIST AC-6 requires least privilege for agent access"}
- {Driver 2 — e.g., "Agency policy requires FedRAMP-authorized services"}
- {Driver 3}

## Considered Options

1. **{Option A}** — {Brief description}
2. **{Option B}** — {Brief description}
3. **{Option C}** — {Brief description}

## Decision Outcome

Chosen option: **{Option X}**, because {1-2 sentence rationale linking to
decision drivers}.

### Positive Consequences

- {Positive consequence 1}
- {Positive consequence 2}

### Negative Consequences

- {Negative consequence 1}
- {Negative consequence 2}

### Compliance Consequences

- {NIST control satisfied or partially addressed}
- {ATO documentation that needs updating}
- {Monitoring or audit requirements triggered}

## Links

- {Link to related ADR, risk assessment, or policy document}
- {Link to relevant NIST control guidance}
````

## Frontmatter Field Reference

### Standard MADR Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `title` | Yes | Free text | Decision title (imperative: "Use X for Y") |
| `status` | Yes | proposed, accepted, deprecated, superseded | Current status |
| `date` | Yes | YYYY-MM-DD | Decision date |
| `decision_makers` | Yes | YAML array of names | People involved |

### Federal Compliance Extensions

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `category` | Yes | See DECISION_CATEGORIES.md | Decision category |
| `nist_controls` | Yes | YAML array of control IDs | Applicable NIST 800-53 controls |
| `impact_level` | Yes | low, moderate, high | FIPS 199 impact level |
| `ato_relevance` | Yes | yes-boundary, yes-internal, no | ATO package relevance |
| `risk_treatment` | No | mitigate, transfer, accept, avoid, n/a | Risk treatment if addressing a known risk |
| `superseded_by` | No | Filename | ADR that supersedes this one |
| `supersedes` | No | Filename | ADR that this one supersedes |

### ATO Relevance Values

- **yes-boundary** — Decision affects the system authorization boundary
  (e.g., adding a new external service, changing data flows)
- **yes-internal** — Decision is relevant to ATO but internal to the boundary
  (e.g., changing authentication method, updating crypto algorithms)
- **no** — Decision does not affect the ATO package
  (e.g., code style choices, internal refactoring)

### Status Lifecycle

```
proposed → accepted → deprecated
                    → superseded (by newer ADR)
```

- **proposed** — Under review, not yet approved
- **accepted** — Approved and in effect
- **deprecated** — No longer relevant (system/feature removed)
- **superseded** — Replaced by a newer decision (must set `superseded_by`)
