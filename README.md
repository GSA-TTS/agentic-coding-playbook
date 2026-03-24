# Federal Agentic AI Playbook

[![CI — Documentation Quality](https://github.com/GSA-TTS/agentic-ai-playbook/actions/workflows/ci.yml/badge.svg)](https://github.com/GSA-TTS/agentic-ai-playbook/actions/workflows/ci.yml)
[![License: CC0 1.0](https://img.shields.io/badge/license-CC0%201.0-blue.svg)](./LICENSE)
[![Status: Reference Material](https://img.shields.io/badge/status-reference%20material-informational)](#what-this-is-not)

Practical, tool-agnostic **reference material and implementation patterns** for US federal employees building with AI coding agents.

> **Important:** This repository provides **non-binding reference material, examples, and implementation patterns**.
> It does **not** establish policy, requirements, or official guidance.
> It is not a substitute for agency counsel, security review, authorizing officials, or authoritative federal sources.
> Each agency is responsible for determining its own compliance obligations, risk posture, and approval processes.

---

## Quick Start (5 min)

### For most contributors

```bash
make bootstrap
make fix
make verify
````

What that does:

* `make bootstrap` installs hooks and prepares local script permissions
* `make fix` regenerates derived content and runs local hooks
* `make verify` runs the CI-like validation flow before you push

### First-time manual setup

If you are not using the `Makefile` yet:

```bash
brew install pre-commit shellcheck
pre-commit install
bash scripts/sync-generated-content.sh
prek run --all-files
```

### Typical workflow

1. Read [docs/GETTING-STARTED.md](./docs/GETTING-STARTED.md).
2. Copy [templates/AGENTS.md.template](./templates/AGENTS.md.template) into your repository as `AGENTS.md`.
3. Read [docs/CODING-PRACTICES.md](./docs/CODING-PRACTICES.md) and align your repo defaults.
4. Before shipping, complete [checklists/pre-deployment.md](./checklists/pre-deployment.md).

> **Commit note:** hooks may regenerate or fix derived files such as `INDEX.yaml` or generated README sections. If that happens, stage the updated files and run `git commit` again.

---

## What This Is

A collection of markdown files, templates, and executable skills that **demonstrate patterns and approaches** for guiding AI agent behavior across the software development lifecycle — from project setup through deployment and ongoing operations.

These materials are intended for:

* **FIPS Moderate** impact level systems
* **Single-agent architectures**
* **Internal enterprise environments**

## What This Is Not

* Not federal policy, directive, or official guidance
* Not a substitute for NIST, OMB, FedRAMP, CISA, or agency-specific requirements
* Not an approved architecture or reference implementation
* Not sufficient for ATO authorization without agency review
* Not a source of binding control interpretations or legal determinations

This repository supports **learning, experimentation, internal development, and repeatable implementation patterns**.

---

## Who This Is For

Federal employees (typically GS-12 to GS-15) who:

* Use AI coding agents (Open Code, GitHub Copilot, Cursor, Claude Code, etc.)
* Can write basic code but are not deeply familiar with NIST frameworks
* Need to build software aligned with federal security expectations
* Want AI-assisted workflows that are secure-by-default

---

## Framework Alignment

Examples and patterns in this playbook map to authoritative sources, including NIST AI RMF, NIST SP 800-53, NIST SP 800-218A, OWASP guidance for LLM and agentic systems, CISA Secure by Design, and relevant OMB and FedRAMP materials.

Where this repository cites or derives patterns from authoritative sources, those sources remain authoritative. This repository packages reference material and executable skills for practical internal use; it does not replace the underlying source material.

See individual documents for detailed traceability and control mappings.

---

## Repository Structure

<!-- GENERATED:REPO_STRUCTURE:START -->
<!-- source: scripts/generate-readme-structure.sh -->
<!-- do not edit manually -->
```text
agentic-ai-playbook/
├── README.md
├── CONTEXT-GUIDE.md
├── INDEX.yaml
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODEOWNERS
├── LICENSE
├── .pre-commit-config.yaml
├── .github/workflows/
├── scripts/
│   ├── check-executables.sh
│   ├── config.sh
│   ├── export-agent-bundle.sh
│   ├── generate-index.sh
│   ├── generate-readme-changelog.sh
│   ├── generate-readme-skills.sh
│   ├── generate-readme-structure.sh
│   ├── run-shellcheck.sh
│   ├── sync-generated-content.sh
│   ├── validate-docs.sh
│   ├── validate-skills.sh
│   └── lib/common.sh
├── docs/
│   └── CODING-PRACTICES.md
├── templates/
│   └── agent-bundle/
├── examples/
├── checklists/
└── skills/
    ├── federal-agents-config/
    ├── federal-decision-records/
    ├── federal-pre-deployment-check/
    ├── federal-repo-setup/
    ├── federal-risk-assessment/
    └── federal-security-controls-lookup/
```
<!-- GENERATED:REPO_STRUCTURE:END -->

> **For AI agents:** Read `CONTEXT-GUIDE.md` first. Load only what is required.

---

## Start Here — By Role

### Developer

1. Read [docs/GETTING-STARTED.md](./docs/GETTING-STARTED.md).
2. Copy [templates/AGENTS.md.template](./templates/AGENTS.md.template).
3. Follow [docs/CODING-PRACTICES.md](./docs/CODING-PRACTICES.md).
4. Complete [checklists/pre-deployment.md](./checklists/pre-deployment.md).

### Security / ISSO

1. Review [docs/SECURITY-CONTROLS.md](./docs/SECURITY-CONTROLS.md).
2. Complete [templates/risk-assessment.md](./templates/risk-assessment.md).
3. Validate the identity and authorization model in [docs/AGENT-IDENTITY.md](./docs/AGENT-IDENTITY.md).

### Manager

1. Review [AGENTS.md](./AGENTS.md) (Sections 1–3).
2. Understand risk and adoption considerations via [templates/risk-assessment.md](./templates/risk-assessment.md).
3. Review the implementation approach in [docs/SECURITY-CONTROLS.md](./docs/SECURITY-CONTROLS.md).

### AI Agent

1. Read [CONTEXT-GUIDE.md](./CONTEXT-GUIDE.md).
2. Follow [AGENTS.md](./AGENTS.md).
3. For coding tasks, load project-local coding standards first, then `.agent-skills/docs/CODING-PRACTICES.md` if present, then the canonical [docs/CODING-PRACTICES.md](./docs/CODING-PRACTICES.md).
4. Load additional documents only when required.

---

## Contributor Workflow

For routine local work:

```bash
make fix
make verify
```

If you are working without `make`, the equivalent flow is:

```bash
bash scripts/sync-generated-content.sh
prek run --all-files
```

Use the CI-like validation flow before pushing changes:

```bash
bash scripts/sync-generated-content.sh --check
bash scripts/validate-docs.sh
bash scripts/validate-skills.sh
bash scripts/run-shellcheck.sh
prek run --all-files
```

> **Note:** generated content is intentional in this repository. A failed first commit is normal if hooks update `INDEX.yaml` or README-generated sections.

---

## Exporting an Agent Bundle

This repository can export a portable bundle for use in local repositories or sandboxed agent environments.

The export is intended to package **non-binding reference material, templates, and selected executable skills** into a deterministic, local-first structure. It is a portability mechanism for internal use. It does **not** convert this repository into official guidance or change the non-binding status of its contents.

### Most common export flow

Preview the export first:

```bash
make export-dry-run EXPORT_TARGET=../my-repo
```

Then export into the target repository:

```bash
make export EXPORT_TARGET=../my-repo EXPORT_OVERWRITE=true
```

### What gets exported

An exported bundle can include:

* `AGENTS.md` generated from `templates/AGENTS.md.template`
* `.agent-skills/skills/` with selected skills
* `.agent-skills/docs/CODING-PRACTICES.md` as a compact coding reference companion for local and sandboxed agent use
* optional supporting files from `templates/` and `checklists/`
* `.agent-skills/manifest.json` describing what was exported
* `.agent-skills/README.md` with usage notes for local or sandboxed environments

### Common examples

Export the recommended default profile into another repository:

```bash
make export EXPORT_TARGET=../my-repo EXPORT_OVERWRITE=true
```

Preview an export into another repository:

```bash
make export-dry-run EXPORT_TARGET=../my-repo
```

Export all available bundled skills:

```bash
make export EXPORT_TARGET=../my-repo EXPORT_PROFILE=all EXPORT_OVERWRITE=true
```

Export to a standalone bundle directory instead of directly into another repository:

```bash
make export EXPORT_OUTPUT=./dist/agent-bundle EXPORT_OVERWRITE=true
```

Advanced custom example:

```bash
make export \
  EXPORT_TARGET=../my-repo \
  EXPORT_PROJECT_NAME="Internal API" \
  EXPORT_SKILLS="federal-agents-config federal-pre-deployment-check" \
  EXPORT_INCLUDES="templates/risk-assessment.md checklists/pre-deployment.md" \
  EXPORT_OVERWRITE=true
```

To see available skills:

```bash
bash scripts/export-agent-bundle.sh --list-skills
```

### Profiles

* `minimal` — `AGENTS.md` plus the exported coding practices companion
* `core` — recommended default bundle for most internal teams
* `all` — every available skill plus common supporting files

### Notes for sandboxed agent environments

* The bundle does not require network access.
* Exported files are copied, not symlinked.
* The manifest provides a machine-readable inventory for sandbox loaders.
* The bundle can be mounted read-only in a restricted environment.
* Skills remain scoped operational procedures and reference-derived implementation helpers, not unrestricted code execution entrypoints.

---

## Agent Skills — Executable Procedures

This repository uses a **dual-layer architecture**:

* **Reference layer:** explains *what* and *why*
* **Execution layer (skills):** defines *how*

<!-- GENERATED:SKILLS_TABLE:START -->
<!-- do not edit manually; run: sh scripts/generate-readme-skills.sh -->
| Skill | Purpose | Scripts? |
|-------|---------|----------|
| `federal-agents-config` | Generate a project-specific AGENTS.md through interactive decision-tree elicitation | Yes |
| `federal-decision-records` | Create, validate, and index architectural and security decision records using MADR... | Yes |
| `federal-pre-deployment-check` | Run the federal pre-deployment security checklist against a codebase | Yes |
| `federal-repo-setup` | Initialize a code repository with federal security compliance defaults including... | Yes |
| `federal-risk-assessment` | Walk through the AI agent risk assessment worksheet interactively, helping users... | No |
| `federal-security-controls-lookup` | Look up NIST SP 800-53 controls, OWASP LLM/Agentic risks, or security keywords to find... | No |
<!-- GENERATED:SKILLS_TABLE:END -->

Skills reference supporting documents by path and section rather than duplicating policy content. Scripts are read-only or generative and do not install packages or silently modify git history.

---

## Scope and Limitations

### In Scope

* Single-agent systems
* Internal enterprise applications
* FIPS Moderate environments
* Software development lifecycle activities

### Out of Scope

* Multi-agent orchestration
* FIPS High or classified systems
* Public-facing AI services
* Model training or fine-tuning pipelines
* Procurement policy

---

## Versioning

This playbook tracks evolving federal standards.
See [CHANGELOG.md](./CHANGELOG.md) for full history.

<!-- GENERATED:CHANGELOG_SUMMARY:START -->
<!-- do not edit manually; run: sh scripts/generate-readme-changelog.sh -->

## Recent Changes

## [0.4.0] - 2026-03-24

### Added

* Agent bundle export workflow for local-first and sandboxed agent use
* `scripts/export-agent-bundle.sh` for deterministic, offline-safe exports
* `.agent-skills/docs/CODING-PRACTICES.md` included in exported bundles
* `make export-dry-run` to preview bundle exports without writing files
* `make doctor` to validate local tooling and script readiness

### Changed

* `make verify` is now the primary validation command (replaces `make check`)
* Export workflow standardized around `EXPORT_TARGET`
* `make export` help output streamlined for common usage
* Repository language clarified to reinforce non-authoritative positioning

### Fixed

* macOS compatibility in `scripts/export-agent-bundle.sh` (removed bash-specific features)
* Broken references to `docs/CODING-PRACTICES.md`
* Documentation inconsistencies across contributor workflows

### Documentation

* README, CONTRIBUTING, and setup docs aligned with current command surface
* Maintainer release guidance added to `CONTRIBUTING.md`

### Internal

* Added maintainer-only release targets (`make release-check`, `make release-tag`)
* Formalized release readiness checks and tagging process
* Replaced shell-based release parsing with Python implementation

---

[View full changelog](./CHANGELOG.md)

<!-- GENERATED:CHANGELOG_SUMMARY:END -->

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

This work is dedicated to the public domain under [CC0 1.0 Universal](./LICENSE).
