# OpenCode Configuration and Operations Guide

OpenCode is an open-source, provider-agnostic coding agent available as a terminal interface, desktop app, and web app.

This guide targets **OpenCode V2**. V1 configuration is still recognized in many cases, but V2 renamed several important fields. In particular, V2 uses `agents`, ordered `permissions`, `providers`, and `mcp.servers`. If you are upgrading an older setup, use the official V1-to-V2 migration guide instead of mixing both syntaxes in one example.

---

## 1. Installation

For the V2 CLI, the current npm package is:

```bash
npm install -g @opencode/cli
opencode --version
```

Other installation methods are documented by OpenCode. On Windows, use a supported standalone/installer path or npm if it fits your environment; do not assume a Windows package manager is available.

Launch OpenCode from a project directory:

```bash
cd /path/to/your/project
opencode
```

---

## 2. Configuration

OpenCode reads JSON/JSONC configuration validated by:

```text
https://opencode.ai/config.json
```

Keep user-wide defaults small and prefer project configuration for repository-specific behavior. Avoid copying a large global tool catalog into every project.

V2 uses plural top-level collections such as:

- `providers`
- `agents`
- `permissions`
- `mcp.servers`

---

## 3. Providers

For standard providers, the simplest path is usually:

```text
/connect
/models
```

For a custom OpenAI-compatible gateway, V2 uses a provider definition like this:

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
          "modelID": "upstream/coder-v2",
          "name": "Coder"
        }
      }
    }
  }
}
```

For Vertex AI, V2 provides a `google-vertex` provider and uses Application Default Credentials. Supply the project and location through provider settings or supported environment variables.

Do not copy model limits from another provider unless you have verified them for the exact endpoint you are configuring.

---

## 4. Instructions and skills

Keep permanent repository guidance in `AGENTS.md` concise and stable. Put specialized workflows into skills so they are loaded only when needed.

A useful `AGENTS.md` should focus on repository invariants:

- inspect before editing;
- preserve unrelated changes;
- keep development servers on loopback;
- test before reporting completion;
- protect credentials;
- keep temporary artifacts scoped to the workspace.

OpenCode V2 also supports skills through the `skill` tool. Permissions can allow, ask, or deny specific skill IDs.

---

## 5. Agents and permissions

V2 defines custom agents under `agents`. Permissions are ordered rules; the last matching rule wins.

Example:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agents": {
    "reviewer": {
      "description": "Review changes without modifying files.",
      "mode": "subagent",
      "system": "Focus on correctness, regressions, security, and missing tests.",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "deny" }
      ]
    },
    "tester": {
      "description": "Run relevant test and validation commands.",
      "mode": "subagent",
      "system": "Verify behavior and report evidence. Do not make unrelated changes.",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "ask" },
        { "action": "shell", "resource": "git status*", "effect": "allow" },
        { "action": "shell", "resource": "python -m unittest*", "effect": "allow" },
        { "action": "shell", "resource": "pytest*", "effect": "allow" },
        { "action": "shell", "resource": "npm test*", "effect": "allow" }
      ]
    }
  }
}
```

V2 action names differ from V1 in several places. For example:

- V1 `bash` -> V2 `shell`
- V1 `task` -> V2 `subagent`
- V1 `agent` -> V2 `agents`
- V1 `permission` -> V2 ordered `permissions`

Do not mix the two styles in a starter template.

---

## 6. MCP servers

V2 stores MCP servers under `mcp.servers`.

Local stdio server:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "context7": {
        "type": "local",
        "command": ["npx", "-y", "@upstash/context7-mcp"]
      }
    }
  }
}
```

Remote Streamable HTTP server:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "docs": {
        "type": "remote",
        "url": "https://mcp.example.com/mcp"
      }
    }
  }
}
```

Add only servers that solve a real problem. MCP tools can add context and tool-selection overhead, and remote servers may require separate authentication.

---

## 7. Practical troubleshooting

| Symptom | What to check | Safe next step |
|---|---|---|
| Provider authentication fails | Active provider account, environment variable name, model ID | Re-run provider connection and verify the exact provider/model selection |
| Custom model is unavailable | `providers.<id>.models` key, `modelID`, endpoint | Check the provider map and exact upstream model ID |
| Agent cannot edit files | Ordered `permissions` rules | Inspect the last matching `edit` rule |
| Shell action still asks | `shell` resource pattern | Add a narrow allow rule for the exact command family if appropriate |
| MCP server does not connect | `mcp.servers` entry, command/URL, auth | Run `opencode mcp list` and test the server independently |
| Old config behaves strangely | Mixed V1/V2 fields | Migrate the file instead of layering V2 fields onto a legacy example |

---

## 8. V1 migration note

Older OpenCode documentation uses singular keys such as `agent`, `provider`, and tool-grouped `permission` objects. Those examples are useful when maintaining a V1 setup, but new templates in this repository target V2.

When migrating, follow the current OpenCode migration guide and validate the resulting configuration with the V2 schema and CLI.
