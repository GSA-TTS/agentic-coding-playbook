---
title: "Align frontmatter with portable metadata standards via a documented crosswalk"
status: "accepted"
date: "2026-08-10"
decision_makers: ["William Zujkowski", "OpenCode Agent"]
category: "engineering-discipline"
nist_controls: ["SA-5", "CM-3", "SI-7"]
impact_level: "moderate"
ato_relevance: "no"
risk_treatment: "mitigate"
---

# Align frontmatter with portable metadata standards via a documented crosswalk

## Context and Problem Statement

The playbook's content documents use an ad-hoc YAML frontmatter vocabulary
(`title`, `description`, `status`, `tier`, `nist_controls`, `frameworks`,
`last_updated`, `review_cycle`, `contract`, `related_files`, `load_priority`,
`audience`, `keywords`). An investigation prompted by Google's Open Knowledge
Format (OKF) v0.2 asked whether we should adopt OKF or another emerging
frontmatter standard, and if not, whether our fields are portable/interoperable
with the wider metadata ecosystem.

Research (a standards-landscape scan + a schema baseline of this repo, then a
7-of-7 higher-order consensus) found:

- OKF v0.2 is a **single-vendor draft**, not a ratified standard. Its
  provenance/trust/freshness families (`sources`, `generated`, `verified`,
  `stale_after`, Attested Computation) are themselves echoes of Dublin Core and
  SLSA/in-toto.
- Our frontmatter is **~80% already isomorphic to Dublin Core (DCMI Terms / ISO
  15836) and schema.org TechArticle** — the two most mature, portable
  vocabularies, which almost every other standard (DCAT-US, MyST, OKF) echoes.
  `audience` and `keywords` already match those vocabularies verbatim.
- Four concepts recur in every mature standard: freshness, lifecycle-status,
  authorship, provenance.
- **YAML frontmatter is itself a convention, not a standard.** Neither
  [CommonMark](https://spec.commonmark.org/) nor GitHub Flavored Markdown
  defines frontmatter; it is a widely-adopted tooling convention (Jekyll, Hugo,
  Obsidian) parsed per-tool. Our frontmatter schema is therefore **repo-defined
  and locally validated** — this crosswalk is what gives it portability, not any
  Markdown specification.
- Beyond human-facing metadata (Dublin Core / schema.org), our fields also map
  cleanly onto **Model Context Protocol (MCP) resource annotations** — the
  agent-consumption axis (`audience` → `annotations.audience`, `load_priority`/
  `tier` → `annotations.priority`, `last_updated` → `lastModified`). The
  crosswalk records this too so the schema is portable to agent runtimes, not
  only to citation/catalog tools.

## Decision Drivers

- Portability/interoperability with mature standards, at low risk.
- Do not break the existing validator or force an edit to every document.
- Do not couple the repo to an unstable single-vendor draft.
- Keep provenance claims credible: federal supply-chain policy (EO 14028,
  M-22-18) treats a self-asserted `verified: true` flag as no evidence at all.

## Considered Options

1. **Adopt OKF v0.2 as a conformance target.** Rejected: single-vendor draft;
   conforming couples us to an unstable spec for concepts we already express.
2. **Destructively rename our keys to Dublin Core / schema.org term names**
   (`last_updated`→`modified`, etc.). Rejected: breaks the validator, every
   doc, and INDEX generation for zero functional gain — the interoperability
   win is semantic, not lexical.
3. **Keep our key names; document the semantic equivalence in a crosswalk**
   (`data/frontmatter-crosswalk.yaml`) + this ADR, and guard that every schema
   key is crosswalked. Chosen.

## Decision Outcome

Chosen option: **Option 3.** We keep our frontmatter key names for tooling
stability and add `data/frontmatter-crosswalk.yaml` mapping each key to its
Dublin Core term and schema.org property (with `exact_match` flagged where the
name already equals the standard). A `validate-docs` guard fails closed if a key
in `INDEX.yaml` `frontmatter_schema` (required or optional) has no crosswalk
entry, so a newly-added key must be crosswalked deliberately rather than drift
outside any standard.

This gains portability/interoperability semantics without a destructive rename
and without adopting an unstable format.

### Non-goals (explicit)

- **No OKF conformance.** OKF is design inspiration only.
- **No key renames.** The crosswalk is documentation-as-data, not a migration.
- **No self-asserted provenance.** We do not add `generated:`/`verified:`
  frontmatter flags. If document provenance is ever required, the credible path
  is a signed in-toto/SLSA sidecar (tracked separately), never a YAML flag.

### Related follow-ups (epic #208)

- Freshness enforcement: optional `stale_after` + a validator staleness check
  (today `last_updated` + `review_cycle` staleness is prose-only, unenforced)
  — issue #210.
- Accessibility: a repo-level Section 508 statement + markdown-hygiene lint
  (scoped away from per-doc frontmatter per maintainer decision) — issue #211.
- A generated repo-root `llms.txt` for agent navigation — issue #212.

### Positive Consequences

- Our metadata becomes interoperable with the widest set of tools/standards via
  a single documented artifact.
- The crosswalk guard prevents new keys from escaping standards alignment.
- No breaking change; no doc churn.

### Negative Consequences

- The crosswalk is a maintained artifact that must be updated when a frontmatter
  key is added (enforced by the guard, so it cannot silently rot).

### Compliance Consequences

- SA-5 (system documentation — metadata is now self-describing against
  recognized standards), CM-3 (change control — guarded), SI-7 (integrity —
  the guard keeps the schema and crosswalk in sync). Tooling/docs only;
  `ato_relevance: no`.

## Links

- Epic #208; issues #209 (this ADR), #210, #211, #212
- `data/frontmatter-crosswalk.yaml`
- Dublin Core: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
- schema.org TechArticle: https://schema.org/TechArticle
- OKF v0.2 (reference only): https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
