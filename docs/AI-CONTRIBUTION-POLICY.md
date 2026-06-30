---
title: "AI-Assisted Contribution Policy"
description: "Canonical policy governing AI-assisted contributions — human accountability, disclosure, provenance, verification, data handling, security review, and licensing posture for federal AI-assisted development"
status: canonical
tier: 2
last_updated: "2026-06-30"
owner: "agentic-coding-playbook maintainers (@gsa.gov)"
policy_version: "1.0.0"
nist_controls: ["AU-2", "AU-3", "CA-2", "CM-3", "IA-8", "PL-4", "SA-5", "SA-11", "SA-15", "SC-8", "SC-28", "SI-10", "SI-12", "SR-3"]
frameworks: ["OMB M-25-21", "NIST AI RMF 1.0", "NIST AI 600-1", "NIST SP 800-218A", "OMB M-16-21", "U.S. Copyright Office AI Part 2", "OWASP Top 10 LLM 2025", "OWASP Top 10 Agentic 2026"]
audience: ["developers", "managers", "isso"]
keywords: ["ai-contribution", "human-accountability", "disclosure", "provenance", "CC0", "public-domain", "copyright", "verification", "contribution-policy"]
related_files: ["AGENTS.md", "CONTRIBUTING.md", "docs/AGENT-IDENTITY.md", "docs/FEDERAL-AI-LANDSCAPE.md", "data/federal-ai-landscape.yaml"]
load_priority: "task-context"
review_cycle: "quarterly"
---

<!-- LOAD: on-demand — Load when a task involves contribution policy, AI attribution/disclosure, provenance, or licensing of AI-assisted work. -->

# AI-Assisted Contribution Policy

> **Policy version 1.0.0** · Owner: agentic-coding-playbook maintainers · Review cadence: quarterly (per frontmatter `review_cycle`). Material changes are versioned in §13 and require maintainer review like any other behavioral-contract change.
>
> **Disclaimer:** This policy references federal guidance, statutes, and agency positions (e.g., OMB memoranda, NIST standards, and U.S. Copyright Office reports) for context only. It is **not legal advice** and does not constitute official GSA policy or an authoritative interpretation of any federal requirement. Citations to agency materials describe an **agency operating position**, not a legal determination. Agencies and contributors remain responsible for tailoring these expectations to their own ATO requirements, organizational policy, and risk tolerance.
>
> **Key words:** "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" are used per [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).
>
> **What this policy adds vs. restates.** This document is the single home for the *contribution-specific* expectations on AI-assisted work (accountability, disclosure, provenance, licensing). For the general behavioral rules it depends on — data handling, supply-chain, testing, run-and-verify — it **references** `AGENTS.md` rather than restating them (per §12). Where a clause is mechanically checkable in CI it is tagged **[CI-checkable]**; otherwise it is **[self-attested, review-enforced]** so readers know what is observable versus honor-system.

## 1. Purpose & Scope

This document is the **canonical** policy governing AI-assisted contributions to this repository and to downstream repositories that reference it (the community patterns hub and the quickstart). It defines the **behavioral and accountability expectations** for any contributor who uses an AI coding agent or assistant to help author a contribution.

This policy is **enforced at review time** by maintainers applying these clauses as acceptance criteria, supplemented by the CI checks noted on individual clauses. It is not, by itself, self-executing automation.

**In scope:** human accountability, disclosure, provenance, verification, data handling (by reference), security review, licensing posture, and proportional review rigor for AI-assisted work.

**Out of scope (governed downstream):** contributor *eligibility* (e.g., the federal-employee/contractor `.gov`/`.mil` requirement) and the pull-request-template attestation checkbox live in the downstream `CONTRIBUTING.md` and PR template. **Those downstream rules are binding and may be stricter than this policy** (see §12) — a reader MUST consult the consuming repository's `CONTRIBUTING.md` for the full, binding set of requirements. This document does not define or weaken them.

> **Control Mapping:** PL-4 (Rules of Behavior), SA-5 (System Documentation)

## 2. Core Principle: Human Ownership & Accountability

An AI agent is a tool. The **human contributor is the author of record** and is fully accountable for every AI-assisted contribution they submit — to the same degree as if they had written every line themselves. Federal AI governance places human accountability and meaningful oversight at the center of permissible AI use; this repository adopts that posture without exception.

The submitting human MUST be able to **explain and defend every change** in a contribution. **If a contributor cannot explain a change, they MUST NOT submit it.** "The AI wrote it" is never a sufficient account of a change.

> Federal basis: OMB M-25-21 (human oversight / accountability for AI use); NIST AI RMF 1.0 GOVERN (accountability) and AI 600-1 (Generative AI Profile).
>
> **Control Mapping:** AU-3 (Content of Audit Records — traceability), PL-4 (Rules of Behavior), SA-11 (Developer Testing)

## 3. Human Accountability for AI-Assisted Contributions

**[self-attested, review-enforced]**

The contributor MUST:
- Take full ownership of any AI-assisted change as their own work.
- Be prepared to explain, in their own words, **what** the change does, **why** it is correct, and **how** they verified it.
- Decline to submit — and remove — any AI-suggested change they do not understand well enough to defend in review.

The contributor MUST NOT:
- Submit code, configuration, or documentation whose behavior or rationale they cannot account for.
- Treat AI authorship as a transfer of responsibility; accountability remains with the human.

**How this is checked (so the bar is not arbitrary):** a maintainer MAY ask the contributor one targeted question about any change — what a line does, why an approach was chosen, how an edge case is handled. An inability to answer in the contributor's own words is grounds to decline the change under §10. The test is *the human's* understanding, not whether an agent can re-explain its own output; re-prompting the AI to explain a change does not satisfy this clause.

> Federal basis: OMB M-25-21 (human oversight); NIST AI RMF 1.0 GOVERN.
>
> **Control Mapping:** AU-3 (Content of Audit Records), SA-11 (Developer Testing), PL-4 (Rules of Behavior)

## 4. Disclosure of AI Assistance

**[self-attested, review-enforced]** — disclosure is low-stakes and normalized; this project dogfoods AI agents, so an honest "I used AI for X" is expected and welcome, never penalized.

Contributors SHOULD disclose AI assistance — which tool(s) were used and for what (e.g., "OpenCode used to draft the parser and tests").

- **Pull-request-level disclosure is RECOMMENDED.** A short note in the PR description is the preferred mechanism.
- **Per-commit attribution is OPTIONAL.** A contributor MAY add a commit-level `Co-authored-by:` trailer, but it is not required.

This is consistent with the playbook's existing identity stance (`AGENTS.md` §2): system-level traceability over granular per-commit attribution. Disclosure supports review and audit — it does not diminish the human accountability of §2–§3, and disclosing AI use never counts against a contribution.

> Federal basis: NIST AI RMF 1.0 GOVERN (transparency); NIST AI 600-1.
>
> **Control Mapping:** AU-2 (Audit Events), AU-3 (Content of Audit Records), IA-8 (Identification)

## 5. Provenance and the Right to Contribute

**[self-attested, review-enforced]**

A contribution's provenance — that the contributor has the right to submit it and that it is offered under this repository's license — is a **human** responsibility. An AI agent cannot certify provenance, license compatibility, or the right to contribute, and MUST NOT be represented as having done so.

The contributor MUST:
- Personally certify, by opening the pull request, that they have the right to contribute the change under this repository's `LICENSE` (see §9) — the human, not the agent, is the certifying party.
- Confirm no proprietary, incompatibly-licensed, or contractually-restricted material was introduced via the AI tool (AI assistants can reproduce training data; the contributor is responsible for catching it).

The contributor / agent MUST NOT:
- Present any attestation, sign-off, or license certification as having been made by an AI agent.

> **Note on mechanism:** This repository does **not** currently use a Developer Certificate of Origin (DCO) `Signed-off-by` gate; provenance is certified by the human act of opening the PR under the repository's CC0 `LICENSE`. If a consuming repository adopts DCO, the same principle applies — only a human may sign off (Developer Certificate of Origin 1.1). What the human certifies is **origin and the right to submit** the contribution, not necessarily copyright ownership — much federal-employee work is a U.S. Government work with no copyright to assert (17 U.S.C. §105), yet the origin/right-to-submit certification still applies. This policy does not impose DCO where it is not already in use.
>
> Federal basis: OMB M-16-21 (open-source default); contribution-rights certification as a human act.
>
> **Control Mapping:** AU-3 (Content of Audit Records), SR-3 (Supply Chain Controls), CM-3 (Configuration Change Control)

## 6. Verification Before Submission

**[partially CI-checkable]** — secret scanning, dependency resolution/lockfiles, tests, and linters run in CI; the *judgment* that output is correct and non-fabricated is review-enforced.

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

## 7. Data Handling (AI-Tool-Specific)

**[partially CI-checkable]** — secret scanning (e.g. gitleaks) catches committed secrets; the prohibition on *inputting* sensitive data to an external tool is self-attested.

The general data-protection rules in [`AGENTS.md` §4](../AGENTS.md) apply in full and are **not restated here.** This clause adds the one AI-tool-specific obligation:

The contributor MUST NOT input into an AI tool — for prompting, context, or any other purpose — secrets, credentials, PII, CUI, or non-public government data **unless that specific tool is authorized for that data class** under the relevant system's ATO. An unapproved AI tool is an unapproved destination for data; treat it as exfiltration. When a data classification is uncertain, default to the highest applicable protection level (per `AGENTS.md` §4.2).

> Federal basis: OMB M-25-22 (vendors must not train on non-public government data without consent); `AGENTS.md` §4.
>
> **Control Mapping:** SC-28 (Protection of Information at Rest), SC-8 (Transmission Confidentiality), SI-12 (Information Management)

## 8. Security Review of AI-Generated Output

**[partially CI-checkable]** — SAST/secret/dependency scans run in CI; the proportional human security judgment is review-enforced.

The secure-code-generation and supply-chain rules in [`AGENTS.md` §5 and §7](../AGENTS.md) apply in full and are **not restated here.** This clause adds the AI-specific emphasis: AI-generated code carries characteristic risks (insecure output handling, injection-prone patterns, over-broad tool use, insecure defaults) and MUST receive security scrutiny proportional to its role and risk.

The contributor MUST:
- Flag security-relevant AI-generated changes (auth, authz, data handling, external input, command/tool invocation) for explicit human security review before merge.

The contributor SHOULD:
- Screen AI-generated output against the OWASP Top 10 for LLM Applications and the OWASP Top 10 for Agentic Applications threat classes.

> Federal basis: OWASP Top 10 for LLM Applications; OWASP Top 10 for Agentic Applications; NIST SP 800-218A; `AGENTS.md` §5, §7.
>
> **Control Mapping:** SA-11 (Developer Testing), SI-10 (Input Validation), SA-15 (Development Process)

## 9. Licensing & Intellectual Property

**[self-attested, review-enforced]**

This repository releases its contributions **into the public domain** under the [CC0 1.0 Universal](../LICENSE) dedication, consistent with the federal default to release custom-developed code as open source (OMB M-16-21).

How that applies to AI-assisted work:

- **Public domain by default.** The repository's intent is that everything in it is freely usable by anyone with no rights reserved. CC0 1.0 is the instrument used to achieve that.
- **Human-authored portions** (the parts of a contribution shaped by human creative judgment) carry copyright that vests in the author or the U.S. Government; the contributor dedicates that copyright to the public domain via CC0.
- **Purely AI-generated portions** generally carry **no copyright at all** — the U.S. Copyright Office's operating position is that copyright requires human authorship, so material produced without human creative input is not protectable. For those portions there is no copyright to dedicate; they are already free of copyright. CC0's public-domain *fallback* (its no-rights-asserted terms) still applies, so the practical result is uniform: **no rights reserved over any part of the contribution.**
- **Inherited or reused material** that is owned by a third party (e.g., a snippet, dependency, or asset originating elsewhere) remains under **its own rights holder's license** and is **not** dedicated to the public domain by this repository. The contributor MUST NOT introduce such material unless its license permits the use, MUST retain the original license/attribution where required, and MUST identify it so it is not mistaken for public-domain content.

**Inbound third-party license compatibility.** Because this repository is dedicated to the public domain (CC0), it can only cleanly incorporate third-party material under **permissive, non-copyleft** terms (e.g., MIT, BSD, ISC, Apache-2.0, CC0, or other public-domain-equivalent). The contributor MUST NOT introduce copyleft or share-alike material (e.g., GPL, LGPL, AGPL, CC-BY-SA) that would impose obligations the repository's CC0 dedication cannot satisfy; such material MUST be declined or routed for explicit maintainer approval. Permissively-licensed inbound material retains its own license and attribution (above) and is not re-dedicated to the public domain.

The contributor MUST:
- Confirm they have the **right to contribute** the change (no incompatible licenses, no proprietary code copied in, no contractual bar).
- Preserve and disclose the licensing of any inherited/reused third-party material, which retains its original rights.
- Accept that all other parts of the contribution are released with no rights reserved under the repository's CC0 `LICENSE`.

> This framing avoids asserting copyright over material that has none: human-authored parts are CC0-dedicated; AI-generated parts are uncopyrightable (CC0's public-domain terms still yield "no rights reserved"); third-party material keeps its own license. The net effect — free reuse of this repository's own content — is consistent and coherent.
>
> Federal basis: OMB M-16-21 (Federal Source Code Policy — open-source default and public release); U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 2: Copyrightability* (2025) — human-authorship requirement (agency operating position, not legal advice).
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
| §5 Provenance / human certification (informative; DCO not in use here) | *Developer Certificate of Origin 1.1* (Linux Foundation) | `dco-1-1` |
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

## 13. Policy Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-30 | Initial policy: human accountability, disclosure, human provenance/right-to-contribute (no DCO mandate), verification (anti-hallucination/slopsquatting), AI-tool data handling, security review, CC0/public-domain licensing with third-party-rights carve-out, proportional scrutiny, downstream-consumption rules. |
