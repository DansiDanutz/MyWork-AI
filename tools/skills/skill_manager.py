#!/usr/bin/env python3
"""
MyWork-AI Agent Skills Manager
============================
Inspired by Anthropic/OpenAI Agent Skills standard

Manages skills discovery, installation, and execution.
Skills are folder-based with SKILL.md manifest + scripts.

Usage:
    mw skills list               # List installed skills
    mw skills install <url>      # Install skill from GitHub URL
    mw skills create <name>      # Scaffold a new skill
    mw skills remove <name>      # Remove a skill
    mw skills run <name> <cmd>   # Run skill command
    mw skills info <name>        # Show skill information
"""

import os
import sys
import json
import subprocess
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configuration
SKILLS_DIR = Path(__file__).parent
INSTALLED_DIR = SKILLS_DIR / "installed"
SKILL_MANIFEST = "SKILL.md"
SKILL_CONFIG = "skill.json"


class SkillManager:
    def __init__(self):
        """Initialize the Skills Manager."""
        self.skills_dir = SKILLS_DIR
        self.installed_dir = INSTALLED_DIR
        self.installed_dir.mkdir(exist_ok=True)

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all installed skills with metadata."""
        skills = []
        
        if not self.installed_dir.exists():
            return skills
            
        for skill_dir in self.installed_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue
                
            skill_info = self._load_skill_info(skill_dir)
            if skill_info:
                skills.append(skill_info)
                
        return sorted(skills, key=lambda x: x['name'])

    def install_skill(self, url: str, name: Optional[str] = None) -> bool:
        """Install a skill from GitHub URL."""
        try:
            print(f"🔄 Installing skill from: {url}")
            
            # Determine skill name
            if not name:
                name = self._extract_skill_name(url)
                
            skill_path = self.installed_dir / name
            if skill_path.exists():
                print(f"❌ Skill '{name}' already exists")
                return False

            # Clone or download skill
            if url.startswith(('http://', 'https://')):
                if url.endswith('.git') or 'github.com' in url:
                    return self._install_from_git(url, skill_path)
                else:
                    return self._install_from_url(url, skill_path)
            else:
                return self._install_from_local(url, skill_path)
                
        except Exception as e:
            print(f"❌ Error installing skill: {e}")
            return False

    def create_skill(self, name: str) -> bool:
        """Scaffold a new skill with template structure."""
        try:
            skill_path = self.installed_dir / name
            if skill_path.exists():
                print(f"❌ Skill '{name}' already exists")
                return False

            skill_path.mkdir(parents=True)
            
            # Create SKILL.md manifest
            self._create_skill_manifest(skill_path, name)
            
            # Create basic script template
            self._create_skill_script(skill_path, name)
            
            # Create skill.json config
            self._create_skill_config(skill_path, name)
            
            print(f"✅ Created skill '{name}' at {skill_path}")
            print(f"💡 Edit {skill_path}/SKILL.md to customize")
            return True
            
        except Exception as e:
            print(f"❌ Error creating skill: {e}")
            return False

    def remove_skill(self, name: str) -> bool:
        """Remove an installed skill."""
        try:
            skill_path = self.installed_dir / name
            if not skill_path.exists():
                print(f"❌ Skill '{name}' not found")
                return False

            shutil.rmtree(skill_path)
            print(f"✅ Removed skill '{name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error removing skill: {e}")
            return False

    def run_skill_command(self, skill_name: str, command: str, args: List[str] = None) -> int:
        """Run a specific command from a skill."""
        try:
            skill_info = self._get_skill_info(skill_name)
            if not skill_info:
                print(f"❌ Skill '{skill_name}' not found")
                return 1

            commands = skill_info.get('commands', {})
            if command not in commands:
                print(f"❌ Command '{command}' not found in skill '{skill_name}'")
                print(f"Available commands: {list(commands.keys())}")
                return 1

            # Execute command
            cmd_info = commands[command]
            script_path = skill_info['path'] / cmd_info['script']
            
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return 1

            # Build command
            if script_path.suffix == '.py':
                cmd = [sys.executable, str(script_path)] + (args or [])
            elif script_path.suffix == '.sh':
                cmd = ['bash', str(script_path)] + (args or [])
            else:
                cmd = [str(script_path)] + (args or [])

            # Set environment
            env = os.environ.copy()
            env['SKILL_PATH'] = str(skill_info['path'])
            env['SKILL_NAME'] = skill_name
            
            return subprocess.call(cmd, env=env)
            
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return 1

    def show_skill_info(self, name: str) -> bool:
        """Show detailed information about a skill."""
        skill_info = self._get_skill_info(name)
        if not skill_info:
            print(f"❌ Skill '{name}' not found")
            return False

        print(f"\n📦 Skill: {skill_info['name']}")
        print("=" * 50)
        print(f"Description: {skill_info['description']}")
        print(f"Version: {skill_info['version']}")
        print(f"Author: {skill_info['author']}")
        print(f"Path: {skill_info['path']}")
        
        if skill_info['dependencies']:
            print(f"Dependencies: {', '.join(skill_info['dependencies'])}")
        
        if skill_info['commands']:
            print("\nCommands:")
            for cmd, info in skill_info['commands'].items():
                print(f"  {cmd}: {info['description']}")
                
        return True

    def _load_skill_info(self, skill_path: Path) -> Optional[Dict[str, Any]]:
        """Load skill information from SKILL.md."""
        manifest_path = skill_path / SKILL_MANIFEST
        if not manifest_path.exists():
            return None
            
        try:
            content = manifest_path.read_text()
            skill_info = self._parse_skill_manifest(content)
            skill_info['path'] = skill_path
            return skill_info
        except Exception:
            return None

    def _get_skill_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get skill info by name."""
        skill_path = self.installed_dir / name
        if not skill_path.exists():
            return None
        return self._load_skill_info(skill_path)

    def _parse_skill_manifest(self, content: str) -> Dict[str, Any]:
        """Parse SKILL.md manifest file following Anthropic standard."""
        lines = content.strip().split('\n')
        skill_info = {
            'name': 'unknown',
            'description': '',
            'version': '1.0.0',
            'author': 'unknown',
            'dependencies': [],
            'commands': {}
        }
        
        current_section = None
        current_command = None
        
        for line in lines:
            line = line.strip()
            
            # Parse metadata
            if line.startswith('# '):
                skill_info['name'] = line[2:].strip()
            elif line.startswith('**Description:**'):
                skill_info['description'] = line.replace('**Description:**', '').strip()
            elif line.startswith('**Version:**'):
                skill_info['version'] = line.replace('**Version:**', '').strip()
            elif line.startswith('**Author:**'):
                skill_info['author'] = line.replace('**Author:**', '').strip()
            
            # Parse sections
            elif line == '## Dependencies':
                current_section = 'dependencies'
            elif line == '## Commands':
                current_section = 'commands'
            elif line.startswith('### ') and current_section == 'commands':
                current_command = line[4:].strip()
                skill_info['commands'][current_command] = {
                    'description': '',
                    'script': f'{current_command}.py',  # Default
                    'usage': ''
                }
            elif line.startswith('- ') and current_section == 'dependencies':
                dep = line[2:].strip()
                skill_info['dependencies'].append(dep)
            elif current_command and line.startswith('**Script:**'):
                script = line.replace('**Script:**', '').strip()
                skill_info['commands'][current_command]['script'] = script
            elif current_command and line.startswith('**Usage:**'):
                usage = line.replace('**Usage:**', '').strip()
                skill_info['commands'][current_command]['usage'] = usage
            elif current_command and line and not line.startswith('**'):
                # Description text
                if skill_info['commands'][current_command]['description']:
                    skill_info['commands'][current_command]['description'] += ' '
                skill_info['commands'][current_command]['description'] += line
                
        return skill_info

    def _extract_skill_name(self, url: str) -> str:
        """Extract skill name from URL."""
        if url.endswith('.git'):
            url = url[:-4]
        name = url.split('/')[-1]
        return name.lower().replace('_', '-')

    def _install_from_git(self, url: str, skill_path: Path) -> bool:
        """Install skill from git repository."""
        try:
            subprocess.run(['git', 'clone', url, str(skill_path)], 
                         check=True, capture_output=True)
            
            # Validate skill structure
            if not self._validate_skill(skill_path):
                shutil.rmtree(skill_path)
                print("❌ Invalid skill structure")
                return False
                
            print(f"✅ Installed skill from {url}")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Git clone failed")
            return False

    def _install_from_url(self, url: str, skill_path: Path) -> bool:
        """Install skill from download URL."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpfile = Path(tmpdir) / "skill.zip"
                urllib.request.urlretrieve(url, tmpfile)
                
                # Extract (simplified - assumes zip)
                shutil.unpack_archive(tmpfile, skill_path)
                
            if not self._validate_skill(skill_path):
                shutil.rmtree(skill_path)
                print("❌ Invalid skill structure")
                return False
                
            print(f"✅ Installed skill from {url}")
            return True
            
        except Exception:
            print("❌ Download failed")
            return False

    def _install_from_local(self, path: str, skill_path: Path) -> bool:
        """Install skill from local directory."""
        try:
            source_path = Path(path)
            if not source_path.exists():
                print(f"❌ Source path not found: {path}")
                return False
                
            shutil.copytree(source_path, skill_path)
            
            if not self._validate_skill(skill_path):
                shutil.rmtree(skill_path)
                print("❌ Invalid skill structure")
                return False
                
            print(f"✅ Installed skill from {path}")
            return True
            
        except Exception as e:
            print(f"❌ Local install failed: {e}")
            return False

    def _validate_skill(self, skill_path: Path) -> bool:
        """Validate that a skill has required structure."""
        manifest_path = skill_path / SKILL_MANIFEST
        if not manifest_path.exists():
            return False
            
        try:
            content = manifest_path.read_text()
            skill_info = self._parse_skill_manifest(content)
            return bool(skill_info['name'] and skill_info['description'])
        except Exception:
            return False

    def _create_skill_manifest(self, skill_path: Path, name: str):
        """Create a SKILL.md manifest template."""
        manifest_content = f"""# {name}

**Description:** A custom skill for {name} functionality

**Version:** 1.0.0

**Author:** MyWork-AI User

## Dependencies

- python3
- mywork-ai

## Commands

### run

**Script:** run.py
**Usage:** mw skills run {name} run [options]

Main command to execute the skill functionality.

### help

**Script:** help.py
**Usage:** mw skills run {name} help

Show detailed help and usage information.

## Installation

This skill was created using the MyWork-AI skills framework.

## Usage Examples

```bash
mw skills run {name} run
mw skills run {name} help
```

## Configuration

Edit `config.json` to customize skill behavior.
"""
        (skill_path / SKILL_MANIFEST).write_text(manifest_content)

    def _create_skill_script(self, skill_path: Path, name: str):
        """Create basic script template."""
        script_content = f'''#!/usr/bin/env python3
"""
{name} Skill - Main Script
========================
"""

import os
import sys
from pathlib import Path

def main():
    """Main skill function."""
    print(f"🚀 Running {name} skill")
    
    # Get skill environment
    skill_path = os.environ.get('SKILL_PATH', '.')
    skill_name = os.environ.get('SKILL_NAME', '{name}')
    
    print(f"Skill path: {{skill_path}}")
    print(f"Arguments: {{sys.argv[1:]}}")
    
    # Your skill logic here
    print("✅ Skill execution completed")

if __name__ == '__main__':
    main()
'''
        (skill_path / "run.py").write_text(script_content)

        help_script = f'''#!/usr/bin/env python3
"""
{name} Skill - Help Script
========================
"""

def main():
    """Show skill help."""
    print(f"""
{name} Skill Help
{'=' * (len(name) + 11)}

This skill provides {name} functionality.

Commands:
  run    - Execute main skill functionality
  help   - Show this help message

Examples:
  mw skills run {name} run
  mw skills run {name} help

For more information, see the SKILL.md file.
""")

if __name__ == '__main__':
    main()
'''
        (skill_path / "help.py").write_text(help_script)

    def _create_skill_config(self, skill_path: Path, name: str):
        """Create skill.json configuration file."""
        config = {
            "name": name,
            "enabled": True,
            "settings": {
                "debug": False,
                "timeout": 300
            }
        }
        (skill_path / SKILL_CONFIG).write_text(json.dumps(config, indent=2))


def main():
    """CLI interface for skill manager."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    manager = SkillManager()
    command = sys.argv[1]
    args = sys.argv[2:]

    if command == 'list':
        skills = manager.list_skills()
        if not skills:
            print("No skills installed. Create one with: mw skills create <name>")
            return 0
            
        print("\n📦 Installed Skills:")
        print("=" * 50)
        for skill in skills:
            commands = list(skill['commands'].keys())
            print(f"• {skill['name']} v{skill['version']}")
            print(f"  {skill['description']}")
            if commands:
                print(f"  Commands: {', '.join(commands)}")
            print()

    elif command == 'install':
        if not args:
            print("Usage: mw skills install <url> [name]")
            return 1
        url = args[0]
        name = args[1] if len(args) > 1 else None
        return 0 if manager.install_skill(url, name) else 1

    elif command == 'create':
        if not args:
            print("Usage: mw skills create <name>")
            return 1
        return 0 if manager.create_skill(args[0]) else 1

    elif command == 'remove':
        if not args:
            print("Usage: mw skills remove <name>")
            return 1
        return 0 if manager.remove_skill(args[0]) else 1

    elif command == 'run':
        if len(args) < 2:
            print("Usage: mw skills run <skill-name> <command> [args...]")
            return 1
        skill_name = args[0]
        cmd = args[1]
        cmd_args = args[2:] if len(args) > 2 else []
        return manager.run_skill_command(skill_name, cmd, cmd_args)

    elif command == 'info':
        if not args:
            print("Usage: mw skills info <name>")
            return 1
        return 0 if manager.show_skill_info(args[0]) else 1

    else:
        print(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())