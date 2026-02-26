# Federal Agentic AI Guidance

Practical, tool-agnostic guidance for US federal employees building with AI coding agents.

> **Disclaimer:** This guidance is **informational only** and is not authoritative federal policy. Each agency must tailor these recommendations to their specific Authority to Operate (ATO) requirements, organizational policies, risk tolerance, and applicable laws and regulations. This project does not replace official NIST publications, OMB memoranda, or agency-specific guidance.

---

## What This Is

A collection of markdown files that tell AI agents **what to do** and **how to do it** when helping federal employees build software. These files can be placed in any repository to guide agent behavior across the full software development lifecycle — from project setup through deployment and ongoing operations.

This guidance is designed for **FIPS Moderate** impact level systems using **single-agent** architectures in **internal enterprise** environments.

## Who This Is For

Federal employees (typically GS-12 to GS-15) who:
- Have access to AI coding agents (Open Code, GitHub Copilot, Cursor, etc.)
- Can write basic code but may not be deeply familiar with NIST frameworks
- Need to build software that meets federal security and compliance requirements
- Want their AI agents to follow secure-by-default practices

## Framework Alignment

Every recommendation in this guidance maps to one or more authoritative sources:

| Framework | Version | Description |
|-----------|---------|-------------|
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | 1.0 (Jan 2023) | AI Risk Management Framework — Govern, Map, Measure, Manage |
| [NIST SP 800-53](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Rev 5.2.0 | Security and Privacy Controls for Information Systems |
| [NIST COSAiS](https://csrc.nist.gov/projects/cosais) | Draft 2026 | SP 800-53 Control Overlays for Securing AI Systems |
| [NIST SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final) | Final | Secure Software Development Practices for Generative AI (SSDF) |
| [NCCOE Agent Identity](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization) | Concept Paper (Feb 2026) | Software and AI Agent Identity and Authorization |
| [NIST CAISI](https://www.nist.gov/caisi/ai-agent-standards-initiative) | Initiative (Feb 2026) | AI Agent Standards Initiative |
| [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | 1.0 (Jul 2024) | Generative AI Profile for AI RMF |
| [CISA Secure by Design](https://www.cisa.gov/securebydesign) | 2025 | Secure by Design Principles for AI Systems |
| [OWASP Top 10 LLM](https://genai.owasp.org/llm-top-10/) | 2025 | Top 10 Risks for LLM Applications |
| [OWASP Agentic AI](https://genai.owasp.org/) | 2025 | Top 10 Risks for Agentic AI Applications |
| [OMB M-25-21](https://www.whitehouse.gov/) | Apr 2025 | AI Governance (replaces M-24-10) |
| [FedRAMP 20x](https://www.fedramp.gov/ai/) | 2025 | Cloud/AI Service Authorization |

## Repository Structure

```
federal-agentic-ai-guidance/
├── README.md                        # This file
├── CONTEXT-GUIDE.md                 # Agent entry point — read this FIRST for loading instructions
├── INDEX.yaml                       # Document index with load_priority metadata
├── AGENTS.md                        # Master agent behavior rules
├── CODING_PRACTICES.md              # Secure coding standards for AI-assisted development
├── CONTRIBUTING.md                  # How to contribute to this guidance
├── CHANGELOG.md                     # Version history and framework updates
├── CODEOWNERS                       # Repository ownership
├── LICENSE                          # CC0 1.0 Universal (public domain)
├── SECURITY.md                      # Security policy and responsible disclosure
├── .github/
│   ├── dependabot.yml               # Automated GitHub Actions updates
│   ├── ISSUE_TEMPLATE/              # Bug report and improvement request templates
│   ├── PULL_REQUEST_TEMPLATE.md     # PR checklist for contributors
│   └── workflows/
│       ├── ci.yml                   # Markdown lint, link check, ShellCheck, frontmatter + skills validation
│       └── release.yml              # Automated GitHub releases on version tags
├── scripts/
│   ├── config.sh                    # Centralized schema constants (status, tiers, limits)
│   ├── lib/
│   │   └── common.sh               # Shared frontmatter extraction and JSON output helpers
│   ├── generate-index.sh            # Deterministic INDEX.yaml generator (run after doc changes)
│   ├── validate-docs.sh             # Frontmatter and INDEX.yaml consistency checks
│   └── validate-skills.sh           # Agent Skills format validation
├── docs/
│   ├── GETTING-STARTED.md           # Repository setup, tooling, environment hardening
│   ├── SECURITY-CONTROLS.md         # NIST 800-53 control overlay for agentic systems
│   ├── AGENT-IDENTITY.md            # Agent identity, auth, and delegation (NCCOE aligned)
│   └── TRACEABILITY.md              # Control → document → checklist traceability matrix
├── templates/
│   ├── AGENTS.md.template           # Copy-paste AGENTS.md for any new project
│   └── risk-assessment.md           # AI risk assessment worksheet
├── examples/
│   └── AGENTS.md.example            # Completed example: federal HR portal
├── checklists/
│   └── pre-deployment.md            # Pre-deployment security checklist
└── skills/                          # Agent Skills — executable compliance procedures
    ├── federal-agents-config/             # Interactive AGENTS.md generation
    ├── federal-decision-records/          # MADR decision records with compliance extensions
    ├── federal-pre-deployment-check/      # Automated pre-deployment checklist
    ├── federal-repo-setup/                # Repository initialization with compliance defaults
    ├── federal-risk-assessment/           # Guided risk assessment worksheet
    └── federal-security-controls-lookup/  # NIST/OWASP control lookup
```

> **For AI agents:** Read `CONTEXT-GUIDE.md` first — it tells you which documents to load for your task. Only load what you need to minimize context usage.

## Start Here — By Role

### I'm a **Developer** using an AI coding agent

1. Read [docs/GETTING-STARTED.md](./docs/GETTING-STARTED.md) — set up your repo with security defaults
2. Copy [templates/AGENTS.md.template](./templates/AGENTS.md.template) into your project
3. Read [CODING_PRACTICES.md](./CODING_PRACTICES.md) — secure coding standards to follow
4. Before deploying, complete [checklists/pre-deployment.md](./checklists/pre-deployment.md)

### I'm an **ISSO/Security Officer** evaluating AI agent use

1. Read [docs/SECURITY-CONTROLS.md](./docs/SECURITY-CONTROLS.md) — 800-53 control overlay for agents
2. Complete [templates/risk-assessment.md](./templates/risk-assessment.md) for the system
3. Read [docs/AGENT-IDENTITY.md](./docs/AGENT-IDENTITY.md) — identity and authorization model
4. Review [checklists/pre-deployment.md](./checklists/pre-deployment.md) — sign-off checklist

### I'm a **Manager** approving AI agent adoption

1. Read [AGENTS.md](./AGENTS.md) Sections 1-3 — core principles, identity, and authorization
2. Review [templates/risk-assessment.md](./templates/risk-assessment.md) — understand what your team will assess
3. Skim [docs/SECURITY-CONTROLS.md](./docs/SECURITY-CONTROLS.md) Section 5 — implementation roadmap

### I'm an **AI Agent** reading this repository

1. Read [CONTEXT-GUIDE.md](./CONTEXT-GUIDE.md) — tells you what to load for your task
2. Read [AGENTS.md](./AGENTS.md) — behavioral rules (this is your contract)
3. Load additional docs only when your task matches their keywords (see CONTEXT-GUIDE.md)

## Agent Skills — Executable Compliance Procedures

This repository uses a **dual-layer architecture**:

- **Policy layer** (docs, templates, checklists): Human-readable guidance explaining *what* to do and *why* — unchanged from v0.1.x
- **Execution layer** (skills): Agent-actionable procedures in [Agent Skills format](https://agentskills.io) explaining *how* — step-by-step workflows agents can follow

Skills are compatible with Open Code, Claude Code, OpenAI Codex CLI, Gemini CLI, Cursor, VS Code, and [25+ other platforms](https://agentskills.io).

<!-- GENERATED:SKILLS_TABLE:START — do not edit, run: bash scripts/generate-index.sh -->
| Skill | Purpose | Scripts? |
|-------|---------|----------|
| `federal-agents-config` | Generate a project-specific AGENTS.md through interactive decision-tree elicitation | Yes |
| `federal-decision-records` | Create, validate, and index architectural and security decision records using MADR... | Yes |
| `federal-pre-deployment-check` | Run the federal pre-deployment security checklist against a codebase | Yes |
| `federal-repo-setup` | Initialize a code repository with federal security compliance defaults including... | Yes |
| `federal-risk-assessment` | Walk through the AI agent risk assessment worksheet interactively, helping users... | No |
| `federal-security-controls-lookup` | Look up NIST SP 800-53 controls, OWASP LLM/Agentic risks, or security keywords to find... | No |
<!-- GENERATED:SKILLS_TABLE:END -->

Skills reference policy docs by path and section — they never duplicate policy content. All scripts output structured JSON and are read-only or generative (they never modify git state or install packages).

## Scope and Limitations

**In scope:**
- Single-agent systems (one AI assistant helping one developer)
- Internal enterprise applications (not public-facing AI services)
- FIPS Moderate impact level (covers most federal internal systems)
- Software development lifecycle (design through operations)

**Out of scope (future work):**
- Multi-agent orchestration and coordination
- FIPS High or classified systems
- Public-facing AI chatbots or customer service agents
- AI model training, fine-tuning, or ML pipeline operations
- Procurement guidance (see OMB M-24-18 directly)

## Versioning

This guidance tracks evolving federal standards. Each document includes version references for the specific NIST publications it aligns with. See [CHANGELOG.md](./CHANGELOG.md) for update history.

| Date | Version | Change |
|------|---------|--------|
| 2026-02-26 | 0.3.1 | macOS compatibility fix for frontmatter parsing in generate-index.sh |
| 2026-02-26 | 0.3.0 | LLM context optimization — progressive disclosure, Quick References, tiered loading |
| 2026-02-25 | 0.2.2 | QA/QC — example §14-§15, traceability matrix, word-splitting fix |
| 2026-02-25 | 0.2.1 | Centralized config/schema — shared script library, DRY enforcement |
| 2026-02-25 | 0.2.0 | Agent Skills execution layer — 6 skills, dual-layer architecture |
| 2026-02-25 | 0.1.1 | Community infrastructure — SECURITY.md, issue templates, Dependabot |
| 2026-02-25 | 0.1.0 | Initial MVP — 5 core documents, 2 templates, 1 checklist |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to contribute. This is a community effort — feedback from federal practitioners is especially valuable.

## License

This work is dedicated to the public domain under [CC0 1.0 Universal](./LICENSE). Federal employees may freely use, modify, and distribute this guidance without restriction.
