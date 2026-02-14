#!/usr/bin/env python3
"""
MyWork Plugin Manager — extend mw with custom commands.

Plugins are Python files in ~/.mywork/plugins/ or <project>/.mw-plugins/
Each plugin exports: NAME, DESCRIPTION, and a run(args) function.

Usage:
    mw plugin list              List installed plugins
    mw plugin install <path>    Install a plugin from file/URL
    mw plugin remove <name>     Remove a plugin
    mw plugin create <name>     Scaffold a new plugin
    mw plugin info <name>       Show plugin details
"""

import os
import sys
import json
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime

GLOBAL_PLUGIN_DIR = Path.home() / ".mywork" / "plugins"
LOCAL_PLUGIN_DIR = Path(".mw-plugins")
PLUGIN_REGISTRY = GLOBAL_PLUGIN_DIR / "registry.json"

PLUGIN_TEMPLATE = '''#!/usr/bin/env python3
"""
MyWork Plugin: {name}
Description: {description}
"""

NAME = "{name}"
DESCRIPTION = "{description}"
VERSION = "0.1.0"
AUTHOR = ""

def run(args):
    """Entry point. args = list of CLI arguments after the command name."""
    print(f"🔌 {{NAME}} v{{VERSION}}")
    if args:
        print(f"   Args: {{args}}")
    else:
        print("   No arguments provided.")
        print(f"   Usage: mw {{NAME}} [args...]")
'''


def ensure_dirs():
    GLOBAL_PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    if not PLUGIN_REGISTRY.exists():
        PLUGIN_REGISTRY.write_text("{}")


def load_registry():
    ensure_dirs()
    try:
        return json.loads(PLUGIN_REGISTRY.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_registry(reg):
    ensure_dirs()
    PLUGIN_REGISTRY.write_text(json.dumps(reg, indent=2))


def discover_plugins():
    """Find all plugins from global + local dirs."""
    plugins = {}
    for d in [GLOBAL_PLUGIN_DIR, LOCAL_PLUGIN_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(f.stem, str(f))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                name = getattr(mod, "NAME", f.stem)
                plugins[name] = {
                    "name": name,
                    "description": getattr(mod, "DESCRIPTION", "No description"),
                    "version": getattr(mod, "VERSION", "0.0.0"),
                    "author": getattr(mod, "AUTHOR", ""),
                    "path": str(f),
                    "source": "local" if d == LOCAL_PLUGIN_DIR else "global",
                }
            except Exception as e:
                plugins[f.stem] = {
                    "name": f.stem,
                    "description": f"⚠️ Error loading: {e}",
                    "path": str(f),
                    "source": "error",
                }
    return plugins


def cmd_list():
    plugins = discover_plugins()
    if not plugins:
        print("📭 No plugins installed.")
        print(f"   Global dir: {GLOBAL_PLUGIN_DIR}")
        print(f"   Local dir:  {LOCAL_PLUGIN_DIR}")
        print(f"\n   Create one: mw plugin create my-tool")
        return
    print(f"🔌 Installed Plugins ({len(plugins)})\n")
    for name, info in sorted(plugins.items()):
        src = "📁" if info["source"] == "local" else "🌍"
        ver = info.get("version", "")
        print(f"  {src} {name} v{ver} — {info['description']}")
    print(f"\n   Global: {GLOBAL_PLUGIN_DIR}")
    if LOCAL_PLUGIN_DIR.exists():
        print(f"   Local:  {LOCAL_PLUGIN_DIR}")


def cmd_create(args):
    if not args:
        print("❌ Usage: mw plugin create <name> [description]")
        return
    name = args[0].replace("-", "_")
    desc = " ".join(args[1:]) if len(args) > 1 else f"Custom {name} plugin"
    ensure_dirs()
    target = GLOBAL_PLUGIN_DIR / f"{name}.py"
    if target.exists():
        print(f"❌ Plugin '{name}' already exists at {target}")
        return
    target.write_text(PLUGIN_TEMPLATE.format(name=name, description=desc))
    # Update registry
    reg = load_registry()
    reg[name] = {"installed": datetime.now().isoformat(), "path": str(target)}
    save_registry(reg)
    print(f"✅ Plugin '{name}' created at {target}")
    print(f"   Edit it, then run: mw {name}")


def cmd_install(args):
    if not args:
        print("❌ Usage: mw plugin install <file_path>")
        return
    src = Path(args[0])
    if not src.exists():
        print(f"❌ File not found: {src}")
        return
    ensure_dirs()
    dest = GLOBAL_PLUGIN_DIR / src.name
    shutil.copy2(src, dest)
    # Validate
    try:
        spec = importlib.util.spec_from_file_location(src.stem, str(dest))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        name = getattr(mod, "NAME", src.stem)
    except Exception as e:
        print(f"⚠️ Installed but failed to load: {e}")
        name = src.stem
    reg = load_registry()
    reg[name] = {"installed": datetime.now().isoformat(), "path": str(dest)}
    save_registry(reg)
    print(f"✅ Plugin '{name}' installed to {dest}")


def cmd_remove(args):
    if not args:
        print("❌ Usage: mw plugin remove <name>")
        return
    name = args[0]
    plugins = discover_plugins()
    if name not in plugins:
        print(f"❌ Plugin '{name}' not found")
        return
    path = Path(plugins[name]["path"])
    if path.exists():
        path.unlink()
    reg = load_registry()
    reg.pop(name, None)
    save_registry(reg)
    print(f"🗑️ Plugin '{name}' removed")


def cmd_info(args):
    if not args:
        print("❌ Usage: mw plugin info <name>")
        return
    plugins = discover_plugins()
    name = args[0]
    if name not in plugins:
        print(f"❌ Plugin '{name}' not found")
        return
    info = plugins[name]
    print(f"🔌 {info['name']} v{info.get('version', '?')}")
    print(f"   Description: {info['description']}")
    print(f"   Author:      {info.get('author', 'Unknown')}")
    print(f"   Path:        {info['path']}")
    print(f"   Source:       {info['source']}")


def run_plugin(name, args):
    """Execute a plugin by name."""
    plugins = discover_plugins()
    if name not in plugins:
        return False
    info = plugins[name]
    if info["source"] == "error":
        print(f"❌ Plugin '{name}' has errors and cannot run")
        return True
    try:
        spec = importlib.util.spec_from_file_location(name, info["path"])
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "run"):
            mod.run(args)
        else:
            print(f"❌ Plugin '{name}' has no run() function")
    except Exception as e:
        print(f"❌ Plugin '{name}' error: {e}")
    return True


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return

    subcmd = args[0]
    rest = args[1:]

    commands = {
        "list": lambda: cmd_list(),
        "ls": lambda: cmd_list(),
        "create": lambda: cmd_create(rest),
        "install": lambda: cmd_install(rest),
        "remove": lambda: cmd_remove(rest),
        "uninstall": lambda: cmd_remove(rest),
        "info": lambda: cmd_info(rest),
    }

    if subcmd in commands:
        commands[subcmd]()
    else:
        print(f"❌ Unknown subcommand: {subcmd}")
        print("   Available: list, create, install, remove, info")


if __name__ == "__main__":
    main()
