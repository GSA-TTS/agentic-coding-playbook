# Federal Agentic AI Guidance

Practical, tool-agnostic guidance for US federal employees building with AI coding agents.

> **Disclaimer:** This guidance is **informational only** and is not authoritative federal policy. Each agency must tailor these recommendations to their specific Authority to Operate (ATO) requirements, organizational policies, risk tolerance, and applicable laws and regulations. This project does not replace official NIST publications, OMB memoranda, or agency-specific guidance.

---

## What This Is

A collection of markdown files that tell AI agents **what to do** and **how to do it** when helping federal employees build software. These files can be placed in any repository to guide agent behavior across the full software development lifecycle — from project setup through deployment and ongoing operations.

This guidance is designed for **FIPS Moderate** impact level systems using **single-agent** architectures in **internal enterprise** environments.

## Who This Is For

Federal employees (typically GS-12 to GS-15) who:
- Have access to AI coding agents (Claude Code, GitHub Copilot, Cursor, etc.)
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
├── INDEX.yaml                       # Document index — agents read this first
├── AGENTS.md                        # Master agent behavior rules
├── CODING_PRACTICES.md              # Secure coding standards for AI-assisted development
├── CONTRIBUTING.md                  # How to contribute to this guidance
├── CHANGELOG.md                     # Version history and framework updates
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
└── checklists/
    └── pre-deployment.md            # Pre-deployment security checklist
```

> **For AI agents:** Read `INDEX.yaml` first to understand the document inventory, then read `AGENTS.md` for behavioral rules.

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

1. Read [INDEX.yaml](./INDEX.yaml) — document inventory and schema
2. Read [AGENTS.md](./AGENTS.md) — behavioral rules (this is your contract)
3. Read frontmatter of relevant docs to find cross-references

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
| 2026-02-25 | 0.1.0 | Initial MVP — 5 core documents, 2 templates, 1 checklist |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to contribute. This is a community effort — feedback from federal practitioners is especially valuable.

## License

This work is dedicated to the public domain under [CC0 1.0 Universal](./LICENSE). Federal employees may freely use, modify, and distribute this guidance without restriction.
