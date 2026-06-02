---
name: ato-package
title: "ATO Package Assembly"
description: "Collect and verify all ATO submission artifacts into a review-ready package"
status: canonical
tier: 2
load_priority: on-demand
audience: ["developers", "isso", "agents"]
triggers: ["ATO", "authority to operate", "package", "submission", "ISSO review", "compliance package"]
dependencies: ["federal-risk-assessment", "federal-pre-deployment-check", "federal-decision-records"]
---

# ATO Package Assembly

This skill collects, validates, and indexes all Authority to Operate submission
artifacts into a review-ready package for ISSO review.

## When to Use

- Before submitting a system for ISSO review
- When preparing an ATO package for a new or updated system
- When asked "is the compliance package complete?"
- After completing risk assessment, pre-deployment checks, and decision records

## Assembly Procedure

### Step 1: Artifact Inventory

Check which required artifacts exist in the target repository:

- [ ] `AGENTS.md` — behavioral contract defining agent permissions and constraints
- [ ] `docs/risk-assessment.md` — completed risk assessment (not the template)
- [ ] `docs/adr/` directory with at least `ADR-001` — architecture decision records
- [ ] `checklists/pre-deployment.md` — completed checklist with sign-off
- [ ] `docs/CODING_PRACTICES.md` — coding standards and practices
- [ ] `SECURITY.md` — vulnerability disclosure policy
- [ ] `.github/workflows/` — CI/CD pipeline definitions

For each artifact, record: exists (yes/no), last modified date, file size.

If an artifact is missing, note it as a gap and continue. Do not stop the
assembly process for missing items — the gap analysis in Step 4 will capture them.

### Step 2: Validate Artifacts

Run validators on each artifact that exists:

```bash
# Validate risk assessment structure and completeness
make validate-risk-assessment RISK_PATH=docs/risk-assessment.md

# Validate frontmatter, skills, and landscape references
make validate

# Run pre-deployment security checks
make pre-deploy
```

Record the pass/fail result of each validator. If a validator is not available
in the target repo, note "validator not available" and flag for manual review.

For `docs/risk-assessment.md`, also verify:
- All sections are filled in (not placeholder text)
- Risk scores are calculated (Likelihood x Impact)
- Treatment plans exist for Medium (6+) and above risks
- Sign-off section has names and dates

For `checklists/pre-deployment.md`, also verify:
- All 60 items have a Pass/Fail/N/A status
- Failed items have remediation notes
- Sign-off block at the bottom is completed

### Step 3: Generate Package Index

Create `docs/ato-package-index.md` with the following structure:

```markdown
# ATO Package Index

| # | Artifact | Path | NIST Control Families | Status | Last Updated | Reviewer Sign-off |
|---|----------|------|-----------------------|--------|--------------|-------------------|
| 1 | Behavioral Contract | AGENTS.md | PL, SA | Complete | YYYY-MM-DD | _________________ |
| 2 | Risk Assessment | docs/risk-assessment.md | RA, CA | Complete | YYYY-MM-DD | _________________ |
| 3 | Decision Records | docs/adr/ | SA, CM | Complete | YYYY-MM-DD | _________________ |
| 4 | Pre-Deployment Checklist | checklists/pre-deployment.md | SA, SI, CM | Complete | YYYY-MM-DD | _________________ |
| 5 | Coding Practices | docs/CODING_PRACTICES.md | SA, SI | Complete | YYYY-MM-DD | _________________ |
| 6 | Security Policy | SECURITY.md | IR, SI | Complete | YYYY-MM-DD | _________________ |
| 7 | CI/CD Pipeline | .github/workflows/ | SA, CM, SI | Complete | YYYY-MM-DD | _________________ |
```

Populate Status as: **Complete**, **Partial**, or **Missing**.

Pull last-updated dates from file frontmatter `last_updated` field if present,
otherwise use the git log date (`git log -1 --format=%ai -- <path>`).

Reference `docs/SECURITY-CONTROLS.md` for NIST control family mappings and
`docs/TRACEABILITY.md` for the control-to-document matrix.

### Step 4: Gap Analysis

Report what is missing or incomplete:

**Blocking gaps** (must fix before submission):
- Any artifact with Status = Missing
- Risk assessment that has not been validated
- Pre-deployment checklist without sign-off
- No ADRs in `docs/adr/`

**Non-blocking gaps** (should fix, will not prevent submission):
- Partial artifacts (some sections incomplete)
- Stale artifacts (last updated > 90 days ago)
- Missing NIST control coverage for system-relevant control families
- Decision records that lack a "Status: Accepted" designation

For each gap, provide:
- What is missing
- Which NIST control families are affected
- Suggested remediation action
- Which dependency skill can help (e.g., `federal-risk-assessment` for
  missing risk assessment, `federal-decision-records` for missing ADRs)

### Step 5: Present Summary

Output a readiness assessment in this format:

```
## ATO Package Readiness

**System:** [name]
**Date:** [today]
**Assessment:** [Ready for Review / Needs Attention / Not Ready]

### Artifact Summary
- [X/7] artifacts present
- [X/7] artifacts validated
- [X] blocking gaps
- [X] non-blocking gaps

### Blocking Items
- [ ] [Description] — run `[skill name]` to resolve
- [ ] [Description] — manual action required

### Non-Blocking Items
- [ ] [Description] — recommended before submission

### Next Steps
[What the user should do next based on the assessment]
```

**Assessment criteria:**
- **Ready for Review**: All 7 artifacts present, all validators pass, no blocking gaps
- **Needs Attention**: All artifacts present but some validators fail or non-blocking gaps exist
- **Not Ready**: Any blocking gap exists (missing artifacts, unsigned checklists, unvalidated risk assessment)

## Important Notes

- This skill is **read-only** — it inventories and validates but does not create or modify artifacts.
- The package index (`docs/ato-package-index.md`) is the only file this skill generates.
- All sign-off lines require human signatures. The agent cannot sign on behalf of reviewers.
- NIST control mappings come from `docs/SECURITY-CONTROLS.md` and `docs/TRACEABILITY.md`.
- Use dependency skills to fill gaps: `federal-risk-assessment`, `federal-pre-deployment-check`, `federal-decision-records`.
- **Policy reference:** `docs/SECURITY-CONTROLS.md` (control mappings), `docs/TRACEABILITY.md` (control-to-document matrix).
