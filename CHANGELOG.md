# Changelog

All notable changes to this playbook will be documented in this file.

This project uses [Semantic Versioning](https://semver.org/). Framework alignment versions are tracked inline in each document.

## [0.7.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.0...v0.7.0) (2026-04-09)


### Features

* clean import of agentic-coding-playbook v0.6.0 ([8e1d408](https://github.com/GSA-TTS/agentic-coding-playbook/commit/8e1d408597855dd81cbb3d330b10952b906ab424))

## [0.6.0](https://github.com/gsa-tts/agentic-coding-playbook/compare/v0.5.1...v0.6.0) (2026-04-07)


### Features

* add dependency lock files and pip-audit SCA scanning ([#85](https://github.com/gsa-tts/agentic-coding-playbook/issues/85)) ([bdd0b3f](https://github.com/gsa-tts/agentic-coding-playbook/commit/bdd0b3f70be174a4a0738e9b95fe4fa498bf66b8))
* nexus-agents iteration 2 — CI hardening, Makefile targets, pyproject.toml checker ([#89](https://github.com/gsa-tts/agentic-coding-playbook/issues/89)) ([2eb18db](https://github.com/gsa-tts/agentic-coding-playbook/commit/2eb18db6bda27cc0d4e31b2106a4eff7b1904731))
* nexus-agents review — harden CLI, doctor, CI, refactor, add 23 tests ([#80](https://github.com/gsa-tts/agentic-coding-playbook/issues/80)) ([d7c7067](https://github.com/gsa-tts/agentic-coding-playbook/commit/d7c7067474c097a4dc3fc2cc545a4572ccc967d5))

## [0.5.1](https://github.com/gsa-tts/agentic-coding-playbook/compare/v0.5.0...v0.5.1) (2026-04-02)


### Bug Fixes

* remove sandbox/Docker config — playbook is governance only ([#72](https://github.com/gsa-tts/agentic-coding-playbook/issues/72)) ([382cc39](https://github.com/gsa-tts/agentic-coding-playbook/commit/382cc3905d940b1ceb91ab117c7a051384ebdcfc))

## [0.5.0](https://github.com/gsa-tts/agentic-coding-playbook/compare/v0.4.0...v0.5.0) (2026-04-02)


### Features

* add continuous monitoring guidance for deployed AI systems ([#60](https://github.com/gsa-tts/agentic-coding-playbook/issues/60)) ([69435bd](https://github.com/gsa-tts/agentic-coding-playbook/commit/69435bd096e86b353b49d6f174d1f2908edb9a84))
* add sandbox support for isolated AI agent execution ([#71](https://github.com/gsa-tts/agentic-coding-playbook/issues/71)) ([e0615c5](https://github.com/gsa-tts/agentic-coding-playbook/commit/e0615c5ef4d89cf1e503dc944432928d319d358e))
* AI bias testing, model evaluation, and PIA template ([#59](https://github.com/gsa-tts/agentic-coding-playbook/issues/59), [#61](https://github.com/gsa-tts/agentic-coding-playbook/issues/61), [#62](https://github.com/gsa-tts/agentic-coding-playbook/issues/62)) ([421b554](https://github.com/gsa-tts/agentic-coding-playbook/commit/421b5545584eecb25623cbeaf2e118e0313496b9))
* auto-inject test and landscape counts via make generate ([b323353](https://github.com/gsa-tts/agentic-coding-playbook/commit/b3233538690ba3cc1c1ddacf191d4988492a140b))
* make new-project command + CI validators + NIST AI 800-4 ([#64](https://github.com/gsa-tts/agentic-coding-playbook/issues/64), [#65](https://github.com/gsa-tts/agentic-coding-playbook/issues/65), [#67](https://github.com/gsa-tts/agentic-coding-playbook/issues/67)) ([d37d82f](https://github.com/gsa-tts/agentic-coding-playbook/commit/d37d82ffc491828b6f8e4d3a74d22bfcd86f18ed))
* make new-project copies skills + creates agent config shims ([1f5c1a9](https://github.com/gsa-tts/agentic-coding-playbook/commit/1f5c1a9144bfb152b20e27edfdd4edbc226e6b04))
* prompt injection defense patterns + Section 508 accessibility ([#63](https://github.com/gsa-tts/agentic-coding-playbook/issues/63), [#65](https://github.com/gsa-tts/agentic-coding-playbook/issues/65)) ([005b011](https://github.com/gsa-tts/agentic-coding-playbook/commit/005b0117eee8543b9e47e2bfe35b1d0d70674515))
* rename to agentic-coding-playbook for GSA-TTS ([1c3a2b5](https://github.com/gsa-tts/agentic-coding-playbook/commit/1c3a2b53a7e61b2791b5ae07bddb620b1de932b5))


### Bug Fixes

* **ci:** disable MD004 (list style) — CHANGELOG.md uses mixed styles ([9de2c0b](https://github.com/gsa-tts/agentic-coding-playbook/commit/9de2c0b7c84437ab9c28cf2ce0608a5e658a5378))
* **ci:** exclude CHANGELOG.md from markdown lint ([c88cb85](https://github.com/gsa-tts/agentic-coding-playbook/commit/c88cb850e13ae2d34cda95d8ff20604e3e97d6c8))
* **ci:** remove audit-repo from CI — designed for target repos not playbook ([18e5329](https://github.com/gsa-tts/agentic-coding-playbook/commit/18e532989c7f8c0f7f91ccaace014e608b282461))
* harden YAML serialization + make link-check non-blocking ([ba6a569](https://github.com/gsa-tts/agentic-coding-playbook/commit/ba6a569974c060493652a3980c2814344799de5d))
* remove Claude-specific references — make fully tool-agnostic ([6e8e9e4](https://github.com/gsa-tts/agentic-coding-playbook/commit/6e8e9e46bac23d1a9f7bd714d1424e1f7c444325))
* remove remaining Claude-specific examples from skills and tests ([4d86786](https://github.com/gsa-tts/agentic-coding-playbook/commit/4d86786d4adab7c03cf93b0f76744367e9b36b57))
* ruff format validate_docs.py ([5ec1c2a](https://github.com/gsa-tts/agentic-coding-playbook/commit/5ec1c2aacf17bf29a0c90117b2b7bfdf1645ea75))
* update test count 248 → 252 across all docs ([9d90426](https://github.com/gsa-tts/agentic-coding-playbook/commit/9d90426735931e4a731349d16b8354397b63d905))


### Documentation

* add GSA VDP link + contributor eligibility requirement ([ae6dbc0](https://github.com/gsa-tts/agentic-coding-playbook/commit/ae6dbc053132891ef5cce3465a7e7f9a74848827))
* add ROADMAP.md — long-term plan for the playbook ([38a3bdc](https://github.com/gsa-tts/agentic-coding-playbook/commit/38a3bdcd70a6fb9093b8155db30f70f3b6064960))
* simplify contributor workflow — make generate + make ci is all you need ([a4d85fa](https://github.com/gsa-tts/agentic-coding-playbook/commit/a4d85fa0e4fb005242f2cb658e72d66af31d6ba0))


### Refactoring

* remove agent shims — AGENTS.md is the universal standard ([cb29fd3](https://github.com/gsa-tts/agentic-coding-playbook/commit/cb29fd3527ba174ff85b45a02203be0cde59ede3))

## [0.4.0](https://github.com/gsa-tts/agentic-coding-playbook/compare/v0.3.0...v0.4.0) (2026-03-25)


### Features

* add ato-package skill for ATO submission assembly ([#56](https://github.com/gsa-tts/agentic-coding-playbook/issues/56)) ([cb623c7](https://github.com/gsa-tts/agentic-coding-playbook/commit/cb623c76fffe132a572b5010e932429164c06ceb))
* add code-review skill + fix federal-repo-setup gaps ([#51](https://github.com/gsa-tts/agentic-coding-playbook/issues/51), [#52](https://github.com/gsa-tts/agentic-coding-playbook/issues/52)) ([05d11b9](https://github.com/gsa-tts/agentic-coding-playbook/commit/05d11b94a164e91a72e4f0b73e689eee205e9a3e))
* add LLM-optimized compact coding standards for code generation ([#57](https://github.com/gsa-tts/agentic-coding-playbook/issues/57)) ([23fc9be](https://github.com/gsa-tts/agentic-coding-playbook/commit/23fc9bee62c8078a87549e9261555c6c41c46e00))
* add risk assessment validation module with 17 TDD tests ([#54](https://github.com/gsa-tts/agentic-coding-playbook/issues/54)) ([e8e37fd](https://github.com/gsa-tts/agentic-coding-playbook/commit/e8e37fdeaf0530ee500a5120aeecd5a32edf6f3e))
* auto-generate word counts in CONTEXT-GUIDE.md ([#58](https://github.com/gsa-tts/agentic-coding-playbook/issues/58)) ([caba7de](https://github.com/gsa-tts/agentic-coding-playbook/commit/caba7de79cc5d5a5c2a293f9b83148d1219163d0))
* make project-bootstrap skill portable and idempotent ([e7df042](https://github.com/gsa-tts/agentic-coding-playbook/commit/e7df042f69644ca62c4ba104d17f1bad85cfaaa1))
* replace markdownlint (Node.js) with pymarkdownlnt (Python) ([4a1acff](https://github.com/gsa-tts/agentic-coding-playbook/commit/4a1acff87b69b9822dbaf823efb39fcf7ff8f35d))
* standardize skill schema + add contributor templates and recipes ([a96a842](https://github.com/gsa-tts/agentic-coding-playbook/commit/a96a842fa580fe4352152b0117ca29f3113ad0f5))


### Bug Fixes

* documentation accuracy — version strings, claims, contributor guide ([1a7f8ba](https://github.com/gsa-tts/agentic-coding-playbook/commit/1a7f8bad1e0cfc387eef76b8e5cc37838796d095))
* remove all stale bash script references from docs ([1b36c6f](https://github.com/gsa-tts/agentic-coding-playbook/commit/1b36c6fd9f2f7e7b3585b2d206f5fff7effd6e53))
* repair broken sed replacements in skill SKILL.md files ([7c0f64c](https://github.com/gsa-tts/agentic-coding-playbook/commit/7c0f64c1f554f0e10e6c9892585651235de37940))
* skill audit fixes — schema, counts, stale references ([3319d61](https://github.com/gsa-tts/agentic-coding-playbook/commit/3319d610594baf9e12fff76ae8bb0f00f7624903))
* sync all docs with current state — counts, skills, subcommands ([15bcccf](https://github.com/gsa-tts/agentic-coding-playbook/commit/15bcccf624551f940b6d07ccc0cfd88402819675))
* update CONTEXT-GUIDE.md word counts + add missing docs ([a2aec39](https://github.com/gsa-tts/agentic-coding-playbook/commit/a2aec39f4054c8fa8ebb5fc7a051be8bcd2fda10))
* update repo references for gsa-tts/agentic-ai-playbook ([93c148c](https://github.com/gsa-tts/agentic-coding-playbook/commit/93c148c3ca3e24400d5c92baa5b3073705bec22d))


### Documentation

* expand release process documentation in CONTRIBUTING.md ([e18c636](https://github.com/gsa-tts/agentic-coding-playbook/commit/e18c636b736c7ac68ca73b4bc4d68f54db6870d9))
* rewrite README for better onboarding UX/DX ([ad8d55e](https://github.com/gsa-tts/agentic-coding-playbook/commit/ad8d55ea7ade9cdb0921487a03eef3c7f1c8f0b6))


### Refactoring

* auto-generate skill tables + delete llms.txt (DRY) ([66c35b0](https://github.com/gsa-tts/agentic-coding-playbook/commit/66c35b0715a68b41f11f010a31a7d121813ed62d))
* complete bash-to-Python migration — zero shell scripts remain ([21b9438](https://github.com/gsa-tts/agentic-coding-playbook/commit/21b9438db1693c95b2de5157b0304fce3e3f62f1))
* complete Python migration — remove last bash validator ([ded8825](https://github.com/gsa-tts/agentic-coding-playbook/commit/ded88257bdcee961cea226149d56a6a9cfbe65be))
* project-bootstrap delegates to federal-repo-setup ([#53](https://github.com/gsa-tts/agentic-coding-playbook/issues/53)) ([84fc7c3](https://github.com/gsa-tts/agentic-coding-playbook/commit/84fc7c31743396e22e5b9a0d28f11e7f01e1b40a))
* remove dead agent-doctor.sh + update doc references ([4f858d9](https://github.com/gsa-tts/agentic-coding-playbook/commit/4f858d91a31d1fb4ae26780585a2d54265b9893e))


### CI/CD

* trigger release-please after enabling PR permissions ([14a80e7](https://github.com/gsa-tts/agentic-coding-playbook/commit/14a80e7778d13c987e22d327c7eb6e895bc5156a))

## [0.3.0] - 2026-02-26

### Added

- **LLM context optimization — progressive disclosure architecture**:
  - `CONTEXT-GUIDE.md` — compact agent entry point (~500 words) with tiered loading instructions, keyword triggers, and typical task profiles
  - `load_priority` frontmatter field on all 11 content documents: `always`, `task-context`, `on-demand`, `reference-only`
  - `<!-- LOAD: ... -->` HTML comment directives after frontmatter in every document
  - `load_priority_values` in INDEX.yaml schema and `DOC_LOAD_PRIORITY_VALUES`/`DOC_LOAD_PRIORITY_REGEX` in `scripts/config.sh`
  - `load_priority` validation in `scripts/validate-docs.sh`
  - `load_priority` field emitted in INDEX.yaml document entries via `scripts/generate-index.sh`
- **Quick Reference sections** at the top of 5 core docs (AGENTS.md, docs/CODING_PRACTICES.md, SECURITY-CONTROLS.md, AGENT-IDENTITY.md, GETTING-STARTED.md) — actionable summaries in table format for LLM-efficient scanning

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

- **Engineering discipline sections in docs/CODING_PRACTICES.md** — 3 new sections (§11-§13):
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
  - `federal-pre-deployment-check` — Automated + manual execution of the 58-item pre-deployment checklist (+ check runner and report generator)
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
- docs/CODING_PRACTICES.md — secure coding standards for AI-assisted development (10 sections)
- docs/GETTING-STARTED.md — repository setup, tooling, and environment hardening
- docs/SECURITY-CONTROLS.md — NIST 800-53 control overlay (37 controls, 10 families)
- docs/AGENT-IDENTITY.md — agent identity, authentication, and delegation guidance
- docs/TRACEABILITY.md — bidirectional control-to-document traceability matrix
- templates/AGENTS.md.template — copy-paste agent rules for new projects
- templates/risk-assessment.md — AI risk assessment worksheet (AI RMF aligned)
- checklists/pre-deployment.md — 58-item pre-deployment security checklist
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
