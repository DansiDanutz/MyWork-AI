#!/usr/bin/env python3
"""
Deploy Check Skill - Configuration
=================================
Configure deployment checklist rules and environment settings.
"""

import os
import json
from pathlib import Path

def main():
    """Configure deployment check settings."""
    skill_path = Path(os.environ.get('SKILL_PATH', '.'))
    config_path = skill_path / 'config.json'
    
    # Default configuration
    default_config = {
        "environments": {
            "development": {
                "strict": False,
                "ssl_required": False,
                "backup_required": False
            },
            "staging": {
                "strict": True,
                "ssl_required": True,
                "backup_required": False
            },
            "production": {
                "strict": True,
                "ssl_required": True,
                "backup_required": True,
                "monitoring_required": True
            }
        },
        "required_files": [
            "README.md",
            ".env.example", 
            "requirements.txt"
        ],
        "security_checks": True,
        "performance_checks": True,
        "documentation_checks": True,
        "git_checks": True,
        "custom_checks": []
    }
    
    if config_path.exists():
        print("📋 Current Deploy Check Configuration:")
        print("=" * 50)
        with open(config_path) as f:
            current_config = json.load(f)
        print(json.dumps(current_config, indent=2))
    else:
        print("📋 Creating default deploy check configuration...")
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Configuration created at: {config_path}")
    
    print(f"\n💡 Edit {config_path} to customize deployment checks")
    print("\nConfiguration options:")
    print("• environments: Define rules per environment")
    print("• required_files: Files that must exist")
    print("• *_checks: Enable/disable check categories")
    print("• custom_checks: Add custom validation scripts")
    
    return 0

if __name__ == '__main__':
    exit(main())