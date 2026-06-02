---
name: project-bootstrap
title: "Project Bootstrap"
description: "Automatically set up a new federal coding project from a PROJECT_PLAN.md file"
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["new project", "bootstrap", "setup repo", "initialize", "scaffolding"]
dependencies: ["federal-repo-setup", "federal-agents-config", "federal-decision-records"]
---

# Skill: Project Bootstrap

Set up a complete federal coding project from a single PROJECT_PLAN.md file.

## When to Use

- Starting a new project from scratch
- User says "set up a new repo" or "bootstrap this project"
- A PROJECT_PLAN.md file exists but the repo is empty/minimal

## Prerequisites

- PROJECT_PLAN.md exists in the target repository root
- The sections Project Identity, Tech Stack, and Compliance Level must be filled in
- Access to the playbook repo (this repo) for source files

## Files Copied from Playbook to Target Repo

This skill copies the following files from the playbook repo into the target repository. **If a file already exists in the target repo, ask the user before overwriting.**

| Source (this repo) | Destination (target repo) | Purpose |
|---|---|---|
| `templates/AGENTS.md.template` | `AGENTS.md` | Agent behavioral contract (customized per project) |
| `docs/CODING_PRACTICES.md` | `docs/CODING_PRACTICES.md` | Secure coding standards |
| `CONTEXT-GUIDE.md` | `CONTEXT-GUIDE.md` | Agent context routing |
| `templates/risk-assessment.md` | `docs/risk-assessment.md` | Risk assessment (pre-filled from plan) |
| `checklists/pre-deployment.md` | `checklists/pre-deployment.md` | 62-item pre-deployment checklist |

The agent must have access to these files — either via the playbook repo cloned locally, or by fetching from the [playbook repository](https://github.com/gsa-tts/agentic-coding-playbook).

## Procedure

### Step 0: Validate Environment and Plan

Before bootstrapping, ensure the environment is ready and the plan is valid:

1. Run the environment doctor (if playbook tools available): `make doctor`
2. Validate the plan: `make validate-plan PLAN=PROJECT_PLAN.md`
   - Fix any errors (unfilled placeholders, missing sections) before proceeding

For a completed example of generated output, see `examples/AGENTS.md.example`.

### Step 1: Read and Parse PROJECT_PLAN.md

Read the PROJECT_PLAN.md file. Extract:
- `project_name` — from Project Identity table
- `language` — from Tech Stack table (Language row)
- `framework` — from Tech Stack table (Framework row)
- `database` — from Tech Stack table (Database row)
- `cloud` — from Tech Stack table (Cloud/Hosting row)
- `ci_cd` — from Tech Stack table (CI/CD row)
- `compliance_level` — from Compliance Level checkboxes (Low/Moderate/High)
- `data_classifications` — from Data Classification checkboxes
- `requirements` — from Key Requirements list
- `implementation_approach` — from Implementation Approach section

If any required field is missing, ask the user to fill it in before proceeding.

### Step 2: Create Directory Structure

Based on the language/framework, create the appropriate structure:

**Python (FastAPI/Flask/Django):**
```
src/
  app/
    __init__.py
    main.py
    routes/
    models/
    schemas/
tests/
  __init__.py
  conftest.py
docs/
  adr/
requirements.txt (or pyproject.toml)
```

**TypeScript/JavaScript (Node.js/Next.js):**
```
src/
  index.ts
  routes/
  models/
  middleware/
tests/
docs/
  adr/
package.json
tsconfig.json
```

**Go:**
```
cmd/
  main.go
internal/
  handlers/
  models/
pkg/
tests/
docs/
  adr/
go.mod
```

### Step 3: Generate AGENTS.md

Copy `templates/AGENTS.md.template` from the playbook repo to the target repo root as `AGENTS.md`. If `AGENTS.md` already exists, ask the user before overwriting.

Customize based on PROJECT_PLAN.md:
- Set the compliance level in the header
- Add project-specific prohibited actions based on data classifications
- If PII: add "MUST NOT log PII fields" to prohibited actions
- If CUI: add CUI handling requirements
- If FIPS High: add additional encryption requirements

### Step 4: Copy Standards Files

Copy these files from the playbook repo to the target repo (skip any that already exist unless the user confirms overwrite):
- `docs/CODING_PRACTICES.md` → target `docs/CODING_PRACTICES.md`
- `CONTEXT-GUIDE.md` → target `CONTEXT-GUIDE.md`
- `templates/risk-assessment.md` → target `docs/risk-assessment.md`
- `checklists/pre-deployment.md` → target `checklists/pre-deployment.md`

### Step 5: Create ADR-001 (Initial Architecture)

Create `docs/adr/001-initial-architecture.md`:

```markdown
# ADR-001: Initial Architecture

## Status
Accepted

## Context
[Extract from PROJECT_PLAN.md Business Objective + Implementation Approach]

## Decision
[Extract from PROJECT_PLAN.md Tech Stack table]

## Consequences
- [Derive from stack choices]
- [Include compliance implications from Compliance Level]
```

### Step 6: Generate Risk Assessment

Copy `templates/risk-assessment.md` to `docs/risk-assessment.md`.

Pre-fill based on PROJECT_PLAN.md:
- System name from Project Identity
- Compliance level from Compliance Level
- Data types from Data Classification
- Threat scenarios from Key Requirements + Constraints

### Step 7: Run federal-repo-setup Skill

Delegate to the `federal-repo-setup` skill to create:
- `.gitignore` with stack-appropriate patterns
- `.editorconfig` for consistent formatting
- `.pre-commit-config.yaml` with secrets scanning
- CI/CD workflow (`.github/workflows/ci.yml`) pinned to SHAs
- `SECURITY.md` — vulnerability disclosure template
- `CONTRIBUTING.md` — contribution standards
- `LICENSE` — CC0 1.0 (federal default)

See `skills/federal-repo-setup/SKILL.md` for the full procedure. If you've already run repo-setup, skip this step.

### Step 8: Generate README.md

Create `README.md` from project name + business objective in PROJECT_PLAN.md.

### Step 9: Summary Report

Output a summary of what was created:
```
Project Bootstrap Complete
========================
Project: {project_name}
Stack: {language} + {framework}
Compliance: FIPS {level}
Files created: {count}

Created:
  ✓ Directory structure ({language} conventions)
  ✓ AGENTS.md (behavioral contract)
  ✓ CODING_PRACTICES.md (secure coding standards)
  ✓ CONTEXT-GUIDE.md (agent routing)
  ✓ ADR-001 (initial architecture decision)
  ✓ Risk assessment (pre-filled from project plan)
  ✓ CI/CD workflow (pinned to SHAs)
  ✓ README.md, SECURITY.md, CONTRIBUTING.md, LICENSE

Next steps:
  1. Review generated files
  2. Start coding — the agent follows the standards automatically
  3. Run: /federal-pre-deployment-check before deploying
```

## Verification

After bootstrap, verify:
- [ ] All files exist and are non-empty
- [ ] AGENTS.md has correct compliance level
- [ ] CI workflow matches the chosen stack
- [ ] ADR-001 accurately reflects the project plan
- [ ] Risk assessment has correct data classifications
- [ ] .gitignore covers the chosen stack
- [ ] No secrets or placeholder credentials in any file
