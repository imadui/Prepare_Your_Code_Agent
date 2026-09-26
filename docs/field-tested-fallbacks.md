# Field-Tested Setup and Fallbacks

This page captures the failure modes that matter in real coding-agent setups. It is intentionally operational: each section starts with the preferred path, then gives the fallback that should be used when the preferred path fails.

The goal is not to maximize the number of tools. The goal is to build an agent environment that can recover from provider, desktop, MCP, browser, authentication, and configuration problems without weakening workstation security.

---

## 1. Validate the runtime before tuning prompts

Always start with the runtime itself:

```bash
codex --version
claude --version
opencode --version
```

Then validate the selected model with one minimal prompt before adding MCP servers, browser automation, or subagents.

Why this matters: a working raw provider request does not prove the coding agent is using the intended provider, model, configuration file, or credentials.

**Rule:** do not debug prompts, skills, or browser tooling while the runtime/model layer is still broken.

---

## 2. Do not assume CLI and Desktop are the same build

Desktop and CLI releases can move at different speeds. A configuration accepted by a newer CLI may be rejected by an older Desktop sidecar.

### Preferred path

Verify both versions independently before changing a valid configuration:

```text
CLI version
Desktop version
Effective config
Selected model
```

### Fallback

If the CLI works but Desktop reports a configuration schema error:

1. do not immediately downgrade or rewrite the working CLI config;
2. update Desktop first;
3. verify the Desktop build actually matches the configuration generation you are using;
4. only then investigate syntax differences.

This avoids turning one healthy setup into two broken ones.

---

## 3. OpenCode V2: use V2 syntax consistently

New OpenCode V2 setups should use:

- `agents`
- ordered `permissions`
- `providers`
- `mcp.servers`

Do not mix V1 and V2 fields in the same starter config.

Useful validation commands:

```bash
opencode debug config
opencode debug agents
opencode models
opencode mcp list
```

For permissions, remember that rules are ordered and the last matching rule wins.

---

## 4. OpenCode service cold start and MCP initialization

A background service may be healthy before all MCP servers have finished reconciling.

A reliable diagnostic sequence is:

```bash
opencode service stop
opencode service start
opencode api GET /api/info
opencode reload
opencode mcp list
```

If MCP servers are missing immediately after `service start`, do not rewrite the config first. Reload the config, allow a short initialization window, then check again.

For a Desktop + CLI setup on one workstation, keep the service on loopback. A fixed local port can make pairing and Desktop reconnection predictable:

```bash
opencode service set port 49374
opencode service start
opencode service status
```

Do not bind to `0.0.0.0` unless remote access is explicitly required and reviewed.

---

## 5. GitHub: prefer the simplest authenticated path

GitHub MCP is useful when structured GitHub tools are materially better than shell commands. It is not mandatory for ordinary repository work.

### Preferred path

Use GitHub CLI authentication and verify it independently:

```bash
gh auth status
```

### MCP path

If using a GitHub MCP server, verify it separately with the runtime's MCP status command.

### Fallback

If GitHub MCP authentication fails while `gh auth status` succeeds, use `gh` for repository operations instead of repeatedly moving tokens between configs and environment variables.

Examples:

```bash
gh repo view
gh issue list
gh pr create
gh pr view
gh pr checks
```

Never print a PAT just to make an MCP server work. Prefer OS keyring-backed credentials where available.

---

## 6. Browser automation: CLI first, MCP when it adds value

For coding agents, browser automation should be deterministic and low-overhead.

### Preferred stack

1. **Playwright CLI** for navigation, click/fill flows, snapshots, and screenshots.
2. **Chrome DevTools MCP** for console, network, runtime, and performance diagnostics.
3. **Playwright MCP** only when its structured MCP tool surface is specifically useful.

This keeps the default tool catalog smaller and reduces context/tool-selection overhead.

### Install browser tools locally when possible

For stable workstations, prefer a pinned local tool directory over downloading `@latest` on every launch.

Example layout:

```text
%LOCALAPPDATA%\OpenCodeTools\
  playwright-cli\
  chrome-devtools\
```

---

## 7. Existing authenticated browser sessions

Do not solve an authentication problem by copying browser credential databases.

When the user asks the agent to work with an already-open browser session, use the browser's supported attach/extension path when available.

For Playwright CLI, the preferred flow is:

```text
inspect sessions
attach to existing Edge/Chrome through the supported extension path
select the existing tab
operate it
detach when done
```

This preserves SSO, cookies, MFA state, extensions, and open tabs without scraping `Cookies`, `Login Data`, `Web Data`, or `Local State` files.

### Fallback: dedicated persistent automation profile

If an existing session cannot be attached, use a dedicated persistent browser profile. Authenticate once, then reuse that automation profile on later runs.

Keep it separate from the user's normal browser profile.

---

## 8. Enterprise Windows: optimize for auditability

On managed workstations, "works" is not enough. The setup should also be explainable to endpoint security and support teams.

Prefer:

- standard-user installs;
- visible scripts;
- ordinary user-local application directories;
- loopback-only local servers;
- signed vendor binaries;
- normal browser extensions and supported attach mechanisms;
- OS keyrings for credentials.

Avoid:

- `ExecutionPolicy Bypass`;
- hidden PowerShell/VBS launchers;
- disabling Defender/EDR/firewall;
- Defender exclusions;
- ad-hoc unsigned helper executables;
- changing ACLs/ownership to force an install;
- copying browser credential stores.

---

## 9. Autonomy should remove prompts, not remove boundaries

A useful autonomous agent does not need to ask about every edit, test, or normal Git operation.

The safer pattern is:

```text
routine engineering operations -> ALLOW
dangerous/host-level operations -> DENY
interactive approval prompts -> minimize or eliminate
```

Examples of operations commonly safe to allow inside a trusted workspace:

- read/search/edit repository files;
- run tests, lint, build;
- inspect Git status/diff/log;
- create normal commits/branches/PRs when the task clearly requires delivery;
- use browser automation against the requested application.

Examples that should remain blocked on a normal workstation:

- security-tool changes;
- elevation;
- global package-manager or Git configuration mutation;
- raw credential-store reads;
- destructive history rewriting unless explicitly requested.

For genuinely unrestricted execution, use an isolated VM/container rather than removing host protections.

---

## 10. Codex fallback strategy

For Codex, prefer native OpenAI authentication/provider paths first.

If a custom provider or gateway fails:

1. validate the upstream endpoint outside Codex;
2. verify the exact Codex provider and wire-protocol configuration supported by the installed version;
3. verify whether the relevant keys are allowed at user or project scope;
4. only then consider a compatibility gateway.

Do not build a bridge simply because another runtime accepts the same endpoint. Runtime provider support is not interchangeable.

If the desired non-OpenAI model/provider is unsupported or brittle in Codex, use a runtime that supports that provider directly rather than making the entire workstation depend on an unnecessary proxy.

---

## 11. Claude Code fallback strategy

For Claude Code, use its native account or officially supported deployment integrations first.

If a provider path does not work:

1. verify the deployment is one Claude Code officially supports;
2. verify the active settings scope;
3. run `claude doctor`;
4. inspect `/status`, `/permissions`, and MCP state;
5. keep personal overrides in local settings rather than weakening shared project policy.

Do not assume an arbitrary OpenAI-compatible endpoint can be substituted for Claude Code's supported authentication/deployment paths.

---

## 12. The final acceptance sequence

Before calling a workstation "prepared", validate all of these in order:

1. provider connectivity;
2. runtime CLI;
3. selected model;
4. effective configuration;
5. documentation lookup;
6. MCP health;
7. Git and GitHub;
8. edit/build/test loop;
9. browser automation if needed;
10. subagent discovery and execution;
11. workspace/credential boundaries;
12. final evidence report.

If a lower layer fails, fix it before debugging a higher one.

That discipline is the difference between a demo configuration and a dependable coding-agent workstation.
