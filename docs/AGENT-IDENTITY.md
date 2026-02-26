---
title: "Agent Identity, Authentication, Authorization, and Delegation"
description: "Agent identity management aligned with NCCOE concept paper — authentication, authorization, delegation, and audit logging for AI agents"
status: canonical
tier: 1
last_updated: "2026-02-25"
nist_controls: ["AC-2", "AC-3", "AC-6", "AU-2", "AU-3", "IA-2", "IA-5", "IA-8"]
frameworks: ["NCCOE Agent Identity & Authorization", "NIST CAISI", "NIST SP 800-53 Rev 5.2", "NIST SP 800-63"]
audience: "developers"
keywords: ["agent-identity", "OAuth", "RBAC", "delegation", "audit-logging", "NCCOE", "authentication"]
related_files: ["AGENTS.md", "docs/SECURITY-CONTROLS.md", "templates/risk-assessment.md"]
load_priority: "task-context"
review_cycle: "quarterly"
---

<!-- LOAD: task-context — Load when task involves authentication, authorization, identity, OAuth, RBAC, delegation, or audit logging. -->

# Agent Identity, Authentication, Authorization, and Delegation

> **Version:** 0.1.0 | **Impact Level:** FIPS Moderate | **Scope:** Single-agent, internal enterprise

## Quick Reference

| Concern | Requirement |
|---------|-------------|
| Identity | Unique agent ID per instance, human-readable name, version tracked |
| Authentication | OAuth 2.0 client credentials or API keys via approved KMS, no shared credentials |
| Authorization | RBAC with least privilege, explicit permission lists, deny-by-default |
| Delegation | Agent acts on behalf of authenticated user, inherits user's max permissions (never exceeds) |
| Session | Time-limited tokens, automatic expiry, no persistent sessions without re-auth |
| Audit | Log every action with: agent ID, delegating user, timestamp, action, outcome |
| Revocation | Immediate credential revocation capability, break-glass procedures documented |

> **Full guidance with NCCOE alignment and implementation patterns in sections below.**

---

> **Disclaimer:** This guidance is informational only and is not authoritative federal policy. Each agency must tailor these recommendations to their specific ATO requirements, organizational policies, and risk tolerance.

This document provides practical guidance for managing AI coding agent identities within federal systems. It covers how agents are identified, how they authenticate, what they are authorized to do, how user identity delegates to agent identity, and how all of it gets logged for audit.

**Alignment:** This guidance aligns with:
- **NCCOE** — [Accelerating the Adoption of Software and AI Agent Identity and Authorization](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization) Concept Paper (February 2026)
- **NIST CAISI** — [AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative) (February 2026)

**Key words:** "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" are used per [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Agent Identity Model](#2-agent-identity-model)
3. [Authentication](#3-authentication)
4. [Authorization](#4-authorization)
5. [Delegation Model](#5-delegation-model)
6. [Audit and Non-Repudiation](#6-audit-and-non-repudiation)
7. [Human-in-the-Loop Patterns](#7-human-in-the-loop-patterns)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Introduction

<!-- NCCOE Agent Identity: All Focus Areas -->
<!-- NIST CAISI: AI Agent Standards -->
<!-- NIST SP 800-53: IA-1 (Policy and Procedures) -->

AI coding agents present a new identity management challenge for federal systems. They are not human users, but they act on behalf of human users. They are not traditional service accounts, but they consume APIs and modify resources. They need credentials to function, but they cannot present a PIV card or answer an MFA challenge.

Federal identity and access management (IAM) systems were designed around two categories: **human users** and **service accounts**. AI agents fall somewhere in between. They interact conversationally like humans, execute automated tasks like services, and operate with delegated authority from the user who invoked them.

The NCCOE concept paper (February 2026) identifies four focus areas for managing this new category of identity:

| # | NCCOE Focus Area | This Document |
|---|---|---|
| 1 | **Identification** — Distinguishing AI agents from human users and managing metadata about agent capabilities | [Section 2](#2-agent-identity-model) |
| 2 | **Authorization** — Using OAuth 2.0, RBAC, and policy-based access control for agent rights | [Section 4](#4-authorization) |
| 3 | **Access Delegation** — Linking user identities to AI agents for accountability | [Section 5](#5-delegation-model) |
| 4 | **Logging and Transparency** — Linking agent actions to their non-human entity for audit | [Section 6](#6-audit-and-non-repudiation) |

The NIST CAISI initiative is developing standards for AI agent behavior more broadly. While those standards are still emerging, this document provides actionable guidance you can implement now.

**Who should read this:** Federal developers, DevOps engineers, and system administrators who deploy or manage AI coding agents. You do not need deep IAM expertise — this document explains concepts as it goes.

> **Control Mapping:** IA-1 (Identification and Authentication Policy), PL-1 (Security Planning Policy)

---

## 2. Agent Identity Model

<!-- NCCOE Agent Identity: Focus Area 1 — Identification -->
<!-- NIST SP 800-53: AC-2 (Account Management), IA-2 (Identification), IA-8 (Non-Organizational Users) -->
<!-- OWASP Agentic: Identity and Privilege Abuse -->

An AI coding agent needs a distinct identity within your system — separate from the user who invoked it and separate from other agents. Without this, you cannot answer basic audit questions: Who made this change? Was it the human or the agent? Which agent?

### 2.1 Identity Approaches

There are three common patterns for how agents authenticate to systems. Each has tradeoffs.

| Approach | Description | Pros | Cons |
|---|---|---|---|
| **Agent service account** | Agent gets its own account with its own credentials | Clear audit trail; fine-grained permissions; revocable | Requires account provisioning; credential management overhead |
| **User-delegated token** | Agent uses a scoped token derived from the user's session | Inherits user context; no separate provisioning; natural accountability | Token scope must be carefully limited; user session dependency |
| **Shared credentials** | Agent uses the user's credentials directly | Simple setup | No distinction in audit logs; violates least privilege; cannot revoke agent access independently |

**Recommendation:** Federal systems SHOULD use either agent service accounts or user-delegated tokens. Shared credentials MUST NOT be used in production systems because they make it impossible to distinguish agent actions from user actions in audit logs.

### 2.2 Required Agent Metadata

Every AI agent operating in your system MUST have the following metadata recorded and available for audit:

| Field | Description | Example |
|---|---|---|
| `agent_id` | Unique identifier for this agent instance | `open-code-a1b2c3d4` |
| `agent_name` | Human-readable name of the agent product | `Open Code` |
| `agent_version` | Version of the agent software | `1.42.0` |
| `agent_type` | Category of agent | `coding-assistant` |
| `owning_user` | The human user who invoked the agent | `jane.doe@agency.gov` |
| `capabilities` | What the agent is allowed to do | `["file_read", "file_write", "shell_exec"]` |
| `created_at` | When the agent session was created | `2026-02-25T14:30:00Z` |
| `expires_at` | When the agent's authorization expires | `2026-02-25T22:30:00Z` |

The agent SHOULD also track:
- **Model identifier** — which AI model is powering the agent (e.g., `claude-opus-4-6`)
- **Provider** — the vendor or service (e.g., `anthropic`, `openai`, `self-hosted`)
- **Deployment context** — where the agent is running (e.g., `developer-workstation`, `ci-pipeline`, `cloud-ide`)

### 2.3 Distinguishing Agent Actions from Human Actions

Every action taken by an agent MUST be distinguishable from a human action in all systems the agent touches.

**In version control:**
- Agent-authored commits MUST include a co-authorship trailer:
  ```
  Co-Authored-By: Open Code <agent@example.com>
  ```
- The committer identity SHOULD identify the agent, not the user, when possible
- If the VCS system does not support separate committer/author fields, the commit message body MUST identify the agent

**In API calls:**
- The `User-Agent` header SHOULD include the agent name and version:
  ```
  User-Agent: open-code/1.42.0 (federal-workstation)
  ```
- If the API supports custom headers, include an `X-Agent-Id` header with the agent's unique identifier

**In audit logs:**
- Every log entry MUST include both the `owning_user` and the `agent_id` (see [Section 6](#6-audit-and-non-repudiation))

### 2.4 Naming Conventions for Agent Accounts

When provisioning service accounts for agents, use a naming convention that makes agent accounts immediately identifiable:

```
svc-agent-{agent-type}-{environment}-{sequence}
```

Examples:
- `svc-agent-claude-dev-001` — Open Code agent in development
- `svc-agent-copilot-staging-001` — GitHub Copilot agent in staging
- `svc-agent-cursor-prod-001` — Cursor agent in production

Naming rules:
- Agent service account names MUST contain "agent" or "ai" to distinguish them from human and traditional service accounts
- Agent accounts MUST be placed in a distinct organizational unit (OU) or group in your identity provider
- Agent accounts MUST NOT share naming patterns with human accounts

> **Control Mapping:** AC-2 (Account Management), IA-2 (Identification and Authentication), IA-4 (Identifier Management), IA-8 (Identification and Authentication — Non-Organizational Users)

---

## 3. Authentication

<!-- NCCOE Agent Identity: Focus Areas 1, 3 -->
<!-- NIST SP 800-53: IA-2 (Identification), IA-5 (Authenticator Management), IA-8 (Non-Org Users), SC-23 (Session Authenticity) -->
<!-- NIST SP 800-63: Digital Identity Guidelines -->

AI agents authenticate differently than humans. They cannot present a PIV/CAC card, answer a phone-based MFA challenge, or type a password. Authentication mechanisms for agents must accommodate these constraints while maintaining federal security requirements.

### 3.1 OAuth 2.0 Client Credentials Flow (Service-to-Service)

When an agent acts as a standalone service — for example, a CI/CD pipeline agent that runs automated code reviews — use the OAuth 2.0 client credentials grant.

**How it works:**
1. The agent is registered as an OAuth client with your identity provider
2. The agent authenticates using a `client_id` and `client_secret` (or client certificate)
3. The identity provider issues a short-lived access token
4. The agent includes this token in API requests

**Requirements:**
- The client secret MUST be stored in an approved secrets management solution — never in source code or environment variables committed to version control
- Access tokens MUST have a maximum lifetime of **1 hour**
- The agent MUST request only the scopes needed for the current task
- Client credentials MUST be rotated on a defined schedule (agency policy, typically 90 days maximum)

**When to use:** Automated pipelines, scheduled tasks, background agents that do not operate on behalf of a specific user session.

### 3.2 OAuth 2.0 On-Behalf-Of Flow (User-Delegated)

When an agent acts on behalf of a specific user — for example, a coding assistant helping a developer in their IDE — use the OAuth 2.0 on-behalf-of (OBO) flow or a comparable delegation mechanism.

**How it works:**
1. The user authenticates normally (PIV/CAC, SSO, MFA)
2. The user's session generates a delegation token for the agent
3. The agent uses this delegation token to access resources on the user's behalf
4. All actions are traceable to both the user and the agent

**Requirements:**
- The delegation token MUST have a narrower scope than the user's full permissions
- The delegation token MUST expire when the user's session ends (or sooner)
- The token MUST NOT be transferable to other agents or sessions
- The user MUST be able to revoke the delegation at any time

**When to use:** Interactive coding sessions where the agent operates within the user's context.

### 3.3 API Key Management

Many AI agents connect to external model providers (Anthropic, OpenAI, etc.) using API keys. These keys require careful management.

**Requirements:**
- API keys MUST be stored in approved secrets management solutions (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or agency equivalent)
- API keys MUST NOT be committed to version control, stored in `.env` files that could be committed, or passed as command-line arguments (which appear in process listings)
- API keys MUST be rotated on a regular schedule (90 days maximum; 30 days recommended)
- Each agent instance or environment SHOULD have its own API key to enable granular revocation
- API key usage SHOULD be monitored for anomalous patterns (unusual volume, off-hours access, unexpected endpoints)

**Rotation procedure:**
1. Generate new key in the provider's management console
2. Update the secrets management solution with the new key
3. Verify the agent functions with the new key
4. Revoke the old key
5. Log the rotation event

### 3.4 PIV/CAC-Aware Workflows

AI agents cannot directly use PIV or CAC smart cards. However, PIV/CAC authentication can gate agent access.

**Pattern: PIV-gated agent activation:**
1. User authenticates to the workstation or IDE using PIV/CAC
2. Successful PIV authentication unlocks the ability to invoke the agent
3. The agent receives a delegated token derived from the PIV-authenticated session
4. The agent's token inherits the user's PIV-verified identity for audit purposes

**Requirements:**
- Agent access MUST be contingent on the user having completed strong authentication (PIV/CAC or equivalent MFA)
- If the user's PIV session expires or is revoked, the agent's delegated token MUST be invalidated
- The agent MUST NOT cache or store PIV-derived credentials beyond the current session

### 3.5 Token Scope and Lifetime Requirements

| Token Type | Maximum Lifetime | Scope Rule |
|---|---|---|
| Agent service account token | 1 hour | Minimum scopes for task category |
| User-delegated token | Shorter of: 8 hours or user session | Subset of user's permissions |
| CI/CD pipeline token | Duration of pipeline run | Read-only unless write explicitly needed |
| API provider key | 90 days (rotate) | Per-environment, per-agent-type |

**Scope examples:**

```
# Coding assistant — needs file access and limited git operations
scope: repo:read repo:write:branch git:commit git:push:branch

# Code review agent — read-only
scope: repo:read pull_request:read pull_request:comment

# CI/CD agent — needs build and deploy
scope: repo:read ci:trigger artifact:write deploy:staging
```

Tokens MUST NOT include wildcard or administrative scopes. If the agent needs elevated access for a specific operation, it MUST request escalation through the human-in-the-loop approval process (see [Section 7](#7-human-in-the-loop-patterns)).

> **Control Mapping:** IA-2 (Identification and Authentication), IA-4 (Identifier Management), IA-5 (Authenticator Management), IA-5(2) (PKI-Based Authentication), SC-12 (Cryptographic Key Establishment)

---

## 4. Authorization

<!-- NCCOE Agent Identity: Focus Area 2 — Authorization -->
<!-- NIST SP 800-53: AC-3 (Access Enforcement), AC-6 (Least Privilege), AC-16 (Security and Privacy Attributes) -->
<!-- OWASP Agentic: Tool Misuse and Exploitation, Identity and Privilege Abuse -->

Authorization determines what an agent is allowed to do once it has been identified and authenticated. Federal systems MUST enforce authorization controls that are at least as strict for agents as they are for human users — and in many cases, stricter.

### 4.1 Least Privilege Enforcement

The principle of least privilege is the foundation of agent authorization. Agents MUST start with zero permissions and be granted only what they need.

**Rules:**
- Agents MUST be authorized only for the specific tasks they are designed to perform
- Agents MUST NOT inherit the full permission set of the invoking user
- Permissions MUST be granted at the narrowest scope possible (specific repository, not all repositories; specific directory, not entire filesystem)
- Permissions MUST be reviewed and recertified on a regular schedule (quarterly minimum)
- Unused permissions MUST be revoked — if an agent has not used a permission in 30 days, review whether it is still needed

### 4.2 Role-Based Access Control (RBAC) for Agents

Define agent roles that map to specific capability levels. This is simpler to manage than per-agent permission lists.

| Role | Permissions | Use Case |
|---|---|---|
| `agent-reader` | Read files, read git history, read CI results | Code review, documentation lookup |
| `agent-developer` | Read/write files, create branches, run tests, commit to feature branches | Interactive coding assistance |
| `agent-ci` | Read files, run builds, run tests, publish artifacts | CI/CD pipeline automation |
| `agent-reviewer` | Read files, read PRs, post review comments | Automated code review |
| `agent-admin` | Should not exist for agents | Agents MUST NOT have administrative access |

**Assignment rules:**
- Each agent MUST be assigned exactly one role per system
- Role escalation (moving from `agent-reader` to `agent-developer`) MUST require human approval
- The `agent-admin` role MUST NOT exist — agents MUST NOT have administrative access to any system
- Custom roles SHOULD be defined when the standard roles do not fit, rather than granting a broader standard role

### 4.3 Policy-Based Access Control

For fine-grained authorization decisions, use a policy engine. This allows rules like "Agent X can write to files in `/src/` but not `/config/`" or "Agent Y can run `npm test` but not `npm publish`."

**Common policy engines:**
- **Open Policy Agent (OPA)** — General-purpose, widely adopted in federal environments
- **Cedar** — AWS-developed, designed for fine-grained authorization
- **Agency-specific solutions** — Many agencies have existing policy decision points (PDPs)

**Example policy (OPA/Rego-style pseudocode):**

```rego
# Agent can write files only within the project source directory
allow_file_write {
    input.actor.type == "agent"
    input.resource.type == "file"
    startswith(input.resource.path, "/project/src/")
    not startswith(input.resource.path, "/project/src/config/secrets/")
}

# Agent can execute shell commands only from an allowlist
allow_shell_exec {
    input.actor.type == "agent"
    input.action == "shell_exec"
    input.command.name in {"npm", "npx", "python", "pytest", "git"}
}
```

### 4.4 Capability Boundaries

Define explicit boundaries for what agents can and cannot do. These boundaries apply regardless of the agent's role.

| Capability | Default | Notes |
|---|---|---|
| **Filesystem read** | Project directory only | No access to home directory, system files, or other projects |
| **Filesystem write** | Project source directories only | No write access to config, deployment, or CI directories without approval |
| **Shell execution** | Allowlisted commands only | See allowlist in your AGENTS.md |
| **Network access** | Deny by default | Specific endpoints allowlisted per project |
| **Git operations** | Commit and push to feature branches | No force push; no push to main/production branches |
| **Package installation** | With approval | Agent may suggest; human approves |
| **Database access** | Read-only in non-production | No direct production database access |
| **Secrets access** | Deny | Agent cannot read secrets directly; uses delegated tokens |

### 4.5 Deny-by-Default Posture

Authorization for agents MUST follow a deny-by-default model:

- If a permission is not explicitly granted, it is denied
- If a capability boundary is not defined, the capability is denied
- If the policy engine is unreachable or returns an error, the action is denied
- If the agent's token has expired, all actions are denied — no grace period

This is the opposite of how many developer tools work by default (which typically allow everything the user can do). Federal agent deployments MUST explicitly configure permissions rather than relying on defaults.

> **Control Mapping:** AC-3 (Access Enforcement), AC-6 (Least Privilege), AC-6(1) (Authorize Access to Security Functions), AC-6(5) (Privileged Accounts), AC-16 (Security and Privacy Attributes), CM-7 (Least Functionality)

---

## 5. Delegation Model

<!-- NCCOE Agent Identity: Focus Area 3 — Access Delegation -->
<!-- NIST SP 800-53: AC-2 (Account Management), AC-3 (Access Enforcement), AC-17 (Remote Access) -->
<!-- OWASP Agentic: Human Agent Trust Exploitation -->

When a user invokes an AI coding agent, the agent acts on the user's behalf. This creates a delegation chain: the user delegates authority to the agent, and the agent's actions are ultimately the user's responsibility. This delegation must be explicit, scoped, revocable, and auditable.

### 5.1 Chain of Accountability

```
User (authenticated via PIV/MFA)
  └── delegates to → Agent (with scoped token)
       └── performs → Action (logged with both identities)
            └── traced to → User (accountable party)
```

**Rules:**
- Every agent action MUST be traceable back to the user who initiated the session
- The user MUST be informed about what actions the agent has taken (or proposes to take)
- The user retains full accountability for agent actions — the agent does not absorb responsibility
- If the delegation chain is broken (token expired, user session ended), the agent MUST stop

### 5.2 Delegation Token Patterns

A delegation token encodes the relationship between the user and the agent. It answers: "Who authorized this agent? What is it allowed to do? For how long?"

**Recommended token claims (JWT-style):**

```json
{
  "iss": "https://idp.agency.gov",
  "sub": "svc-agent-claude-dev-001",
  "act": {
    "sub": "jane.doe@agency.gov"
  },
  "scope": "repo:read repo:write:branch git:commit",
  "capabilities": ["file_read", "file_write", "shell_exec_allowlisted"],
  "project": "project-alpha",
  "iat": 1740494400,
  "exp": 1740523200,
  "jti": "example_token_id"
}
```

Key fields:
- `sub` — the agent's identity
- `act.sub` — the delegating user's identity (the "actor on behalf of" claim)
- `scope` — the specific permissions delegated
- `capabilities` — the agent's operational boundaries
- `project` — limits the delegation to a specific project
- `exp` — hard expiration (no renewal without re-authentication)
- `jti` — unique token ID for revocation tracking

### 5.3 Revocation and Scope Limitation

Users MUST be able to revoke agent delegation at any time, with immediate effect.

**Revocation requirements:**
- Revoking the user's session MUST revoke all delegated agent tokens
- The user MUST have a mechanism to revoke agent access independently of their own session (e.g., a "disconnect agent" button)
- Revocation MUST take effect within **60 seconds** (token validation must check revocation lists)
- Revoked tokens MUST be logged with the reason for revocation

**Scope limitation requirements:**
- Delegation tokens MUST be scoped to a specific project or repository
- Delegation tokens MUST NOT grant access to resources the user does not have access to
- Delegation tokens SHOULD be scoped to the current task (e.g., "implement feature X" does not need deploy permissions)

### 5.4 Impersonation Prevention

Agents MUST NOT impersonate users. The distinction is important: acting on behalf of a user (with delegation) is legitimate; pretending to be a user is not.

**Rules:**
- Agent API calls MUST use the agent's own identity, with the delegation claim indicating the user — not the user's identity directly
- Agent-authored content (commits, comments, messages) MUST be identifiable as agent-authored
- If a system does not support delegation claims (no "on behalf of" concept), the agent MUST use its own service account and include the user's identity in metadata or log entries
- Agents MUST NOT use the user's credentials (username/password, PIV certificate, session cookie) to authenticate as the user

> **Control Mapping:** AC-2 (Account Management), AC-3 (Access Enforcement), AC-17 (Remote Access), IA-2 (Identification), IA-4 (Identifier Management), IA-5 (Authenticator Management)

---

## 6. Audit and Non-Repudiation

<!-- NCCOE Agent Identity: Focus Area 4 — Logging and Transparency -->
<!-- NIST SP 800-53: AU-2 (Audit Events), AU-3 (Content of Audit Records), AU-6 (Audit Review), AU-10 (Non-Repudiation), AU-12 (Audit Generation) -->

Every action taken by an agent MUST be logged in a way that answers: Who requested it? Which agent did it? What was done? When? What was the result? This section defines the audit requirements for agent operations.

### 6.1 Required Audit Fields

Every agent action log entry MUST include the following fields:

| Field | Description | Required |
|---|---|---|
| `timestamp` | When the action occurred (ISO 8601, UTC) | MUST |
| `event_id` | Unique identifier for this event | MUST |
| `correlation_id` | Links related events in a chain of actions | MUST |
| `session_id` | The agent session this action belongs to | MUST |
| `requesting_user` | The human who initiated the session | MUST |
| `agent_id` | The agent instance that performed the action | MUST |
| `agent_name` | Human-readable agent name | MUST |
| `agent_version` | Agent software version | MUST |
| `action_type` | Category of action (file_read, file_write, shell_exec, api_call, git_commit) | MUST |
| `action_detail` | Specific action taken | MUST |
| `resource` | What was acted upon (file path, API endpoint, repository) | MUST |
| `result` | Outcome (success, failure, denied, error) | MUST |
| `authorization_basis` | Which role, policy, or approval authorized this action | SHOULD |
| `delegation_token_id` | The JTI of the delegation token used | SHOULD |
| `model_id` | The AI model that powered the action | SHOULD |
| `risk_level` | Assessed risk of the action (low, medium, high) | SHOULD |

### 6.2 Log Format Specification

Agent audit logs MUST use structured JSON format. One JSON object per line (JSON Lines format).

**Example: File write event**

```json
{
  "timestamp": "2026-02-25T14:32:07.123Z",
  "event_id": "evt_7f3a2b1c",
  "correlation_id": "corr_9e8d7c6b",
  "session_id": "sess_a1b2c3d4",
  "requesting_user": "jane.doe@agency.gov",
  "agent_id": "open-code-a1b2c3d4",
  "agent_name": "Open Code",
  "agent_version": "1.42.0",
  "action_type": "file_write",
  "action_detail": "Modified src/api/handler.ts — added input validation",
  "resource": "/project-alpha/src/api/handler.ts",
  "result": "success",
  "authorization_basis": "role:agent-developer",
  "delegation_token_id": "example_token_id"
}
```

**Example: Denied action**

```json
{
  "timestamp": "2026-02-25T14:33:12.456Z",
  "event_id": "evt_8g4b3c2d",
  "correlation_id": "corr_9e8d7c6b",
  "session_id": "sess_a1b2c3d4",
  "requesting_user": "jane.doe@agency.gov",
  "agent_id": "open-code-a1b2c3d4",
  "agent_name": "Open Code",
  "agent_version": "1.42.0",
  "action_type": "file_write",
  "action_detail": "Attempted to modify deploy/production.yaml",
  "resource": "/project-alpha/deploy/production.yaml",
  "result": "denied",
  "authorization_basis": "policy:deny_production_config_write",
  "delegation_token_id": "example_token_id"
}
```

### 6.3 Correlation IDs for Action Chains

When an agent performs a sequence of related actions (e.g., read a file, modify it, run tests, commit), all events in that sequence MUST share a `correlation_id`. This enables auditors to reconstruct the full chain of events.

**Rules:**
- A new `correlation_id` MUST be generated when the user gives the agent a new task
- All actions within that task MUST use the same `correlation_id`
- If a task spawns sub-tasks, each sub-task SHOULD have its own `correlation_id` that references the parent via a `parent_correlation_id` field
- Correlation IDs MUST be included in API requests (via headers) so that downstream systems can continue the trace

### 6.4 Retention Requirements

Agent audit logs MUST be retained according to your agency's records management policy. As a baseline:

| Log Category | Minimum Retention | Rationale |
|---|---|---|
| Security-relevant events (auth, access denial, escalation) | 3 years | NARA GRS 3.2, agency policy |
| Standard operational events (file reads/writes, test runs) | 1 year | Operational needs |
| Session metadata (start, end, user, agent) | 3 years | Accountability |

Logs MUST be stored in a tamper-evident manner. Agents MUST NOT have write access to their own audit logs — logs MUST be written to a system the agent cannot modify or delete.

### 6.5 Non-Repudiation

Non-repudiation means proving that a specific agent took a specific action at a specific time, and that neither the user nor the agent can deny it.

**Requirements:**
- Audit logs MUST be written to an append-only store that the agent cannot modify
- Logs SHOULD be integrity-protected (cryptographic hashing, log signing, or blockchain-style chaining)
- The delegation token used for each action MUST be logged, so the authorization chain can be verified after the fact
- If a dispute arises about whether an agent took an action, the audit trail MUST contain sufficient evidence to resolve it

> **Control Mapping:** AU-2 (Audit Events), AU-3 (Content of Audit Records), AU-6 (Audit Review, Analysis, and Reporting), AU-10 (Non-Repudiation), AU-11 (Audit Record Retention), AU-12 (Audit Record Generation), AU-14 (Session Audit)

---

## 7. Human-in-the-Loop Patterns

<!-- NCCOE Agent Identity: Focus Areas 2, 3 -->
<!-- NIST SP 800-53: AC-6 (Least Privilege), CM-3 (Configuration Change Control), CM-5 (Access Restrictions for Change) -->
<!-- NIST AI RMF: GOVERN 6 (Accountability), MANAGE 1 (Risk Treatment) -->
<!-- OWASP Agentic: Human Agent Trust Exploitation -->

Not every agent action needs human approval — that would eliminate the productivity benefit of agents. But some actions are too risky to automate without a check. This section defines a tiered approval model.

### 7.1 Tiered Approval Model

Classify agent actions into three risk tiers. Each tier has a different approval requirement.

| Tier | Risk Level | Approval Requirement | Examples |
|---|---|---|---|
| **Tier 1 — Auto-approve** | Low | Agent proceeds without asking | Read files, run tests, search codebase, view git history |
| **Tier 2 — Notify** | Medium | Agent proceeds but notifies the user | Write files in project directory, commit to feature branch, install dev dependency |
| **Tier 3 — Block until approved** | High | Agent stops and waits for explicit user approval | Push to remote, modify CI/CD config, delete files, access external APIs, install production dependencies |

**Classification rules:**
- If an action is **reversible** and confined to the project — Tier 1 or Tier 2
- If an action **leaves the local environment** (network, push, deploy) — Tier 3
- If an action is **destructive** (delete, overwrite, force push) — Tier 3
- If an action affects **security controls** (auth config, firewall rules, permissions) — Tier 3
- When in doubt — Tier 3

### 7.2 Approval Workflow Examples

**Tier 2 notification (file write):**
```
Agent: I modified src/api/handler.ts to add input validation for the
       email parameter. Changes: +12 lines, -3 lines.
       [View diff] [Undo]
```

**Tier 3 approval request (push to remote):**
```
Agent: I have 3 commits on branch feat/input-validation ready to push
       to origin. Changes include:
       - Added email validation in handler.ts
       - Added unit tests in handler.test.ts
       - Updated API documentation

       May I push these to the remote? [Approve] [Deny] [Review changes]
```

**Tier 3 approval request (external API call):**
```
Agent: To check for known vulnerabilities in the lodash package, I need
       to query the OSV.dev API (https://api.osv.dev/v1/query).
       This will send the package name and version. No other data.

       May I proceed? [Approve] [Deny]
```

### 7.3 Emergency Bypass Procedures

In rare cases, an organization may need to grant an agent broader permissions temporarily — for example, during an incident response. Emergency bypass MUST follow these rules:

- Emergency bypass MUST be authorized by at least two people (four-eyes principle)
- The bypass MUST have a hard expiration (maximum 4 hours)
- All actions taken during the bypass period MUST be logged at the highest detail level
- A post-incident review MUST evaluate all actions taken under the bypass
- The bypass MUST be recorded in the incident tracking system with justification

Emergency bypass MUST NOT be used to circumvent normal authorization for convenience. It is strictly for time-critical situations where the standard approval workflow would cause unacceptable delay.

> **Control Mapping:** AC-6 (Least Privilege), CM-3 (Configuration Change Control), CM-5 (Access Restrictions for Change), AC-6(1) (Authorize Access to Security Functions), IR-4 (Incident Handling)

---

## 8. Implementation Checklist

Use this checklist when setting up agent identity and access management for a project. Items marked with **(P0)** are required before any agent is deployed. Items marked with **(P1)** are required before production use.

### Identity Setup

- [ ] **(P0)** Agent service account or delegation mechanism is provisioned
- [ ] **(P0)** Agent metadata is recorded (name, version, type, owning user, capabilities)
- [ ] **(P0)** Agent accounts use the naming convention (`svc-agent-{type}-{env}-{seq}`)
- [ ] **(P0)** Agent accounts are in a distinct OU/group in the identity provider
- [ ] **(P1)** Agent identity is included in all version control commits (co-authorship trailer)

### Authentication

- [ ] **(P0)** API keys are stored in approved secrets management (not in code or env files)
- [ ] **(P0)** Agent tokens have maximum lifetime of 1 hour (service) or 8 hours (delegated)
- [ ] **(P0)** Agent access requires user MFA/PIV authentication first
- [ ] **(P1)** API key rotation is scheduled (90 days maximum)
- [ ] **(P1)** Token scope is limited to minimum required permissions

### Authorization

- [ ] **(P0)** Agent permissions follow least privilege — deny by default
- [ ] **(P0)** Agent role is assigned (agent-reader, agent-developer, agent-ci, agent-reviewer)
- [ ] **(P0)** Capability boundaries are defined (filesystem, network, shell, git)
- [ ] **(P1)** Policy engine rules are defined for fine-grained access control
- [ ] **(P1)** Quarterly permission review is scheduled

### Delegation

- [ ] **(P0)** Delegation chain is documented (user -> agent -> actions)
- [ ] **(P0)** Delegation tokens include both user and agent identity
- [ ] **(P0)** User can revoke agent delegation independently
- [ ] **(P1)** Delegation tokens are project-scoped
- [ ] **(P1)** Impersonation prevention is verified (agent uses own identity, not user's)

### Audit

- [ ] **(P0)** Agent actions are logged in structured JSON format
- [ ] **(P0)** Logs include all required fields (timestamp, user, agent, action, result)
- [ ] **(P0)** Agents cannot modify or delete their own audit logs
- [ ] **(P1)** Correlation IDs link related actions
- [ ] **(P1)** Log retention meets agency requirements (minimum 1 year operational, 3 years security)
- [ ] **(P1)** Non-repudiation controls are in place (append-only, integrity-protected)

### Human-in-the-Loop

- [ ] **(P0)** Action risk tiers are defined (auto-approve, notify, block-until-approved)
- [ ] **(P0)** High-risk actions require explicit user approval before execution
- [ ] **(P1)** Approval workflow is implemented and tested
- [ ] **(P1)** Emergency bypass procedure is documented with four-eyes requirement

---

## NIST SP 800-53 Control Cross-Reference

| Section | Primary Controls | NCCOE Focus Area |
|---------|-----------------|------------------|
| 2. Agent Identity Model | AC-2, IA-2, IA-4, IA-8 | 1 — Identification |
| 3. Authentication | IA-2, IA-5, SC-12, SC-23 | 1 — Identification, 3 — Delegation |
| 4. Authorization | AC-3, AC-6, AC-16, CM-7 | 2 — Authorization |
| 5. Delegation Model | AC-2, AC-3, AC-17, IA-2, IA-4 | 3 — Access Delegation |
| 6. Audit and Non-Repudiation | AU-2, AU-3, AU-6, AU-10, AU-11, AU-12, AU-14 | 4 — Logging and Transparency |
| 7. Human-in-the-Loop | AC-6, CM-3, CM-5, IR-4 | 2 — Authorization, 3 — Delegation |

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-25 | 0.1.0 | Initial release — NCCOE concept paper alignment, single-agent scope |

## Framework References

- NIST SP 800-53 Rev 5.2.0 (September 2024)
- NIST SP 800-63-4 Digital Identity Guidelines (December 2024)
- NIST AI RMF 1.0 (January 2023)
- NIST AI 600-1 Generative AI Profile (July 2024)
- NCCOE Accelerating the Adoption of Software and AI Agent Identity and Authorization — Concept Paper (February 2026)
- NIST CAISI AI Agent Standards Initiative (February 2026)
- OWASP Top 10 for Agentic Applications 2026 (December 2025)
- OAuth 2.0 Authorization Framework — RFC 6749
- OAuth 2.0 Token Exchange — RFC 8693
- JSON Web Token (JWT) — RFC 7519
- CISA Secure by Design Principles (2025)
- OMB M-25-21 (April 2025)
