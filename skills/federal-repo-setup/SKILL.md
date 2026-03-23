---
name: federal-repo-setup
description: >
  Initialize a code repository with federal security compliance defaults including
  .gitignore with secrets exclusions, pre-commit hooks for secrets scanning and
  linting, .editorconfig, and CI/CD security baseline. Use when setting up a new
  project or hardening an existing repo for federal AI development.
compatibility: Requires git, a supported language runtime, and shell access.
metadata:
  author: wz-gsa
  version: "0.2.0"
  frameworks: "NIST SP 800-53 Rev 5.2 (CM-2, CM-6, SA-10)"
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
    rev: v8.21.2 # Pin to latest stable
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
        args: ["--baseline", ".secrets.baseline"]
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

If the project uses environment variables, create `.env.example` with placeholder values:

```bash
# Database connection (use secrets manager in production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API keys (NEVER commit actual values)
API_KEY=your-api-key-here

# Application settings
LOG_LEVEL=info
DEBUG=false
```

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
      - uses: actions/checkout@v4
      # Add language-specific linter step

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Add language-specific test step

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Add SAST scanner (see TOOL_MATRIX.md)

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Add dependency vulnerability scanner

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2
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

### Step 8: Run Audit Script

Run the audit script to verify the setup is complete:

```bash
bash skills/federal-repo-setup/scripts/audit-repo-setup.sh
```

The script outputs structured JSON. Review any failures and address them.

### Step 9: Next Steps

After completing repo setup, recommend:

1. **Configure AGENTS.md** — Use the `federal-agents-config` skill to generate a project-specific AGENTS.md
2. **Review branch protection** — Set up required reviews, status checks, force-push restrictions per `docs/GETTING-STARTED.md` Section 5
3. **Complete pre-deployment checklist** — Use the `federal-pre-deployment-check` skill before any deployment

## Important Notes

- This skill generates new files. It does NOT install packages, make network calls, or modify git history.
- Generated CI pipelines use `permissions: contents: read` (least privilege).
- All tool version pins should be verified against current stable releases.
- Pre-commit hook configuration is a starting point — agencies may require additional hooks.
- **Policy reference:** All steps trace back to `docs/GETTING-STARTED.md`. Read that document for the "why" behind each requirement.
