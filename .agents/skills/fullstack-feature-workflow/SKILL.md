---
name: fullstack-feature-workflow
description: Step-by-step workflow for implementing, testing, and verifying full-stack features efficiently without getting stuck in loops.
---

# Full-Stack Feature Development Runbook

Use this skill when tasked with building a new end-to-end full-stack feature (API + Frontend component).

## Phase 1: Context & Dependency Analysis
1. Inspect existing project APIs and data models.
2. Check schema definitions before modifying backend routes or UI state.

## Phase 2: Backend First Implementation
1. Define/Update data models or schema types.
2. Implement backend endpoint(s) with request validation and error handling.
3. Test backend endpoint locally using `curl` or unit tests before touching frontend code.

## Phase 3: Frontend Integration
1. Build reusable UI components.
2. Integrate API calls with clear loading, error, and empty states.
3. Verify interactive behavior and responsive layout.

## Phase 4: Verification Checklist
- [ ] Backend endpoint responds correctly to valid inputs.
- [ ] Backend handles invalid/edge inputs gracefully (e.g. 400 Bad Request).
- [ ] UI displays loading, error, and success states properly.
- [ ] No console errors or unhandled promises exist.
