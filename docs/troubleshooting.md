# Troubleshooting Matrix

This guide provides a rapid lookup matrix for diagnosing and resolving common coding agent issues.

Follow the **Safe Next Step** column rather than applying ad-hoc workarounds or weakening workstation security controls.

---

## Diagnostic Matrix

| Symptom | Likely Layer | What to Check | Safe Next Step |
|---|---|---|---|
| **Provider returns HTTP 401 / Unauthorized** | Layer 1: Provider | Check whether the API key is set in the current shell environment (`echo $OPENAI_API_KEY` or doctor script). | Re-export the environment variable. Verify API key status in the vendor web console. Never paste the key into the chat. |
| **Model returns HTTP 404 / Model Not Found** | Layer 1: Provider | Verify exact model spelling. Check whether your account/tier has access to the requested model. | Check model catalog via `/models` or CLI flags. Verify regional deployment names for Azure OpenAI or Vertex AI. |
| **Model returns HTTP 429 / Rate Limit Exceeded** | Layer 1: Provider | Account quota exhausted, monthly billing cap reached, or per-minute token threshold hit. | Check vendor billing dashboard. Add request retries with exponential backoff or switch to a fallback model. |
| **MCP server crashes or fails to spawn on startup** | Layer 4: MCP | Inspect command and arguments in `config.toml` or `opencode.json`. Ensure `npx` or the server binary is installed in `PATH`. | Test running the command manually in your terminal. Check that node/python dependencies are installed. |
| **MCP authentication gets stuck in an infinite OAuth loop** | Layer 4: MCP | Callback port conflict or expired local OAuth token cache. | Set a fixed port in config (e.g., `mcp_oauth_callback_port = 8080`) or clear expired token cache under `$CODEX_HOME`. |
| **GitHub CLI (`gh`) prompts for login or reports invalid token** | Layer 6: GitHub | Keyring credentials out of sync or expired personal access token. | Run `gh auth status`. Refresh credentials using `gh auth refresh` or export `GITHUB_TOKEN` for the current process. |
| **Playwright browser automation fails to launch** | Layer 9: Browser | Missing browser binaries or system libraries. | Run `npx playwright install chromium` to download local headless browser binaries. |
| **Local development server triggers Windows Firewall popup** | Layer 9: Browser / Guardrails | Dev server is binding to `0.0.0.0` or bare `::` instead of `127.0.0.1`. | Stop the server. Pass `--host 127.0.0.1` or edit server config to explicitly bind to `127.0.0.1`. Never disable the firewall. |
| **Agent attempts to modify `~/.gitconfig` or global npm packages** | Layer 11: Guardrails | Agent instructions lack local configuration constraints. | Add explicit rules in `AGENTS.md`: "Use `git config --local`" and "Install dependencies locally in `.venv` or `node_modules`". |
| **Temporary files and scratch scripts accumulate in project root** | Layer 11: Guardrails | Agent is generating temporary files directly in `cwd`. | Enforce `.agent-tmp/<run-id>/` directory convention in `AGENTS.md`. Add `.agent-tmp/` to `.gitignore`. |
| **Subagent fails to spawn or times out** | Layer 10: Subagents | Concurrency limit reached or subagents are disabled in configuration. | Check `agents.enabled = true` and `max_concurrent_threads_per_session` in `config.toml`. Ensure completed subagents are closed. |
| **Unit tests pass but web UI renders blank or fails on click** | Layer 8 & 9: Verification | Frontend client-side rendering error, missing bundle asset, or broken hydration. | Inspect browser console logs and network failures using Playwright MCP before declaring the task complete. |
| **Agent exhibits confusion or hallucinations after multiple turns** | Layer 3 & 4: Context | Context window exhaustion or tool schema overload (> 15 tools active). | Disable unused MCP servers. Use a leaner tool profile (`MINIMAL` or `ENGINEERING`). Run `/compact` to summarize history. |
