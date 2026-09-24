import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.providers.test_openai import test_openai
from scripts.providers.test_gemini import test_gemini
from scripts.providers.test_vertex import test_vertex
from scripts.providers.test_anthropic import test_anthropic
from scripts.providers.test_azure import test_azure
from scripts.providers.test_compatible import test_compatible


class TestProviders(unittest.TestCase):

    def test_dry_run_modes(self):
        # All provider scripts must succeed in dry-run mode without real network calls or keys
        self.assertTrue(test_openai(dry_run=True))
        self.assertTrue(test_gemini(dry_run=True))
        self.assertTrue(test_vertex(dry_run=True))
        self.assertTrue(test_anthropic(dry_run=True))
        self.assertTrue(test_azure(dry_run=True))
        self.assertTrue(test_compatible(dry_run=True))

    def test_missing_credentials_graceful_failure(self):
        # When keys are absent and dry_run=False, scripts should fail gracefully (return False)
        env_backup = dict(os.environ)
        for k in ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "AZURE_OPENAI_API_KEY"]:
            if k in os.environ:
                del os.environ[k]
        try:
            self.assertFalse(test_openai(dry_run=False))
            self.assertFalse(test_gemini(dry_run=False))
            self.assertFalse(test_anthropic(dry_run=False))
            self.assertFalse(test_azure(dry_run=False))
        finally:
            os.environ.clear()
            os.environ.update(env_backup)


if __name__ == "__main__":
    unittest.main()
