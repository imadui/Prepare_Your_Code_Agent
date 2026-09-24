#!/usr/bin/env python3
"""
Environment Doctor for Prepare Your Code Agent.
Checks runtime dependencies, CLI availability, provider environment variable
presence (without printing values), git status, and temporary directory hygiene.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_command_version(cmd_args):
    try:
        res = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if res.returncode == 0:
            output = (res.stdout or res.stderr).strip().splitlines()
            return output[0] if output else "Installed (no version output)"
        return None
    except Exception:
        return None


def check_tools():
    tools = {
        "python": [sys.executable, "--version"],
        "git": ["git", "--version"],
        "gh": ["gh", "--version"],
        "node": ["node", "--version"],
        "codex": ["codex", "--version"],
        "claude": ["claude", "--version"],
        "opencode": ["opencode", "--version"],
    }
    results = {}
    for name, cmd in tools.items():
        version = get_command_version(cmd)
        results[name] = {
            "available": version is not None,
            "version": version or "Not found"
        }
    return results


def check_provider_env_vars():
    vars_to_check = [
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT",
        "COMPATIBLE_BASE_URL",
        "COMPATIBLE_API_KEY"
    ]
    status = {}
    for var in vars_to_check:
        val = os.environ.get(var)
        status[var] = "PRESENT" if val and len(val.strip()) > 0 else "NOT SET"
    return status


def check_git_repo(repo_dir=REPO_ROOT):
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=3,
            check=False
        )
        if res.returncode != 0:
            if "dubious ownership" in (res.stderr or "").lower():
                return {
                    "is_git_repo": True,
                    "status": "Dubious ownership detected. Resolve repository ownership or trust through your approved Git/workstation process; this doctor does not modify global Git configuration.",
                    "safe_directory_needed": True
                }
            return {"is_git_repo": False, "status": "Not a git repository"}
        
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=3,
            check=False
        )
        dirty = bool(status_res.stdout.strip())
        branch_res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=3,
            check=False
        )
        branch = branch_res.stdout.strip() or "HEAD (detached)"
        return {
            "is_git_repo": True,
            "branch": branch,
            "clean": not dirty,
            "uncommitted_files": len(status_res.stdout.strip().splitlines()) if dirty else 0
        }
    except Exception as e:
        return {"is_git_repo": False, "error": str(e)}


def check_temp_dir(repo_dir=REPO_ROOT):
    tmp_dir = os.path.join(repo_dir, ".agent-tmp")
    exists = os.path.exists(tmp_dir)
    file_count = 0
    if exists:
        for root, _, files in os.walk(tmp_dir):
            file_count += len(files)
    return {
        "path": ".agent-tmp",
        "exists": exists,
        "file_count": file_count
    }


def run_doctor():
    data = {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine()
        },
        "tools": check_tools(),
        "providers": check_provider_env_vars(),
        "git": check_git_repo(),
        "temp_directory": check_temp_dir()
    }
    return data


def print_human_report(data):
    print("==================================================")
    print(" Prepare Your Code Agent - Environment Doctor")
    print("==================================================")
    print(f"OS: {data['os']['system']} {data['os']['release']} ({data['os']['machine']})")
    print("\n--- Command-Line Tools ---")
    for name, info in data["tools"].items():
        status = "[OK]  " if info["available"] else "[WARN]"
        print(f"  {status} {name:<10}: {info['version']}")

    print("\n--- Provider Environment Variables ---")
    for var, status in data["providers"].items():
        indicator = "[SET] " if status == "PRESENT" else "[NONE]"
        print(f"  {indicator} {var:<30}: {status}")

    print("\n--- Git Repository State ---")
    git = data["git"]
    if git.get("is_git_repo") and not git.get("safe_directory_needed"):
        state = "Clean" if git.get("clean") else f"Dirty ({git.get('uncommitted_files')} changed files)"
        print(f"  [OK]   Branch: {git.get('branch')} | Working tree: {state}")
    else:
        print(f"  [WARN] {git.get('status', 'Not inside a git repository')}")

    print("\n--- Temporary Storage (.agent-tmp/) ---")
    tmp = data["temp_directory"]
    if tmp["exists"] and tmp["file_count"] > 0:
        print(f"  [WARN] .agent-tmp contains {tmp['file_count']} files. Run cleanup before task completion.")
    else:
        print("  [OK]   .agent-tmp is empty / clean.")
    print("==================================================")


def main():
    parser = argparse.ArgumentParser(description="Environment Doctor for Prepare Your Code Agent")
    parser.add_argument("--json", action="store_true", help="Output doctor report as JSON")
    args = parser.parse_args()

    data = run_doctor()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_human_report(data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
