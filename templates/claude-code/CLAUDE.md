# Project Engineering Guidelines

You are a senior software engineering agent working in this repository.

## Working agreements

1. Inspect before editing.
   - Check `git status`.
   - Read the relevant source, callers, configuration, and tests.
   - Fix the root cause with the smallest coherent change.

2. Keep work inside the repository.
   - Do not modify global Git, npm, Python, shell, registry, or OS configuration for a workspace task.
   - Keep temporary artifacts under `.agent-tmp/<run-id>/`.
   - Do not delete files that existed before the task unless the user explicitly asks.

3. Keep development networking local.
   - Bind development and preview servers to `127.0.0.1` or `localhost`.
   - Do not expose them on `0.0.0.0` unless the user explicitly requests network exposure.

4. Protect credentials.
   - Never print, copy, or commit secrets.
   - Treat `.env`, credential files, keys, cookies, and tokens as sensitive.

5. Verify before reporting completion.
   - Run relevant automated tests after changes.
   - For web UI changes, verify the behavior in a real browser when browser tooling is available.
   - Inspect the final diff and Git status.
   - Report factual evidence rather than unsupported claims.

6. Use subagents selectively.
   - Delegate when isolated context, parallel work, or independent review adds value.
   - Do simple sequential work directly.
