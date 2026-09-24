# Claude Code Configuration and Operations Guide

Claude Code is Anthropic's agentic coding tool. It can read and edit a codebase, run shell commands, work with Git, connect external tools through MCP, load project instructions and skills, and delegate focused work to subagents.

The preparation principles in this repository apply to Claude Code too. The architecture is largely the same:

1. verify the model/provider path;
2. keep permanent instructions concise;
3. grant only the permissions the workflow actually needs;
4. add MCP servers deliberately;
5. move specialized procedures into skills;
6. use subagents for bounded independent work;
7. validate the result with tests, diffs, and observable evidence.

The important differences are the configuration files and runtime-specific features described below.

Official documentation: https://code.claude.com/docs/en/overview

---

## 1. Install and verify Claude Code

Claude Code is available in the terminal, IDE integrations, desktop, and web. For a local engineering setup, verify the CLI first:

```bash
claude --version
```

On Windows, Anthropic documents WinGet as one supported installation path:

```powershell
winget install Anthropic.ClaudeCode
```

Start Claude Code from the repository you want it to work on:

```bash
cd /path/to/repository
claude
```

Claude Code can authenticate through a Claude account / Anthropic Console path, and the CLI also supports Anthropic-supported third-party deployment options such as Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. Keep provider credentials outside the repository.

Official references:
- Overview: https://code.claude.com/docs/en/overview
- Enterprise deployment options: https://code.claude.com/docs/en/third-party-integrations

---

## 2. Understand the settings scopes

Claude Code reads JSON settings from several scopes:

| Scope | File | Use it for |
|---|---|---|
| User | `~/.claude/settings.json` | Personal defaults across projects |
| Shared project | `.claude/settings.json` | Team permissions, hooks, plugins, and project environment settings |
| Project local | `.claude/settings.local.json` | Personal overrides for one project; keep it untracked |
| Managed | Organization-managed sources | Security and compliance policy |

For a repository you intend to share, prefer a small committed `.claude/settings.json` and keep personal exceptions in `.claude/settings.local.json`.

The settings format is strict JSON. The published schema is:

```text
https://json.schemastore.org/claude-code-settings.json
```

Official reference: https://code.claude.com/docs/en/settings

---

## 3. Project instructions: CLAUDE.md and AGENTS.md

Claude Code supports `CLAUDE.md` files for persistent project instructions.

Useful locations include:

```text
~/.claude/CLAUDE.md
./CLAUDE.md
./.claude/CLAUDE.md
```

Keep these files focused on stable repository facts and working agreements:

- build and test commands;
- architecture constraints;
- coding conventions;
- repository-specific safety rules;
- required verification before completion.

Do not turn `CLAUDE.md` into a giant playbook. Put specialized procedures into skills.

### Interoperability with AGENTS.md

Current Claude Code versions can also read `AGENTS.md`. If a repository already uses `AGENTS.md` for Codex or another coding agent, you do not necessarily need to duplicate the same rules.

A useful cross-agent pattern is:

```markdown
@AGENTS.md

## Claude Code

Add only Claude-specific instructions here.
```

On Windows, prefer the import form above rather than a symlink.

Official reference: https://code.claude.com/docs/en/memory

---

## 4. Permissions: separate behavior from enforcement

Instructions tell the model what it should do. Permissions decide what Claude Code is actually allowed to do.

Claude Code supports `allow`, `ask`, and `deny` rules in settings.

Example:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(python -m unittest *)",
      "Bash(pytest *)",
      "Bash(npm test *)"
    ],
    "ask": [
      "Bash(git commit *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Bash(git push *)",
      "Bash(git config --global *)",
      "Bash(npm install -g *)"
    ]
  }
}
```

This is deliberately conservative:

- inspection and tests can run without friction;
- commits ask;
- pushes remain blocked until you explicitly decide to allow them;
- common credential files stay unreadable;
- workspace tasks do not mutate global Git or npm state.

Claude Code evaluates permission rules in deny, then ask, then allow order. A matching deny cannot be overridden by a narrower allow.

Avoid `bypassPermissions` on a normal workstation. Anthropic documents it for isolated environments such as containers or virtual machines.

Official reference: https://code.claude.com/docs/en/permissions

---

## 5. Connect external tools with MCP

Claude Code supports both remote and local MCP servers.

Remote HTTP server:

```bash
claude mcp add --transport http example https://mcp.example.com/mcp
```

Local stdio server:

```bash
claude mcp add example -- npx -y @example/mcp-server
```

For a team-shared MCP configuration, use project scope or commit an appropriate `.mcp.json` after reviewing it.

The same tool-curation rule used elsewhere in this repository applies here: do not register every available MCP server. Add one when it provides a capability the built-in tools do not already cover well.

Official reference: https://code.claude.com/docs/en/mcp

---

## 6. Put repeatable workflows into skills

Claude Code project skills live under:

```text
.claude/skills/<skill-name>/SKILL.md
```

A skill uses YAML frontmatter plus Markdown instructions:

```markdown
---
description: Validate the current change before reporting completion.
---

Inspect the current diff, run the relevant tests, and report factual evidence.
Do not modify unrelated files.
```

Skills are a better home for procedures that are useful only in specific situations:

- release preparation;
- database migrations;
- PR review;
- benchmark validation;
- documentation generation;
- application verification.

Keep permanent instructions small and load these procedures only when the task needs them.

Official reference: https://code.claude.com/docs/en/skills

---

## 7. Use project subagents for bounded independent work

Claude Code project subagents are Markdown files under:

```text
.claude/agents/
```

Example reviewer:

```markdown
---
name: reviewer
description: Independent review of completed changes for correctness, regressions, security, and missing tests.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
---

Review the actual diff and relevant source files.
Do not modify files.
Report concrete findings with evidence.
```

Good subagent tasks:

- codebase exploration;
- independent review;
- test execution and failure analysis;
- security inspection.

Avoid spawning a subagent for one trivial command or for work that blocks the very next step in the main thread.

Official reference: https://code.claude.com/docs/en/sub-agents

---

## 8. Hooks are deterministic automation, not more prompting

Claude Code hooks run at defined lifecycle events such as `PreToolUse` and `PostToolUse`.

A useful pattern is running a formatter or validator after edits:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

Keep hooks:

- deterministic;
- fast;
- repository-scoped;
- auditable;
- free of hidden credential handling.

Do not use hooks to bypass workstation policy or silently broaden the agent's permissions.

Official reference: https://code.claude.com/docs/en/hooks

---

## 9. A practical preparation sequence

Use the same progressive approach as for Codex and OpenCode:

### Minimal
- Claude Code CLI works;
- authentication works;
- concise project instructions;
- Git status and test commands work;
- conservative permissions.

### Engineering
Add:
- documentation MCP where needed;
- GitHub tooling where the task requires remote operations;
- project skills for repeatable workflows;
- reviewer/tester subagents.

### Browser
Add:
- browser automation only for applications that need UI verification;
- loopback-only local development servers;
- explicit process lifecycle management.

Do not enable browser, GitHub, database, and communication tools just because they exist.

---

## 10. Validate the setup

Before trusting a prepared Claude Code environment with larger autonomous tasks, verify each layer:

```bash
claude --version
git status
python -m unittest discover tests
```

Inside Claude Code, also check the runtime configuration:

```text
/status
/permissions
/hooks
/context
```

Useful validation questions:

- Which instruction files were loaded?
- Which settings scope supplied the active permissions?
- Can tests run without unnecessary prompts?
- Are credential files denied?
- Are MCP servers healthy?
- Are subagents discoverable?
- Does the final report cite real test/diff evidence?
- Did the task stay inside the workspace?

Use `claude doctor` when configuration entries or customizations do not load as expected.

---

## 11. What transfers from Codex and OpenCode

Most preparation principles are runtime-independent:

| Principle | Codex | Claude Code | OpenCode |
|---|---|---|---|
| Lean project instructions | `AGENTS.md` | `CLAUDE.md` and/or `AGENTS.md` | `AGENTS.md` |
| Project permissions | Sandbox + approvals | `.claude/settings.json` permissions | `permissions` |
| MCP | `mcp_servers` | `claude mcp` / `.mcp.json` | `mcp.servers` |
| Skills | Skills | `.claude/skills/` | Skills/tooling supported by runtime |
| Subagents | `[agents]` | `.claude/agents/` | `agents` |
| Hooks | Codex hooks | Claude Code hooks | Runtime/plugin dependent |
| Validation | Tests + evidence | Tests + evidence | Tests + evidence |

The files differ. The engineering discipline does not.

---

## Reference links

- Overview: https://code.claude.com/docs/en/overview
- Settings: https://code.claude.com/docs/en/settings
- Project instructions and memory: https://code.claude.com/docs/en/memory
- Permissions: https://code.claude.com/docs/en/permissions
- MCP: https://code.claude.com/docs/en/mcp
- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents
- Hooks: https://code.claude.com/docs/en/hooks
