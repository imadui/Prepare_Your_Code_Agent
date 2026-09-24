#!/usr/bin/env python3
"""
Smoke test for Google Gemini API (AI Studio Developer API).
Reads GEMINI_API_KEY and sends a minimal request to verify reachability.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def test_gemini(dry_run=False):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL") or ("your-model-name" if dry_run else "")

    if not dry_run and (not api_key or not model):
        print("FAIL: GEMINI_API_KEY and GEMINI_MODEL must be set in environment.")
        return False

    payload = {
        "contents": [{"parts": [{"text": "ping"}]}],
        "generationConfig": {"maxOutputTokens": 5}
    }

    if dry_run:
        print(f"[DRY-RUN PASS] Gemini payload formed for model '{model}'.")
        return True

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"PASS: Gemini API connected successfully using model '{model}'.")
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
    parser = argparse.ArgumentParser(description="Test Gemini API connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate request format without live call")
    args = parser.parse_args()
    sys.exit(0 if test_gemini(dry_run=args.dry_run) else 1)
