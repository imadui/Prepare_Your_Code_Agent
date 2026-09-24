#!/usr/bin/env python3
"""
Acceptance Benchmark Validator for Coding Agent Workspace.
Evaluates an agent's deliverable against the objective criteria
defined in examples/acceptance-test/checklist.md.
"""

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.validation.safety_check import scan_repository


def evaluate_workspace(workspace_dir, test_command=None):
    checks = []

    # 1. Check Git status
    git_clean = False
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            check=False
        )
        if res.returncode == 0:
            git_clean = len(res.stdout.strip()) == 0
            checks.append({
                "name": "Git Status",
                "passed": git_clean,
                "detail": "Working tree is clean" if git_clean else "Uncommitted files present"
            })
        elif "dubious ownership" in (res.stderr or "").lower():
            checks.append({
                "name": "Git Status",
                "passed": False,
                "detail": "Git safe.directory issue detected. Resolve repository ownership or trust through your approved Git/workstation process; this validator does not modify global Git configuration."
            })
        else:
            checks.append({
                "name": "Git Status",
                "passed": False,
                "detail": "Not a valid git repository"
            })
    except Exception as e:
        checks.append({"name": "Git Status", "passed": False, "detail": str(e)})

    # 2. Check for Automated Tests and Execution
    test_dir = os.path.join(workspace_dir, "tests")
    tests_exist = os.path.exists(test_dir)
    if tests_exist:
        try:
            test_run = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "tests"],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=45,
                check=False
            )
            tests_passed = test_run.returncode == 0
            checks.append({
                "name": "Automated Tests",
                "passed": tests_passed,
                "detail": "All tests passed (exit 0)" if tests_passed else "Test suite reported failures"
            })
        except Exception as e:
            checks.append({"name": "Automated Tests", "passed": False, "detail": f"Execution error: {e}"})
    else:
        checks.append({"name": "Automated Tests", "passed": False, "detail": "tests/ directory not found"})

    # 3. Security & Secrets Scanner
    findings = scan_repository(workspace_dir, quick=False)
    checks.append({
        "name": "Security & Hygiene",
        "passed": len(findings) == 0,
        "detail": "0 sensitive patterns or forbidden files" if not findings else f"{len(findings)} security findings detected"
    })

    # 4. Network Safety: Loopback Binding Check
    network_safe = True
    suspicious_bindings = []
    for root, _, files in os.walk(workspace_dir):
        if any(ign in root for ign in [".git", ".venv", "node_modules", ".agent-tmp"]):
            continue
        for fname in files:
            if fname.endswith((".py", ".ts", ".js", ".json", ".toml", ".yaml")):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "0.0.0.0" in content and "never bind" not in content.lower() and "forbidden" not in content.lower():
                            suspicious_bindings.append(os.path.relpath(fpath, workspace_dir))
                            network_safe = False
                except Exception:
                    pass
    checks.append({
        "name": "Network Safety (Loopback)",
        "passed": network_safe,
        "detail": "All servers conform to loopback (127.0.0.1/localhost)" if network_safe else f"Potential 0.0.0.0 binding in: {suspicious_bindings}"
    })

    # 5. Check for .agent-tmp hygiene
    tmp_dir = os.path.join(workspace_dir, ".agent-tmp")
    tmp_clean = True
    count = 0
    if os.path.exists(tmp_dir):
        count = sum(len(files) for _, _, files in os.walk(tmp_dir))
        tmp_clean = count == 0
    checks.append({
        "name": "Temporary File Hygiene",
        "passed": tmp_clean,
        "detail": ".agent-tmp is empty" if tmp_clean else f".agent-tmp contains {count} files"
    })

    all_passed = all(c["passed"] for c in checks)
    return {"all_passed": all_passed, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description="Evaluate workspace acceptance criteria")
    parser.add_argument("--workspace", default=os.getcwd(), help="Path to workspace")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--test-command", help="Optional test command to run instead of auto-detection")
    args = parser.parse_args()

    res = evaluate_workspace(args.workspace, test_command=args.test_command)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("==================================================")
        print(" Acceptance Benchmark Evaluation")
        print("==================================================")
        for check in res["checks"]:
            status = "[PASS]" if check["passed"] else "[FAIL]"
            print(f"  {status} {check['name']:<25}: {check['detail']}")
        print("==================================================")
        print(f"Overall Result: {'PASS' if res['all_passed'] else 'FAIL'}")

    sys.exit(0 if res["all_passed"] else 1)


if __name__ == "__main__":
    main()
