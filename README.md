# Multi-Agent Architecture and Engineering System

A public reference for the multi-provider coding architecture and agent orchestration system I use to build, verify, and ship production software. It documents my complete skillset organization, multi-model coordination in T3 Code, token governance policies, and deterministic release pipelines.

```
                              +---------------------------------------+
                              |         User Task Intake & Scope      |
                              +---------------------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |      T3 Code Workstation Coordinator  |
                              |   (Task-Bounded Threads & Worktrees)  |
                              +---------------------------------------+
                                     /            |            \
                                    /             |             \
                                   v              v              v
+------------------------------------+  +--------------------+  +------------------------------------+
|    Antigravity A1/A2 (Unmetered)   |  |   OpenAI / Codex   |  |     Anthropic / Claude Opus/Sonnet |
|   Routine Code & First-Pass Review |  |  Core Engineering  |  |  Deep Architecture & Refactoring   |
+------------------------------------+  +--------------------+  +------------------------------------+
                                   \              |              /
                                    \             v             /
                                     +-------------------------+
                                     |  Frontier Verification  |
                                     |  Antigravity A3/A4 or   |
                                     |       Sol 6.2 High      |
                                     +-------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |    Deterministic Pre-Flight Gate      |
                              |   (test, lint, typecheck, build)      |
                              +---------------------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |      Blind Independent Review         |
                              |   (Max 2 Rounds, Early Exit)          |
                              +---------------------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |    Verifiable Release Receipt         |
                              |     (Frozen Git Commit Parity)        |
                              +---------------------------------------+
```

## System Pillars

### 1. [The Skillset Architecture](docs/skillset-architecture.md)
The system operates on a curated library of **543 modular engineering skills** (with **87 core discoverable skills** projected into provider startup menus). Skills load dynamically based on trigger cues rather than bloating static system prompts:
- **Frontend & Design Systems:** Design token programmatic parity, 4-state component architecture (Default, Loading Skeleton, Empty, Error), strict null safety, and responsive geometry across mobile, tablet, and desktop breakpoints.
- **Backend Architecture & Data Governance:** Strict Decimal arithmetic for financial metrics and monetary values, presentation separation, and upstream data source masking.
- **Database & Cloud Infrastructure:** Schema contracts, optimistic concurrency control, edge runtimes (Cloudflare Workers, Durable Objects, Queues), and query optimization.
- **Testing & Headless Verification:** Enforced headless Playwright runner (`headless_browser.py`) without focus-stealing windows, deterministic unit/integration test suites, and regression checks.

### 2. [Multi-Provider Orchestration and T3 Code](docs/multi-provider-orchestration.md)
T3 Code acts as the central workstation orchestrator, coordinating models across providers based on capability, cost class, and rate-limit boundaries:
- **Task-Bounded Thread Lifecycles:** Threads are retired at milestone boundaries. Long-lived threads accumulate hundreds of thousands of tokens, causing models to repeatedly cycle through 450K-token compaction loops and re-send massive context per turn. Retiring threads upon task completion and starting clean threads (`t3_thread_launch`) yields a 10x to 15x reduction in token throughput.
- **Provider Matrix:**
  - **Antigravity A1 / A2 (Gemini 3.8 Flash):** Unmetered workhorse for routine code edits, test suites, formatting, and initial review passes.
  - **Antigravity A3 / A4 (Hydrogen, Neon):** Metered frontier reasoning models for high-risk reviews, deep architectural audits, and cryptographic logic.
  - **OpenAI / Codex (Sol, Terra, Luna):** Standard code generation, structural refactoring, and medium-reasoning reviews.
  - **Anthropic / Claude (Opus 5.5, Sonnet 5.5):** System-level architectural design and codebase evolution.
- **Token & Quota Governance:**
  - **Reasoning Effort Tiering:** Routine tasks and reviews cap reasoning effort at `medium`, reserving `high` and `xhigh` strictly for high-risk blast radius.
  - **Bounded Concurrency:** Concurrency is capped at 1 to 2 active orchestrators simultaneously to prevent account-wide 429 rate limit lockouts and machine resource exhaustion.
  - **Lean Briefs:** Child agents receive only `git diff --stat`, scoped diffs, target paths, and explicit acceptance criteria.

### 3. [Review and Release Pipeline](docs/review-and-release-pipeline.md)
All changes that produce deliverables pass through a formal verification pipeline:
- **Deterministic Pre-Flight Gate:** Local automated checks (`test`, `lint`, `typecheck`, `build`) must pass before an LLM reviewer is dispatched, preventing token waste on broken code.
- **Blast-Radius Risk Tiers:**
  - **Low:** 1 round only, unmetered Gemini A1/A2 or free tier (zero paid Sol draw).
  - **Medium:** 1 to 2 rounds, unmetered Gemini + standard reviewer at `medium` reasoning.
  - **High:** 1 to 2 rounds, frontier Sol 6.2 or Antigravity A3/A4 (Neon/Hydrogen) paired with Gemini A1/A2.
- **Blind Independent Review:** Reviewers inspect frozen commit hashes and requirements without author defenses.
- **Reconciliation Ledger & Cap:** Every finding is fixed or refuted with evidence. Review is capped at at most 2 rounds, with immediate early exit when round 1 passes cleanly. Disagreements at the cap escalate to a human engineer.
- **Release Receipt:** Generates a cryptographic release receipt (`release.json`) bound to the exact commit SHA before merging.

## Visual Flowchart

Open [the architecture diagram](architecture.mmd) to view the complete Mermaid flowchart detailing task intake, orchestration, verification, review, and release.

## Running the Release Checker

The repository includes a reference checker that validates release candidate commits against task scope and reviewer approvals:

```bash
# Verify release candidate against receipt
python scripts/check_release.py PATH_TO_WORKTREE PATH_TO_RECEIPT

# Run checker test suite
python -m unittest discover -s tests
```

## Repository Structure

```text
├── architecture.mmd              # Full Mermaid architectural flowchart
├── README.md                     # Architecture overview and system pillars
├── docs/
│   ├── skillset-architecture.md  # 543-skill library, domains, and dynamic routing
│   ├── multi-provider-orchestration.md # T3 Code, provider matrix, and quota governance
│   └── review-and-release-pipeline.md  # Pre-flight gates, risk tiers, and 2-round cap
├── examples/
│   └── release.json              # Sample verifiable release receipt
├── scripts/
│   └── check_release.py          # Reference release boundary verification script
└── tests/
    └── test_check_release.py     # Unit tests for the release verification script
```
