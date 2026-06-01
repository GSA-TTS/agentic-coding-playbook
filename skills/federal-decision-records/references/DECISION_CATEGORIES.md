---
title: "Decision Categories for Federal AI Projects"
description: "Pre-filled decision categories with suggested NIST control mappings and example decisions"
status: canonical
tier: 3
last_updated: "2026-06-01"
---

# Decision Categories for Federal AI Projects

Each category maps to relevant NIST 800-53 controls. When creating a decision
record, suggest the mapped controls — the user can accept, modify, or skip.

## Categories

### 1. Agent Authorization

Decisions about which AI agents are authorized, what capabilities they have,
and what actions are prohibited.

**Suggested NIST controls:** AC-2, AC-3, AC-6, CM-7, PL-4

**Example decisions:**
- Use GitHub Copilot as the authorized AI coding agent for Project X
- Restrict agent file system access to the repository directory only
- Prohibit agent from making network calls outside the approved allowlist
- Require human approval for all agent-initiated git push operations

**Decision drivers to suggest:**
- Least privilege (AC-6)
- Agent identity and accountability (IA-8, AU-2)
- Prohibited actions list (PL-4)
- FedRAMP authorization status of agent vendor

### 2. Data Handling

Decisions about data classification, access controls, encryption, and data
flows involving AI agents.

**Suggested NIST controls:** AC-3, MP-4, SC-8, SC-13, SC-28, SI-12

**Example decisions:**
- Classify all agent-processed data as CUI with NIST 800-171 controls
- Encrypt all data at rest using AES-256 with FIPS 140-3 validated module
- Prohibit agent from accessing PII databases directly
- Route all agent API calls through the agency proxy for DLP inspection

**Decision drivers to suggest:**
- Data classification (FIPS 199, NIST 800-60)
- Encryption requirements (SC-13, FIPS 140-3)
- Data minimization (SI-12)
- Data residency (agency policy)

### 3. Deployment and Infrastructure

Decisions about deployment architecture, CI/CD security, environment
separation, and infrastructure configuration.

**Suggested NIST controls:** CM-2, CM-3, CM-6, SA-10, SA-11, RA-5

**Example decisions:**
- Deploy to agency-managed GovCloud with FedRAMP High baseline
- Require all CI/CD pipelines to include SAST, SCA, and secrets scanning
- Separate development, staging, and production environments with network isolation
- Require human approval gate before production deployment

**Decision drivers to suggest:**
- Baseline configuration (CM-2)
- Change control (CM-3)
- Separation of duties (AC-5)
- Vulnerability scanning (RA-5)

### 4. Authentication and Identity

Decisions about how agents and users authenticate, session management,
identity federation, and credential storage.

**Suggested NIST controls:** IA-2, IA-5, IA-8, AC-2, AC-7, AC-12

**Example decisions:**
- Use PIV/CAC for all human authentication to the development environment
- Authenticate AI agent via OAuth 2.0 service account with scoped permissions
- Store all secrets in HashiCorp Vault with automatic rotation
- Enforce session timeout of 15 minutes for agent API tokens

**Decision drivers to suggest:**
- Multi-factor authentication (IA-2)
- Credential management (IA-5)
- Agent identity (NCCOE Agent Identity)
- Session management (AC-12)

### 5. Cryptography

Decisions about cryptographic algorithms, key management, TLS configuration,
and FIPS validation requirements.

**Suggested NIST controls:** SC-8, SC-12, SC-13, SC-17

**Example decisions:**
- Use TLS 1.3 for all agent-to-service communication
- Use FIPS 140-3 validated cryptographic module for all encryption operations
- Implement automated key rotation every 90 days
- Prohibit use of MD5, SHA-1, DES, 3DES, and RSA < 2048-bit

**Decision drivers to suggest:**
- FIPS 140-2/3 compliance (SC-13)
- Key management (SC-12)
- Transport encryption (SC-8)
- Certificate management (SC-17)

### 6. Audit and Monitoring

Decisions about logging, monitoring, incident response, and audit trail
requirements for AI agent activities.

**Suggested NIST controls:** AU-2, AU-3, AU-6, AU-12, IR-4, IR-6, SI-4

**Example decisions:**
- Log all agent actions with timestamp, agent ID, action, and outcome
- Send agent audit logs to SIEM within 5 minutes of generation
- Generate alerts for agent actions that exceed normal patterns
- Retain agent audit logs for 3 years per NARA schedule

**Decision drivers to suggest:**
- Audit events (AU-2)
- Content of audit records (AU-3)
- Continuous monitoring (SI-4)
- Incident handling (IR-4)

### 7. Dependency and Supply Chain

Decisions about third-party dependencies, supply chain security, SBOM
generation, and vendor risk management.

**Suggested NIST controls:** SA-12, SR-3, SR-4, SR-11, RA-5

**Example decisions:**
- Pin all dependencies to exact versions with lock files
- Run dependency vulnerability scanning in CI using OSV-Scanner
- Generate SBOM in CycloneDX format for all releases
- Require security review for any new dependency with >100KB bundle size

**Decision drivers to suggest:**
- Supply chain risk management (SR-3)
- Component authenticity (SR-4)
- Vulnerability scanning (RA-5)
- SBOM requirements (EO 14028)

### 8. Input Validation and Output Handling

Decisions about how the system validates input from AI agents and external
sources, and how agent output is sanitized.

**Suggested NIST controls:** SI-10, SI-15, SC-18

**Example decisions:**
- Validate all agent-generated SQL using parameterized queries only
- Sanitize all agent output before rendering in web UI (XSS prevention)
- Reject agent-generated code that uses eval(), exec(), or dynamic imports
- Implement output length limits on all agent responses

**Decision drivers to suggest:**
- Input validation (SI-10)
- Information output filtering (SI-15)
- OWASP Top 10 for LLM (prompt injection, insecure output handling)
- OWASP Top 10 for Agentic AI (excessive agency, privilege escalation)

## Using Categories

When creating a decision record:

1. Present this list and ask which category applies
2. Use the suggested NIST controls as defaults (user can modify)
3. Use the decision drivers as prompts to help the user think through
   compliance implications
4. If a decision spans multiple categories, use the primary category and
   list secondary controls from other categories
