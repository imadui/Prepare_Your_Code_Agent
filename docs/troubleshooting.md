# Troubleshooting Matrix

This guide provides a rapid lookup matrix for diagnosing and resolving common coding agent issues.

Follow the **Safe Next Step** column rather than applying ad-hoc workarounds or weakening workstation security controls.

---

## Diagnostic Matrix

| Symptom | Likely Layer | What to Check | Safe Next Step |
|---|---|---|---|
| **Provider returns HTTP 401 / Unauthorized** | Layer 1: Provider | Check whether the expected credential variable is present without printing its value. Use the doctor script or a shell presence check. | Re-export the environment variable. Verify API key status in the vendor web console. Never paste the key into the chat. |
| **Model returns HTTP 404 / Model Not Found** | Layer 1: Provider | Verify exact model spelling. Check whether your account/tier has access to the requested model. | Check model catalog via `/models` or CLI flags. Verify regional deployment names for Azure OpenAI or Vertex AI. |
| **Model returns HTTP 429 / Rate Limit Exceeded** | Layer 1: Provider | Account quota exhausted, monthly billing cap reached, or per-minute token threshold hit. | Check vendor billing dashboard. Add request retries with exponential backoff or switch to a fallback model. |
| **OpenCode CLI works but Desktop rejects the config** | Layer 2: Runtime | Compare CLI version, Desktop version, and Desktop local-server version before editing the config. | Update/align Desktop first. Do not downgrade a working V2 config just to satisfy an older sidecar. |
| **OpenCode starts healthy but `mcp list` shows no servers** | Layer 4: MCP lifecycle | Run `opencode api GET /api/info`, then `opencode reload`, wait briefly, and check `opencode mcp list` again. | Treat this as service/config reconciliation before rewriting `mcp.servers`. |
| **GitHub MCP fails but `gh auth status` is healthy** | Layer 4/6: MCP + GitHub | Check whether the MCP server is duplicating or misformatting authentication headers. | Use `gh` as the operational fallback and diagnose MCP separately. Do not print/copy PATs into logs. |
| **Browser automation opens a clean unauthenticated session** | Layer 9: Browser | Determine whether the user asked for an already-open authenticated Edge/Chrome tab. | Prefer supported attach/extension flow; if unavailable, use a dedicated persistent automation profile. Do not copy browser cookie/login databases. |
| **Playwright works but is slow/heavy as an MCP** | Layer 4/9: Tooling | Compare the task with the tool surface actually needed. | Use Playwright CLI for normal interaction; keep Chrome DevTools MCP for console/network/runtime; enable full Playwright MCP only when useful. |
| **MCP server crashes or fails to spawn on startup** | Layer 4: MCP | Inspect the runtime's MCP configuration: Codex `config.toml`, Claude Code `claude mcp` / `.mcp.json`, or OpenCode `opencode.json`. Ensure the server command is installed in `PATH`. | Test the launch command manually, then inspect the runtime's MCP status before weakening permissions. |
| **MCP authentication gets stuck in an infinite OAuth loop** | Layer 4: MCP | Callback port conflict or expired local OAuth token cache. | Check the configured callback port and current MCP authentication status. If cached OAuth state appears stale, use the product's supported re-authentication/logout flow rather than manually deleting credential files unless the documentation specifically instructs it. |
| **GitHub CLI (`gh`) prompts for login or reports invalid token** | Layer 6: GitHub | Keyring credentials out of sync or expired personal access token. | Run `gh auth status`. Refresh credentials using the normal GitHub CLI authentication flow. Avoid printing or copying tokens into logs or chat. |
| **Playwright browser automation fails to launch** | Layer 9: Browser | Missing browser/channel, enterprise browser policy, or missing local Playwright runtime. | First try an installed browser channel (Chrome/Edge) when appropriate. Install Playwright-managed browser binaries only when the workflow actually needs them. |
| **Local development server triggers Windows Firewall popup** | Layer 9: Browser / Guardrails | Dev server is binding to `0.0.0.0` or bare `::` instead of `127.0.0.1`. | Stop the server. Pass `--host 127.0.0.1` or edit server config to explicitly bind to `127.0.0.1`. Never disable the firewall. |
| **Agent attempts to modify `~/.gitconfig` or global npm packages** | Layer 11: Guardrails | Agent instructions or permissions lack local configuration constraints. | Add the rule to `AGENTS.md` / `CLAUDE.md` and enforce it with the runtime's permission layer where supported. |
| **Temporary files and scratch scripts accumulate in project root** | Layer 11: Guardrails | Agent is generating temporary files directly in `cwd`. | Enforce `.agent-tmp/<run-id>/` in project instructions (`AGENTS.md` / `CLAUDE.md`) and keep `.agent-tmp/` ignored. |
| **Subagent fails to spawn or times out** | Layer 10: Subagents | Runtime configuration, concurrency, or agent discovery is wrong. | In Codex, inspect `[agents]`; in Claude Code, verify `.claude/agents/` and run `claude doctor`; in OpenCode, inspect `agents`. |
| **Unit tests pass but web UI renders blank or fails on click** | Layer 8 & 9: Verification | Frontend client-side rendering error, missing bundle asset, or broken hydration. | Reproduce with Playwright CLI, then inspect console/network with Chrome DevTools MCP when deeper diagnostics are needed. |
| **Agent exhibits confusion or hallucinations after multiple turns** | Layer 3 & 4: Context | Context window exhaustion or tool schema overload (> 15 tools active). | Disable unused MCP servers. Use a leaner tool profile (`MINIMAL` or `ENGINEERING`). Run `/compact` to summarize history. |
