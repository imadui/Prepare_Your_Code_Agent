# Project Engineering Guidelines (OpenCode)

## Working Agreements

- **Inspect First:** Check `git status` and existing code before proposing changes.
- **Root Cause Solutions:** Prefer robust fixes over symptom patches.
- **Loopback Servers:** Bind all local dev servers strictly to `127.0.0.1`.
- **Clean Diff:** Run project linters and tests before requesting review.
- **No Hardcoded Secrets:** Read all credentials from `{env:...}` variables.

## External Rules
When working on specific subsystems, load the corresponding guidelines using your Read tool:
- Security & Privacy: @docs/guardrails.md
- Tool Configuration: @docs/tools.md
