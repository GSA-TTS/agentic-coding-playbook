---
title: "Control Traceability Matrix"
description: "Bidirectional mapping between NIST 800-53 controls, OWASP risks, document sections, and checklist items"
status: canonical
tier: 2
last_updated: "2026-02-25"
nist_controls: ["AC-2", "AC-3", "AC-5", "AC-6", "AC-12", "AC-17", "AU-2", "AU-3", "AU-6", "AU-12", "CM-2", "CM-3", "CM-5", "CM-6", "CM-7", "IA-2", "IA-5", "IA-8", "IR-4", "IR-6", "RA-3", "RA-5", "SA-4", "SA-5", "SA-8", "SA-11", "SA-12", "SA-15", "SA-17", "SC-7", "SC-8", "SC-13", "SC-28", "SI-2", "SI-3", "SI-10", "SI-11", "SI-17", "SR-3", "SR-11"]
frameworks: ["NIST SP 800-53 Rev 5.2", "OWASP Top 10 LLM 2025", "OWASP Top 10 Agentic 2026", "NIST AI RMF 1.0"]
audience: "isso"
keywords: ["traceability", "audit", "cross-reference", "control-mapping"]
related_files: ["AGENTS.md", "CODING_PRACTICES.md", "docs/SECURITY-CONTROLS.md", "checklists/pre-deployment.md"]
load_priority: "on-demand"
review_cycle: "quarterly"
---

<!-- LOAD: on-demand — Load when performing audit, tracing controls to documents, or preparing ATO evidence. -->

# Control Traceability Matrix

> **Version:** 0.1.0 | **Impact Level:** FIPS Moderate
>
> **Disclaimer:** This matrix is informational only. Each agency must verify control implementation against their specific ATO requirements.

This document provides bidirectional traceability between:
- **NIST SP 800-53 Rev 5.2 controls** (the compliance framework)
- **OWASP risks** (the threat model)
- **Guidance documents** (the implementation guidance)
- **Checklist items** (the verification steps)

Use this matrix to:
- **Auditors:** Trace from a control → find all documents and checklist items that address it
- **Developers:** Trace from a checklist failure → find the guidance that explains how to fix it
- **ISSOs:** Trace from an OWASP risk → find controls, guidance, and verification methods

---

## 1. NIST 800-53 Control → Document Mapping

For each control referenced in this guidance, this table shows where implementation guidance and verification steps can be found.

| Control | Name | AGENTS.md | CODING_PRACTICES.md | SECURITY-CONTROLS.md | AGENT-IDENTITY.md | Checklist |
|---------|------|-----------|--------------------|--------------------|-------------------|-----------|
| AC-2 | Account Management | §2.1 | — | §3.1 | §2, §3 | — |
| AC-3 | Access Enforcement | §3.1 | §3.2 | §3.1 | §4 | 4.1, 4.2 |
| AC-5 | Separation of Duties | — | — | §3.1 | — | 1.1 |
| AC-6 | Least Privilege | §3.1, §10 | — | §3.1 | §4 | 4.3 |
| AC-12 | Session Termination | §2.3 | — | §3.1 | §3 | — |
| AC-17 | Remote Access | §6.1 | — | §3.1 | — | — |
| AU-2 | Event Logging | §2.2 | §6.2 | §3.2 | §6 | 6.4 |
| AU-3 | Content of Audit Records | §2.2 | §6.2 | §3.2 | §6 | 6.5 |
| AU-6 | Audit Review | §2.2 | — | §3.2 | §6 | — |
| AU-12 | Audit Record Generation | §2.2, §14.3 | — | §3.2 | §6 | — |
| CM-2 | Baseline Configuration | §12.1, §15.3 | — | §3.3 | — | 10.1 |
| CM-3 | Configuration Change Control | §3.2, §13, §14.1, §14.2 | — | §3.3 | — | 1.3, 1.4 |
| CM-5 | Access Restrictions for Change | §3.2, §14.2 | — | §3.3 | — | 10.6 |
| CM-6 | Configuration Settings | §12.1, §15.3 | — | §3.3 | — | 10.2 |
| CM-7 | Least Functionality | §3.1, §10 | — | §3.3 | — | — |
| IA-2 | Identification and Authentication | §2.1 | §3.1 | §3.4 | §2, §3 | 4.1 |
| IA-5 | Authenticator Management | — | §4 | §3.4 | §3 | 2.1, 2.6 |
| IA-8 | Non-Org User Identification | §2.1 | — | §3.4 | §2 | — |
| IR-4 | Incident Handling | §9.1 | — | §3.5 | — | — |
| IR-6 | Incident Reporting | §9.2, §14.5 | — | §3.5 | — | — |
| RA-3 | Risk Assessment | §1 | — | §3.6 | — | — |
| RA-5 | Vulnerability Scanning | §9.2 | §5.2 | §3.6 | — | 9.4, 9.5 |
| SA-4 | Acquisition Process | — | §5.1 | §3.7 | — | — |
| SA-11 | Developer Testing | §8, §14.3, §14.4 | §1.1 | §3.7 | — | 9.1, 9.2, 9.3 |
| SA-12 | Supply Chain Protection | §7 | §5 | §3.7 | — | 5.1-5.7 |
| SA-15 | Development Process | §15.1, §15.2 | §1.1 | §3.7 | — | — |
| SA-5 | System Documentation | §15.4 | — | — | — | — |
| SA-8 | Security Engineering Principles | §15.1, §15.2 | — | §3.7 | — | — |
| SA-17 | Developer Security Architecture | §15.1 | — | — | — | — |
| SC-7 | Boundary Protection | §6.1 | §8 | §3.8 | — | 8.3 |
| SC-8 | Transmission Confidentiality | §6.1 | §8.1 | §3.8 | — | 7.1, 7.2 |
| SC-13 | Cryptographic Protection | §5.4 | §7 | §3.8 | — | 7.3, 7.4 |
| SC-28 | Protection at Rest | §4 | §4, §7 | §3.8 | — | 7.5 |
| SI-2 | Flaw Remediation | §9 | §5.2 | §3.9 | — | — |
| SI-3 | Malicious Code Protection | §10, §11 | — | §3.9 | — | — |
| SI-10 | Input Validation | §5.1, §11 | §2 | §3.9 | — | 3.1-3.6 |
| SI-11 | Error Handling | — | §6.1 | §3.9 | — | 6.1, 6.2 |
| SI-17 | Fail-Safe Procedures | §14.5, §14.6 | — | — | — | — |
| SR-3 | Supply Chain Controls | §7 | §5.2 | §3.10 | — | 5.1-5.7 |
| SR-11 | Component Authenticity | §7 | §5.2 | §3.10 | — | 5.5 |

---

## 2. OWASP Risk → Control and Guidance Mapping

### OWASP Top 10 for LLM Applications 2025

| OWASP ID | Risk | Primary Controls | AGENTS.md | CODING_PRACTICES.md | Checklist |
|----------|------|-----------------|-----------|--------------------|-----------|
| LLM01 | Prompt Injection | SI-10, SI-3 | §11 | §2.1 | 3.1 |
| LLM02 | Sensitive Information Disclosure | SC-28, SI-12 | §4 | §4, §6.2 | 2.1-2.6, 6.3 |
| LLM03 | Supply Chain Vulnerabilities | SA-12, SR-3 | §7 | §5 | 5.1-5.7 |
| LLM04 | Data and Model Poisoning | SI-10 | §11 | — | — |
| LLM05 | Improper Output Handling | SI-10, SI-15 | — | §2.2 | 3.1-3.6 |
| LLM06 | Excessive Agency | AC-6, CM-7 | §3, §10 | — | 4.3 |
| LLM07 | System Prompt Leakage | SC-28 | §4 | — | 2.1 |
| LLM08 | Vector and Embedding Weaknesses | — | — | — | — |
| LLM09 | Misinformation | SA-11 | §8.2 | §1.2 | 9.6 |
| LLM10 | Unbounded Consumption | — | — | §8.1 | 8.2 |

### OWASP Top 10 for Agentic Applications 2026

| OWASP ID | Risk | Primary Controls | AGENTS.md | CODING_PRACTICES.md | Checklist |
|----------|------|-----------------|-----------|--------------------|-----------|
| Agentic-01 | Agent Goal Hijack | SI-10 | §11 | §2.1 | 3.1 |
| Agentic-02 | Identity and Privilege Abuse | AC-2, AC-6, IA-2 | §2, §3 | §3 | 4.1-4.5 |
| Agentic-03 | Unexpected Code Execution | CM-7, SI-3 | §10 | — | — |
| Agentic-04 | Insecure Inter-Agent Communication | — | Out of scope (MVP) | — | — |
| Agentic-05 | Human Agent Trust Exploitation | AC-6 | §3.2, §8.2 | §1.2 | 1.1, 1.5 |
| Agentic-06 | Tool Misuse and Exploitation | AC-6, CM-7 | §3, §10 | — | 4.3 |
| Agentic-07 | Agentic Supply Chain Vulnerabilities | SA-12, SR-3 | §7 | §5 | 5.1-5.7 |
| Agentic-08 | Memory and Context Poisoning | SI-10 | §11 | — | — |
| Agentic-09 | Cascading Failures | IR-4 | §9 | §6.1 | — |
| Agentic-10 | Rogue Agents | CM-7, AU-2 | §10 | — | — |

---

## 3. Checklist Item → Control and Guidance Mapping

This reverse mapping lets reviewers trace from a failed checklist item back to the control it satisfies and the guidance for remediation.

| Checklist # | Checklist Item | NIST Control | Guidance Location |
|------------|---------------|-------------|-------------------|
| 1.1 | Human review of AI-generated code | SA-11, AC-5 | AGENTS.md §8.2 |
| 1.2 | AI attribution in commits | SA-15 | AGENTS.md §2.1 |
| 1.3 | Standard PR/review process followed | CM-3 | AGENTS.md §3.2 |
| 1.4 | No direct commits to protected branches | CM-3, CM-5 | AGENTS.md §3.2 |
| 1.5 | Reviewer understands the code | SA-11 | AGENTS.md §8.2 |
| 2.1 | No secrets in source code | IA-5, SC-28 | CODING_PRACTICES.md §4 |
| 2.2 | No secrets in committed config | IA-5 | CODING_PRACTICES.md §4 |
| 2.3 | No secrets in CI/CD definitions | IA-5 | CODING_PRACTICES.md §4.2 |
| 2.4 | No internal network info exposed | SC-7 | AGENTS.md §6.1 |
| 2.5 | Secrets scanning hook active | IA-5 | GETTING-STARTED.md §4 |
| 2.6 | Credentials from approved secrets mgmt | IA-5, SC-28 | CODING_PRACTICES.md §4.1 |
| 3.1 | External input validated | SI-10 | CODING_PRACTICES.md §2.1 |
| 3.2 | Parameterized SQL queries | SI-10 | CODING_PRACTICES.md §2.1 |
| 3.3 | Context-appropriate output encoding | SI-10, SI-15 | CODING_PRACTICES.md §2.2 |
| 3.4 | Path traversal prevention | SI-10 | CODING_PRACTICES.md §2.1 |
| 3.5 | No unsafe APIs with untrusted data | SI-10, SC-18 | CODING_PRACTICES.md §9 |
| 3.6 | Redirect URL allowlisting | SI-10 | CODING_PRACTICES.md §9 |
| 4.1 | All protected endpoints authenticated | IA-2, AC-3 | CODING_PRACTICES.md §3.1 |
| 4.2 | Server-side authorization enforcement | AC-3 | CODING_PRACTICES.md §3.2 |
| 4.3 | Least privilege applied | AC-6 | AGENTS.md §3.1 |
| 4.4 | Secure session management | SC-23 | CODING_PRACTICES.md §3.3 |
| 4.5 | No hardcoded auth bypasses | AC-3 | CODING_PRACTICES.md §3.2 |
| 5.1 | Dependencies pinned to exact versions | SA-12, SR-3 | CODING_PRACTICES.md §5.2 |
| 5.2 | Lock file committed | SA-12 | CODING_PRACTICES.md §5.2 |
| 5.3 | No critical/high dependency CVEs | RA-5, SR-3 | CODING_PRACTICES.md §5.2 |
| 5.4 | Dependency licenses reviewed | SA-4 | CODING_PRACTICES.md §5.1 |
| 5.5 | Package names verified (typosquatting) | SR-11 | CODING_PRACTICES.md §5.1, AGENTS.md §7.1 |
| 5.6 | Dependency scanning in CI/CD | RA-5 | CODING_PRACTICES.md §5.2 |
| 5.7 | SBOM generated/updated | SA-12 | CODING_PRACTICES.md §5.2 |
| 6.1 | Explicit error handling | SI-11 | CODING_PRACTICES.md §6.1 |
| 6.2 | No internal details in error messages | SI-11 | CODING_PRACTICES.md §6.1 |
| 6.3 | No sensitive data in logs | AU-3 | CODING_PRACTICES.md §6.2 |
| 6.4 | Audit logging for security events | AU-2 | CODING_PRACTICES.md §6.2 |
| 6.5 | Structured log format | AU-3 | CODING_PRACTICES.md §6.2 |
| 7.1 | TLS 1.2+ for all network comms | SC-8 | AGENTS.md §6.1 |
| 7.2 | TLS certificate validation enabled | SC-8 | AGENTS.md §6.1 |
| 7.3 | Current FIPS-validated crypto | SC-13 | AGENTS.md §5.4 |
| 7.4 | No custom cryptographic implementations | SC-13 | AGENTS.md §5.4 |
| 7.5 | Sensitive data encrypted at rest | SC-28 | CODING_PRACTICES.md §7 |
| 7.6 | No hardcoded crypto keys | SC-13, IA-5 | AGENTS.md §5.4 |
| 8.1 | Authenticated API endpoints | IA-2, AC-3 | CODING_PRACTICES.md §8.1 |
| 8.2 | Rate limiting on public endpoints | SC-7 | CODING_PRACTICES.md §8.1 |
| 8.3 | CORS with explicit origin allowlist | SC-7 | CODING_PRACTICES.md §8.2 |
| 8.4 | Security headers configured | SC-7 | CODING_PRACTICES.md §8.2 |
| 8.5 | No sensitive data in URL params | SC-8 | CODING_PRACTICES.md §8.1 |
| 8.6 | Request/response schema validation | SI-10 | CODING_PRACTICES.md §8.1 |
| 9.1 | Unit tests for new functionality | SA-11 | AGENTS.md §8.1 |
| 9.2 | All existing tests pass | SA-11 | AGENTS.md §8.1 |
| 9.3 | Error paths and edge cases tested | SA-11 | AGENTS.md §8.1 |
| 9.4 | SAST scan passed | RA-5, SA-11 | CODING_PRACTICES.md §10.2 |
| 9.5 | SCA scan passed | RA-5, SA-12 | CODING_PRACTICES.md §5.2 |
| 9.6 | AI code reviewed for hallucinated APIs | SA-11 | CODING_PRACTICES.md §1.2 |
| 10.1 | Infrastructure changes version-controlled | CM-2, SA-10 | CODING_PRACTICES.md §10.1 |
| 10.2 | No default credentials | CM-6, IA-5 | CODING_PRACTICES.md §10.1 |
| 10.3 | Least-privilege IAM roles | AC-6 | CODING_PRACTICES.md §10.1 |
| 10.4 | Logging/monitoring enabled | AU-2, AU-12 | CODING_PRACTICES.md §10.1 |
| 10.5 | Container images scanned | RA-5 | CODING_PRACTICES.md §5.3 |
| 10.6 | Human approval gate for production | CM-5 | AGENTS.md §3.2 |

---

## 4. AI RMF Function → Document Mapping

| AI RMF Function | Sub-Function | Primary Documents |
|----------------|-------------|-------------------|
| **GOVERN** | GOVERN 1 — Policies | AGENTS.md §1, §10, §12, §13, §14, §15 |
| | GOVERN 6 — Accountability | AGENTS.md §2, AGENT-IDENTITY.md §2, §5, §6 |
| **MAP** | MAP 1 — Context | GETTING-STARTED.md, risk-assessment template |
| | MAP 3 — Supply Chain | AGENTS.md §7, CODING_PRACTICES.md §5 |
| | MAP 5 — Data | AGENTS.md §4, CODING_PRACTICES.md §4 |
| **MEASURE** | MEASURE 1 — Metrics | AGENTS.md §8, pre-deployment checklist |
| | MEASURE 2 — Testing | AGENTS.md §8, §15, CODING_PRACTICES.md §1, SECURITY-CONTROLS.md §3.6 |
| **MANAGE** | MANAGE 1 — Risk Treatment | AGENTS.md §14, SECURITY-CONTROLS.md §5, risk-assessment template §6 |
| | MANAGE 2 — Ongoing Monitoring | AGENTS.md §6, §11, SECURITY-CONTROLS.md §3.6 |
| | MANAGE 4 — Incident Response | AGENTS.md §9, SECURITY-CONTROLS.md §3.5 |

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-25 | 0.1.0 | Initial release |
