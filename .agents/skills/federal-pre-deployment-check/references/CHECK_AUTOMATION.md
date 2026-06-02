---
title: "Pre-Deployment Check Automation Classification"
description: "Classifies each of the 58 pre-deployment checklist items as automated, semi-automated, or manual"
status: canonical
tier: 3
last_updated: "2026-06-01"
---

# Check Automation Classification

Each of the 58 pre-deployment checklist items is classified by how an agent can verify it.

## Classification Key

| Type | Description | Agent Action |
|------|-------------|-------------|
| **Automated** | Agent can run a tool and check the result | Run command, parse output, report pass/fail |
| **Semi-automated** | Agent can read files and assess compliance | Read files, search patterns, report findings |
| **Manual** | Requires human judgment or verification | Ask the user to verify, record their answer |

## Full Classification

### 1. Code Review and Provenance (SA-11, SA-15, CM-3)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 1.1 | Human review of AI-generated code | Manual | Ask reviewer |
| 1.2 | AI attribution documented | Semi-automated | Check PR description, AGENTS.md, or `git log --format='%b' \| grep Co-Authored-By` |
| 1.3 | Standard PR/review process followed | Manual | Ask reviewer |
| 1.4 | No direct commits to protected branches | Semi-automated | Check branch protection config or git history |
| 1.5 | Reviewer understands the code | Manual | Ask reviewer |

### 2. Secrets and Credentials (IA-5, SC-28)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 2.1 | No secrets in source code | Automated | `gitleaks detect` or grep fallback |
| 2.2 | No secrets in committed config | Automated | `gitleaks detect` (covers config files) |
| 2.3 | No secrets in CI/CD definitions | Semi-automated | Read CI config, check for inline secrets |
| 2.4 | No internal network info exposed | Semi-automated | Grep for IP patterns, hostnames |
| 2.5 | Secrets scanning hook active | Automated | Check `.pre-commit-config.yaml` for gitleaks/detect-secrets |
| 2.6 | Credentials from approved secrets mgmt | Manual | Ask developer about secrets source |

### 3. Input Validation and Output Encoding (SI-10, SI-15)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 3.1 | External input validated | Semi-automated | Search for input handling, check validation patterns |
| 3.2 | Parameterized SQL queries | Automated | Grep for string-concatenated SQL patterns |
| 3.3 | Context-appropriate output encoding | Semi-automated | Search for output encoding in templates |
| 3.4 | Path traversal prevention | Semi-automated | Search for path join/resolve without validation |
| 3.5 | No unsafe APIs with untrusted data | Automated | Grep for eval(), innerHTML, exec(), os.system() |
| 3.6 | Redirect URL allowlisting | Semi-automated | Search for redirect handling code |

### 4. Authentication and Authorization (IA-2, AC-3, AC-6)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 4.1 | All protected endpoints authenticated | Manual | Ask developer/reviewer |
| 4.2 | Server-side authorization enforcement | Manual | Ask developer/reviewer |
| 4.3 | Least privilege applied | Manual | Ask developer/reviewer |
| 4.4 | Secure session management | Manual | Ask developer/reviewer |
| 4.5 | No hardcoded auth bypasses | Manual | Ask developer/reviewer |

### 5. Dependency Security (SA-12, SR-3)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 5.1 | Dependencies pinned to exact versions | Automated | Parse package manifest for version ranges |
| 5.2 | Lock file committed | Automated | Check for lock file existence |
| 5.3 | No critical/high dependency CVEs | Automated | `npm audit --json` / `pip-audit` / `govulncheck` |
| 5.4 | Dependency licenses reviewed | Manual | Ask developer |
| 5.5 | Package names verified (typosquatting) | Manual | Ask developer |
| 5.6 | Dependency scanning in CI/CD | Automated | Check CI config for SCA tools |
| 5.7 | SBOM generated/updated | Manual | Ask developer |

### 6. Error Handling and Logging (AU-2, AU-3, SI-11)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 6.1 | Explicit error handling | Automated | Grep for empty catch/except blocks |
| 6.2 | No internal details in error messages | Semi-automated | Search for stack trace patterns in responses |
| 6.3 | No sensitive data in logs | Semi-automated | Search for PII patterns near log statements |
| 6.4 | Audit logging for security events | Manual | Ask developer |
| 6.5 | Structured log format | Manual | Ask developer |

### 7. Cryptography and Data Protection (SC-13, SC-28, SC-8)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 7.1 | TLS 1.2+ for all network comms | Semi-automated | Search for TLS config, SSLContext settings |
| 7.2 | TLS certificate validation enabled | Semi-automated | Search for verify=False, InsecureRequestWarning |
| 7.3 | Current FIPS-validated crypto | Semi-automated | Search for deprecated algorithms (MD5, SHA1, DES) |
| 7.4 | No custom cryptographic implementations | Semi-automated | Search for custom crypto patterns |
| 7.5 | Sensitive data encrypted at rest | Manual | Ask developer about storage encryption |
| 7.6 | No hardcoded crypto keys | Automated | Grep for PEM blocks, base64-encoded keys |

### 8. API and Network Security (SC-7, AC-4)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 8.1 | Authenticated API endpoints | Semi-automated | Search for unprotected route definitions |
| 8.2 | Rate limiting on public endpoints | Semi-automated | Search for rate limiting middleware/config |
| 8.3 | CORS with explicit origin allowlist | Semi-automated | Search for CORS config, check for wildcards |
| 8.4 | Security headers configured | Semi-automated | Search for helmet/security headers middleware |
| 8.5 | No sensitive data in URL params | Semi-automated | Search for query param construction with sensitive data |
| 8.6 | Request/response schema validation | Semi-automated | Search for schema validation middleware |

### 9. Testing (SA-11, CA-2)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 9.1 | Unit tests for new functionality | Manual | Ask developer |
| 9.2 | All existing tests pass | Automated | Run test suite (skipped for safety by default) |
| 9.3 | Error paths and edge cases tested | Manual | Ask developer |
| 9.4 | SAST scan passed | Automated | Check CI config for SAST tools |
| 9.5 | SCA scan passed | Automated | Check CI config for SCA tools |
| 9.6 | AI code reviewed for hallucinated APIs | Manual | Ask reviewer |

### 10. Infrastructure and Deployment (CM-2, CM-6, SA-10)

| # | Check | Type | Tool/Method |
|---|-------|------|-------------|
| 10.1 | Infrastructure changes version-controlled | Semi-automated | Check for IaC files in git |
| 10.2 | No default credentials | Semi-automated | Search for common default password patterns |
| 10.3 | Least-privilege IAM roles | Manual | Ask developer |
| 10.4 | Logging/monitoring enabled | Manual | Ask developer |
| 10.5 | Container images scanned | Semi-automated | Check CI for trivy/docker scan |
| 10.6 | Human approval gate for production | Manual | Ask developer |

## Summary

| Type | Count | Percentage |
|------|-------|-----------|
| Automated | 18 | 31% |
| Semi-automated | 22 | 38% |
| Manual | 18 | 31% |
| **Total** | **58** | **100%** |
