---
title: "Federal AI Coding Playbook"
description: "Step-by-step guide for starting a federal coding project with AI agents"
tier: 1
load_priority: always
audience: ["developers", "managers", "agents"]
status: canonical
related:
  - AGENTS.md
  - docs/CODING_PRACTICES.md
  - CONTEXT-GUIDE.md
---

# Federal AI Coding Playbook

A step-by-step path from zero to deployable federal software with AI coding agents.

## Quick Start (5 minutes)

```bash
# 1. Clone the playbook repo (or download the template files)
git clone https://github.com/gsa-tts/agentic-coding-playbook.git

# 2. Copy the project plan template to your repo
cp agentic-coding-playbook/templates/PROJECT_PLAN.md /your-repo/PROJECT_PLAN.md

# 3. Fill out PROJECT_PLAN.md (the ONE thing the human does)
#    - Project name, tech stack, compliance level, data types

# 4. Tell your AI agent: "Bootstrap this project from PROJECT_PLAN.md"
#    The agent copies standards files from the playbook and sets up:
#    - a thin project AGENTS.md (referencing the universal contract),
#      CODING_PRACTICES.md, directory structure
#    - CI/CD, risk assessment, ADRs, security docs

# 5. Start coding — the agent follows the standards automatically
```

The bootstrap skill copies key files from this playbook into your repo (a thin project AGENTS.md, CODING_PRACTICES.md, a project-scoped CONTEXT-GUIDE.md, risk assessment template, pre-deployment checklist). The universal `AGENTS.md` is **not** copied — it is expected to be available to your agent globally, and the thin project AGENTS.md references it as a prerequisite. See the [project-bootstrap skill](skills/project-bootstrap/SKILL.md) for the full file list.

## The Path

### Phase 0: Write Your Project Plan

**Template:** `templates/PROJECT_PLAN.md`

This is the ONE thing the human does. Fill out:
- Project name and business objective
- Tech stack (language, framework, database, cloud)
- Compliance level (FIPS Low/Moderate/High)
- Data classification (PII, CUI, etc.)
- Key requirements and constraints
- Team and roles

Everything else can be automated by the AI agent.

**Skill:** `project-bootstrap` — reads your PROJECT_PLAN.md and runs all subsequent phases automatically.

### Phase 0.5: Environment Doctor

**Skill:** `agent-permissions` | **Script:** `make doctor`

Before the agent can interact with GitHub, cloud.gov, or other services, it needs credentials. The environment doctor:
- **Detects** available tools and credentials (env vars, CLI auth status, git remotes)
- **Diagnoses** gaps against your PROJECT_PLAN.md requirements
- **Guides** you with one-liner fix commands for each missing item

```bash
make doctor              # Human-readable checklist
make doctor-json         # Machine-readable for CI/automation
```

The agent running in a sandbox cannot create tokens itself — the doctor tells you exactly what to set up, then verifies it works. Run it first, fix any `[FAIL]` items, then proceed to Phase 1.

### Phase 1: Repository Setup

**Skill:** `federal-repo-setup`

What happens:
- Creates standard directory structure
- Adds required files: LICENSE, SECURITY.md, CONTRIBUTING.md
- Configures .gitignore for federal patterns (no PII, no credentials)
- Sets up CI/CD templates with security scanning

**Key files produced:**
- `.gitignore` — federal-safe defaults
- `SECURITY.md` — vulnerability disclosure process
- `CONTRIBUTING.md` — contribution requirements

### Phase 2: Agent Configuration

**Skill:** `federal-agents-config`

What happens:
- Generates or validates your thin project AGENTS.md (references the universal contract as a prerequisite)
- Ensures NIST 800-53 control mappings are present
- Configures project-specific prohibited actions
- Sets up human-in-the-loop approval gates

**Key files produced/validated:**
- `AGENTS.md` — thin project-layer contract for AI agents (universal rules referenced, not copied)
- `CONTEXT-GUIDE.md` — tiered loading configuration

### Phase 3: Write Code

**Skill:** `code-review` | **Reference:** `docs/CODING_PRACTICES.md`

The AI agent follows coding practices from AGENTS.md and creates compliant PRs:
- Input validation with schemas at all boundaries
- Secrets via environment variables, never hardcoded
- Dependencies pinned to exact versions
- AI assistance documented (PR-level recommended, commit attribution optional)
- Code review checklist before merge (hallucination check, security review)

### Phase 4: Document Decisions

**Skill:** `federal-decision-records`

What happens:
- Creates Architecture Decision Records (ADRs) for significant choices
- Maintains decision index for traceability
- Links decisions to NIST controls where applicable

### Phase 5: Assess Risk

**Skill:** `federal-risk-assessment`

What happens:
- Evaluates system against threat catalog
- Maps risks to NIST 800-53 controls
- Produces risk assessment document for ATO package

### Phase 6: Pre-Deployment Check

**Skill:** `federal-pre-deployment-check`

What happens:
- Runs 62-item security checklist
- Verifies NIST control implementation
- Checks for common federal compliance gaps
- Produces deployment readiness report

### Phase 7: Deploy to cloud.gov

**Skill:** `cloudgov-deploy`

What happens:
- Generates manifest.yml for your stack
- Deploys to cloud.gov sandbox (free for all .gov/.mil emails)
- Sets up database and storage services
- Creates CI/CD pipeline for automatic deployments

**Why cloud.gov:** Any federal employee with a .gov or .mil email can [sign up for a free sandbox](https://cloud.gov/sign-up/) in minutes. cloud.gov is FedRAMP Authorized, inherits ~80% of NIST 800-53 controls, and deploys with a single `cf push`. No Kubernetes, no Terraform, no infrastructure management needed for prototyping.

> **Sandbox limitation:** Sandbox contents are cleared every 90 days. For persistent deployments, your agency needs a cloud.gov organization. Do not deploy with real data to the sandbox.

## What the AI Agent Gets

When an AI agent opens a repository with these files, it automatically:

1. **Reads `AGENTS.md`** — understands what it can and cannot do
2. **Reads `docs/CODING_PRACTICES.md`** — knows how to write compliant code
3. **Checks `CONTEXT-GUIDE.md`** — loads additional context based on the current task
4. **Uses skills** — follows structured procedures for setup, documentation, security

No special configuration needed. The files ARE the configuration.

## Skill Reference

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

## Framework Alignment

Every step in this playbook maps to established frameworks:

| Phase | NIST 800-53 | SSDF | AI RMF |
|---|---|---|---|
| Repo Setup | CM-2, CM-3 | PW.1, PS.1 | Map 1.1 |
| Agent Config | AC-3, AU-2 | PO.2 | Govern 1.2 |
| Write Code | SI-10, SC-8 | PW.5, PW.6 | Manage 2.2 |
| Document Decisions | CM-3, SA-11 | PW.4 | Map 3.3 |
| Assess Risk | RA-3, RA-5 | RV.1 | Measure 2.1 |
| Pre-Deploy | CA-2, CA-7 | RV.2, RV.3 | Manage 4.1 |
| Deploy | SC-8, SC-13 | PW.9 | Manage 3.1 |

## Complementary Tools

### GSA-TTS hello-ato

[hello-ato](https://github.com/gsa-tts/hello-ato) is a GSA-TTS copier template that scaffolds ATO-ready projects with cloud.gov Terraform IaC. If your agency uses cloud.gov, you can use hello-ato for initial scaffolding, then add this playbook's AGENTS.md and CODING_PRACTICES.md on top:

```bash
# Option A: Start with hello-ato, add playbook
uvx copier copy --trust gh:GSA-TTS/hello-ato my-project
cp AGENTS.md CODING_PRACTICES.md CONTEXT-GUIDE.md my-project/

# Option B: Start with this playbook (works with any cloud)
# Fill out PROJECT_PLAN.md → AI agent runs project-bootstrap skill
```

hello-ato and this playbook are complementary: hello-ato handles cloud.gov infrastructure, this playbook handles AI agent behavior and secure coding practices.
