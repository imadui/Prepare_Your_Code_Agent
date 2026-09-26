# OpenCode V2 Configuration and Operations Guide

OpenCode is a provider-agnostic coding agent available as a terminal interface, desktop app, and web app.

This guide targets **OpenCode V2** and is written as an operational playbook. The important lesson is that a valid config is only one layer: provider resolution, Desktop/CLI version alignment, background service state, MCP lifecycle, browser tooling, and validation all need to work together.

For the real-world recovery paths behind this guide, also read [field-tested-fallbacks.md](field-tested-fallbacks.md).

---

## 1. Install and verify the runtime

For the V2 CLI:

```bash
npm install -g @opencode/cli
opencode --version
```

On Windows, Desktop and CLI can be installed separately. **Do not assume they are the same build.** Verify each one before changing a configuration that already works.

Launch from a repository:

```bash
cd /path/to/project
opencode
```

Useful first commands:

```bash
opencode --version
opencode debug config
opencode debug agents
opencode models
opencode mcp list
```

If a minimal model call does not work, stop there and fix provider/runtime connectivity before adding tools.

---

## 2. Use V2 configuration consistently

OpenCode V2 uses:

- `providers`
- `agents`
- ordered `permissions`
- `mcp.servers`

Do not mix those with legacy V1 singular fields in a new starter config.

Global config:

```text
~/.config/opencode/opencode.jsonc
```

Project config:

```text
<repo>/opencode.jsonc
<repo>/.opencode/opencode.jsonc
```

OpenCode merges configuration by scope. Keep global defaults small; put repository-specific behavior in the repository.

Always validate the effective result instead of reading one file and guessing:

```bash
opencode debug config
```

---

## 3. Provider setup: prefer direct support

For built-in providers, prefer OpenCode's native provider integration instead of adding a proxy just because a proxy is possible.

The interactive path is:

```text
/connect
/models
```

For a custom OpenAI-compatible gateway:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "company/coder",
  "providers": {
    "company": {
      "name": "Company Gateway",
      "env": ["COMPANY_GATEWAY_KEY"],
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "https://gateway.example.com/v1"
      },
      "models": {
        "coder": {
          "modelID": "upstream/coder",
          "name": "Coder"
        }
      }
    }
  }
}
```

### Vertex AI

OpenCode V2 has a direct `google-vertex` provider. Prefer it over a compatibility bridge when Vertex is the real upstream.

Example:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "google-vertex/YOUR_MODEL_ID",
  "providers": {
    "google-vertex": {
      "settings": {
        "project": "YOUR_GCP_PROJECT",
        "location": "global"
      }
    }
  }
}
```

Use Application Default Credentials or the authentication mechanism supported by your organization. Keep credential files out of the repository.

Verify the provider/model the runtime actually resolved:

```bash
opencode debug config
opencode models
opencode run "Reply exactly MODEL_OK. Do not use tools."
```

A raw Vertex API success is useful, but the `opencode run` smoke test is the proof that OpenCode is wired correctly.

---

## 4. Instructions and skills

Keep permanent `AGENTS.md` guidance concise:

- inspect before editing;
- preserve unrelated changes;
- keep dev servers on loopback;
- test before reporting completion;
- protect credentials;
- keep scratch artifacts scoped to the workspace;
- report observable evidence.

Move specialized procedures into skills so they are loaded only when needed.

Good skill candidates:

- current documentation lookup;
- deep debugging;
- GitHub workflow;
- implementation verification;
- release checks;
- repository archaeology;
- safe Git;
- browser testing;
- Windows/PowerShell-specific workflow.

The goal is progressive disclosure, not one giant permanent prompt.

---

## 5. Agents and permissions

V2 permissions are ordered rules. **The last matching rule wins.**

Conservative example:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git diff *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" }
  ]
}
```

A read-only reviewer:

```json
{
  "agents": {
    "reviewer": {
      "description": "Review code without modifying files.",
      "mode": "subagent",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "deny" }
      ]
    }
  }
}
```

Useful agent roles:

- `explore`: fast read-only codebase mapping;
- `reviewer`: independent diff review;
- `tester`: test execution and failure analysis;
- `security`: read-only security inspection.

OpenCode also ships built-in agents including `build`, `plan`, `general`, and `explore`. Override a built-in only when you need different behavior.

### Autonomous mode without permission fatigue

For a mature workstation, "autonomous" should mean routine engineering actions run without prompts, not that the agent can reconfigure the host.

A useful pattern is:

```json
{
  "permissions": [
    { "action": "*", "resource": "*", "effect": "allow" }
  ],
  "experimental": {
    "policies": [
      { "action": "permission", "resource": "read:*/.ssh/*", "effect": "deny" },
      { "action": "permission", "resource": "read:*/.aws/*", "effect": "deny" },
      { "action": "permission", "resource": "shell:*git config --global*", "effect": "deny" }
    ]
  }
}
```

Policies are binary hard boundaries; they do not create approval prompts. Use them for host/security/credential operations that should fail directly.

For truly unrestricted execution, use an isolated VM/container instead of removing workstation protections.

---

## 6. MCP: add less, verify more

MCP servers live under `mcp.servers`.

Remote Context7 example:

```json
{
  "mcp": {
    "servers": {
      "context7": {
        "type": "remote",
        "url": "https://mcp.context7.com/mcp"
      }
    }
  }
}
```

Local stdio example:

```json
{
  "mcp": {
    "servers": {
      "example": {
        "type": "local",
        "command": ["node", "server.js"]
      }
    }
  }
}
```

Prefer a local pinned install for tooling you rely on heavily. Re-downloading `@latest` at every agent start is convenient for experimentation but less predictable for a stable workstation.

Check MCP state with:

```bash
opencode mcp list
```

---

## 7. The MCP cold-start failure mode

A background service can report healthy before MCP reconciliation is complete.

If `opencode mcp list` unexpectedly shows no servers after a cold start, use this sequence before changing the config:

```bash
opencode service stop
opencode service start
opencode api GET /api/info
opencode reload
# allow a short initialization window
opencode mcp list
```

If the servers appear after `reload`, the config was not the problem.

This distinction matters: otherwise you can waste time rewriting a correct `mcp.servers` block to solve a lifecycle race.

---

## 8. Background service, Desktop, and fixed loopback port

OpenCode V2 provides a background service:

```bash
opencode service start
opencode service status
opencode service restart
opencode service stop
```

For Desktop + CLI on one workstation, a fixed local port makes reconnection predictable:

```bash
opencode service set port 49374
opencode service start
opencode service status
```

Keep it bound to loopback when remote access is not required.

Health check:

```bash
opencode api GET /api/info
```

### Windows: keep the local service available after sign-in

If Desktop and CLI both depend on the same fixed loopback service, you can start it at user logon with a **visible standard-user Startup script**. This is ordinary user-session startup, not a hidden scheduled task.

```powershell
$OC = "$env:APPDATA\npm\opencode.cmd"
$Startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$Starter = Join-Path $Startup "OpenCode_Service_Start.cmd"

& $OC service set port 49374
& $OC service start

$Content = @'
@echo off
"%APPDATA%\npm\opencode.cmd" service start >nul 2>&1
'@

Set-Content -LiteralPath $Starter -Value $Content -Encoding ASCII
```

Verify:

```powershell
& $OC service status

Get-NetTCPConnection -LocalPort 49374 -State Listen -ErrorAction SilentlyContinue |
Select-Object LocalAddress, LocalPort, OwningProcess
```

Expected bind address for a single-machine setup: `127.0.0.1`.

Do not switch the hostname to `0.0.0.0` just to make Desktop work locally. Do not hide the startup script or convert it into stealth persistence.

Web/Desktop pairing:

```bash
opencode pair
```

Pairing links are one-time and short-lived. If a link expires, generate a new one instead of changing server settings.

### Desktop/CLI mismatch

If CLI V2 works but Desktop reports a schema/configuration error:

1. verify the Desktop version independently;
2. update Desktop before editing the working CLI config;
3. verify the Desktop's local server version;
4. only then troubleshoot config syntax.

A CLI success does not prove the Desktop sidecar is the same generation.

---

## 9. GitHub integration: MCP is optional

GitHub MCP is useful for structured GitHub operations, but it is not required for a strong coding-agent setup.

First verify GitHub CLI:

```bash
gh auth status
```

If `gh` is healthy but GitHub MCP authentication fails, use `gh` as the fallback:

```bash
gh repo view
gh issue list
gh pr create
gh pr checks
```

This is often simpler and avoids moving a PAT into another configuration layer.

Do not print tokens to debug an MCP header. Prefer the OS keyring and normal `gh auth` flows.

---

## 10. Browser stack: Playwright CLI first

For coding agents, the default browser stack should optimize for deterministic interaction and low tool-schema overhead.

Recommended order:

1. **Playwright CLI** for navigation, clicks, forms, snapshots, and screenshots;
2. **Chrome DevTools MCP** for console/network/runtime/performance diagnostics;
3. **Playwright MCP** only when its richer MCP tool surface is specifically useful.

A local tool layout on Windows can be:

```text
%LOCALAPPDATA%\OpenCodeTools\
  playwright-cli\
  chrome-devtools\
```

### Microsoft Edge

Use the installed Edge browser when that matches the application's real user environment.

For a new automation session, launch Edge through Playwright.

For an **already-open authenticated browser**, prefer the supported attach/extension path when available. That preserves SSO, cookies, MFA state, extensions, and existing tabs.

Do **not** copy raw Edge/Chrome `Cookies`, `Login Data`, `Web Data`, or `Local State` databases to "clone" a session.

Fallback: use a dedicated persistent automation profile. Authenticate once and reuse that separate profile on future automation runs.

---

## 11. Managed Windows / enterprise workstation guidance

A coding-agent setup should remain auditable.

Prefer:

- standard-user installs;
- signed vendor binaries;
- visible startup scripts;
- user-local tool directories;
- loopback services;
- normal keyring-backed credentials;
- supported browser attach/extension mechanisms.

Avoid:

- `ExecutionPolicy Bypass`;
- hidden PowerShell/VBS launchers;
- disabling or excluding Defender/EDR;
- firewall weakening;
- ACL/ownership tricks;
- hidden persistence;
- direct browser credential-database copying.

On a managed workstation, reliability and auditability are part of the engineering requirement.

---

## 12. Troubleshooting matrix

| Symptom | What to check first | Fallback |
|---|---|---|
| Model absent | `opencode debug config`, `opencode models` | Verify direct provider settings before adding a bridge |
| CLI works, Desktop fails | Desktop version/local server version | Update/align Desktop before rewriting config |
| `No MCP servers configured` after cold start | service health + `reload` | Wait briefly, rerun `mcp list` |
| GitHub MCP auth fails | `gh auth status` | Use `gh` CLI/keyring |
| Playwright new browser requires login | existing browser attach path | persistent automation profile |
| Browser UI works but app still fails | console/network | Chrome DevTools MCP |
| Agent asks too often | ordered permissions | allow routine actions, hard-deny host-risk actions |
| Old config behaves strangely | mixed V1/V2 syntax | migrate instead of layering both styles |

---

## 13. Acceptance test

Do not call the setup complete until these pass:

```bash
opencode --version
opencode debug config
opencode debug agents
opencode run "Reply exactly CORE_OK. Do not use tools."
opencode mcp list
gh auth status
```

Then test:

- one read-only explorer subagent;
- one reviewer subagent;
- one tester subagent;
- browser tooling if your workflow needs it;
- final Git diff/status evidence.

The point of the preparation is not to create an impressive config file. It is to create a runtime that recovers predictably when one layer fails.
