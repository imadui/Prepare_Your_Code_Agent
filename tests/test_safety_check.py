import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.validation.safety_check import scan_repository


class TestSafetyCheck(unittest.TestCase):

    def test_current_repo_is_safe(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        findings = scan_repository(root_dir, quick=False)
        self.assertEqual(findings, [], f"Expected 0 findings in clean repo, got: {findings}")

    def test_catches_forbidden_file_and_patterns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create a forbidden .env file
            env_file = os.path.join(tmpdir, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("SECRET=123")

            # 2. Create a forbidden private key file
            key_file = os.path.join(tmpdir, "test.pem")
            with open(key_file, "w", encoding="utf-8") as f:
                f.write("dummy key")

            # 3. Create a file containing a simulated real secret pattern
            secret_file = os.path.join(tmpdir, "leak.py")
            with open(secret_file, "w", encoding="utf-8") as f:
                fake_key = ''.join(['s', 'k', '-']) + ('a' * 25)
                f.write(f'API_KEY = {fake_key}\n')

            findings = scan_repository(tmpdir, quick=False)
            types = [f["type"] for f in findings]
            self.assertIn("FORBIDDEN_FILE", types)
            self.assertIn("FORBIDDEN_EXTENSION", types)
            self.assertIn("SECRET_PATTERN", types)


if __name__ == "__main__":
    unittest.main()
