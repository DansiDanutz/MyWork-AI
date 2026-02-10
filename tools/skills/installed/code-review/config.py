#!/usr/bin/env python3
"""
Code Review Skill - Configuration
================================
Configure code review rules and preferences.
"""

import os
import json
from pathlib import Path

def main():
    """Configure code review settings."""
    skill_path = Path(os.environ.get('SKILL_PATH', '.'))
    config_path = skill_path / 'config.json'
    
    # Default configuration
    default_config = {
        "enabled_checks": [
            "security",
            "performance",
            "style", 
            "documentation",
            "complexity"
        ],
        "file_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c"],
        "ignore_patterns": ["*/node_modules/*", "*/.git/*", "*/venv/*", "*/__pycache__/*"],
        "severity_levels": ["low", "medium", "high", "critical"],
        "max_line_length": 120,
        "max_function_length": 50,
        "max_complexity": 10
    }
    
    if config_path.exists():
        print("📋 Current Configuration:")
        print("=" * 50)
        with open(config_path) as f:
            current_config = json.load(f)
        print(json.dumps(current_config, indent=2))
    else:
        print("📋 Creating default configuration...")
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Configuration created at: {config_path}")
    
    print(f"\n💡 Edit {config_path} to customize settings")
    return 0

if __name__ == '__main__':
    exit(main())