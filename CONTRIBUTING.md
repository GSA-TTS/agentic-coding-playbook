# Contributing

Thanks for helping improve the Federal Agentic AI Playbook.

This repository is designed to be **self-validating and low-friction**, so contributors can focus on content—not tooling.

---

## Quick Start

```bash
make bootstrap
make fix
make verify
````

* `make bootstrap` — installs hooks and prepares your environment
* `make fix` — regenerates derived content and runs local checks (may modify files)
* `make verify` — runs full validation locally (the same validation flow contributors should run before pushing)

> If hooks or generators modify files during commit, stage the changes and run `git commit` again. This is expected.

---

## How to Contribute

1. **Open an issue** describing the improvement, gap, or correction
2. **Reference relevant standards** (NIST, OMB, CISA, OWASP, etc.) where applicable
3. **Create a feature branch** and make your changes
4. **Run `make fix` and `make verify` locally**
5. **Submit a pull request** with a clear explanation of what changed and why

---

## Contribution Guidelines

### Content Standards

* Cite authoritative sources (NIST, OMB, CISA, OWASP) where recommendations are made
* Keep content **tool-agnostic** — no vendor or product endorsements
* Use **plain language** — not all readers are NIST specialists
* Provide **actionable examples**, not just theory
* Include **control mappings** where relevant (e.g., NIST SP 800-53)

### What We Need

* Practitioner feedback (what works / what doesn’t)
* Missing controls, patterns, or scenarios
* Clarity improvements (simplify language where possible)
* Template improvements for real-world use
* Updates aligned to new or revised standards

### What We Don’t Accept

* Vendor-specific recommendations
* Classified or CUI content
* Guidance that contradicts authoritative sources without justification
* Speculative or unsupported recommendations

---

## Generated Content (Important)

This repository intentionally generates some files:

* `INDEX.yaml`
* README sections (structure, skills table, changelog summary)

These are maintained by scripts and hooks.

Do not manually edit generated sections. Instead:

```bash
make fix
```

If validation fails:

```bash
make verify
```

---

## Exporting an Agent Bundle

The repository can export a portable agent bundle into another repository or into a standalone output directory.

Preview an export first:

```bash
make export-dry-run EXPORT_TARGET=../my-repo
```

Export into another repository:

```bash
make export EXPORT_TARGET=../my-repo EXPORT_OVERWRITE=true
```

Export all available bundled skills:

```bash
make export EXPORT_TARGET=../my-repo EXPORT_PROFILE=all EXPORT_OVERWRITE=true
```

To see available skills:

```bash
bash scripts/export-agent-bundle.sh --list-skills
```

---

## Contributing Agent Skills

Skills are executable procedures located in `skills/`.

They convert reference material into **step-by-step workflows**.

### Skill Structure

```text
skills/your-skill-name/
├── SKILL.md
├── scripts/ (optional)
└── references/ (optional)
```

### Skill Requirements

1. `SKILL.md` must include frontmatter with:

   * `name`
   * `description`

2. `name` must:

   * match the directory name
   * use lowercase and hyphens only
   * be ≤ 64 characters

3. `SKILL.md` must be under 500 lines

4. Do not duplicate policy — reference documents by path/section

5. Scripts must be:

   * read-only or generative
   * deterministic (no hidden side effects)
   * no package installs or network calls

6. Script output must be structured JSON:

```json
{
  "status": "success | failure | partial",
  "results": [],
  "warnings": [],
  "errors": []
}
```

1. No unsafe execution patterns (`eval`, `exec`, etc.) unless there is a tightly scoped, justified compatibility need and the input is fully controlled

2. All scripts must pass validation:

   * Bash → ShellCheck
   * Python → `py_compile`

### Validation

Run locally:

```bash
make fix
make verify
```

CI will enforce the same checks.

---

## Review Process

* All pull requests require review by a maintainer
* Changes affecting control mappings or security posture receive additional scrutiny

---

## Maintainers: Releases

Release-related make targets exist for maintainers, but they are intentionally not shown in the default `make` help output.

### Release readiness

Before cutting a release:

1. move the current top changelog entry from `[Unreleased]` to a versioned heading
2. run release checks

```bash
make release-check
```

This will:

* run the full local verification flow
* fail if the top changelog entry is still `[Unreleased]`

### Create a release tag

After the changelog is versioned and committed:

```bash
make release-tag VERSION=v0.3.3
git push origin v0.3.3
```

This will:

* verify the working tree is clean
* verify the tag does not already exist
* verify the top changelog entry matches the requested version
* create an annotated tag locally

Pushing the tag triggers the GitHub release workflow.

---

## Code of Conduct

Be constructive, direct, and respectful.

This repository is used by federal practitioners—clarity and accuracy matter more than speed.
