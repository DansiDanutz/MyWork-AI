#!/usr/bin/env python3
"""
MyWork Agent Engine
===================
Nanobot-inspired AI agent system. Define agents in YAML, run them instantly.
Supports multiple LLM providers via LiteLLM, tool calling, MCP servers,
and a built-in chat interface.

Usage:
    mw agent run agent.yaml          # Run agent with CLI chat
    mw agent run agent.yaml --web    # Run with web UI
    mw agent init my-agent           # Create agent from template
    mw agent list                    # List available agents
    mw agent validate agent.yaml     # Validate agent config
    mw agent export agent.yaml       # Package agent for marketplace

Agent YAML format:
    name: My Agent
    model: gpt-4.1
    description: A helpful assistant
    instructions: |
      You are a helpful assistant that...
    temperature: 0.7
    tools:
      - name: web_search
        description: Search the web
        parameters:
          query: {type: string, description: Search query}
        command: "curl -s 'https://api.search.com?q={query}'"
      - name: read_file
        description: Read a file
        parameters:
          path: {type: string, description: File path}
        command: "cat {path}"
    mcpServers:
      - url: https://example.com/mcp
        headers:
          Authorization: "Bearer ${MY_TOKEN}"
"""

import json
import os
import sys
import subprocess
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Lazy imports for optional deps
yaml = None
litellm = None


def _ensure_yaml():
    global yaml
    if yaml is None:
        try:
            import yaml as _yaml
            yaml = _yaml
        except ImportError:
            print("❌ PyYAML required. Install: pip install mywork-ai[agent]")
            sys.exit(1)


def _ensure_litellm():
    global litellm
    if litellm is None:
        try:
            import litellm as _litellm
            litellm = _litellm
            litellm.drop_params = True  # Don't error on unsupported params
        except ImportError:
            print("❌ LiteLLM required. Install: pip install mywork-ai[agent]")
            sys.exit(1)


# ─── Agent Config ────────────────────────────────────────────────────────────

DEFAULT_AGENT = {
    "name": "MyWork Agent",
    "model": "gpt-4.1-mini",
    "description": "A helpful AI assistant",
    "instructions": "You are a helpful AI assistant.",
    "temperature": 0.7,
    "max_tokens": 4096,
    "tools": [],
    "mcpServers": [],
}

AGENT_TEMPLATE = """# MyWork Agent Configuration
# Docs: https://github.com/DansiDanutz/MyWork-AI#agents

name: {name}
description: {description}
model: gpt-4.1-mini  # or: claude-sonnet-4-20250514, deepseek/deepseek-chat, ollama/llama3
temperature: 0.7
max_tokens: 4096

instructions: |
  You are a helpful AI assistant named {name}.
  Be concise, accurate, and helpful.

# Tools the agent can call (shell commands with parameter substitution)
tools:
  - name: web_search
    description: Search the web for information
    parameters:
      query: {{type: string, description: "Search query"}}
    command: "curl -s 'https://html.duckduckgo.com/html/?q={{query}}' | head -100"

  - name: read_file
    description: Read contents of a file
    parameters:
      path: {{type: string, description: "File path to read"}}
    command: "cat '{{path}}'"

  - name: list_files
    description: List files in a directory
    parameters:
      dir: {{type: string, description: "Directory path", default: "."}}
    command: "ls -la '{{dir}}'"

  - name: run_command
    description: Run a shell command
    parameters:
      cmd: {{type: string, description: "Shell command to execute"}}
    command: "{{cmd}}"

# MCP Servers (optional)
# mcpServers:
#   - url: https://example.com/mcp
#     headers:
#       Authorization: "Bearer ${{MY_TOKEN}}"
"""


def load_agent_config(path: str) -> Dict[str, Any]:
    """Load and validate agent YAML config."""
    _ensure_yaml()
    p = Path(path)

    if p.is_dir():
        # Directory-based config (like nanobot)
        main_file = p / "agents" / "main.md"
        if main_file.exists():
            return _load_markdown_agent(main_file)
        # Fallback to agent.yaml in dir
        yaml_file = p / "agent.yaml"
        if not yaml_file.exists():
            yaml_file = p / "nanobot.yaml"
        if not yaml_file.exists():
            print(f"❌ No agent config found in {p}")
            sys.exit(1)
        p = yaml_file

    if p.suffix == ".md":
        return _load_markdown_agent(p)

    with open(p) as f:
        config = yaml.safe_load(f) or {}

    # Support nanobot-style nested agents
    if "agents" in config and isinstance(config["agents"], dict):
        # Pick first agent or "main"
        agents = config["agents"]
        agent_key = "main" if "main" in agents else list(agents.keys())[0]
        agent_config = agents[agent_key]
        agent_config.setdefault("name", agent_key)
        # Merge top-level mcpServers
        if "mcpServers" in config:
            agent_config.setdefault("mcpServers", [])
            mcp_defs = config["mcpServers"]
            if isinstance(mcp_defs, dict):
                for name, server in mcp_defs.items():
                    server["name"] = name
                    agent_config["mcpServers"].append(server)
        config = agent_config

    # Apply defaults
    for key, default in DEFAULT_AGENT.items():
        config.setdefault(key, default)

    # Resolve env vars in config
    config = _resolve_env_vars(config)

    return config


def _load_markdown_agent(path: Path) -> Dict[str, Any]:
    """Load agent from .md file with YAML front-matter (nanobot directory format)."""
    _ensure_yaml()
    content = path.read_text()

    if not content.startswith("---"):
        return {**DEFAULT_AGENT, "instructions": content, "name": path.stem}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {**DEFAULT_AGENT, "instructions": content, "name": path.stem}

    front_matter = yaml.safe_load(parts[1]) or {}
    instructions = parts[2].strip()

    config = {**DEFAULT_AGENT, **front_matter, "instructions": instructions}
    config.setdefault("name", path.stem)
    return _resolve_env_vars(config)


def _resolve_env_vars(obj):
    """Resolve ${ENV_VAR} patterns in config values."""
    if isinstance(obj, str):
        def replace_env(match):
            var = match.group(1)
            return os.environ.get(var, match.group(0))
        return re.sub(r'\$\{(\w+)\}', replace_env, obj)
    elif isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(v) for v in obj]
    return obj


def validate_agent_config(config: Dict[str, Any]) -> List[str]:
    """Validate agent config, return list of issues."""
    issues = []
    if not config.get("name"):
        issues.append("Missing 'name'")
    if not config.get("model"):
        issues.append("Missing 'model'")
    if not config.get("instructions"):
        issues.append("Missing 'instructions'")
    for i, tool in enumerate(config.get("tools", [])):
        if not tool.get("name"):
            issues.append(f"Tool {i}: missing 'name'")
        if not tool.get("command") and not tool.get("function"):
            issues.append(f"Tool {i} ({tool.get('name', '?')}): missing 'command' or 'function'")
    return issues


# ─── Tool Execution ──────────────────────────────────────────────────────────

def _build_tool_definitions(tools: List[Dict]) -> List[Dict]:
    """Convert agent tool configs to OpenAI function-calling format."""
    definitions = []
    for tool in tools:
        params = tool.get("parameters", {})
        properties = {}
        required = []
        for param_name, param_def in params.items():
            if isinstance(param_def, dict):
                properties[param_name] = {
                    "type": param_def.get("type", "string"),
                    "description": param_def.get("description", param_name),
                }
                if "default" not in param_def:
                    required.append(param_name)
            else:
                properties[param_name] = {"type": "string", "description": str(param_def)}
                required.append(param_name)

        definitions.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", tool["name"]),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })
    return definitions


def _execute_tool(tool_config: Dict, arguments: Dict[str, Any]) -> str:
    """Execute a tool command with parameter substitution."""
    command = tool_config.get("command", "")

    # Substitute parameters
    for key, value in arguments.items():
        command = command.replace(f"{{{key}}}", str(value))

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output[:10000]  # Cap output
    except subprocess.TimeoutExpired:
        return "[Error: Command timed out after 30s]"
    except Exception as e:
        return f"[Error: {e}]"


# ─── Chat Engine ─────────────────────────────────────────────────────────────

class AgentChat:
    """Interactive chat session with an agent."""

    def __init__(self, config: Dict[str, Any]):
        _ensure_litellm()
        self.config = config
        self.model = config["model"]
        self.messages: List[Dict] = [
            {"role": "system", "content": config["instructions"]}
        ]
        self.tools_config = {t["name"]: t for t in config.get("tools", [])}
        self.tool_definitions = _build_tool_definitions(config.get("tools", []))
        self.total_tokens = 0
        self.total_cost = 0.0

    def chat(self, user_message: str) -> str:
        """Send a message and get a response, handling tool calls."""
        self.messages.append({"role": "user", "content": user_message})

        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }

        if self.tool_definitions:
            kwargs["tools"] = self.tool_definitions
            kwargs["tool_choice"] = "auto"

        max_iterations = 10  # Prevent infinite tool loops
        for _ in range(max_iterations):
            try:
                response = litellm.completion(**kwargs)
            except Exception as e:
                error_msg = f"[LLM Error: {e}]"
                self.messages.append({"role": "assistant", "content": error_msg})
                return error_msg

            choice = response.choices[0]
            message = choice.message

            # Track usage
            if hasattr(response, "usage") and response.usage:
                self.total_tokens += getattr(response.usage, "total_tokens", 0)

            # If no tool calls, return the response
            if not getattr(message, "tool_calls", None):
                content = message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                return content

            # Handle tool calls
            self.messages.append(message.model_dump())

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                if fn_name in self.tools_config:
                    result = _execute_tool(self.tools_config[fn_name], fn_args)
                else:
                    result = f"[Unknown tool: {fn_name}]"

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Continue loop to get LLM's response after tool execution
            kwargs["messages"] = self.messages

        return "[Max tool iterations reached]"


# ─── CLI Interface ───────────────────────────────────────────────────────────

def run_cli_chat(config: Dict[str, Any]):
    """Run interactive CLI chat with the agent."""
    agent = AgentChat(config)

    print(f"\n{'─' * 60}")
    print(f"  🤖 {config['name']}")
    print(f"  {config.get('description', '')}")
    print(f"  Model: {config['model']}")
    tools = config.get("tools", [])
    if tools:
        print(f"  Tools: {', '.join(t['name'] for t in tools)}")
    print(f"{'─' * 60}")
    print("  Type 'quit' to exit, 'clear' to reset, 'info' for stats\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("👋 Goodbye!")
            break

        if user_input.lower() == "clear":
            agent.messages = [agent.messages[0]]  # Keep system prompt
            print("🧹 Conversation cleared.\n")
            continue

        if user_input.lower() == "info":
            print(f"  📊 Tokens used: {agent.total_tokens:,}")
            print(f"  💬 Messages: {len(agent.messages)}")
            print(f"  🔧 Tools: {len(agent.tools_config)}\n")
            continue

        response = agent.chat(user_input)
        print(f"\n🤖: {response}\n")


def run_web_chat(config: Dict[str, Any], port: int = 8080):
    """Run web UI chat with the agent."""
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse, JSONResponse
        import uvicorn
    except ImportError:
        print("❌ Web UI requires: pip install mywork-ai[api,agent]")
        sys.exit(1)

    app = FastAPI(title=config["name"])
    agent = AgentChat(config)

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return _web_ui_html(config)

    @app.post("/chat")
    async def chat(data: dict):
        message = data.get("message", "")
        if not message:
            return JSONResponse({"error": "Empty message"}, status_code=400)
        response = agent.chat(message)
        return {"response": response, "tokens": agent.total_tokens}

    @app.post("/clear")
    async def clear():
        agent.messages = [agent.messages[0]]
        return {"status": "cleared"}

    @app.get("/info")
    async def info():
        return {
            "name": config["name"],
            "model": config["model"],
            "tools": [t["name"] for t in config.get("tools", [])],
            "tokens": agent.total_tokens,
            "messages": len(agent.messages),
        }

    print(f"\n🌐 {config['name']} running at http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def _web_ui_html(config: Dict[str, Any]) -> str:
    """Generate a clean chat UI."""
    name = config.get("name", "MyWork Agent")
    desc = config.get("description", "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;height:100vh;display:flex;flex-direction:column}}
header{{background:#1e293b;border-bottom:1px solid #334155;padding:16px 24px;display:flex;align-items:center;gap:12px}}
header h1{{font-size:18px;font-weight:600}} header p{{font-size:13px;color:#94a3b8}}
.chat{{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}}
.msg{{max-width:80%;padding:12px 16px;border-radius:16px;font-size:14px;line-height:1.6;white-space:pre-wrap}}
.msg.user{{background:#3b82f6;color:white;align-self:flex-end;border-bottom-right-radius:4px}}
.msg.bot{{background:#1e293b;border:1px solid #334155;align-self:flex-start;border-bottom-left-radius:4px}}
.msg.bot .thinking{{color:#94a3b8;font-style:italic;font-size:12px}}
.input-area{{background:#1e293b;border-top:1px solid #334155;padding:16px 24px;display:flex;gap:12px}}
input{{flex:1;background:#0f172a;border:1px solid #334155;border-radius:12px;padding:12px 16px;color:#e2e8f0;font-size:14px;outline:none}}
input:focus{{border-color:#3b82f6}}
button{{background:#3b82f6;color:white;border:none;border-radius:12px;padding:12px 24px;font-size:14px;cursor:pointer;font-weight:500}}
button:hover{{background:#2563eb}} button:disabled{{opacity:.5;cursor:not-allowed}}
.typing{{display:none;align-self:flex-start;padding:12px 16px;background:#1e293b;border:1px solid #334155;border-radius:16px;border-bottom-left-radius:4px}}
.typing.show{{display:block}}
.typing span{{display:inline-block;width:8px;height:8px;background:#64748b;border-radius:50%;margin:0 2px;animation:bounce .6s infinite alternate}}
.typing span:nth-child(2){{animation-delay:.2s}} .typing span:nth-child(3){{animation-delay:.4s}}
@keyframes bounce{{to{{transform:translateY(-6px);opacity:.3}}}}
</style>
</head>
<body>
<header>
<div style="width:40px;height:40px;background:#3b82f6;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px">🤖</div>
<div><h1>{name}</h1><p>{desc}</p></div>
</header>
<div class="chat" id="chat"></div>
<div class="typing" id="typing"><span></span><span></span><span></span></div>
<div class="input-area">
<input id="input" placeholder="Type a message..." autocomplete="off">
<button id="send" onclick="send()">Send</button>
</div>
<script>
const chat=document.getElementById('chat'),input=document.getElementById('input'),typing=document.getElementById('typing'),btn=document.getElementById('send');
function addMsg(text,role){{const d=document.createElement('div');d.className='msg '+role;d.textContent=text;chat.appendChild(d);chat.scrollTop=chat.scrollHeight}}
async function send(){{const m=input.value.trim();if(!m)return;input.value='';btn.disabled=true;addMsg(m,'user');typing.classList.add('show');
try{{const r=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:m}})}});const d=await r.json();addMsg(d.response||d.error,'bot')}}
catch(e){{addMsg('Connection error','bot')}}finally{{typing.classList.remove('show');btn.disabled=false;input.focus()}}}}
input.addEventListener('keydown',e=>{{if(e.key==='Enter'&&!e.shiftKey){{e.preventDefault();send()}}}});
input.focus();
</script>
</body></html>"""


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_agent(args: List[str]) -> int:
    """Main entry point for `mw agent` commands."""
    if not args:
        _print_help()
        return 0

    subcmd = args[0]
    rest = args[1:]

    if subcmd == "run":
        return _cmd_run(rest)
    elif subcmd == "init":
        return _cmd_init(rest)
    elif subcmd == "list":
        return _cmd_list(rest)
    elif subcmd == "validate":
        return _cmd_validate(rest)
    elif subcmd == "export":
        return _cmd_export(rest)
    elif subcmd == "info":
        return _cmd_info(rest)
    else:
        print(f"❌ Unknown command: agent {subcmd}")
        _print_help()
        return 1


def _cmd_run(args: List[str]) -> int:
    """Run an agent from YAML config."""
    if not args:
        print("Usage: mw agent run <agent.yaml> [--web] [--port 8080]")
        return 1

    config_path = args[0]
    web_mode = "--web" in args
    port = 8080
    if "--port" in args:
        idx = args.index("--port")
        if idx + 1 < len(args):
            port = int(args[idx + 1])

    if not os.path.exists(config_path):
        print(f"❌ File not found: {config_path}")
        return 1

    config = load_agent_config(config_path)
    issues = validate_agent_config(config)
    if issues:
        print(f"⚠️  Config warnings: {', '.join(issues)}")

    if web_mode:
        run_web_chat(config, port)
    else:
        run_cli_chat(config)
    return 0


def _cmd_init(args: List[str]) -> int:
    """Create a new agent from template."""
    _ensure_yaml()
    name = args[0] if args else "my-agent"
    safe_name = name.replace(" ", "-").lower()
    filename = f"{safe_name}.yaml"

    if os.path.exists(filename):
        print(f"❌ {filename} already exists")
        return 1

    desc = " ".join(args[1:]) if len(args) > 1 else "A helpful AI assistant"

    content = AGENT_TEMPLATE.format(name=name, description=desc)
    with open(filename, "w") as f:
        f.write(content)

    print(f"✅ Created {filename}")
    print(f"   Edit it, then run: mw agent run {filename}")
    return 0


def _cmd_list(args: List[str]) -> int:
    """List agent configs in current directory."""
    _ensure_yaml()
    found = []
    for p in Path(".").rglob("*.yaml"):
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and ("agents" in data or "instructions" in data or "model" in data):
                name = data.get("name", data.get("agents", {}).get("main", {}).get("name", p.stem))
                model = data.get("model", "?")
                found.append((str(p), name, model))
        except Exception:
            pass

    for p in Path(".").rglob("*.md"):
        if p.parent.name == "agents":
            content = p.read_text()
            if content.startswith("---"):
                found.append((str(p), p.stem, "md-agent"))

    if not found:
        print("No agent configs found in current directory.")
        print("Create one: mw agent init my-agent")
        return 0

    print(f"\n🤖 Found {len(found)} agent(s):\n")
    for path, name, model in found:
        print(f"  {name:<30} {model:<25} {path}")
    return 0


def _cmd_validate(args: List[str]) -> int:
    """Validate agent config."""
    if not args:
        print("Usage: mw agent validate <agent.yaml>")
        return 1

    config = load_agent_config(args[0])
    issues = validate_agent_config(config)

    if issues:
        print(f"❌ {len(issues)} issue(s):")
        for issue in issues:
            print(f"   • {issue}")
        return 1

    tools = config.get("tools", [])
    print(f"✅ Valid agent config")
    print(f"   Name: {config['name']}")
    print(f"   Model: {config['model']}")
    print(f"   Tools: {len(tools)}")
    print(f"   Instructions: {len(config.get('instructions', ''))} chars")
    return 0


def _cmd_info(args: List[str]) -> int:
    """Show detailed info about an agent."""
    if not args:
        print("Usage: mw agent info <agent.yaml>")
        return 1

    config = load_agent_config(args[0])
    tools = config.get("tools", [])

    print(f"\n🤖 {config['name']}")
    print(f"{'─' * 50}")
    print(f"  Model:        {config['model']}")
    print(f"  Temperature:  {config.get('temperature', 0.7)}")
    print(f"  Max tokens:   {config.get('max_tokens', 4096)}")
    print(f"  Description:  {config.get('description', '-')}")
    print(f"  Instructions: {len(config.get('instructions', ''))} chars")

    if tools:
        print(f"\n  🔧 Tools ({len(tools)}):")
        for t in tools:
            params = list(t.get("parameters", {}).keys())
            print(f"     {t['name']:<20} {t.get('description', '')[:40]}")
            if params:
                print(f"     {'':20} params: {', '.join(params)}")

    mcp = config.get("mcpServers", [])
    if mcp:
        print(f"\n  🔌 MCP Servers ({len(mcp)}):")
        for s in mcp:
            print(f"     {s.get('name', s.get('url', '?'))}")

    return 0


def _cmd_export(args: List[str]) -> int:
    """Package agent for marketplace."""
    if not args:
        print("Usage: mw agent export <agent.yaml>")
        return 1

    config = load_agent_config(args[0])
    safe_name = config["name"].lower().replace(" ", "-")
    export_dir = Path(f"export-{safe_name}")
    export_dir.mkdir(exist_ok=True)

    # Copy agent file
    import shutil
    shutil.copy2(args[0], export_dir / "agent.yaml")

    # Generate README
    tools = config.get("tools", [])
    readme = f"""# {config['name']}

{config.get('description', '')}

## Quick Start

```bash
pip install mywork-ai[agent]
mw agent run agent.yaml
```

## Configuration

- **Model:** {config['model']}
- **Tools:** {', '.join(t['name'] for t in tools) if tools else 'None'}

## Web UI

```bash
mw agent run agent.yaml --web
# Open http://localhost:8080
```
"""
    (export_dir / "README.md").write_text(readme)
    (export_dir / "LICENSE").write_text("MIT License\n\nCopyright (c) 2026\n")

    print(f"✅ Exported to {export_dir}/")
    print(f"   Ready for: mw marketplace publish {export_dir}")
    return 0


def _print_help():
    print("""
🤖 MyWork Agent Engine
━━━━━━━━━━━━━━━━━━━━━

  mw agent run <config>        Run agent (CLI chat)
  mw agent run <config> --web  Run agent (Web UI on :8080)
  mw agent init <name>         Create agent from template
  mw agent list                List agents in current dir
  mw agent validate <config>   Validate agent config
  mw agent info <config>       Show agent details
  mw agent export <config>     Package for marketplace

Supports: OpenAI, Anthropic, Google, Ollama, DeepSeek, Mistral, 100+ more
Config:   YAML files or directory-based (.md agents)
""")


if __name__ == "__main__":
    sys.exit(cmd_agent(sys.argv[1:]))
