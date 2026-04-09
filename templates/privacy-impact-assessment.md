---
title: "Privacy Impact Assessment for AI-Enabled Systems"
description: "PIA template for federal systems using AI components — data flows, privacy risks, mitigations, and compliance sign-off"
status: canonical
tier: 3
last_updated: "2026-03-26"
nist_controls: ["AR-2", "AP-2", "DM-1", "SE-1", "TR-1", "UL-1"]
frameworks: ["Privacy Act of 1974", "E-Government Act of 2002", "OMB Circular A-130", "OMB M-25-21", "OMB M-26-04"]
audience: "isso"
keywords: ["privacy-impact-assessment", "PIA", "PII", "CUI", "AI-data-flows", "Privacy-Act"]
related_files: ["templates/risk-assessment.md", "docs/SECURITY-CONTROLS.md"]
load_priority: "reference-only"
review_cycle: "annually"
---

<!-- LOAD: reference-only — Load only when conducting a privacy impact assessment or preparing ATO documentation for AI-enabled systems. -->

# Privacy Impact Assessment for AI-Enabled Systems

<!--
  INSTRUCTIONS:
  1. Complete this PIA before deploying any system that uses AI components and processes PII or CUI
  2. Review with your Privacy Officer and ISSO
  3. Update when AI components, data flows, or system purpose change materially
  4. Retain completed PIAs as part of your ATO documentation package

  Based on: Agentic Coding Playbook v0.4.0
  Aligned with: Privacy Act of 1974, E-Government Act of 2002 (Section 208), OMB Circular A-130
-->

---

## Section 1: System Description

| Field | Value |
|-------|-------|
| **System Name** | |
| **System Owner** | |
| **Privacy Officer** | |
| **ISSO** | |
| **System Purpose** | |
| **Assessment Date** | |
| **Assessor Name/Title** | |
| **FIPS Impact Level** | [ ] Low [ ] Moderate [ ] High |

### AI Components

| Component | Model/Product | Vendor | Purpose |
|-----------|--------------|--------|---------|
| | | | |
| | | | |

---

## Section 2: Data Collection

<!-- Privacy Act: (e)(1) — Maintain only relevant and necessary records -->

### 2.1 PII and CUI Inventory

| Data Element | Collected? | From Whom | Legal Authority | Retention Period |
|-------------|-----------|-----------|-----------------|-----------------|
| Full name | [ ] Yes [ ] No | | | |
| Email address | [ ] Yes [ ] No | | | |
| Social Security Number | [ ] Yes [ ] No | | | |
| Date of birth | [ ] Yes [ ] No | | | |
| Home address | [ ] Yes [ ] No | | | |
| Phone number | [ ] Yes [ ] No | | | |
| Biometric data | [ ] Yes [ ] No | | | |
| Financial records | [ ] Yes [ ] No | | | |
| Health information (PHI) | [ ] Yes [ ] No | | | |
| Employment records | [ ] Yes [ ] No | | | |
| CUI (specify category) | [ ] Yes [ ] No | | | |

### 2.2 Collection Notice

- [ ] Privacy Act Statement provided at point of collection
- [ ] System of Records Notice (SORN) published in Federal Register
- [ ] Individuals informed of purpose and authority for collection

---

## Section 3: AI-Specific Data Flows

<!-- M-26-04: AI system data handling transparency -->

### 3.1 Data Sent to AI Models

| Data Type | Sent to Model? | Model/Service | Justification |
|-----------|---------------|---------------|---------------|
| PII (direct identifiers) | [ ] Yes [ ] No | | |
| PII (indirect/derived) | [ ] Yes [ ] No | | |
| CUI | [ ] Yes [ ] No | | |
| Source code | [ ] Yes [ ] No | | |
| User-generated content | [ ] Yes [ ] No | | |
| System logs | [ ] Yes [ ] No | | |

### 3.2 Data Returned by AI Models

| Output Type | Contains PII? | Contains CUI? | Stored? | Retention |
|------------|--------------|---------------|---------|-----------|
| Generated text/code | [ ] Yes [ ] No | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Classifications/scores | [ ] Yes [ ] No | [ ] Yes [ ] No | [ ] Yes [ ] No | |
| Recommendations | [ ] Yes [ ] No | [ ] Yes [ ] No | [ ] Yes [ ] No | |

### 3.3 Training Data Usage

| Question | Answer |
|----------|--------|
| Is system data used to train or fine-tune AI models? | [ ] Yes [ ] No [ ] Unknown |
| Has training data opt-out been confirmed with vendor? | [ ] Yes [ ] No [ ] N/A |
| Does the vendor retain prompts or outputs? | [ ] Yes [ ] No [ ] Unknown |
| Vendor data retention period | |
| Data residency (where is data processed?) | [ ] US only [ ] International [ ] Unknown |

---

## Section 4: Privacy Risks

Rate each risk for your specific deployment. **Likelihood**: 1 (Rare) to 5 (Almost Certain). **Impact**: 1 (Negligible) to 5 (Severe). **Risk = Likelihood x Impact**.

| # | Risk | Description | Likelihood (1-5) | Impact (1-5) | Risk Score |
|---|------|-------------|-------------------|--------------|------------|
| PR1 | **Data exposure to AI vendor** | PII or CUI transmitted to third-party AI model provider without adequate safeguards | | | |
| PR2 | **Inference attacks** | AI model outputs reveal PII not explicitly provided — inferring identity, health status, or sensitive attributes from indirect data | | | |
| PR3 | **Model memorization** | AI model memorizes and later reproduces PII from training data or prompt history in responses to other users | | | |
| PR4 | **Re-identification** | Anonymized or de-identified data is re-identified through AI-assisted correlation with external datasets | | | |
| PR5 | **Unauthorized collection** | AI system collects or processes PII beyond stated purpose — scope creep in data usage or retention | | | |

---

## Section 5: Mitigations

For each risk rated Medium (6-11) or above, document control measures.

| Risk # | Mitigation | Implementation Status | Responsible Party |
|--------|-----------|----------------------|-------------------|
| PR1 | | [ ] Implemented [ ] Planned [ ] N/A | |
| PR2 | | [ ] Implemented [ ] Planned [ ] N/A | |
| PR3 | | [ ] Implemented [ ] Planned [ ] N/A | |
| PR4 | | [ ] Implemented [ ] Planned [ ] N/A | |
| PR5 | | [ ] Implemented [ ] Planned [ ] N/A | |

### Common AI Privacy Controls

- [ ] PII stripped or pseudonymized before sending to AI models
- [ ] AI vendor contract includes data processing agreement (DPA) with FedRAMP-equivalent protections
- [ ] Training data opt-out confirmed in writing with vendor
- [ ] AI model outputs reviewed for PII leakage before storage or display
- [ ] Data minimization applied — only necessary data sent to AI components
- [ ] Encryption in transit (TLS 1.2+) for all AI API communications
- [ ] Access logging enabled for all AI model interactions
- [ ] Retention limits enforced on AI-generated outputs containing PII

---

## Section 6: Compliance

### 6.1 Legal and Policy References

| Requirement | Applicable? | Compliance Status | Notes |
|------------|------------|-------------------|-------|
| **Privacy Act of 1974** (5 U.S.C. 552a) — Governs collection, maintenance, use, and dissemination of PII in federal systems of records | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |
| **E-Government Act of 2002** (Section 208) — Requires PIAs for IT systems collecting PII | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |
| **OMB Circular A-130** (Managing Information as a Strategic Resource) — Privacy and information security requirements for federal information systems | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |
| **OMB M-25-21** — Pre-deployment testing requirements for AI systems in federal environments | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |
| **OMB M-26-04** — AI transparency, model cards, and data handling requirements | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |
| **FISMA** — Federal Information Security Modernization Act privacy overlay | [ ] Yes [ ] No | [ ] Compliant [ ] Partial [ ] Non-compliant | |

### 6.2 SORN and Privacy Notice

| Question | Answer |
|----------|--------|
| Does a System of Records Notice (SORN) cover this system? | [ ] Yes [ ] No [ ] In progress |
| SORN citation (if applicable) | |
| Is the Privacy Act Statement displayed at point of collection? | [ ] Yes [ ] No [ ] N/A |
| Is a privacy policy published and accessible to users? | [ ] Yes [ ] No |

---

## Section 7: Sign-Off

### Privacy Determination

Based on this assessment, the privacy posture of [System Name] with AI components is:

[ ] **Acceptable** — Privacy risks are adequately mitigated; proceed with deployment
[ ] **Conditionally Acceptable** — Proceed after completing mitigations marked as "Planned" above
[ ] **Not Acceptable** — Do not deploy until identified privacy risks are mitigated

### Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **System Owner** | | | |
| **Privacy Officer** | | | |
| **ISSO** | | | |
| **Authorizing Official** (if required) | | | |

---

## Appendix: Revision History

| Date | Version | Assessor | Changes |
|------|---------|----------|---------|
| | 1.0 | | Initial assessment |
