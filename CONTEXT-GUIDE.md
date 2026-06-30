---
title: "Agent Context Loading Guide"
description: "Compact routing document for AI agents — read this FIRST to determine which documents to load for your current task"
status: canonical
tier: 1
load_priority: "always"
audience: "all"
keywords: ["context", "loading", "routing", "index", "progressive-disclosure"]
related_files: ["INDEX.yaml", "AGENTS.md", "docs/CODING_PRACTICES.md"]
review_cycle: "quarterly"
---

<!-- LOAD: always — Agents MUST read this document first. It is the entry point for all tasks. -->

# Agent Context Loading Guide

> **Purpose:** Minimize token usage while ensuring compliance. Load only what your task requires.

## Loading Rules

1. **Always load** this file and the two Tier 1 docs below
2. **Match keywords** from your task to the document triggers below
3. **Load on demand** — do NOT load all documents preemptively
4. **Security is non-negotiable** — when in doubt about a security requirement, load the relevant doc rather than guessing

## Tier 1 — Always Load (~15,415 words)

These define the behavioral contract. Load for **every task**.

| Document | Words | What It Covers |
|----------|-------|----------------|
| `AGENTS.md` | 5,759 | Agent rules: permissions, prohibitions, data handling, identity, meta-constraints |
| `PLAYBOOK.md` | 1,155 | Step-by-step guide: project setup → deployment (9 phases, 12 skills) |
| `docs/CODING_PRACTICES.md` | 6,886 | Secure coding: input validation, secrets, dependencies, architecture, TDD, SOLID |
| `docs/CODING_STANDARDS_COMPACT.md` | 450 | **Code generation shortcut** — load INSTEAD of full CODING_PRACTICES.md for routine code tasks |
| `docs/AGENT-INSTRUCTIONS.md` | 1,165 | Repo-specific tooling reference: canonical paths, validation commands, context budgets |

## Tier 2 — Load When Task Matches (~12,840 words)

| Document | Words | Load When Task Involves |
|----------|-------|------------------------|
| `docs/SECURITY-CONTROLS.md` | 7,184 | Security controls, ATO, FedRAMP, compliance assessment, ISSO review |
| `docs/AGENT-IDENTITY.md` | 5,656 | Authentication, authorization, OAuth, RBAC, delegation, identity management |

## Tier 3 — Load On Demand (~7,206 words)

| Document | Words | Load When Task Involves |
|----------|-------|------------------------|
| `docs/GETTING-STARTED.md` | 4,882 | New repo setup, CI/CD configuration, environment hardening, pre-commit hooks |
| `docs/FEDERAL-AI-LANDSCAPE.md` | — | Federal AI guidance catalog (39 entries, EOs, OMB, NIST) |
| `docs/TRACEABILITY.md` | 2,324 | Audit trail, control-to-document mapping, ISSO evidence, compliance tracing |

## Tier 4 — Reference Only (~3,928 words)

Load only when the specific activity is being performed.

| Document | Words | Load When |
|----------|-------|-----------|
| `templates/risk-assessment.md` | 1,727 | Performing a risk assessment |
| `checklists/pre-deployment.md` | 2,201 | Running pre-deployment checklist |

## Skills — Load Only When Invoked

Skills are self-contained procedures. Load the relevant skill only when executing that workflow.

| Skill | Load When |
|-------|-----------|
| `project-bootstrap` | Setting up a new project from PROJECT_PLAN.md |
| `agent-permissions` | Checking environment readiness, credential setup |
| `federal-repo-setup` | Setting up a new repository with compliance defaults |
| `federal-agents-config` | Generating a project-specific AGENTS.md |
| `code-review` | Reviewing code, creating PRs, merge workflow |
| `federal-decision-records` | Creating architecture decision records |
| `federal-risk-assessment` | Completing a risk assessment worksheet |
| `federal-security-controls-lookup` | Looking up specific NIST/OWASP controls |
| `federal-pre-deployment-check` | Running pre-deployment security checks |
| `federal-landscape-update` | Monitoring federal AI guidance updates (RSS) and refreshing the landscape registry |
| `cloudgov-deploy` | Deploying to cloud.gov |
| `ato-package` | Assembling ATO submission artifacts |

## Typical Task Profiles

| Task Type | Load | Estimated Tokens |
|-----------|------|-----------------|
| Code generation/review | Tier 1 only | ~11K |
| Security assessment | Tier 1 + SECURITY-CONTROLS.md | ~20K |
| New repo setup | Tier 1 + GETTING-STARTED.md | ~17K |
| Auth implementation | Tier 1 + AGENT-IDENTITY.md | ~18K |
| Pre-deployment review | Tier 1 + checklist + TRACEABILITY.md | ~17K |
| Full compliance audit | All Tier 1-3 | ~28K |

> **For the complete document inventory with NIST control mappings, see `INDEX.yaml`.**
