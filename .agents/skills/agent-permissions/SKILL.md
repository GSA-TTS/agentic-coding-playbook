---
name: agent-permissions
title: "Agent Environment Doctor"
description: "Detect available credentials, diagnose gaps against PROJECT_PLAN.md, and guide setup for AI agents in any environment"
status: canonical
tier: 2
last_updated: "2026-06-17"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["permissions", "credentials", "secrets", "tokens", "API key", "access", "sandbox", "authentication", "doctor", "environment check"]
dependencies: ["project-bootstrap"]
---

# Skill: Agent Environment Doctor

Detect what credentials and tools an AI coding agent has access to, diagnose gaps against the project plan, and output actionable fix commands for each missing item.

## When to Use

- First thing after cloning a repo — before the agent tries to push, deploy, or call APIs
- Agent reports "permission denied" or "authentication failed"
- Onboarding a new developer or setting up a new environment
- Running the agent in a sandboxed environment (Codespace, container, CI runner)
- After rotating credentials to verify everything still works

## Core Principles

**Detect, don't create.** A sandboxed agent cannot create tokens or access browser UIs. This skill checks what's available and tells the human exactly what to fix.

**Never log secret values.** Check env var names and CLI auth status only. Never print, log, or transmit credential values.

**Least privilege.** Every credential gets the minimum scope needed for its job.

## Quick Start

```bash
# Run the environment doctor
make doctor

# Machine-readable JSON output
make doctor-json

# With custom project plan path
PYTHONPATH=scripts python3 -m playbook_validator doctor --plan path/to/PROJECT_PLAN.md
```

## How It Works

The doctor runs three phases:

### Phase 1: Detect

Scans the environment for available tools and credentials:

| Check | Method | What It Proves |
|---|---|---|
| Git | `command -v git` | Version control available |
| Git remote | `git remote get-url origin` | Platform identified (GitHub/GitLab) |
| GitHub CLI | `gh auth status` | Can create PRs, issues, manage repo |
| GITHUB_TOKEN | env var presence | API access for automation |
| cloud.gov CLI | `cf target` | Can deploy applications |
| GitLab token | GITLAB_TOKEN env var | Can push to GitLab instance |
| AI API keys | ANTHROPIC_API_KEY, OPENAI_API_KEY, etc. | Agent has LLM access |
| .gitignore | grep for `.env` pattern | Secrets won't be committed |

### Phase 2: Diagnose

Compares detected capabilities against PROJECT_PLAN.md requirements:

- Reads the **Agent Environment** section of PROJECT_PLAN.md
- Matches checked checkboxes (`- [x]`) to service checks
- Services not required by the plan are marked `[SKIP]`
- If no plan is found, checks all services

### Phase 3: Guide

For each `[FAIL]` item, prints one actionable fix command:

```
[FAIL] gh CLI authenticated
       Fix: Run: gh auth login
```

## Output Format

### Human-Readable (default)

```
═══ Agent Environment Doctor ═══

  Plan: PROJECT_PLAN.md

── Git & Platform ──
  [PASS] git — git version 2.43.0
  [PASS] git remote — GitHub — git@github.com:org/repo.git

── GitHub ──
  [PASS] gh CLI authenticated — user: octocat
  [PASS] GITHUB_TOKEN — set (value hidden)

── cloud.gov ──
  [PASS] cf CLI authenticated — org: sandbox-gsa, space: dev
  [SKIP] cloud.gov CI credentials — set CF_USERNAME + CF_PASSWORD for CI/CD

── GitLab ──
  [SKIP] GitLab — not required per PROJECT_PLAN.md

── Package Registries ──
  [SKIP] npm registry — not required per PROJECT_PLAN.md
  [SKIP] PyPI — not required per PROJECT_PLAN.md

── AI/LLM API Keys ──
  [PASS] ANTHROPIC_API_KEY — set (value hidden)

── Security ──
  [PASS] .gitignore — .env is protected
  [PASS] .env.example — template exists for team onboarding

── Summary ──

  Passed: 7  |  Failed: 0  |  Skipped: 4

  ✓ Environment is ready. All required services are configured.
```

### JSON (`--json` flag)

```json
{
  "status": "success",
  "checks_passed": 7,
  "checks_failed": 0,
  "skipped": 4,
  "results": [
    {"file": "env", "check": "git", "pass": true},
    {"file": "env", "check": "gh CLI authenticated", "pass": true}
  ],
  "warnings": [],
  "errors": []
}
```

Exit code 0 means all required checks pass. Exit code 1 means one or more required checks failed.

## Credential Reference

When the doctor reports a `[FAIL]`, use this reference to create the missing credential.

### GitHub — Fine-Grained Personal Access Token

1. Go to: **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
1. Click **Generate new token**
1. Set:
   - **Token name:** `ai-agent-<project-name>`
   - **Expiration:** 90 days (rotate regularly)
   - **Repository access:** Only select repositories → pick your project repo
   - **Permissions:**

| Permission | Level | Why |
|---|---|---|
| Contents | Read and write | Push code, create branches |
| Pull requests | Read and write | Create and manage PRs |
| Issues | Read and write | Create and manage issues |
| Actions | Read | View CI status |
| Metadata | Read | Required (always included) |

**Do NOT grant:** Admin, Secrets, Environments, Pages, Security alerts write

```bash
# Prompt for the token (no echo) so it never lands in shell history or the
# process list. Alternatively, pipe it from a CLI: `gh auth token | ...`.
read -rs GITHUB_TOKEN && export GITHUB_TOKEN
```

### cloud.gov — SSO Login (sandbox)

```bash
cf login -a api.fr.cloud.gov --sso
# Visit the URL shown, authenticate, paste the passcode
```

### cloud.gov — Service Account (CI/CD)

```bash
cf create-service cloud-gov-service-account space-deployer <project-name>-deployer
cf service-key <project-name>-deployer deployer-key
# Use the output username/password as CF_USERNAME and CF_PASSWORD
```

### GitLab (workshop.cloud.gov)

1. Login to your workshop.cloud.gov GitLab instance
1. Go to: **Settings → Access Tokens**
1. Create token with scopes: `read_repository`, `write_repository`, `read_api`

```bash
# Prompt for the token (no echo); keeps the literal out of shell history.
read -rs GITLAB_TOKEN && export GITLAB_TOKEN
export GITLAB_URL=https://<your-instance>.workshop.cloud.gov
```

## Environment Template

Create a `.env.example` file (committed to git) showing required variables.
Use empty values or obvious placeholders — never put real token literals (or
realistic-looking ones) in a committed file:

```bash
# .env.example — Required environment variables for AI agent
# Copy to .env and fill in values. NEVER commit .env to git.
# Set real values via a prompt (e.g. `read -rs GITHUB_TOKEN`) or a secrets
# manager — not by editing literals into your shell history.

# GitHub (required for code hosting)
GITHUB_TOKEN=

# cloud.gov (required for deployment)
# CF_USERNAME=
# CF_PASSWORD=
# CF_ORG=
# CF_SPACE=

# GitLab (if using workshop.cloud.gov)
# GITLAB_TOKEN=
# GITLAB_URL=https://your-instance.workshop.cloud.gov
```

Ensure `.gitignore` includes:

```
.env
.env.local
*.pem
*.key
```

## Token Rotation Schedule

| Token | Rotation | Reminder Method |
|---|---|---|
| GitHub PAT | Every 90 days | Set expiration date on token |
| cloud.gov service key | Every 90 days | Calendar reminder |
| GitLab token | Every 90 days | Set expiration date on token |
| npm/PyPI tokens | Every 180 days | Calendar reminder |

## Security Rules

1. **NEVER** commit credentials to git (use .env + .gitignore)
1. **NEVER** log token values (log "token present: yes/no" instead)
1. **ALWAYS** use fine-grained tokens with minimum scopes
1. **ALWAYS** set expiration dates on tokens
1. **ALWAYS** use GitHub Actions secrets for CI/CD credentials
1. **ROTATE** all tokens on the schedule above
1. **REVOKE** tokens immediately if compromised

## Verification

Run the doctor and confirm all required items pass:

```bash
make doctor
# Exit code 0 = ready
# Exit code 1 = items need attention
```
