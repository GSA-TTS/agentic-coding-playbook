---
title: "Agent Context Loading Guide (Project)"
description: "Compact routing document for AI agents working in this project — read this FIRST to determine which documents to load for your current task"
status: canonical
tier: 1
load_priority: "always"
audience: "all"
keywords: ["context", "loading", "routing", "progressive-disclosure"]
related_files: ["AGENTS.md", "docs/CODING_PRACTICES.md"]
review_cycle: "quarterly"
---

<!-- LOAD: always — Agents MUST read this document first. It is the entry point for all tasks. -->

# Agent Context Loading Guide

> **Purpose:** Minimize token usage while ensuring compliance. Load only what your task requires.

## Prerequisite: Universal Behavioral Contract

This project layers on top of the **Federal AI Agent Behavioral Best Practices**
(the universal `AGENTS.md`), which is expected to already be available to your
agent (see the Prerequisite section of this project's `AGENTS.md`). If it is not
available, STOP and follow the instructions in `AGENTS.md` before loading
anything else.

## Loading Rules

1. **Always load** this file, the project `AGENTS.md`, and `docs/CODING_PRACTICES.md`
2. **Match keywords** from your task to the documents below
3. **Load on demand** — do NOT load all documents preemptively
4. **Security is non-negotiable** — when in doubt, load the relevant doc rather than guessing

## Always Load

These define the behavioral contract for this project. Load for **every task**.

| Document | What It Covers |
|----------|----------------|
| `AGENTS.md` | Project-specific agent rules; references the universal contract |
| `docs/CODING_PRACTICES.md` | Secure coding: input validation, secrets, dependencies, architecture, TDD, SOLID |
| `docs/CODING_STANDARDS_COMPACT.md` | **Code generation shortcut** — load INSTEAD of full CODING_PRACTICES.md for routine code tasks |

## Load On Demand

| Document | Load When Task Involves |
|----------|------------------------|
| `docs/risk-assessment.md` | Performing a risk assessment |
| `checklists/pre-deployment.md` | Running the pre-deployment checklist |

## Skills — Load Only When Invoked

Skills are self-contained procedures in `skills/*/SKILL.md`. Load the relevant
skill only when executing that workflow.

> For the universal behavioral rules (identity, least privilege, data protection,
> prompt-injection defense, meta-constraints, engineering discipline), see the
> universal `AGENTS.md` referenced by this project's `AGENTS.md`.
