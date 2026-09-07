# Agent Workspace Configuration

Welcome to the project workspace! This repository is configured with **Agentic AI Customizations** to ensure maximum development speed, low token consumption, zero looping, and consistent code quality.

## Workspace Customization Overview

- **Rules (`.agents/rules/`)**:
  - [`agentic_efficiency.md`](file://.agents/rules/agentic_efficiency.md): Enforces anti-looping rules, 2-retry limits, empirical log inspection, and context hygiene.
  - [`coding_standards.md`](file://.agents/rules/coding_standards.md): Defines modularity, TypeScript/Schema rules, dynamic styling, and security guardrails.

- **Skills (`.agents/skills/`)**:
  - [`fullstack-feature-workflow`](file://.agents/skills/fullstack-feature-workflow/SKILL.md): On-demand runbook for building full-stack features phase by phase.

## Agent Guidelines for This Project
1. **Follow Progressive Disclosure**: Keep system context lean. Only load specialized skills when executing relevant multi-step workflows.
2. **Execute In Phases**: For non-trivial features, create an Implementation Plan before altering code.
3. **Verify Empirical Output**: Run server build and verification commands after changes. Never assume code works without test/run execution.
