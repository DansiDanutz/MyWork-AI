#!/usr/bin/env python3
"""
Test suite for the MyWork agent engine (tools/agent.py).
Covers agent configuration, validation, tool execution, and CLI commands.
"""

import pytest
import tempfile
import subprocess
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

# Import agent module
import sys
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
try:
    import agent as agent_module
except ImportError:
    pytest.skip("agent.py not importable", allow_module_level=True)


class TestAgentConfig:
    """Test agent configuration loading and validation."""
    
    def test_load_basic_agent(self, tmp_path):
        """Test loading a basic agent configuration."""
        config_path = tmp_path / "basic_agent.yaml"
        config_path.write_text("""
name: Test Agent
model: gpt-4.1-mini
description: A test agent
instructions: You are a test agent.
temperature: 0.5
max_tokens: 1000
""")
        
        config = agent_module.load_agent_config(config_path)
        assert config['name'] == "Test Agent"
        assert config['model'] == "gpt-4.1-mini"
        assert config['temperature'] == 0.5
        assert config['max_tokens'] == 1000
    
    def test_load_markdown_agent(self, tmp_path):
        """Test loading agent from markdown file with YAML frontmatter."""
        config_path = tmp_path / "agent.md"
        config_path.write_text("""---
name: Markdown Agent
model: claude-sonnet-4-20250514
description: A detailed agent
temperature: 0.7
max_tokens: 2048
---
# Instructions

You are a markdown-based agent configuration.
This should be treated as your instructions.
""")
        
        config = agent_module.load_agent_config(config_path)
        assert config['name'] == "Markdown Agent"
        assert "markdown-based agent" in config['instructions']
    
    def test_load_simple_markdown(self, tmp_path):
        """Test loading simple markdown without frontmatter."""
        config_path = tmp_path / "simple.md"
        config_path.write_text("""# Simple Agent

Just basic markdown content.
""")
        
        config = agent_module.load_agent_config(config_path)
        assert config['name'] == "simple"
        assert "Just basic markdown" in config['instructions']


class TestAgentValidation:
    """Test agent configuration validation."""
    
    def test_validate_complete_agent(self):
        """Test validation of complete agent configuration."""
        config = {
            'name': 'Valid Agent',
            'model': 'gpt-4.1-mini',
            'instructions': 'You are a valid agent.',
            'tools': [
                {
                    'name': 'search',
                    'description': 'Search the web',
                    'command': 'curl https://api.com?q={query}'
                }
            ]
        }
        issues = agent_module.validate_agent_config(config)
        assert len(issues) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validation catches missing required fields."""
        config = {}
        issues = agent_module.validate_agent_config(config)
        assert "Missing 'name'" in issues
        assert "Missing 'model'" in issues
        assert "Missing 'instructions'" in issues


class TestToolExecution:
    """Test agent tool execution functionality."""
    
    def test_format_command(self):
        """Test formatting commands with variable substitution."""
        template = "cat {path}"
        arguments = {'path': '/tmp/test.txt'}
        cmd = agent_module._format_command(template, arguments)
        assert cmd == "cat /tmp/test.txt"
    
    def test_command_substitution(self):
        """Test variable substitution in commands."""
        template = "curl -s 'https://api.com?q={query}&limit={limit}'"
        args = {'query': 'test search', 'limit': 10}
        result = agent_module._format_command(template, args)
        assert "test search" in result
        assert "limit=10" in result


class TestEnvironmentVariableResolution:
    """Test resolution of environment variables in configurations."""
    
    def test_resolve_simple_env_var(self):
        """Test resolving simple environment variables."""
        with patch.dict('os.environ', {'API_KEY': 'test123'}):
            result = agent_module._resolve_env_vars('token=${API_KEY}')
            assert result == 'token=test123'


def test_cli_help_output():
    """Test that CLI help is accessible."""
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            f'import sys; sys.path.insert(0, {str(TOOLS)!r}); import agent; agent.cmd_agent(["--help"])'
        ], capture_output=True, text=True, timeout=10)
        
        # Help should either succeed or show usage
        assert result.returncode == 0
    except subprocess.TimeoutExpired:
        pytest.fail("CLI help took too long")


def test_module_imports():
    """Test that all required functions and classes are available."""
    assert hasattr(agent_module, 'load_agent_config')
    assert hasattr(agent_module, 'validate_agent_config')
    assert hasattr(agent_module, '_resolve_env_vars')
    assert hasattr(agent_module, '_format_command')


class TestIntegration:
    """Integration tests for the agent engine."""
    
    def test_full_agent_lifecycle(self, tmp_path):
        """Test complete agent lifecycle: config → validation → action."""
        config_path = tmp_path / "test_agent.yaml"
        config_path.write_text("""
name: Integration Test Agent
model: gpt-4.1-mini
description: For integration testing
instructions: "You are a test agent for integration testing."
temperature: 0.1
max_tokens: 100
tools: []
""")
        
        # Load config
        config = agent_module.load_agent_config(config_path)
        
        # Validate
        issues = agent_module.validate_agent_config(config)
        assert len(issues) == 0
        
        # Check basic structure
        assert config['name'] == "Integration Test Agent"
        assert config['temperature'] == 0.1
        assert config['tools'] == []


# Quick sanity test for pytest discovery
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
