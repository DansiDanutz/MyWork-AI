"""
MyWork Plugin Manager — Extensible plugin system for mw CLI.

Plugins live in ~/.mywork/plugins/<name>/ with a plugin.json manifest.
Each plugin can add CLI commands, hooks, and templates.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PLUGINS_DIR = Path.home() / ".mywork" / "plugins"
PLUGIN_REGISTRY_URL = "https://raw.githubusercontent.com/DansiDanutz/MyWork-AI/main/plugin-registry.json"


def get_plugins_dir() -> Path:
    """Get or create plugins directory."""
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    return PLUGINS_DIR


def load_plugin_manifest(plugin_dir: Path) -> Optional[Dict[str, Any]]:
    """Load plugin.json from a plugin directory."""
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.exists():
        return None
    try:
        with open(manifest_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def list_plugins() -> List[Dict[str, Any]]:
    """List all installed plugins with their metadata."""
    plugins_dir = get_plugins_dir()
    plugins = []
    for item in sorted(plugins_dir.iterdir()):
        if item.is_dir():
            manifest = load_plugin_manifest(item)
            if manifest:
                manifest["_path"] = str(item)
                manifest["_enabled"] = not (item / ".disabled").exists()
                plugins.append(manifest)
    return plugins


def install_plugin(source: str) -> Dict[str, Any]:
    """
    Install a plugin from a git URL or local path.
    Returns result dict with status.
    """
    plugins_dir = get_plugins_dir()
    source_path = Path(source).expanduser()

    if source_path.exists() and source_path.is_dir():
        # Local install — copy
        manifest = load_plugin_manifest(source_path)
        if not manifest:
            return {"ok": False, "error": f"No valid plugin.json in {source}"}
        name = manifest.get("name", source_path.name)
        dest = plugins_dir / name
        if dest.exists():
            return {"ok": False, "error": f"Plugin '{name}' already installed. Use 'mw plugin update {name}'."}
        shutil.copytree(source_path, dest)
        return {"ok": True, "name": name, "version": manifest.get("version", "0.0.0")}

    elif source.startswith("http") or source.startswith("git@"):
        # Git clone
        try:
            tmp_dir = plugins_dir / ".tmp_clone"
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
            subprocess.run(["git", "clone", "--depth=1", source, str(tmp_dir)],
                           capture_output=True, text=True, check=True, timeout=30)
            manifest = load_plugin_manifest(tmp_dir)
            if not manifest:
                shutil.rmtree(tmp_dir)
                return {"ok": False, "error": "Cloned repo has no valid plugin.json"}
            name = manifest.get("name", tmp_dir.name)
            dest = plugins_dir / name
            if dest.exists():
                shutil.rmtree(tmp_dir)
                return {"ok": False, "error": f"Plugin '{name}' already installed."}
            tmp_dir.rename(dest)
            return {"ok": True, "name": name, "version": manifest.get("version", "0.0.0")}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Git clone failed: {e.stderr}"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Git clone timed out"}
    else:
        return {"ok": False, "error": f"Unknown source: {source}. Use a git URL or local path."}


def uninstall_plugin(name: str) -> Dict[str, Any]:
    """Remove an installed plugin."""
    plugin_dir = get_plugins_dir() / name
    if not plugin_dir.exists():
        return {"ok": False, "error": f"Plugin '{name}' not found."}
    shutil.rmtree(plugin_dir)
    return {"ok": True, "name": name}


def enable_plugin(name: str) -> Dict[str, Any]:
    """Enable a disabled plugin."""
    plugin_dir = get_plugins_dir() / name
    disabled_flag = plugin_dir / ".disabled"
    if not plugin_dir.exists():
        return {"ok": False, "error": f"Plugin '{name}' not found."}
    if disabled_flag.exists():
        disabled_flag.unlink()
    return {"ok": True, "name": name, "enabled": True}


def disable_plugin(name: str) -> Dict[str, Any]:
    """Disable a plugin without removing it."""
    plugin_dir = get_plugins_dir() / name
    if not plugin_dir.exists():
        return {"ok": False, "error": f"Plugin '{name}' not found."}
    (plugin_dir / ".disabled").touch()
    return {"ok": True, "name": name, "enabled": False}


def run_plugin_command(name: str, cmd_args: List[str]) -> int:
    """Run a command defined by a plugin."""
    plugin_dir = get_plugins_dir() / name
    manifest = load_plugin_manifest(plugin_dir)
    if not manifest:
        print(f"❌ Plugin '{name}' not found or invalid.")
        return 1
    if (plugin_dir / ".disabled").exists():
        print(f"⚠️  Plugin '{name}' is disabled. Run: mw plugin enable {name}")
        return 1

    commands = manifest.get("commands", {})
    if not cmd_args:
        # Show available commands
        print(f"📦 {manifest.get('name', name)} v{manifest.get('version', '?')}")
        print(f"   {manifest.get('description', 'No description')}")
        if commands:
            print(f"\n   Commands:")
            for cmd_name, cmd_info in commands.items():
                desc = cmd_info.get("description", "") if isinstance(cmd_info, dict) else ""
                print(f"     mw {name}:{cmd_name}  — {desc}")
        return 0

    sub_cmd = cmd_args[0]
    if sub_cmd not in commands:
        print(f"❌ Unknown command '{sub_cmd}' for plugin '{name}'.")
        return 1

    cmd_info = commands[sub_cmd]
    script = cmd_info.get("run") if isinstance(cmd_info, dict) else cmd_info
    if not script:
        print(f"❌ No 'run' defined for command '{sub_cmd}'.")
        return 1

    # Run the script from the plugin directory
    script_path = plugin_dir / script
    if script.endswith(".py"):
        result = subprocess.run([sys.executable, str(script_path)] + cmd_args[1:], cwd=str(plugin_dir))
    elif script.endswith(".sh"):
        result = subprocess.run(["bash", str(script_path)] + cmd_args[1:], cwd=str(plugin_dir))
    else:
        result = subprocess.run([str(script_path)] + cmd_args[1:], cwd=str(plugin_dir))
    return result.returncode


def get_plugin_commands() -> Dict[str, str]:
    """Get all commands from enabled plugins. Returns {command_name: plugin_name}."""
    commands = {}
    for plugin in list_plugins():
        if plugin.get("_enabled", True):
            for cmd_name in plugin.get("commands", {}):
                full_name = f"{plugin['name']}:{cmd_name}"
                commands[full_name] = plugin["name"]
    return commands


def create_plugin_scaffold(name: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Create a new plugin scaffold."""
    dest = Path(path or ".") / name
    if dest.exists():
        return {"ok": False, "error": f"Directory '{dest}' already exists."}

    dest.mkdir(parents=True)

    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": f"{name} plugin for MyWork-AI",
        "author": "",
        "commands": {
            "hello": {
                "run": "hello.py",
                "description": "Example command"
            }
        },
        "hooks": {},
        "requires": []
    }

    with open(dest / "plugin.json", "w") as f:
        json.dump(manifest, f, indent=2)

    with open(dest / "hello.py", "w") as f:
        f.write('#!/usr/bin/env python3\n"""Example plugin command."""\nimport sys\n\ndef main():\n    print(f"Hello from {__file__}!")\n    print(f"Args: {sys.argv[1:]}")\n\nif __name__ == "__main__":\n    main()\n')

    with open(dest / "README.md", "w") as f:
        f.write(f"# {name}\n\nMyWork-AI plugin.\n\n## Commands\n\n- `mw {name}:hello` — Example command\n")

    return {"ok": True, "path": str(dest)}


def cmd_plugin(args: List[str]) -> int:
    """Handle 'mw plugin' subcommands."""
    if not args:
        args = ["list"]

    sub = args[0]

    if sub == "list":
        plugins = list_plugins()
        if not plugins:
            print("📦 No plugins installed.")
            print("   Install one: mw plugin install <git-url-or-path>")
            print("   Create one:  mw plugin create <name>")
            return 0
        print(f"📦 Installed plugins ({len(plugins)}):\n")
        for p in plugins:
            status = "✅" if p.get("_enabled", True) else "⏸️"
            print(f"  {status} {p.get('name', '?')} v{p.get('version', '?')}")
            print(f"     {p.get('description', '')}")
            cmds = list(p.get("commands", {}).keys())
            if cmds:
                print(f"     Commands: {', '.join(cmds)}")
            print()
        return 0

    elif sub == "install":
        if len(args) < 2:
            print("Usage: mw plugin install <git-url-or-local-path>")
            return 1
        result = install_plugin(args[1])
        if result["ok"]:
            print(f"✅ Installed plugin '{result['name']}' v{result.get('version', '?')}")
        else:
            print(f"❌ {result['error']}")
            return 1
        return 0

    elif sub == "uninstall" or sub == "remove":
        if len(args) < 2:
            print("Usage: mw plugin uninstall <name>")
            return 1
        result = uninstall_plugin(args[1])
        if result["ok"]:
            print(f"✅ Removed plugin '{result['name']}'")
        else:
            print(f"❌ {result['error']}")
            return 1
        return 0

    elif sub == "enable":
        if len(args) < 2:
            print("Usage: mw plugin enable <name>")
            return 1
        result = enable_plugin(args[1])
        if result["ok"]:
            print(f"✅ Enabled plugin '{result['name']}'")
        else:
            print(f"❌ {result['error']}")
            return 1
        return 0

    elif sub == "disable":
        if len(args) < 2:
            print("Usage: mw plugin disable <name>")
            return 1
        result = disable_plugin(args[1])
        if result["ok"]:
            print(f"⏸️  Disabled plugin '{result['name']}'")
        else:
            print(f"❌ {result['error']}")
            return 1
        return 0

    elif sub == "create":
        if len(args) < 2:
            print("Usage: mw plugin create <name> [--path <dir>]")
            return 1
        path = None
        if "--path" in args:
            idx = args.index("--path")
            if idx + 1 < len(args):
                path = args[idx + 1]
        result = create_plugin_scaffold(args[1], path)
        if result["ok"]:
            print(f"✅ Created plugin scaffold at {result['path']}")
            print(f"   Edit plugin.json to configure, then: mw plugin install {result['path']}")
        else:
            print(f"❌ {result['error']}")
            return 1
        return 0

    elif sub == "info":
        if len(args) < 2:
            print("Usage: mw plugin info <name>")
            return 1
        return run_plugin_command(args[1], [])

    elif sub == "run":
        if len(args) < 3:
            print("Usage: mw plugin run <name> <command> [args...]")
            return 1
        return run_plugin_command(args[1], args[2:])

    else:
        print(f"Unknown subcommand: {sub}")
        print("Available: list, install, uninstall, enable, disable, create, info, run")
        return 1
