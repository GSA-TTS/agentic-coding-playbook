# Security Policy

## Scope

This repository contains **guidance documentation only** — no executable code, services, or infrastructure. Security concerns here relate to:

- Incorrect or outdated security guidance that could lead to insecure implementations
- Misaligned NIST control mappings that could cause compliance gaps
- Missing or wrong OWASP cross-references
- Guidance that contradicts authoritative federal publications

## Reporting a Concern

### For Guidance Accuracy Issues

If you find guidance that is **incorrect, outdated, or could lead to insecure implementations**:

1. **Preferred:** Open a [GitHub Issue](https://github.com/cloud-gov/federal-agentic-ai-guidance/issues/new) with the "guidance-accuracy" label
2. **For sensitive issues:** Email the maintainers listed in [CODEOWNERS](./CODEOWNERS)

Please include:

- Which document and section contains the issue
- The specific guidance that is incorrect
- The authoritative source that contradicts it (NIST publication, OMB memo, etc.)
- Suggested correction

### For Repository Security Issues

If you find a security issue with the **repository infrastructure** (CI pipeline, GitHub Actions, etc.):

1. Use [GitHub Security Advisories](https://github.com/cloud-gov/federal-agentic-ai-guidance/security/advisories/new) to report privately
2. Do **not** open a public issue for infrastructure security concerns

## Response Timeline

- **Acknowledgment:** Within 5 business days
- **Assessment:** Within 10 business days
- **Resolution:** Depends on severity and scope of required changes

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Framework Version Tracking

This guidance tracks evolving federal standards. When a referenced framework is updated (e.g., new NIST SP revision), we will:

1. Create an issue tracking the update
2. Review all affected documents
3. Update mappings and cross-references
4. Tag a new release with updated framework versions in CHANGELOG.md
