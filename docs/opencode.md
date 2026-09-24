# OpenCode Configuration and Operations Guide

OpenCode is an open-source, provider-agnostic AI coding agent designed for the terminal. It features a client/server architecture, language server protocol (LSP) integration, and an interactive Terminal User Interface (TUI).

This guide explains how to install OpenCode, connect providers, configure primary and subagent roles, integrate MCP servers, and enforce permission boundaries.

---

## 1. Prerequisites and Installation

OpenCode runs on Node.js and requires modern CLI tooling (Git, Node 18+).

### Installing OpenCode
```bash
# Install globally using npm
npm install -g opencode-ai

# Verify installation
opencode --version
```

### Launching OpenCode
Run `opencode` in your terminal inside any project directory to launch the interactive TUI:
```bash
cd /path/to/your/project
opencode
```

---

## 2. Configuration Hierarchy

OpenCode discovers configuration from two main locations:

1. **Global Configuration:**
   `~/.config/opencode/opencode.json` (Linux/macOS) or `%USERPROFILE%\.config\opencode\opencode.json` (Windows). Defines user-wide custom providers, default models, and global MCP servers.
2. **Project Configuration:**
   `./opencode.json` in the root of the active workspace. Overrides or extends global settings with project-specific agents, rules, and local MCP tools.

Both files validate against the official JSON schema:
`https://opencode.ai/config.json`

---

## 3. Provider Configuration in `opencode.json`

OpenCode uses Vercel AI SDK adapters under the hood, making it compatible with any major provider or custom OpenAI-compatible endpoint.

### A. Connecting Standard Providers
You can connect providers interactively via the `/connect` command inside the TUI or define them directly in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    },
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```

### B. Custom OpenAI-Compatible Endpoints
To connect an internal gateway, vLLM, LiteLLM, or Ollama, configure an entry using `@ai-sdk/openai-compatible`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "enterprise-gateway": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Enterprise LLM Gateway",
      "options": {
        "baseURL": "https://llm-gateway.example.com/v1",
        "apiKey": "{env:GATEWAY_API_KEY}",
        "headers": {
          "X-Organization-Unit": "Platform-Engineering"
        }
      },
      "models": {
        "custom-code-model": {
          "name": "Custom Code Model",
          "limit": {
            "context": 128000,
            "output": 8192
          }
        }
      }
    }
  }
}
```

---

## 4. Instructions with `AGENTS.md`

OpenCode natively supports `AGENTS.md` in the project root.

### Initializing `AGENTS.md`
Run the `/init` command inside OpenCode to analyze the repository structure and generate a baseline `AGENTS.md`:
```text
/init
```

### On-Demand Rule Referencing (`@rules`)
Instead of placing hundreds of lines of documentation directly into `AGENTS.md`, OpenCode supports referencing external rule files on demand:

```markdown
# Project Guidelines

## External Rules
When working on specific sub-systems, load the corresponding guidelines using your Read tool:
- For API endpoints: @docs/api-standards.md
- For Database migrations: @docs/database-rules.md
- For Security standards: @docs/security-check.md

Do not load these files preemptively. Only read them when relevant to your current task.
```
This approach keeps baseline context usage minimal while providing full guidance when needed.

---

## 5. Primary Agents and Subagents

OpenCode allows you to define distinct agents with tailored modes, system prompts, models, and execution permissions.

### Agent Modes
- `mode: "primary"`: Main agent role selectable by the user in the TUI (e.g., standard builder or planner).
- `mode: "subagent"`: Delegated worker spawned programmatically for specialized, bounded tasks (e.g., code reviewer).

### Permission Controls
Each agent can have distinct permissions for filesystem and shell operations:
- `allow`: Action executes autonomously without prompting.
- `ask`: Agent prompts the user for confirmation before acting.
- `deny`: Action is strictly forbidden.

### Example Agent Configuration
```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-3-7-sonnet-20250219",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      }
    },
    "plan": {
      "mode": "primary",
      "model": "openai/gpt-6-luna",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    },
    "code-reviewer": {
      "description": "Reviews changes for security, performance, and architecture.",
      "mode": "subagent",
      "model": "anthropic/claude-3-7-sonnet-20250219",
      "prompt": "You are a senior code reviewer. You have read-only access. Inspect diffs, test coverage, and security implications.",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    }
  }
}
```

---

## 6. Model Context Protocol (MCP) in OpenCode

OpenCode connects to external tools via the Model Context Protocol. MCP servers are defined under the `"mcp"` key in `opencode.json`.

### Stdio Server (Local Command)
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Remote Server (SSE / Streamable HTTP)
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "company-docs": {
      "type": "remote",
      "url": "https://mcp.internal.example.com/sse"
    }
  }
}
```

---

## 7. Troubleshooting OpenCode

| Symptom | Cause | Remedy |
|---|---|---|
| `Provider auth error` | Environment variable not found or `{env:...}` syntax error. | Ensure key is exported in your shell and formatted as `"{env:KEY_NAME}"`. |
| `Agent cannot edit files` | Agent `permission.edit` is set to `"deny"`. | Set `permission.edit: "allow"` or `"ask"` for primary builder agents. |
| `TUI model picker is empty` | No models defined under custom provider. | Declare explicit model entries under `provider.<id>.models`. |
| `MCP server failed to spawn` | `npx` or executable missing from `PATH`. | Verify command exists locally and runs standalone in terminal. |
