---
trigger: always_on
---

# Full-Stack Coding Standards & Architectural Rules

## 1. Code Quality & Modularity
- **Modular Component Architecture**: Keep UI components small, modular, and single-purpose.
- **Strict Typing & Interfaces**: Declare explicit TypeScript interfaces or schema definitions for all API endpoints and component props.
- **Preserve Comments & API Contracts**: Never remove existing docstrings or change function signatures without updating caller sites across the codebase.

## 2. Dynamic Layout & Styling
- **Modern Styling System**: Use CSS modules or tailored HSL variables with modern layout practices (Flexbox/Grid). Avoid arbitrary hardcoded pixel magic numbers in dynamic layouts.
- **Aesthetic Excellence**: Incorporate responsive designs, harmonious color themes, clear typographic hierarchies, and micro-interactions.

## 3. Security & Environment Configuration
- **No Hardcoded Secrets**: Store environment keys and sensitive configuration in `.env` files.
- **Sanitize Inputs**: Validate incoming request payloads on the server side using schemas (e.g. Zod or Pydantic).
