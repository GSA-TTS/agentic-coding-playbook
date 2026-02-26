# Changelog

All notable changes to this guidance will be documented in this file.

This project uses [Semantic Versioning](https://semver.org/). Framework alignment versions are tracked inline in each document.

## [0.3.1] - 2026-02-26

### Fixed

- `scripts/lib/common.sh` — replaced `head -n -1` with `sed '$ d'` for macOS/BSD compatibility; the negative line count syntax is GNU-specific and caused "head: illegal line count -- -1" errors on macOS
- `scripts/validate-docs.sh` — same fix for frontmatter extraction (2 occurrences)
- `scripts/validate-skills.sh` — same fix for frontmatter extraction
- INDEX.yaml — regenerated with corrected frontmatter parsing (now correctly shows 47 unique NIST controls and 14 frameworks)

### Changed

- README.md — added Claude Code to list of compatible AI coding agents

## [0.3.0] - 2026-02-26

### Added

- **LLM context optimization — progressive disclosure architecture**:
  - `CONTEXT-GUIDE.md` — compact agent entry point (~500 words) with tiered loading instructions, keyword triggers, and typical task profiles
  - `load_priority` frontmatter field on all 11 content documents: `always`, `task-context`, `on-demand`, `reference-only`
  - `<!-- LOAD: ... -->` HTML comment directives after frontmatter in every document
  - `load_priority_values` in INDEX.yaml schema and `DOC_LOAD_PRIORITY_VALUES`/`DOC_LOAD_PRIORITY_REGEX` in `scripts/config.sh`
  - `load_priority` validation in `scripts/validate-docs.sh`
  - `load_priority` field emitted in INDEX.yaml document entries via `scripts/generate-index.sh`
- **Quick Reference sections** at the top of 5 core docs (AGENTS.md, CODING_PRACTICES.md, SECURITY-CONTROLS.md, AGENT-IDENTITY.md, GETTING-STARTED.md) — actionable summaries in table format for LLM-efficient scanning

### Changed

- AGENTS.md: replaced 15-row NIST Control Cross-Reference Matrix (~340 words) with a pointer to `docs/TRACEABILITY.md` (single source of truth for traceability)
- README.md: updated agent instructions to point to `CONTEXT-GUIDE.md` as entry point, updated repo structure tree
- INDEX.yaml: now includes `load_priority` for each document and `load_priority_values` in schema

### Token Impact

| Scenario | Words | Tokens | Reduction |
|----------|-------|--------|-----------|
| Load everything | 44,596 | ~58K | baseline |
| Typical code task (CONTEXT-GUIDE + Tier 1) | 8,950 | ~12K | -80% |
| Security assessment (+ SECURITY-CONTROLS) | 16,162 | ~21K | -64% |
| Full compliance audit (Tiers 1-3) | 28,909 | ~38K | -35% |

## [0.2.2] - 2026-02-25

### Added

- `examples/AGENTS.md.example` — added §14 Agent Meta-Constraints and §15 Engineering Discipline sections with HR Benefits Portal-specific values
- `docs/TRACEABILITY.md` — added §14-§15 control mappings: 4 new controls (SA-5, SA-8, SA-17, SI-17) and updated 8 existing controls (AU-12, CM-2, CM-3, CM-5, CM-6, IR-6, SA-11, SA-15) with §14-§15 section references
- `docs/TRACEABILITY.md` — updated AI RMF function mappings for GOVERN 1, MANAGE 1, MEASURE 2

### Fixed

- `scripts/validate-docs.sh` — replaced unsafe word-splitting `for file in $CONTENT_FILES` with NUL-delimited `mapfile` + `while IFS= read -r` for safe handling of filenames with spaces
- `scripts/validate-docs.sh` — replaced unsafe `for path in $INDEX_PATHS` with `while IFS= read -r` loop

## [0.2.1] - 2026-02-25

### Added

- **Centralized config and shared script library** — eliminates duplication across 5 scripts:
  - `scripts/config.sh` — single source of truth for schema constants (status values, tier values, required fields, NIST control regex, skill limits, size/complexity limits, framework versions)
  - `scripts/lib/common.sh` — shared frontmatter extraction (`get_field()`, `get_array_field()`) and JSON output helpers (`json_init()`, `json_add_result()`, `json_output()`)

### Changed

- All 5 shell scripts now source `scripts/config.sh` and/or `scripts/lib/common.sh` instead of duplicating helpers
- CI: ShellCheck now uses `-x` flag and `-e SC1091` to support cross-file sourcing
- `validate-docs.sh`: uses `REQUIRED_FRONTMATTER_FIELDS`, `DOC_STATUS_REGEX`, `DOC_TIER_REGEX` from config.sh
- `validate-skills.sh`: uses `SKILL_MAX_LINES`, `SKILL_NAME_MAX_LENGTH`, `SKILL_NAME_INVALID_CHARS_REGEX` from config.sh
- `generate-index.sh`: uses `REQUIRED_FRONTMATTER_FIELDS`, `OPTIONAL_FRONTMATTER_FIELDS`, `DOC_STATUS_VALUES`, `DOC_AUDIENCE_VALUES`, `DOC_REVIEW_CYCLE_VALUES` from config.sh; uses `get_field()`, `get_array_field()` from lib/common.sh
- `validate-adrs.sh`: uses `REQUIRED_ADR_FIELDS`, `ADR_STATUS_REGEX`, `NIST_CONTROL_REGEX`, `ADR_FILENAME_REGEX` from config.sh; uses `json_init()`, `json_add_result()`, `json_output()` from lib/common.sh
- `generate-adr-index.sh`: uses `get_field()`, `get_array_field()` from lib/common.sh

## [0.2.0] - 2026-02-25

### Added

- **Engineering discipline sections in CODING_PRACTICES.md** — 3 new sections (§11-§13):
  - §11 Architecture Discipline — ADR usage policy, Design by Contract, Interfaces before implementations, Separation of Concerns, Conway's Law awareness
  - §12 Change Safety and Verification — TDD (red-green-refactor), property-based testing, regression test rule, snapshot/golden tests, idempotent operations, explicit error signaling
  - §13 Scope, Simplicity, and Maintainability — KISS/YAGNI/DRY, Rule of Three, size/complexity guidelines (≤50 lines/function, ≤400 lines/file, ≤10 cyclomatic complexity), SOLID principles, module boundaries
- **Agent meta-constraint sections in AGENTS.md** — 2 new sections (§14-§15):
  - §14 Agent Meta-Constraints — Plan before executing, PR discipline (5 required sections), verification transcript, run-and-verify loop, no silent failures, risk modes
  - §15 Engineering Discipline Enforcement — ADR trigger conditions, discipline enforcement in review, one-command bootstrap/verify, docs-as-code, why-before-what
- AGENTS.md.template updated with Agent Meta-Constraints and Engineering Discipline template stubs
- **Agent Skills execution layer** — 6 skills in [Agent Skills format](https://agentskills.io) for cross-platform agent compatibility
  - `federal-security-controls-lookup` — NIST/OWASP control and keyword lookup across all policy documents
  - `federal-repo-setup` — Repository initialization with federal security compliance defaults (+ audit script)
  - `federal-agents-config` — Interactive AGENTS.md generation via decision-tree elicitation (+ generation and validation scripts)
  - `federal-pre-deployment-check` — Automated + manual execution of the pre-deployment checklist (+ check runner and report generator)
  - `federal-risk-assessment` — Guided risk assessment worksheet completion (+ pre-filled threat catalog)
  - `federal-decision-records` — MADR-based decision records with federal compliance extensions (+ index generator and validator scripts)
- `scripts/validate-skills.sh` — CI validation for skill format (frontmatter, line count, ShellCheck, py_compile)
- `skills-validation` CI job in GitHub Actions
- Skills section in INDEX.yaml with inventory of all 6 skills
- Agent Skills section in README.md explaining dual-layer architecture
- Skill contribution guidelines in CONTRIBUTING.md
- Reference documents: TOOL_MATRIX.md, PLACEHOLDER_SCHEMA.json, ELICITATION_GUIDE.md, CHECK_AUTOMATION.md, THREAT_CATALOG.md, ADR_TEMPLATE.md, DECISION_CATEGORIES.md
- `scripts/generate-index.sh` — Deterministic INDEX.yaml generator (derives all metadata from frontmatter)
- INDEX.yaml drift detection in CI (`generate-index.sh --check`)
- Cross-validation: skills on disk must appear in INDEX.yaml

### Fixed

- INDEX.yaml `total_nist_controls_referenced` was 42 (correct: 40 unique controls from frontmatter)
- INDEX.yaml `frameworks_covered` was 12 (correct: 14 unique frameworks from frontmatter)
- `docs/SECURITY-CONTROLS.md` description said "37 controls" (correct: 36 controls in overlay)
- README.md version table only showed 0.1.0 (added 0.1.1, 0.2.0)
- Skill `federal-security-controls-lookup` document inventory was hardcoded (now references INDEX.yaml)

### Changed

- CI: ShellCheck now also checks skill scripts in `skills/*/scripts/*.sh`
- `scripts/validate-docs.sh`: excludes `skills/` directory (skills have their own validation)
- `scripts/validate-docs.sh`: INDEX.yaml path validation excludes skill paths (validated by validate-skills.sh)
- README.md: updated repository structure tree to include skills directory
- CONTRIBUTING.md: added skill contribution requirements and structure guide

## [0.1.1] - 2026-02-25

### Added

- SECURITY.md — responsible disclosure policy for guidance accuracy and infrastructure issues
- GitHub issue templates — bug report and document improvement request
- Pull request template — checklist for frontmatter, INDEX.yaml, and cross-references
- Dependabot configuration — weekly GitHub Actions version updates
- ShellCheck linting in CI pipeline for shell scripts

### Fixed

- CI pipeline: corrected markdownlint-cli2-action SHA and version (v18 → v22)
- Frontmatter validation: fixed broken pipe error with long YAML arrays
- Frontmatter validation: exclude .github/ templates and SECURITY.md from content checks
- Link checker: ignore private repo URLs (404 in unauthenticated CI context)
- Markdownlint: disabled cosmetic rules that conflict with guidance formatting

### Changed

- Updated all GitHub Actions to latest versions via Dependabot (checkout v6, markdownlint v22, link-check v1.0.17, gh-release v2.5)

## [0.1.0] - 2026-02-25

### Added

- Initial repository structure and scaffolding
- AGENTS.md — master agent behavior rules (13 sections, 19+ NIST control mappings)
- CODING_PRACTICES.md — secure coding standards for AI-assisted development (10 sections)
- docs/GETTING-STARTED.md — repository setup, tooling, and environment hardening
- docs/SECURITY-CONTROLS.md — NIST 800-53 control overlay (37 controls, 10 families)
- docs/AGENT-IDENTITY.md — agent identity, authentication, and delegation guidance
- docs/TRACEABILITY.md — bidirectional control-to-document traceability matrix
- templates/AGENTS.md.template — copy-paste agent rules for new projects
- templates/risk-assessment.md — AI risk assessment worksheet (AI RMF aligned)
- checklists/pre-deployment.md — pre-deployment security checklist
- examples/AGENTS.md.example — completed example for federal HR portal
- INDEX.yaml — machine-readable document index with schema definition
- YAML frontmatter on all content documents (title, description, status, tier)

### Infrastructure

- GitHub Actions CI pipeline (markdown lint, link check, frontmatter validation)
- Automated release workflow (triggered by semver tags)
- Frontmatter and INDEX.yaml consistency validation script
- Markdownlint and markdown-link-check configuration
- CODEOWNERS and CONTRIBUTING.md

### Framework Versions Referenced

| Framework | Version | Date |
|-----------|---------|------|
| NIST AI RMF | 1.0 | Jan 2023 |
| NIST SP 800-53 | Rev 5.2.0 | Sep 2024 |
| NIST SP 800-218A | Final | Jun 2024 |
| NIST AI 600-1 | 1.0 | Jul 2024 |
| NIST COSAiS | Concept Paper | Aug 2025 |
| NCCOE Agent Identity | Concept Paper | Feb 2026 |
| NIST CAISI | Initiative Launch | Feb 2026 |
| OWASP Top 10 LLM | 2025 | Nov 2024 |
| OWASP Agentic AI | 1.0 | Dec 2025 |
| CISA Secure by Design | 2025 | 2025 |
| OMB M-25-21 | Final | Apr 2025 |
