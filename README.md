# MyWork Framework

> A unified AI-powered development framework combining project orchestration, autonomous coding, and workflow automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GSD Version](https://img.shields.io/badge/GSD-v1.9.10-blue.svg)](https://github.com/anthropics/claude-code)
[![n8n Integration](https://img.shields.io/badge/n8n-2709%20templates-orange.svg)](https://n8n.io)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)

---

## Overview

MyWork is a productivity framework that orchestrates multiple AI tools into a cohesive development environment:

- **GSD (Get Shit Done)** - Project lifecycle management with phased execution
- **WAT (Workflows, Agents, Tools)** - Task execution with deterministic reliability
- **Autocoder** - Long-running autonomous coding for large projects
- **n8n Integration** - Visual workflow automation with 2,709+ templates
- **Brain/Knowledge Vault** - Self-learning system that grows with experience

## Architecture

```
+-------------------------------------------------------------+
|                    MASTER ORCHESTRATOR                       |
|              (Routes requests to right layer)                |
+-------------------------------------------------------------+
                              |
        +---------------------+---------------------+
        v                     v                     v
+---------------+     +---------------+     +---------------+
|     GSD       |     |     WAT       |     |  AUTOMATION   |
|  Orchestration|     |   Execution   |     |   ENGINES     |
+---------------+     +---------------+     +---------------+
| - Planning    |     | - Workflows   |     | - Autocoder   |
| - Phases      |     | - Agents      |     | - n8n         |
| - Verification|     | - Tools       |     | - MCP Servers |
+---------------+     +---------------+     +---------------+
```

### When to Use What

| Task Type | Use | Why |
|-----------|-----|-----|
| New project from scratch | `/gsd:new-project` | Full planning, requirements, roadmap |
| Add features to existing project | `/gsd:plan-phase` | Structured phased development |
| Quick bug fix or config change | `/gsd:quick` | Fast, minimal overhead |
| Build complete app (20+ features) | Autocoder | Multi-session autonomous coding |
| Visual automation (webhooks, APIs) | n8n workflow | 2,709 templates available |
| Deterministic tasks | WAT tools | Reliable, testable Python scripts |

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Claude Code CLI](https://github.com/anthropics/claude-code)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/DansiDanutz/MyWork-AI.git
cd MyWork-AI

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Verify installation
python tools/mw.py status
```

### Your First Project

```bash
# Create a new project
python tools/mw.py new my-app fastapi

# Navigate to project
cd projects/my-app

# Initialize GSD
/gsd:new-project

# Start first phase
/gsd:plan-phase 1
/gsd:execute-phase 1
```

---

## Project Structure

```
MyWork/
+-- .planning/              # Framework-level state
|   +-- BRAIN.md            # Knowledge vault (self-learning)
|   +-- STATE.md            # Current context
|   +-- codebase/           # Codebase analysis
+-- projects/               # All projects live here
|   +-- _template/          # Project template
|   +-- [your-projects]/    # Your projects
+-- tools/                  # CLI tools
|   +-- mw.py               # Unified CLI
|   +-- auto_update.py      # Safe updates
|   +-- module_registry.py  # Code indexing (1,300+ modules)
|   +-- health_check.py     # System diagnostics
|   +-- brain.py            # Knowledge manager
|   +-- brain_learner.py    # Auto-learning engine
|   +-- scaffold.py         # Project templates
+-- workflows/              # WAT workflows (SOPs)
+-- CLAUDE.md               # Master Orchestrator instructions
+-- .env.example            # Environment template
+-- .mcp.json.example       # MCP config template
```

---

## CLI Reference

### Unified CLI (`mw`)

```bash
# Run any command
python tools/mw.py <command>
```

### Core Commands

| Command | Description |
|---------|-------------|
| `mw status` | Quick health check |
| `mw doctor` | Full system diagnostics |
| `mw search <query>` | Search module registry |
| `mw new <name> [template]` | Create new project |
| `mw scan` | Index all project modules |
| `mw update` | Check for updates |

### Project Commands

| Command | Description |
|---------|-------------|
| `mw projects` | List all projects |
| `mw open <name>` | Open in VS Code |
| `mw cd <name>` | Print cd command |

### Brain Commands

| Command | Description |
|---------|-------------|
| `mw brain search <query>` | Search knowledge vault |
| `mw brain add <content>` | Add a lesson |
| `mw brain learn` | Run daily learning |
| `mw brain learn-deep` | Weekly deep analysis |
| `mw brain stats` | Show statistics |

### Automation Commands

| Command | Description |
|---------|-------------|
| `mw ac start <project>` | Start Autocoder |
| `mw ac stop <project>` | Stop Autocoder |
| `mw ac pause <project>` | Pause Autocoder |
| `mw ac resume <project>` | Resume Autocoder |
| `mw ac status` | Check Autocoder status |
| `mw ac progress <project>` | Show Autocoder progress |
| `mw ac list` | List Autocoder projects |
| `mw n8n list` | List n8n workflows |
| `mw n8n status` | Check n8n connection |

### Autocoder Access Options

**Option 1: mw CLI (recommended)**

```bash
mw ac status
mw ac start marketplace
mw ac pause marketplace
mw ac resume marketplace
mw ac stop marketplace
mw ac ui
```

**Option 2: Explicit venv path (no activation needed)**

```bash
$AUTOCODER_ROOT/venv/bin/python $MYWORK_ROOT/tools/autocoder_api.py status
$AUTOCODER_ROOT/venv/bin/python $MYWORK_ROOT/tools/autocoder_api.py start marketplace
```

**Option 3: Activate Autocoder venv first**

```bash
cd $AUTOCODER_ROOT
source venv/bin/activate
python $MYWORK_ROOT/tools/autocoder_api.py status
```

### Autocoder Always-On (macOS)

If you want long-running autonomous coding (multi-hour sessions), install the LaunchAgent service:

```bash
mw ac service setup
mw ac service install
mw ac service status
```

This keeps the Autocoder UI available and restarts the server if it exits.

### Autocoder Troubleshooting

Common fixes if the service or UI isn't responding:

```bash
# Check service status
mw ac service status

# Restart the service
mw ac service restart

# View logs (last 50 lines)
mw ac service logs

# Follow logs live
mw ac service logs -f
```

If the server is not running, confirm:
- `AUTOCODER_ROOT` points to the correct Autocoder folder
- the Autocoder venv exists (`$AUTOCODER_ROOT/venv`)
- port `8888` is not already in use

---

## GSD Commands

| Command | Purpose |
|---------|---------|
| `/gsd:new-project` | Initialize new project with discovery and roadmap |
| `/gsd:map-codebase` | Analyze existing codebase (brownfield) |
| `/gsd:plan-phase N` | Create detailed task plans for phase N |
| `/gsd:execute-phase N` | Run plans in parallel waves |
| `/gsd:verify-work N` | User acceptance testing |
| `/gsd:progress` | Check current status |
| `/gsd:quick` | Ad-hoc tasks with GSD guarantees |
| `/gsd:pause-work` | Save context when stopping |
| `/gsd:resume-work` | Restore context for next session |

---

## Features

### Module Registry

Indexes reusable code patterns across all projects:

```bash
# Search for auth components
mw search "authentication"

# Scan all projects
mw scan
```

Currently tracking **1,300+ modules** across projects.

### Brain/Knowledge Vault

Self-learning system that captures and recalls knowledge:

```bash
# Search knowledge
mw brain search "api"

# Run auto-learning
mw brain learn

# Check stats
mw brain stats
```

### Auto-Updates

Safe dependency management with rollback support:

```bash
# Check for updates
mw update check

# Update specific component
mw update gsd

# View status
mw update status
```

### Health Monitoring

System diagnostics and auto-fix:

```bash
# Quick check
mw status

# Full diagnostics
mw doctor

# Auto-fix issues
mw fix
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional - Other LLM Providers
OPENAI_API_KEY=sk-xxxxx
OPENROUTER_API_KEY=sk-or-v1-xxxxx
GROQ_API_KEY=gsk_xxxxx

# Optional - n8n Integration
N8N_API_URL=https://your-instance.app.n8n.cloud
N8N_API_KEY=your-n8n-api-key

# Optional - GitHub
GITHUB_TOKEN=ghp_xxxxx
```

### MCP Servers

Copy `.mcp.json.example` to `.mcp.json` and configure your MCP servers.

---

## Security

**Important:** This framework handles sensitive credentials. Follow these practices:

- **Never commit `.env`** - Contains API keys
- **Never commit `.mcp.json`** - Contains server credentials
- **Use `.example` files** - Templates are safe to commit
- **Run `mw doctor`** - Checks for exposed secrets
- **Review `.gitignore`** - Comprehensive security rules

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Project Templates

Available templates for new projects:

| Template | Description |
|----------|-------------|
| `basic` | Minimal Python project |
| `fastapi` | FastAPI backend with SQLAlchemy |
| `nextjs` | Next.js frontend with TypeScript |
| `fullstack` | FastAPI + Next.js combination |
| `cli` | Command-line tool with Click |
| `automation` | n8n workflow project |

```bash
# Create from template
mw new my-project fastapi
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Claude Code](https://github.com/anthropics/claude-code) - AI coding assistant
- [GSD](https://github.com/anthropics/claude-code) - Project orchestration
- [n8n](https://n8n.io) - Workflow automation
- [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) - n8n MCP server
- [n8n-skills](https://github.com/czlonkowski/n8n-skills) - Claude Code skills for n8n

---

Built with AI, for AI-assisted development.
