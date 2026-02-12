#!/usr/bin/env python3
"""MyWork Plugin Manager - Extensible plugin system for mw CLI.

Enables community plugins that add new commands, templates, and integrations.
Plugins live in ~/.mywork/plugins/ and are auto-discovered on startup.
"""

import json
import os
import sys
import shutil
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

PLUGIN_DIR = Path.home() / ".mywork" / "plugins"
PLUGIN_REGISTRY = PLUGIN_DIR / "registry.json"
PLUGIN_INDEX_URL = "https://raw.githubusercontent.com/DansiDanutz/mywork-plugins/main/index.json"


class Colors:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    ENDC = "\033[0m"


def ensure_plugin_dir():
    """Create plugin directory if it doesn't exist."""
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    if not PLUGIN_REGISTRY.exists():
        PLUGIN_REGISTRY.write_text(json.dumps({"plugins": {}, "installed_at": datetime.now().isoformat()}, indent=2))


def load_registry() -> Dict:
    """Load the local plugin registry."""
    ensure_plugin_dir()
    try:
        return json.loads(PLUGIN_REGISTRY.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {"plugins": {}}


def save_registry(registry: Dict):
    """Save the local plugin registry."""
    ensure_plugin_dir()
    PLUGIN_REGISTRY.write_text(json.dumps(registry, indent=2))


def validate_plugin(plugin_path: Path) -> Dict[str, Any]:
    """Validate a plugin directory structure and return its manifest."""
    manifest_file = plugin_path / "plugin.json"
    if not manifest_file.exists():
        return {"valid": False, "error": "Missing plugin.json manifest"}
    
    try:
        manifest = json.loads(manifest_file.read_text())
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid plugin.json: {e}"}
    
    required_fields = ["name", "version", "description", "author"]
    missing = [f for f in required_fields if f not in manifest]
    if missing:
        return {"valid": False, "error": f"Missing fields in plugin.json: {', '.join(missing)}"}
    
    # Check for entry point
    entry = manifest.get("entry", "main.py")
    entry_path = plugin_path / entry
    if not entry_path.exists():
        return {"valid": False, "error": f"Entry point '{entry}' not found"}
    
    # Security: check for suspicious patterns
    suspicious = _security_scan(plugin_path)
    if suspicious:
        manifest["_warnings"] = suspicious
    
    manifest["_path"] = str(plugin_path)
    manifest["valid"] = True
    return manifest


def _security_scan(plugin_path: Path) -> List[str]:
    """Basic security scan for suspicious patterns."""
    warnings = []
    dangerous_patterns = [
        ("os.system(", "Direct system command execution"),
        ("subprocess.call(", "Subprocess without capture"),
        ("eval(", "Dynamic code evaluation"),
        ("exec(", "Dynamic code execution"),
        ("__import__", "Dynamic imports"),
        ("open('/etc/", "System file access"),
        ("shutil.rmtree('/'", "Root directory deletion"),
    ]
    
    for py_file in plugin_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            for pattern, desc in dangerous_patterns:
                if pattern in content:
                    warnings.append(f"⚠️  {py_file.name}: {desc} ({pattern})")
        except Exception:
            pass
    
    return warnings


def install_plugin(source: str, force: bool = False) -> Dict:
    """Install a plugin from a local path or git URL."""
    ensure_plugin_dir()
    
    if source.startswith(("http://", "https://", "git@")):
        # Git clone
        plugin_name = source.rstrip("/").split("/")[-1].replace(".git", "")
        target = PLUGIN_DIR / plugin_name
        
        if target.exists():
            if force:
                shutil.rmtree(target)
            else:
                return {"success": False, "error": f"Plugin '{plugin_name}' already installed. Use --force to reinstall."}
        
        result = subprocess.run(
            ["git", "clone", "--depth=1", source, str(target)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {"success": False, "error": f"Git clone failed: {result.stderr}"}
    
    elif os.path.isdir(source):
        # Local directory — copy
        plugin_name = os.path.basename(os.path.abspath(source))
        target = PLUGIN_DIR / plugin_name
        
        if target.exists():
            if force:
                shutil.rmtree(target)
            else:
                return {"success": False, "error": f"Plugin '{plugin_name}' already installed. Use --force to reinstall."}
        
        shutil.copytree(source, target)
    else:
        return {"success": False, "error": f"Invalid source: {source}"}
    
    # Validate
    validation = validate_plugin(target)
    if not validation.get("valid"):
        shutil.rmtree(target, ignore_errors=True)
        return {"success": False, "error": f"Invalid plugin: {validation.get('error')}"}
    
    # Show security warnings
    if validation.get("_warnings"):
        print(f"\n{Colors.YELLOW}⚠️  Security warnings:{Colors.ENDC}")
        for w in validation["_warnings"]:
            print(f"   {w}")
    
    # Register
    registry = load_registry()
    registry["plugins"][validation["name"]] = {
        "version": validation["version"],
        "description": validation["description"],
        "author": validation["author"],
        "path": str(target),
        "installed": datetime.now().isoformat(),
        "enabled": True,
        "commands": validation.get("commands", []),
    }
    save_registry(registry)
    
    # Install dependencies if requirements.txt exists
    req_file = target / "requirements.txt"
    if req_file.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"],
                      capture_output=True, timeout=120)
    
    return {"success": True, "name": validation["name"], "version": validation["version"]}


def uninstall_plugin(name: str) -> Dict:
    """Remove an installed plugin."""
    registry = load_registry()
    if name not in registry.get("plugins", {}):
        return {"success": False, "error": f"Plugin '{name}' not found"}
    
    plugin_info = registry["plugins"][name]
    plugin_path = Path(plugin_info["path"])
    
    if plugin_path.exists():
        shutil.rmtree(plugin_path)
    
    del registry["plugins"][name]
    save_registry(registry)
    
    return {"success": True, "name": name}


def list_plugins() -> List[Dict]:
    """List all installed plugins."""
    registry = load_registry()
    plugins = []
    for name, info in registry.get("plugins", {}).items():
        info["name"] = name
        plugins.append(info)
    return plugins


def get_plugin_commands() -> Dict[str, Dict]:
    """Get all commands registered by plugins for CLI integration."""
    registry = load_registry()
    commands = {}
    for name, info in registry.get("plugins", {}).items():
        if not info.get("enabled", True):
            continue
        for cmd in info.get("commands", []):
            commands[cmd] = {
                "plugin": name,
                "path": info["path"],
            }
    return commands


def run_plugin_command(plugin_name: str, command: str, args: List[str] = None) -> int:
    """Execute a plugin command."""
    registry = load_registry()
    plugin_info = registry.get("plugins", {}).get(plugin_name)
    if not plugin_info:
        print(f"{Colors.RED}Plugin '{plugin_name}' not found{Colors.ENDC}")
        return 1
    
    plugin_path = Path(plugin_info["path"])
    entry = "main.py"
    
    # Load manifest for entry point
    manifest_file = plugin_path / "plugin.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        entry = manifest.get("entry", "main.py")
    
    entry_path = plugin_path / entry
    if not entry_path.exists():
        print(f"{Colors.RED}Plugin entry point not found: {entry}{Colors.ENDC}")
        return 1
    
    # Run the plugin
    cmd = [sys.executable, str(entry_path), command] + (args or [])
    result = subprocess.run(cmd, cwd=str(plugin_path))
    return result.returncode


def create_plugin_scaffold(name: str, path: str = None) -> Dict:
    """Create a new plugin scaffold."""
    target = Path(path or ".") / name
    if target.exists():
        return {"success": False, "error": f"Directory '{target}' already exists"}
    
    target.mkdir(parents=True)
    
    # plugin.json
    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": f"MyWork plugin: {name}",
        "author": "Your Name",
        "entry": "main.py",
        "commands": [name],
        "mw_version": ">=2.0.0",
    }
    (target / "plugin.json").write_text(json.dumps(manifest, indent=2))
    
    # main.py
    (target / "main.py").write_text(f'''#!/usr/bin/env python3
"""{name} - MyWork Plugin"""

import sys

def run(args=None):
    """Main entry point for the plugin."""
    args = args or sys.argv[1:]
    print(f"🔌 {name} plugin running!")
    print(f"   Args: {{args}}")
    return 0

if __name__ == "__main__":
    sys.exit(run())
''')
    
    # README.md
    (target / "README.md").write_text(f"""# {name}

A MyWork plugin.

## Installation

```bash
mw plugin install /path/to/{name}
```

## Usage

```bash
mw {name}
```
""")
    
    return {"success": True, "path": str(target)}


# CLI interface
def main(args: List[str] = None) -> int:
    """Plugin manager CLI."""
    args = args or sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h", "help"):
        print(f"""
{Colors.BOLD}🔌 MyWork Plugin Manager{Colors.ENDC}
{'─' * 45}

{Colors.CYAN}Usage:{Colors.ENDC}
  mw plugin list                    List installed plugins
  mw plugin install <source>        Install from path or git URL
  mw plugin uninstall <name>        Remove a plugin
  mw plugin create <name>           Scaffold a new plugin
  mw plugin info <name>             Show plugin details
  mw plugin enable <name>           Enable a plugin
  mw plugin disable <name>          Disable a plugin

{Colors.CYAN}Sources:{Colors.ENDC}
  Local:  mw plugin install ./my-plugin
  Git:    mw plugin install https://github.com/user/mw-plugin.git

{Colors.CYAN}Create your own:{Colors.ENDC}
  mw plugin create my-plugin        Creates scaffold with plugin.json + main.py
""")
        return 0
    
    subcmd = args[0]
    subargs = args[1:]
    
    if subcmd == "list":
        plugins = list_plugins()
        if not plugins:
            print(f"\n{Colors.DIM}No plugins installed. Try: mw plugin install <source>{Colors.ENDC}")
            return 0
        
        print(f"\n{Colors.BOLD}🔌 Installed Plugins{Colors.ENDC}")
        print(f"{'─' * 55}")
        for p in plugins:
            status = f"{Colors.GREEN}●{Colors.ENDC}" if p.get("enabled", True) else f"{Colors.RED}○{Colors.ENDC}"
            cmds = ", ".join(p.get("commands", []))
            print(f"  {status} {Colors.BOLD}{p['name']}{Colors.ENDC} v{p.get('version', '?')}")
            print(f"    {Colors.DIM}{p.get('description', '')}{Colors.ENDC}")
            if cmds:
                print(f"    Commands: {Colors.CYAN}{cmds}{Colors.ENDC}")
        print()
        return 0
    
    elif subcmd == "install":
        if not subargs:
            print(f"{Colors.RED}Usage: mw plugin install <source>{Colors.ENDC}")
            return 1
        force = "--force" in subargs
        source = [a for a in subargs if not a.startswith("--")][0]
        
        print(f"\n{Colors.BOLD}📦 Installing plugin...{Colors.ENDC}")
        result = install_plugin(source, force=force)
        if result["success"]:
            print(f"{Colors.GREEN}✅ Installed {result['name']} v{result['version']}{Colors.ENDC}\n")
            return 0
        else:
            print(f"{Colors.RED}❌ {result['error']}{Colors.ENDC}\n")
            return 1
    
    elif subcmd == "uninstall":
        if not subargs:
            print(f"{Colors.RED}Usage: mw plugin uninstall <name>{Colors.ENDC}")
            return 1
        result = uninstall_plugin(subargs[0])
        if result["success"]:
            print(f"{Colors.GREEN}✅ Uninstalled {result['name']}{Colors.ENDC}")
            return 0
        else:
            print(f"{Colors.RED}❌ {result['error']}{Colors.ENDC}")
            return 1
    
    elif subcmd == "create":
        if not subargs:
            print(f"{Colors.RED}Usage: mw plugin create <name>{Colors.ENDC}")
            return 1
        result = create_plugin_scaffold(subargs[0])
        if result["success"]:
            print(f"{Colors.GREEN}✅ Plugin scaffold created at {result['path']}{Colors.ENDC}")
            print(f"{Colors.DIM}   Edit plugin.json and main.py, then: mw plugin install {result['path']}{Colors.ENDC}")
            return 0
        else:
            print(f"{Colors.RED}❌ {result['error']}{Colors.ENDC}")
            return 1
    
    elif subcmd == "info":
        if not subargs:
            print(f"{Colors.RED}Usage: mw plugin info <name>{Colors.ENDC}")
            return 1
        registry = load_registry()
        info = registry.get("plugins", {}).get(subargs[0])
        if not info:
            print(f"{Colors.RED}Plugin '{subargs[0]}' not found{Colors.ENDC}")
            return 1
        print(f"\n{Colors.BOLD}🔌 {subargs[0]}{Colors.ENDC}")
        print(f"{'─' * 40}")
        for k, v in info.items():
            if not k.startswith("_"):
                print(f"  {Colors.CYAN}{k}:{Colors.ENDC} {v}")
        print()
        return 0
    
    elif subcmd in ("enable", "disable"):
        if not subargs:
            print(f"{Colors.RED}Usage: mw plugin {subcmd} <name>{Colors.ENDC}")
            return 1
        registry = load_registry()
        if subargs[0] not in registry.get("plugins", {}):
            print(f"{Colors.RED}Plugin '{subargs[0]}' not found{Colors.ENDC}")
            return 1
        registry["plugins"][subargs[0]]["enabled"] = (subcmd == "enable")
        save_registry(registry)
        state = "enabled" if subcmd == "enable" else "disabled"
        print(f"{Colors.GREEN}✅ Plugin '{subargs[0]}' {state}{Colors.ENDC}")
        return 0
    
    else:
        print(f"{Colors.RED}Unknown command: {subcmd}. Try: mw plugin --help{Colors.ENDC}")
        return 1


cmd_plugin = main  # alias for mw.py integration

if __name__ == "__main__":
    sys.exit(main())
