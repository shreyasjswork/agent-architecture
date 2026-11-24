# Multi-Provider Orchestration and T3 Code Integration

This document outlines the orchestration framework, provider allocation model, and sustainable token governance mechanisms implemented across the engineering workstation.

## The T3 Code Orchestration Layer

T3 Code serves as the central workstation orchestrator. It manages workspace environments, tool execution brokers, and agent thread lifecycles across multiple AI providers.

### 1. Task-Bounded Thread Lifecycle
A critical optimization in multi-agent systems is managing context expansion:
- **The Problem:** Long-lived threads that run dozens of turns accumulate tool outputs, command results, and code diffs. Within 10 to 15 turns, thread context can reach 350K to 450K tokens. When a model compacts, the summary briefly drops to ~25K tokens, but active engineering turns rapidly rebuild the context back to 400K+ tokens. Re-sending 400K tokens per turn quickly burns through provider 5-hour rolling rate limits and token quotas.
- **The Solution:** Bounding thread lifetimes to discrete tasks or milestones. When a feature or work item completes, the orchestrator records a concise, durable handoff artifact and starts a fresh top-level thread (`t3_thread_launch`). A fresh thread starts at 15K to 30K tokens and finishes in 10 to 15 turns without ever approaching the 450K threshold, reducing overall token throughput by 10x to 15x.

### 2. Worktree Isolation
To prevent dirty workspace state and cross-task interference, independent tasks run in isolated Git worktrees (`isolation: 'worktree'`). Changes remain isolated on dedicated feature branches without mutating the primary working tree or affecting concurrent processes.

### 3. Asynchronous Queuing and Mid-Turn Steering
T3 Code provides native queue management (`t3_queue`):
- Non-blocking execution allows completed child outputs and background task notifications to queue without interrupting active turns.
- Queued deliveries can be promoted to steer running turns (`promote_to_steer`) when relevant, avoiding unnecessary polling loops or idle waits.

## Provider Allocation Matrix

The workstation coordinates five distinct provider tiers, routing tasks based on cost class, capability, and rate-limit boundaries:

| Provider Tier | Models Available | Purpose and Cost Classification |
| :--- | :--- | :--- |
| **Antigravity A1 / A2** | Gemini 3.8 Flash | **Unmetered workhorse.** Used for routine code changes, test authoring, lint wrappers, inventory tasks, and first-round reviews. |
| **Antigravity A3 / A4** | Hydrogen, Neon | **Metered frontier models.** Reserved for high-risk reviews, deep architectural audits, and cryptographic or complex security logic. |
| **OpenAI / Codex** | Sol 6.2, Terra, Luna | **Standard code and refactoring.** Sol 6.2 Medium is used for standard reviews; Terra and Luna handle batch edits and bounded background tasks. |
| **Anthropic / Claude** | Opus 5.5, Sonnet 5.5 | **System evolution and architecture.** Used for deep codebase refactoring, architectural planning, and complex system debugging. |
| **OpenCode Public** | OpenCode Free Tier | **Exploratory tasks.** Used as a fallback tier for non-critical, rate-tolerant background work. |

## Sustainable Token and Quota Governance

To ensure steady productivity without hitting provider rate limits or quota lockouts, the workstation enforces six strict guardrails:

### 1. Bounded Orchestrator Concurrency (Max 1 to 2 Active Tasks)
Running 10 or more orchestrator threads simultaneously causes severe cascading fan-out. Each orchestrator spawns sub-agents and reviewers, resulting in 30 to 40 concurrent model processes. This causes:
- Immediate HTTP 429 rate limit lockouts because all threads share the same account quota pool.
- Severe local machine thrashing from dozens of spawned Node and tool processes.
- Git merge and rebase churn when multiple branches land concurrently.
The workstation caps active task orchestrators at **1 to 2 simultaneous threads**. Additional tasks wait in the request ledger and execute sequentially.

### 2. Reasoning Effort Tiering
Hidden reasoning and thinking tokens generate significant output volume. The workstation enforces:
- `medium` reasoning effort for routine code implementation, bug fixes, and standard code reviews.
- `high` or `xhigh` reasoning effort strictly reserved for High-risk blast radius tasks (authentication, credential management, financial calculations, migrations, and security policies).

### 3. Reviewer Roster Tiering
Rather than running fixed panels of expensive frontier models for every change:
- **Low-Risk:** 1 reviewer only, routed to unmetered Gemini A1/A2 or free tier (zero paid Sol draw).
- **Medium-Risk:** 1 unmetered reviewer + 1 standard reviewer (Sol at `medium` reasoning, or A3/A4 Neon/Hydrogen for deep critique).
- **High-Risk:** 1 to 2 rounds pairing frontier models (Sol 6.2 or A3/A4 Neon/Hydrogen) with Gemini A1/A2.
- **Strict Early Exit:** A clean first round ends review immediately. Round 2 is never dispatched just because budget permits.

### 4. Deterministic Pre-Flight Gate
Before any LLM reviewer is dispatched, local automated checks (`test`, `lint`, `typecheck`, `build`) must pass cleanly. If deterministic checks fail, review dispatch is blocked until the author fixes the failure locally, eliminating token waste on broken code.

### 5. Lean Review Briefs
Prompts sent to child workers and reviewers must contain only `git diff --stat`, the scoped diff, target file paths, and explicit acceptance criteria. Pasting full conversation transcripts, multi-megabyte terminal logs, or duplicated policy files into prompts is strictly prohibited.
