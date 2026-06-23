# Changelog

All notable changes to this playbook will be documented in this file.

This project uses [Semantic Versioning](https://semver.org/). Framework alignment versions are tracked inline in each document.

## [0.11.4](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.11.3...v0.11.4) (2026-06-22)


### Documentation

* add missing docs to index; correct control count to 35 ([#123](https://github.com/GSA-TTS/agentic-coding-playbook/issues/123)) ([b6a85de](https://github.com/GSA-TTS/agentic-coding-playbook/commit/b6a85de7942b5a958c833088da590f2b6f3ac71d))


### Maintenance

* remove redundant root CODEOWNERS; consolidate to .github/CODEOWNERS ([#125](https://github.com/GSA-TTS/agentic-coding-playbook/issues/125)) ([2782868](https://github.com/GSA-TTS/agentic-coding-playbook/commit/27828686d39f912c524aa145c8cc0dc1f2851941))

## [0.11.3](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.11.2...v0.11.3) (2026-06-22)


### Maintenance

* **deps:** bump pytest from 9.0.3 to 9.1.0 ([#115](https://github.com/GSA-TTS/agentic-coding-playbook/issues/115)) ([c351875](https://github.com/GSA-TTS/agentic-coding-playbook/commit/c351875e81fa107718d006873e4cefa605873ec7))
* **deps:** bump ruff from 0.15.16 to 0.15.17 ([#119](https://github.com/GSA-TTS/agentic-coding-playbook/issues/119)) ([7d47db8](https://github.com/GSA-TTS/agentic-coding-playbook/commit/7d47db86ec39b49573772f4b4ce18e193695313e))
* **deps:** pin js-yaml 4.2.0 + markdown-it 14.2.0 in linters; add npm dependabot coverage ([#117](https://github.com/GSA-TTS/agentic-coding-playbook/issues/117)) ([0fdf9dd](https://github.com/GSA-TTS/agentic-coding-playbook/commit/0fdf9ddfc45b20ed09d3eeece482dff6d27a0271))

## [0.11.2](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.11.1...v0.11.2) (2026-06-17)


### Documentation

* **security:** remove secret literals from credential examples ([#113](https://github.com/GSA-TTS/agentic-coding-playbook/issues/113)) ([f06ed5c](https://github.com/GSA-TTS/agentic-coding-playbook/commit/f06ed5c1d0baabe6b218de94d09c82299d167084))

## [0.11.1](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.11.0...v0.11.1) (2026-06-12)


### Documentation

* codify PR-title Action as commit-validation standard + squash-merge preference ([#109](https://github.com/GSA-TTS/agentic-coding-playbook/issues/109)) ([aaf68b3](https://github.com/GSA-TTS/agentic-coding-playbook/commit/aaf68b3768126674acbd517a6526b98286d3c016)), closes [#108](https://github.com/GSA-TTS/agentic-coding-playbook/issues/108)
* fix accuracy issues from cross-repo docs review ([#111](https://github.com/GSA-TTS/agentic-coding-playbook/issues/111)) ([9aa432f](https://github.com/GSA-TTS/agentic-coding-playbook/commit/9aa432f7fdd963517ed4702802720746a3f92b8f))

## [0.11.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.5...v0.11.0) (2026-06-10)


### Features

* **coding-practices:** add version control and release management section ([#94](https://github.com/GSA-TTS/agentic-coding-playbook/issues/94)) ([9e43d8e](https://github.com/GSA-TTS/agentic-coding-playbook/commit/9e43d8e779f34168b05586853bb27f880169ae2d))


### Bug Fixes

* **ci:** upgrade pip before pip-audit to avoid PYSEC-2026-196 ([#100](https://github.com/GSA-TTS/agentic-coding-playbook/issues/100)) ([345dcbe](https://github.com/GSA-TTS/agentic-coding-playbook/commit/345dcbe6a4bd002178e4d11e01cf77f870c8b02b))


### Documentation

* remove WORKFLOW_CONTRACT.md (documented deleted reusable workflows) ([#106](https://github.com/GSA-TTS/agentic-coding-playbook/issues/106)) ([d2fe567](https://github.com/GSA-TTS/agentic-coding-playbook/commit/d2fe5677d32d0d4ff96349f753d9c828d23a7444)), closes [#102](https://github.com/GSA-TTS/agentic-coding-playbook/issues/102)


### Maintenance

* **ci:** add zizmor CI workflow, drop brittle local hook ([#103](https://github.com/GSA-TTS/agentic-coding-playbook/issues/103)) ([#104](https://github.com/GSA-TTS/agentic-coding-playbook/issues/104)) ([b3d82e0](https://github.com/GSA-TTS/agentic-coding-playbook/commit/b3d82e07a16389dc1e7a2a43c0b0f95535b2e373))
* **ci:** remove reusable workflows ([#99](https://github.com/GSA-TTS/agentic-coding-playbook/issues/99)) ([38a5ae9](https://github.com/GSA-TTS/agentic-coding-playbook/commit/38a5ae94417dcb3f8628b17e163efc94db508449))
* **ci:** use lockfile for markdownlint supply chain security ([#101](https://github.com/GSA-TTS/agentic-coding-playbook/issues/101)) ([3d3dce6](https://github.com/GSA-TTS/agentic-coding-playbook/commit/3d3dce66571dbe2759340f9375bf3a10cf396921))
* **deps:** bump actions/checkout from 6.0.2 to 6.0.3 ([#97](https://github.com/GSA-TTS/agentic-coding-playbook/issues/97)) ([aa5f617](https://github.com/GSA-TTS/agentic-coding-playbook/commit/aa5f617b233fd656015925b2d65bf78def0297ef))
* **deps:** bump actions/setup-node from 4.4.0 to 6.4.0 ([#105](https://github.com/GSA-TTS/agentic-coding-playbook/issues/105)) ([f8328b4](https://github.com/GSA-TTS/agentic-coding-playbook/commit/f8328b4aeaf949e4ca752f4a591c7332ff8a0aa1))
* **deps:** bump ruff from 0.15.15 to 0.15.16 ([#98](https://github.com/GSA-TTS/agentic-coding-playbook/issues/98)) ([570ffa9](https://github.com/GSA-TTS/agentic-coding-playbook/commit/570ffa9dd31072667324b1fc0ebe36e2be8acb52))


### Tests

* add coverage for skill scripts; refactor generate_agents_md ([#84](https://github.com/GSA-TTS/agentic-coding-playbook/issues/84)) ([#107](https://github.com/GSA-TTS/agentic-coding-playbook/issues/107)) ([d8c0208](https://github.com/GSA-TTS/agentic-coding-playbook/commit/d8c0208d3fc117de1eb83780453f3c65c5ecff5b))
* **rss:** add test coverage for landscape RSS scripts ([#95](https://github.com/GSA-TTS/agentic-coding-playbook/issues/95)) ([bd9a884](https://github.com/GSA-TTS/agentic-coding-playbook/commit/bd9a88482eb63d7e930ab9fb410d6307e943cd98))

## [0.10.5](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.4...v0.10.5) (2026-06-02)


### Bug Fixes

* update doctor.py to check markdownlint-cli2 instead of pymarkdown ([#92](https://github.com/GSA-TTS/agentic-coding-playbook/issues/92)) ([750835b](https://github.com/GSA-TTS/agentic-coding-playbook/commit/750835be42e7b5fcc8b4c7073dd237718bbe6373)), closes [#85](https://github.com/GSA-TTS/agentic-coding-playbook/issues/85)


### Documentation

* fix skills count from 11 to 12 ([#90](https://github.com/GSA-TTS/agentic-coding-playbook/issues/90)) ([7166a2e](https://github.com/GSA-TTS/agentic-coding-playbook/commit/7166a2e7b47f8545509ed82880673c5d0cee0ef3))

## [0.10.4](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.3...v0.10.4) (2026-06-01)


### Maintenance

* add gitleaks config and fix code quality issues ([#82](https://github.com/GSA-TTS/agentic-coding-playbook/issues/82)) ([fe936d3](https://github.com/GSA-TTS/agentic-coding-playbook/commit/fe936d36cd32b0c40ec2b72e745cb697f6409efe))

## [0.10.3](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.2...v0.10.3) (2026-05-29)


### Maintenance

* harden workflows and update dependencies ([#80](https://github.com/GSA-TTS/agentic-coding-playbook/issues/80)) ([bc548a7](https://github.com/GSA-TTS/agentic-coding-playbook/commit/bc548a76f2b597b52b001e7e9c9c849e67f0df7b))

## [0.10.2](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.1...v0.10.2) (2026-05-28)


### Documentation

* add WORKFLOW_CONTRACT.md for reusable workflows ([bbd52d7](https://github.com/GSA-TTS/agentic-coding-playbook/commit/bbd52d737c107601d4767a5524ab2ccf8fcc9b3a))
* add WORKFLOW_CONTRACT.md for reusable workflows ([b9842e8](https://github.com/GSA-TTS/agentic-coding-playbook/commit/b9842e85d6f0ac336eb2cac4b46a2f0ade921c77))

## [0.10.1](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.10.0...v0.10.1) (2026-05-28)


### Bug Fixes

* **ci:** correct action-semantic-pull-request SHA ([#74](https://github.com/GSA-TTS/agentic-coding-playbook/issues/74)) ([8c1ee27](https://github.com/GSA-TTS/agentic-coding-playbook/commit/8c1ee272b225552b5d221e9df63ef863038f43e1))
* **ci:** remove GITHUB_TOKEN from release-please workflow secrets ([#75](https://github.com/GSA-TTS/agentic-coding-playbook/issues/75)) ([5c2b636](https://github.com/GSA-TTS/agentic-coding-playbook/commit/5c2b636fe15d1139c17acf0bfce2242d21b3a1b0))
* **ci:** remove GITHUB_TOKEN from reusable workflow secrets ([#72](https://github.com/GSA-TTS/agentic-coding-playbook/issues/72)) ([8754045](https://github.com/GSA-TTS/agentic-coding-playbook/commit/875404507e27a0c5ce2262be7edf10166e548664))
* **ci:** update release-please-action to v4.4.1 with correct SHA ([#76](https://github.com/GSA-TTS/agentic-coding-playbook/issues/76)) ([3f8dfe1](https://github.com/GSA-TTS/agentic-coding-playbook/commit/3f8dfe12e16a1b5d3f5f975bf65ed9c11cc5d0b0))

## [0.10.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.9.0...v0.10.0) (2026-05-28)


### Features

* **skills:** add federal-landscape-update skill for RSS monitoring ([#70](https://github.com/GSA-TTS/agentic-coding-playbook/issues/70)) ([891696e](https://github.com/GSA-TTS/agentic-coding-playbook/commit/891696ec3cff91837e86b4f46da8530d3de57748))

## [0.9.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.8.3...v0.9.0) (2026-05-28)


### Features

* **ci:** add reusable GitHub Actions workflows for ecosystem ([#68](https://github.com/GSA-TTS/agentic-coding-playbook/issues/68)) ([7183464](https://github.com/GSA-TTS/agentic-coding-playbook/commit/7183464d8f75e26967585d3f390afebf16746ae9))


### Maintenance

* add landscape RSS state file to .gitignore ([#69](https://github.com/GSA-TTS/agentic-coding-playbook/issues/69)) ([14eea23](https://github.com/GSA-TTS/agentic-coding-playbook/commit/14eea23eb911796bf12565b9ebe9b4295730ee37))
* disable subject-case rule to allow acronyms ([#66](https://github.com/GSA-TTS/agentic-coding-playbook/issues/66)) ([5d68910](https://github.com/GSA-TTS/agentic-coding-playbook/commit/5d689109c6dab92c80876d602b7c697d0f1ea4f7))

## [0.8.3](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.8.2...v0.8.3) (2026-05-27)


### Maintenance

* **hooks:** add markdownlint and zizmor to pre-commit ([#64](https://github.com/GSA-TTS/agentic-coding-playbook/issues/64)) ([1f0c995](https://github.com/GSA-TTS/agentic-coding-playbook/commit/1f0c9953b4e45f67b0dffe12e6529e55fb695f1b))


### Refactoring

* **tests:** add conftest.py with shared fixtures ([#62](https://github.com/GSA-TTS/agentic-coding-playbook/issues/62)) ([267be30](https://github.com/GSA-TTS/agentic-coding-playbook/commit/267be30d8da1df19a8f970f96a7deb064ab5c7b6)), closes [#60](https://github.com/GSA-TTS/agentic-coding-playbook/issues/60)

## [0.8.2](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.8.1...v0.8.2) (2026-05-27)


### Maintenance

* add CODEOWNERS file for security-sensitive paths ([#58](https://github.com/GSA-TTS/agentic-coding-playbook/issues/58)) ([10fdc6b](https://github.com/GSA-TTS/agentic-coding-playbook/commit/10fdc6b37e5e6f69f296efcb9fc6a2578c067571)), closes [#56](https://github.com/GSA-TTS/agentic-coding-playbook/issues/56)

## [0.8.1](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.8.0...v0.8.1) (2026-05-27)


### Documentation

* add comprehensive Conventional Commits guidance ([#51](https://github.com/GSA-TTS/agentic-coding-playbook/issues/51)) ([c87cbd0](https://github.com/GSA-TTS/agentic-coding-playbook/commit/c87cbd0a49a10c2f2e224c5a1a65690630334cfd)), closes [#50](https://github.com/GSA-TTS/agentic-coding-playbook/issues/50)

## [0.8.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.7.1...v0.8.0) (2026-05-27)


### Features

* **landscape:** add Phase 1 foundation for automated monitoring ([#49](https://github.com/GSA-TTS/agentic-coding-playbook/issues/49)) ([db6129f](https://github.com/GSA-TTS/agentic-coding-playbook/commit/db6129fa84cd5667ce14302b5e94ad1ac17520b7))


### Bug Fixes

* **skills:** correct CODING_PRACTICES.md path in federal-repo-setup ([#47](https://github.com/GSA-TTS/agentic-coding-playbook/issues/47)) ([dadb4cf](https://github.com/GSA-TTS/agentic-coding-playbook/commit/dadb4cf2f251168893a773d4f5d12807959776f8)), closes [#45](https://github.com/GSA-TTS/agentic-coding-playbook/issues/45)

## [0.7.1](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.7.0...v0.7.1) (2026-05-26)


### Maintenance

* **ci:** make pre-commit hooks opt-in ([#43](https://github.com/GSA-TTS/agentic-coding-playbook/issues/43)) ([ba2e451](https://github.com/GSA-TTS/agentic-coding-playbook/commit/ba2e45121f748922fdce3208a2097183fef70815)), closes [#42](https://github.com/GSA-TTS/agentic-coding-playbook/issues/42)
* remove vestigial root CODEOWNERS file ([405d8f7](https://github.com/GSA-TTS/agentic-coding-playbook/commit/405d8f714d15e8432aae28319b5c819bbeed398c))

## [0.7.0](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.6...v0.7.0) (2026-05-26)


### Features

* **ci:** Add workflow_dispatch trigger for manual CI runs ([ce831eb](https://github.com/GSA-TTS/agentic-coding-playbook/commit/ce831eb4c4dfb31c3285196ea6f268d4c65756cf))


### Documentation

* improve ecosystem documentation and contribution experience ([#37](https://github.com/GSA-TTS/agentic-coding-playbook/issues/37)) ([63f97d2](https://github.com/GSA-TTS/agentic-coding-playbook/commit/63f97d2279187792cb881c1c777fa3d82983666d))


### Maintenance

* add CODEOWNERS file ([#40](https://github.com/GSA-TTS/agentic-coding-playbook/issues/40)) ([963c9e7](https://github.com/GSA-TTS/agentic-coding-playbook/commit/963c9e75b4e98b38f70c8bf481798e3b1864c924))
* **ci:** add commitlint configuration ([#41](https://github.com/GSA-TTS/agentic-coding-playbook/issues/41)) ([1db6fcb](https://github.com/GSA-TTS/agentic-coding-playbook/commit/1db6fcb687f8bba14bf9348531b72dd33e70a554))
* **deps:** bump ruff from 0.15.13 to 0.15.14 ([#38](https://github.com/GSA-TTS/agentic-coding-playbook/issues/38)) ([bc12bfb](https://github.com/GSA-TTS/agentic-coding-playbook/commit/bc12bfb48e7321f42d765a81ba70118e5195b308))

## [0.6.6](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.5...v0.6.6) (2026-05-21)


### Bug Fixes

* **ci:** remove sarif upload until code security is enabled ([b667f89](https://github.com/GSA-TTS/agentic-coding-playbook/commit/b667f89f349803893a3207408b9c4b3b7787bb4d))
* **ci:** use semgrep action and add actions:read permission ([487daac](https://github.com/GSA-TTS/agentic-coding-playbook/commit/487daac170c49ace919687840c27a70f13b5478f))
* **ci:** use semgrep ce container instead of deprecated action ([323fec0](https://github.com/GSA-TTS/agentic-coding-playbook/commit/323fec0a85f6ad2f673882fb55dfa97beb2d26b6))


### Maintenance

* **ci:** upgrade python to 3.13 for active bugfix support ([f9dec0c](https://github.com/GSA-TTS/agentic-coding-playbook/commit/f9dec0cad232cb61087f7384c2d89297148c17f8))
* **deps:** bump googleapis/release-please-action from 4.4.1 to 5.0.0 ([#23](https://github.com/GSA-TTS/agentic-coding-playbook/issues/23)) ([4a9dbae](https://github.com/GSA-TTS/agentic-coding-playbook/commit/4a9dbae8ece6e546e32c81aac80c40ade2834119))
* **deps:** bump ruff from 0.15.12 to 0.15.13 ([#32](https://github.com/GSA-TTS/agentic-coding-playbook/issues/32)) ([c121fc2](https://github.com/GSA-TTS/agentic-coding-playbook/commit/c121fc28ae9b3ef45f210e061c7a6e7babd98c8d))


### CI/CD

* **security:** add semgrep sast scanning to ci pipeline ([0871963](https://github.com/GSA-TTS/agentic-coding-playbook/commit/08719631d751d88e604b5389e3831ce90666f11a))
* **security:** add semgrep sast scanning to ci pipeline ([0333e01](https://github.com/GSA-TTS/agentic-coding-playbook/commit/0333e01635b04fde63ba29928d54386b87645d93))

## [0.6.5](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.4...v0.6.5) (2026-04-28)


### Bug Fixes

* **ci:** ignore CVE-2026-3219 in pip during vulnerability scan ([95457f2](https://github.com/GSA-TTS/agentic-coding-playbook/commit/95457f2cea991c051a052e06e5cb5d6b61cf9bf5))


### Maintenance

* **deps:** bump pre-commit from 4.5.1 to 4.6.0 ([#25](https://github.com/GSA-TTS/agentic-coding-playbook/issues/25)) ([4d1a332](https://github.com/GSA-TTS/agentic-coding-playbook/commit/4d1a332635212e26697bc21a7a1efe7dc6e4ba1b))
* **deps:** bump ruff from 0.15.11 to 0.15.12 ([#24](https://github.com/GSA-TTS/agentic-coding-playbook/issues/24)) ([680e025](https://github.com/GSA-TTS/agentic-coding-playbook/commit/680e025e6492302b834602143a77ece5844d04ec))

## [0.6.4](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.3...v0.6.4) (2026-04-20)


### Maintenance

* **deps:** bump actions/setup-node from 4.4.0 to 6.4.0 ([#19](https://github.com/GSA-TTS/agentic-coding-playbook/issues/19)) ([b250656](https://github.com/GSA-TTS/agentic-coding-playbook/commit/b250656c2712fe8b9cbb7bad1c65028232d9ebf1))
* **deps:** bump ruff from 0.15.9 to 0.15.11 ([#20](https://github.com/GSA-TTS/agentic-coding-playbook/issues/20)) ([33edb27](https://github.com/GSA-TTS/agentic-coding-playbook/commit/33edb2783647332d48b9908bfc0e731e4f7aa51a))

## [0.6.3](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.2...v0.6.3) (2026-04-20)


### Maintenance

* **deps:** bump googleapis/release-please-action from 4.4.0 to 4.4.1 ([#18](https://github.com/GSA-TTS/agentic-coding-playbook/issues/18)) ([dede825](https://github.com/GSA-TTS/agentic-coding-playbook/commit/dede825beb454a72f0fa57371c9794f50c26c5f8))

## [0.6.2](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.1...v0.6.2) (2026-04-14)


### Bug Fixes

* **deps:** upgrade pytest to 9.0.3 for CVE-2025-71176 ([4849d13](https://github.com/GSA-TTS/agentic-coding-playbook/commit/4849d13ad4a3379dfb4aac68cc54f80bb37c4a9d))


### Documentation

* update ai attribution guidance based on federal research ([7d8b7e9](https://github.com/GSA-TTS/agentic-coding-playbook/commit/7d8b7e9c497bc0d9b804231566d2e39d2c78c794))


### Maintenance

* fix word counts, urls, and enhance gitignore ([9699d31](https://github.com/GSA-TTS/agentic-coding-playbook/commit/9699d311e3be82d44f2e2e4929ed5c78035e8e93))


### Tests

* unlock GPG cache ([da48a80](https://github.com/GSA-TTS/agentic-coding-playbook/commit/da48a80bdadf8438504afa938c3b50ad58517708))

## [0.6.1](https://github.com/GSA-TTS/agentic-coding-playbook/compare/v0.6.0...v0.6.1) (2026-04-09)


### Maintenance

* reset version to 0.6.0 after tag cleanup ([8d834e6](https://github.com/GSA-TTS/agentic-coding-playbook/commit/8d834e69b5cf23fdf1203273da3d5ecff7e36a8d))

## [0.6.0](https://github.com/gsa-tts/agentic-coding-playbook/compare/v0.5.1...v0.6.0) (2026-04-09)


### Features

* add dependency lock files and pip-audit SCA scanning ([#85](https://github.com/gsa-tts/agentic-coding-playbook/issues/85)) ([bdd0b3f](https://github.com/gsa-tts/agentic-coding-playbook/commit/bdd0b3f70be174a4a0738e9b95fe4fa498bf66b8))
* CI hardening, Makefile targets, pyproject.toml checker ([#89](https://github.com/gsa-tts/agentic-coding-playbook/issues/89)) ([2eb18db](https://github.com/gsa-tts/agentic-coding-playbook/commit/2eb18db6bda27cc0d4e31b2106a4eff7b1904731))
* harden CLI, doctor, CI, refactor, add 23 tests ([#80](https://github.com/gsa-tts/agentic-coding-playbook/issues/80)) ([d7c7067](https://github.com/gsa-tts/agentic-coding-playbook/commit/d7c7067474c097a4dc3fc2cc545a4572ccc967d5))

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
