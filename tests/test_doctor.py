"""Tests for mw doctor command.

NOTE: The doctor command performs network calls (API connectivity, pip checks, etc.)
which can hang in CI environments. These tests are marked as 'slow' and skipped in CI.
"""
import subprocess
import sys
import os
import pytest

# Skip all tests in this module when running in CI (no network access / hangs)
pytestmark = pytest.mark.skipif(
    os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true",
    reason="Doctor tests require network access and may hang in CI"
)


@pytest.mark.timeout(30)
def test_doctor_help():
    """Doctor --help should return quickly without hanging."""
    r = subprocess.run(
        [sys.executable, "tools/mw.py", "doctor", "--help"],
        capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0
    assert "Doctor" in r.stdout or "Diagnostics" in r.stdout


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_doctor_runs():
    """Doctor command should run and produce diagnostics output."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=45, stdin=subprocess.DEVNULL)
    assert "Doctor" in r.stdout or "DIAGNOSTIC" in r.stdout or "HEALTH" in r.stdout

@pytest.mark.slow
@pytest.mark.timeout(60)
def test_doctor_checks_todos():
    """Doctor should check for TODO markers."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=45, stdin=subprocess.DEVNULL)
    assert "TODO" in r.stdout or "todo" in r.stdout.lower()

@pytest.mark.slow
@pytest.mark.timeout(60)
def test_doctor_checks_git():
    """Doctor should check git health."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=45, stdin=subprocess.DEVNULL)
    assert any(x in r.stdout.upper() for x in ["GIT", "COMMIT", "BRANCH"])

@pytest.mark.slow
@pytest.mark.timeout(60)
def test_doctor_alias():
    """Diagnose should be an alias for doctor."""
    r = subprocess.run([sys.executable, "tools/mw.py", "diagnose"], capture_output=True, text=True, timeout=45, stdin=subprocess.DEVNULL)
    assert "Doctor" in r.stdout or "DIAGNOSTIC" in r.stdout or "HEALTH" in r.stdout
