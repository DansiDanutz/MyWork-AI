"""Tests for mw doctor command."""
import subprocess
import sys
import pytest

@pytest.mark.timeout(60)
def test_doctor_runs():
    """Doctor command should run and produce diagnostics output."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    # Doctor may return non-zero if it finds issues, but should produce output
    assert "Doctor" in r.stdout or "DIAGNOSTIC" in r.stdout or "HEALTH" in r.stdout

@pytest.mark.timeout(60)
def test_doctor_checks_todos():
    """Doctor should check for TODO markers."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    assert "TODO" in r.stdout or "todo" in r.stdout.lower()

@pytest.mark.timeout(60)
def test_doctor_checks_git():
    """Doctor should check git health."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    assert any(x in r.stdout.upper() for x in ["GIT", "COMMIT", "BRANCH"])

@pytest.mark.timeout(60)
def test_doctor_alias():
    """Diagnose should be an alias for doctor."""
    r = subprocess.run([sys.executable, "tools/mw.py", "diagnose"], capture_output=True, text=True, timeout=30)
    assert "Doctor" in r.stdout or "DIAGNOSTIC" in r.stdout or "HEALTH" in r.stdout
