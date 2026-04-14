---
name: self-improvement
description: The universal self-evolution engine for Gemini CLI. Manages cross-project behavioral refinement and project-specific logic logging.
---

# Gemini CLI Universal Self-Improvement Protocol

## 0. Multi-Project Scope
This skill is GLOBAL. It governs the agent`'s evolution across all workspaces.

## 1. Dual-Layer Logging Strategy
- **Global Logs ($HOME/.gemini/learnings/)**:
  - `SOUL.md`: General behavioral principles (e.g., \"Be concise\", \"Windows/PS compliance\").
  - `TOOLS.md`: Global tool gotchas (e.g., \"Use write_file for complex JSON\").
  - `GLOBAL_PATTERNS.md`: Recurring logic structures found across different projects.
- **Local Logs (./.learnings/)**:
  - `LEARNINGS.md`: Project-specific logic, corrections, and conventions.
  - `ERRORS.md`: Technical debt and specific tool failures in this workspace.

## 2. Trigger Events
The agent MUST invoke this protocol when:
- **Critical Failure**: Any command fails or a user denies a crucial execution.
- **Explicit Correction**: User says \"No\", \"Wrong\", \"Actually...\", \"That`'s outdated\".
- **Pattern Recognition**: A mechanism (logic/UI/API) is encountered for the 3rd time.
- **Session Wrap-up**: Final act before ending the workday.

## 3. Implementation Rules (Windows/win32)
- ALWAYS use Python with `encoding=`'utf-8-sig`' for file operations to ensure data integrity.
- Use `save_memory` ONLY for cross-session global facts, NOT for transient session data.

## 4. Promotion & Evolution
- **Local -> Global**: During session wrap-up, identify project learnings that have universal value and move them to Global Logs.
- **Global -> Skill**: If a Global Pattern is highly reusable, propose creating a new Skill with `skill-creator`.
