---
title: "AI-Assisted Contribution Policy"
description: "Canonical policy governing AI-assisted contributions — human accountability, disclosure, provenance, verification, data handling, security review, and licensing posture for federal AI-assisted development"
status: canonical
tier: 2
last_updated: "2026-06-30"
nist_controls: ["AU-2", "AU-3", "CA-2", "CM-3", "IA-8", "PL-4", "SA-5", "SA-11", "SA-15", "SC-8", "SC-28", "SI-10", "SI-12", "SR-3"]
frameworks: ["OMB M-25-21", "NIST AI RMF 1.0", "NIST AI 600-1", "NIST SP 800-218A", "OMB M-16-21", "U.S. Copyright Office AI Part 2", "Developer Certificate of Origin 1.1", "OWASP Top 10 LLM 2025", "OWASP Top 10 Agentic 2026"]
audience: ["developers", "managers", "isso"]
keywords: ["ai-contribution", "human-accountability", "disclosure", "provenance", "DCO", "CC0", "copyright", "verification", "contribution-policy"]
related_files: ["AGENTS.md", "CONTRIBUTING.md", "docs/AGENT-IDENTITY.md", "docs/FEDERAL-AI-LANDSCAPE.md", "data/federal-ai-landscape.yaml"]
load_priority: "task-context"
review_cycle: "quarterly"
---

<!-- LOAD: on-demand — Load when a task involves contribution policy, AI attribution/disclosure, provenance/DCO, or licensing of AI-assisted work. -->

# AI-Assisted Contribution Policy

> **Disclaimer:** This policy references federal guidance, statutes, and agency positions (e.g., OMB memoranda, NIST standards, and U.S. Copyright Office reports) for context only. It is **not legal advice** and does not constitute official GSA policy or an authoritative interpretation of any federal requirement. Agencies and contributors remain responsible for tailoring these expectations to their own ATO requirements, organizational policy, and risk tolerance. Where an agency position is cited (notably U.S. Copyright Office guidance), it is identified as that agency's stated position and not as settled law.
>
> **Key words:** "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" are used per [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## 1. Purpose & Scope

This document is the **canonical** policy governing AI-assisted contributions to this repository and to downstream repositories that reference it (the community patterns hub and the quickstart). It defines the **behavioral and accountability expectations** for any contributor who uses an AI coding agent or assistant to help author a contribution.

This policy is a **stated expectation enforced at review time** — a maintainer reviewing a contribution applies these clauses as acceptance criteria. It is not self-executing automation.

**In scope:** human accountability, disclosure, provenance, verification, data handling, security review, licensing posture, and proportional review rigor for AI-assisted work.

**Out of scope:** contributor *eligibility* mechanics (e.g., federal-employee/contractor `.gov`/`.mil` requirements) and the pull-request-template attestation checkbox. Those live in the downstream `CONTRIBUTING.md` and pull-request template; this document references that they exist but does **not** define them. This is the behavioral/accountability policy, not the eligibility gate.

> **Control Mapping:** PL-4 (Rules of Behavior), SA-5 (System Documentation)

## 2. Core Principle: Human Ownership & Accountability

An AI agent is a tool. The **human contributor is the author of record** and is fully accountable for every AI-assisted contribution they submit — to the same degree as if they had written every line themselves. Federal AI governance places human accountability and meaningful oversight at the center of permissible AI use; this repository adopts that posture without exception.

The submitting human MUST be able to **explain and defend every change** in a contribution. **If a contributor cannot explain a change, they MUST NOT submit it.** "The AI wrote it" is never a sufficient account of a change.

> Federal basis: OMB M-25-21 (human oversight / accountability for AI use); NIST AI RMF 1.0 GOVERN (accountability) and AI 600-1 (Generative AI Profile).
>
> **Control Mapping:** AU-3 (Content of Audit Records — traceability), PL-4 (Rules of Behavior), SA-11 (Developer Testing)

## 3. Human Accountability for AI-Assisted Contributions

The contributor MUST:
- Take full ownership of any AI-assisted change as their own work.
- Be prepared to explain, in their own words, **what** the change does, **why** it is correct, and **how** they verified it.
- Decline to submit — and remove — any AI-suggested change they do not understand well enough to defend in review.

The contributor MUST NOT:
- Submit code, configuration, or documentation whose behavior or rationale they cannot account for.
- Treat AI authorship as a transfer of responsibility; accountability remains with the human.

> Federal basis: OMB M-25-21 (human oversight); NIST AI RMF 1.0 GOVERN.
>
> **Control Mapping:** AU-3 (Content of Audit Records), SA-11 (Developer Testing), PL-4 (Rules of Behavior)

## 4. Disclosure of AI Assistance

Contributors SHOULD disclose AI assistance — which tool(s) were used and for what (e.g., "OpenCode used to draft the parser and tests").

- **Pull-request-level disclosure is RECOMMENDED.** A short note in the PR description is the preferred mechanism.
- **Per-commit attribution is OPTIONAL.** A contributor MAY add a commit-level `Co-authored-by:` trailer, but it is not required.

This is consistent with the playbook's existing identity stance (`AGENTS.md` §2): system-level traceability over granular per-commit attribution. Disclosure supports review and audit — it does not diminish the human accountability of §2–§3.

> Federal basis: NIST AI RMF 1.0 GOVERN (transparency); NIST AI 600-1.
>
> **Control Mapping:** AU-2 (Audit Events), AU-3 (Content of Audit Records), IA-8 (Identification)

## 5. Provenance — Only Humans Certify Origin

Provenance certification is a human act of legal and ethical responsibility. An AI agent cannot certify the origin or contribution rights of a change.

Contributors and agents MUST NOT:
- Add a Developer Certificate of Origin `Signed-off-by:` trailer on behalf of, or as, an AI agent.
- Let an agent self-certify provenance, license compatibility, or contribution rights.

A `Signed-off-by:` trailer, where used, MUST be added by a **human** who thereby certifies the Developer Certificate of Origin 1.1 terms. The certifying human takes responsibility for license compliance and for the right to contribute the change.

> Federal basis: Developer Certificate of Origin 1.1 (Linux Foundation) — only a human can attest origin.
>
> **Control Mapping:** AU-3 (Content of Audit Records), SR-3 (Supply Chain Controls), CM-3 (Configuration Change Control)

## 6. Verification Before Submission

AI-generated output is a draft, not a finished contribution. The contributor MUST review and verify it before submission.

The contributor MUST:
- Review and verify all AI-generated code, configuration, and documentation before submitting it.
- Confirm that the contribution meets the **same testing, security, and review bar** as any non-AI contribution (per `AGENTS.md` §8 testing requirements and §14.4 run-and-verify loop).
- Run the project's tests and checks and confirm they pass against the real flow, not a mocked one.

The contributor MUST NOT submit contributions containing:
- **Fabricated or hallucinated APIs**, functions, flags, or library names that do not exist.
- **Fabricated citations**, references, or documentation links.
- **Placeholder or stub content** presented as complete (e.g., `TODO`, `...`, invented example data left in place of real implementation).

When AI suggests a **new dependency**, the contributor MUST verify the package actually exists, is the intended (non-typosquatted) package, and is from a trusted registry before adding it — AI tools routinely hallucinate plausible-sounding package names ("slopsquatting" risk). This reinforces `AGENTS.md` §7 (Supply Chain Security).

> Federal basis: NIST SP 800-218A (Secure Software Development Practices for GenAI); NIST AI 600-1 (validity / reliability).
>
> **Control Mapping:** SA-11 (Developer Testing), SI-10 (Input Validation), CA-2 (Control Assessments)

## 7. Data Handling

AI tools transmit and may retain whatever a contributor inputs. Contributors MUST respect data authorization boundaries when using them.

The contributor MUST NOT input into an AI tool — for prompting, context, or any purpose — any of the following **unless that specific tool is authorized for that data class**:
- Secrets, credentials, API keys, or tokens.
- Personally Identifiable Information (PII).
- Controlled Unclassified Information (CUI).
- Non-public government data of any kind.

The contributor MUST:
- Respect the ATO / authorization boundary of the system and of the AI tool — an unapproved tool is an unapproved destination for data.
- Default to the highest applicable protection level when a data classification is uncertain (consistent with `AGENTS.md` §4).

> Federal basis: OMB M-25-22 context — vendors must not train on non-public government data without consent; respect authorization boundaries for AI tools.
>
> **Control Mapping:** SC-28 (Protection of Information at Rest), SC-8 (Transmission Confidentiality), SI-12 (Information Management)

## 8. Security Review of AI-Generated Output

AI-generated code carries characteristic security risks (insecure output handling, injection-prone patterns, over-broad tool use, insecure defaults) and MUST receive security scrutiny proportional to its role and risk.

The contributor MUST:
- Subject AI-generated code to security review proportional to what it touches (authentication, authorization, data handling, external input, command/tool invocation).
- Flag security-relevant AI-generated changes for explicit human security review before merge.

The contributor SHOULD:
- Screen AI-generated output against the OWASP Top 10 for LLM Applications and the OWASP Top 10 for Agentic Applications threat classes.
- Highlight areas of uncertainty so reviewers can focus scrutiny.

> Federal basis: OWASP Top 10 for LLM Applications; OWASP Top 10 for Agentic Applications; NIST SP 800-218A.
>
> **Control Mapping:** SA-11 (Developer Testing), SI-10 (Input Validation), SA-15 (Development Process)

## 9. Licensing & Intellectual Property

Contributions are accepted under this repository's **public-domain / CC0** posture, consistent with the federal default to release custom-developed code as open source and with the recognition that purely AI-generated material may not carry copyright.

The contributor MUST:
- Confirm they have the **right to contribute** the change (no incompatible licenses, no proprietary code copied in, no contractual bar).
- Accept that the contribution is dedicated to the public domain / CC0 as governed by the repository's `LICENSE`.

Purely AI-generated material lacks the human authorship that the U.S. Copyright Office identifies as required for copyright protection (an agency position, cited for context, not legal advice). This reinforces — rather than complicates — the repository's public-domain posture: AI-assisted contributions fit cleanly within a no-rights-reserved model.

> Federal basis: OMB M-16-21 (Federal Source Code Policy — open-source default and public release); U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* (2025) — human-authorship requirement (agency position).
>
> **Control Mapping:** SA-5 (System Documentation), CM-3 (Configuration Change Control), SR-3 (Supply Chain Controls)

## 10. Proportional Scrutiny

Review rigor scales with how much of a contribution was AI-generated and how much risk it carries. This policy is **welcoming to AI assistance but rigorous about its output** — AI assistance is encouraged; low-quality or unexplained AI output is not.

Maintainers MAY:
- Require additional testing, evidence, or explanation in proportion to the share of AI-generated content and its blast radius.
- Request that the contributor walk through any change in their own words.
- **Decline a contribution the submitter cannot explain or defend**, regardless of whether it appears to work.

Contributors SHOULD anticipate heavier review for security-sensitive, cross-module, or large AI-generated changes, and SHOULD pre-empt it by providing clear rationale and verification evidence.

> Federal basis: NIST AI RMF 1.0 MAP / MEASURE / MANAGE (risk-proportionate controls); NIST SP 800-218A.
>
> **Control Mapping:** SA-11 (Developer Testing), SA-15 (Development Process), CA-2 (Control Assessments)

## 11. Federal Basis (Source Map)

Each clause maps to the registry entry in [`data/federal-ai-landscape.yaml`](../data/federal-ai-landscape.yaml) that grounds it. See [`docs/FEDERAL-AI-LANDSCAPE.md`](FEDERAL-AI-LANDSCAPE.md) for the human-readable catalog.

| Clause | Federal / framework source | Registry id |
|--------|----------------------------|-------------|
| §2–§3 Human accountability | OMB, *Accelerating Federal Use of AI through Innovation, Governance, and Public Trust* (M-25-21, 2025, active) — the live OMB AI governance memo (supersedes the rescinded M-24-10) | `m-25-21` |
| §2–§3, §6, §10 Oversight, validity, risk-proportion | NIST *AI Risk Management Framework 1.0* — GOVERN / MAP / MEASURE / MANAGE | `nist-ai-100-1` |
| §4, §6, §8 Transparency, provenance, validity | NIST *AI RMF Generative AI Profile* (AI 600-1) | `nist-ai-600-1` |
| §5, §6, §8 Secure-by-design for AI-generated code | NIST *Secure Software Development Practices for GenAI and Dual-Use Foundation Models* (SP 800-218A) | `nist-sp-800-218a` |
| §9 Open-source / public-release default | OMB *Federal Source Code Policy* (M-16-21, 2016) | `m-16-21` |
| §9 Human-authorship → public-domain posture (agency position) | U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* (2025) | `usco-ai-part2-copyrightability` |
| §5 Provenance — only humans certify | *Developer Certificate of Origin 1.1* (Linux Foundation) | `dco-1-1` |
| §8 Security review of AI output | *OWASP Top 10 for LLM Applications* | `owasp-llm-top-10` |
| §8 Security review of agentic behavior | *OWASP Top 10 for Agentic Applications* | `owasp-agentic-top-10` |
| §7 Data-training / authorization context | OMB *Driving Efficient Acquisition of AI in Government* (M-25-22, 2025) | `m-25-22` |

## 12. How Downstream Repositories Consume This Policy

This is the **canonical** AI-Assisted Contribution Policy. Downstream repositories (the community patterns hub and the quickstart) MUST **reference** this document rather than restate its normative content — duplicated policy text is how repositories drift apart.

Downstream repositories:
- MUST link to this policy as the authoritative source for AI-assisted-contribution expectations.
- MAY add repository-specific *mechanics* (e.g., the `CONTRIBUTING.md` eligibility rules and PR-template attestation in §1) that layer on top of, but do not contradict, this policy.
- MUST NOT weaken any `MUST` / `MUST NOT` clause here; where a downstream repository's posture is stricter, the stricter rule wins.
- SHOULD, on detecting drift between a local copy and this canonical version, open a drift issue rather than maintain a divergent copy.

> **Control Mapping:** SA-5 (System Documentation), CM-3 (Configuration Change Control), PL-4 (Rules of Behavior)
