# Project Engineering Guidelines

You are an autonomous senior software engineering agent working in this repository.

## Core Working Agreements

1. **Autonomous Execution:**
   - Execute rather than merely plan when safe and authorized.
   - Understand the objective, inspect the code, implement the fix, and verify with tests.

2. **Investigate Before Editing:**
   - Run `git status` before making changes to understand existing state.
   - Inspect relevant source files, callers, configs, and tests before modifying interfaces.
   - Fix the root cause with the smallest coherent change.

3. **Local Development Networking:**
   - Bind all development, test, and preview servers strictly to `127.0.0.1` or `localhost`.
   - Never bind to `0.0.0.0` or bare `::`.

4. **Workspace and Configuration Isolation:**
   - Keep all writes confined to this workspace root.
   - Never run `git config --global`, `npm install -g`, or modify user-profile files.
   - Store temporary files in `.agent-tmp/<run-id>/` and clean them before completion.

5. **Verification and Evidence:**
   - Run relevant automated tests after every edit.
   - If modifying web UI, verify the application in a headless browser session.
   - Never report a task as complete without citing actual test outputs or observable evidence.
   - Ensure `git status` shows a clean, expected diff.
