#!/usr/bin/env python3
"""Tests for plugin_manager.py"""

import json
import os
import sys
import shutil
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.plugin_manager import (
    validate_plugin,
    create_plugin_scaffold,
    install_plugin,
    uninstall_plugin,
    list_plugins,
    load_registry,
    save_registry,
    _security_scan,
    main,
    PLUGIN_DIR,
)


@pytest.fixture
def tmp_plugin_dir(tmp_path, monkeypatch):
    """Override plugin directory to temp."""
    monkeypatch.setattr("tools.plugin_manager.PLUGIN_DIR", tmp_path / "plugins")
    monkeypatch.setattr("tools.plugin_manager.PLUGIN_REGISTRY", tmp_path / "plugins" / "registry.json")
    return tmp_path


@pytest.fixture
def sample_plugin(tmp_path):
    """Create a valid sample plugin."""
    plugin_dir = tmp_path / "test-plugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(json.dumps({
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "author": "Test",
        "entry": "main.py",
        "commands": ["test-cmd"],
    }))
    (plugin_dir / "main.py").write_text('print("hello")')
    return plugin_dir


def test_validate_plugin_valid(sample_plugin):
    result = validate_plugin(sample_plugin)
    assert result["valid"] is True
    assert result["name"] == "test-plugin"


def test_validate_plugin_missing_manifest(tmp_path):
    result = validate_plugin(tmp_path)
    assert result["valid"] is False
    assert "Missing plugin.json" in result["error"]


def test_validate_plugin_missing_fields(tmp_path):
    (tmp_path / "plugin.json").write_text('{"name": "x"}')
    result = validate_plugin(tmp_path)
    assert result["valid"] is False
    assert "Missing fields" in result["error"]


def test_validate_plugin_missing_entry(tmp_path):
    (tmp_path / "plugin.json").write_text(json.dumps({
        "name": "x", "version": "1.0", "description": "x", "author": "x"
    }))
    result = validate_plugin(tmp_path)
    assert result["valid"] is False
    assert "Entry point" in result["error"]


def test_security_scan_clean(sample_plugin):
    warnings = _security_scan(sample_plugin)
    assert len(warnings) == 0


def test_security_scan_suspicious(tmp_path):
    (tmp_path / "bad.py").write_text('eval("dangerous")')
    warnings = _security_scan(tmp_path)
    assert len(warnings) > 0
    assert "eval(" in warnings[0]


def test_create_plugin_scaffold(tmp_path):
    result = create_plugin_scaffold("my-plugin", str(tmp_path))
    assert result["success"] is True
    assert (tmp_path / "my-plugin" / "plugin.json").exists()
    assert (tmp_path / "my-plugin" / "main.py").exists()
    assert (tmp_path / "my-plugin" / "README.md").exists()


def test_create_plugin_scaffold_exists(tmp_path):
    (tmp_path / "my-plugin").mkdir()
    result = create_plugin_scaffold("my-plugin", str(tmp_path))
    assert result["success"] is False


def test_install_from_local(tmp_plugin_dir, sample_plugin):
    result = install_plugin(str(sample_plugin))
    assert result["success"] is True
    assert result["name"] == "test-plugin"


def test_install_duplicate_blocked(tmp_plugin_dir, sample_plugin):
    install_plugin(str(sample_plugin))
    result = install_plugin(str(sample_plugin))
    assert result["success"] is False
    assert "already installed" in result["error"]


def test_install_force_reinstall(tmp_plugin_dir, sample_plugin):
    install_plugin(str(sample_plugin))
    result = install_plugin(str(sample_plugin), force=True)
    assert result["success"] is True


def test_uninstall(tmp_plugin_dir, sample_plugin):
    install_plugin(str(sample_plugin))
    result = uninstall_plugin("test-plugin")
    assert result["success"] is True
    assert len(list_plugins()) == 0


def test_uninstall_not_found(tmp_plugin_dir):
    result = uninstall_plugin("nonexistent")
    assert result["success"] is False


def test_list_plugins_empty(tmp_plugin_dir):
    assert list_plugins() == []


def test_list_plugins_with_installed(tmp_plugin_dir, sample_plugin):
    install_plugin(str(sample_plugin))
    plugins = list_plugins()
    assert len(plugins) == 1
    assert plugins[0]["name"] == "test-plugin"


def test_registry_persistence(tmp_plugin_dir, sample_plugin):
    install_plugin(str(sample_plugin))
    reg = load_registry()
    assert "test-plugin" in reg["plugins"]


def test_cli_help(capsys):
    result = main(["--help"])
    assert result == 0


def test_cli_list_empty(tmp_plugin_dir, capsys):
    result = main(["list"])
    assert result == 0


def test_cli_create(tmp_path, capsys):
    os.chdir(tmp_path)
    result = main(["create", "demo"])
    assert result == 0
    assert (tmp_path / "demo" / "plugin.json").exists()


def test_cli_install_missing_source(capsys):
    result = main(["install"])
    assert result == 1


def test_cli_unknown_command(capsys):
    result = main(["foobar"])
    assert result == 1
