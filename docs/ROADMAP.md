---
title: "Roadmap"
description: "Long-term plan for the Agentic Coding Playbook — making it a living resource for federal engineers learning agentic coding"
status: canonical
tier: 3
last_updated: "2026-06-01"
load_priority: reference-only
audience: ["developers", "managers"]
keywords: ["roadmap", "plan", "future", "strategy"]
---

# Roadmap

Long-term plan for making the Agentic Coding Playbook a living, learnable resource for federal engineers.

## Current State

<!-- GENERATED:ROADMAP_METRICS:START — do not edit, run: make generate -->
| Metric | Count |
|--------|-------|
| Documents | 23 |
| Skills | 12 |
| Tests | 546 |
| Checklist items | 62 |
| Landscape entries | 42 |
| NIST controls mapped | 35 |
<!-- GENERATED:ROADMAP_METRICS:END -->

> These counts are generated from the repository's own sources (`INDEX.yaml`
> stats, `data/federal-ai-landscape.yaml`, `docs/SECURITY-CONTROLS.md`, the
> checklist, and pytest collection) by `make generate` — do not hand-edit.

The playbook covers the full SDLC from project planning through deployment and continuous monitoring. All content is model-agnostic (AGENTS.md standard, 25+ tools).

## Phase 1: Documentation Site (Next)

**Goal:** Make the playbook browsable and searchable as a hosted website.

- Convert markdown docs to a static documentation site
- Auto-generate navigation from tier structure
- Add full-text search
- Deploy to a FedRAMP-authorized hosting platform
- Skills become interactive pages with copy-paste commands

The content is already well-structured with YAML frontmatter — static site generation is primarily a configuration task.

**Effort:** Medium (1-2 weeks).

## Phase 2: Interactive Skills

**Goal:** Make skills executable, not just readable.

Enable users to run code blocks directly from skill documents in their editor or terminal, rather than manual copy-paste. Several open-source tools support executable markdown — evaluate options that work without vendor lock-in.

**Effort:** Small (2-3 days). Add annotations to existing code blocks.

## Phase 3: Learning Paths

**Goal:** Guide engineers through agentic coding concepts progressively.

Structure:

```
Learning Paths:
├── Beginner: "I've never used an AI coding agent"
│   → AGENTS.md sections 1-3 → GETTING-STARTED.md → first skill (federal-repo-setup)
├── Intermediate: "I use Copilot but need federal compliance"
│   → CODING_PRACTICES.md → SECURITY-CONTROLS.md → code-review skill
└── Advanced: "I want to build multi-agent workflows"
│   → AGENT-IDENTITY.md → PROMPT-INJECTION-DEFENSE.md → ato-package skill
```

Each path is a curated sequence of existing documents with checkpoint exercises.

**Effort:** Medium. Content exists — needs sequencing, exercises, and progress tracking.

## Phase 4: Community Contributions

**Goal:** Build a community of federal practitioners contributing skills and guidance.

- Quarterly landscape review (tracked by #46)
- Skill contribution guide with templates (already exists)
- Office hours or async Q&A channel
- Agency-specific skill packs (extensions, not forks)
- Align with existing federal digital service guide patterns

## Phase 5: Automated Freshness

**Goal:** Eliminate all manual maintenance.

| Currently automated | Not yet automated |
|---|---|
| Skills tables (3 files) | Test count in README |
| Word counts in CONTEXT-GUIDE | Landscape entry count in README |
| INDEX.yaml from frontmatter | Framework version strings |
| CHANGELOG from commits | NIST control count in README |
| Releases from tags | |

Extend `make generate` to inject all dynamic counts from source data. Add a CI check that fails if any hardcoded count drifts from the computed value.

## Phase 6: Multi-Agent Guidance (Future)

**Goal:** Extend beyond single-agent to multi-agent coordination.

Tracked by issue #13. Requires:
- Agent-to-agent communication protocols
- Delegation and trust boundaries
- Shared state management
- Conflict resolution when agents disagree
- NIST controls for multi-agent systems (emerging)

This is blocked on NIST CAISI standards (expected 2026-2027).

## Success Metrics

| Metric | Target | How measured |
|--------|--------|-------------|
| Time to first bootstrapped repo | < 10 minutes | User testing |
| Test pass rate | 100% | CI |
| Stale content items | 0 | `make generate-check` |
| Quarterly landscape review | On schedule | Issue #46 |
| Community contributions | 1+ per quarter | PR count |
