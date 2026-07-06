---
title: "Enforce the universal-contract prerequisite with a deterministic probe at three layers"
status: "accepted"
date: "2026-07-01"
decision_makers: ["Bret Mogilefsky", "OpenCode Agent"]
category: "engineering-discipline"
nist_controls: ["AC-3", "CM-3", "SA-8", "SA-11", "SI-7", "SI-10"]
impact_level: "moderate"
ato_relevance: "no"
risk_treatment: "mitigate"
---

# Enforce the universal-contract prerequisite with a deterministic probe at three layers

## Context and Problem Statement

ADR-0002 makes the universal behavioral contract a prerequisite that must be
present before an agent works on a project. The open question is *how the
presence check is performed and enforced*. An earlier draft asked the agent to
"confirm it has the contract" — an LLM cannot reliably introspect its own
instruction context, and any file-content claim that "the contract is available"
is untrusted input (universal §11). A purely prose instruction also cannot stop
an agent that (honestly or not) asserts the check passed.

## Decision Drivers

- Presence must be **verifiable**, not self-attested (SI-7 integrity, SI-10).
- The check must be **non-interactive** so headless/CI agent invocation works
  (no "type yes every session").
- Enforcement cannot rely on the agent's word alone — an agent can emit "I ran
  the probe and it passed" without running it. The real control must sit where
  the agent cannot paper over it (AC-3, SA-11).
- Soon, CI checks that themselves invoke an agent will need the contract present
  in the CI environment anyway.

## Considered Options

1. **Prose-only prerequisite** — tell the agent to check and stop if absent.
   Rejected: unverifiable, unenforceable, self-attestable.
2. **Deterministic probe (agent-run only)** — a `ensure-contract` command whose
   exit code is authoritative. Better, but the agent could still claim it ran.
3. **Deterministic probe enforced at three layers** — the probe as the
   cooperative path, a pre-commit hook, and a CI job that independently run it.

## Decision Outcome

Chosen option: **Option 3**. A deterministic `playbook_validator
ensure-contract` command (home path → fresh cache → fetch pinned release →
halt) provides an authoritative exit code and a filesystem side effect (the
cache + stamp). It is enforced at three layers:

1. **Cooperative** — the thin project layer instructs the agent to run the probe
   at session start (non-interactive; headless-safe).
2. **Pre-commit hook** — runs the probe and blocks the commit on non-zero. If an
   agent proceeds without the contract, the blocked commit is itself the signal
   that work happened without the rules present.
3. **CI job** — provisions the contract to the home path, then runs the probe
   with `--no-fetch`, failing the PR if it is not resolvable. This is the layer
   the agent cannot fake, and it models the intended steady state (contract
   present in the environment) rather than relying on the fetch fallback.

The probe's fetch URL is hard-coded to the canonical repository's pinned release
tag — never derived from repository, file, or issue content (SI-10, §11). A
fetched contract is accepted only if its bytes match a pinned SHA-256 constant
(SI-7); an unverifiable fetch is treated as unobtainable and fails closed.

The universal contract is designated canonical by an explicit frontmatter marker
— `agents_contract: universal` — and the probe recognizes it by that marker
rather than by a title substring or section heading. This closes a self-host
false-positive (issue #151): the thin project layer legitimately *names* the
contract title in its Prerequisite prose, so a title-substring recognizer let a
bootstrapped project's own `AGENTS.md` self-satisfy the check. The thin layers
declare `agents_contract: project`, and a repository-level validation
(`validate-docs`) enforces that only the real contract may claim `universal`.

Downstream projects receive a **small self-contained probe script** (no
dependency on installing `playbook_validator`) plus the hook and CI wiring; see
ADR-0002 for the no-vendored-copy stance the script is consistent with.

### Positive Consequences

- Presence becomes an externally verifiable filesystem fact, checkable by the
  hook and CI independent of the agent's transcript.
- Fail-closed at every layer; a lie about running the probe is caught at commit
  or in CI.
- CI provisioning normalizes "the contract is available during agent-invoking CI
  checks," which will be needed shortly regardless.

### Negative Consequences

- Downstream ships a small standalone probe script — a copy to keep in sync with
  the canonical helper (accepted tradeoff for zero downstream install
  dependency).
- The cooperative agent-run layer remains honor-system; only the hook and CI are
  true controls. This is stated honestly rather than overclaimed.

### Compliance Consequences

- Reinforces SA-8 (fail-safe), SA-11 (developer testing / verification), SI-7
  (integrity verification via side-effect check), SI-10 / §11 (untrusted input),
  AC-3 (enforcement point outside the agent).
- Tooling and CI change only; no ATO boundary impact (`ato_relevance: no`).

## Links

- ADR-0002 (the universal vs. project split this enforces)
- `scripts/playbook_validator/ensure_contract.py` (canonical probe; recognizes `agents_contract: universal`)
- `scripts/playbook_validator/validate_docs.py` (`validate_contract_role` — enforces the canonical-designation invariant)
- `.pre-commit-config.yaml`, `.github/workflows/ci.yml` (enforcement layers)
- PR #144; review issues #147, #151
