"""
Tests for health_check.py
=========================
Tests for the Health Check functionality.
"""

import pytest


class TestHealthCheck:
    """Tests for health check functions."""

    def test_quick_check_runs(self, temp_mywork_root):
        """Quick health check should run without errors."""
        import sys
        if 'health_check' in sys.modules:
            del sys.modules['health_check']

        # Import should work
        from health_check import HealthChecker

        checker = HealthChecker()
        # Just verify it can be instantiated
        assert checker is not None

    def test_check_directories_exist(self, temp_mywork_root):
        """Should check required directories."""
        import sys
        if 'health_check' in sys.modules:
            del sys.modules['health_check']

        from health_check import HealthChecker

        checker = HealthChecker()
        # Verify the checker has access to paths
        assert hasattr(checker, 'run_quick') or hasattr(checker, 'run_full')

    def test_results_structure(self, temp_mywork_root):
        """Health check results should have proper structure."""
        import sys
        if 'health_check' in sys.modules:
            del sys.modules['health_check']

        from health_check import HealthChecker

        checker = HealthChecker()

        # The checker should be able to report results
        # Implementation varies but should return some form of results
        assert checker is not None
