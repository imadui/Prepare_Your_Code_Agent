# Contributing to Prepare Your Code Agent

Thank you for your interest in improving practical patterns for autonomous coding agents.

## Design Philosophy

This project prioritizes practical, verifiable guidance over theoretical complexity:
- **Keep it lean:** More configuration is not better configuration. Every proposed setting or tool must justify its overhead.
- **Evidence first:** Configuration advice and workflows must be verifiable with reproducible commands or test scripts.
- **No marketing buzzwords:** Write with the voice of an experienced automation engineer. Avoid hype words (*revolutionary*, *supercharge*, *game-changing*, etc.).
- **Strict safety:** Never include real keys, private hostnames, internal network paths, or customer names in documentation or test fixtures.

## How to Contribute

1. **Fork the repository** and create a feature branch from `main`.
2. **Make focused changes:**
   - Keep documentation clear, concise, and backed by official vendor documentation.
   - Ensure all scripts use Python standard library where possible to avoid dependency bloat.
3. **Run local validation:**
   ```bash
   python scripts/doctor/doctor.py
   python scripts/validation/safety_check.py
   python -m unittest discover tests
   ```
4. **Submit a pull request** with a concise description of what was tested and why the change is beneficial.
