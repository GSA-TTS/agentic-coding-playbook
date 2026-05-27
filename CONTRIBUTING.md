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
make setup      # Install dependencies only
```

### Pre-commit Hooks (Optional)

Pre-commit hooks are **optional** for this repository. They are designed for **contributors** who are actively developing this project.

**If you cloned this repo for guidance only** (to reference standards for your own projects), **you do not need to install the hooks**.

**If you are contributing to this repo**, you can opt-in to pre-commit hooks:

```bash
make install-hooks    # [OPTIONAL] Install pre-commit hooks
```

These hooks run automatically on `git commit` and check for:
- YAML/JSON syntax errors
- Trailing whitespace and end-of-file fixes
- Secrets detection (gitleaks)
- Python linting and formatting (ruff)

**CI enforces the same checks** via `make ci`, so hooks are not required — they just provide faster feedback during local development.

#### Working in SBX Containers

Most users will be working **inside Docker SBX containers** per the [Quickstart guidance](https://github.com/GSA-TTS/agentic-coding-quickstart). This creates additional considerations for pre-commit hooks.

**Installing the pre-commit tools in a container:**

When you run `make setup` or `make install-hooks` inside an SBX container, the pre-commit tools are installed in that container's environment:

```bash
sbx exec <sandbox-name> make install-hooks
```

**Two workflows for committing changes:**

**Workflow A: Edit in container, verify in container, commit on host**
1. Edit files inside the SBX container
2. Run `make ci` inside the container to verify all checks pass
3. Exit the container and commit from your host machine
4. Pre-commit hooks (if installed on host) will run again on commit

This workflow is recommended because:
- Keeps git history on the host (persistent across container restarts)
- Verifies changes in the same environment where they'll run in CI
- No risk of losing commits when containers are destroyed

**Workflow B: Edit in container, install hooks in container, commit in container**
1. Edit files inside the SBX container
2. Install pre-commit hooks inside the container: `make install-hooks`
3. Commit changes inside the container

**Important:** SBX containers are ephemeral. If the container is destroyed or recreated, any hooks installed inside it will be lost. You'll need to re-run `make install-hooks` in the new container.

**Recommended practice:**

Before committing on your host machine, verify changes in the container first:

```bash
sbx exec <sandbox-name> make ci
```

This ensures all checks pass in the standardized SBX environment before you commit. CI will run the same checks, so catching issues early saves time.

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

## Commit Message Format

We follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) to maintain a clean, parseable git history and enable automated changelog generation. This standard is enforced by CI — PRs with non-conventional titles will not pass checks.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types for Playbook Repository

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New skill, doc, or feature | `feat(skills): add federal-decision-records skill` |
| `fix` | Bug fix in skill or script | `fix(validator): correct frontmatter schema check` |
| `docs` | Documentation only | `docs: update SECURITY-CONTROLS.md` |
| `test` | Add or fix tests | `test(validator): add edge case coverage` |
| `chore` | Maintenance (deps, CI) | `chore(deps): update feedparser to 6.0.11` |
| `refactor` | Code restructuring (no behavior change) | `refactor(validator): simplify frontmatter parsing` |
| `perf` | Performance improvement | `perf(validator): cache INDEX.yaml reads` |
| `ci` | CI/CD pipeline changes | `ci: add commitlint enforcement` |

### Common Scopes

- `skills` — Skill implementations
- `validator` — Validation scripts in `scripts/`
- `landscape` — Federal AI landscape registry
- `docs` — Documentation files
- `ci` — CI/CD workflows
- `deps` — Dependencies

### Examples

✅ **Good:**
```
feat(landscape): add Phase 1 foundation for automated monitoring

Implement RSS monitoring and version comparison scripts for
federal AI guidance. Enables automated detection of new EOs,
OMB memos, and NIST standards.

Related to #46
```

```
fix(validator): handle skills with no scripts directory

Previously crashed with FileNotFoundError when validating
skills without a scripts/ directory.

Closes #48
```

```
docs: add cloud.gov sandbox 90-day wipe warning

Warn contributors about ephemeral SBX environments to prevent
data loss.
```

❌ **Bad:**
```
update landscape
```
```
fixed bug
```
```
WIP: testing stuff
```

### Line Length

- **First line (subject):** ≤72 characters (recommended), ≤100 characters (enforced by commitlint)
- **Body lines:** ≤100 characters for readability

### AI Agent Attribution

**When AI agents contribute to a commit**, include a `Co-authored-by:` trailer per [AGENTS.md section 2.1](AGENTS.md#21-agent-identification):

```
feat(skills): add new pattern

Implementation details...

Co-authored-by: OpenCode Agent <user@gsa.gov>
```

**Format Requirements:**
- Trailer appears after a blank line following the commit body
- Uses the format: `Co-authored-by: Agent Name <email@gsa.gov>`
- Email MUST use `@gsa.gov` domain for federal compliance
- Multiple co-authors each get their own line

**Why we require this:**
- Maintains transparent audit trail per AU-2 (Audit Events)
- Enables attribution in GitHub UI and contribution graphs
- Distinguishes human-written from AI-assisted code
- Supports future AI risk management analysis

See [AGENTS.md](AGENTS.md#21-agent-identification) for full AI attribution requirements.

### Validation

Check your commit message locally before pushing:

```bash
# Option 1: Use commitlint (if installed via pre-commit hooks)
npx commitlint --from=HEAD~1

# Option 2: Run the full CI suite (includes commitlint)
make ci
```

### Pre-commit Hook (Optional)

Automate validation with our pre-commit config:

```bash
# Install pre-commit hooks
make install-hooks

# Your commits will now be validated automatically
```

The commitlint hook is already configured in `.pre-commit-config.yaml`.

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
