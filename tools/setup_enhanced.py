#!/usr/bin/env python3
"""
Enhanced Setup Function for MyWork-AI
=====================================
Interactive setup wizard that properly configures the user environment.
"""

import sys
import json
import platform
from datetime import datetime
from pathlib import Path

# Colors (will be imported from main mw.py)
class Colors:
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    ENDC = "\033[0m"

def get_input(prompt, default=""):
    """Get user input with optional default."""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()

def yes_no(prompt, default=True):
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} ({default_str}): ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def cmd_setup_enhanced(args=None):
    """Enhanced setup command for first-time users - interactive configuration wizard."""
    if args and (args[0] in ["--help", "-h"]):
        print("""
Setup Commands — First-Time Setup Guide
=======================================
Usage:
    mw setup                        Run first-time setup wizard
    mw setup --help                 Show this help message

Description:
    Interactive setup wizard that configures:
    • User profile and preferences
    • API keys for AI services (OpenRouter/OpenAI)
    • Default project template preferences
    • ~/.mywork/ configuration directory
    • Shell completions (optional)

The wizard creates a personalized MyWork configuration and guides you
through your first project creation.

Examples:
    mw setup                        # Run interactive setup wizard
""")
        return 0
        
    # ASCII Art Welcome
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ███╗   ███╗██╗   ██╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗          ║
║    ████╗ ████║╚██╗ ██╔╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝          ║
║    ██╔████╔██║ ╚████╔╝ ██║ █╗ ██║██║   ██║██████╔╝█████╔╝           ║
║    ██║╚██╔╝██║  ╚██╔╝  ██║███╗██║██║   ██║██╔══██╗██╔═██╗           ║
║    ██║ ╚═╝ ██║   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗          ║
║    ╚═╝     ╚═╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝          ║
║                                                                      ║
║                  Welcome to the MyWork-AI Framework!                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.BOLD}🚀 Let's set up your personalized MyWork environment!{Colors.ENDC}
""")
    
    # Python version check
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"{Colors.RED}❌ Python {python_version.major}.{python_version.minor} is too old{Colors.ENDC}")
        print(f"{Colors.RED}   MyWork requires Python 3.9 or higher{Colors.ENDC}")
        return 1
    
    print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} looks good!{Colors.ENDC}\n")
    
    # Step 1: User Profile
    print(f"{Colors.BOLD}{Colors.CYAN}👤 Step 1: User Profile{Colors.ENDC}")
    print("─" * 30)
    
    user_name = get_input("What's your name?", "Developer")
    
    # Step 2: Project preferences  
    print(f"\n{Colors.BOLD}{Colors.CYAN}🎯 Step 2: Project Preferences{Colors.ENDC}")
    print("─" * 30)
    
    print("What type of projects do you usually build? (select multiple)")
    print("1. Web APIs (FastAPI, Flask)")
    print("2. Web Apps (React, Next.js)")  
    print("3. CLI Tools")
    print("4. Data Science/ML")
    print("5. Full-stack applications")
    
    project_types = get_input("Enter numbers (e.g., 1,3,5)", "1,2").split(',')
    project_types = [t.strip() for t in project_types if t.strip()]
    
    # Step 3: API Configuration
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔑 Step 3: AI API Setup{Colors.ENDC}")
    print("─" * 30)
    print("MyWork works best with AI assistance. Let's configure your API keys.")
    
    api_key = None
    api_provider = "none"
    
    if yes_no("Do you have an OpenRouter API key?", False):
        api_key = get_input("Enter your OpenRouter API key").strip()
        if api_key:
            api_provider = "openrouter"
    elif yes_no("Do you have an OpenAI API key?", False):
        api_key = get_input("Enter your OpenAI API key").strip() 
        if api_key:
            api_provider = "openai"
    else:
        print(f"{Colors.YELLOW}⏭️  No API key provided - you can add one later in ~/.mywork/config.json{Colors.ENDC}")
    
    # Step 4: Create ~/.mywork directory and config
    print(f"\n{Colors.BOLD}{Colors.CYAN}📁 Step 4: Configuration Setup{Colors.ENDC}")
    print("─" * 30)
    
    config_dir = Path.home() / ".mywork"
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "user": {
            "name": user_name,
            "setup_date": datetime.now().isoformat(),
            "version": "2.0.0"
        },
        "preferences": {
            "project_types": project_types,
            "default_template": "basic"
        },
        "api": {
            "provider": api_provider,
            "key": api_key if api_key else ""
        },
        "completion_configured": False
    }
    
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps(config, indent=2))
    
    print(f"{Colors.GREEN}✅ Configuration saved to {config_file}{Colors.ENDC}")
    
    # Step 5: Shell completions (optional)
    print(f"\n{Colors.BOLD}{Colors.CYAN}🐚 Step 5: Shell Completions (Optional){Colors.ENDC}")
    print("─" * 30)
    
    if yes_no("Install shell completions for tab-completion?", True):
        try:
            # Import the completions command (this might fail if not available)
            import subprocess
            result = subprocess.run([sys.executable, "-c", 
                "from tools.mw import cmd_completions; cmd_completions(['install'])"], 
                capture_output=True, text=True)
            if result.returncode == 0:
                config["completion_configured"] = True
                config_file.write_text(json.dumps(config, indent=2))
                print(f"{Colors.GREEN}✅ Shell completions installed{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not auto-install completions{Colors.ENDC}")
            print(f"{Colors.BLUE}💡 You can install them later with: mw completions install{Colors.ENDC}")
    
    # Final setup complete message
    print(f"""
{Colors.BOLD}{Colors.GREEN}🎉 Setup Complete! Welcome to MyWork, {user_name}!{Colors.ENDC}

{Colors.BOLD}✨ What's next?{Colors.ENDC}
{Colors.CYAN}1. Take the interactive tour:{Colors.ENDC}
   {Colors.BOLD}mw tour{Colors.ENDC}                    # Learn key features hands-on

{Colors.CYAN}2. Create your first project:{Colors.ENDC}
   {Colors.BOLD}mw new my-app{Colors.ENDC}              # Basic project
   {Colors.BOLD}mw new api-server fastapi{Colors.ENDC}  # FastAPI project

{Colors.CYAN}3. Explore the framework:{Colors.ENDC}
   {Colors.BOLD}mw dashboard{Colors.ENDC}               # Web dashboard
   {Colors.BOLD}mw status{Colors.ENDC}                  # Health check
   
{Colors.BLUE}📖 Configuration stored in: {config_dir}/{Colors.ENDC}
{Colors.BLUE}🎯 You're ready to build! Try '{Colors.BOLD}mw tour{Colors.ENDC}{Colors.BLUE}' next{Colors.ENDC}
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(cmd_setup_enhanced(sys.argv[1:]))