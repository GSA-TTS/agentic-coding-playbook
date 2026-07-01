---
title: "Federal AI Landscape"
description: "Canonical catalog of federal AI guidance, executive orders, standards, and legislation relevant to AI-assisted software development"
status: canonical
tier: 2
last_updated: "2026-06-29"
load_priority: on-demand
audience: ["developers", "isso", "managers", "agents"]
keywords: ["federal", "AI", "guidance", "executive order", "NIST", "OMB", "OWASP", "compliance", "legislation"]
last_reviewed: "2026-06-29"
---

# Federal AI Landscape

Canonical reference for all federal AI guidance relevant to AI-assisted software development. Each entry includes current status, relevance to this playbook, and official source URL.

> **Last reviewed:** 2026-06-29. Federal AI policy is evolving rapidly. Verify status before citing in compliance documents.
>
> **Machine-readable data:** [`data/federal-ai-landscape.yaml`](../data/federal-ai-landscape.yaml) — structured registry with IDs, dates, statuses, cross-references, and compliance deadlines. Use the YAML for programmatic access; this document is the human-readable companion.

## Status Summary

| Category | Active | Revoked/Rescinded | Draft |
|---|---|---|---|
| Executive Orders | 5 | 1 | 0 |
| OMB Memoranda | 5 | 2 | 0 |
| NIST Standards | 8 | 0 | 3 |
| Federal Legislation | 4 | 0 | 0 |
| Agency Strategies | 4 | 0 | 0 |
| Agency Reports | 2 | 0 | 0 |
| Industry Standards | 6 | 0 | 0 |
| White House Plans | 2 | 0 | 0 |
| **Total** | **36** | **3** | **3** |

> Counts reflect `data/federal-ai-landscape.yaml` (42 entries total; "final" standards counted as Active). `status: final` and `status: active` both denote in-effect references.

---

## Executive Orders

### Active

**EO 14179 — Removing Barriers to American Leadership in Artificial Intelligence**
- **Signed:** January 23, 2025 | **President:** Trump | **Status:** Active
- Revoked EO 14110. Directs policy favoring AI innovation over regulation. Removes safety reporting requirements for foundation model developers. Tasks agencies with removing barriers to AI development.
- **Relevance:** Removed mandatory safety testing and federal procurement guardrails from EO 14110. Agents operating under this playbook should note the shift from prescriptive compliance to voluntary best practices.
- **Source:** [whitehouse.gov](https://www.whitehouse.gov/presidential-actions/removing-barriers-to-american-leadership-in-artificial-intelligence/)

**EO — Ensuring a National Policy Framework for Artificial Intelligence**
- **Signed:** December 11, 2025 | **President:** Trump | **Status:** Active
- Establishes minimally burdensome national AI framework. Creates DOJ AI Litigation Task Force to challenge state AI laws that burden interstate commerce. Asserts federal primacy over AI regulation.
- **Relevance:** Signals federal preemption of state AI laws. Agencies deploying AI should track which state requirements may be challenged.
- **Source:** [whitehouse.gov](https://www.whitehouse.gov/presidential-actions/2025/12/eliminating-state-law-obstruction-of-national-artificial-intelligence-policy/)

**EO 14319 — Preventing Woke AI in the Federal Government**
- **Signed:** July 23, 2025 | **President:** Trump | **Status:** Active
- Requires federal LLM procurements comply with two "Unbiased AI Principles": Truth-Seeking (factual accuracy, acknowledge uncertainty) and Ideological Neutrality (nonpartisan outputs). Implemented by OMB M-26-04.
- **Relevance:** Directly affects any federal project procuring LLM capabilities. Vendors must provide model cards and acceptable use policies.
- **Source:** [whitehouse.gov](https://www.whitehouse.gov/presidential-actions/)

**EO 13960 — Promoting the Use of Trustworthy AI in the Federal Government**
- **Signed:** December 3, 2020 | **President:** Trump (1st term) | **Status:** Active
- Establishes principles for federal AI use: lawful, purposeful, accurate, safe, transparent, accountable. Requires agency AI use-case inventories.
- **Relevance:** Foundation for trustworthy AI principles still in effect. Agency AI inventories remain required.
- **Source:** [Federal Register](https://www.federalregister.gov/d/2020-27065)

**EO 13859 — Maintaining American Leadership in Artificial Intelligence**
- **Signed:** February 11, 2019 | **President:** Trump (1st term) | **Status:** Active
- Launched the American AI Initiative. Directs federal investment in AI R&D, data access for researchers, workforce development.
- **Relevance:** Established the policy foundation for federal AI investment. Still active.
- **Source:** [Federal Register](https://www.federalregister.gov/d/2019-02544)

### Revoked

**EO 14110 — Safe, Secure, and Trustworthy Development and Use of AI** *(Revoked)*
- **Signed:** October 30, 2023 | **President:** Biden | **Status:** Revoked by EO 14179 (Jan 2025)
- Required AI safety testing/red-teaming for dual-use foundation models, NIST AI safety standards, watermarking, federal agency AI governance, OMB procurement guidance. The most extensive federal AI executive order at the time of signing.
- **Relevance:** Historical reference. Many of its provisions (Chief AI Officers, AI inventories, risk management) were preserved in successor policies M-25-21 and M-25-22 despite the EO's revocation.
- **Source:** [Federal Register](https://www.federalregister.gov/d/2023-24283)

---

## OMB Memoranda

### Active

**M-25-21 — Accelerating Federal Use of AI through Innovation, Governance, and Public Trust**
- **Issued:** April 15, 2025 | **Status:** Active (replaced M-24-10)
- Requires Chief AI Officer appointment within 60 days. Consolidates "rights-impacting" and "safety-impacting" into single "high-impact AI" category. Requires pre-deployment testing, impact assessments, continuous monitoring. Compliance deadline: April 15, 2026.
- **Relevance:** Primary governance framework for federal AI use. Defines "high-impact AI" classification that drives risk management requirements.
- **Source:** [whitehouse.gov (PDF)](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf)

**M-25-22 — Driving Efficient Acquisition of AI in Government**
- **Issued:** April 15, 2025 | **Status:** Active (replaced M-24-18)
- Applies to solicitations after October 1, 2025. Vendors prohibited from training on non-public government data without consent. Maximize U.S.-made AI. GSA to develop procurement repository.
- **Relevance:** Directly affects AI tool procurement. Data training restrictions are relevant to any AI agent processing government data.
- **Source:** [whitehouse.gov (PDF)](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-22-Driving-Efficient-Acquisition-of-Artificial-Intelligence-in-Government.pdf)

**M-26-04 — Increasing Public Trust in AI Through Unbiased AI Principles**
- **Issued:** December 11, 2025 | **Status:** Active (implements EO 14319)
- Two enforceable procurement principles: Truth-Seeking and Ideological Neutrality. Agencies update procurement policies by March 11, 2026. Requires model cards, acceptable use policies, feedback mechanisms from vendors.
- **Relevance:** All new LLM procurements must comply. Vendors must demonstrate factual accuracy and nonpartisan outputs.
- **Source:** [whitehouse.gov (PDF)](https://www.whitehouse.gov/wp-content/uploads/2025/12/M-26-04-Increasing-Public-Trust-in-Artificial-Intelligence-Through-Unbiased-AI-Principles-1.pdf)

**M-16-21 — Federal Source Code Policy**
- **Issued:** August 8, 2016 | **Status:** Active
- Establishes the federal default to release custom-developed code as open source and to share reusable code across government. Predates the AI memos but remains the policy basis for publishing federal repositories publicly.
- **Relevance:** Basis for publishing these GSA-TTS repositories in the open and for the CC0 / public-domain dedication posture used by the community-hub repo. Underpins the AI-assisted contribution policy's licensing terms.
- **Source:** [obamawhitehouse.archives.gov (PDF)](https://obamawhitehouse.archives.gov/sites/default/files/omb/memoranda/2016/m_16_21.pdf)

### Rescinded

**M-24-10 — Advancing Governance, Innovation, and Risk Management for Agency Use of AI** *(Rescinded)*
- **Issued:** March 28, 2024 | **Status:** Rescinded (replaced by M-25-21, April 15, 2025)
- **Source:** [whitehouse.gov (PDF)](https://www.whitehouse.gov/wp-content/uploads/2024/03/M-24-10-Advancing-Governance-Innovation-and-Risk-Management-for-Agency-Use-of-Artificial-Intelligence.pdf)

**M-24-18 — Advancing the Responsible Acquisition of AI in Government** *(Rescinded)*
- **Issued:** October 3, 2024 | **Status:** Rescinded (replaced by M-25-22, April 15, 2025)
- **Source:** [whitehouse.gov (PDF)](https://www.whitehouse.gov/wp-content/uploads/2024/10/M-24-18-AI-Acquisition-Memorandum.pdf)

---

## NIST Standards

### Final

**AI 100-1 — AI Risk Management Framework (AI RMF 1.0)**
- **Published:** January 26, 2023 | **Status:** Final
- Core voluntary framework with Govern/Map/Measure/Manage functions for AI risk. Foundation document referenced by all federal AI policies.
- **Relevance:** This playbook's risk assessment phase maps directly to AI RMF functions.
- **Source:** [nist.gov](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)

**AI 600-1 — Generative AI Profile (AI RMF Companion)**
- **Published:** July 26, 2024 | **Status:** Final
- 13 GenAI-specific risks with 400+ mitigation actions. Covers governance, content provenance, pre-deployment testing, incident disclosure.
- **Relevance:** Directly applicable to AI coding agent deployment and governance.
- **Source:** [nist.gov](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

**AI 100-2 E2025 — Adversarial Machine Learning: Taxonomy and Terminology**
- **Published:** March 24, 2025 | **Status:** Final (supersedes E2023 edition)
- Taxonomy of AML attacks (evasion, poisoning, privacy, misuse) for predictive and generative AI.
- **Relevance:** Informs threat modeling for AI agents. Relevant to prompt injection and adversarial input defense.
- **Source:** [csrc.nist.gov](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)

**AI 100-4 — Reducing Risks Posed by Synthetic Content**
- **Published:** November 20, 2024 (updated Feb 2026) | **Status:** Final
- Digital watermarking, metadata recording, content provenance for AI-generated output.
- **Relevance:** Relevant to AI agent output attribution and content provenance.
- **Source:** [nist.gov](https://www.nist.gov/publications/reducing-risks-posed-synthetic-content-overview-technical-approaches-digital-content)

**AI 100-5 E2025 — Plan for Global Engagement on AI Standards**
- **Published:** July 26, 2024 (updated 2025) | **Status:** Final
- International AI standardization strategy and coordination.
- **Relevance:** Background context for international AI compliance alignment.
- **Source:** [nist.gov](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-5e2025.pdf)

**SP 800-218A — Secure Software Development Practices for Generative AI and Dual-Use Foundation Models**
- **Published:** July 2024 | **Status:** Final
- Extends SSDF v1.1 (SP 800-218) with AI-specific secure development practices across the full SDLC.
- **Relevance:** Most directly applicable NIST publication for AI coding agents. Covers the entire lifecycle for AI system integrators.
- **Source:** [csrc.nist.gov](https://csrc.nist.gov/pubs/sp/800/218/a/final)

### Draft

**AI 800-1 — Managing Misuse Risk for Dual-Use Foundation Models**
- **Published:** January 2025 (2nd public draft) | **Status:** Draft
- Voluntary practices for misuse risk across AI lifecycle. Appendices on cyber and bio misuse.
- **Relevance:** Informs responsible deployment of coding agents and misuse prevention.
- **Source:** [nist.gov (PDF)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-1.ipd2.pdf)

**IR 8596 — Cybersecurity Framework Profile for AI (Cyber AI Profile)**
- **Published:** December 16, 2025 (initial preliminary draft) | **Status:** Draft (comment period closed Feb 28, 2026)
- Maps CSF 2.0 to AI adoption security. Bridges cybersecurity and AI risk frameworks.
- **Relevance:** Will provide implementation-level guidance for securing AI systems when finalized.
- **Source:** [csrc.nist.gov](https://csrc.nist.gov/pubs/ir/8596/iprd)

---

## Federal Legislation

**National Artificial Intelligence Initiative Act of 2020**
- **Enacted:** January 1, 2021 | **Public Law:** 116-283 (div. E, title LI)
- Established National AI Initiative Office, interagency committee, AI research institutes. Codified in 15 U.S.C. Chapter 119.
- **Relevance:** Establishes the federal AI research and coordination infrastructure.
- **Source:** [congress.gov](https://www.congress.gov/bill/116th-congress/house-bill/6216)

**AI in Government Act of 2020**
- **Enacted:** December 27, 2020 | **Public Law:** 116-260
- Established AI Center of Excellence at GSA. Required OPM to identify AI competency gaps in federal workforce.
- **Relevance:** Created GSA's AI advisory capacity used by federal agencies.
- **Source:** [congress.gov](https://www.congress.gov/bill/116th-congress/house-bill/2575)

**Advancing American AI Act**
- **Enacted:** December 23, 2022 | **Public Law:** 117-263 (div. G, title LXXII, § 7225)
- Directs federal agencies to acquire and use AI responsibly. Requires AI governance frameworks, risk management, and transparency for government AI systems.
- **Relevance:** Legal mandate for responsible AI adoption across federal agencies.
- **Source:** [congress.gov](https://www.congress.gov/bill/117th-congress/senate-bill/1353)

**TAKE IT DOWN Act**
- **Enacted:** May 19, 2025 | **Public Law:** 119-XX
- Criminalizes non-consensual intimate imagery including AI-generated deepfakes. Requires platforms to establish notice-and-takedown processes.
- **Relevance:** First federal law limiting harmful AI use. Sets precedent for AI content liability. Platform compliance deadline: May 19, 2026.
- **Source:** [congress.gov](https://www.congress.gov/bill/119th-congress/senate-bill/146)

---

## Agency Strategies and Guidance

**CISA Roadmap for Artificial Intelligence (2023-2024)**
- **Issued by:** CISA | **Published:** November 2023 | **Status:** Active
- Whole-of-agency plan for responsible AI use in cybersecurity. Promotes Secure by Design principles for AI systems. Annual AI risk assessments for critical infrastructure sectors.
- **Relevance:** Defines cybersecurity expectations for AI-enabled federal systems.
- **Source:** [cisa.gov](https://www.cisa.gov/resources-tools/resources/roadmap-ai)

**DHS Artificial Intelligence Roadmap 2024**
- **Issued by:** DHS | **Published:** March 2024 | **Status:** Active
- Most detailed agency AI plan. Three lines of effort: responsible AI use, AI for homeland security, AI risk in critical infrastructure.
- **Relevance:** Model for agency-level AI governance planning.
- **Source:** [dhs.gov](https://www.dhs.gov/publication/ai-roadmap)

**DoD Responsible AI Strategy and Implementation Pathway**
- **Issued by:** DoD/CDAO | **Published:** June 2022 (updated October 2024) | **Status:** Active
- RAI principles: responsible, equitable, traceable, reliable, governable. CDAO chartering directive and implementation instruction.
- **Relevance:** Relevant for defense-adjacent projects. RAI principles align with this playbook's AGENTS.md behavioral contracts.
- **Source:** [defense.gov (PDF)](https://media.defense.gov/2024/Oct/26/2003571790/-1/-1/0/2024-06-RAI-STRATEGYIMPLEMENTATION-PATHWAY.PDF)

**National Security Memorandum on AI (NSM-25)**
- **Issued by:** White House/NSC | **Published:** October 24, 2024 | **Status:** Active (Biden-era, not yet revoked)
- First-ever NSM on AI. Directs government to lead safe AI development, harness AI for national security, advance international AI governance. Companion Framework for AI Governance and Risk Management in National Security.
- **Relevance:** Sets national security AI requirements that may apply to defense and intelligence-adjacent projects.
- **Source:** [whitehouse.gov (archived)](https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/2024/10/24/fact-sheet-biden-harris-administration-outlines-coordinated-approach-to-harness-power-of-ai-for-u-s-national-security/)

---

## Agency Reports

Reports and accountability frameworks issued by federal agencies. These state agency
positions and analysis; they are authoritative as the issuing agency's view but are not
themselves binding law. Provided for context — not legal advice.

**GAO AI Accountability Framework**
- **Issued by:** GAO | **Published:** June 2021 (GAO-21-519SP) | **Status:** Active
- Four pillars: governance, data, performance, monitoring. Used for federal AI audits. 35 recommendations to 19 agencies.
- **Relevance:** Audit framework. Projects may be evaluated against these pillars.
- **Source:** [gao.gov](https://www.gao.gov/products/gao-21-519sp)

**Copyright and Artificial Intelligence, Part 2: Copyrightability**
- **Issued by:** U.S. Copyright Office | **Published:** January 29, 2025 | **Status:** Active
- The Office's position that copyright protection requires human authorship, and that purely AI-generated material is not copyrightable; human creative contribution determines protectability.
- **Relevance:** Informs the public-domain / CC0 posture for AI-assisted contributions and the licensing terms in the AI-assisted contribution policy. Agency position for context, not legal advice.
- **Source:** [copyright.gov (PDF)](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)

---

## White House Plans

**AI Action Plan — Winning the Race: America's AI Action Plan**
- **Issued by:** OSTP | **Published:** July 23, 2025 | **Status:** Active
- 90 federal policy positions across three pillars: Accelerating Innovation, Building American AI Infrastructure, Leading in International Diplomacy and Security. Cross-cutting priorities: worker protection, trustworthy/unbiased AI, safeguarding against misuse.
- **Relevance:** Sets the strategic direction for all federal AI activity under current administration.
- **Source:** [whitehouse.gov](https://www.whitehouse.gov/ostp/)

---

## Industry Standards

These complement federal guidance and are referenced throughout this playbook.

**OWASP Top 10 for LLM Applications (2025)**
- **Organization:** OWASP Foundation | **Version:** 2.0 (2025) | **Status:** Released
- Key LLM risks: prompt injection, insecure output handling, supply chain vulnerabilities, sensitive information disclosure.
- **Relevance:** Primary security checklist for LLM-powered features in federal applications.
- **Source:** [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

**OWASP Top 10 for Agentic Applications (2026)**
- **Organization:** OWASP Foundation | **Version:** 1.0 (December 2025) | **Status:** Released
- Covers agent goal hijacking, tool misuse, identity/privilege abuse, cascading failures. Introduces "least agency" principle.
- **Relevance:** Directly applicable to this playbook's agent behavioral contracts (AGENTS.md). Defines the threat model for multi-agent systems.
- **Source:** [genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

**MITRE ATLAS (Adversarial Threat Landscape for AI Systems)**
- **Organization:** MITRE Corporation | **Version:** Continuously updated | **Status:** Active
- ATT&CK-aligned threat taxonomy for AI/ML systems. Used by DoD and federal agencies for AI threat modeling.
- **Relevance:** Threat modeling reference for AI security assessments.
- **Source:** [atlas.mitre.org](https://atlas.mitre.org/)

**ISO/IEC 42001:2023 — AI Management System**
- **Organization:** ISO/IEC JTC 1/SC 42 | **Version:** 2023 (1st edition) | **Status:** Published
- Certifiable AI management system standard. Covers AI governance, risk assessment, and continuous improvement.
- **Relevance:** International compliance reference. May be required for projects with international partners.
- **Source:** [iso.org](https://www.iso.org/standard/81230.html)

**NIST SP 800-218 — Secure Software Development Framework (SSDF) v1.1**
- **Organization:** NIST | **Version:** 1.1 (February 2022) | **Status:** Final
- Baseline secure development practices mandated by EO 14028 for all federal software. (Categorized as a NIST standard in the registry; listed here for proximity to the supply-chain references it underpins.)
- **Relevance:** Foundation for CODING_PRACTICES.md. SP 800-218A extends this for AI-specific practices.
- **Source:** [csrc.nist.gov](https://csrc.nist.gov/publications/detail/sp/800-218/final)

**SLSA (Supply-chain Levels for Software Artifacts)**
- **Organization:** OpenSSF / Google | **Version:** 1.0 (2023) | **Status:** Active
- Build provenance, source integrity, and dependency verification framework.
- **Relevance:** Model provenance and training data integrity for AI supply chain security.
- **Source:** [slsa.dev](https://slsa.dev/)

**Developer Certificate of Origin (DCO) 1.1**
- **Organization:** Linux Foundation | **Version:** 1.1 (2004) | **Status:** Active
- Lightweight per-commit provenance attestation — the `Signed-off-by` sign-off by which a contributor certifies they have the right to submit the contribution.
- **Relevance:** Basis for requiring that a human (not an agent) certifies the origin and contribution rights of AI-assisted contributions. Used by the AI-assisted contribution policy.
- **Source:** [developercertificate.org](https://developercertificate.org/)

---

## Playbook Phase Mapping

| Phase | Primary References |
|---|---|
| **Phase 0: Project Plan** | M-25-21 (high-impact AI classification), EO 13960 (AI principles) |
| **Phase 0.5: Environment Doctor** | M-25-22 (procurement), M-26-04 (LLM procurement principles) |
| **Phase 1: Repo Setup** | SP 800-218 (SSDF), SLSA (supply chain) |
| **Phase 2: Agent Config** | OWASP Agentic 2026, AI RMF 1.0, AI 600-1 (GenAI profile) |
| **Phase 3: Write Code** | SP 800-218A (AI SDLC), OWASP LLM 2025, AI 100-2 (adversarial ML) |
| **Phase 4: Document Decisions** | GAO AI Accountability Framework (governance pillar) |
| **Phase 5: Assess Risk** | AI RMF 1.0 (Measure/Manage), AI 600-1, IR 8596 (Cyber AI Profile) |
| **Phase 6: Pre-Deploy Check** | CISA Secure by Design, NIST SP 800-53 |
| **Phase 7: Deploy** | FedRAMP, M-25-22 (acquisition requirements) |

---

## Maintenance

This document should be reviewed quarterly. Federal AI policy is changing rapidly — key dates to watch:

- **April 15, 2026:** M-25-21 compliance deadline for federal agencies
- **October 1, 2025:** M-25-22 applies to new solicitations
- **March 11, 2026:** M-26-04 procurement policy updates due
- **May 19, 2026:** TAKE IT DOWN Act platform compliance deadline
- **TBD 2026:** NIST IR 8596 (Cyber AI Profile) finalization expected
- **TBD 2026:** NIST AI 800-1 finalization expected
