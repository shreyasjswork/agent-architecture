# Review and Release Pipeline

This document details the quality assurance, independent code review, and release verification pipeline that governs all production changes.

## Core Principles

1. **Blast Radius Sets the Bar:** Review depth and model allocation scale with the change's blast radius, not author preference.
2. **Deterministic Checks Before Models:** Deterministic command-line tests and linting gate changes before any model reviewer is dispatched.
3. **Independent Discovery:** Initial code review is conducted blind. Reviewers evaluate the frozen commit diff and requirements without author defenses or prior analysis.
4. **Finite Review Budget:** At least 1 and at most 2 reviewer-rounds per work item. Round 1 clean pass ends review immediately.
5. **Verifiable Audit Receipts:** Code does not merge without a cryptographically verifiable release receipt bound to the frozen commit hash.

## 1. Blast Radius Risk Tiers

The change sets the risk tier, determining model selection and review rounds:

| Risk Tier | Scope and Examples | Model Allocation and Rounds |
| :--- | :--- | :--- |
| **Low** | Documentation, copy, isolated unit tests, formatting, internal flags, small non-breaking fixes. | **1 round only.** Routed to unmetered Gemini A1/A2 or free tier. Zero paid model draw. |
| **Medium** | Standard feature implementation, shared components, presentation layer, API consumers. | **1 to 2 rounds.** Unmetered Gemini A1/A2 paired with a standard reviewer (Sol at `medium` reasoning, or A3/A4 Neon/Hydrogen). |
| **High** | Auth, security guards, credentials, payments, database migrations, schema contracts, financial calculations, diffs over 1,000 lines. | **1 to 2 rounds.** Frontier models (Sol 6.2 High, or Antigravity A3/A4 Neon/Hydrogen) paired with Gemini A1/A2. |

## 2. The Deterministic Pre-Flight Gate

Before any review task is spawned:
1. The author runs local automated verification:
   - Unit and integration test suites.
   - Linter and style checks.
   - Static type checking (`tsc` or `mypy`).
   - Incremental build verification.
2. If any deterministic check fails, review dispatch is immediately aborted. The author must fix the regression locally first. Model tokens are never spent reviewing code with broken builds or failing tests.

## 3. Blind Independent Review

When pre-flight checks pass:
1. **Freeze the Candidate:** The change is committed on the feature branch, producing a stable Git commit hash.
2. **Lean Brief Dispatch:** The reviewer is given only the frozen Git range, `git diff --stat`, the scoped diff, and explicit acceptance criteria.
3. **Discovery Independence:** Reviewers run independent code audits, AST inspections, and headless browser checks. The reviewer delivers a structured findings report containing:
   - Finding IDs.
   - Severity tags (Important, Nit, Pre-existing).
   - Exact source locations and reproduction steps.
   - Actual versus expected behavior.

## 4. Parent Triage and the Reconciliation Ledger

The author adjudicates every finding in a formal reconciliation ledger:
- **Accepted:** The author implements the fix, re-runs local tests, and commits a fix revision.
- **Rejected with Evidence:** The author provides code or specification evidence proving the finding is invalid or unreachable.
- **Pre-existing:** Pre-existing bugs not introduced by the change are documented but do not block the current release unless within scope.

An item cannot merge or release while an Important bug or security vulnerability remains open.

## 5. Fix Verification and Early Exit

- **Early Exit:** If Round 1 produces an approval with no Important findings, the review pipeline concludes immediately.
- **Round 2 (Fix Verification):** If fixes were required, the original reviewer re-inspects only the fix diff. The reviewer verifies that the finding is resolved and that no regressions were introduced.
- **Strict Cap at Round 2:** If disagreements remain after Round 2, the process halts. The author marks the item blocked and escalates to a human engineer with the reconciliation ledger. Nested review loops and fourth-round attempts are strictly prohibited.

## 6. The Release Boundary and Receipt Verification

Before merging or publishing:
1. A release receipt (`release.json`) records the exact candidate commit hash, author identity, reviewer identity, and check outcomes.
2. The reference checker (`scripts/check_release.py`) verifies:
   - The frozen Git range matches the authorized scope paths.
   - No unauthorized files or secrets leaked into the diff.
   - The reviewer approved the exact commit hash being released.
3. Once verified, the candidate commit merges into the base branch, and the task-bounded thread is cleanly retired.
