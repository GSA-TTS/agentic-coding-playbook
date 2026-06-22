---
title: "Adopt a Laziness Ladder for simplicity guidance"
status: "accepted"
date: "2026-06-22"
decision_makers: ["William Zujkowski", "OpenCode Agent"]
category: "engineering-discipline"
nist_controls: ["SA-8", "SA-11", "SA-15"]
impact_level: "moderate"
ato_relevance: "no"
risk_treatment: "n/a"
---

# Adopt a Laziness Ladder for simplicity guidance

## Context and Problem Statement

The playbook's behavioral contract (`AGENTS.md` §1, §15) and coding standards
(`docs/CODING_PRACTICES.md` §13) already prioritize simplicity and YAGNI, but
they did not give the agent a concrete, ordered decision procedure for *how* to
reach the minimum solution. Agents commonly over-build (custom components where
a native feature exists, new dependencies where the stdlib suffices), which
increases attack surface and maintenance burden.

## Decision Drivers

- §13 already states "complexity is the enemy of security" but lacked an
  actionable, memorable rule for code generation and review.
- The open-source [ponytail](https://github.com/DietrichGebert/ponytail) ruleset
  (MIT, ~48k stars) demonstrates a concise "stop at the first rung that holds"
  ladder with measured reductions in code volume on real agentic tasks.
- Federal use requires that any "write less code" guidance MUST NOT erode
  validation, error handling, security, or accessibility (SA-8 secure
  engineering principles, Section 508).

## Considered Options

1. **Add a short "Laziness Ladder" subsection to §13.1 + reference it from
   AGENTS.md §15.2** — additive, keeps existing rules.
2. **Adopt ponytail wholesale** (its plugin, hooks, MCP machinery, and
   irreverent tone) — rejected: tooling and tone are a poor fit for a federal
   standards document.
3. **Do nothing** — leave the existing prose-only YAGNI guidance.

## Decision Outcome

Chosen option: **Option 1**, because it captures the useful, original idea (an
ordered decision ladder) as concise additive guidance without importing
inappropriate tooling or tone, and explicitly hardens it with non-negotiable
federal carve-outs.

### Positive Consequences

- Agents get a concrete, ordered procedure (skip → stdlib → native → existing
  dep → one line → minimum code) for both generation and review.
- The "never simplify away validation/error-handling/security/accessibility"
  carve-out is stated as mandatory, preventing misuse as a code-golf license.
- A companion `over-engineering-review` skill is added to the patterns repo to
  operationalize the ladder as a reviewable delete-list.

### Negative Consequences

- One more subsection to maintain in §13 and keep in sync with the AGENTS.md
  §15.2 reference.

### Compliance Consequences

- Reinforces SA-8 (security engineering principles) and SA-15 (development
  process); no new controls required.
- Documentation-only change; no ATO package impact (`ato_relevance: no`).

## Links

- `docs/CODING_PRACTICES.md` §13.1.1 (the Laziness Ladder)
- `AGENTS.md` §15.2 (discipline enforcement in review)
- ponytail (MIT): https://github.com/DietrichGebert/ponytail
- agentic-coding-patterns: `over-engineering-review` skill (companion)
