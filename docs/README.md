# Documentation Index

Canonical index of all documentation in the agentic-coding-playbook.

## Tier 1 — Always Load

| Document | Description |
|----------|-------------|
| [AGENTS.md](../AGENTS.md) | Agent behavioral contract — permissions, prohibitions, data handling |
| [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) | Model-agnostic repo-specific reference (canonical paths, validation package, context budgets) |
| [CODING_PRACTICES.md](CODING_PRACTICES.md) | Secure coding standards for AI-assisted development |
| [CODING_STANDARDS_COMPACT.md](CODING_STANDARDS_COMPACT.md) | LLM-optimized compact coding standards (~500 words) |
| [PLAYBOOK.md](../PLAYBOOK.md) | Step-by-step guide from project setup to deployment |

## Tier 2 — Load When Needed

| Document | Description |
|----------|-------------|
| [SECURITY-CONTROLS.md](SECURITY-CONTROLS.md) | NIST 800-53 Rev 5 control overlay (35 controls mapped) |
| [AGENT-IDENTITY.md](AGENT-IDENTITY.md) | Authentication, authorization, RBAC for AI agents |
| [FEDERAL-AI-LANDSCAPE.md](FEDERAL-AI-LANDSCAPE.md) | Federal AI guidance catalog (42 entries) |

## Tier 3 — Reference

| Document | Description |
|----------|-------------|
| [GETTING-STARTED.md](GETTING-STARTED.md) | Detailed repo setup walkthrough |
| [PROMPT-INJECTION-DEFENSE.md](PROMPT-INJECTION-DEFENSE.md) | Implementation patterns for defending against prompt injection |
| [ROADMAP.md](ROADMAP.md) | Long-term plan for the playbook as a living federal resource |
| [TRACEABILITY.md](TRACEABILITY.md) | Bidirectional control-to-document matrix |

## Data Files

| File | Description |
|------|-------------|
| [federal-ai-landscape.yaml](../data/federal-ai-landscape.yaml) | Machine-readable federal AI guidance registry |
| [INDEX.yaml](../INDEX.yaml) | Document index with metadata and loading instructions |

## Navigation

- **Agent entry point:** [CONTEXT-GUIDE.md](../CONTEXT-GUIDE.md)
- **Project instructions:** [AGENTS.md](../AGENTS.md)

## Complete Document Inventory

> The tier tables above are the **human onboarding order** (what to read first).
> The table below is the complete machine inventory, generated from
> [`INDEX.yaml`](../INDEX.yaml) — its `tier` is the machine-inventory
> classification, which intentionally differs from this page's onboarding tiers
> and from `CONTEXT-GUIDE.md`'s context-budget loading tiers (three distinct
> purposes; see [tier taxonomies](#tier-taxonomies)).

<!-- GENERATED:DOC_INVENTORY:START — do not edit, run: make generate -->
| Document | Tier | Purpose |
|----------|------|---------|
| `AGENTS.md` | 1 | Best practices for AI coding agent behavior in federal development environments — includes behavioral standards, engineering discipline enforcement, and verification requirements |
| `CONTEXT-GUIDE.md` | 1 | Compact routing document for AI agents — read this FIRST to determine which documents to load for your current task |
| `PLAYBOOK.md` | 1 | Step-by-step guide for starting a federal coding project with AI agents |
| `docs/AGENT-IDENTITY.md` | 1 | Agent identity management aligned with NCCoE concept paper — authentication, authorization, delegation, and audit logging for AI agents |
| `docs/AGENT-INSTRUCTIONS.md` | 1 | Model-agnostic repo-specific reference for any AI coding agent working in this repository |
| `docs/CODING_PRACTICES.md` | 1 | Secure coding standards for AI-assisted development — input validation, secrets management, dependency security, architecture discipline, change safety, SOLID principles, OWASP/SSDF alignment |
| `docs/CODING_STANDARDS_COMPACT.md` | 1 | LLM-optimized coding standards for inclusion in code generation context (~500 words) |
| `docs/SECURITY-CONTROLS.md` | 1 | 800-53 control overlay mapping 35 security controls across 10 families to concrete AI agent behaviors and verification methods |
| `templates/CONTEXT-GUIDE.project.md` | 1 | Compact routing document for AI agents working in this project — read this FIRST to determine which documents to load for your current task |
| `docs/AI-CONTRIBUTION-POLICY.md` | 2 | Canonical policy governing AI-assisted contributions — human accountability, disclosure, provenance, verification, data handling, security review, and licensing posture for federal AI-assisted development |
| `docs/FEDERAL-AI-LANDSCAPE.md` | 2 | Canonical catalog of federal AI guidance, executive orders, standards, and legislation relevant to AI-assisted software development |
| `docs/GETTING-STARTED.md` | 2 | Step-by-step guide for setting up a development repository with security controls for AI coding agents |
| `docs/TRACEABILITY.md` | 2 | Bidirectional mapping between NIST 800-53 controls, OWASP risks, document sections, and checklist items |
| `templates/SKILL.md.template` | 2 | One sentence describing what this skill does and when to use it |
| `templates/doc.md.template` | 2 | One-line summary of what this document covers |
| `checklists/pre-deployment.md` | 3 | 62-item security checklist for deploying AI-assisted code — secrets, input validation, auth, dependencies, testing, infrastructure, accessibility |
| `docs/PROMPT-INJECTION-DEFENSE.md` | 3 | Implementation patterns for defending against prompt injection in AI-assisted federal applications |
| `docs/ROADMAP.md` | 3 | Long-term plan for the Agentic Coding Playbook — making it a living resource for federal engineers learning agentic coding |
| `examples/AGENTS.md.example` | 3 | Completed example showing a thin, project-specific AGENTS.md layered on the universal contract for a hypothetical federal HR benefits portal |
| `templates/AGENTS.md.template` | 3 | Copy-paste template for a thin, project-specific AGENTS.md that layers on top of the universal Federal AI Agent behavioral contract |
| `templates/PROJECT_PLAN.md` | 3 | Starting point for a new federal coding project — fill this out and let the AI agent set up everything else |
| `templates/privacy-impact-assessment.md` | 3 | PIA template for federal systems using AI components — data flows, privacy risks, mitigations, and compliance sign-off |
| `templates/risk-assessment.md` | 3 | Structured risk assessment template aligned with NIST AI RMF — threat analysis, control assessment, and sign-off |
<!-- GENERATED:DOC_INVENTORY:END -->

### Tier taxonomies

This repository uses the word "tier" for three **distinct** purposes; they are
curated independently on purpose and are not expected to match:

| View | Source | Meaning |
|------|--------|---------|
| Machine inventory tier | `INDEX.yaml` frontmatter `tier` | Load priority for an agent building context from a cold start |
| Onboarding tier | this page's tables above | Pedagogical reading order for a new human contributor |
| Context-budget tier | `CONTEXT-GUIDE.md` | Token-budget loading strategy (word-count aware) |

A document can legitimately sit in a different tier in each view (e.g.
`SECURITY-CONTROLS.md` is machine-inventory tier 1 but onboarding tier 2). The
generated inventory above reflects only the machine-inventory tier.
