#!/usr/bin/env python3
"""
Smoke test for OpenAI API connectivity.
Reads OPENAI_API_KEY and sends a minimal request to verify endpoint reachability.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def test_openai(dry_run=False):
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-6-sol")

    if not api_key and not dry_run:
        print("FAIL: OPENAI_API_KEY is not set in environment.")
        return False

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }

    if dry_run:
        print(f"[DRY-RUN PASS] OpenAI payload formed for model '{model}' at '{base_url}'.")
        return True

    endpoint = f"{base_url}/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                resp_data = json.loads(resp.read().decode("utf-8"))
                print(f"PASS: OpenAI API connected successfully using model '{model}'.")
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
    parser = argparse.ArgumentParser(description="Test OpenAI API connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate request format without live call")
    args = parser.parse_args()
    sys.exit(0 if test_openai(dry_run=args.dry_run) else 1)
