"""Tests for the MyWork plugin manager."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.plugin_manager import (
    cmd_plugin,
    create_plugin_scaffold,
    disable_plugin,
    enable_plugin,
    get_plugin_commands,
    install_plugin,
    list_plugins,
    load_plugin_manifest,
    uninstall_plugin,
)


@pytest.fixture
def tmp_plugins(tmp_path, monkeypatch):
    """Use a temporary plugins directory."""
    monkeypatch.setattr("tools.plugin_manager.PLUGINS_DIR", tmp_path / "plugins")
    return tmp_path / "plugins"


@pytest.fixture
def sample_plugin(tmp_path):
    """Create a sample plugin directory."""
    plugin_dir = tmp_path / "sample-plugin"
    plugin_dir.mkdir()
    manifest = {
        "name": "sample-plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "commands": {
            "greet": {"run": "greet.py", "description": "Say hello"}
        }
    }
    with open(plugin_dir / "plugin.json", "w") as f:
        json.dump(manifest, f)
    with open(plugin_dir / "greet.py", "w") as f:
        f.write('print("Hello from sample!")\n')
    return plugin_dir


def test_list_plugins_empty(tmp_plugins):
    """Empty plugins dir returns empty list."""
    assert list_plugins() == []


def test_load_manifest_missing():
    """Loading from nonexistent dir returns None."""
    assert load_plugin_manifest(Path("/nonexistent")) is None


def test_load_manifest_valid(sample_plugin):
    """Loading a valid manifest works."""
    manifest = load_plugin_manifest(sample_plugin)
    assert manifest is not None
    assert manifest["name"] == "sample-plugin"
    assert manifest["version"] == "1.0.0"


def test_install_from_local(tmp_plugins, sample_plugin):
    """Install plugin from local path."""
    result = install_plugin(str(sample_plugin))
    assert result["ok"] is True
    assert result["name"] == "sample-plugin"
    assert (tmp_plugins / "sample-plugin" / "plugin.json").exists()


def test_install_duplicate(tmp_plugins, sample_plugin):
    """Installing same plugin twice fails."""
    install_plugin(str(sample_plugin))
    result = install_plugin(str(sample_plugin))
    assert result["ok"] is False
    assert "already installed" in result["error"]


def test_uninstall(tmp_plugins, sample_plugin):
    """Uninstalling removes the plugin."""
    install_plugin(str(sample_plugin))
    result = uninstall_plugin("sample-plugin")
    assert result["ok"] is True
    assert not (tmp_plugins / "sample-plugin").exists()


def test_uninstall_missing(tmp_plugins):
    """Uninstalling nonexistent plugin fails."""
    result = uninstall_plugin("nope")
    assert result["ok"] is False


def test_enable_disable(tmp_plugins, sample_plugin):
    """Enable/disable toggle works."""
    install_plugin(str(sample_plugin))
    result = disable_plugin("sample-plugin")
    assert result["ok"] is True
    assert (tmp_plugins / "sample-plugin" / ".disabled").exists()

    result = enable_plugin("sample-plugin")
    assert result["ok"] is True
    assert not (tmp_plugins / "sample-plugin" / ".disabled").exists()


def test_list_plugins_with_installed(tmp_plugins, sample_plugin):
    """List shows installed plugins."""
    install_plugin(str(sample_plugin))
    plugins = list_plugins()
    assert len(plugins) == 1
    assert plugins[0]["name"] == "sample-plugin"
    assert plugins[0]["_enabled"] is True


def test_list_plugins_disabled(tmp_plugins, sample_plugin):
    """Disabled plugins show in list."""
    install_plugin(str(sample_plugin))
    disable_plugin("sample-plugin")
    plugins = list_plugins()
    assert len(plugins) == 1
    assert plugins[0]["_enabled"] is False


def test_get_plugin_commands(tmp_plugins, sample_plugin):
    """Get commands from enabled plugins."""
    install_plugin(str(sample_plugin))
    cmds = get_plugin_commands()
    assert "sample-plugin:greet" in cmds


def test_get_plugin_commands_disabled(tmp_plugins, sample_plugin):
    """Disabled plugins don't expose commands."""
    install_plugin(str(sample_plugin))
    disable_plugin("sample-plugin")
    cmds = get_plugin_commands()
    assert len(cmds) == 0


def test_create_scaffold(tmp_path):
    """Create plugin scaffold generates correct files."""
    result = create_plugin_scaffold("my-plugin", str(tmp_path))
    assert result["ok"] is True
    plugin_dir = tmp_path / "my-plugin"
    assert (plugin_dir / "plugin.json").exists()
    assert (plugin_dir / "hello.py").exists()
    assert (plugin_dir / "README.md").exists()
    manifest = json.loads((plugin_dir / "plugin.json").read_text())
    assert manifest["name"] == "my-plugin"


def test_create_scaffold_exists(tmp_path):
    """Can't scaffold over existing dir."""
    (tmp_path / "existing").mkdir()
    result = create_plugin_scaffold("existing", str(tmp_path))
    assert result["ok"] is False


def test_install_invalid_path(tmp_plugins):
    """Install from nonexistent local path gives error."""
    result = install_plugin("/nonexistent/path/to/plugin")
    assert result["ok"] is False


def test_cmd_plugin_list_empty(tmp_plugins, capsys):
    """CLI: mw plugin list with no plugins."""
    cmd_plugin(["list"])
    out = capsys.readouterr().out
    assert "No plugins installed" in out


def test_cmd_plugin_create(tmp_plugins, tmp_path, capsys):
    """CLI: mw plugin create."""
    cmd_plugin(["create", "test-plug", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert "Created plugin scaffold" in out
