---
name: federal-risk-assessment
title: "Federal Risk Assessment"
description: "Walk through the AI agent risk assessment worksheet interactively, helping users complete each section with context-appropriate guidance."
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["risk", "ATO", "threat", "vulnerability", "risk assessment"]
dependencies: []
---

# Federal Risk Assessment

This skill walks users through the risk assessment template from
`templates/risk-assessment.md` interactively, helping them complete each
section with context-appropriate guidance.

## When to Use

- Preparing for Authority to Operate (ATO) review
- Evaluating risk before deploying an AI coding agent
- Updating a risk assessment after system or agent changes
- When an ISSO asks for an AI agent risk assessment

## How It Works

Read `templates/risk-assessment.md` first to discover the current worksheet structure
(sections, capabilities, data types, threats, control areas). Then guide the user
through each section, explain what's needed, ask questions, and fill in the template.

## Assessment Procedure

### Section 1: System Identification

Ask the user for basic system information:

> "Let's start with system identification. I need the following:
> 1. System name
> 2. System owner (name, title)
> 3. ISSO (name, title)
> 4. FIPS impact level (Low / Moderate / High)
> 5. ATO status (Active / In process / Pre-ATO)
> 6. Today's date as the assessment date
> 7. Your name and title as assessor
> 8. When should this be reviewed next? (Default: 1 year from now)"

Fill in the System Identification table.

### Section 2: AI Agent Identification

Ask about the AI agent being assessed:

> "Now let's identify the AI agent:
> 1. Agent name and product (e.g., GitHub Copilot, Cursor, Codex)
> 2. Agent version
> 3. Agent vendor (e.g., Anthropic, GitHub/Microsoft)
> 4. Deployment model — Local (runs on dev machine), Cloud SaaS, or Self-hosted?
> 5. FedRAMP status — Authorized, In process, Not applicable, Unknown?
> 6. Data residency — US only, International, Unknown?
> 7. Training data opt-out — Confirmed, Not available, Unknown?"

Then walk through the capabilities checklist:

> "Which of these capabilities will the agent use in this project? (Yes/No for each)"

Present the capabilities from `templates/risk-assessment.md` Section 2
(Agent Capabilities Inventory). Read the template to discover the current list.
For each capability, ask Yes/No.

### Section 3: Data Classification

#### 3.1 Data Types

Present the data types table and ask for each:

> "For each data type, tell me if it's present in the system, its classification,
> and whether the agent needs access to it."

Walk through the data types listed in `templates/risk-assessment.md` Section 3
(Data Classification). Read the template to discover the current list.

#### 3.2 Data Flow

For each data destination in `templates/risk-assessment.md` Section 3.2
(Data Flow), ask if it's authorized and encrypted.

### Section 4: Threat Analysis

This is the most important section. Use the pre-filled threat catalog
from [references/THREAT_CATALOG.md](references/THREAT_CATALOG.md) to help
users understand each threat.

For each threat in [references/THREAT_CATALOG.md](references/THREAT_CATALOG.md), explain the threat using the catalog entry, then ask:

> "For **T[N]: [Threat Name]** — [one-sentence description from catalog]
>
> On a scale of 1-5:
> - **Likelihood** (1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain): How likely is this in your environment?
> - **Impact** (1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Severe): If it happened, how bad would it be?
>
> What existing mitigations do you have? (e.g., pre-commit hooks, code review, branch protection)"

Calculate Risk = Likelihood x Impact for each threat.

After completing all threats, summarize with the risk tolerance table:
- Critical (20-25): MUST mitigate before deployment
- High (12-19): MUST mitigate within 30 days
- Medium (6-11): SHOULD mitigate
- Low (1-5): MAY accept with documentation

### Section 5: Control Assessment

Walk through the control areas listed in `templates/risk-assessment.md` Section 5
(Control Implementation Status). Read the template to discover the current list.

> "For each control area, what's the current implementation status?"

Present each control area from the template and ask: Implemented / Partial / Not implemented.

If "Partial" or "Not implemented", ask what's missing and note it.

### Section 6: Risk Treatment Plan

For each risk rated Medium (6+) or above in Section 4, create a treatment plan:

> "Risk T[N] scored [score] ([level]). How would you like to treat it?
> - **Mitigate**: Reduce likelihood or impact with additional controls
> - **Transfer**: Shift risk to another party (e.g., vendor SLA)
> - **Accept**: Document and accept the residual risk
> - **Avoid**: Eliminate the risk by not using the capability"

For "Mitigate", ask:
- What controls will be implemented?
- Who is responsible?
- Target completion date?
- How will you verify the control works?

### Section 7: Acceptance and Sign-Off

Summarize the assessment:

> "Based on this assessment:
> - [X] risks scored Critical or High
> - [X] risks scored Medium
> - [X] risks scored Low
> - [X] of [N] control areas fully implemented
>
> The recommended risk acceptance is: [Acceptable / Conditionally Acceptable / Not Acceptable]
>
> Would you like to adjust anything before finalizing?"

Present the completed worksheet with all sections filled in.

**Remind the user:** "This is a draft assessment. It must be reviewed and
signed by the System Owner and ISSO before it becomes part of the ATO documentation."

## Important Notes

- This skill is **read-only** — it produces a document but does not modify the system.
- The completed assessment is a **draft** requiring human review and sign-off.
- Risk scores are based on the user's input — the agent does not override or second-guess ratings.
- Threat descriptions are pre-filled from OWASP and NIST sources. See `references/THREAT_CATALOG.md`.
- The full template is at `templates/risk-assessment.md`. This skill makes it interactive, it does not change the template structure.
- **Policy reference:** `templates/risk-assessment.md` (template), `docs/SECURITY-CONTROLS.md` (control guidance).
