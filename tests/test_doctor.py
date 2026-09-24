import os
import sys
import unittest
from unittest.mock import patch

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doctor.doctor import (
    check_tools,
    check_provider_env_vars,
    check_git_repo,
    check_temp_dir,
    run_doctor
)


class TestDoctor(unittest.TestCase):

    def test_check_tools_returns_dict(self):
        tools = check_tools()
        self.assertIsInstance(tools, dict)
        self.assertIn("python", tools)
        self.assertIn("claude", tools)
        self.assertTrue(tools["python"]["available"])

    def test_provider_env_vars_redaction(self):
        mock_env = {
            "OPENAI_API_KEY": "sk-dummy-test-key-should-never-appear",
            "GEMINI_API_KEY": "",
        }
        with patch.dict(os.environ, mock_env, clear=True):
            res = check_provider_env_vars()
            self.assertEqual(res["OPENAI_API_KEY"], "PRESENT")
            self.assertEqual(res["GEMINI_API_KEY"], "NOT SET")
            self.assertEqual(res["ANTHROPIC_API_KEY"], "NOT SET")
            # Ensure raw secret is not in any values
            for key, val in res.items():
                self.assertNotIn("sk-dummy", val)

    def test_check_git_repo(self):
        git_info = check_git_repo()
        self.assertIsInstance(git_info, dict)
        self.assertIn("is_git_repo", git_info)

    def test_check_temp_dir(self):
        tmp_info = check_temp_dir()
        self.assertIsInstance(tmp_info, dict)
        self.assertIn("exists", tmp_info)
        self.assertIn("file_count", tmp_info)

    def test_run_doctor_structure(self):
        data = run_doctor()
        self.assertIn("os", data)
        self.assertIn("tools", data)
        self.assertIn("providers", data)
        self.assertIn("git", data)
        self.assertIn("temp_directory", data)


if __name__ == "__main__":
    unittest.main()
