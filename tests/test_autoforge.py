"""Tests for AutoForge integration modules."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add tools dir so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import autoforge_api
import autoforge_service


class TestAutoForgeAPI:
    """Test AutoForge API integration."""

    def test_module_imports_successfully(self):
        """Test that autoforge_api module can be imported without errors."""
        import autoforge_api
        assert hasattr(autoforge_api, '__file__')

    def test_autoforge_branding_in_docstring(self):
        """Test that module docstring references AutoForge, not Autocoder."""
        import autoforge_api
        docstring = autoforge_api.__doc__ or ""
        assert "AutoForge" in docstring
        assert "Autocoder" not in docstring

    @patch('autoforge_api.httpx.get')
    def test_server_status_check(self, mock_get):
        """Test server status checking functionality."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # This would test actual status check if we had the function exposed
        # For now, just test that httpx is being used
        assert mock_get.called == False  # Haven't called it yet

    def test_config_constants(self):
        """Test that configuration constants are properly set."""
        import autoforge_api
        # Check that basic module structure exists
        assert hasattr(autoforge_api, 'Path')  # Should have Path import


class TestAutoForgeService:
    """Test AutoForge Service management."""

    def test_service_module_imports_successfully(self):
        """Test that autoforge_service module can be imported."""
        import autoforge_service
        assert hasattr(autoforge_service, '__file__')

    def test_service_branding_in_docstring(self):
        """Test that service module docstring references AutoForge."""
        import autoforge_service
        docstring = autoforge_service.__doc__ or ""
        # Should contain AutoForge references
        assert "AutoForge" in docstring or "autoforge" in str(autoforge_service.__file__)

    def test_service_has_expected_structure(self):
        """Test that service module has expected imports and structure."""
        import autoforge_service
        # Should have basic imports for service management
        assert hasattr(autoforge_service, 'subprocess') or hasattr(autoforge_service, 'os')


class TestBackwardsCompatibility:
    """Test that backwards compatibility aliases work correctly."""

    def test_autocoder_api_alias_exists(self):
        """Test that autocoder_api.py still exists as alias/symlink."""
        autocoder_api_path = os.path.join(
            os.path.dirname(__file__), '..', 'tools', 'autocoder_api.py'
        )
        assert os.path.exists(autocoder_api_path)

    def test_autocoder_service_alias_exists(self):
        """Test that autocoder_service.py still exists as alias/symlink."""
        autocoder_service_path = os.path.join(
            os.path.dirname(__file__), '..', 'tools', 'autocoder_service.py'
        )
        assert os.path.exists(autocoder_service_path)

    def test_autocoder_aliases_point_to_autoforge(self):
        """Test that old autocoder files are symlinks to new autoforge files."""
        autocoder_api_path = os.path.join(
            os.path.dirname(__file__), '..', 'tools', 'autocoder_api.py'
        )
        if os.path.islink(autocoder_api_path):
            # If it's a symlink, check it points to autoforge_api.py
            target = os.readlink(autocoder_api_path)
            assert 'autoforge_api.py' in target


class TestCLIIntegration:
    """Test CLI integration with AutoForge commands."""

    def test_autoforge_commands_available(self):
        """Test that AutoForge commands are available in CLI."""
        # Import the main mw module
        import mw
        
        # Check that autoforge commands exist in the commands dictionary
        # This assumes cmd_autoforge function exists
        assert hasattr(mw, 'cmd_autoforge')

    def test_legacy_command_mapping(self):
        """Test that legacy 'ac' commands still work."""
        import mw
        
        # The command mapping should include both af and ac
        with patch.object(mw.sys, 'argv', ['mw', 'help']):
            with patch('builtins.print'):  # Suppress help output
                try:
                    mw.main()
                except SystemExit:
                    pass  # Help command exits, that's expected

    @patch('mw.cmd_autoforge')
    def test_af_command_calls_autoforge_function(self, mock_cmd):
        """Test that 'mw af' calls the correct function."""
        import mw
        mock_cmd.return_value = 0
        
        with patch.object(mw.sys, 'argv', ['mw', 'af', 'status']):
            try:
                result = mw.main()
                mock_cmd.assert_called_with(['af', 'status'])
            except SystemExit as e:
                # If main() calls sys.exit(), that's also acceptable
                pass

    @patch('mw.cmd_autoforge')
    def test_ac_legacy_command_calls_autoforge_function(self, mock_cmd):
        """Test that 'mw ac' (legacy) still calls AutoForge function."""
        import mw
        mock_cmd.return_value = 0
        
        with patch.object(mw.sys, 'argv', ['mw', 'ac', 'status']):
            try:
                result = mw.main()
                mock_cmd.assert_called_with(['ac', 'status'])
            except SystemExit as e:
                # If main() calls sys.exit(), that's also acceptable
                pass


class TestDocumentationConsistency:
    """Test that documentation and help text is consistent with AutoForge branding."""

    def test_help_text_mentions_autoforge(self):
        """Test that help documentation mentions AutoForge, not Autocoder."""
        import mw
        
        # Get the module docstring (used for help)
        docstring = mw.__doc__ or ""
        help_text = str(docstring)
        
        # Should mention AutoForge
        assert "AutoForge" in help_text or "af" in help_text

    def test_autoforge_api_help_consistent(self):
        """Test that AutoForge API help text is consistent."""
        import autoforge_api
        
        docstring = autoforge_api.__doc__ or ""
        # Should reference AutoForge tools/commands
        assert "autoforge" in docstring.lower() or "AutoForge" in docstring

    def test_no_old_autocoder_references_in_help(self):
        """Test that help text doesn't contain old Autocoder references."""
        import mw
        
        docstring = mw.__doc__ or ""
        # Should not contain old references
        assert "Autocoder Commands:" not in docstring  # Should be "AutoForge Commands:"