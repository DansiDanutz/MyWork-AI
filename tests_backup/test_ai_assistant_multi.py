"""Tests for multi-provider AI assistant."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ai_assistant import (
    PROVIDERS, MODEL_SHORTCUTS, _detect_provider, _get_provider_key,
    _load_env, cmd_ai, cmd_ai_providers, cmd_ai_models,
)


class TestProviderConfig(unittest.TestCase):
    """Test provider configuration."""

    def test_all_providers_have_required_keys(self):
        for name, prov in PROVIDERS.items():
            self.assertIn("url", prov, f"{name} missing url")
            self.assertIn("env_key", prov, f"{name} missing env_key")
            self.assertIn("default_model", prov, f"{name} missing default_model")

    def test_four_providers_exist(self):
        self.assertIn("openrouter", PROVIDERS)
        self.assertIn("deepseek", PROVIDERS)
        self.assertIn("openai", PROVIDERS)
        self.assertIn("gemini", PROVIDERS)

    def test_model_shortcuts_resolve_to_valid_providers(self):
        for shortcut, (prov, model) in MODEL_SHORTCUTS.items():
            self.assertIn(prov, PROVIDERS, f"Shortcut '{shortcut}' uses unknown provider '{prov}'")
            self.assertTrue(len(model) > 0, f"Shortcut '{shortcut}' has empty model")

    def test_model_shortcuts_contain_common_models(self):
        self.assertIn("deepseek", MODEL_SHORTCUTS)
        self.assertIn("gemini", MODEL_SHORTCUTS)
        self.assertIn("claude", MODEL_SHORTCUTS)
        self.assertIn("gpt4", MODEL_SHORTCUTS)


class TestProviderDetection(unittest.TestCase):
    """Test auto-detection of providers."""

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False)
    def test_detect_openrouter(self):
        name, key = _detect_provider()
        self.assertEqual(name, "openrouter")
        self.assertEqual(key, "test-key")

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "ds-key"}, clear=False)
    def test_detect_deepseek(self):
        # Clear higher-priority keys
        env = {k: "" for k in ["OPENROUTER_API_KEY"]}
        env["DEEPSEEK_API_KEY"] = "ds-key"
        with patch.dict(os.environ, env, clear=False):
            # Force re-detection
            os.environ.pop("OPENROUTER_API_KEY", None)
            name, key = _detect_provider()
            # Should find deepseek if openrouter not set
            self.assertIsNotNone(name)

    @patch("tools.ai_assistant._load_env")
    @patch.dict(os.environ, {}, clear=True)
    def test_detect_none(self, mock_env):
        name, key = _detect_provider()
        self.assertIsNone(name)
        self.assertIsNone(key)


class TestGetProviderKey(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": "gem-key"}, clear=False)
    def test_get_gemini_key(self):
        key = _get_provider_key("gemini")
        self.assertEqual(key, "gem-key")

    @patch("tools.ai_assistant._load_env")
    @patch.dict(os.environ, {}, clear=True)
    def test_no_key_returns_none(self, mock_env):
        key = _get_provider_key("openai")
        self.assertFalse(key)  # empty string or None


class TestCmdAi(unittest.TestCase):
    """Test cmd_ai routing."""

    @patch("builtins.print")
    def test_no_args_shows_help(self, mock_print):
        result = cmd_ai([])
        self.assertEqual(result, 0)
        # Should have printed help text
        calls = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("AI Assistant", calls)

    @patch("builtins.print")
    def test_providers_command(self, mock_print):
        result = cmd_ai(["providers"])
        self.assertEqual(result, 0)

    @patch("builtins.print")
    def test_models_command(self, mock_print):
        result = cmd_ai(["models"])
        self.assertEqual(result, 0)

    @patch("builtins.print")
    def test_unknown_treated_as_ask(self, mock_print):
        """Unknown subcommands should be treated as questions."""
        with patch("tools.ai_assistant._call_llm", return_value="test response"):
            result = cmd_ai(["what is python"])
            self.assertEqual(result, 0)


class TestProviderURLs(unittest.TestCase):
    """Verify provider URLs are valid."""

    def test_urls_are_https(self):
        for name, prov in PROVIDERS.items():
            self.assertTrue(prov["url"].startswith("https://"), f"{name} URL not HTTPS")

    def test_urls_end_with_completions(self):
        for name, prov in PROVIDERS.items():
            self.assertTrue(prov["url"].endswith("completions"), f"{name} URL doesn't end with completions")


if __name__ == "__main__":
    unittest.main()
