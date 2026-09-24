import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.validation.run_acceptance import detect_test_command


class TestAcceptanceCommandDetection(unittest.TestCase):

    def test_detects_npm_test_from_package_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as f:
                json.dump({"scripts": {"test": "node --test"}}, f)

            self.assertEqual(detect_test_command(tmpdir), ["npm", "test"])

    def test_falls_back_to_python_unittest_for_tests_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "tests"))

            self.assertEqual(
                detect_test_command(tmpdir),
                [sys.executable, "-m", "unittest", "discover", "tests"],
            )

    def test_explicit_test_command_takes_precedence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "tests"))

            command = detect_test_command(tmpdir, test_command="python -m pytest -q")
            self.assertEqual(command[:3], ["python", "-m", "pytest"])


if __name__ == "__main__":
    unittest.main()
