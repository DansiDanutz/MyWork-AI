#!/usr/bin/env python3
"""Tests for mw config command."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MW = str(Path(__file__).parent.parent / "tools" / "mw.py")

def run(args, env=None):
    return subprocess.run(
        [sys.executable, MW] + args,
        capture_output=True, text=True, timeout=15, env=env
    )

def test_config_list():
    r = run(["config", "list"])
    assert r.returncode == 0
    assert "MyWork Configuration" in r.stdout
    assert "theme" in r.stdout

def test_config_list_default():
    r = run(["config"])
    assert r.returncode == 0
    assert "theme" in r.stdout

def test_config_get_default():
    r = run(["config", "get", "log_level"])
    assert r.returncode == 0
    assert "info" in r.stdout

def test_config_get_unknown():
    r = run(["config", "get", "nonexistent_key_xyz"])
    assert r.returncode == 1
    assert "Unknown" in r.stdout

def test_config_set_and_get():
    r = run(["config", "set", "theme", "test_value_123"])
    assert r.returncode == 0
    assert "test_value_123" in r.stdout
    r2 = run(["config", "get", "theme"])
    assert r2.returncode == 0
    assert "test_value_123" in r2.stdout

def test_config_set_bool():
    r = run(["config", "set", "telemetry", "true"])
    assert r.returncode == 0
    r2 = run(["config", "get", "telemetry"])
    assert "True" in r2.stdout
    # Reset
    run(["config", "set", "telemetry", "false"])

def test_config_set_int():
    r = run(["config", "set", "max_brain_entries", "500"])
    assert r.returncode == 0
    r2 = run(["config", "get", "max_brain_entries"])
    assert "500" in r2.stdout
    # Reset
    run(["config", "set", "max_brain_entries", "1000"])

def test_config_reset():
    run(["config", "set", "theme", "custom"])
    r = run(["config", "reset"])
    assert r.returncode == 0
    assert "reset to defaults" in r.stdout
    r2 = run(["config", "get", "theme"])
    assert "default" in r2.stdout

def test_config_rm():
    run(["config", "set", "custom_key", "val"])
    r = run(["config", "rm", "custom_key"])
    assert r.returncode == 0
    assert "Removed" in r.stdout

def test_config_rm_missing():
    r = run(["config", "rm", "nonexistent_xyz"])
    assert r.returncode == 1

def test_config_path():
    r = run(["config", "path"])
    assert r.returncode == 0
    assert "config.json" in r.stdout

def test_config_set_missing_args():
    r = run(["config", "set"])
    assert r.returncode == 1

def test_config_get_missing_args():
    r = run(["config", "get"])
    assert r.returncode == 1

def test_config_unknown_sub():
    r = run(["config", "bananas"])
    assert r.returncode == 1

def test_config_alias_cfg():
    r = run(["cfg"])
    assert r.returncode == 0
    assert "MyWork Configuration" in r.stdout

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
