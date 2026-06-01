---
name: code-review
title: "Code Review and PR Workflow"
description: "Review AI-assisted code changes and create compliant pull requests with proper attribution"
status: canonical
tier: 2
last_updated: "2026-06-01"
load_priority: on-demand
audience: ["developers", "agents"]
triggers: ["code review", "pull request", "PR", "review code", "merge", "attribution"]
dependencies: []
---

# Code Review and PR Workflow

Review AI-assisted code changes and create compliant pull requests.

**Context loading:** When *writing* code, load `docs/CODING_STANDARDS_COMPACT.md` (~500 words). When *reviewing* code, load the full `docs/CODING_PRACTICES.md` (~4,100 words). This skill references both.

## When to Use

- Before creating a pull request with AI-assisted changes
- When reviewing code that an AI agent generated or modified
- When a user asks "review this code" or "create a PR"
- After completing a feature or bug fix, before merge

## Step 1: Pre-PR Checks

Run automated checks before creating the PR. Fix all failures before proceeding.

### 1.1 Linter, Formatter, and Tests

Run the project's linter and full test suite. Detect the toolchain from config
files (e.g., `npm run lint && npm test`, `ruff check . && pytest`,
`go vet ./... && go test ./...`). All tests MUST pass before proceeding. If no
linter is configured, flag this as a gap.

### 1.2 Secrets Scan

Run `gitleaks detect --no-git -v` (or grep the diff for key/secret/token/password
patterns as a fallback). Any match MUST be investigated and real secrets removed
immediately. See `docs/CODING_PRACTICES.md` Section 4.

### 1.3 Size and Complexity

Verify the changes respect project limits (per `docs/CODING_PRACTICES.md` Section 13.3):

- Functions: 50 lines or fewer
- Files: 400 lines or fewer (400-600 acceptable with justification)
- Cyclomatic complexity: 10 or fewer per function
- Parameters: 5 or fewer per function

Flag violations in the PR description with justification if they are intentional.

## Step 2: Attribution

All AI-generated code MUST be attributed per `AGENTS.md` Section 2.1.

### 2.1 Co-authored-by Trailer

Every commit that includes AI-generated or AI-modified code MUST include a
`Co-authored-by:` trailer (note: lowercase "authored"):

```
Co-authored-by: OpenCode Agent <user@gsa.gov>
```

**Format:**
- Appears after a blank line following the commit body
- Uses lowercase `Co-authored-by:` (matches GitHub standard)
- Email should match the user's verified email
- One line per co-author

**Example:**
```
feat: add user authentication

Implement login.gov SSO integration.

Co-authored-by: OpenCode Agent <user@gsa.gov>
```

To verify attribution on existing commits:

```bash
git log --format='%H %s%n%(trailers:key=Co-authored-by)' -10
```

If commits are missing attribution, amend them before creating the PR (if on a
feature branch with no downstream consumers). For commits already pushed and
shared, note the gap in the PR description.

Attribution is required when the agent wrote, refactored, or generated code
(including tests and config). It is NOT required for code the human wrote
entirely or for trivial formatting by automated tools.

## Step 3: Create the Pull Request

### 3.1 PR Title

Use conventional commit format:

```
feat(auth): add login.gov SSO integration
fix(api): validate email format on user registration
refactor(db): extract query builder from handler
docs: add ADR-0005 for session management
test(api): add regression test for issue #42
```

### 3.2 PR Description

The PR description MUST include:

1. **Summary** -- what changed and why (1-3 sentences)
2. **Related issues** -- link to issue numbers (`Closes #42`, `Refs #38`)
3. **Related ADRs** -- reference any architecture decisions (`See docs/decisions/0005-session-management.md`)
4. **AI attribution** -- which AI agent was used and for which parts
5. **Test plan** -- how to verify the changes work

Keep the description concise. The AI attribution section names the agent and
confirms human review occurred.

## Step 4: Code Review Checklist

Review against the Category 1 checks from `checklists/pre-deployment.md`:

| # | Check | How to Verify |
|---|-------|---------------|
| 4.1 | All AI-generated code reviewed by a human | Confirm reviewer is not the person who prompted the agent |
| 4.2 | Reviewer understands what the code does | Reviewer can explain the logic in their own words |
| 4.3 | No hallucinated APIs or methods | Verify every imported module, function call, and method exists in the dependency's actual docs |
| 4.4 | No deprecated methods or patterns | Check deprecation warnings in linter output and dependency changelogs |
| 4.5 | Test coverage is adequate | New code has corresponding tests; coverage did not decrease |
| 4.6 | No TODO/FIXME/HACK without a linked issue | Every temporary workaround references a tracking issue |
| 4.7 | Error handling is explicit | No empty catch blocks, no swallowed errors, no silent fallbacks |

### Hallucination Check

AI agents may generate calls to APIs, libraries, or language features that do
not exist (`docs/CODING_PRACTICES.md` Section 1.2). For each new dependency or
unfamiliar API call:

1. Confirm the package exists in the registry (npm, PyPI, crates.io)
2. Confirm the specific function or method exists in the package's current version
3. Confirm the function signature matches how it is called

## Step 5: Security Review

Review against `AGENTS.md` Section 5 (Secure Code Generation) and
`checklists/pre-deployment.md` Category 2 (Secrets) and Category 3 (Input Validation).

| # | Check | What to Look For |
|---|-------|------------------|
| 5.1 | No secrets in the diff | API keys, tokens, passwords, private keys, connection strings |
| 5.2 | No hardcoded internal hostnames or IPs | Server names, internal URLs, IP addresses |
| 5.3 | Input validation on new endpoints | All external input validated server-side with allowlists |
| 5.4 | Parameterized queries only | No string concatenation for SQL, shell commands, or LDAP queries |
| 5.5 | No eval/exec with external data | No `eval()`, `exec()`, `Function()`, `child_process.exec(untrusted)` |
| 5.6 | Output encoding matches context | HTML, URL, shell escaping applied correctly per output context |
| 5.7 | Dependencies checked for CVEs | `npm audit` / `pip-audit` / `cargo audit` shows no critical/high issues |
| 5.8 | New dependencies verified | Package name is correct (no typosquatting), license is compatible, actively maintained |

If any security check fails, the PR MUST NOT be approved until the issue is resolved.

## Step 6: Merge Criteria

All of the following MUST be true before merging:

- [ ] All CI checks pass (lint, test, security scan)
- [ ] At least one human reviewer approved the PR
- [ ] The reviewer is NOT the same person who directed the AI agent (per `checklists/pre-deployment.md` item 1.1)
- [ ] All review comments are resolved
- [ ] AI assistance is documented (PR description or commit attribution)
- [ ] No secrets or credentials in the diff
- [ ] PR description includes summary, related issues, and test plan

Prefer squash merge for single-purpose branches. Delete the branch after merge.
Verify CI passes on the target branch.

## Framework Alignment

| Step | NIST 800-53 | SSDF | Pre-Deploy Category |
|------|-------------|------|---------------------|
| Pre-PR checks | SA-11, SI-2 | PW.7, PW.9 | -- |
| Attribution | AU-2, AU-3 | PO.2 | Category 1 (1.2) |
| Code review | SA-11, SA-15, CM-3 | PW.2, PW.7 | Category 1 |
| Security review | SI-10, IA-5, SC-28 | PW.5 | Categories 2, 3 |
| Merge criteria | CM-3, CM-5 | PW.6 | Category 1 (1.3, 1.4) |
