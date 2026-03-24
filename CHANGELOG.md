# Changelog

All notable changes to this playbook are documented in this file.

This project follows [Semantic Versioning](https://semver.org/). Framework alignment versions are tracked inline within individual documents.

## [Unreleased]

### Added

- Portable agent bundle export workflow for local-first and sandboxed agent use
- `scripts/export-agent-bundle.sh` to generate deterministic offline-safe exports
- compact exported `.agent-skills/docs/CODING-PRACTICES.md` companion for coding tasks in local and sandboxed agent environments
- `make export-dry-run` to preview bundle exports without writing files
- `make doctor` to check local tooling and script readiness
- hidden maintainer targets `make release-check` and `make release-tag` for release operations without polluting the default contributor UX
- maintainer release guidance in `CONTRIBUTING.md`

### Changed

- `make verify` is now the primary local validation command, replacing contributor-facing references to `make check`
- export workflow UX simplified around `EXPORT_TARGET` as the primary way to populate another repository
- `make export` help output tightened around the most common copy-paste examples
- README, CONTRIBUTING, and setup guidance updated to align with the current command surface and file locations
- README wording refined to reinforce that this repository is reference material and implementation patterns, not official guidance or policy
- release process clarified around explicit readiness checks, versioned changelog entries, annotated tags, and tag-push driven GitHub releases
- release notes generation uses safer Python-based document table parsing instead of brittle shell-only parsing

### Fixed

- macOS bash compatibility in `scripts/export-agent-bundle.sh` by removing unsupported bash nameref usage
- stale path references to `CODING_PRACTICES.md` after the move to `docs/CODING-PRACTICES.md`
- contributor and maintainer command drift across repo documentation
- reduced ambiguity in repository language where “playbook,” “guidance,” and “reference material” could otherwise be conflated
- improved release note generation resilience when `INDEX.yaml` formatting changes
- improved operator safety around release tagging by adding local cleanliness and duplicate-tag checks

## [0.3.2] - 2026-03-23

### Changed

- Repository migrated from **cloud-gov** to **GSA-TTS**
- Repository renamed from **federal-agentic-ai-guidance** to **agentic-ai-playbook** to better reflect its non-authoritative, reference-oriented positioning
- Documentation updated to align with the new repository name, structure, and positioning as non-binding reference material
- Language refined across the repository to reduce ambiguity between policy, guidance, and reference content
- README updated with a 5-minute quick start, badges, stronger non-binding framing, and clearer generated-content markers
- Generated-content synchronization split into dedicated scripts for `INDEX.yaml`, the README repository structure block, the README skills table, and the README changelog summary
- README repository structure moved from a manually maintained tree to a generated block sourced from the current filesystem
- CI and pre-commit updated to validate all generated README content through the shared sync script
- Contributor guidance now explicitly notes that a commit may need to be run more than once when generated content is refreshed during pre-commit

### Fixed

- Regenerated `INDEX.yaml` to reflect current repository structure and content

## [0.3.1] - 2026-02-26

### Fixed

- `scripts/lib/common.sh` — replaced `head -n -1` with `sed '$ d'` for macOS/BSD compatibility (GNU-specific syntax caused failures)
- `scripts/validate-docs.sh` — applied same fix for frontmatter extraction (2 locations)
- `scripts/validate-skills.sh` — applied same fix for frontmatter extraction
- `INDEX.yaml` — regenerated with corrected frontmatter parsing (47 unique NIST controls, 14 frameworks)

### Changed

- `README.md` — added Claude Code to supported AI coding agents

## [0.3.0] - 2026-02-26

### Added

- **LLM context optimization (progressive disclosure architecture):**
  - `CONTEXT-GUIDE.md` — agent entry point with tiered loading instructions and task-based triggers
  - `load_priority` frontmatter field (`always`, `task-context`, `on-demand`, `reference-only`)
  - HTML `<!-- LOAD: ... -->` directives in all content documents
  - Schema + validation support in `scripts/config.sh`, `validate-docs.sh`, and `generate-index.sh`
  - INDEX.yaml now includes `load_priority` metadata

- **Quick Reference sections** in core documents for efficient LLM scanning

### Changed

- AGENTS.md — replaced inline NIST control matrix with reference to `docs/TRACEABILITY.md`
- README.md — updated agent workflow to use `CONTEXT-GUIDE.md` as entry point
- INDEX.yaml — expanded schema to include `load_priority`

### Token Impact

| Scenario | Tokens | Reduction |
|----------|--------|-----------|
| Full load | ~58K | baseline |
| Typical code task | ~12K | -80% |
| Security assessment | ~21K | -64% |
| Full audit | ~38K | -35% |

## [0.2.2] - 2026-02-25

### Added

- `examples/AGENTS.md.example` — expanded with Agent Meta-Constraints and Engineering Discipline sections
- `docs/TRACEABILITY.md` — extended control mappings (+4 new controls, updates to 8 existing controls)
- Updated AI RMF mappings (GOVERN 1, MANAGE 1, MEASURE 2)

### Fixed

- `scripts/validate-docs.sh` — replaced unsafe word-splitting with NUL-delimited handling for filenames

## [0.2.1] - 2026-02-25

### Added

- Centralized configuration and shared script library:
  - `scripts/config.sh` — schema constants and validation rules
  - `scripts/lib/common.sh` — shared parsing and JSON helpers

### Changed

- All scripts refactored to use shared config and helpers (DRY enforcement)
- CI updated to support cross-file sourcing (`shellcheck -x`)
- Validation scripts now reference centralized schema definitions

## [0.2.0] - 2026-02-25

### Added

- Engineering discipline sections in `CODING_PRACTICES.md` (architecture, testing, maintainability)
- Agent meta-constraints in `AGENTS.md` (planning, PR discipline, verification loops)
- Agent Skills execution layer (6 skills, cross-platform compatible)
- `scripts/validate-skills.sh` and CI integration
- Deterministic `INDEX.yaml` generation (`generate-index.sh`)
- Cross-validation between filesystem and INDEX.yaml
- Expanded README and CONTRIBUTING guidance
- Reference materials supporting skills

### Fixed

- INDEX.yaml metadata accuracy (control counts, framework counts)
- Documentation inconsistencies in control coverage and version tracking

### Changed

- CI expanded to validate skill scripts
- Validation scope clarified between docs and skills
- Repository structure updated to reflect skills architecture

## [0.1.1] - 2026-02-25

### Added

- SECURITY.md (responsible disclosure)
- Issue and PR templates
- Dependabot configuration
- ShellCheck integration in CI

### Fixed

- CI pipeline issues (markdownlint, link checker, frontmatter validation)
- Validation edge cases (long YAML arrays, private links)

### Changed

- Updated GitHub Actions versions via Dependabot

## [0.1.0] - 2026-02-25

### Added

- Initial repository structure and core documentation
- AGENTS.md, docs/CODING_PRACTICES.md, and supporting docs/templates/checklists
- INDEX.yaml with schema and frontmatter validation
- GitHub Actions CI pipeline and release workflow

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
