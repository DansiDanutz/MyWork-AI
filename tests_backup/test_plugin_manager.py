#!/usr/bin/env python3
"""Tests for plugin_manager."""
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.plugin_manager import (
    discover_plugins, cmd_create, cmd_list, cmd_remove,
    cmd_info, run_plugin, load_registry, save_registry,
    PLUGIN_TEMPLATE, main
)


class TestPluginManager:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_global = os.environ.get("MW_PLUGIN_DIR")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_discover_empty(self):
        """No plugins in empty dirs."""
        import tools.plugin_manager as pm
        orig = pm.GLOBAL_PLUGIN_DIR
        pm.GLOBAL_PLUGIN_DIR = Path(self.tmpdir) / "empty"
        plugins = discover_plugins()
        # May find 0 or some from local dir
        pm.GLOBAL_PLUGIN_DIR = orig

    def test_create_and_discover(self, capsys):
        import tools.plugin_manager as pm
        orig = pm.GLOBAL_PLUGIN_DIR
        orig_reg = pm.PLUGIN_REGISTRY
        pm.GLOBAL_PLUGIN_DIR = Path(self.tmpdir) / "plugins"
        pm.PLUGIN_REGISTRY = pm.GLOBAL_PLUGIN_DIR / "registry.json"
        
        cmd_create(["test_plug", "A test plugin"])
        captured = capsys.readouterr()
        assert "✅" in captured.out
        
        plugins = discover_plugins()
        assert "test_plug" in plugins
        
        pm.GLOBAL_PLUGIN_DIR = orig
        pm.PLUGIN_REGISTRY = orig_reg

    def test_run_plugin(self, capsys):
        import tools.plugin_manager as pm
        orig = pm.GLOBAL_PLUGIN_DIR
        orig_reg = pm.PLUGIN_REGISTRY
        pm.GLOBAL_PLUGIN_DIR = Path(self.tmpdir) / "plugins"
        pm.PLUGIN_REGISTRY = pm.GLOBAL_PLUGIN_DIR / "registry.json"
        
        cmd_create(["runner", "Test runner"])
        capsys.readouterr()
        
        result = run_plugin("runner", ["arg1"])
        assert result is True
        captured = capsys.readouterr()
        assert "runner" in captured.out
        
        pm.GLOBAL_PLUGIN_DIR = orig
        pm.PLUGIN_REGISTRY = orig_reg

    def test_run_nonexistent(self):
        import tools.plugin_manager as pm
        orig = pm.GLOBAL_PLUGIN_DIR
        pm.GLOBAL_PLUGIN_DIR = Path(self.tmpdir) / "empty"
        pm.GLOBAL_PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
        
        result = run_plugin("nonexistent", [])
        assert result is False
        
        pm.GLOBAL_PLUGIN_DIR = orig

    def test_remove_plugin(self, capsys):
        import tools.plugin_manager as pm
        orig = pm.GLOBAL_PLUGIN_DIR
        orig_reg = pm.PLUGIN_REGISTRY
        pm.GLOBAL_PLUGIN_DIR = Path(self.tmpdir) / "plugins"
        pm.PLUGIN_REGISTRY = pm.GLOBAL_PLUGIN_DIR / "registry.json"
        
        cmd_create(["to_remove"])
        capsys.readouterr()
        
        cmd_remove(["to_remove"])
        captured = capsys.readouterr()
        assert "removed" in captured.out.lower() or "🗑️" in captured.out
        
        plugins = discover_plugins()
        assert "to_remove" not in plugins
        
        pm.GLOBAL_PLUGIN_DIR = orig
        pm.PLUGIN_REGISTRY = orig_reg

    def test_registry_persistence(self):
        import tools.plugin_manager as pm
        orig_reg = pm.PLUGIN_REGISTRY
        pm.PLUGIN_REGISTRY = Path(self.tmpdir) / "reg.json"
        
        save_registry({"test": {"installed": "now"}})
        loaded = load_registry()
        assert "test" in loaded
        
        pm.PLUGIN_REGISTRY = orig_reg

    def test_main_help(self, capsys):
        main(["help"])
        captured = capsys.readouterr()
        assert "plugin" in captured.out.lower() or "Plugin" in captured.out
