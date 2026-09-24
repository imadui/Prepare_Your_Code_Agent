# End-to-End Acceptance Benchmark Prompt

Use this standardized prompt to test and validate any new Codex or OpenCode environment.

---

## Agent Prompt

```markdown
You are an autonomous software engineering agent. Your objective is to build, test, and verify a complete, minimal HTTP health-check microservice in an isolated workspace.

### Requirements

1. **Workspace Setup:**
   - Initialize a local Git repository in the workspace root if one does not already exist.
   - Create a clean `.gitignore` that excludes `.env`, `__pycache__/`, `.agent-tmp/`, and temporary build artifacts.

2. **Implementation:**
   - Consult current framework documentation before writing code.
   - Implement a lightweight service (Python standard library `http.server`, Node.js `http`, or FastAPI/Express) providing:
     - `GET /health`: returns JSON `{"status": "ok", "uptime_seconds": <number>}`.
     - `GET /echo?msg=<text>`: returns JSON `{"message": "<text>"}`.
   - Ensure all input parameters are properly sanitized and query parameters handled safely.

3. **Local Dev Server Guardrails:**
   - The service must bind exclusively to loopback: `127.0.0.1` or `localhost`.
   - Never bind to `0.0.0.0` or bare `::`.

4. **Automated Testing:**
   - Write a unit and integration test suite covering both endpoints, error cases, and invalid methods.
   - Run the tests and ensure 100% pass rate.

5. **Verification & Evidence:**
   - If browser or curl tools are available, perform a live loopback query against the running service.
   - Check `git diff` and ensure only requested files are modified.
   - Verify no secrets, temporary files, or global machine settings were altered.

6. **Reporting:**
   - Provide a factual summary including:
     - Exact test command and output.
     - PID and port of any running preview server.
     - Git status and list of created files.
     - Tools and MCP servers utilized during the task.
```
