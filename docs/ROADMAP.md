---
title: "Roadmap"
description: "Long-term plan for the Agentic Coding Playbook — making it a living resource for federal engineers learning agentic coding"
status: canonical
tier: 3
load_priority: reference-only
audience: ["developers", "managers"]
keywords: ["roadmap", "plan", "future", "strategy"]
---

# Roadmap

Long-term plan for making the Agentic Coding Playbook a living, learnable resource for federal engineers.

## Current State (v0.5.0)

| Metric | Count |
|--------|-------|
| Documents | 20 |
| Skills | 11 |
| Tests | 270 |
| Checklist items | 62 |
| Landscape entries | 39 |
| NIST controls mapped | 55 |

The playbook covers the full SDLC from project planning through deployment and continuous monitoring. All content is model-agnostic (AGENTS.md standard, 25+ tools).

## Phase 1: Documentation Site (Next)

**Goal:** Make the playbook browsable and searchable as a website.

**Recommended tool:** [Astro Starlight](https://starlight.astro.build/) — built for docs, supports YAML frontmatter natively, fast static output, sidebar auto-generation.

- Convert markdown docs to a Starlight site
- Auto-generate sidebar from tier structure
- Add search (built into Starlight)
- Deploy to GitHub Pages or cloud.gov
- Skills become interactive pages with copy-paste commands

**Why Starlight:** Python-based alternatives (MkDocs) are good but Starlight has native frontmatter validation via content collections (replaces some of our custom validators), built-in versioning, and is used by major open source projects.

**Effort:** Medium (1-2 weeks). The content is already well-structured — it's mostly configuration.

## Phase 2: Interactive Skills with Runme

**Goal:** Make skills executable, not just readable.

[Runme](https://runme.dev/) lets users run code blocks directly from markdown in VS Code or the terminal. Skills like `federal-repo-setup` and `code-review` have command blocks that could be executed in place.

- Add Runme annotations to skill code blocks
- Users click "Run" on each step instead of copy-pasting
- Works with any terminal — no vendor lock-in

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
- Align with 18F/digital.gov guide patterns

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

## Tooling Decisions

### Keep (working well)

| Tool | Purpose | Why keep |
|------|---------|----------|
| Custom Python validators | Frontmatter, skills, landscape, ADRs | Tailored to our schema, 285 tests |
| pymarkdown | Markdown lint | Python-native, no Node.js dependency |
| ruff | Python lint + format | Fast, comprehensive |
| release-please | Automated releases | Zero-maintenance changelog + versioning |
| Makefile | Developer commands | Universal, no dependencies |

### Consider adding

| Tool | Purpose | When |
|------|---------|------|
| Astro Starlight | Documentation site | Phase 1 |
| Runme | Interactive skills | Phase 2 |

### Not recommended

| Tool | Why not |
|------|---------|
| MkDocs | Good but Starlight has better frontmatter validation |
| Docusaurus | React dependency, heavy for a playbook |
| Backstage | Designed for service catalogs, overkill here |
| Custom CLI (npm/pip package) | YAGNI — Makefile + Python module is sufficient |

## Success Metrics

| Metric | Target | How measured |
|--------|--------|-------------|
| Time to first bootstrapped repo | < 10 minutes | User testing |
| Test pass rate | 100% | CI |
| Stale content items | 0 | `make generate-check` |
| Quarterly landscape review | On schedule | Issue #46 |
| Community contributions | 1+ per quarter | PR count |
