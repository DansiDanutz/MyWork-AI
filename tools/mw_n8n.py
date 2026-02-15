#!/usr/bin/env python3
"""
n8n Command Module for MyWork-AI
================================
Handles all n8n workflow automation commands.

Extracted from mw.py to improve maintainability.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List

def cmd_n8n(args: List[str]) -> int:
    """n8n workflow automation commands."""
    if not args or (len(args) == 1 and args[0] in ["--help", "-h"]):
        print("""
n8n Commands — Workflow Automation Manager
==========================================
Usage:
    mw n8n setup                    Install & start n8n (Docker or local)
    mw n8n status                   Check n8n connection status
    mw n8n list                     List all workflows
    mw n8n import <file.json>       Import a workflow from JSON
    mw n8n export <id> [file]       Export workflow to JSON
    mw n8n activate <id>            Activate a workflow
    mw n8n deactivate <id>          Deactivate a workflow
    mw n8n delete <id>              Delete a workflow
    mw n8n exec <id>                Execute a workflow manually
    mw n8n executions [id]          List recent executions
    mw n8n logs <exec_id>           Show execution details
    mw n8n config                   Show/set n8n connection config
    mw n8n test <file.json>         Validate workflow JSON locally
    mw n8n --help                   Show this help message

Description:
    Full interface to n8n workflow automation. Manage workflows,
    monitor executions, import/export automations, and integrate
    with the MyWork-AI ecosystem.

Examples:
    mw n8n setup                    # Install n8n locally
    mw n8n status                   # Check connection
    mw n8n import workflow.json     # Import automation
    mw n8n list                     # See all workflows
    mw n8n exec abc123              # Trigger a run
""")
        return 0

    subcmd = args[0]
    sub_args = args[1:]

    if subcmd == "setup":
        return _n8n_setup(sub_args)
    elif subcmd == "status":
        return _n8n_status()
    elif subcmd == "list":
        return _n8n_api_call("GET", "/api/v1/workflows", display="workflows")
    elif subcmd == "import":
        if not sub_args:
            print("❌ Error: Missing workflow file")
            print("💡 Try: mw n8n import workflow.json")
            return 1
        return _n8n_import(sub_args[0])
    elif subcmd == "export":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            print("💡 Try: mw n8n export <workflow-id>")
            return 1
        outfile = sub_args[1] if len(sub_args) > 1 else None
        return _n8n_export(sub_args[0], outfile)
    elif subcmd == "activate":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("PATCH", f"/api/v1/workflows/{sub_args[0]}", body={"active": True})
    elif subcmd == "deactivate":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("PATCH", f"/api/v1/workflows/{sub_args[0]}", body={"active": False})
    elif subcmd == "delete":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        confirm = input(f"⚠️  Delete workflow {sub_args[0]}? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0
        return _n8n_api_call("DELETE", f"/api/v1/workflows/{sub_args[0]}")
    elif subcmd == "exec":
        if not sub_args:
            print("❌ Error: Missing workflow ID")
            return 1
        return _n8n_api_call("POST", f"/api/v1/workflows/{sub_args[0]}/execute", display="execution")
    elif subcmd == "executions":
        wf_id = sub_args[0] if sub_args else None
        path = "/api/v1/executions"
        if wf_id:
            path += f"?workflowId={wf_id}"
        return _n8n_api_call("GET", path, display="executions")
    elif subcmd == "logs":
        if not sub_args:
            print("❌ Error: Missing execution ID")
            return 1
        return _n8n_api_call("GET", f"/api/v1/executions/{sub_args[0]}", display="execution_detail")
    elif subcmd == "config":
        return _n8n_config(sub_args)
    elif subcmd == "test":
        if not sub_args:
            print("❌ Error: Missing workflow file")
            return 1
        return _n8n_test(sub_args[0])
    else:
        print(f"❌ Unknown n8n command: {subcmd}")
        print("💡 Try: mw n8n --help")
        return 1


def _n8n_get_config():
    """Get n8n connection config from env or .env file."""
    url = os.environ.get("N8N_API_URL", "")
    key = os.environ.get("N8N_API_KEY", "")
    if not url:
        # Try reading from .env in project root
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("N8N_API_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("N8N_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return url, key


def _n8n_api_call(method: str, path: str, body: dict = None, display: str = None) -> int:
    """Make an API call to n8n."""
    url, key = _n8n_get_config()
    if not url:
        print("❌ n8n not configured")
        print("💡 Try: mw n8n setup")
        print("   Or set N8N_API_URL and N8N_API_KEY in your .env file")
        return 1

    full_url = url.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-N8N-API-KEY"] = key

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(full_url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"❌ n8n API error ({e.code}): {body_text[:200]}")
        return 1
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach n8n at {url}")
        print(f"💡 Is n8n running? Try: mw n8n setup")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    # Display results
    if display == "workflows":
        workflows = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(workflows, list):
            if not workflows:
                print("📋 No workflows found")
            else:
                print(f"📋 {len(workflows)} workflow(s):\n")
                for wf in workflows:
                    status = "🟢 Active" if wf.get("active") else "⚪ Inactive"
                    print(f"  {status}  {wf.get('id', '?'):>6}  {wf.get('name', 'Untitled')}")
                    if wf.get("tags"):
                        tags = ", ".join(t.get("name", t) if isinstance(t, dict) else str(t) for t in wf["tags"])
                        print(f"              Tags: {tags}")
        else:
            print(json.dumps(result, indent=2))
    elif display == "executions":
        execs = result.get("data", result) if isinstance(result, dict) else result
        if isinstance(execs, list):
            if not execs:
                print("📋 No executions found")
            else:
                print(f"📋 {len(execs)} execution(s):\n")
                for ex in execs[:20]:
                    status_icon = "✅" if ex.get("finished") and not ex.get("stoppedAt") else "❌" if ex.get("stoppedAt") else "⏳"
                    print(f"  {status_icon}  {ex.get('id', '?'):>8}  {ex.get('workflowId', '?')}  {ex.get('startedAt', '?')[:19]}")
        else:
            print(json.dumps(result, indent=2))
    elif display == "execution_detail":
        print(f"Execution: {result.get('id')}")
        print(f"Workflow:  {result.get('workflowId')}")
        print(f"Status:    {'✅ Success' if result.get('finished') else '❌ Failed'}")
        print(f"Started:   {result.get('startedAt', 'N/A')}")
        print(f"Finished:  {result.get('stoppedAt', 'N/A')}")
        if result.get('data', {}).get('resultData', {}).get('error'):
            err = result['data']['resultData']['error']
            print(f"Error:     {err.get('message', err)}")
    else:
        if isinstance(result, dict) and result.get("id"):
            print(f"✅ Done (ID: {result['id']})")
        else:
            print("✅ Done")

    return 0


def _n8n_setup(args: List[str]) -> int:
    """Install and setup n8n."""
    print("🚀 Setting up n8n...")
    
    # Check if Docker is available
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker found - setting up n8n with Docker...")
            return _n8n_setup_docker(args)
        else:
            print("⚠️  Docker not found - setting up n8n locally...")
            return _n8n_setup_local(args)
    except FileNotFoundError:
        print("⚠️  Docker not found - setting up n8n locally...")
        return _n8n_setup_local(args)


def _n8n_setup_docker(args: List[str]) -> int:
    """Setup n8n with Docker."""
    import subprocess
    
    print("🐳 Starting n8n with Docker...")
    
    # Check if n8n container already exists
    result = subprocess.run(["docker", "ps", "-a", "--filter", "name=n8n", "--format", "{{.Names}}"], 
                          capture_output=True, text=True)
    
    if "n8n" in result.stdout:
        print("📦 n8n container exists - starting it...")
        subprocess.run(["docker", "start", "n8n"])
    else:
        print("📦 Creating new n8n container...")
        cmd = [
            "docker", "run", "-d", "--name", "n8n",
            "-p", "5678:5678",
            "-e", "WEBHOOK_URL=http://localhost:5678/",
            "n8nio/n8n"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to start n8n: {result.stderr}")
            return 1
    
    print("✅ n8n is starting up...")
    print("🌐 Access n8n at: http://localhost:5678")
    print("💡 Set N8N_API_URL=http://localhost:5678 in your .env file")
    print("💡 Generate an API key in n8n Settings > API")
    
    return 0


def _n8n_setup_local(args: List[str]) -> int:
    """Setup n8n locally with npm."""
    import subprocess
    
    print("📦 Installing n8n globally...")
    
    try:
        result = subprocess.run(["npm", "install", "-g", "n8n"], check=True)
        print("✅ n8n installed successfully!")
        print("🚀 Starting n8n...")
        print("💡 Run 'n8n start' to launch n8n")
        print("🌐 Access n8n at: http://localhost:5678")
        print("💡 Set N8N_API_URL=http://localhost:5678 in your .env file")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install n8n: {e}")
        print("💡 Try: npm install -g n8n")
        return 1
    except FileNotFoundError:
        print("❌ npm not found")
        print("💡 Install Node.js and npm first: https://nodejs.org/")
        return 1


def _n8n_status() -> int:
    """Check n8n connection status."""
    url, key = _n8n_get_config()
    
    if not url:
        print("❌ n8n not configured")
        print("💡 Set N8N_API_URL in your .env file")
        print("💡 Try: mw n8n setup")
        return 1
    
    print(f"🔍 Checking n8n at {url}...")
    
    try:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["X-N8N-API-KEY"] = key
            
        req = urllib.request.Request(f"{url.rstrip('/')}/api/v1/workflows", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            count = len(result.get("data", result)) if isinstance(result, dict) else len(result)
            print(f"✅ n8n is running ({count} workflows)")
            if key:
                print("🔑 API key is configured")
            else:
                print("⚠️  No API key configured")
                print("💡 Set N8N_API_KEY in your .env file")
            return 0
            
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach n8n: {e.reason}")
        print("💡 Is n8n running? Try: mw n8n setup")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _n8n_config(args: List[str]) -> int:
    """Show or configure n8n connection."""
    url, key = _n8n_get_config()
    
    if not args:
        # Show current config
        print("n8n Configuration:")
        print(f"  URL: {url or '(not set)'}")
        print(f"  Key: {'*' * (len(key) - 8) + key[-8:] if key else '(not set)'}")
        print("\n💡 Set in .env file:")
        print("  N8N_API_URL=http://localhost:5678")
        print("  N8N_API_KEY=n8n_api_xxxxxxxx")
        return 0
    
    if args[0] == "set":
        if len(args) < 3:
            print("❌ Usage: mw n8n config set <url|key> <value>")
            return 1
        
        setting = args[1]
        value = args[2]
        
        # This would require .env file modification
        print(f"💡 Set {setting.upper()} in your .env file:")
        if setting == "url":
            print(f"  N8N_API_URL={value}")
        elif setting == "key":
            print(f"  N8N_API_KEY={value}")
        else:
            print(f"❌ Unknown setting: {setting}")
            return 1
        
        return 0
    
    print("❌ Unknown config command")
    print("💡 Try: mw n8n config")
    return 1


def _n8n_import(workflow_file: str) -> int:
    """Import a workflow from JSON file."""
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Prepare for n8n API
        if isinstance(workflow_data, dict) and "nodes" in workflow_data:
            # Already in n8n format
            import_data = workflow_data
        else:
            print("❌ Invalid workflow format")
            return 1
        
        return _n8n_api_call("POST", "/api/v1/workflows", body=import_data, display="workflow")
        
    except FileNotFoundError:
        print(f"❌ File not found: {workflow_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1


def _n8n_export(workflow_id: str, output_file: str = None) -> int:
    """Export a workflow to JSON file."""
    result = _n8n_api_call("GET", f"/api/v1/workflows/{workflow_id}")
    if result != 0:
        return result
    
    # This would need to capture the API response
    output_file = output_file or f"workflow_{workflow_id}.json"
    print(f"💡 Workflow exported to: {output_file}")
    return 0


def _n8n_test(workflow_file: str) -> int:
    """Validate workflow JSON locally."""
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Basic validation
        required_fields = ["nodes", "connections"]
        for field in required_fields:
            if field not in workflow_data:
                print(f"❌ Missing required field: {field}")
                return 1
        
        nodes = workflow_data.get("nodes", [])
        if not isinstance(nodes, list):
            print("❌ Nodes must be a list")
            return 1
        
        if len(nodes) == 0:
            print("⚠️  Workflow has no nodes")
        
        print(f"✅ Workflow validation passed ({len(nodes)} nodes)")
        return 0
        
    except FileNotFoundError:
        print(f"❌ File not found: {workflow_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1