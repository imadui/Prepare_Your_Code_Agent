# Project Engineering Guidelines (OpenCode)

## Working Agreements

- **Inspect First:** Check `git status` and existing code before proposing changes.
- **Root Cause Solutions:** Prefer robust fixes over symptom patches.
- **Loopback Servers:** Bind all local dev servers strictly to `127.0.0.1`.
- **Clean Diff:** Run project linters and tests before requesting review.
- **No Hardcoded Secrets:** Read all credentials from `{env:...}` variables.

## Supporting Guidelines
Read the relevant repository guidance when the task needs it:
- Security and privacy work: `docs/guardrails.md`
- Tool or MCP configuration: `docs/tools.md`

Do not assume that mentioning a path automatically loads it; explicitly read the file when it is relevant.
