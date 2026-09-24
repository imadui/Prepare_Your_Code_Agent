#!/usr/bin/env python3
"""
Repository-content safety scanner.
Scans the selected workspace for common publication risks:
- Credential-like filenames and sensitive file extensions
- Common hardcoded secret patterns
- Machine-specific Windows user paths
- Unexpected large files

This is a repository-content check, not proof of machine-wide isolation and not a replacement for a dedicated secrets scanner.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# File extensions that should never be tracked
DISALLOWED_EXTENSIONS = {
    ".pem", ".key", ".p12", ".pfx", ".db", ".sqlite", ".sqlite3"
}

# Filenames that should never be tracked (except example templates)
DISALLOWED_EXACT_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "id_rsa", "id_ed25519", "credentials.json", "service_account.json"
}

# Regular expressions for detecting real credential values
SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OpenAI API Key format"),
    (re.compile(r"gh[pousr]_[a-zA-Z0-9]{20,}"), "GitHub Token format"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID format"),
    (re.compile(r"AIza[0-9A-Za-z\\-_]{35}"), "Google API Key format"),
    (re.compile(r"-----BEGIN [A-Z]+ PRIVATE KEY-----"), "Private Key header"),
    (re.compile(r"(?i)c:\\users\\[a-zA-Z0-9._-]+"), "User-specific Windows path")
]

IGNORED_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".agent-tmp"
}


def scan_repository(root_dir, quick=False):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        for fname in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, fname), root_dir).replace("\\", "/")
            full_path = os.path.join(dirpath, fname)
            _, ext = os.path.splitext(fname)

            # 1. Check disallowed filenames
            if fname in DISALLOWED_EXACT_NAMES:
                findings.append({
                    "type": "FORBIDDEN_FILE",
                    "file": rel_path,
                    "detail": f"Disallowed credential filename: {fname}"
                })

            # 2. Check disallowed file extensions
            if ext.lower() in DISALLOWED_EXTENSIONS:
                findings.append({
                    "type": "FORBIDDEN_EXTENSION",
                    "file": rel_path,
                    "detail": f"Disallowed file extension: {ext}"
                })

            # 3. Check for oversized files (> 5MB)
            try:
                fsize = os.path.getsize(full_path)
                if fsize > 5 * 1024 * 1024:
                    findings.append({
                        "type": "OVERSIZED_FILE",
                        "file": rel_path,
                        "detail": f"File size {fsize} bytes exceeds 5MB limit"
                    })
            except OSError:
                continue

            if quick:
                continue

            # 4. Content scanning for text files
            if fsize < 1024 * 1024:  # Scan files smaller than 1MB
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, start=1):
                            for regex, desc in SECRET_PATTERNS:
                                # Skip matches in doc examples if explicitly marked as placeholder
                                if "your-" in line or "placeholder" in line or "example" in line:
                                    continue
                                match = regex.search(line)
                                if match:
                                    findings.append({
                                        "type": "SECRET_PATTERN",
                                        "file": rel_path,
                                        "line": line_num,
                                        "detail": f"Potential {desc} detected: {match.group(0)[:8]}..."
                                    })
                except Exception:
                    pass

    return findings


def main():
    parser = argparse.ArgumentParser(description="Repository Safety and Secrets Scanner")
    parser.add_argument("--root", default=os.getcwd(), help="Root directory to scan (default: current working directory)")
    parser.add_argument("--quick", action="store_true", help="Quick check (filenames and extensions only)")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    args = parser.parse_args()

    findings = scan_repository(args.root, quick=args.quick)

    if args.json:
        print(json.dumps({"passed": len(findings) == 0, "findings": findings}, indent=2))
    else:
        print("==================================================")
        print(" Repository Safety Check")
        print("==================================================")
        if not findings:
            print("[PASS] No configured repository-content safety findings detected.")
        else:
            print(f"[FAIL] Found {len(findings)} potential safety issues:")
            for item in findings:
                loc = f"{item['file']}:{item.get('line', '')}" if 'line' in item else item['file']
                print(f"  - [{item['type']}] {loc} -> {item['detail']}")
        print("==================================================")

    sys.exit(0 if len(findings) == 0 else 1)


if __name__ == "__main__":
    main()
