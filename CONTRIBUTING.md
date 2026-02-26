# Contributing

Thank you for your interest in improving federal agentic AI guidance. This project benefits from input by practitioners across agencies.

## How to Contribute

1. **Open an issue** describing the improvement, gap, or correction
2. **Reference the specific NIST control or framework section** that applies
3. **Fork the repo** and make your changes on a feature branch
4. **Submit a pull request** with a clear description of what changed and why

## Contribution Guidelines

### Content Standards

- **Every recommendation must cite an authoritative source** (NIST publication, OMB memo, CISA guidance, or OWASP standard)
- **Keep guidance tool-agnostic** — never recommend a specific vendor or product
- **Use plain language** — the audience includes federal employees who may not be NIST specialists
- **Provide actionable examples** — show what to do, not just what the standard says
- **Include control mappings** — every section should reference applicable NIST 800-53 controls

### What We Need

- **Practitioner feedback** — Does this guidance work in your agency's environment?
- **Gap identification** — What security controls or scenarios are missing?
- **Plain language improvements** — Where is the guidance unclear or too technical?
- **Template refinements** — Are the templates practical for real ATO packages?
- **Framework updates** — Has a referenced NIST publication been updated?

### What We Don't Accept

- Vendor-specific recommendations or product placements
- Classified or CUI content
- Content that contradicts published NIST guidance without clear justification
- Speculative recommendations not grounded in authoritative sources

## Contributing Agent Skills

Skills are executable procedures in [Agent Skills format](https://agentskills.io) that live in `skills/`. They convert policy guidance into step-by-step workflows agents can follow.

### Skill Structure

```
skills/your-skill-name/
├── SKILL.md              # Required — frontmatter + instructions (<500 lines)
├── scripts/              # Optional — executable code (Bash or Python 3.10+)
│   └── your-script.sh
└── references/           # Optional — supporting documentation
    └── YOUR_REF.md
```

### Skill Requirements

1. **SKILL.md frontmatter** must include `name` and `description` per the [Agent Skills spec](https://agentskills.io/specification)
2. **`name` must match the directory name** — lowercase, hyphens only, max 64 characters
3. **SKILL.md must be under 500 lines** — move detailed reference material to `references/`
4. **No policy duplication** — reference policy docs by path and section (e.g., `docs/GETTING-STARTED.md Section 4`)
5. **Scripts must be read-only or generative** — never modify git state, install packages, or make network calls
6. **Scripts must output structured JSON** — `{"status": "success|failure|partial", "results": [...], "warnings": [...], "errors": [...]}`
7. **No eval/exec** in scripts — validate file paths with `realpath` + prefix check
8. **All Bash scripts must pass ShellCheck** — CI enforces this
9. **All Python scripts must pass `py_compile`** — CI enforces this
10. **Run `bash scripts/generate-index.sh`** to regenerate INDEX.yaml with the new skill

### Validation

Run `bash scripts/validate-skills.sh` locally before submitting a PR. CI runs this automatically.

## Review Process

All pull requests require review by at least one maintainer. Changes to security controls mapping or compliance guidance require additional scrutiny.

## Code of Conduct

Be professional, constructive, and respectful. This is guidance that federal employees will rely on — quality and accuracy matter more than speed.
