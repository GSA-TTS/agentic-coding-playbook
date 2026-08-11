# Accessibility Statement

The Agentic Coding Playbook is committed to accessibility as a federal
obligation under **Section 508 of the Rehabilitation Act** and the **21st
Century Integrated Digital Experience Act (21st Century IDEA)**. This statement
covers the accessibility of **this repository's own content** (its Markdown
documentation). Guidance for making the *software you build* accessible lives in
[`docs/CODING_PRACTICES.md` §14 (Accessibility)](docs/CODING_PRACTICES.md).

## Scope

This repository is a documentation and tooling corpus consumed as Markdown on
GitHub, in editors, and by AI agents. There is no hosted web UI, so
accessibility here means **accessible document structure**: content that screen
readers, keyboard navigation, and assistive tooling can parse reliably.

## What we do

Every Markdown document in this repository is expected to:

- **Start with a single top-level heading (H1)** and use properly nested
  heading levels — the primary navigation landmark for assistive technology.
- **Provide alternative text for every image** (`![descriptive text](path)`;
  decorative images use `alt=""`). Enforced by markdownlint **MD045** in CI and
  pre-commit.
- **Use real Markdown tables with header rows** (GFM tables require a header +
  separator row to render), so tabular data is announced with column context.
- **Prefer plain language and descriptive link text** ("see the contributing
  guide", not "click here"), per [`CONTRIBUTING.md`](CONTRIBUTING.md).

The image alt-text rule runs in CI (`markdownlint-cli2`) and pre-commit, so that
regression fails the build rather than shipping. Heading structure, table
headers, and link text are contributor conventions reinforced in review.

## What we ask of contributors

When adding or editing documentation:

1. Give the document one H1 and nest sub-headings without skipping levels.
2. Add meaningful `alt` text to any image; use `alt=""` only for purely
   decorative images.
3. Keep tables real Markdown tables with a header row — don't fake them with
   spacing.
4. Write descriptive link text and plain language.

Run `make lint` (or let pre-commit run) before opening a pull request.

## Reporting an accessibility issue

If you find a documentation-accessibility problem in this repository, open a
GitHub issue. For accessibility of a GSA service or website (not this repo), see
the [GSA Section 508 program](https://www.section508.gov/).

## References

- [Section 508 program (section508.gov)](https://www.section508.gov/)
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/)
- [`docs/CODING_PRACTICES.md` §14](docs/CODING_PRACTICES.md) — accessibility of
  software the playbook advises on
