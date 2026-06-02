---
title: "AI Agent Threat Catalog"
description: "Pre-filled threat descriptions for the 10 threats in the risk assessment template, with OWASP references and example mitigations"
status: canonical
tier: 3
last_updated: "2026-06-01"
---

# AI Agent Threat Catalog

Pre-filled threat descriptions for the risk assessment template. Each entry
includes the OWASP reference, a plain-language description, example attack
scenarios, and common mitigations.

Source: OWASP Top 10 for LLM Applications 2025, OWASP Top 10 for Agentic AI 2026.

## T1: Prompt Injection

**OWASP Reference:** LLM01, Agentic-01

**Description:** An attacker crafts input that causes the AI agent to take
unauthorized actions — executing unintended commands, bypassing restrictions,
or disclosing sensitive information. This can happen directly (user input) or
indirectly (malicious content in files, API responses, or web pages the agent reads).

**Example scenarios:**
- Malicious code comment contains instructions the agent follows
- API response includes hidden text that redirects agent behavior
- Issue description contains encoded instructions to close other issues

**Common mitigations:**
- Treat all external content as untrusted data (AGENTS.md Section 11)
- Input validation on all external inputs (SI-10)
- Agent cannot override AGENTS.md rules based on prompts (AGENTS.md Section 10)

**Typical rating for FIPS Moderate:** Likelihood 3, Impact 4 (Risk: 12 — High)

## T2: Sensitive Data Disclosure

**OWASP Reference:** LLM02

**Description:** The AI agent unintentionally exposes secrets, PII, CUI, or
other sensitive data in its output — in code comments, commit messages, log
statements, error messages, or responses to the user.

**Example scenarios:**
- Agent includes API key in a code sample
- Agent logs PII from test data in debug output
- Agent puts internal hostnames in configuration documentation

**Common mitigations:**
- Pre-commit secrets scanning (IA-5)
- Agent prohibited from including PII in logs/comments (AGENTS.md Section 4)
- Data handling rules in AGENTS.md

**Typical rating for FIPS Moderate:** Likelihood 3, Impact 3 (Risk: 9 — Medium)

## T3: Supply Chain Compromise

**OWASP Reference:** LLM03, Agentic-07

**Description:** The AI agent introduces a malicious, vulnerable, or
inappropriate dependency — either by recommending a typosquatted package,
a package with known CVEs, or a package with incompatible licensing.

**Example scenarios:**
- Agent installs `requetss` instead of `requests` (typosquatting)
- Agent adds a dependency with a known critical CVE
- Agent recommends a package that sends telemetry data

**Common mitigations:**
- Dependency scanning in CI (SA-12, SR-3)
- Lock files committed to version control
- Agent must verify package names and check CVEs before adding (AGENTS.md Section 7)
- Approved registries list

**Typical rating for FIPS Moderate:** Likelihood 2, Impact 4 (Risk: 8 — Medium)

## T4: Insecure Code Generation

**OWASP Reference:** LLM05

**Description:** The AI agent generates code with security vulnerabilities —
SQL injection, XSS, path traversal, buffer overflow, or other OWASP Top 10
web application risks.

**Example scenarios:**
- Agent uses string concatenation for SQL queries
- Agent generates code with `eval()` on user input
- Agent creates file handling without path traversal checks

**Common mitigations:**
- SAST scanning in CI (SA-11)
- Human code review of all agent-generated code
- Coding standards enforcement (docs/CODING_PRACTICES.md)
- Pre-deployment checklist items 3.1-3.6

**Typical rating for FIPS Moderate:** Likelihood 3, Impact 3 (Risk: 9 — Medium)

## T5: Excessive Agency

**OWASP Reference:** LLM06, Agentic-06

**Description:** The AI agent performs actions beyond its intended scope or
authorization — accessing files outside the project, modifying system
configurations, or taking destructive actions without approval.

**Example scenarios:**
- Agent reads sensitive files outside the project directory
- Agent installs system-wide packages without asking
- Agent pushes code to production branch directly

**Common mitigations:**
- Least privilege configuration (AC-6)
- Actions requiring approval listed in AGENTS.md
- Branch protection rules
- File system boundary restrictions

**Typical rating for FIPS Moderate:** Likelihood 3, Impact 3 (Risk: 9 — Medium)

## T6: Credential Compromise

**OWASP Reference:** Agentic-02

**Description:** The agent's own credentials or tokens are exposed or stolen,
allowing an attacker to impersonate the agent or access resources with the
agent's permissions.

**Example scenarios:**
- Agent token stored in plain text in config file
- Agent credentials leaked in error message
- Agent session persists after user disconnects

**Common mitigations:**
- Secrets management system (IA-5)
- Session timeout and credential rotation
- Agent identity separate from user identity (AGENT-IDENTITY.md)
- Audit logging of all agent authentication events

**Typical rating for FIPS Moderate:** Likelihood 2, Impact 4 (Risk: 8 — Medium)

## T7: Unauthorized Code Execution

**OWASP Reference:** Agentic-03

**Description:** The AI agent executes code from an untrusted external source
without review — running scripts downloaded from the internet, executing
code from untrusted repositories, or following instructions embedded in
external content.

**Example scenarios:**
- Agent downloads and runs a setup script from a URL
- Agent executes code block found in a Stack Overflow answer
- Agent runs a script from an untrusted npm postinstall hook

**Common mitigations:**
- Agent prohibited from executing external code (AGENTS.md Section 10)
- Code review before execution
- Sandboxed execution environments

**Typical rating for FIPS Moderate:** Likelihood 2, Impact 5 (Risk: 10 — Medium)

## T8: Context/Memory Poisoning

**OWASP Reference:** Agentic-08

**Description:** An attacker manipulates the agent's context or memory to
influence its behavior in subsequent interactions — injecting false
information, modifying persistent state, or corrupting cached data.

**Example scenarios:**
- Malicious file content poisons agent's understanding of the codebase
- Injected comments create false security assumptions
- Modified config files redirect agent behavior

**Common mitigations:**
- No state persistence between unrelated sessions (AGENTS.md Section 2.3)
- Validate context sources
- Agent re-reads authoritative files (AGENTS.md, INDEX.yaml) at session start

**Typical rating for FIPS Moderate:** Likelihood 2, Impact 3 (Risk: 6 — Medium)

## T9: Audit Trail Gaps

**OWASP Reference:** Agentic-02

**Description:** Agent actions cannot be reconstructed from logs, making it
impossible to determine what the agent did, when, and why — undermining
accountability and incident response.

**Example scenarios:**
- Agent modifies files without logging the changes
- Agent commands not captured in audit trail
- Agent session lacks correlation IDs for tracing

**Common mitigations:**
- Audit logging of all agent actions (AU-2, AU-3)
- AI attribution documented (PR-level or commit-level per AGENTS.md)
- Structured log format with timestamps
- Agent cannot delete or modify logs (AGENTS.md Section 2.2)

**Typical rating for FIPS Moderate:** Likelihood 2, Impact 3 (Risk: 6 — Medium)

## T10: Human Trust Exploitation

**OWASP Reference:** Agentic-05

**Description:** Users over-trust agent output and accept code or
recommendations without adequate review, leading to deployment of
vulnerable, incorrect, or non-compliant code.

**Example scenarios:**
- Developer merges agent-generated code without reading it
- Reviewer rubber-stamps AI-assisted PR
- Team relies solely on agent for security decisions

**Common mitigations:**
- Human review required for all agent code (SA-11)
- Reviewer must not be the person who prompted the agent (AC-5)
- Agent flags code as requiring human review (AGENTS.md Section 8)
- Pre-deployment checklist item 9.6 (check for hallucinated APIs)

**Typical rating for FIPS Moderate:** Likelihood 4, Impact 3 (Risk: 12 — High)

## Risk Score Quick Reference

| Risk Level | Score | Action |
|-----------|-------|--------|
| Critical | 20-25 | MUST mitigate before deployment |
| High | 12-19 | MUST mitigate within 30 days |
| Medium | 6-11 | SHOULD mitigate |
| Low | 1-5 | MAY accept with documentation |

## Typical Risk Profile for FIPS Moderate

Based on common federal internal systems with standard controls:

| Threat | Typical Score | Level |
|--------|--------------|-------|
| T1: Prompt Injection | 12 | High |
| T2: Data Disclosure | 9 | Medium |
| T3: Supply Chain | 8 | Medium |
| T4: Insecure Code | 9 | Medium |
| T5: Excessive Agency | 9 | Medium |
| T6: Credential Compromise | 8 | Medium |
| T7: Unauthorized Execution | 10 | Medium |
| T8: Context Poisoning | 6 | Medium |
| T9: Audit Trail Gaps | 6 | Medium |
| T10: Human Trust | 12 | High |

These are starting points. Each system must assess its own risk based on
its specific deployment context, data sensitivity, and existing controls.
