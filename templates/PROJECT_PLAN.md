---
title: "Project Plan"
description: "Starting point for a new federal coding project — fill this out and let the AI agent set up everything else"
status: canonical
tier: 3
load_priority: reference-only
audience: ["developers", "tech-leads", "managers"]
---

# Project Plan

> **Instructions:** Fill out each section below. Your AI coding agent will use this to automatically set up the repository, generate compliance documentation, and create the initial project structure. Be specific — the more detail you provide, the better the agent can help.

## Project Identity

| Field | Value |
|---|---|
| **Project Name** | <!-- e.g., Benefits Portal API --> |
| **Repository Name** | <!-- e.g., benefits-portal-api --> |
| **Organization/Agency** | <!-- e.g., HHS/CMS --> |
| **Project Owner** | <!-- Name and role --> |
| **Start Date** | <!-- YYYY-MM-DD --> |
| **Target Completion** | <!-- YYYY-MM-DD or "Ongoing" --> |

## Business Objective

<!-- 2-3 sentences describing what this project does and why it matters. This becomes the README description and feeds into risk documentation. -->

## Tech Stack

| Component | Choice | Rationale |
|---|---|---|
| **Language** | <!-- e.g., Python 3.12, TypeScript 5.x, Go 1.22 --> | <!-- Why this language? --> |
| **Framework** | <!-- e.g., FastAPI, Next.js, Gin --> | <!-- Why this framework? --> |
| **Database** | <!-- e.g., PostgreSQL 16, none --> | <!-- Why this database? --> |
| **Cloud/Hosting** | <!-- cloud.gov (recommended — free sandbox for .gov/.mil), AWS GovCloud, on-prem --> | <!-- Deployment target --> |
| **CI/CD** | <!-- e.g., GitHub Actions, GitLab CI, Concourse --> | <!-- Build pipeline --> |
| **Container Runtime** | <!-- e.g., Docker, Podman, none --> | <!-- If applicable --> |

## Compliance Level

<!-- Check ONE: -->

- [ ] **FIPS Low** — Public-facing informational content, no PII, no CUI
- [ ] **FIPS Moderate** — Most federal systems: PII, financial data, internal tools
- [ ] **FIPS High** — National security systems, critical infrastructure

## Data Classification

<!-- Check all that apply: -->

- [ ] Public data only
- [ ] PII (Personally Identifiable Information)
- [ ] CUI (Controlled Unclassified Information)
- [ ] PHI (Protected Health Information)
- [ ] Financial data (FTI, payment info)
- [ ] Authentication credentials/secrets

## Key Requirements

<!-- List the 3-5 most important functional requirements. These help the agent understand what to build. -->

1. <!-- Requirement 1 -->
2. <!-- Requirement 2 -->
3. <!-- Requirement 3 -->

## Constraints

<!-- List any hard constraints the project must work within. -->

- [ ] Must use FedRAMP-authorized services only
- [ ] Must support Section 508 accessibility
- [ ] Must integrate with existing system: <!-- name -->
- [ ] Must support offline/air-gapped operation
- [ ] Other: <!-- describe -->

## Team

| Role | Person | Access Level |
|---|---|---|
| Project Owner | <!-- name --> | Admin |
| Lead Developer | <!-- name --> | Write |
| Security/ISSO | <!-- name --> | Read + Review |
| Approving Official | <!-- name --> | Read |

## Agent Environment

<!-- Where will the AI coding agent run? Check all that apply: -->

- [ ] **Local machine** — developer's workstation with CLI access
- [ ] **GitHub Codespace** — cloud-hosted dev environment
- [ ] **Sandboxed container** — isolated Docker/Podman environment
- [ ] **CI/CD only** — agent runs in GitHub Actions, no local access

<!-- What services does the agent need access to? Check all that apply: -->

- [ ] **GitHub** — push code, create PRs, manage issues
- [ ] **cloud.gov** — deploy applications
- [ ] **workshop.cloud.gov (GitLab)** — alternative code hosting
- [ ] **npm/PyPI** — publish packages
- [ ] **Container registry** — push images

<!-- The `agent-permissions` skill will configure minimal-scope credentials for each checked service. -->

## Implementation Approach

<!-- Describe at a high level how you plan to build this. 3-5 sentences. The AI agent will use this to generate ADR-001 (Initial Architecture Decision). -->

## What Happens Next

After you fill out this template and place it in your repository:

1. **The AI agent reads this file** and understands your project
2. **It runs the project-bootstrap skill** which:
   - Creates the directory structure appropriate for your stack
   - Generates AGENTS.md (behavioral contract for AI agents)
   - Copies CODING_PRACTICES.md (secure coding standards)
   - Creates ADR-001 from your implementation approach
   - Generates a risk assessment from your compliance level + data classification
   - Sets up CI/CD workflows for your stack
   - Creates SECURITY.md, CONTRIBUTING.md, LICENSE
3. **You review the generated files** and adjust as needed
4. **Start building** — the agent follows the standards automatically

The entire setup takes about 5 minutes of human input and 2 minutes of agent work.
