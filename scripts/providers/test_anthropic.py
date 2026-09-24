#!/usr/bin/env python3
"""
Smoke test for Anthropic Claude API connectivity.
Reads ANTHROPIC_API_KEY and sends a minimal request to verify reachability.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def test_anthropic(dry_run=False):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1").rstrip("/")
    model = os.environ.get("ANTHROPIC_MODEL") or ("your-model-name" if dry_run else "")

    if not dry_run and (not api_key or not model):
        print("FAIL: ANTHROPIC_API_KEY and ANTHROPIC_MODEL must be set in environment.")
        return False

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }

    if dry_run:
        print(f"[DRY-RUN PASS] Anthropic payload formed for model '{model}' at '{base_url}'.")
        return True

    endpoint = f"{base_url}/messages"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"PASS: Anthropic API connected successfully using model '{model}'.")
                return True
            print(f"FAIL: Unexpected status {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        print(f"FAIL: HTTP error {e.code} ({e.reason})")
        return False
    except Exception as e:
        print(f"FAIL: Network or connection error: {type(e).__name__}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Anthropic API connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate request format without live call")
    args = parser.parse_args()
    sys.exit(0 if test_anthropic(dry_run=args.dry_run) else 1)
