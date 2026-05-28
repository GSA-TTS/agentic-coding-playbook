---
title: "Reusable Workflows Contract"
description: "API contract, versioning policy, and usage guide for GSA-TTS reusable GitHub Actions workflows"
status: canonical
tier: 2
last_updated: "2026-05-28"
audience: "developers"
keywords: ["reusable-workflows", "github-actions", "ci-cd", "versioning", "api-contract"]
related_files: [".github/workflows/reusable-pr-lint.yml", ".github/workflows/reusable-markdown-quality.yml", ".github/workflows/reusable-python-quality.yml", ".github/workflows/reusable-release-please.yml", ".github/workflows/reusable-semgrep.yml"]
load_priority: "on-demand"
review_cycle: "quarterly"
---

# Reusable Workflows Contract

This document defines the API contract, versioning policy, and usage guidelines for reusable GitHub Actions workflows in the GSA-TTS agentic ecosystem.

## Overview

The `agentic-coding-playbook` repository provides reusable workflows that downstream repositories (quickstart, patterns, and future projects) can consume for consistent CI/CD.

### Benefits

- **Consistency**: All repos use identical CI patterns
- **Maintainability**: Fix once, propagate everywhere
- **Security**: Centralized updates for action SHA pins
- **Compliance**: Standardized checks across the ecosystem

### Available Workflows

| Workflow | Purpose | Version |
|----------|---------|---------|
| `reusable-pr-lint.yml` | PR title validation (Conventional Commits) | v1 |
| `reusable-markdown-quality.yml` | Markdown linting and link checking | v1 |
| `reusable-python-quality.yml` | Python lint, test, pip-audit | v1 |
| `reusable-release-please.yml` | Automated releases via release-please | v1 |
| `reusable-semgrep.yml` | SAST scanning with Semgrep CE | v1 |

## Versioning Policy

### Version Tags

Workflows are versioned using Git tags in the format `workflows/vN`:

- `workflows/v1` - Current stable release
- `workflows/v2` - Next major version (breaking changes)
- `@main` - Latest development (not recommended for production)

### Semantic Versioning

We follow semantic versioning principles:

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking: input removed/renamed | Major (v1→v2) | Removing `validate-commits` input |
| Breaking: output schema changed | Major | Changing output names |
| Feature: new optional input | Minor (within major) | Adding new optional flag |
| Fix: bug fix | Patch (within major) | Fixing SHA typo |

### Breaking Change Policy

1. **Announcement**: Breaking changes are announced 2 weeks before tagging a new major version
2. **Deprecation**: Old versions remain available but unsupported for 6 months
3. **Migration Guide**: Each major version includes migration instructions

## Usage

### Pinning to Stable Version (Recommended)

```yaml
jobs:
  lint:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-pr-lint.yml@workflows/v1
```

### Pinning to Main (Development Only)

```yaml
jobs:
  lint:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-pr-lint.yml@main
```

## Workflow API Reference

### reusable-pr-lint.yml

Validates PR titles and optionally all commits follow Conventional Commits.

**Inputs:**

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `validate-commits` | boolean | No | `false` | Validate all commits in addition to PR title |
| `allowed-types` | string | No | See below | Comma-separated list of allowed commit types |
| `node-version` | string | No | `'22'` | Node.js version for commitlint |

Default `allowed-types`: `feat,fix,docs,chore,refactor,test,perf,ci,style,build,revert,security`

**Permissions Required:**

```yaml
permissions:
  contents: read
  pull-requests: read
```

**Example:**

```yaml
name: PR Lint

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

jobs:
  lint:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-pr-lint.yml@workflows/v1
    with:
      validate-commits: true
```

### reusable-markdown-quality.yml

Markdown linting and optional link checking.

**Inputs:**

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `node-version` | string | No | `'22'` | Node.js version |
| `markdownlint-globs` | string | No | `''` | Glob patterns (uses config file if empty) |
| `run-link-check` | boolean | No | `false` | Run markdown link checker |
| `link-check-config` | string | No | `.markdown-link-check.json` | Link checker config path |
| `link-check-path` | string | No | `.` | Directory to check |
| `continue-on-link-error` | boolean | No | `true` | Continue on flaky external URLs |

**Permissions Required:**

```yaml
permissions:
  contents: read
```

**Example:**

```yaml
name: Markdown Quality

on:
  pull_request:
  push:
    branches: [main]

jobs:
  markdown:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-markdown-quality.yml@workflows/v1
    with:
      run-link-check: true
      continue-on-link-error: false
```

### reusable-python-quality.yml

Python linting (ruff), testing (pytest), and security scanning (pip-audit).

**Inputs:**

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `python-version` | string | No | `'3.13'` | Python version |
| `scripts-path` | string | No | `'scripts/'` | Path for linting |
| `run-tests` | boolean | No | `true` | Run pytest |
| `test-path` | string | No | `'scripts/tests/'` | Test directory |
| `run-pip-audit` | boolean | No | `true` | Run pip-audit |
| `pip-audit-flags` | string | No | `'--skip-editable'` | pip-audit flags |
| `install-command` | string | No | `'pip install -e ".[dev]"'` | Dependency install |
| `pythonpath` | string | No | `'scripts'` | PYTHONPATH |

**Permissions Required:**

```yaml
permissions:
  contents: read
```

**Example:**

```yaml
name: Python CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  python:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-python-quality.yml@workflows/v1
    with:
      python-version: '3.12'
      scripts-path: 'src/'
      test-path: 'tests/'
```

### reusable-release-please.yml

Automated release management via Google's release-please.

**Inputs:**

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `config-file` | string | No | `''` | Path to release-please-config.json |
| `manifest-file` | string | No | `''` | Path to .release-please-manifest.json |
| `release-type` | string | No | `'simple'` | Release type when not using config |

**Outputs:**

| Output | Description |
|--------|-------------|
| `release_created` | Whether a release was created |
| `tag_name` | The release tag name |
| `version` | The release version |

**Permissions Required:**

```yaml
permissions:
  contents: write
  pull-requests: write
```

**Example (Simple):**

```yaml
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  release:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-release-please.yml@workflows/v1
    with:
      release-type: simple
```

**Example (With Config):**

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-release-please.yml@workflows/v1
    with:
      config-file: 'release-please-config.json'
      manifest-file: '.release-please-manifest.json'
```

### reusable-semgrep.yml

Static Application Security Testing using Semgrep Community Edition.

**Inputs:**

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `scan-path` | string | No | `'.'` | Path to scan |
| `rulesets` | string | No | `'p/python p/security-audit'` | Space-separated rulesets |

**Permissions Required:**

```yaml
permissions:
  contents: read
```

**Example:**

```yaml
name: Security

on:
  pull_request:
  push:
    branches: [main]

jobs:
  sast:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-semgrep.yml@workflows/v1
    with:
      scan-path: 'src/'
      rulesets: 'p/python p/security-audit p/owasp-top-ten'
```

## Token Handling

### GITHUB_TOKEN Inheritance

Reusable workflows automatically inherit `GITHUB_TOKEN` from the calling workflow via the `permissions` block. **Do not pass `GITHUB_TOKEN` as a secret** — this causes a "reserved name collision" error.

**Correct:**

```yaml
jobs:
  release:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-release-please.yml@workflows/v1
    with:
      release-type: simple
    # No secrets block needed
```

**Incorrect:**

```yaml
jobs:
  release:
    uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-release-please.yml@workflows/v1
    with:
      release-type: simple
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # ERROR: reserved name
```

### Required Permissions

Calling workflows must have sufficient permissions for the reusable workflow to function:

| Workflow | Required Permissions |
|----------|---------------------|
| pr-lint | `contents: read`, `pull-requests: read` |
| markdown-quality | `contents: read` |
| python-quality | `contents: read` |
| release-please | `contents: write`, `pull-requests: write` |
| semgrep | `contents: read` |

## Troubleshooting

### Common Errors

**"Unable to resolve action ... unable to find version"**

The action SHA is incorrect. This is fixed in the reusable workflow — ensure you're using the latest `workflows/v1` tag or `@main`.

**"secret name GITHUB_TOKEN within workflow_call can not be used"**

Remove the `secrets: GITHUB_TOKEN` line from your calling workflow. The token is automatically inherited.

**"Resource not accessible by integration"**

The calling repository needs to grant Actions write permissions:
1. Go to repo Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"

### Getting Help

1. Check this document's troubleshooting section
2. Search existing issues in `agentic-coding-playbook`
3. Open a new issue with the workflow run URL

## Changelog

### workflows/v1 (2026-05-28)

Initial stable release after CI stabilization:

- Fixed `GITHUB_TOKEN` reserved name collision in pr-lint and release-please
- Corrected action SHA for `amannn/action-semantic-pull-request` (v5.5.3)
- Corrected action SHA for `googleapis/release-please-action` (v4.4.1)
- All workflows tested and verified working

## Migration Guide

### Migrating from @main to @workflows/v1

Update your workflow references:

```diff
- uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-pr-lint.yml@main
+ uses: GSA-TTS/agentic-coding-playbook/.github/workflows/reusable-pr-lint.yml@workflows/v1
```

No input changes required — v1 is API-compatible with the stabilized @main.
