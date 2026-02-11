"""Tests for mw test and mw workflow commands."""
import os
import sys
import subprocess
import tempfile

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "tools")
MW = os.path.join(TOOLS_DIR, "mw.py")


def run_mw(*args, timeout=15, cwd=None):
    result = subprocess.run(
        [sys.executable, MW] + list(args),
        capture_output=True, text=True, timeout=timeout, cwd=cwd
    )
    return result


def test_test_help():
    r = run_mw("test", "--help")
    assert "Universal Test Runner" in r.stdout
    assert r.returncode == 0


def test_test_detects_python():
    """In a dir with setup.py, should detect Python."""
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "setup.py"), "w").write("# test")
        os.makedirs(os.path.join(d, "tests"))
        r = run_mw("test", cwd=d)
        assert "Detected: Python" in r.stdout


def test_test_detects_node():
    """In a dir with package.json, should detect Node."""
    with tempfile.TemporaryDirectory() as d:
        import json
        with open(os.path.join(d, "package.json"), "w") as f:
            json.dump({"name": "test", "scripts": {"test": "echo ok"}}, f)
        r = run_mw("test", cwd=d)
        assert "Detected: Node" in r.stdout


def test_test_no_project():
    """In empty dir, should fail gracefully."""
    with tempfile.TemporaryDirectory() as d:
        r = run_mw("test", cwd=d)
        assert "Could not detect" in r.stdout
        assert r.returncode == 1


def test_workflow_help():
    r = run_mw("workflow", "--help")
    assert "Multi-Step Workflows" in r.stdout
    assert r.returncode == 0


def test_workflow_no_args():
    r = run_mw("workflow")
    assert "Multi-Step Workflows" in r.stdout
