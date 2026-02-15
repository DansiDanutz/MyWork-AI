#!/usr/bin/env python3
"""
Unit tests for n8n commands and API functions.
Tests n8n integration, workflow validation, configuration, and error handling.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, Mock
from urllib.error import URLError, HTTPError
import sys

# Add the tools directory to the Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# Import the functions we want to test
try:
    # Import from mw.py
    from mw import _n8n_test, _n8n_get_config, _n8n_status, _n8n_import
    
    # Import from n8n_api.py  
    from n8n_api import health_check, get_headers, _is_placeholder, _load_from_mcp
    N8N_API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import n8n functions: {e}")
    N8N_API_AVAILABLE = False


class TestN8nFunctions(unittest.TestCase):
    """Test n8n command functions from mw.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Sample valid workflow data for testing
        self.valid_workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [100, 200],
                    "parameters": {}
                },
                {
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [300, 200],
                    "parameters": {"url": "https://api.example.com"}
                }
            ],
            "connections": {
                "Start": {
                    "main": [[{"node": "HTTP Request", "type": "main", "index": 0}]]
                }
            },
            "settings": {}
        }
        
        # Invalid workflow with missing required fields
        self.invalid_workflow_missing_nodes = {
            "name": "Invalid Workflow",
            "connections": {}
        }
        
        # Invalid workflow with duplicate node names
        self.invalid_workflow_duplicate_names = {
            "name": "Duplicate Names",
            "nodes": [
                {"name": "Node1", "type": "start", "position": [0, 0]},
                {"name": "Node1", "type": "http", "position": [100, 0]}  # Duplicate name
            ],
            "connections": {}
        }

    @patch('builtins.print')
    def test_n8n_test_valid_workflow(self, mock_print):
        """Test _n8n_test with a valid workflow JSON file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_workflow, f)
            temp_file = f.name
        
        try:
            result = _n8n_test(temp_file)
            self.assertEqual(result, 0)  # Should return 0 for valid workflow
            
            # Check that success message was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("✅ Workflow is valid!" in call for call in print_calls))
        finally:
            Path(temp_file).unlink()

    @patch('builtins.print')
    def test_n8n_test_file_not_found(self, mock_print):
        """Test _n8n_test with non-existent file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        result = _n8n_test("nonexistent_file.json")
        self.assertEqual(result, 1)  # Should return 1 for error
        
        # Check error message was printed
        mock_print.assert_called_with("❌ File not found: nonexistent_file.json")

    @patch('builtins.print')
    def test_n8n_test_invalid_json(self, mock_print):
        """Test _n8n_test with invalid JSON file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_file = f.name
        
        try:
            result = _n8n_test(temp_file)
            self.assertEqual(result, 1)  # Should return 1 for error
            
            # Check that JSON error was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("❌ Invalid JSON:" in call for call in print_calls))
        finally:
            Path(temp_file).unlink()

    @patch('builtins.print')
    def test_n8n_test_missing_nodes(self, mock_print):
        """Test _n8n_test with workflow missing required nodes"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_workflow_missing_nodes, f)
            temp_file = f.name
        
        try:
            result = _n8n_test(temp_file)
            self.assertEqual(result, 1)  # Should return 1 for errors
            
            # Check that error was reported
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("Missing 'nodes' array" in call for call in print_calls))
        finally:
            Path(temp_file).unlink()

    @patch('builtins.print')
    def test_n8n_test_duplicate_node_names(self, mock_print):
        """Test _n8n_test with duplicate node names"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_workflow_duplicate_names, f)
            temp_file = f.name
        
        try:
            result = _n8n_test(temp_file)
            self.assertEqual(result, 1)  # Should return 1 for errors
            
            # Check that duplicate name error was reported
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("duplicate name 'Node1'" in call for call in print_calls))
        finally:
            Path(temp_file).unlink()

    @patch.dict(os.environ, {'N8N_API_URL': 'https://test.n8n.cloud', 'N8N_API_KEY': 'test-key'})
    def test_n8n_get_config_from_env(self):
        """Test _n8n_get_config reading from environment variables"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        url, key = _n8n_get_config()
        self.assertEqual(url, 'https://test.n8n.cloud')
        self.assertEqual(key, 'test-key')

    @patch.dict(os.environ, {}, clear=True)
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_n8n_get_config_from_env_file(self, mock_read_text, mock_exists):
        """Test _n8n_get_config reading from .env file when env vars not set"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_exists.return_value = True
        mock_read_text.return_value = """
N8N_API_URL=https://env.file.n8n.cloud
N8N_API_KEY=env-file-key
OTHER_VAR=some-value
"""
        
        url, key = _n8n_get_config()
        self.assertEqual(url, 'https://env.file.n8n.cloud')
        self.assertEqual(key, 'env-file-key')

    @patch.dict(os.environ, {}, clear=True)
    @patch('pathlib.Path.exists')
    def test_n8n_get_config_no_config(self, mock_exists):
        """Test _n8n_get_config when no configuration is available"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_exists.return_value = False
        
        url, key = _n8n_get_config()
        self.assertEqual(url, '')
        self.assertEqual(key, '')

    @patch('urllib.request.urlopen')
    @patch('mw._n8n_get_config')
    @patch('builtins.print')
    def test_n8n_status_success(self, mock_print, mock_config, mock_urlopen):
        """Test _n8n_status with successful connection"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_config.return_value = ('https://test.n8n.cloud', 'test-key')
        
        # Mock successful API responses
        mock_response1 = MagicMock()
        mock_response1.read.return_value = json.dumps({"data": []}).encode()
        mock_response1.__enter__ = MagicMock(return_value=mock_response1)
        mock_response1.__exit__ = MagicMock(return_value=False)
        
        mock_response2 = MagicMock()
        mock_response2.read.return_value = json.dumps({
            "data": [
                {"id": "1", "name": "Workflow 1", "active": True},
                {"id": "2", "name": "Workflow 2", "active": False}
            ]
        }).encode()
        mock_response2.__enter__ = MagicMock(return_value=mock_response2)
        mock_response2.__exit__ = MagicMock(return_value=False)
        
        mock_urlopen.side_effect = [mock_response1, mock_response2]
        
        result = _n8n_status()
        self.assertEqual(result, 0)  # Should return 0 for success
        
        # Check success messages were printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any("✅ n8n is running!" in call for call in print_calls))
        self.assertTrue(any("Workflows: 2 total, 1 active" in call for call in print_calls))

    @patch('mw._n8n_get_config')
    @patch('builtins.print')
    def test_n8n_status_no_config(self, mock_print, mock_config):
        """Test _n8n_status when n8n is not configured"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_config.return_value = ('', '')  # No config
        
        result = _n8n_status()
        self.assertEqual(result, 1)  # Should return 1 for error
        
        mock_print.assert_any_call("❌ n8n not configured")

    @patch('urllib.request.urlopen')
    @patch('mw._n8n_get_config')
    @patch('builtins.print')
    def test_n8n_status_connection_error(self, mock_print, mock_config, mock_urlopen):
        """Test _n8n_status with connection error"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_config.return_value = ('https://unreachable.n8n.cloud', 'test-key')
        mock_urlopen.side_effect = URLError("Connection refused")
        
        result = _n8n_status()
        self.assertEqual(result, 1)  # Should return 1 for error
        
        # Check error message was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any("❌ Cannot reach n8n at" in call for call in print_calls))

    @patch('builtins.print')
    def test_n8n_import_file_not_found(self, mock_print):
        """Test _n8n_import with non-existent file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        result = _n8n_import("nonexistent_file.json")
        self.assertEqual(result, 1)  # Should return 1 for error
        
        mock_print.assert_called_with("❌ File not found: nonexistent_file.json")

    @patch('builtins.print')  
    def test_n8n_import_invalid_json(self, mock_print):
        """Test _n8n_import with invalid JSON file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_file = f.name
        
        try:
            result = _n8n_import(temp_file)
            self.assertEqual(result, 1)  # Should return 1 for error
            
            # Check that JSON error was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("❌ Invalid JSON:" in call for call in print_calls))
        finally:
            Path(temp_file).unlink()

    @patch('mw._n8n_api_call')
    @patch('builtins.print')
    def test_n8n_import_success(self, mock_print, mock_api_call):
        """Test _n8n_import with valid workflow file"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_api_call.return_value = 0  # Successful API call
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_workflow, f)
            temp_file = f.name
        
        try:
            result = _n8n_import(temp_file)
            self.assertEqual(result, 0)  # Should return 0 for success
            
            # Check that import message was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("📦 Importing workflow: Test Workflow" in call for call in print_calls))
            
            # Check API was called with correct parameters
            mock_api_call.assert_called_once_with(
                "POST", "/api/v1/workflows", body=self.valid_workflow, display=None
            )
        finally:
            Path(temp_file).unlink()


class TestN8nApiHelpers(unittest.TestCase):
    """Test helper functions from n8n_api.py"""

    def test_is_placeholder_empty_string(self):
        """Test _is_placeholder with empty string"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        self.assertTrue(_is_placeholder(""))

    def test_is_placeholder_none(self):
        """Test _is_placeholder with None (converted to empty string)"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        self.assertTrue(_is_placeholder(""))

    def test_is_placeholder_with_placeholder_text(self):
        """Test _is_placeholder with placeholder text"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        self.assertTrue(_is_placeholder("https://your-instance.app.n8n.cloud"))
        self.assertTrue(_is_placeholder("your-n8n-api-key-here"))
        self.assertTrue(_is_placeholder("Your-Instance-URL"))

    def test_is_placeholder_with_real_values(self):
        """Test _is_placeholder with real configuration values"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        self.assertFalse(_is_placeholder("https://mycompany.app.n8n.cloud"))
        self.assertFalse(_is_placeholder("n8n_api_1234567890abcdef"))

    @patch('pathlib.Path.exists')
    def test_load_from_mcp_file_not_exists(self, mock_exists):
        """Test _load_from_mcp when .mcp.json doesn't exist"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_exists.return_value = False
        
        url, key = _load_from_mcp()
        self.assertEqual(url, "")
        self.assertEqual(key, "")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_from_mcp_invalid_json(self, mock_read_text, mock_exists):
        """Test _load_from_mcp with invalid JSON"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_exists.return_value = True
        mock_read_text.return_value = "invalid json {"
        
        url, key = _load_from_mcp()
        self.assertEqual(url, "")
        self.assertEqual(key, "")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_from_mcp_success(self, mock_read_text, mock_exists):
        """Test _load_from_mcp with valid MCP configuration"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
            
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            "mcpServers": {
                "n8n-mcp": {
                    "env": {
                        "N8N_API_URL": "https://mcp.n8n.cloud",
                        "N8N_API_KEY": "mcp-api-key"
                    }
                }
            }
        })
        
        url, key = _load_from_mcp()
        self.assertEqual(url, "https://mcp.n8n.cloud")
        self.assertEqual(key, "mcp-api-key")

    def test_get_headers(self):
        """Test get_headers returns correct headers"""
        if not N8N_API_AVAILABLE:
            self.skipTest("n8n functions not available")
        
        import n8n_api as n8n_mod
        original = n8n_mod.N8N_API_KEY
        n8n_mod.N8N_API_KEY = "test-api-key"
        try:
            headers = get_headers()
            expected = {
                "X-N8N-API-KEY": "test-api-key", 
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        finally:
            n8n_mod.N8N_API_KEY = original
        self.assertEqual(headers, expected)


if __name__ == '__main__':
    # Set up test environment
    os.environ.setdefault('N8N_API_URL', 'https://test.n8n.cloud')
    os.environ.setdefault('N8N_API_KEY', 'test-key')
    
    # Run the tests
    unittest.main(verbosity=2)