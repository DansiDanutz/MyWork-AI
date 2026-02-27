#!/usr/bin/env python3
"""Comprehensive tests for ai_review.py

Tests cover:
- Language detection from file extensions
- Review prompt generation
- Output formatting for different result types
- Git diff handling (mocked)
- File review error handling
"""

import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ai_review import (
    detect_language,
    create_review_prompt,
    format_output,
    call_openrouter_api,
    get_git_diff,
    review_file,
    review_diff
)


class TestDetectLanguage:
    """Test language detection from file extensions."""
    
    def test_python_extension(self):
        """Detect Python language."""
        assert detect_language("test.py") == "Python"
        assert detect_language("app.py") == "Python"
        assert detect_language("/path/to/module.py") == "Python"
    
    def test_javascript_typescript(self):
        """Detect JavaScript and TypeScript."""
        assert detect_language("script.js") == "JavaScript"
        assert detect_language("app.ts") == "TypeScript"
        assert detect_language("component.jsx") == "React JSX"
        assert detect_language("component.tsx") == "React TSX"
    
    def test_web_languages(self):
        """Detect web development languages."""
        assert detect_language("index.html") == "HTML"
        assert detect_language("style.css") == "CSS"
        assert detect_language("styles.scss") == "SCSS"
        assert detect_language("app.vue") == "Vue.js"
    
    def test_config_languages(self):
        """Detect configuration languages."""
        assert detect_language("config.yaml") == "YAML"
        assert detect_language("config.yml") == "YAML"
        assert detect_language("data.json") == "JSON"
        assert detect_language("script.sh") == "Shell Script"
    
    def test_system_languages(self):
        """Detect system programming languages."""
        assert detect_language("main.c") == "C"
        assert detect_language("app.cpp") == "C++"
        assert detect_language("program.cs") == "C#"
        assert detect_language("main.go") == "Go"
        assert detect_language("lib.rs") == "Rust"
        assert detect_language("app.java") == "Java"
    
    def test_data_analysis_languages(self):
        """Detect data analysis languages."""
        assert detect_language("script.r") == "R"
        assert detect_language("app.scala") == "Scala"
        assert detect_language("code.sql") == "SQL"
    
    def test_other_languages(self):
        """Detect other common languages."""
        assert detect_language("app.php") == "PHP"
        assert detect_language("script.rb") == "Ruby"
        assert detect_language("app.swift") == "Swift"
        assert detect_language("app.kt") == "Kotlin"
        assert detect_language("app.dart") == "Dart"
    
    def test_unknown_extension(self):
        """Return 'Unknown' for unsupported extensions."""
        assert detect_language("file.unknown") == "Unknown"
        assert detect_language("noextension") == "Unknown"
        assert detect_language("file.xyz123") == "Unknown"
    
    def test_case_insensitive(self):
        """Language detection is case-insensitive."""
        assert detect_language("TEST.PY") == "Python"
        assert detect_language("App.JS") == "JavaScript"
        assert detect_language("FILE.TS") == "TypeScript"


class TestCreateReviewPrompt:
    """Test review prompt generation."""
    
    def test_basic_prompt_structure(self):
        """Prompt has required sections."""
        code = "def hello():\n    print('world')"
        prompt = create_review_prompt(code, "Python")
        
        assert "You are an expert code reviewer" in prompt
        assert "CODE TO REVIEW:" in prompt
        assert code in prompt
        assert "## 🔍 **ISSUES FOUND**" in prompt
        assert "## 💡 **SUGGESTIONS**" in prompt
        assert "## 🛡️ **SECURITY CONCERNS**" in prompt
        assert "## ⚡ **PERFORMANCE TIPS**" in prompt
        assert "## 🧹 **CODE STYLE**" in prompt
        assert "## ✅ **POSITIVE FEEDBACK**" in prompt
        assert "## 📊 **OVERALL SCORE**" in prompt
    
    def test_language_in_prompt(self):
        """Language is included in prompt."""
        code = "const x = 42;"
        prompt = create_review_prompt(code, "JavaScript")
        
        assert "JavaScript" in prompt
        assert "```javascript" in prompt.lower()
    
    def test_context_in_prompt(self):
        """Context is included in prompt."""
        code = "print('test')"
        prompt = create_review_prompt(code, "Python", context="Review for production")
        
        assert "CONTEXT: Review for production" in prompt
    
    def test_empty_context(self):
        """Prompt works with empty context."""
        code = "x = 1"
        prompt = create_review_prompt(code, "Python", context="")
        
        assert "CONTEXT: " in prompt
    
    def test_multiline_code(self):
        """Prompt preserves code formatting."""
        code = """
def test():
    return True
"""
        prompt = create_review_prompt(code, "Python")
        
        assert "def test():" in prompt
        assert "return True" in prompt
    
    def test_special_characters_in_code(self):
        """Prompt handles special characters."""
        code = "print('Hello © World™')"
        prompt = create_review_prompt(code, "Python")
        
        assert "Hello © World™" in prompt


class TestFormatOutput:
    """Test output formatting."""
    
    def test_format_file_review(self):
        """Format file review output."""
        result = {
            "file": "test.py",
            "language": "Python",
            "lines": 42,
            "review": "Great code!"
        }
        output = format_output(result)
        
        assert "**File Review**: test.py" in output
        assert "**Language**: Python" in output
        assert "**Lines**: 42" in output
        assert "Great code!" in output
    
    def test_format_git_diff_staged(self):
        """Format staged git diff review."""
        result = {
            "type": "git_diff",
            "staged": True,
            "review": "Good changes"
        }
        output = format_output(result)
        
        assert "**Git Diff Review** (Staged Changes)" in output
        assert "Good changes" in output
    
    def test_format_git_diff_unstaged(self):
        """Format unstaged git diff review."""
        result = {
            "type": "git_diff",
            "staged": False,
            "review": "Review complete"
        }
        output = format_output(result)
        
        assert "**Git Diff Review** (Unstaged Changes)" in output
        assert "Review complete" in output
    
    def test_format_error(self):
        """Format error messages."""
        result = {"error": "File not found"}
        output = format_output(result)
        
        assert output.startswith("❌")
        assert "File not found" in output
    
    def test_format_missing_optional_fields(self):
        """Handle missing optional fields gracefully."""
        result = {
            "file": "test.js",
            "review": "OK"
        }
        output = format_output(result)
        
        assert "**File Review**: test.js" in output
        assert "OK" in output
        # Missing lines and language should not cause errors
        assert "**Language**" not in output
        assert "**Lines**" not in output
    
    def test_format_empty_review(self):
        """Handle empty or missing review."""
        result = {
            "file": "test.py",
            "language": "Python",
            "lines": 10
        }
        output = format_output(result)
        
        assert "No review available" in output


class TestGetGitDiff:
    """Test git diff retrieval."""
    
    @patch('subprocess.run')
    def test_get_unstaged_diff(self, mock_run):
        """Get unstaged git diff."""
        mock_run.return_value = MagicMock(stdout="diff content")
        diff = get_git_diff(staged=False)
        
        assert diff == "diff content"
        mock_run.assert_called_once_with(["git", "diff"], capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_get_staged_diff(self, mock_run):
        """Get staged git diff."""
        mock_run.return_value = MagicMock(stdout="staged diff")
        diff = get_git_diff(staged=True)
        
        assert diff == "staged diff"
        mock_run.assert_called_once_with(["git", "diff", "--staged"], capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_git_diff_exception(self, mock_run):
        """Handle exceptions when getting git diff."""
        mock_run.side_effect = Exception("Git not found")
        diff = get_git_diff(staged=False)
        
        assert "Error getting git diff:" in diff
        assert "Git not found" in diff


class TestReviewFile:
    """Test file review functionality."""
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_review_nonexistent_file(self, mock_exists, mock_open):
        """Return error for non-existent file."""
        mock_exists.return_value = False
        result = review_file("nonexistent.py")
        
        assert "error" in result
        assert "File not found" in result["error"]
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_review_empty_file(self, mock_exists, mock_open):
        """Return error for empty file."""
        mock_exists.return_value = True
        mock_open.return_value.read.return_value = ""
        result = review_file("empty.py")
        
        assert "error" in result
        assert "File is empty" in result["error"]
    
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('ai_review.call_openrouter_api')
    def test_review_successful_file(self, mock_api, mock_exists, mock_open):
        """Successfully review a file."""
        mock_exists.return_value = True
        mock_open.return_value.read.return_value = "print('hello')"
        mock_api.return_value = "Review: Good code!"
        
        result = review_file("test.py")
        
        assert result["file"] == "test.py"
        assert result["language"] == "Python"
        assert result["lines"] == 1
        assert result["review"] == "Review: Good code!"
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_review_file_io_error(self, mock_exists, mock_open):
        """Handle IO errors when reading file."""
        mock_exists.return_value = True
        mock_open.side_effect = IOError("Permission denied")
        result = review_file("test.py")
        
        assert "error" in result
        assert "Error reviewing file" in result["error"]
    
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('ai_review.call_openrouter_api')
    def test_review_detects_language(self, mock_api, mock_exists, mock_open):
        """Detect correct language for different files."""
        test_cases = [
            ("test.js", "JavaScript"),
            ("app.ts", "TypeScript"),
            ("index.html", "HTML"),
            ("style.css", "CSS"),
            ("config.yaml", "YAML"),
            ("script.sh", "Shell Script"),
        ]
        
        mock_exists.return_value = True
        mock_open.return_value.read.return_value = "code"
        mock_api.return_value = "Review"
        
        for filename, expected_lang in test_cases:
            result = review_file(filename)
            assert result["language"] == expected_lang


class TestReviewDiff:
    """Test git diff review functionality."""
    
    @patch('ai_review.get_git_diff')
    @patch('ai_review.call_openrouter_api')
    def test_review_empty_diff(self, mock_api, mock_diff):
        """Return error for empty diff."""
        mock_diff.return_value = ""
        result = review_diff(staged=False)
        
        assert "error" in result
        assert "No working directory changes to review" in result["error"]
    
    @patch('ai_review.get_git_diff')
    @patch('ai_review.call_openrouter_api')
    def test_review_successful_diff(self, mock_api, mock_diff):
        """Successfully review git diff."""
        mock_diff.return_value = "diff --git a/test.py b/test.py"
        mock_api.return_value = "Diff review: Good changes!"
        
        result = review_diff(staged=False)
        
        assert result["type"] == "git_diff"
        assert result["staged"] is False
        assert result["review"] == "Diff review: Good changes!"
    
    @patch('ai_review.get_git_diff')
    @patch('ai_review.call_openrouter_api')
    def test_review_staged_diff(self, mock_api, mock_diff):
        """Review staged diff."""
        mock_diff.return_value = "staged changes"
        mock_api.return_value = "Review"
        
        result = review_diff(staged=True)
        
        assert result["staged"] is True
    
    @patch('ai_review.get_git_diff')
    def test_review_diff_exception(self, mock_diff):
        """Handle exceptions during diff review."""
        mock_diff.side_effect = Exception("Git error")
        result = review_diff(staged=False)
        
        assert "error" in result
        assert "Error reviewing diff" in result["error"]


class TestCallOpenRouterApi:
    """Test OpenRouter API calls (integration tests with mocking)."""
    
    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    def test_successful_api_call(self, mock_urlopen):
        """Test successful API response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"choices": [{"message": {"content": "Review response"}}]}'
        mock_urlopen.return_value = mock_response
        
        result = call_openrouter_api("Review this code")
        
        assert result == "Review response"
    
    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    def test_api_call_no_choices(self, mock_urlopen):
        """Handle API response with no choices."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": []}'
        mock_urlopen.return_value = mock_response
        
        result = call_openrouter_api("Review this code")
        
        assert result == "Error: No response from API"
    
    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    def test_api_call_exception(self, mock_urlopen):
        """Handle API call exceptions."""
        mock_urlopen.side_effect = Exception("Network error")
        
        result = call_openrouter_api("Review this code")
        
        assert "Error: Failed to call OpenRouter API" in result
        assert "Network error" in result
    
    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {}, clear=True)
    def test_api_call_no_key(self, mock_urlopen):
        """API call with no API key set."""
        # This should still make the request, just with empty key
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"choices": [{"message": {"content": "Test"}}]}'
        mock_urlopen.return_value = mock_response
        
        # Should not raise exception, just use empty string for key
        result = call_openrouter_api("Test")
        assert result == "Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
