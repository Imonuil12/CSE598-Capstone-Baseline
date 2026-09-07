---
trigger: always_on
---

# Agentic Efficiency & Anti-Looping Rules

## 1. Token Conservation & Context Hygiene
- **Avoid Unnecessary Full-File Scans**: Use targeted search tools (`grep_search`) before inspecting files with `view_file`.
- **Restrict Slice Viewing**: Limit `view_file` line ranges to relevant blocks rather than viewing 800-line windows repeatedly.
- **Do Not Re-summarize Context**: When completing sub-tasks or updating artifacts, do not dump long recaps into chat responses. State key findings or diffs concisely.

## 2. Anti-Looping & Error Handling Protocols
- **2-Attempt Limit on Command Retries**: If a shell command or build fails twice with the same output, STOP immediately. Do NOT run the exact same command a third time.
- **Inspect Empirical Logs First**: Always inspect exact log traces before forming diagnostic hypotheses. Never guess errors.
- **No Superficial Symptom Patches**: Do not swallow exceptions or add dummy mock fallbacks to make a test green unless explicitly instructed. Fix the root cause or ask for clarification.

## 3. Execution Verification & Incremental Steps
- **Incremental Edits**: Make discrete, logical code edits. Run relevant linting/testing commands after each edit step to verify correctness.
- **Never Declare Success Without Empirical Verification**: Always verify that server builds or unit tests compile and run before marking a task complete.
