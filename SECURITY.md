# Security Policy

## Scope

This repository is part of the **Agentic Coding Capability Assessment** — an internal GSA initiative. It contains:

- **Reference documentation** for secure agentic coding practices
- **Python validation toolchain** (`scripts/playbook_validator/`)
- **Skills and templates** for AI-assisted development

There are no deployed services or production infrastructure. Security concerns here relate to:

- Incorrect or outdated standards that could lead to insecure implementations
- Misaligned NIST control mappings that could cause compliance gaps
- Content that contradicts authoritative federal publications

> **Note:** This repository provides informational content and best practices. It is not authoritative GSA policy or official federal guidance.

## Reporting and Fixing Security Issues

This is an **internal assessment repository** with trusted contributors. The appropriate response to most issues is to fix them directly.

### For Content Accuracy Issues

If you find content that is incorrect, outdated, or could lead to insecure implementations:

1. **Submit a PR to fix it** — This is the preferred approach for internal repos
2. **Open an issue** if you're unsure how to fix it or want to discuss first
3. **Ask in the agentic-coding Slack channel** if you have questions or need help

Please include:
- Which document and section contains the issue
- The specific content that is incorrect
- The authoritative source that contradicts it (NIST publication, OMB memo, etc.)
- Suggested correction

### For Repository Infrastructure Issues

If you find a security issue with the repository infrastructure (CI pipeline, GitHub Actions, dependencies, validation scripts):

1. **Submit a PR to fix it** — You have access, so fix it directly when possible
2. **Open an issue** to track the problem if you need help or it requires discussion
3. **Contact channel admins** if you're unsure about the right approach

Since this is an internal repository, formal security advisories are not required. Use your judgment — if something seems sensitive, discuss with channel admins before posting details publicly.

### For GSA Platform Issues (Outside This Repo)

For security concerns related to GSA systems or infrastructure outside the scope of this repository:

- **Follow your normal GSA security reporting processes**
- **Submit a ticket** or **email GSA security** as appropriate for your organization

These repos are for the assessment — platform and infrastructure security follows standard GSA procedures.

## Framework Version Tracking

This content tracks evolving federal standards. When a referenced framework is updated (e.g., new NIST SP revision), we will:

1. Create an issue tracking the update
2. Review all affected documents
3. Update mappings and cross-references
4. Tag a new release with updated framework versions in CHANGELOG.md

## Security Best Practices

When using this repository:

1. **Validate all content** — Run `make validate` before using templates
2. **Check authoritative sources** — This content references NIST/OMB/OWASP but is not a substitute
3. **Review agent-generated code** — AI-assisted development requires human review
4. **Follow AGENTS.md** — The behavioral contract helps prevent unsafe agent actions

## Supported Versions

Security updates are applied to the current `main` branch. Check the [CHANGELOG](CHANGELOG.md) for the current version.

---

**Last Updated:** 2026-05-21
