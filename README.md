# Agentic Coding Playbook

Practical, tool-agnostic playbook for federal employees building software with AI coding agents.

[![CI](https://github.com/gsa-tts/agentic-coding-playbook/actions/workflows/ci.yml/badge.svg)](https://github.com/gsa-tts/agentic-coding-playbook/actions/workflows/ci.yml)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

> **Note:** This playbook represents best practices. Tailor to your agency's ATO requirements and policies.

## Agentic Coding Ecosystem

This repository is part of a three-repo ecosystem:

| Repo | Purpose | When to Use |
|------|---------|-------------|
| **[Quickstart](https://github.com/GSA-TTS/agentic-coding-quickstart)** | Get running | First day setup, SBX + USAi config |
| **[Playbook](https://github.com/GSA-TTS/agentic-coding-playbook)** (you are here) | Do it right | Repo setup, standards, best practices |
| **[Patterns](https://github.com/GSA-TTS/agentic-coding-patterns)** | Share & learn | Community patterns, lessons learned |

**Your journey:** After getting your environment running (Quickstart), use this Playbook to set up your projects with good defaults, then share what you learn in Patterns.

---

## Quick Start

```bash
# 1. Copy the project plan template into your repo
cp templates/PROJECT_PLAN.md /path/to/your-repo/PROJECT_PLAN.md

# 2. Fill out PROJECT_PLAN.md — project name, tech stack, compliance level

# 3. Validate the plan
make validate-plan PLAN=/path/to/your-repo/PROJECT_PLAN.md

# 4. Check your environment
make doctor

# 5. Tell your AI agent: "Bootstrap this project from PROJECT_PLAN.md"
```

The agent reads your plan and sets up everything: `AGENTS.md`, coding standards, directory structure, CI/CD, risk assessment, and security docs. See [PLAYBOOK.md](./PLAYBOOK.md) for the full walkthrough.

---

## What This Is

A set of markdown files, templates, and validation tools that help AI coding agents follow **secure-by-default practices** when assisting federal employees with software development. Drop these files into any repository to establish consistent behavioral standards across the full development lifecycle.

A practical, living approach to secure AI-assisted development for federal
teams — usable across single-agent and multi-agent ("swarm") workflows, and
spanning backend, frontend, accessibility/Section 508, and the full development
lifecycle. It is grounded in current federal requirements and security and
software-development best practices; it is **not** authoritative federal policy,
and it does not replace your agency's own authorization decisions.

## The Two-Layer Contract

Agent behavioral rules are split into two layers:

- **Universal contract** — this repository's [`AGENTS.md`](./AGENTS.md), the
  *Federal AI Agent Behavioral Best Practices*. It applies to **every** project
  and is the single source of truth for the universal rules (core principles,
  identity, least privilege, data protection, prompt-injection defense,
  meta-constraints, engineering discipline). It is **not** copied into
  individual projects — that would let copies drift.
- **Project layer** — a thin `AGENTS.md` in each project (see
  [`templates/AGENTS.md.template`](./templates/AGENTS.md.template)) that declares
  the universal contract as a **prerequisite** and adds only project-specific
  rules.

### Making the universal contract available

Because the universal contract is not vendored per-project, each project expects
it to be provided by the environment at a conventional location:

```
~/.agentic-coding-playbook/AGENTS.md      # (override with $AGENTIC_CODING_PLAYBOOK_HOME)
```

The supported way to provision it is the **`agentic-coding-patterns` `acq`
provisioning kit**, applied by the [`acq` wrapper](https://github.com/GSA-TTS/agentic-coding-quickstart),
which selects a sandbox backend and makes the contract available to agents in a
sandboxed environment:

<https://github.com/GSA-TTS/agentic-coding-patterns/tree/main/integrations/isolation/acq-kits>

If the home path is unavailable, projects bootstrapped by this playbook ship a
self-contained probe (`scripts/ensure-contract.py`) that populates a
**git-ignored fallback cache** at `.agents/cache/AGENTS.universal.md` from the
pinned release, warning that the copy is a fallback. Presence is a
**deterministic, fail-closed** check enforced at session start, in a pre-commit
hook, and in CI — if the contract cannot be obtained, work does not proceed.
See [ADR-0002](./docs/decisions/0002-universal-vs-project-agents-md.md) and
[ADR-0003](./docs/decisions/0003-enforce-contract-prerequisite.md).

## Who This Is For

| Role | Start Here |
|------|-----------|
| **Developer** using an AI agent | [PLAYBOOK.md](./PLAYBOOK.md) — step-by-step from setup to deploy |
| **ISSO / Security Officer** | [docs/SECURITY-CONTROLS.md](./docs/SECURITY-CONTROLS.md) — 35 NIST 800-53 controls mapped |
| **Manager** approving AI agent use | [AGENTS.md](./AGENTS.md) sections 1-3 — principles, identity, authorization |
| **AI Agent** reading this repo | [CONTEXT-GUIDE.md](./CONTEXT-GUIDE.md) — tells you what to load for your task |
| **Contributor** | [CONTRIBUTING.md](./CONTRIBUTING.md) — commit conventions, skill format, review process |

---

## The Playbook Path

| Phase | What Happens | Skill |
|-------|-------------|-------|
| **0. Plan** | Human fills out [PROJECT_PLAN.md](./templates/PROJECT_PLAN.md) | — |
| **0.5. Doctor** | Agent checks environment readiness | `agent-permissions` |
| **1. Repo Setup** | Directory structure, .gitignore, CI/CD templates | `federal-repo-setup` |
| **2. Agent Config** | Generate a thin project [AGENTS.md](./AGENTS.md) that layers on the universal contract | `federal-agents-config` |
| **3. Code** | Write code following [CODING_PRACTICES.md](./docs/CODING_PRACTICES.md) | — |
| **4. Decisions** | Document architecture decisions as ADRs | `federal-decision-records` |
| **5. Risk** | Assess against threat catalog | `federal-risk-assessment` |
| **6. Pre-Deploy** | Run 62-item security checklist | `federal-pre-deployment-check` |
| **7. Deploy** | Deploy to [cloud.gov](https://cloud.gov) | `cloudgov-deploy` |

Full details: [PLAYBOOK.md](./PLAYBOOK.md)

---

## Skills — Executable Best Practice Procedures

Skills convert best practices into step-by-step workflows that any AI coding agent can follow. The behavioral contract (`AGENTS.md`) uses the [AGENTS.md standard](https://agents.md), supported by 25+ AI coding tools.

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

---

## Developer Tools

All validation and generation tools live in the `scripts/playbook_validator/` Python package (546 tests).

```bash
make help              # Show all available commands
make setup             # Install dependencies + pre-commit hooks
make test              # Run all tests
make lint              # Ruff lint + format check
make validate          # Run all document validators
make doctor            # Check environment readiness
make ci                # Reproduce full CI locally
```

| Command | What It Does |
|---------|-------------|
| `make validate-plan PLAN=path` | Validate a PROJECT_PLAN.md before bootstrap |
| `make validate-docs` | Check frontmatter on all content documents |
| `make validate-skills` | Validate skill directory structure |
| `make validate-landscape` | Validate federal AI landscape registry |
| `make generate` | Regenerate INDEX.yaml and README skills table |
| `make doctor` | Check git, GitHub CLI, cloud.gov, API keys |
| `make pre-deploy` | Run pre-deployment security checks |

**Prerequisites:** Python 3.12+, `pip install -e ".[dev]"`

---

## Framework Alignment

Every practice maps to one or more authoritative sources:

| Framework | Version | Focus |
|-----------|---------|-------|
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | 1.0 | AI risk: Govern, Map, Measure, Manage |
| [NIST SP 800-53](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Rev 5.2 | Security and privacy controls |
| [NIST SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final) | Final | Secure AI software development (SSDF) |
| [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | 1.0 | GenAI risk profile |
| [OWASP Top 10 LLM](https://genai.owasp.org/llm-top-10/) | 2025 | LLM application risks |
| [OWASP Agentic AI](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 | Agentic application risks |
| [OMB M-25-21](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf) | Apr 2025 | Federal AI governance |
| [CISA Secure by Design](https://www.cisa.gov/securebydesign) | 2025 | Secure-by-default principles |

Full catalog of 42 federal AI guidance documents: [docs/FEDERAL-AI-LANDSCAPE.md](./docs/FEDERAL-AI-LANDSCAPE.md)

---

## Repository Structure

```
agentic-coding-playbook/
├── AGENTS.md                        # Universal agent behavior rules (AGENTS.md standard)
├── PLAYBOOK.md                      # Step-by-step guide: setup → deploy
├── CONTEXT-GUIDE.md                 # Agent entry point — routes to right docs
├── INDEX.yaml                       # Machine-readable document index
├── Makefile                         # Developer commands (make help)
├── pyproject.toml                   # Python config (ruff, pytest, PyYAML)
├── docs/
│   ├── AGENT-INSTRUCTIONS.md        # Detailed tooling reference
│   ├── CODING_PRACTICES.md          # Secure coding standards
│   ├── SECURITY-CONTROLS.md         # 35 NIST 800-53 controls mapped
│   ├── FEDERAL-AI-LANDSCAPE.md      # Federal AI guidance catalog
│   └── ...                          # See docs/README.md for full index
├── data/
│   └── federal-ai-landscape.yaml    # Machine-readable guidance registry
├── scripts/
│   ├── playbook_validator/          # Python validation package (546 tests)
│   └── tests/                       # TDD test suite
├── skills/                          # 12 executable compliance procedures
├── templates/                       # PROJECT_PLAN.md, AGENTS.md.template
├── examples/                        # Completed AGENTS.md example
└── checklists/                      # 62-item pre-deployment checklist
```

---

## Where this applies

- **Agentic workflows:** single-agent and multi-agent / swarm approaches. (Note:
  multi-agent patterns add threat surface — inter-agent prompt injection, wider
  tool/credential blast radius — and our guidance there is still maturing.)
- **Across the stack:** backend, public-facing and frontend work, and
  accessibility / Section 508.
- **Security baseline:** written against a **FIPS Moderate** baseline; adapt the
  controls to your own system's impact level and ATO.
- **Lifecycle:** the full software development lifecycle.

## What this is not

- **Not authoritative federal policy** and not a substitute for your agency's
  security authorization (ATO) process. Confirm any requirement against its
  current authoritative source (NIST, OMB, your agency) — this repo is a
  practical snapshot, not the system of record.
- **Not a foundation for FIPS High or classified systems.** Consult your
  agency's security team for those contexts.
- **Not procurement guidance** — see
  [OMB M-25-22](https://www.whitehouse.gov/).
- **Community-maintained and evolving.** Methods here are community-tested, not
  guaranteed; provided as-is under [CC0 1.0](./LICENSE) with no warranty.

---

## Contributing

We welcome contributions from the federal agentic-coding community.

- **Fix it directly** — Submit a PR
- **Questions** — Open a GitHub issue or start a discussion
- **Not sure how?** — Open an issue to discuss

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details. This project uses [conventional commits](https://www.conventionalcommits.org/) and automated releases via [release-please](https://github.com/googleapis/release-please). Documentation follows our [accessibility statement](./ACCESSIBILITY.md) (Section 508).

### Share What You Learn

Discovered a useful workflow or pattern? Consider contributing it to the [Patterns repo](https://github.com/GSA-TTS/agentic-coding-patterns) so others can benefit.

## License

[CC0 1.0 Universal](./LICENSE) — public domain. Federal employees may freely use, modify, and distribute this playbook.
