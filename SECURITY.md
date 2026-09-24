# Security Policy

## Core Principle: Public-Safe and Isolated by Design

This repository is maintained with strict isolation and public safety standards:
- **No credentials:** Never commit API keys, tokens, session cookies, SSH keys, service account JSON files, or real credentials.
- **Generic examples:** All documentation and configuration templates use sanitized placeholders (`your-project-id`, `your-model-name`, `https://your-endpoint.example.com`).
- **Workspace containment:** All autonomous agent operations must remain inside the assigned project root without mutating global machine configuration.
- **Loopback development:** Local preview and test servers must bind exclusively to `127.0.0.1` or `localhost`.

## Reporting a Security Vulnerability

If you discover a potential security vulnerability or an unintentional exposure of sensitive data:

1. **Do not open a public GitHub issue.**
2. Report the vulnerability privately via GitHub Private Vulnerability Reporting or contact the maintainer directly:
   - **GitHub:** [@imadui](https://github.com/imadui)
   - **LinkedIn:** [Imad Eddine Berjamy](https://linkedin.com/in/berjamy)
3. Include detailed steps to reproduce the issue, the affected files or configurations, and potential impact.
4. Reports will be acknowledged within 48 hours, and a remediation plan will be provided promptly.

## Safe Usage Guidelines for Coding Agents

When configuring autonomous coding agents (Codex, OpenCode, or similar):
- Maintain an explicit `.gitignore` covering `.env`, credentials, local database files, and temporary scratch folders (`.agent-tmp/`).
- Apply least-privilege sandbox settings (`workspace-write` or equivalent) rather than unrestricted full-access modes.
- Avoid passing persistent environment variables containing production secrets into agent shells.
- Run automated pre-commit and safety validation checks before publishing repositories.
