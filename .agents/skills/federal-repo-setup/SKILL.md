---
name: federal-repo-setup
title: "Federal Repository Setup"
description: "Initialize a code repository with federal security compliance defaults including .gitignore, pre-commit hooks, .editorconfig, and CI/CD security baseline."
status: canonical
tier: 2
last_updated: "2026-06-17"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["repo setup", "repository", "federal compliance", "pre-commit", "security baseline", "hardening"]
dependencies: []
---

# Federal Repository Setup

This skill converts the playbook in `docs/GETTING-STARTED.md` into an executable
workflow for initializing a repository with federal security compliance defaults.

## When to Use

- Setting up a new code repository for federal AI development
- Hardening an existing repo to meet FIPS Moderate compliance baseline
- Adding missing security tooling (secrets scanning, SAST, dependency audit)
- Preparing a project for ATO review

## Prerequisites

Before starting, confirm the user has:
- Git 2.39+ installed
- A supported language runtime (Python 3.10+, Node.js 18+, Go 1.21+, Java 17+, or .NET 8+)
- An approved AI coding agent (per agency policy)
- Access to pre-commit framework (`pip install pre-commit` or equivalent)

## Setup Procedure

### Step 1: Detect Language and Framework

Examine the repository to determine the primary language and framework:

1. Check for language indicators:
   - `requirements.txt`, `pyproject.toml`, `setup.py` -> Python
   - `package.json` -> JavaScript/TypeScript
   - `go.mod` -> Go
   - `pom.xml`, `build.gradle` -> Java
   - `*.csproj`, `*.sln` -> .NET
   - `Cargo.toml` -> Rust
2. Check for framework indicators (package manifests, config files)
3. If multiple languages, ask which is primary

Record the detected language — it determines which tools to recommend in later steps.
See [references/TOOL_MATRIX.md](references/TOOL_MATRIX.md) for the full language-to-tool mapping.

### Step 2: Generate .gitignore

Create or update `.gitignore` with federal-required exclusion patterns.

**Required patterns (all languages):**

```gitignore
# === Federal Security: Secrets and Credentials ===
.env
.env.*
!.env.example
*.key
*.pem
*.p12
*.pfx
*.jks
credentials.*
**/secrets/
*.secret

# === Federal Security: IDE and Editor ===
.idea/
.vscode/settings.json
*.swp
*.swo
*~

# === Federal Security: OS Artifacts ===
.DS_Store
Thumbs.db
desktop.ini
```

**Add language-specific patterns** from https://github.com/github/gitignore for the detected language.

**Policy reference:** `docs/GETTING-STARTED.md` Section 2 — Repository Initialization.

### Step 3: Generate .editorconfig

Create `.editorconfig` for consistent formatting:

```ini
root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8

[*.{py,js,ts,go,java,cs,rs}]
indent_style = space
indent_size = 4

[*.{yml,yaml,json}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
```

Adjust `indent_size` if the project already has an established convention.

### Step 4: Set Up Secrets Scanning (Pre-commit Hook)

Install a pre-commit secrets scanner. This is the **highest priority** security control.

**Option A — gitleaks (recommended):**

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2  # Pin to latest stable
    hooks:
      - id: gitleaks
```

**Option B — detect-secrets:**

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Then run:
```bash
pre-commit install
```

**Policy reference:** `docs/GETTING-STARTED.md` Section 4 — Secrets Scanning.
**Control:** IA-5 (Authenticator Management).

### Step 5: Set Up Linting Pre-commit Hook

Add a language-appropriate linter to `.pre-commit-config.yaml`.
See [references/TOOL_MATRIX.md](references/TOOL_MATRIX.md) for the recommended linter per language.

**Example for Python:**
```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Example for JavaScript/TypeScript:**
```yaml
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.17.0
    hooks:
      - id: eslint
        additional_dependencies:
          - eslint-plugin-security
```

### Step 6: Create .env.example

If the project uses environment variables, create `.env.example` with empty or
clearly-fake placeholder values — never a real (or realistic-looking) secret,
since this file is committed to git:

```bash
# Database connection (use secrets manager in production; leave blank here)
#   Secrets manager format will be: postgresql://user:password@localhost:5432/dbname
DATABASE_URL=

# API keys (NEVER commit actual values; populate via prompt or secrets manager)
API_KEY=

# Application settings
LOG_LEVEL=info
DEBUG=false
```

> Set real values at runtime without exposing them in shell history — e.g.
> `read -rs API_KEY && export API_KEY`, or inject from your secrets manager.

**Rule:** `.env.example` MUST be committed. `.env` MUST NOT be committed.
**Policy reference:** `docs/GETTING-STARTED.md` Section 6 — Environment Variables.

### Step 7: Generate CI/CD Security Baseline

Create a CI pipeline with the 5 required security stages.

**For GitHub Actions** (`.github/workflows/security.yml`):

```yaml
name: Security Baseline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      # Add language-specific linter step

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      # Add language-specific test step

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      # Add SAST scanner (see TOOL_MATRIX.md)

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      # Add dependency vulnerability scanner

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      - uses: gitleaks/gitleaks-action@ff98106e4c7b2bc287b24eaf42907196329070c7 # v2.3.9
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**For GitLab CI** (`.gitlab-ci.yml`):

```yaml
stages:
  - lint
  - test
  - sast
  - dependency-scan
  - secrets-scan

# Add language-specific jobs for each stage
```

**Policy reference:** `docs/GETTING-STARTED.md` Section 7 — CI/CD Security Baseline.
**Controls:** SA-11, RA-5, SA-12.

### Step 8: Generate SECURITY.md

If `SECURITY.md` does not already exist in the repository root, create it:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

<!-- Update this table to reflect your project's actual version support policy. -->

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability, please email **[AGENCY_SECURITY_CONTACT]** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Affected version(s)
4. Any potential impact assessment

We will acknowledge receipt within **2 business days** and provide an initial
assessment within **5 business days**.

## Responsible Disclosure

We follow coordinated vulnerability disclosure. We ask that you:

- Allow us reasonable time to investigate and address the issue before public disclosure
- Make a good-faith effort to avoid privacy violations, data destruction, or service disruption
- Do not exploit the vulnerability beyond what is necessary to demonstrate it

## Agency-Specific Policy

<!-- Replace this section with your agency's vulnerability handling policy,
     including references to any applicable NIST SP 800-53 controls (IR-6, SI-5)
     and your agency's incident response plan. -->

This project follows [NIST SP 800-53 IR-6](https://csf.tools/reference/nist-sp-800-53/r5/ir/ir-6/)
(Incident Reporting) and [SI-5](https://csf.tools/reference/nist-sp-800-53/r5/si/si-5/)
(Security Alerts, Advisories, and Directives).
```

Replace `[AGENCY_SECURITY_CONTACT]` with the actual security contact if known, or leave it as a placeholder for the team to fill in.

### Step 9: Generate CONTRIBUTING.md

If `CONTRIBUTING.md` does not already exist in the repository root, create it:

```markdown
# Contributing

Thank you for your interest in contributing to this project.

## How to Contribute

1. **Check existing issues** — look for open issues or create a new one describing the change
2. **Fork the repository** and create a feature branch from `main`
3. **Make your changes** — follow the coding standards below
4. **Write or update tests** to cover your changes
5. **Submit a pull request** against `main` with a clear description

## Code Standards

This project follows the coding practices documented in
[CODING_PRACTICES.md](../../docs/CODING_PRACTICES.md) (if present) or the
language-specific conventions established in the codebase.

Key expectations:
- All code must pass linting and static analysis before merge
- Security scanning (secrets, SAST, dependency audit) must pass in CI
- New features require tests; bug fixes require a regression test

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Optional longer description.
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `ci`

Examples:
- `feat(auth): add PIV card authentication flow`
- `fix(api): handle null response from upstream service`
- `docs: update deployment runbook for FedRAMP boundary`

## Review Process

All pull requests require:
1. At least one approving review from a maintainer
2. All CI checks passing (lint, test, SAST, secrets scan, dependency audit)
3. No unresolved review comments

Reviewers will evaluate contributions for correctness, security impact,
test coverage, and adherence to project coding standards.

## Questions?

Open an issue with the `question` label or contact the project maintainers.
```

### Step 10: Generate LICENSE

If `LICENSE` does not already exist in the repository root, create it with the
CC0 1.0 Universal public domain dedication (standard for U.S. federal government work).

Use the full legal text from the canonical source:
https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt

The file should begin with:

```
CC0 1.0 Universal

Statement of Purpose

The laws of most jurisdictions throughout the world automatically confer
exclusive Copyright and Related Rights (defined below) upon the creator and
subsequent owner(s) (each and all, an "owner") of an original work of
authorship and/or a database (each, a "Work").
...
```

Copy the complete CC0 1.0 legal text (Sections 1-4 plus Statement of Purpose) into the
`LICENSE` file. Do not abbreviate or summarize the legal text.

**Note:** CC0 is the standard license for U.S. federal government works (17 U.S.C. 105).
If the project includes contributions from non-federal employees or uses a different
license policy, ask the team before generating this file.

### Step 11: Run Audit Script

Run the audit script to verify the setup is complete:

```bash
make validate
```

The script outputs structured JSON. Review any failures and address them.

### Step 12: Next Steps

After completing repo setup, recommend:

1. **Configure AGENTS.md** — Use the `federal-agents-config` skill to generate a project-specific AGENTS.md
2. **Review branch protection** — Set up required reviews, status checks, force-push restrictions per `docs/GETTING-STARTED.md` Section 5
3. **Complete pre-deployment checklist** — Use the `federal-pre-deployment-check` skill before any deployment

## Verification Checklist

Before marking setup complete, confirm all required files exist:

- [ ] `.gitignore` — includes federal security exclusion patterns
- [ ] `.editorconfig` — consistent formatting rules
- [ ] `.pre-commit-config.yaml` — secrets scanning + linting hooks
- [ ] `.env.example` — placeholder environment variables (if applicable)
- [ ] `.github/workflows/security.yml` or `.gitlab-ci.yml` — CI/CD security baseline
- [ ] `SECURITY.md` — vulnerability disclosure process
- [ ] `CONTRIBUTING.md` — contribution standards and review process
- [ ] `LICENSE` — CC0 1.0 Universal (or agency-approved alternative)

## Important Notes

- This skill generates new files. It does NOT install packages, make network calls, or modify git history.
- Steps 8-10 check for existing files before creating — safe to re-run on established repos.
- Generated CI pipelines use `permissions: contents: read` (least privilege).
- All tool version pins should be verified against current stable releases.
- Pre-commit hook configuration is a starting point — agencies may require additional hooks.
- **Policy reference:** All steps trace back to `docs/GETTING-STARTED.md`. Read that document for the "why" behind each requirement.
