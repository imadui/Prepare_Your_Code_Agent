#!/usr/bin/env python3
"""
Smoke test for Generic OpenAI-Compatible Gateway connectivity.
Works with LiteLLM, vLLM, Ollama, LM Studio, Groq, OpenRouter, and custom proxies.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def test_compatible(dry_run=False):
    base_url = os.environ.get("COMPATIBLE_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("COMPATIBLE_API_KEY", "dummy-key")
    model = os.environ.get("COMPATIBLE_MODEL") or ("your-model-name" if dry_run else "")

    if not dry_run and (not base_url or not model):
        print("FAIL: COMPATIBLE_BASE_URL and COMPATIBLE_MODEL must be set in environment.")
        return False

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }

    if dry_run:
        print(f"[DRY-RUN PASS] Compatible payload formed for model '{model}' at '{base_url or 'http://localhost:11434/v1'}'.")
        return True

    endpoint = f"{base_url}/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(endpoint, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"PASS: Compatible endpoint connected successfully using model '{model}'.")
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
    parser = argparse.ArgumentParser(description="Test OpenAI-compatible endpoint connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate request format without live call")
    args = parser.parse_args()
    sys.exit(0 if test_compatible(dry_run=args.dry_run) else 1)
