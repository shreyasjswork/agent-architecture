# Skillset Architecture

This document describes the organization, discovery mechanism, and execution lifecycle of the agent skillset library powering the multi-provider engineering workstation.

## Overview

The skillset library consists of 543 modular engineering skills, with 87 core discoverable skills projected directly into provider startup catalogs. Rather than relying on static prompt instructions or bloated system prompts, skills are organized as modular folders containing instructions, scripts, templates, and reference guides that load on demand when triggered by specific task requirements.

```text
W:/DevTools/Shared/agents/skills/
├── ai-agents/            # Agent SDKs, workflows, and task orchestration
├── backend/              # API patterns, async processing, service architecture
├── cloud-devops/         # Cloudflare, container runtimes, infrastructure as code
├── data-ai/              # Data analysis, schema processing, retrieval systems
├── database/             # PostgreSQL design, query optimization, migrations
├── frontend/             # Design systems, React/Astro, state management, UI tokens
├── mobile/               # Cross-platform and responsive layout standards
├── security/             # Security audits, dependency analysis, secret management
└── testing-qa/           # Headless browser testing, unit test fixtures, mock setups
```

## Domain Specialization

### 1. Frontend Engineering and Design Systems
- **Design Token Parity:** Eliminates arbitrary CSS hex codes and magic spacing. All visual values map programmatically to semantic theme variables and design tokens.
- **4-State Component Pattern:** Every component presenting dynamic data must implement Default, Loading Skeleton, Empty, and Error states.
- **Responsive Geometry:** Explicit verification across target breakpoints (375px mobile, 768px tablet, 1280px+ desktop) without regression.
- **Accessibility Compliance:** Semantic HTML landmarks, keyboard navigation traps for overlays, and ARIA state management.

### 2. Backend Architecture and Data Governance
- **High-Precision Calculations:** Decimal math is mandatory for monetary values, financial metrics, and exchange rates. Floating point arithmetic is strictly forbidden for calculations.
- **Presentation Separation:** Frontend code operates strictly as a presentation layer. All aggregation, filtering, and data transformations reside in backend services.
- **Upstream Data Masking:** Backend proxies strip upstream provider headers, internal identifiers, and third-party metadata before delivering payloads to the client.

### 3. Database Engineering and Storage
- **Schema Contracts:** Version-controlled migrations with explicit rollback definitions.
- **Optimistic Concurrency:** Row versioning and conditional writes prevent state corruption during concurrent updates.
- **Query Optimization:** Explain plan verification, partial indexes for filtered queries, and connection pool sizing.

### 4. Cloud Infrastructure and Edge Workflows
- **Edge Runtimes:** Serverless worker orchestration, key-value stores, and durable objects for stateful coordination.
- **Asynchronous Pipelines:** Producer-consumer queues with explicit retry policies, backpressure management, and dead-letter queues.

### 5. Quality Assurance and Headless Browser Verification
- **Enforced Headless Automation:** Browser verification runs through an enforced headless Playwright runner (`headless_browser.py`). Routine automated checks never open visible windows or steal operating system window focus.
- **Deterministic Testing:** Unit, integration, and contract tests gate changes before any review round begins.

## Dynamic Discovery and Routing

To prevent prompt bloat and keep context windows compact, skills follow a two-tier projection model:

1. **Core Discoverable Skills (87 Core):**
   - High-frequency skills indexed in the primary provider configuration (`discovery-core.json`).
   - Descriptions include explicit trigger cues (such as "Use when asked to...", "Activate for...") that allow language models to match user intent directly from natural-language requests.
   - Kept under a strict character budget to ensure total startup instructions across all providers remain well within context limits.

2. **On-Demand and Deep Reference Skills (456 Skills):**
   - Specialized procedural skills (e.g., deep performance profiling, specific database migration procedures, cloud security hardening).
   - Loaded dynamically by workflows or parent orchestrators when a task enters a specific phase.

## Skill Frontmatter Contract

Each skill maintains a standardized `SKILL.md` document with YAML frontmatter:

```yaml
---
name: frontend-design
description: "Use when creating, modifying, or reviewing user-facing UI components. Enforces design token parity, 4-state component architecture, and responsive layouts."
---
```

A deterministic linter (`lint_rules.py`) validates that all skill names match their directory names, descriptions include valid trigger cues, and total menu characters remain within strict context budgets.
