# Changelog

All notable changes to this playbook are documented in this file.

This project follows [Semantic Versioning](https://semver.org/).
GitHub Releases are generated from labeled pull requests.
This changelog is the curated, long-term record of notable changes.

---

## [Unreleased]

### Added

### Changed

### Fixed

### Documentation

### Internal

## [0.4.0] - 2026-03-24

### Added

- Agent bundle export workflow for local-first and sandboxed agent use
- `scripts/export-agent-bundle.sh` for deterministic, offline-safe exports
- `.agent-skills/docs/CODING-PRACTICES.md` included in exported bundles
- `make export-dry-run` to preview bundle exports without writing files
- `make doctor` to validate local tooling and script readiness

### Changed

- `make verify` is now the primary validation command (replaces `make check`)
- Export workflow standardized around `EXPORT_TARGET`
- `make export` help output streamlined for common usage
- Repository language clarified to reinforce non-authoritative positioning

### Fixed

- macOS compatibility in `scripts/export-agent-bundle.sh` (removed bash-specific features)
- Broken references to `docs/CODING-PRACTICES.md`
- Documentation inconsistencies across contributor workflows

### Documentation

- README, CONTRIBUTING, and setup docs aligned with current command surface
- Maintainer release guidance added to `CONTRIBUTING.md`

### Internal

- Added maintainer-only release targets (`make release-check`, `make release-tag`)
- Formalized release readiness checks and tagging process
- Replaced shell-based release parsing with Python implementation

---

## [0.3.2] - 2026-03-23

### Changed

- Repository migrated from **cloud-gov** to **GSA-TTS**
- Repository renamed to **agentic-ai-playbook**
- Documentation updated to reflect non-authoritative positioning
- README improved with quick start, badges, and clearer structure
- Generated content split into dedicated scripts (INDEX, README sections, changelog)
- CI and pre-commit updated to enforce generated content consistency

### Fixed

- Regenerated `INDEX.yaml` to reflect current repository structure

---

## [0.3.1] - 2026-02-26

### Fixed

- macOS/BSD compatibility in frontmatter parsing (`head -n -1` → `sed '$ d'`)
- Validation scripts updated to use portable parsing logic
- `INDEX.yaml` regenerated with corrected parsing

### Changed

- README updated to include Claude Code support

---

## [0.3.0] - 2026-02-26

### Added

- Progressive disclosure architecture for LLM context optimization:
  - `CONTEXT-GUIDE.md`
  - `load_priority` frontmatter field
  - HTML `<!-- LOAD: ... -->` directives
  - Validation + schema support
- Quick reference sections for efficient LLM scanning

### Changed

- AGENTS.md now references `docs/TRACEABILITY.md` instead of inline mappings
- README updated to use `CONTEXT-GUIDE.md` as entry point
- INDEX.yaml schema expanded with `load_priority`

### Performance Impact

| Scenario | Tokens | Reduction |
|----------|--------|-----------|
| Full load | ~58K | baseline |
| Typical code task | ~12K | -80% |
| Security assessment | ~21K | -64% |
| Full audit | ~38K | -35% |

---

## [0.2.2] - 2026-02-25

### Added

- Expanded agent example (`examples/AGENTS.md.example`)
- Extended `docs/TRACEABILITY.md` control mappings

### Fixed

- Safer filename handling in validation scripts (removed unsafe word-splitting)

---

## [0.2.1] - 2026-02-25

### Added

- Centralized configuration and shared script library:
  - `scripts/config.sh`
  - `scripts/lib/common.sh`

### Changed

- Scripts refactored to use shared config (DRY enforcement)
- CI updated for cross-file sourcing
- Validation logic centralized

---

## [0.2.0] - 2026-02-25

### Added

- Engineering discipline sections in `CODING_PRACTICES.md`
- Agent meta-constraints in `AGENTS.md`
- Agent Skills execution layer
- Skill validation scripts and CI integration
- Deterministic `INDEX.yaml` generation

### Changed

- CI expanded to validate skill scripts
- Repository structure updated for skills architecture

### Fixed

- Metadata accuracy in `INDEX.yaml`
- Documentation inconsistencies in control coverage

---

## [0.1.1] - 2026-02-25

### Added

- SECURITY.md, issue templates, Dependabot config
- ShellCheck integration in CI

### Fixed

- CI pipeline issues and validation edge cases

### Changed

- GitHub Actions updated via Dependabot

---

## [0.1.0] - 2026-02-25

### Added

- Initial repository structure and documentation
- AGENTS.md, CODING_PRACTICES.md, templates, and checklists
- INDEX.yaml with validation
- CI pipeline and release workflow

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
