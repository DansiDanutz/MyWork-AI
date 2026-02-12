"""Tests for the interactive tour command."""
import subprocess
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent


def test_tour_quick_runs():
    """Tour runs in quick mode without errors."""
    result = subprocess.run(
        [sys.executable, str(FRAMEWORK_ROOT / "tools" / "tour.py"), "--quick"],
        capture_output=True, text=True, timeout=30, cwd=str(FRAMEWORK_ROOT)
    )
    assert result.returncode == 0
    assert "Welcome to the MyWork-AI Tour" in result.stdout
    assert "Tour complete" in result.stdout


def test_tour_no_color():
    """Tour respects --no-color flag."""
    result = subprocess.run(
        [sys.executable, str(FRAMEWORK_ROOT / "tools" / "tour.py"), "--quick", "--no-color"],
        capture_output=True, text=True, timeout=30, cwd=str(FRAMEWORK_ROOT)
    )
    assert result.returncode == 0
    assert "\033[" not in result.stdout  # No ANSI codes


def test_tour_shows_all_steps():
    """Tour shows all 6 steps."""
    result = subprocess.run(
        [sys.executable, str(FRAMEWORK_ROOT / "tools" / "tour.py"), "--quick"],
        capture_output=True, text=True, timeout=30, cwd=str(FRAMEWORK_ROOT)
    )
    for i in range(1, 7):
        assert f"Step {i}/6" in result.stdout


def test_tour_via_mw():
    """Tour works via mw CLI."""
    result = subprocess.run(
        [sys.executable, str(FRAMEWORK_ROOT / "tools" / "mw.py"), "tour", "--quick"],
        capture_output=True, text=True, timeout=30, cwd=str(FRAMEWORK_ROOT)
    )
    assert result.returncode == 0
    assert "Welcome to the MyWork-AI Tour" in result.stdout


def test_tour_import():
    """Tour module imports cleanly."""
    sys.path.insert(0, str(FRAMEWORK_ROOT))
    from tools.tour import cmd_tour, banner, step
    assert callable(cmd_tour)
    assert callable(banner)
    assert callable(step)
