#!/usr/bin/env python3
"""Tests for changelog_gen.py module."""

import json
import os
import re
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.changelog_gen import (
    COMMIT_TYPES,
    BREAKING_EMOJI,
    parse_commit,
    group_commits,
    format_markdown,
    format_json,
    get_stats,
    run_git,
    get_tags,
    get_commits,
    cmd_changelog,
)


class TestParseCommit(unittest.TestCase):
    """Test parse_commit function."""
    
    def test_feat_commit(self):
        """Test parsing a feature commit."""
        commit = {
            "subject": "feat: add new API endpoint",
            "body": "Adds /api/v2/users endpoint with pagination",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], None)
        self.assertEqual(result["breaking"], False)
        self.assertEqual(result["description"], "add new API endpoint")
    
    def test_feat_with_scope(self):
        """Test parsing a feature commit with scope."""
        commit = {
            "subject": "feat(api): add rate limiting",
            "body": "Implement token bucket algorithm",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], "api")
        self.assertEqual(result["breaking"], False)
        self.assertEqual(result["description"], "add rate limiting")
    
    def test_fix_commit(self):
        """Test parsing a fix commit."""
        commit = {
            "subject": "fix: resolve memory leak",
            "body": "Fix circular reference in cache",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "fix")
        self.assertEqual(result["scope"], None)
        self.assertEqual(result["description"], "resolve memory leak")
    
    def test_breaking_change_in_body(self):
        """Test parsing a commit with BREAKING CHANGE in body."""
        commit = {
            "subject": "feat: change API response format",
            "body": "BREAKING CHANGE: Response now includes metadata field",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["breaking"], True)
    
    def test_breaking_change_exclamation(self):
        """Test parsing a commit with ! for breaking change."""
        commit = {
            "subject": "feat!: drop support for Python 3.7",
            "body": "Minimum Python version is now 3.8",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["breaking"], True)
        self.assertEqual(result["description"], "drop support for Python 3.7")
    
    def test_scope_with_exclamation(self):
        """Test parsing a commit with scope and !."""
        commit = {
            "subject": "feat(api)!: remove deprecated endpoints",
            "body": "Remove /api/v1/users and /api/v1/posts",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], "api")
        self.assertEqual(result["breaking"], True)
        self.assertEqual(result["description"], "remove deprecated endpoints")
    
    def test_non_conventional_commit(self):
        """Test parsing a non-conventional commit."""
        commit = {
            "subject": "Update README with installation instructions",
            "body": "Added pip install command",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "other")
        self.assertEqual(result["scope"], None)
        self.assertEqual(result["breaking"], False)
        self.assertEqual(result["description"], "Update README with installation instructions")
    
    def test_docs_commit(self):
        """Test parsing a docs commit."""
        commit = {
            "subject": "docs: update API documentation",
            "body": "Add examples for all endpoints",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "docs")
        self.assertEqual(result["description"], "update API documentation")
    
    def test_test_commit(self):
        """Test parsing a test commit."""
        commit = {
            "subject": "test: add unit tests for parser",
            "body": "Add 100% coverage for parse_commit function",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "test")
        self.assertEqual(result["description"], "add unit tests for parser")
    
    def test_ci_commit(self):
        """Test parsing a CI commit."""
        commit = {
            "subject": "ci: add GitHub Actions workflow",
            "body": "Add test and lint jobs",
            "breaking": False,
        }
        result = parse_commit(commit)
        self.assertEqual(result["type"], "ci")
        self.assertEqual(result["description"], "add GitHub Actions workflow")


class TestGroupCommits(unittest.TestCase):
    """Test group_commits function."""
    
    def test_group_by_type(self):
        """Test grouping commits by type."""
        commits = [
            {
                "subject": "feat: add new feature",
                "body": "",
                "breaking": False,
            },
            {
                "subject": "fix: repair bug",
                "body": "",
                "breaking": False,
            },
            {
                "subject": "docs: update documentation",
                "body": "",
                "breaking": False,
            },
            {
                "subject": "feat(api): enhance endpoint",
                "body": "",
                "breaking": False,
            },
        ]
        
        parsed_commits = [parse_commit(c) for c in commits]
        groups, breaking = group_commits(parsed_commits)
        
        self.assertEqual(len(breaking), 0)
        self.assertIn("feat", groups)
        self.assertIn("fix", groups)
        self.assertIn("docs", groups)
        self.assertEqual(len(groups["feat"]), 2)
        self.assertEqual(len(groups["fix"]), 1)
        self.assertEqual(len(groups["docs"]), 1)
    
    def test_breaking_changes(self):
        """Test grouping with breaking changes."""
        commits = [
            {
                "subject": "feat!: breaking change",
                "body": "",
                "breaking": False,
            },
            {
                "subject": "fix: normal fix",
                "body": "BREAKING CHANGE: This changes everything",
                "breaking": False,
            },
            {
                "subject": "docs: update docs",
                "body": "",
                "breaking": False,
            },
        ]
        
        parsed_commits = [parse_commit(c) for c in commits]
        groups, breaking = group_commits(parsed_commits)
        
        self.assertEqual(len(breaking), 2)
        self.assertEqual(breaking[0]["description"], "breaking change")
        self.assertEqual(breaking[1]["description"], "normal fix")
    
    def test_other_category(self):
        """Test non-conventional commits go to 'other' category."""
        commits = [
            {
                "subject": "Random commit message",
                "body": "",
                "breaking": False,
            },
            {
                "subject": "Another non-standard commit",
                "body": "",
                "breaking": False,
            },
        ]
        
        parsed_commits = [parse_commit(c) for c in commits]
        groups, breaking = group_commits(parsed_commits)
        
        self.assertIn("other", groups)
        self.assertEqual(len(groups["other"]), 2)


class TestFormatMarkdown(unittest.TestCase):
    """Test format_markdown function."""
    
    def test_basic_formatting(self):
        """Test basic markdown formatting."""
        groups = {
            "feat": [
                {
                    "type": "feat",
                    "scope": None,
                    "description": "add new feature",
                    "short": "abc123",
                    "breaking": False,
                }
            ],
            "fix": [
                {
                    "type": "fix",
                    "scope": "api",
                    "description": "fix memory leak",
                    "short": "def456",
                    "breaking": False,
                }
            ],
        }
        breaking = []
        stats = {"total": 2, "authors": 1}
        
        result = format_markdown(groups, breaking, "Test Changelog", stats)
        
        # Check title
        self.assertIn("# Test Changelog", result)
        # Check stats
        self.assertIn("*2 commits by 1 contributors*", result)
        # Check feature section
        self.assertIn("## 🚀 Features", result)
        self.assertIn("- add new feature (abc123)", result)
        # Check fix section with scope
        self.assertIn("## 🐛 Bug Fixes", result)
        self.assertIn("- **api:** fix memory leak (def456)", result)
    
    def test_breaking_changes_section(self):
        """Test breaking changes section."""
        groups = {
            "feat": [
                {
                    "type": "feat",
                    "scope": "api",
                    "description": "change response format",
                    "short": "xyz789",
                    "breaking": True,
                }
            ],
        }
        breaking = [
            {
                "type": "feat",
                "scope": "api",
                "description": "change response format",
                "short": "xyz789",
                "breaking": True,
            }
        ]
        
        result = format_markdown(groups, breaking, "Test Changelog")
        
        # Check breaking changes section
        self.assertIn(f"## {BREAKING_EMOJI} Breaking Changes", result)
        self.assertIn("- **api:** change response format (xyz789)", result)
    
    def test_empty_groups_skipped(self):
        """Test that empty groups are skipped."""
        groups = {
            "feat": [
                {
                    "type": "feat",
                    "scope": None,
                    "description": "only feature",
                    "short": "abc123",
                    "breaking": False,
                }
            ],
            "fix": [],  # Empty group
        }
        breaking = []
        
        result = format_markdown(groups, breaking, "Test Changelog")
        
        self.assertIn("## 🚀 Features", result)
        self.assertNotIn("## 🐛 Bug Fixes", result)


class TestFormatJson(unittest.TestCase):
    """Test format_json function."""
    
    def test_basic_json(self):
        """Test basic JSON formatting."""
        groups = {
            "feat": [
                {
                    "type": "feat",
                    "scope": None,
                    "description": "add new feature",
                    "short": "abc123",
                    "author": "Test User",
                    "date": "2024-01-01T12:00:00Z",
                    "breaking": False,
                }
            ],
        }
        breaking = []
        stats = {"total": 1, "authors": 1}
        
        result = format_json(groups, breaking, stats)
        data = json.loads(result)
        
        self.assertEqual(data["stats"]["total"], 1)
        self.assertEqual(len(data["breaking_changes"]), 0)
        self.assertIn("🚀 Features", data["changes"])
        self.assertEqual(len(data["changes"]["🚀 Features"]), 1)
        self.assertEqual(data["changes"]["🚀 Features"][0]["description"], "add new feature")
    
    def test_json_with_breaking(self):
        """Test JSON with breaking changes."""
        groups = {
            "feat": [
                {
                    "type": "feat",
                    "scope": "api",
                    "description": "change API",
                    "short": "xyz789",
                    "author": "Test User",
                    "date": "2024-01-01T12:00:00Z",
                    "breaking": True,
                }
            ],
        }
        breaking = [
            {
                "type": "feat",
                "scope": "api",
                "description": "change API",
                "short": "xyz789",
                "author": "Test User",
                "date": "2024-01-01T12:00:00Z",
                "breaking": True,
            }
        ]
        
        result = format_json(groups, breaking)
        data = json.loads(result)
        
        self.assertEqual(len(data["breaking_changes"]), 1)
        self.assertEqual(data["breaking_changes"][0]["description"], "change API")
        self.assertEqual(data["breaking_changes"][0]["scope"], "api")


class TestGetStats(unittest.TestCase):
    """Test get_stats function."""
    
    def test_basic_stats(self):
        """Test basic statistics calculation."""
        commits = [
            {
                "subject": "feat: feature one",
                "author": "Alice",
                "type": "feat",
            },
            {
                "subject": "fix: fix one",
                "author": "Bob",
                "type": "fix",
            },
            {
                "subject": "feat: feature two",
                "author": "Alice",
                "type": "feat",
            },
        ]
        
        # Mock parse_commit to return type
        with patch('tools.changelog_gen.parse_commit') as mock_parse:
            mock_parse.side_effect = lambda c: {**c, "type": c.get("type", "other")}
            stats = get_stats(commits)
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["authors"], 2)
        self.assertIn("Alice", stats["author_names"])
        self.assertIn("Bob", stats["author_names"])
        self.assertEqual(stats["types"]["feat"], 2)
        self.assertEqual(stats["types"]["fix"], 1)


class TestGitFunctions(unittest.TestCase):
    """Test git-related functions with mocking."""
    
    @patch('tools.changelog_gen.subprocess.run')
    def test_run_git_success(self, mock_run):
        """Test run_git with successful execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "git output\n"
        mock_run.return_value = mock_result
        
        result = run_git(["status"])
        self.assertEqual(result, "git output")
    
    @patch('tools.changelog_gen.subprocess.run')
    def test_run_git_failure(self, mock_run):
        """Test run_git with failed execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        result = run_git(["invalid", "command"])
        self.assertEqual(result, "")
    
    @patch('tools.changelog_gen.run_git')
    def test_get_tags(self, mock_run_git):
        """Test get_tags function."""
        mock_run_git.return_value = "v2.0.0\nv1.1.0\nv1.0.0\n"
        tags = get_tags()
        self.assertEqual(tags, ["v2.0.0", "v1.1.0", "v1.0.0"])
    
    @patch('tools.changelog_gen.run_git')
    def test_get_commits(self, mock_run_git):
        """Test get_commits function."""
        mock_output = """abc123|abc123|feat: add feature|Alice|2024-01-01T12:00:00Z|Test body<<<END>>>
def456|def456|fix: repair bug|Bob|2024-01-02T12:00:00Z|<<<END>>>"""
        mock_run_git.return_value = mock_output
        
        commits = get_commits("v1.0.0", "HEAD")
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["hash"], "abc123")
        self.assertEqual(commits[0]["subject"], "feat: add feature")
        self.assertEqual(commits[0]["author"], "Alice")
        self.assertEqual(commits[1]["short"], "def456")
        self.assertEqual(commits[1]["subject"], "fix: repair bug")


class TestCmdChangelog(unittest.TestCase):
    """Test cmd_changelog function."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Initialize git repo
        os.system("git init > /dev/null 2>&1")
        os.system("git config user.email 'test@example.com'")
        os.system("git config user.name 'Test User'")
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('tools.changelog_gen.get_tags')
    @patch('tools.changelog_gen.get_commits')
    @patch('tools.changelog_gen.get_stats')
    @patch('tools.changelog_gen.group_commits')
    @patch('tools.changelog_gen.format_markdown')
    def test_default_command(self, mock_format, mock_group, mock_stats, mock_commits, mock_tags):
        """Test default changelog command."""
        mock_tags.return_value = ["v1.0.0"]
        mock_commits.return_value = [
            {
                "subject": "feat: test feature",
                "author": "Test",
                "date": "2024-01-01T12:00:00Z",
                "body": "",
                "breaking": False,
                "hash": "abc123",
                "short": "abc123",
            }
        ]
        mock_stats.return_value = {"total": 1, "authors": 1}
        mock_group.return_value = ({"feat": ["parsed"]}, [])
        mock_format.return_value = "# Test Changelog\n\n- test feature"