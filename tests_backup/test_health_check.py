"""
Tests for health_check.py
=========================
Tests for the Health Check functionality including utility functions,
HealthCheckLock, Status enum, and HealthChecker methods.
"""

import os
import sys
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestStatus:
    """Tests for the Status enum."""

    def test_status_values(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import Status

        assert Status.OK.value == "✅"
        assert Status.WARNING.value == "⚠️"
        assert Status.ERROR.value == "❌"
        assert Status.UNKNOWN.value == "❓"


class TestCheckFilePermissions:
    """Tests for the check_file_permissions utility."""

    def test_readable_file(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import check_file_permissions

        test_file = temp_mywork_root / "test.txt"
        test_file.write_text("hello")
        ok, msg = check_file_permissions(test_file)
        assert ok is True
        assert msg == ""

    def test_nonexistent_file_with_existing_parent(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import check_file_permissions

        missing = temp_mywork_root / "does_not_exist.txt"
        ok, msg = check_file_permissions(missing)
        assert ok is True

    def test_writable_directory(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import check_file_permissions

        ok, msg = check_file_permissions(temp_mywork_root, need_write=True)
        assert ok is True


class TestSafeSocketConnect:
    """Tests for safe_socket_connect."""

    def test_connection_to_closed_port(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import safe_socket_connect

        # Port 1 is almost certainly closed
        result = safe_socket_connect("127.0.0.1", 1, timeout=0.5)
        assert result is False

    def test_connection_to_invalid_host(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import safe_socket_connect

        result = safe_socket_connect("192.0.2.1", 80, timeout=0.5)
        assert result is False


class TestHealthCheckLock:
    """Tests for the HealthCheckLock context manager."""

    def test_lock_acquire_and_release(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import HealthCheckLock

        lock_file = temp_mywork_root / ".tmp" / "test.lock"
        with HealthCheckLock(lock_file, timeout=2):
            assert lock_file.exists()
        # Lock file cleaned up after exit
        assert not lock_file.exists()

    def test_lock_creates_parent_dirs(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import HealthCheckLock

        lock_file = temp_mywork_root / "nested" / "dir" / "test.lock"
        with HealthCheckLock(lock_file, timeout=2):
            assert lock_file.parent.exists()


class TestHealthChecker:
    """Tests for HealthChecker instantiation and basic methods."""

    def test_instantiation(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import HealthChecker

        checker = HealthChecker()
        assert checker is not None

    def test_has_run_methods(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import HealthChecker

        checker = HealthChecker()
        assert hasattr(checker, "run_quick") or hasattr(checker, "run_full")

    def test_quick_check_returns_results(self, temp_mywork_root):
        if "health_check" in sys.modules:
            del sys.modules["health_check"]
        from health_check import HealthChecker

        checker = HealthChecker()
        if hasattr(checker, "run_quick"):
            results = checker.run_quick()
            assert results is not None
