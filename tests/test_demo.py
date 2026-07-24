"""Tests for mw demo command."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_demo_help():
    """Demo --help should print usage."""
    r = subprocess.run(
        [sys.executable, "tools/demo.py", "--help"],
        capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL,
        cwd=ROOT
    )
    assert "demo" in r.stdout.lower() or "usage" in r.stdout.lower()

def test_demo_import():
    """Demo module should import cleanly."""
    sys.path.insert(0, str(ROOT))
    from tools.demo import demo_quick, demo_full, main
    assert callable(demo_quick)
    assert callable(demo_full)
    assert callable(main)

def test_mw_demo_registered():
    """mw demo should be a recognized command."""
    r = subprocess.run(
        [sys.executable, "tools/mw.py", "--help"],
        capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL,
        cwd=ROOT
    )
    assert "demo" in r.stdout
