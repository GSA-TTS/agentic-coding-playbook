---
title: "Agent Instructions"
description: "Model-agnostic repo-specific reference for any AI coding agent working in this repository"
status: canonical
tier: 1
last_updated: "2026-06-01"
load_priority: always
audience: ["developers", "agents"]
keywords: ["agent", "instructions", "commands", "paths", "skills", "validation"]
---

# Agent Instructions

Model-agnostic reference for any AI coding agent working in this repository. Read this alongside [AGENTS.md](../AGENTS.md) (behavioral contract) and [CONTEXT-GUIDE.md](../CONTEXT-GUIDE.md) (document routing).

## Quick Reference

```bash
# Validation (Python package)
PYTHONPATH=scripts python3 -m playbook_validator validate-docs
PYTHONPATH=scripts python3 -m playbook_validator validate-skills
PYTHONPATH=scripts python3 -m playbook_validator validate-landscape
PYTHONPATH=scripts python3 -m playbook_validator validate-adrs --dir docs/adr
PYTHONPATH=scripts python3 -m playbook_validator validate-plan --path PROJECT_PLAN.md
PYTHONPATH=scripts python3 -m playbook_validator validate-risk-assessment --path templates/risk-assessment.md
PYTHONPATH=scripts python3 -m playbook_validator doctor [--json]
PYTHONPATH=scripts python3 -m playbook_validator audit-repo
PYTHONPATH=scripts python3 -m playbook_validator pre-deploy

# Generation
make generate            # Generate INDEX.yaml + README skills table
make generate-check    # Verify INDEX.yaml is up to date

# Testing
PYTHONPATH=scripts python3 -m pytest scripts/tests/ -v

# Local CI (mirrors .github/workflows/ci.yml — ruff, markdownlint, pytest,
# validators, INDEX freshness, Semgrep SAST, pip-audit SCA). Useful for a fast
# inner loop or when GitHub Actions is unavailable. Builds an invocation-scoped
# CA bundle so it works behind a TLS-intercepting proxy (e.g. ZScaler); runs
# pip-audit in an ephemeral venv to match CI isolation.
scripts/ci-local.sh              # run everything
scripts/ci-local.sh --no-net    # skip the network steps (Semgrep, pip-audit)

# Federal AI Landscape Monitoring (Phase 1)
python scripts/check_federal_landscape_rss.py           # Check RSS feeds for new publications
python scripts/check_federal_landscape_rss.py | \
  python scripts/compare_landscape_versions.py          # Check and compare against registry
```

## Canonical Paths

| Concern | Path |
|---------|------|
| **Agent behavioral contract** | `AGENTS.md` |
| **This instructions file** | `docs/AGENT-INSTRUCTIONS.md` |
| **Secure coding standards** | `docs/CODING_PRACTICES.md` |
| **Step-by-step playbook** | `PLAYBOOK.md` |
| **Context routing** | `CONTEXT-GUIDE.md` |
| **Document index** | `INDEX.yaml` |
| **Federal AI landscape** | `data/federal-ai-landscape.yaml` + `docs/FEDERAL-AI-LANDSCAPE.md` |
| **NIST security controls** | `docs/SECURITY-CONTROLS.md` |
| **Agent identity/auth** | `docs/AGENT-IDENTITY.md` |
| **Risk traceability** | `docs/TRACEABILITY.md` |
| **Skills (procedures)** | `skills/*/SKILL.md` |
| **Templates** | `templates/` |
| **Validation package** | `scripts/playbook_validator/` |
| **Tests** | `scripts/tests/` |
| **Schema constants** | `scripts/playbook_validator/config.py` |

## Document Architecture

This repo uses a **tiered loading** system to minimize token usage:

| Tier | Load When | Key Documents |
|------|-----------|---------------|
| **1 — Always** | Every task | AGENTS.md, CODING_PRACTICES.md, PLAYBOOK.md |
| **2 — On demand** | Task matches keywords | SECURITY-CONTROLS.md, AGENT-IDENTITY.md, FEDERAL-AI-LANDSCAPE.md |
| **3 — Reference** | Explicitly needed | GETTING-STARTED.md, TRACEABILITY.md, templates/ |

## Skills (Executable Workflows)

Skills are structured procedures in `skills/*/SKILL.md`. Each has YAML frontmatter with trigger keywords.

<!-- GENERATED:SKILLS_TABLE:START — do not edit, run: make generate -->
| Skill | Purpose | Scripts? |
|-------|---------|----------|
| `agent-permissions` | Detect available credentials, diagnose gaps against PROJECT_PLAN.md, and guide setup... | No |
| `ato-package` | Collect and verify all ATO submission artifacts into a review-ready package | No |
| `cloudgov-deploy` | Deploy applications to cloud.gov — sandbox setup, manifest generation, CI/CD pipeline | No |
| `code-review` | Review AI-assisted code changes and create compliant pull requests with proper attribution | No |
| `federal-agents-config` | Generate a project-specific AGENTS.md through interactive decision-tree elicitation. | Yes |
| `federal-decision-records` | Create, validate, and index architectural and security decision records using MADR... | No |
| `federal-landscape-update` | Monitor RSS feeds for federal AI guidance updates, compare against current registry,... | No |
| `federal-pre-deployment-check` | Run the 62-item federal pre-deployment security checklist against a codebase. | Yes |
| `federal-repo-setup` | Initialize a code repository with federal security compliance defaults including... | No |
| `federal-risk-assessment` | Walk through the AI agent risk assessment worksheet interactively, helping users... | No |
| `federal-security-controls-lookup` | Look up NIST SP 800-53 controls, OWASP LLM/Agentic risks, or security keywords to find... | No |
| `project-bootstrap` | Automatically set up a new federal coding project from a PROJECT_PLAN.md file | No |
<!-- GENERATED:SKILLS_TABLE:END -->

## Frontmatter Schema

All content `.md` files must have YAML frontmatter:

```yaml
---
title: "Document Title"           # Required
description: "One-line summary"   # Required
status: canonical                 # Required: canonical | draft | deprecated
tier: 2                           # Required: 1 | 2 | 3
load_priority: on-demand          # Optional: always | task-context | on-demand | reference-only
audience: ["developers", "agents"] # Optional
keywords: ["security", "NIST"]    # Optional — used for context routing
---
```

## Federal AI Landscape

The `data/federal-ai-landscape.yaml` registry tracks 42 federal AI guidance documents. Key active references:

- **EO 14179** — Removing Barriers to AI Leadership (Jan 2025)
- **M-25-21** — AI Governance (Apr 2025, compliance deadline Apr 2026)
- **M-25-22** — AI Acquisition (Apr 2025)
- **M-26-04** — Unbiased AI Principles (Dec 2025)
- **NIST AI RMF 1.0, SP 800-218A, AI 600-1**
- **OWASP Agentic Top 10 2026**

Full catalog: `docs/FEDERAL-AI-LANDSCAPE.md`

## Context Budget

| Task Type | Token Budget | Load |
|-----------|-------------|------|
| Quick question | ~800 | CONTEXT-GUIDE.md only |
| Add guidance entry | ~2,000 | CONTEXT-GUIDE + FEDERAL-AI-LANDSCAPE.md |
| Create new skill | ~2,500 | CONTEXT-GUIDE + PLAYBOOK.md + example SKILL.md |
| Security review | ~4,000 | Tier 1 + SECURITY-CONTROLS.md + TRACEABILITY.md |
| Full project setup | ~6,000 | Tier 1 + Tier 2 + PLAYBOOK.md + relevant skills |

## Validation Package

The `scripts/playbook_validator/` Python package provides all validation and generation logic:

| Module | Purpose |
|--------|---------|
| `frontmatter.py` | YAML frontmatter parsing via PyYAML |
| `config.py` | Schema constants + validation helpers |
| `output.py` | ResultCollector (JSON + text output) |
| `validate_docs.py` | Document frontmatter validation |
| `validate_skills.py` | Skill directory validation |
| `validate_landscape.py` | Federal AI landscape registry validation |
| `validate_adrs.py` | ADR file validation |
| `doctor.py` | Environment readiness checker |
| `audit_repo.py` | Federal compliance baseline audit |
| `generate_index.py` | INDEX.yaml generation |
| `pre_deploy_checks.py` | Pre-deployment security checks |

### Maintenance Workflows

#### Federal AI Landscape Monitoring

**Phase 1** (Implemented): Automated RSS monitoring foundation

1. **Check RSS feeds** for new federal AI guidance:
   ```bash
   python scripts/check_federal_landscape_rss.py
   ```

   Monitors:
   - Federal Register (NIST publications)
   - White House actions feed
   - NIST CSRC publications
   - OWASP GenAI releases

   Outputs JSON with `new_entries` list. Exit code 0 if new entries found, 1 if none.

2. **Compare against registry** to detect version/status changes:
   ```bash
   python scripts/check_federal_landscape_rss.py | python scripts/compare_landscape_versions.py
   ```

   Detects:
   - Version updates (e.g., draft → final)
   - Status changes (active → revoked)
   - New publications not yet in `data/federal-ai-landscape.yaml`

3. **State persistence**: Last-seen entry IDs stored in `data/.landscape-rss-state.json`

**Phase 2-4** (Planned): See `skills/federal-landscape-update/SKILL.md` for diff reporting, skill integration, and review workflow.

**Manual review required**: All detected changes must be reviewed by humans before updating the registry or documentation.

## Self-Check Quality Gate

Before completing any task:

- [ ] Frontmatter present and valid on new/modified `.md` files
- [ ] INDEX.yaml regenerated if documents changed
- [ ] Tests pass
- [ ] No real credentials in any file
- [ ] NIST controls cited where applicable
- [ ] Wiring complete + downstream consumers updated (§14.4)
- [ ] Deferred / out-of-scope work captured as tracked issues (§9.3, §15.5)
