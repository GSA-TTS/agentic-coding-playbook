## Summary

<!-- Brief description of changes. Reference the issue number if applicable: Closes #XX -->

## Type of Change

- [ ] Bug fix (incorrect playbook, broken links, wrong control mappings)
- [ ] New content (new document, template, or checklist)
- [ ] Content update (updated playbook, new framework version alignment)
- [ ] Infrastructure (CI, tooling, repository configuration)

## Pre-Merge Checklist

### Required for All Changes

- [ ] Changes are accurate and cite authoritative sources
- [ ] No typos or formatting issues
- [ ] Commit messages follow conventional commits (`feat:`, `fix:`, `docs:`)

### Required for Content Changes

- [ ] YAML frontmatter present with required fields (`title`, `description`, `status`, `tier`)
- [ ] INDEX.yaml updated if adding/removing/renaming documents
- [ ] Cross-references (`related_files` in frontmatter) point to existing files
- [ ] NIST control mappings verified against SP 800-53 Rev 5.2
- [ ] OWASP cross-references verified (LLM Top 10 and/or Agentic Top 10)
- [ ] CHANGELOG.md updated under `[Unreleased]`

### Required for New Documents

- [ ] Document listed in INDEX.yaml with correct metadata
- [ ] README.md file tree updated
- [ ] Tier assignment justified (1=core, 2=how-to, 3=supporting)
- [ ] At least one cross-reference to existing documents

## Notes for Reviewers

<!-- Any additional context that would help reviewers. -->
