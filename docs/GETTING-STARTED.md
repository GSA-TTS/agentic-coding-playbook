---
title: "Getting Started: Repository Setup and Environment Hardening"
description: "Step-by-step guide for setting up a development repository with security controls for AI coding agents"
status: canonical
tier: 2
last_updated: "2026-02-25"
nist_controls: ["CM-2", "CM-6", "SA-10", "PO.1"]
frameworks: ["NIST SP 800-53 Rev 5.2", "NIST SP 800-218"]
audience: "developers"
keywords:
  [
    "setup",
    "repository",
    "pre-commit",
    "secrets-scanning",
    "branch-protection",
    "CI-CD",
  ]
related_files:
  ["AGENTS.md", "CODING_PRACTICES.md", "templates/AGENTS.md.template"]
load_priority: "on-demand"
review_cycle: "semi-annually"
---

<!-- LOAD: on-demand — Load when setting up a new repository, configuring CI/CD, or hardening development environment. -->

# Getting Started: Repository Setup and Environment Hardening

> **Version:** 0.1.0 | **Impact Level:** FIPS Moderate | **Scope:** Single-agent, internal enterprise

## Quick Reference

Setup steps in order (each maps to an 800-53 control family):

1. **Repository init** — `.gitignore` with secrets exclusions, `.editorconfig`, branch protection (CM-2)
2. **AGENTS.md** — Copy template, customize for your project (PL-4)
3. **Pre-commit hooks** — Secrets scanner (gitleaks/detect-secrets), linter, formatter (IA-5, SA-11)
4. **CI/CD pipeline** — SAST, SCA, secrets scan, test suite, human approval gate (SA-11, CM-5)
5. **Environment hardening** — Least-privilege agent credentials, network allowlist, TLS enforcement (AC-6, SC-8)

> **Full step-by-step guide with tool recommendations in sections below.**
> **Automated setup: Use the `federal-repo-setup` skill.**

---

> **Disclaimer:** This playbook is informational only and is not authoritative federal policy. Each agency must tailor these steps to their specific ATO requirements, organizational policies, and risk tolerance.

This document walks through setting up a development repository with security controls appropriate for AI-assisted federal software development. Every step maps to a NIST SP 800-53 control family so your work is traceable to your System Security Plan (SSP).

**Key words:** "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" are used per [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

**Audience:** Federal employees (GS-12 to GS-15) who can write code but may not be deeply familiar with NIST frameworks. If you know how to `git commit`, you have enough background to follow this guide.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Repository Initialization](#2-repository-initialization)
3. [Agent Configuration](#3-agent-configuration)
4. [Secrets Scanning Setup](#4-secrets-scanning-setup)
5. [Branch Protection](#5-branch-protection)
6. [Environment Variables](#6-environment-variables)
7. [CI/CD Security Baseline](#7-cicd-security-baseline)
8. [IDE/Editor Hardening](#8-ideeditor-hardening)
9. [Tooling Selection Criteria](#9-tooling-selection-criteria)
10. [Next Steps](#10-next-steps)

---

## 1. Prerequisites

<!-- NIST SP 800-53: SA-22 (Unsupported System Components), CM-11 (User-Installed Software) -->

Before beginning, confirm you have the following installed and configured on your workstation.

### 1.1 Required Software

| Tool                        | Purpose                                                               | How to Verify                                |
| --------------------------- | --------------------------------------------------------------------- | -------------------------------------------- |
| Git 2.39+                   | Version control                                                       | `git --version`                              |
| An approved AI coding agent | AI-assisted development (see Section 9 for selection criteria)        | Agent-specific — check vendor docs           |
| A language runtime          | Your project's language (Python, Node.js, Go, Java, .NET, Rust, etc.) | Language-specific (e.g., `python --version`) |
| A pre-commit framework      | Automated checks before each commit                                   | `pre-commit --version` or equivalent         |

### 1.2 Required Access

- Write access to your organization's source control platform (GitHub, GitLab, Bitbucket, or agency equivalent)
- Access to your organization's approved package registries
- Access to your organization's secrets management system (if applicable)

### 1.3 Required Knowledge

You SHOULD be familiar with:

- Basic git operations (clone, branch, commit, push, pull request)
- Your project's programming language and package manager
- Your agency's ATO (Authority to Operate) requirements at a high level

You do not need to have memorized NIST publications. This guide cites the specific controls at each step so you can look them up if your SSP requires detailed justification.

> **Control Mapping:** SA-22 (Unsupported System Components), CM-11 (User-Installed Software), SA-4 (Acquisition Process)

---

## 2. Repository Initialization

<!-- NIST SP 800-53: CM-2 (Baseline Configuration), CM-3 (Configuration Change Control) -->
<!-- NIST SP 800-218A: PW.6 (Configure the Build Process) -->

### 2.1 Create the Repository

Create a new repository on your organization's source control platform. Use your agency's standard process — most agencies have a self-service portal or a request form.

**Repository settings you MUST configure at creation:**

- **Visibility:** Internal or private (never public for FIPS Moderate systems without explicit authorization)
- **Default branch:** `main`
- **Initialize with:** A README and a LICENSE file appropriate for your agency

### 2.2 Set Up .gitignore

The `.gitignore` file prevents sensitive files from being committed to version control. You MUST include patterns that block secrets, credentials, and environment-specific files.

Start with a `.gitignore` for your language (templates are widely available for every major language), then add these entries:

```gitignore
# Secrets and credentials — MUST be present
.env
.env.*
*.key
*.pem
*.p12
*.pfx
credentials.*
*secret*
*.keystore

# IDE and editor files
.vscode/settings.json
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
node_modules/
__pycache__/
*.pyc
target/
bin/
obj/

# Agent-specific working files (if your agent creates temp files)
.agent-temp/
```

### 2.3 Set Up .editorconfig

An `.editorconfig` file ensures consistent formatting across all editors and contributors — human and AI alike. This reduces merge conflicts and keeps style consistent regardless of which tool generates the code.

```ini
# .editorconfig
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false

[*.{yml,yaml}]
indent_size = 2

[Makefile]
indent_style = tab
```

Adjust `indent_size` and other values to match your team's coding standards. The important thing is that the file exists and is committed — it gives both human developers and AI agents a shared formatting baseline.

### 2.4 Initial Directory Structure

You SHOULD establish a standard directory layout early. The exact structure depends on your language and framework, but the following skeleton is common across most projects:

```
your-project/
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml      # See Section 4
├── AGENTS.md                    # See Section 3
├── README.md
├── LICENSE
├── src/                         # Application source code
├── tests/                       # Test suite
├── docs/                        # Documentation
└── .github/                     # CI/CD workflows (if using GitHub)
    └── workflows/
```

> **Control Mapping:** CM-2 (Baseline Configuration), CM-3 (Configuration Change Control), SA-10 (Developer Configuration Management)

---

## 3. Agent Configuration

<!-- NIST SP 800-53: PL-4 (Rules of Behavior), CM-6 (Configuration Settings) -->
<!-- NIST AI RMF: GOVERN 1 (Policies), GOVERN 6 (Accountability) -->
<!-- NCCOE Agent Identity: Identification -->

### 3.1 What Is AGENTS.md?

`AGENTS.md` is a file placed in the root of your repository that tells AI coding agents what rules to follow. Most AI coding agents automatically detect and read files like `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, or similar configuration files in your repository. The filename and format vary by tool — `AGENTS.md` is used here as a tool-agnostic convention.

The file defines:

- What the agent is allowed and prohibited from doing
- Security controls the agent must follow
- Data handling requirements
- Testing and review expectations
- Incident escalation procedures

### 3.2 Setting Up AGENTS.md

1. Copy the template from this repository into your project root:

   ```bash
   # From the agentic-ai-playbook repository
   cp templates/AGENTS.md.template /path/to/your-project/AGENTS.md
   ```

   See [templates/AGENTS.md.template](../templates/AGENTS.md.template) for the full template.

2. Customize the template for your project:
   - Replace placeholder values (agency name, system name, impact level) with your specifics
   - Review each section and remove anything not applicable to your project
   - Add project-specific rules (e.g., required frameworks, coding conventions, approved libraries)

3. Commit the file to your repository:

   ```bash
   git add AGENTS.md
   git commit -m "Add agent behavior rules"
   ```

### 3.3 How Agents Read the File

AI coding agents typically read configuration files at session start — when you open a project or begin a conversation. The agent treats the rules in AGENTS.md as behavioral constraints for the session. Key behaviors to understand:

- **Scope:** The rules apply to the repository where the file is located
- **Priority:** Agent rules files are additive — the agent follows its built-in safety rules plus your custom rules
- **Limitations:** An AGENTS.md file is a behavioral guide, not a technical enforcement mechanism. It relies on the agent's compliance. Enforcement comes from the other controls in this guide (branch protection, CI checks, pre-commit hooks)
- **Updates:** When you change the file, agents pick up the changes on the next session or when the file is re-read

### 3.4 Verifying Agent Compliance

You SHOULD verify that your agent is following the rules by:

- Reviewing agent-generated commits for co-authorship attribution
- Checking that agent-generated code passes your CI security scans
- Periodically asking the agent to summarize the rules it is following
- Monitoring audit logs for unexpected actions

> **Control Mapping:** PL-4 (Rules of Behavior), CM-6 (Configuration Settings), AU-6 (Audit Review)

---

## 4. Secrets Scanning Setup

<!-- NIST SP 800-53: IA-5 (Authenticator Management), SC-28 (Protection of Information at Rest) -->
<!-- NIST SP 800-218A: PS.1 (Protect All Forms of Code from Unauthorized Access) -->

Secrets scanning prevents credentials, API keys, tokens, and private keys from being committed to version control. This is one of the most important controls for AI-assisted development — AI agents can inadvertently generate code containing placeholder secrets or copy patterns that include real credentials.

### 4.1 Pre-Commit Hook Installation

A pre-commit hook runs automatically before every `git commit`. If the hook detects a secret, the commit is blocked. This is your primary defense against accidental secret exposure.

**Common tools for secrets scanning** (choose one or more based on your agency's approved tool list):

| Tool           | Detection Approach                        | Configuration File  |
| -------------- | ----------------------------------------- | ------------------- |
| gitleaks       | Regex pattern matching + entropy analysis | `.gitleaks.toml`    |
| detect-secrets | Entropy analysis + heuristic plugins      | `.secrets.baseline` |
| trufflehog     | Regex + entropy + credential verification | `.trufflehog.yaml`  |

The specific tool you use depends on your agency's approved software list. All three are open source and widely used in federal environments. Your agency security team MAY have a preferred tool — check before choosing.

**General setup pattern** (adapt commands for your chosen tool):

```bash
# Step 1: Install the pre-commit framework
pip install pre-commit      # Python-based framework
# OR use your language's equivalent (husky for Node.js, etc.)

# Step 2: Create a pre-commit configuration file
# .pre-commit-config.yaml (example structure — adapt for your tool)
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0 # Pin to a specific version
    hooks:
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: check-merge-conflict
      - id: detect-private-key

  # Add your chosen secrets scanner here
  # Example placeholder — replace with your agency-approved tool:
  # - repo: <secrets-scanner-repo-url>
  #   rev: <pinned-version>
  #   hooks:
  #     - id: <scanner-hook-id>
```

```bash
# Step 3: Install the hooks
pre-commit install

# Step 4: Run against all existing files (first-time scan)
pre-commit run --all-files

# Step 5: Commit the configuration
git add .pre-commit-config.yaml
git commit -m "Add pre-commit hooks for secrets scanning"
```

### 4.2 Custom Rules

You SHOULD extend the default scanning rules to catch agency-specific patterns:

- Internal domain names or hostnames that should not be in public code
- Agency-specific token formats
- Internal IP address ranges
- Certificate or key file patterns specific to your environment

### 4.3 Handling False Positives

Secrets scanners sometimes flag values that are not actual secrets (e.g., test fixtures, example values, documentation). When this happens:

1. Verify the flagged value is genuinely not a secret
2. Add an inline suppression comment following your tool's syntax
3. Document why the suppression was added
4. Include the suppression in your commit for review

You MUST NOT disable the scanner globally to work around false positives. Address each false positive individually.

> **Control Mapping:** IA-5 (Authenticator Management), SC-28 (Protection of Information at Rest), SI-3 (Malicious Code Protection)

---

## 5. Branch Protection

<!-- NIST SP 800-53: CM-5 (Access Restrictions for Change), CM-3 (Configuration Change Control) -->
<!-- NIST SP 800-218A: PO.3 (Define and Use Criteria for Checks) -->

Branch protection rules ensure that no code — human-written or AI-generated — reaches production without proper review and automated validation. This is a critical compensating control for AI-assisted development.

### 5.1 Required Branch Protection Rules

You MUST configure the following protections on your default branch (typically `main`):

| Rule                                | Setting                            | Rationale                                                        |
| ----------------------------------- | ---------------------------------- | ---------------------------------------------------------------- |
| Require pull request reviews        | At least 1 reviewer; 2 recommended | Ensures human review of all changes, including AI-generated code |
| Dismiss stale reviews on new pushes | Enabled                            | Prevents approved reviews from covering different code           |
| Require status checks to pass       | Enabled — include CI pipeline      | Ensures automated scans run before merge                         |
| Require branches to be up to date   | Enabled                            | Prevents merging stale branches that may conflict                |
| Restrict force pushes               | No force push to main              | Preserves audit trail and prevents history rewriting             |
| Restrict deletions                  | Enabled                            | Prevents accidental branch deletion                              |

### 5.2 Configuring Branch Protection

The exact steps depend on your source control platform. The general approach:

1. Navigate to your repository's settings
2. Find the branch protection or branch rules section
3. Select your default branch (`main`)
4. Enable each rule from the table above
5. Save the configuration

**Platform-specific notes:**

- On GitHub: Settings > Branches > Add branch protection rule
- On GitLab: Settings > Repository > Protected branches
- On Bitbucket: Repository settings > Branch permissions
- On agency self-hosted platforms: Consult your platform administrator

### 5.3 Additional Recommendations

You SHOULD also:

- Require signed commits if your agency supports it (maps to SC-13, Cryptographic Protection)
- Require linear history (no merge commits) for cleaner audit trails
- Restrict who can push to protected branches to a defined set of maintainers
- Enable code owners files (CODEOWNERS) to automatically assign reviewers for sensitive paths

### 5.4 Why This Matters for AI Agents

AI agents typically commit code through pull requests, just like human developers. Branch protection ensures that:

- Every AI-generated change is reviewed by a human before it enters the main branch
- Automated security scans catch issues the agent may have introduced
- The audit trail is preserved — you can always trace who approved what

> **Control Mapping:** CM-5 (Access Restrictions for Change), CM-3 (Configuration Change Control), AC-6 (Least Privilege), AU-10 (Non-repudiation)

---

## 6. Environment Variables

<!-- NIST SP 800-53: SC-28 (Protection of Information at Rest), IA-5 (Authenticator Management), CM-6 (Configuration Settings) -->

Environment variables are the standard mechanism for providing configuration and secrets to applications at runtime without embedding them in source code. This section covers managing them securely.

### 6.1 The .env.example Pattern

You MUST create a `.env.example` file that documents every environment variable your application needs — without including actual secret values.

```bash
# .env.example — commit this file to version control
# Copy to .env and fill in values. NEVER commit .env itself.

# Application
APP_ENV=development
APP_PORT=8080
APP_LOG_LEVEL=info

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=                         # Required — get from secrets manager
DB_PASSWORD=                     # Required — get from secrets manager

# External API
API_BASE_URL=https://api.example.gov
API_KEY=                         # Required — get from secrets manager
API_TIMEOUT_MS=5000

# Feature flags
FEATURE_NEW_DASHBOARD=false
```

**Rules for .env.example:**

- MUST list every variable the application needs
- MUST include a comment describing each variable's purpose
- MUST leave secret values blank (or use a clearly fake placeholder like `CHANGE_ME`)
- MUST be committed to version control
- MUST NOT contain actual credentials, tokens, or keys

**Rules for .env:**

- MUST be listed in `.gitignore` (it contains real secrets)
- MUST NOT be committed to version control under any circumstances
- MUST be populated from your agency's secrets management system

### 6.2 Secrets Management

For production deployments, environment variables SHOULD be injected from an approved secrets management system rather than stored in `.env` files on disk.

**Common secrets management approaches** (choose based on your agency's approved services):

| Approach                                  | When to Use                                               |
| ----------------------------------------- | --------------------------------------------------------- |
| Platform secrets (CI/CD built-in secrets) | CI/CD pipeline secrets during build and deploy            |
| Cloud provider secrets manager            | Runtime secrets for cloud-deployed applications           |
| Self-hosted vault                         | Runtime secrets for on-premises or hybrid deployments     |
| Encrypted files (SOPS, age)               | Secrets committed encrypted to version control (advanced) |

Regardless of the approach, all secrets MUST:

- Be encrypted at rest using FIPS-validated encryption
- Be rotated on a defined schedule (per agency policy)
- Be auditable — access to secrets should be logged
- Be scoped to the minimum required audience (least privilege)

### 6.3 What AI Agents Need to Know

You SHOULD instruct your AI agent (via AGENTS.md) to:

- Reference `.env.example` when it needs to know what environment variables exist
- Never generate code that hardcodes values that should come from environment variables
- Use the standard environment variable access pattern for your language (e.g., `os.environ.get()` in Python, `process.env` in Node.js)
- Never log or print the values of secret environment variables

> **Control Mapping:** SC-28 (Protection of Information at Rest), IA-5 (Authenticator Management), CM-6 (Configuration Settings), AC-3 (Access Enforcement)

---

## 7. CI/CD Security Baseline

<!-- NIST SP 800-53: SA-11 (Developer Testing), SA-15 (Development Process), RA-5 (Vulnerability Monitoring) -->
<!-- NIST SP 800-218A: PW.6 (Configure the Build Process), PW.7 (Review and Test Code), PW.9 (Test Executable Code) -->

Your CI/CD (Continuous Integration / Continuous Delivery) pipeline is the automated gatekeeper that validates every change before it reaches production. At minimum, the pipeline MUST include the five checks below.

### 7.1 Minimum Pipeline Stages

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐    ┌──────────────┐
│  Lint   │───>│   Test   │───>│   SAST    │───>│ Dependency  │───>│   Secrets    │
│         │    │          │    │   Scan    │    │ Vuln Scan   │    │    Scan      │
└─────────┘    └──────────┘    └───────────┘    └─────────────┘    └──────────────┘
```

| Stage                             | Purpose                                                                     | Fails Build If                                      |
| --------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------- |
| **Lint**                          | Enforces coding standards and catches common errors                         | Style violations or syntax errors found             |
| **Test**                          | Runs automated test suite                                                   | Any test fails                                      |
| **SAST Scan**                     | Static Application Security Testing — scans source code for vulnerabilities | High or critical findings (configurable threshold)  |
| **Dependency vulnerability scan** | Checks dependencies against known CVE databases                             | Known critical/high vulnerabilities in dependencies |
| **Secrets scan**                  | Scans committed files for hardcoded secrets                                 | Secrets detected                                    |

**SAST** (Static Application Security Testing) analyzes your source code without executing it, looking for patterns that indicate security vulnerabilities — SQL injection, cross-site scripting, path traversal, and similar issues.

**SCA** (Software Composition Analysis) is the category that includes dependency vulnerability scanning. It checks your project's dependencies against databases of known vulnerabilities (CVEs).

### 7.2 Pipeline Configuration

The exact configuration depends on your CI/CD platform (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, etc.). The following is a generic pipeline definition showing the required stages:

```yaml
# Generic CI pipeline — adapt syntax for your platform
stages:
  - name: lint
    run: |
      # Run your language's linter
      # Examples: eslint, pylint, golangci-lint, clippy

  - name: test
    run: |
      # Run your test suite
      # Examples: pytest, jest, go test, cargo test

  - name: sast-scan
    run: |
      # Run your SAST scanner
      # Choose from your agency's approved tool list

  - name: dependency-scan
    run: |
      # Scan dependencies for known vulnerabilities
      # Examples: npm audit, pip-audit, cargo audit, trivy

  - name: secrets-scan
    run: |
      # Scan for hardcoded secrets
      # Use the same tool configured in your pre-commit hooks
```

### 7.3 Pipeline Security

Your CI/CD pipeline itself is a security-critical component. It MUST be configured securely:

- Pipeline configuration files MUST be version-controlled alongside application code
- CI/CD secrets MUST be stored in the platform's secrets management, not in pipeline configuration files
- Build environments SHOULD be ephemeral (destroyed after each run)
- Pipeline changes SHOULD require the same review process as application code
- Pipeline logs MUST NOT expose secret values (most platforms redact secrets by default — verify this is enabled)

### 7.4 Recommended Additional Stages

Beyond the five required stages, you SHOULD consider adding:

| Stage                       | Purpose                                             | When to Add                                              |
| --------------------------- | --------------------------------------------------- | -------------------------------------------------------- |
| Container image scan        | Scan container images for vulnerabilities           | If your project uses containers                          |
| Infrastructure as Code scan | Scan IaC templates for misconfigurations            | If your project includes Terraform, CloudFormation, etc. |
| SBOM generation             | Generate Software Bill of Materials                 | Required by OMB for federal software                     |
| License compliance          | Check dependency licenses for federal compatibility | For projects with many dependencies                      |

> **Control Mapping:** SA-11 (Developer Testing), SA-15 (Development Process), RA-5 (Vulnerability Monitoring), SI-3 (Malicious Code Protection), SA-12 (Supply Chain Protection)

---

## 8. IDE/Editor Hardening

<!-- NIST SP 800-53: CM-7 (Least Functionality), SC-7 (Boundary Protection), AU-2 (Audit Events) -->
<!-- NIST AI 600-1: GAI Risk — Data Privacy -->

Your Integrated Development Environment (IDE) or code editor is the primary interface between you, your AI agent, and your code. Configuring it securely reduces the risk of accidental data exposure.

### 8.1 Telemetry

Many editors and AI agent extensions collect usage data (telemetry) and send it to external servers. For federal systems at FIPS Moderate:

- You SHOULD disable telemetry in your editor and AI agent extensions unless your agency has explicitly authorized the telemetry destination
- You SHOULD review your AI agent's data handling policy to understand what data is sent externally
- You MUST NOT send CUI (Controlled Unclassified Information) or sensitive government data to unauthorized external services

**How to check:** Look in your editor's settings for "telemetry", "usage data", or "data collection" options. Check your AI agent extension's settings for similar options.

### 8.2 Sensitive File Handling

AI agents should not read or suggest changes to files that contain secrets or sensitive configuration. Configure your agent to exclude certain file patterns:

**Files to exclude from AI agent context:**

```
.env
.env.*
*.key
*.pem
*.p12
credentials.*
**/secrets/**
**/private/**
*.tfvars          # Terraform variable files often contain secrets
vault-config.*
```

The mechanism for excluding files varies by agent. Common approaches:

- Agent-specific ignore files (e.g., `.cursorignore`, agent-specific settings)
- Editor workspace settings that exclude paths from indexing
- Rules in AGENTS.md instructing the agent to skip certain file patterns

### 8.3 Auto-Suggest Restrictions

If your AI agent provides auto-complete or inline suggestions:

- You SHOULD disable auto-suggest when editing files that contain secrets or sensitive configuration
- You SHOULD review suggestions carefully before accepting — especially for security-sensitive code (authentication, authorization, cryptography)
- You SHOULD NOT allow agents to auto-complete values in `.env` files or secret configuration files

### 8.4 Workspace Scope

You SHOULD restrict your AI agent's file access to the project directory:

- Do not grant agents access to your entire home directory or filesystem
- Scope agent access to the repository root and its subdirectories
- If your agent supports workspace trust, enable it and verify the trust boundary

> **Control Mapping:** CM-7 (Least Functionality), SC-7 (Boundary Protection), AC-3 (Access Enforcement), AC-6 (Least Privilege)

---

## 9. Tooling Selection Criteria

<!-- NIST SP 800-53: SA-4 (Acquisition Process), SA-9 (External Information System Services) -->
<!-- FedRAMP 20x -->
<!-- OMB M-25-21 (AI Governance) -->

When selecting development tools — AI agents, CI/CD platforms, security scanners, cloud services — federal teams MUST evaluate them against security and compliance criteria, not just developer convenience. This section provides a tool-agnostic evaluation framework.

### 9.1 Mandatory Evaluation Criteria

You MUST evaluate any development tool against these criteria before adoption:

| Criterion                | What to Check                                                                                       | Why It Matters                                                                                                                                                            |
| ------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Authorization status** | Is the tool FedRAMP authorized (or agency-authorized equivalent)?                                   | FedRAMP authorization indicates the tool meets a baseline of federal security controls. For FIPS Moderate, the tool SHOULD hold FedRAMP Moderate or higher authorization. |
| **Data residency**       | Where is data stored and processed? Is it in the US? Can you restrict data to specific regions?     | Federal data MUST be stored and processed within jurisdictions authorized by your agency.                                                                                 |
| **Data handling**        | What data does the tool collect? Is code sent to external servers? Is data used for model training? | Understand what leaves your boundary. AI coding agents may send code to external APIs for processing.                                                                     |
| **Logging and audit**    | Does the tool provide audit logs? Can you export them? Are they tamper-resistant?                   | Federal systems require audit trails (AU-2). You need to be able to demonstrate what the tool did and when.                                                               |
| **Access control**       | Does the tool support SSO/SAML? Can you enforce MFA? Can you manage permissions granularly?         | Federal systems require centralized identity management and multi-factor authentication (IA-2).                                                                           |
| **Encryption**           | Does the tool encrypt data at rest and in transit? Are FIPS-validated modules used?                 | FIPS Moderate requires FIPS 140-2/3 validated cryptographic modules (SC-13).                                                                                              |

### 9.2 Additional Evaluation Criteria

You SHOULD also evaluate:

| Criterion                     | What to Check                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------- |
| **Incident response**         | Does the vendor have a documented incident response process? Will they notify you of breaches? |
| **Supply chain transparency** | Does the vendor publish an SBOM? Do they follow secure development practices?                  |
| **Exit strategy**             | Can you export your data if you switch tools? Is there vendor lock-in?                         |
| **Accessibility**             | Does the tool meet Section 508 requirements?                                                   |
| **Support**                   | Is support available during US business hours? Is there a government support tier?             |

### 9.3 AI Agent-Specific Criteria

When evaluating AI coding agents specifically, also consider:

| Criterion                   | What to Check                                                          |
| --------------------------- | ---------------------------------------------------------------------- |
| **Context window behavior** | What data is included in the AI's context? Can you control it?         |
| **Training data usage**     | Is your code used to train or improve the AI model? Can you opt out?   |
| **Prompt logging**          | Are your prompts and conversations logged? Where? Who can access them? |
| **Output filtering**        | Does the agent filter harmful, insecure, or inappropriate outputs?     |
| **Configuration**           | Can you customize the agent's behavior (via AGENTS.md or equivalent)?  |

### 9.4 Documentation Requirements

You MUST document your tool selection decision, including:

- Which criteria were evaluated
- How the tool met each criterion
- Any risk acceptances or compensating controls
- Approval authority (who authorized the tool for use)

This documentation supports your ATO package and helps future team members understand why specific tools were chosen.

> **Control Mapping:** SA-4 (Acquisition Process), SA-9 (External Information System Services), SA-12 (Supply Chain Protection), RA-3 (Risk Assessment)

---

## 10. Next Steps

With the controls in this guide implemented, your repository has a security baseline appropriate for AI-assisted federal development at FIPS Moderate. Here is what to read next:

| Document                                                        | What It Covers                                                  | When to Read                                      |
| --------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------- |
| [AGENTS.md](../AGENTS.md)                                       | Complete agent behavior rules — the rules your AI agent follows | Before your first AI-assisted coding session      |
| [CODING_PRACTICES.md](../CODING_PRACTICES.md)                   | Secure coding standards for AI-generated and human-written code | Before writing or reviewing any code              |
| [docs/SECURITY-CONTROLS.md](./SECURITY-CONTROLS.md)             | NIST 800-53 control overlay specific to agentic AI systems      | When building your SSP or preparing for ATO       |
| [docs/AGENT-IDENTITY.md](./AGENT-IDENTITY.md)                   | Agent identity, authentication, and delegation (NCCOE-aligned)  | When configuring agent service accounts or tokens |
| [templates/AGENTS.md.template](../templates/AGENTS.md.template) | Copy-paste AGENTS.md for new projects                           | When starting a new repository                    |
| [checklists/pre-deployment.md](../checklists/pre-deployment.md) | Pre-deployment security checklist                               | Before deploying to staging or production         |

### Summary Checklist

Before moving on, verify you have completed:

- [ ] Git installed and configured
- [ ] Repository created with internal/private visibility
- [ ] `.gitignore` includes secret file patterns
- [ ] `.editorconfig` committed
- [ ] `AGENTS.md` customized and committed
- [ ] Pre-commit hooks installed with secrets scanning
- [ ] Branch protection enabled on `main`
- [ ] `.env.example` created and committed; `.env` in `.gitignore`
- [ ] CI/CD pipeline configured with all five required stages
- [ ] Editor telemetry reviewed; sensitive files excluded from agent context
- [ ] Tool selection criteria documented

---

## Glossary

| Term        | Definition                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------- |
| **ATO**     | Authority to Operate — formal authorization for a federal system to process data at a specified impact level        |
| **CUI**     | Controlled Unclassified Information — unclassified information that requires safeguarding per federal regulation    |
| **CVE**     | Common Vulnerabilities and Exposures — a standardized identifier for known security vulnerabilities                 |
| **FedRAMP** | Federal Risk and Authorization Management Program — standardized approach to security assessment for cloud services |
| **FIPS**    | Federal Information Processing Standards — mandatory standards for federal computer systems                         |
| **NIST**    | National Institute of Standards and Technology                                                                      |
| **SAST**    | Static Application Security Testing — analyzing source code for vulnerabilities without executing it                |
| **SBOM**    | Software Bill of Materials — a formal list of all components in a piece of software                                 |
| **SCA**     | Software Composition Analysis — identifying and evaluating third-party components for known vulnerabilities         |
| **SSP**     | System Security Plan — documents the security controls in place for a federal information system                    |

---

## Version History

| Date       | Version | Change          |
| ---------- | ------- | --------------- |
| 2026-02-25 | 0.1.0   | Initial release |

## Framework References

- NIST SP 800-53 Rev 5.2.0 (September 2024)
- NIST SP 800-218A Secure Software Development Practices for Generative AI (June 2024)
- NIST AI RMF 1.0 (January 2023)
- NIST AI 600-1 Generative AI Profile (July 2024)
- NCCOE AI Agent Identity & Authorization Concept Paper (February 2026)
- OWASP Top 10 for LLM Applications 2025 (November 2024)
- CISA Secure by Design Principles (2025)
- FedRAMP 20x Authorization Framework (2025)
- OMB M-25-21 AI Governance (April 2025)
