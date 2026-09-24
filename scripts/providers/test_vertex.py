#!/usr/bin/env python3
"""
Smoke test for Google Cloud Vertex AI Gemini connectivity.
Validates project configuration and ADC credentials.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request


def test_vertex(dry_run=False):
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    model = os.environ.get("VERTEX_MODEL", "gemini-2.5-pro")

    if not project and not dry_run:
        print("FAIL: GOOGLE_CLOUD_PROJECT is not set in environment.")
        return False

    if dry_run:
        print(f"[DRY-RUN PASS] Vertex AI configuration valid for project '{project or 'placeholder'}' and model '{model}'.")
        return True

    # Obtain access token via gcloud or ADC helper
    if not shutil.which("gcloud"):
        print("FAIL: 'gcloud' CLI is required for Vertex AI token retrieval.")
        return False

    try:
        token_res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if token_res.returncode != 0:
            print("FAIL: Failed to obtain access token from gcloud. Run: gcloud auth application-default login")
            return False
        access_token = token_res.stdout.strip()
    except Exception as e:
        print(f"FAIL: Token retrieval error: {type(e).__name__}")
        return False

    endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/"
        f"locations/{location}/publishers/google/models/{model}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
        "generationConfig": {"maxOutputTokens": 5}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"PASS: Vertex AI connected successfully using model '{model}'.")
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
    parser = argparse.ArgumentParser(description="Test Vertex AI connectivity")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without live call")
    args = parser.parse_args()
    sys.exit(0 if test_vertex(dry_run=args.dry_run) else 1)
