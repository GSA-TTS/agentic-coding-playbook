---
name: federal-landscape-update
title: "Federal AI Landscape Update"
description: "Monitor RSS feeds for federal AI guidance updates, compare against current registry, and generate diff reports for human review."
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "isso", "agents"]
triggers: ["landscape update", "federal guidance", "policy update", "RSS monitor", "compliance deadline"]
dependencies: ["feedparser"]
scripts: ["../../scripts/landscape_monitor.py"]
nist_controls: ["CM-3", "SI-7", "SA-5"]
---

# Federal AI Landscape Update

This skill automates the discovery of new federal AI guidance and generates diff
reports for human review. It implements a **hybrid (human-curated automation)**
approach: 70% automated discovery + 30% human judgment.

## When to Use

- Monthly scheduled review (first Monday of each month)
- When a new Executive Order mentioning "AI" is signed
- When NIST publishes a new AI-series document
- When OWASP releases a new LLM/Agentic version
- When a compliance deadline is <30 days away
- When the user asks "what's new in federal AI guidance?"

## Prerequisites

- Python 3.12+ with `feedparser` installed
- Access to `data/federal-ai-landscape.yaml` (structured registry)
- Network access to RSS feeds (whitehouse.gov, nist.gov)

## Execution Procedure

### Step 1: Run the Landscape Monitor

Execute the monitoring script to fetch RSS feeds and compare against the registry:

```bash
PYTHONPATH=scripts python3 -m playbook_validator landscape-check
```

Or run the standalone script:

```bash
python3 scripts/landscape_monitor.py --output reports/landscape-diff-$(date +%Y-%m-%d).md
```

The script will:

1. Fetch RSS feeds from configured sources
2. Parse entries for AI-related publications
3. Compare against `data/federal-ai-landscape.yaml`
4. Identify new, updated, or missing entries
5. Flag compliance deadlines within 30 days
6. Generate a structured diff report

### Step 2: Review the Diff Report

The generated report at `reports/landscape-diff-YYYY-MM-DD.md` includes:

| Section | Description |
|---------|-------------|
| **New Publications** | Items in RSS not in registry |
| **Updated Publications** | Items with newer versions |
| **Approaching Deadlines** | Compliance dates within 30 days |
| **Staleness Warnings** | Registry entries not seen in RSS for >90 days |

### Step 3: Human Review Checklist

For each flagged item, the human reviewer must determine:

- [ ] **Relevance:** Is this publication applicable to AI-assisted development?
- [ ] **Category:** Which category does it belong to?
- [ ] **Urgency:** Does this require immediate action?
- [ ] **Narrative:** What is the "Relevance" annotation for the landscape doc?

### Step 4: Update the Registry

If updates are approved, modify `data/federal-ai-landscape.yaml`:

```yaml
entries:
  - id: new-publication-id
    title: "Publication Title"
    category: nist_standard  # or other category
    source: "NIST"
    date: "2026-05-28"
    status: active
    relevance: "Human-written relevance annotation"
    url: "https://..."
    playbook_phases: []
```

Then regenerate the human-readable document:

```bash
# Regeneration is currently manual - update docs/FEDERAL-AI-LANDSCAPE.md
```

### Step 5: Commit Changes

```bash
git add data/federal-ai-landscape.yaml docs/FEDERAL-AI-LANDSCAPE.md
git commit -m "docs(landscape): update federal AI guidance registry

Add: [list new entries]
Update: [list updated entries]
Remove: [list removed entries]

Reviewed-by: [human reviewer]
Co-authored-by: OpenCode Agent <agent@gsa.gov>"
```

## RSS Feed Sources

| Source | Feed URL | Categories Monitored |
|--------|----------|---------------------|
| White House | `https://www.whitehouse.gov/feed/` | Executive Orders, Presidential Actions |
| NIST CSRC | `https://csrc.nist.gov/csrc/feed/publications` | SP 800-series, AI RMF |
| OWASP | `https://owasp.org/feed.xml` | LLM Top 10, Agentic Top 10 |
| Federal Register | `https://www.federalregister.gov/api/v1/documents.rss` | AI-related regulations |

## Output Format

### Diff Report Structure

```markdown
# Federal AI Landscape Diff Report

**Generated:** 2026-05-28T18:00:00Z
**Registry Version:** data/federal-ai-landscape.yaml @ abc123
**Feeds Checked:** 4

## Summary

- New publications found: 2
- Updates detected: 1
- Deadlines within 30 days: 1
- Staleness warnings: 0

## New Publications

### 1. NIST AI 600-2: Generative AI Security Profile (Draft)

- **Source:** NIST CSRC
- **Date:** 2026-05-15
- **URL:** https://csrc.nist.gov/publications/detail/ai/600-2/draft
- **Suggested Category:** nist_standard
- **Suggested Status:** draft

**Action Required:** Review for relevance and add to registry.

## Approaching Deadlines

### M-25-21 Compliance Deadline

- **Deadline:** 2026-04-15
- **Days Remaining:** -43 (PAST DUE)
- **Entry ID:** m-25-21

**Action Required:** Verify compliance status.

## Staleness Warnings

None.
```

## Automation Classification

| Component | Automation Level | Notes |
|-----------|-----------------|-------|
| RSS feed fetching | Automated | feedparser library |
| AI-keyword filtering | Automated | Regex matching |
| Version comparison | Automated | Date/version parsing |
| Deadline calculation | Automated | Date arithmetic |
| Relevance filtering | **Human** | Is this applicable? |
| Narrative writing | **Human** | "Relevance" annotations |
| Final approval | **Human** | Before registry update |

## Success Metrics

After 6 months of use, measure:

- **Coverage accuracy:** 95%+ of relevant new publications detected
- **Staleness:** Zero sections >120 days old without justification
- **False positive rate:** <20% of flagged publications rejected
- **Time savings:** Human review reduced from ~4 hours to ~1 hour per cycle

## Troubleshooting

### RSS Feed Unreachable

```text
Error: Failed to fetch https://www.whitehouse.gov/feed/
```

**Cause:** Network restriction or site unavailable.
**Fix:** Check network connectivity. The script will continue with other feeds.

### Parser Errors

```text
Error: Could not parse feed entry
```

**Cause:** Malformed RSS entry.
**Fix:** The script logs the entry and continues. Report persistent issues.

### No Updates Found

If the script reports no updates but you expect some:

1. Check if the publication date is within the monitoring window (default: 90 days)
2. Verify the AI-keyword filter matches the publication title
3. Check if the entry already exists in the registry

## Control Mapping

- **CM-3:** Configuration Change Control — Automated monitoring detects guidance changes
- **SI-7:** Information Integrity — Version validation ensures current references
- **SA-5:** System Documentation — Accurate guidance references maintained

## References

- [Issue #46](https://github.com/GSA-TTS/agentic-coding-playbook/issues/46) — Original feature request
- [data/federal-ai-landscape.yaml](../../data/federal-ai-landscape.yaml) — Structured registry
- [docs/FEDERAL-AI-LANDSCAPE.md](../../docs/FEDERAL-AI-LANDSCAPE.md) — Human-readable companion
