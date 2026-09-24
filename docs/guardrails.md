# Workstation Guardrails and Engineering Hygiene

Autonomous coding agents have the power to create files, execute shell commands, and run long-lived processes. Without rigorous guardrails, an agent can unintentionally contaminate developer workstations, leak secrets, or alter machine-wide configurations.

This document defines practical workstation hygiene rules for operating agents safely.

---

## 1. Workspace Isolation

An agent tasked with working on a specific repository must never touch files outside that repository unless explicitly instructed by the user.

### Core Invariants
- **Restricted write scope:** All file writes, creations, and deletions must be contained within the project root directory.
- **No global configuration mutation:**
  - Never run `git config --global` (use `git config --local` or temporary environment variables instead).
  - Never run `npm install -g` or `pip install` globally (use virtual environments: `.venv/` or project `node_modules/`).
  - Never modify system-wide PATH or persistent registry/environment settings.
- **Sandbox enforcement:** Enable filesystem sandboxing (`sandbox_mode = "workspace-write"` in Codex, or explicit agent permissions in OpenCode).

```mermaid
graph TD
    Agent[Agent Shell Session] --> Safe[Project Workspace\n/path/to/my-repo]
    Agent -.->|BLOCKED by Sandbox| GlobalGit[~/.gitconfig]
    Agent -.->|BLOCKED by Sandbox| GlobalEnv[/etc/environment or Registry]
    Agent -.->|BLOCKED by Sandbox| UserProfile[Host User Profile (~/.ssh) or ~/.ssh]
```

---

## 2. Loopback-Only Development Networking

When an agent spins up a development server, preview backend, or test runner, it must strictly bind to loopback interfaces.

### Invariants
- Bind exclusively to `127.0.0.1` or `localhost`.
- **Never bind to `0.0.0.0` or bare `::`:** Binding to `0.0.0.0` exposes local ports to the entire local area network (LAN) and frequently triggers OS firewall prompts or enterprise security alerts.
- **Framework specifics:**
  - Vite: `vite --host 127.0.0.1` (or configure `server: { host: '127.0.0.1' }` in `vite.config.ts`).
  - Next.js: `next dev -H 127.0.0.1`.
  - Python / Flask / FastAPI: `uvicorn main:app --host 127.0.0.1 --port 8000`.
  - Node HTTP: `server.listen(3000, '127.0.0.1')`.
- **Process tracking:** Record the PID and port of any running preview server, and cleanly terminate processes when testing completes.

---

## 3. Secret and Credential Protection

Coding agents process thousands of tokens of code, logs, and command outputs. If secrets enter the context window, they can be echoed in logs, committed to Git, or exposed to third-party endpoints.

### Rules for Handling Secrets
1. **Read from Environment Variables:** Always consume secrets via environment variables (`OPENAI_API_KEY`, `DATABASE_URL`).
2. **Zero Hardcoded Secrets:** Never embed keys, tokens, passwords, or connection strings in code, configuration files, test fixtures, or prompts.
3. **Strict `.gitignore`:** Ensure `.env`, `.env.*`, `credentials/`, `*.pem`, `*.key`, and `*.pfx` are tracked by `.gitignore`.
4. **Shell Environment Scrubbing:** Use Codex's `shell_environment_policy` to strip sensitive environment variables before spawning shell commands:
   ```toml
   [shell_environment_policy]
   inherit = "core"
   ignore_default_excludes = false
   
   [shell_environment_policy.filters]
   "AWS_*" = "exclude"
   "AZURE_*" = "exclude"
   "GITHUB_TOKEN" = "exclude"
   ```
5. **Sanitized Error Logging:** Catch network or authentication errors in scripts and display generic messages rather than dumping raw HTTP request objects with `Authorization` headers.

---

## 4. Script and Binary Safety

To maintain a transparent and audit-friendly environment:
- **Avoid unsigned executable generation:** Never generate ad-hoc compiled `.exe` or `.dll` helper binaries when standard scripts (Python, Node.js, PowerShell) can perform the task.
- **Avoid dynamic compilation:** Avoid in-memory compilation techniques like PowerShell `Add-Type` or dynamic C# emission.
- **Do not bypass execution policies:** Avoid invoking PowerShell with `-ExecutionPolicy Bypass`. Use standard signed policies or unprivileged command execution.
- **Prefer interpreted tooling:** Rely on standard runtimes already installed on the developer machine (Python, Node, Git, standard OS shells).

---

## 5. Least Privilege and Elevation Boundaries

- **Standard User Context:** The agent must operate as an ordinary, unprivileged user.
- **Never request elevation:** Do not use `runas`, `Start-Process -Verb RunAs`, `sudo`, or UAC prompts.
- **Never tamper with endpoint security:** Do not attempt to disable, bypass, or reconfigure Windows Defender, antivirus agents, EDR tooling, or enterprise proxy policies.
- **Handling genuinely elevated tasks:** If a task strictly requires administrative rights (e.g., installing a low-level driver or modifying system services), the agent must stop, complete all non-elevated work, and report the required administrative step clearly to the human developer.

---

## 6. Temporary Artifact Lifecycle

Build caches, intermediate format conversions, and test scratch files clutter workspaces if left unmanaged.

### The `.agent-tmp/` Standard
Direct all temporary file generation to a dedicated workspace folder:
`<workspace>/.agent-tmp/<run-id>/`

### Retention Rules
- **Keep:** Final code deliverables, test suites, runtime dependencies, documentation, and schema migrations.
- **Clean:** Temporary download bundles, intermediate conversion files, scratch benchmark scripts, and discarded patches.
- **Safety:** Never delete files that existed prior to the current agent task.
