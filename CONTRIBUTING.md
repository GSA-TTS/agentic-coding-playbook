# Contributing

Thank you for your interest in improving the Agentic Coding Playbook! This is an internal repository that benefits from input by practitioners across GSA.

## Ecosystem Overview

This repo is one of three in the agentic coding ecosystem:

| Repo | Focus | Typical Contributions |
|------|-------|----------------------|
| **[Quickstart](https://github.com/GSA-TTS/agentic-coding-quickstart)** | Environment setup | SBX fixes, troubleshooting docs |
| **[Playbook](https://github.com/GSA-TTS/agentic-coding-playbook)** (you are here) | Standards & practices | Coding standards, skills, templates |
| **[Patterns](https://github.com/GSA-TTS/agentic-coding-patterns)** | Community sharing | Workflows, lessons learned, examples |

**Not sure where your contribution belongs?** Ask in the agentic-coding Slack channel.

## Getting Help

- **Questions:** Ask in the agentic-coding Slack channel
- **Bugs/improvements:** Open a GitHub issue or submit a PR
- **Security issues:** See [SECURITY.md](SECURITY.md) — direct fixes preferred

## How to Contribute

The simplest approach:

1. **Fix it directly** — Submit a PR (preferred for internal repos)
2. **Not sure how?** — Open an issue to discuss first
3. **Questions?** — Ask in the agentic-coding Slack channel

## Contribution Guidelines

### Content Standards

- **Every recommendation must cite an authoritative source** (NIST publication, OMB memo, CISA guidance, or OWASP standard)
- **Keep content tool-agnostic** — never recommend a specific vendor or product
- **Use plain language** — the audience includes federal employees who may not be NIST specialists
- **Provide actionable examples** — show what to do, not just what the standard says
- **Include control mappings** — every section should reference applicable NIST 800-53 controls

### What We Need

- **Practitioner feedback** — Does this playbook work in your agency's environment?
- **Gap identification** — What security controls or scenarios are missing?
- **Plain language improvements** — Where is the playbook unclear or too technical?
- **Template refinements** — Are the templates practical for real ATO packages?
- **Framework updates** — Has a referenced NIST publication been updated?

### What We Don't Accept

- Vendor-specific recommendations or product placements
- Classified or CUI content
- Content that contradicts published NIST guidance without clear justification
- Speculative recommendations not grounded in authoritative sources

## How to Add a New Skill

1. Copy the template: `cp templates/SKILL.md.template skills/your-skill-name/SKILL.md`
1. Edit the frontmatter — fill in all required fields (`name` must match directory name)
1. Write the procedure sections (When to Use, Prerequisites, Procedure, Verification)
1. Add scripts if needed: `skills/your-skill-name/scripts/`
1. Validate: `make validate-skills`
1. Regenerate index: `make generate`
1. Submit a PR

### Skill Frontmatter Schema

All skills use this frontmatter (see `templates/SKILL.md.template`):

```yaml
---
name: your-skill-name              # Must match directory name
title: "Human-Readable Title"
description: "One-line description"
status: canonical                  # canonical | draft | deprecated
tier: 2
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["keyword1", "keyword2"]
dependencies: []
---
```

### Skill Requirements

1. **`name` must match the directory name** — lowercase, hyphens only, max 64 characters
1. **SKILL.md must be under 500 lines** — move reference material to `references/`
1. **No policy duplication** — reference docs by path (e.g., `docs/GETTING-STARTED.md Section 4`)
1. **Scripts must be read-only or generative** — never modify git state or install packages
1. **Scripts must output structured JSON** — `{"status": "...", "results": [...], "warnings": [...], "errors": [...]}`
1. **All Python scripts must pass ruff lint** — CI enforces this

## How to Add a Federal AI Guidance Entry

1. Copy the template: see `templates/landscape-entry.yaml.template` for the entry format with all allowed values
1. Add the entry to `data/federal-ai-landscape.yaml` under the appropriate section
1. Increment `total_entries` at the top of the YAML file
1. Add a corresponding section to `docs/FEDERAL-AI-LANDSCAPE.md`
1. Update the Status Summary table counts in the markdown
1. Validate: `make validate-landscape`
1. Submit a PR

**Allowed categories:** `executive_order`, `omb_memo`, `nist_standard`, `legislation`, `agency_strategy`, `industry_standard`, `white_house_plan`

**Allowed statuses:** `active`, `revoked`, `rescinded`, `draft`, `final`

## How to Add a New Document

1. Copy the template: `cp templates/doc.md.template docs/YOUR-DOC.md`
1. Fill in frontmatter (title, description, status, tier are required)
1. Write content with NIST control references where applicable
1. Validate: `make validate-docs`
1. Regenerate index: `make generate`
1. Submit a PR

## How to Update a NIST Control Mapping

NIST controls are referenced in three places:

1. **AGENTS.md** — frontmatter `nist_controls` array + inline `<!-- NIST: XX-N -->` comments
1. **docs/SECURITY-CONTROLS.md** — the master control overlay (36 controls mapped)
1. **docs/TRACEABILITY.md** — bidirectional control-to-document matrix

To update a mapping:

1. Update the control in `docs/SECURITY-CONTROLS.md` (add or modify the control section)
1. Update the traceability matrix in `docs/TRACEABILITY.md`
1. If the control applies to agent behavior, reference it in the relevant AGENTS.md section
1. Validate: `make validate-docs`
1. Submit a PR

## First-Time Setup

Run once after cloning the repo:

```bash
make setup      # Install dependencies + pre-commit hooks
```

## Before Every PR

**Two commands** handle everything — run these before pushing:

```bash
make generate   # Auto-updates: INDEX.yaml, skills tables, word counts, test/landscape counts
make ci         # Lint + test + validate + generate-check + SCA audit
```

`make generate` automatically keeps these in sync so you don't have to:
- Skills tables in README.md, AGENTS.md, AGENT-INSTRUCTIONS.md
- Word counts in CONTEXT-GUIDE.md
- Test count and landscape entry count across all docs

If `make ci` passes, your PR is ready.

## Individual Commands

```bash
make validate-docs       # Document frontmatter
make validate-skills     # Skill directories
make validate-landscape  # Federal AI landscape registry
make test                # Python test suite
make lint                # Ruff + markdownlint
make doctor              # Check environment readiness
make new-project DIR=x   # Bootstrap a new project
```

## Commit Messages

This project uses [conventional commits](https://www.conventionalcommits.org/) for automated changelog generation and semantic versioning.

**Format:** `type(scope): description`

| Type | When to Use |
|------|-------------|
| `feat` | New feature, skill, or document |
| `fix` | Bug fix, correction, broken reference |
| `docs` | Documentation-only changes |
| `chore` | Maintenance (deps, config, CI) |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

**Examples:**

```
feat: add PROJECT_PLAN.md validator with TDD tests
fix: update stale M-24-18 reference to M-25-22
docs: add cloud.gov sandbox 90-day wipe warning
chore(deps): update ruff 0.9.10 → 0.15.7
```

PR titles are validated by CI — PRs with non-conventional titles will not pass checks.

## Releases

Releases are fully automated. You never need to manually edit CHANGELOG.md, bump versions, or create tags.

### How it works

1. **Merge PRs** with conventional commit titles to `main`
2. **release-please** automatically opens a "Release PR" that:
   - Bumps the version in `pyproject.toml` and `.release-please-manifest.json`
   - Generates CHANGELOG.md entries from commit messages (grouped by type)
3. **When the Release PR is merged**, a git tag and GitHub Release are created automatically

### Version bump rules (semver)

| Commit Type | Version Bump | Example |
|-------------|-------------|---------|
| `feat:` | Minor | 0.4.0 → 0.5.0 |
| `fix:` | Patch | 0.4.0 → 0.4.1 |
| `feat!:` or `BREAKING CHANGE:` | Major | 0.4.0 → 1.0.0 |
| `docs:`, `chore:`, `refactor:`, `test:`, `ci:` | No bump | Included in next release's changelog |

### What to do (and not do)

- **Do** use conventional commit format for PR titles — CI enforces this
- **Do** merge the Release PR when you're ready to cut a release
- **Do not** manually edit CHANGELOG.md — release-please generates it
- **Do not** manually bump versions in pyproject.toml — release-please handles this
- **Do not** manually create git tags — release-please creates them on merge

### Keeping content accurate

After making changes, run `make generate` to auto-update:
- INDEX.yaml (document and skill metadata)
- Skills tables in README.md, AGENTS.md, docs/AGENT-INSTRUCTIONS.md
- Word counts in CONTEXT-GUIDE.md

Then run `make ci` to verify everything passes before pushing.

## Review Process

All pull requests require review. Changes to security standards require additional attention.

## Teams

- **[@GSA-TTS/agentic-coding-team](https://github.com/orgs/GSA-TTS/teams/agentic-coding-team):** Team members — review, contribute, provide feedback
- **[@GSA-TTS/agentic-coding-admins](https://github.com/orgs/GSA-TTS/teams/agentic-coding-admins):** Repository administrators — merge, release, maintain

## Code of Conduct

Be professional, constructive, and respectful. Quality and accuracy matter.

## Share What You Learn

Discovered a useful workflow or pattern while using this playbook? Consider sharing it in the [Patterns repo](https://github.com/GSA-TTS/agentic-coding-patterns) so others can benefit.
