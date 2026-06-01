---
title: "Security Tool Matrix"
description: "Maps programming languages to recommended security scanners, linters, and dependency audit tools"
status: canonical
tier: 3
last_updated: "2026-06-01"
---

# Security Tool Matrix

Maps programming languages to recommended security tools for federal AI development.
Tools are categorized by function: SAST (static analysis), SCA (dependency scanning),
secrets scanning, and linting.

## Tool Categories

| Category | Purpose | NIST Control | Required in CI? |
|----------|---------|-------------|-----------------|
| SAST | Static Application Security Testing | RA-5, SA-11 | Yes |
| SCA | Software Composition Analysis (dependency vulnerabilities) | RA-5, SA-12, SR-3 | Yes |
| Secrets | Detect hardcoded secrets and credentials | IA-5, SC-28 | Yes |
| Linter | Code quality and security patterns | SA-11 | Yes |
| Formatter | Consistent code style | CM-6 | Recommended |

## Language-Specific Tools

### Python

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | bandit | `pip install bandit` | `bandit -r src/ -f json` |
| SAST | semgrep | `pip install semgrep` | `semgrep --config=auto --json` |
| SCA | pip-audit | `pip install pip-audit` | `pip-audit --format=json` |
| SCA | safety | `pip install safety` | `safety check --json` |
| Linter | ruff | `pip install ruff` | `ruff check --output-format=json` |
| Formatter | ruff | `pip install ruff` | `ruff format --check` |

### JavaScript / TypeScript

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | semgrep | `npm install -g semgrep` | `semgrep --config=auto --json` |
| SAST | eslint-plugin-security | `npm install eslint-plugin-security` | Via ESLint config |
| SCA | npm audit | Built-in | `npm audit --json` |
| SCA | snyk | `npm install -g snyk` | `snyk test --json` |
| Linter | eslint | `npm install eslint` | `eslint --format=json` |
| Formatter | prettier | `npm install prettier` | `prettier --check .` |

### Go

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | gosec | `go install github.com/securego/gosec/v2/cmd/gosec@latest` | `gosec -fmt json ./...` |
| SAST | semgrep | `pip install semgrep` | `semgrep --config=auto --json` |
| SCA | govulncheck | `go install golang.org/x/vuln/cmd/govulncheck@latest` | `govulncheck -json ./...` |
| Linter | golangci-lint | `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` | `golangci-lint run --out-format=json` |
| Formatter | gofmt | Built-in | `gofmt -l .` |

### Java

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | semgrep | `pip install semgrep` | `semgrep --config=auto --json` |
| SAST | spotbugs | Maven/Gradle plugin | Via build tool |
| SCA | dependency-check | Maven/Gradle plugin | `dependency-check --format JSON` |
| Linter | checkstyle | Maven/Gradle plugin | Via build tool |
| Formatter | google-java-format | `google-java-format --dry-run --set-exit-if-changed` | Via build tool |

### .NET (C#)

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | semgrep | `pip install semgrep` | `semgrep --config=auto --json` |
| SAST | security-code-scan | NuGet package | Via build |
| SCA | dotnet list package | Built-in | `dotnet list package --vulnerable --format json` |
| Linter | dotnet format | Built-in | `dotnet format --verify-no-changes` |

### Rust

| Category | Tool | Install | CI Integration |
|----------|------|---------|----------------|
| SAST | cargo-audit | `cargo install cargo-audit` | `cargo audit --json` |
| SCA | cargo-audit | Same as above | `cargo audit --json` |
| Linter | clippy | Built-in | `cargo clippy -- -D warnings` |
| Formatter | rustfmt | Built-in | `cargo fmt -- --check` |

## Cross-Language Tools

These tools work across all languages:

| Category | Tool | Notes |
|----------|------|-------|
| Secrets | gitleaks | Pre-commit hook + CI. Recommended default. |
| Secrets | detect-secrets | Alternative with baseline support. |
| Secrets | trufflehog | Scans git history for leaked secrets. |
| SAST | semgrep | Multi-language SAST with federal-relevant rules. |
| SCA | trivy | Container and filesystem vulnerability scanner. |
| SBOM | syft | Generates SBOM in SPDX/CycloneDX format. |

## Selection Criteria

Per `docs/GETTING-STARTED.md` Section 9, tools MUST meet:

1. **FedRAMP authorization** status appropriate for data classification
2. **Data residency** — data stays within approved boundaries
3. **Data handling** — tool does not retain or train on scanned code
4. **Logging/audit** — tool provides audit-compatible output
5. **Access control** — tool supports role-based access
6. **Encryption** — data encrypted in transit and at rest
