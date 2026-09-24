#!/usr/bin/env python3
"""
Smoke test for Microsoft Azure OpenAI connectivity.
Reads AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and deployment settings.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def test_azure(dry_run=False):
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION") or ("your-api-version" if dry_run else "")

    if not dry_run and (not api_key or not endpoint or not deployment or not api_version):
        print("FAIL: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, or AZURE_OPENAI_API_VERSION is missing.")
        return False

    payload = {
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }

    if dry_run:
        print(f"[DRY-RUN PASS] Azure OpenAI payload formed for deployment '{deployment or 'placeholder'}'.")
        return True

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"PASS: Azure OpenAI connected successfully for deployment '{deployment}'.")
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
    parser = argparse.ArgumentParser(description="Test Azure OpenAI connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate request format without live call")
    args = parser.parse_args()
    sys.exit(0 if test_azure(dry_run=args.dry_run) else 1)
