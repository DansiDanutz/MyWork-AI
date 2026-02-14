"""Tests for mw doctor command."""
import subprocess
import sys

def test_doctor_runs():
    """Doctor command should run without errors."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 or "warnings" in r.stdout.lower() or "passed" in r.stdout.lower()
    assert "Project Doctor" in r.stdout

def test_doctor_checks_todos():
    """Doctor should check for TODO markers."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    assert "TODO" in r.stdout or "todo" in r.stdout.lower()

def test_doctor_checks_git():
    """Doctor should check git status."""
    r = subprocess.run([sys.executable, "tools/mw.py", "doctor"], capture_output=True, text=True, timeout=30)
    assert any(x in r.stdout for x in ["working tree", "uncommitted", "git"])

def test_diagnose_alias():
    """Diagnose should be an alias for doctor."""
    r = subprocess.run([sys.executable, "tools/mw.py", "diagnose"], capture_output=True, text=True, timeout=30)
    assert "Project Doctor" in r.stdout
