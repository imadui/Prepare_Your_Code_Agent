import json
import os
import sys
import tomllib
import unittest


class TestTemplates(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_codex_config_toml_valid(self):
        path = os.path.join(self.root, "templates", "codex", "config.toml")
        self.assertTrue(os.path.exists(path), f"Missing {path}")
        with open(path, "rb") as f:
            data = tomllib.load(f)
        self.assertIn("model", data)
        self.assertIn("approval_policy", data)
        self.assertIn("sandbox_mode", data)
        self.assertIn("agents", data)

    def test_opencode_json_valid(self):
        path = os.path.join(self.root, "templates", "opencode", "opencode.json")
        self.assertTrue(os.path.exists(path), f"Missing {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("agents", data)
        self.assertIn("providers", data)
        self.assertIn("mcp", data)
        self.assertIn("servers", data["mcp"])

    def test_claude_code_settings_json_valid(self):
        path = os.path.join(self.root, "templates", "claude-code", "settings.json")
        self.assertTrue(os.path.exists(path), f"Missing {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("permissions", data)
        self.assertIn("allow", data["permissions"])
        self.assertIn("ask", data["permissions"])
        self.assertIn("deny", data["permissions"])

    def test_claude_code_instruction_and_extensions_exist(self):
        base = os.path.join(self.root, "templates", "claude-code")
        self.assertTrue(os.path.exists(os.path.join(base, "CLAUDE.md")))
        self.assertTrue(os.path.exists(os.path.join(base, "agents", "reviewer.md")))
        self.assertTrue(os.path.exists(os.path.join(base, "skills", "validate", "SKILL.md")))

    def test_codex_hooks_json_valid(self):
        path = os.path.join(self.root, "templates", "codex", "hooks.json")
        self.assertTrue(os.path.exists(path), f"Missing {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("hooks", data)

    def test_env_example_contains_all_providers(self):
        path = os.path.join(self.root, ".env.example")
        self.assertTrue(os.path.exists(path), f"Missing {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("OPENAI_API_KEY", content)
        self.assertIn("GEMINI_API_KEY", content)
        self.assertIn("ANTHROPIC_API_KEY", content)
        self.assertIn("AZURE_OPENAI_API_KEY", content)
        self.assertIn("GOOGLE_CLOUD_PROJECT", content)
        self.assertIn("COMPATIBLE_BASE_URL", content)


if __name__ == "__main__":
    unittest.main()
