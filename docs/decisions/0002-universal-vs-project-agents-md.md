---
title: "Split the agent contract into a universal layer and a thin project layer"
status: "accepted"
date: "2026-07-01"
decision_makers: ["Bret Mogilefsky", "OpenCode Agent"]
category: "engineering-discipline"
nist_controls: ["CM-2", "CM-3", "PL-4", "SA-5", "SA-8", "SI-10"]
impact_level: "moderate"
ato_relevance: "no"
risk_treatment: "mitigate"
---

# Split the agent contract into a universal layer and a thin project layer

## Context and Problem Statement

The playbook's `AGENTS.md` served two roles at once: the universal behavioral
contract that applies to every project, and this repository's own tooling
reference. New projects received a full copy of the universal rules (via the
template), so the universal contract was physically duplicated into every
downstream repository. Copies drift: a project pinned to an old copy silently
diverges from the current federal guidance, and there is no single source of
truth.

## Decision Drivers

- A single source of truth for the universal behavioral rules (CM-2 baseline)
  avoids silent drift across downstream repositories.
- Downstream projects still need their own project-specific rules (permitted /
  prohibited actions, data handling, contacts) — those are legitimately local.
- The universal rules must actually be present before an agent acts on a
  federal project; absence must fail closed, not proceed uncontracted (SA-8).
- Prompt-injection exposure (SI-10, universal §11): any "the rules are present"
  signal must not be satisfiable by untrusted repository/file content.

## Considered Options

1. **Universal contract provided by the environment + thin project layer that
   references it as a prerequisite.** The universal `AGENTS.md` is never
   vendored downstream; each project ships only a thin layer.
2. **Vendored copy per project with a freshness check.** Keep copying the
   universal rules into each repo but add tooling to detect staleness.
3. **Pinned submodule / dependency.** Vendor the playbook as a pinned
   dependency each project references.

## Decision Outcome

Chosen option: **Option 1**, because it eliminates the drift class entirely
(the universal rules exist in exactly one place) while preserving a genuine,
minimal project-specific layer. Options 2 and 3 keep a per-project copy — the
very thing that drifts — and add carrying cost.

The universal contract is expected at a conventional home path
(`~/.agentic-coding-playbook/AGENTS.md`, override `$AGENTIC_CODING_PLAYBOOK_HOME`),
with a git-ignored fallback cache. Presence is a **deterministic filesystem
check** (see ADR-0003), not agent self-attestation and not an interactive
per-session prompt (so headless invocation still works). The prerequisite is
**fail-closed**: if the contract cannot be obtained, the agent must stop — there
is no "proceed without the universal contract" option.

### Positive Consequences

- One source of truth for the universal rules; downstream projects cannot drift
  from federal guidance by carrying a stale copy.
- Thin project layer stays focused on genuinely local rules.
- Fail-closed prerequisite means a federal project is never worked on without
  the behavioral contract present.

### Negative Consequences

- Downstream projects now depend on the environment providing the contract; a
  concrete provisioning path must be documented (README) and enforced (ADR-0003).
- Reverses the earlier "proceed without" escape hatch that an initial draft of
  this work had adopted.

### Compliance Consequences

- Reinforces CM-2 (baseline configuration / single source of truth), PL-4
  (rules of behavior), SA-8 (fail-safe), and SI-10 (untrusted input handling).
- Documentation and tooling change only; no system authorization boundary
  impact (`ato_relevance: no`).

## Links

- `AGENTS.md` (universal contract) and `templates/AGENTS.md.template` (thin layer)
- ADR-0003 (enforcement of the prerequisite)
- PR #144; review issues #145, #146, #147, #148
