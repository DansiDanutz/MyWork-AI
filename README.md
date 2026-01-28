<div align="center">

# MyWork Framework

### AI-Powered Development Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![GSD](https://img.shields.io/badge/GSD-v1.9.10-blue?logo=anthropic&logoColor=white)](https://github.com/anthropics/claude-code)
[![n8n](https://img.shields.io/badge/n8n-2709%20templates-EA4B71?logo=n8n&logoColor=white)](https://n8n.io)

**A unified framework combining project orchestration, autonomous coding, and workflow automation.**

### You Clone. You Build. You Sell. You Earn.

```text
   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
   │  CLONE   │ ───► │  BUILD   │ ───► │  SELL    │ ───► │  EARN    │
   │          │      │          │      │          │      │          │
   │ Get the  │      │ AI builds│      │ List on  │      │ Passive  │
   │ framework│      │ your app │      │Marketplace│      │ income   │
   └──────────┘      └──────────┘      └──────────┘      └──────────┘
```

[The 3 Tools](#the-3-tools-included) | [Two Paths](#two-ways-to-use-this-framework) | [Quick Start](#quick-start) | [How It Works](#how-it-works)

</div>

---

## The 3 Tools (Included)

When you clone this repo, you get **three working tools** ready to use. Log in with your **GitHub account** to access the live platforms.

### 1. Task Tracker

> **Production-ready task management** - Use it, learn from it, improve it.

| | |
|---|---|
| **Live App** | [task-tracker-weld-delta.vercel.app](https://task-tracker-weld-delta.vercel.app) |
| **Source** | [`projects/task-tracker/`](projects/task-tracker/) |
| **Stack** | Next.js 15 + Prisma + Neon PostgreSQL |
| **Features** | GitHub OAuth, full-text search, drag-and-drop, real-time updates |

Built in 5.8 hours with GSD orchestration (39 plans, 211 commits).

### 2. AI Dashboard

> **AI news aggregation and YouTube automation** - Ready to deploy.

| | |
|---|---|
| **Source** | [`projects/ai-dashboard/`](projects/ai-dashboard/) |
| **Stack** | Next.js 14 + FastAPI + APScheduler + SQLite |
| **Features** | YouTube scraper, news aggregator, GitHub trending, HeyGen video automation |
| **Status** | MVP complete, ready for deployment |

### 3. Marketplace

> **Where you sell what you build.** This is a private repo - you access it by logging in with GitHub.

| | |
|---|---|
| **Platform** | [frontend-hazel-ten-17.vercel.app](https://frontend-hazel-ten-17.vercel.app) |
| **API** | [mywork-ai-production.up.railway.app](https://mywork-ai-production.up.railway.app) |
| **Access** | Log in with your **GitHub account** - no source code needed |
| **Features** | Product listings, Stripe payments, seller dashboard, 90% revenue to sellers |

You don't need the Marketplace source code. Just log in, list your product, and start earning.

---

## Two Ways to Use This Framework

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   PATH A: DEVELOP THE SYSTEM            PATH B: BUILD & SELL            │
│   ─────────────────────────             ────────────────────            │
│                                                                         │
│   Add new tools to the framework.       Build products with the         │
│   Improve existing ones.                framework and sell them         │
│   Submit pull requests.                 on the Marketplace.             │
│                                                                         │
│   Examples:                             Examples:                       │
│   - Add a new scraper                   - SaaS app                     │
│   - Improve the Task Tracker            - Analytics tool               │
│   - Create a new template               - Automation service           │
│                                                                         │
│   You make the framework better         You keep 90% of revenue        │
│   for everyone.                         from every sale.               │
│                                                                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
              ┌────────────────────────────────────┐
              │     BOTH PATHS FEED THE BRAIN      │
              │                                    │
              │  Every tool you build, every bug   │
              │  you fix, every project you ship   │
              │  teaches the system something new. │
              │                                    │
              │  The Brain remembers patterns,     │
              │  the Module Registry indexes code, │
              │  and the next project gets easier  │
              │  for EVERYONE in the ecosystem.    │
              └────────────────────────────────────┘
```

---

## Example Product: Sports-AI

This is what a **Path B product** looks like - built with MyWork, sold on the Marketplace:

| | |
|---|---|
| **Live Product** | [sports-ai-one.vercel.app](https://sports-ai-one.vercel.app) |
| **Marketplace Listing** | [View on Marketplace](https://frontend-hazel-ten-17.vercel.app) |
| **Stack** | React + FastAPI + PostgreSQL + Redis |
| **Features** | 10+ sportsbook odds, arbitrage alerts, AI predictions, 2FA |

Sports-AI is **not in this repo** - it's a separate product built to demonstrate what you can create and sell. The knowledge from building it lives in the Brain (`.planning/BRAIN.md`), so future projects benefit from lessons learned.

---

## Production Status

| Component | Type | Status | Link |
|---|---|---|---|
| **Task Tracker** | Tool (in repo) | ![Status](https://img.shields.io/badge/status-live-brightgreen) | [Demo](https://task-tracker-weld-delta.vercel.app) |
| **AI Dashboard** | Tool (in repo) | MVP Complete | [`projects/ai-dashboard/`](projects/ai-dashboard/) |
| **Marketplace** | Platform | ![Status](https://img.shields.io/badge/status-live-brightgreen) | [Platform](https://frontend-hazel-ten-17.vercel.app) |
| **Sports-AI** | Product (example) | ![Status](https://img.shields.io/badge/status-live-brightgreen) | [View](https://sports-ai-one.vercel.app) |

---

## How It Works

### The Architecture

```text
                        ┌─────────────────────────────────────┐
                        │           YOU (Request)              │
                        └─────────────────┬───────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MASTER ORCHESTRATOR                                │
│                                  (CLAUDE.md)                                    │
│                                                                                 │
│   "What type of task is this?"                                                  │
│                                                                                 │
│   New project?        → GSD Layer                                               │
│   Quick fix?          → GSD Quick                                               │
│   20+ features?       → Autocoder                                               │
│   Webhooks/APIs?      → n8n                                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                          │
             ┌────────────────────────────┼────────────────────────────┐
             │                            │                            │
             ▼                            ▼                            ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│      LAYER 1: GSD       │   │      LAYER 2: WAT       │   │   LAYER 3: ENGINES      │
│  (Project Orchestration)│   │   (Task Execution)      │   │     (Automation)        │
├─────────────────────────┤   ├─────────────────────────┤   ├─────────────────────────┤
│                         │   │                         │   │                         │
│  /gsd:new-project       │   │  workflows/             │   │  Autocoder              │
│  /gsd:plan-phase        │   │  (Markdown SOPs)        │   │  Autonomous multi-hour  │
│  /gsd:execute-phase     │   │         │               │   │  coding sessions        │
│  /gsd:verify-work       │   │         ▼               │   │                         │
│                         │   │  tools/                 │   │  n8n                    │
│                         │   │  (Python scripts)       │   │  2,709 workflow         │
│                         │   │                         │   │  templates              │
└────────────┬────────────┘   └────────────┬────────────┘   └──────────┬──────────────┘
             │                             │                            │
             └─────────────────────────────┼────────────────────────────┘
                                           │
                                           ▼
                 ┌─────────────────────────────────────────────┐
                 │              SELF-LEARNING                   │
                 ├─────────────────────────────────────────────┤
                 │                                             │
                 │   BRAIN             MODULE REGISTRY          │
                 │   Remembers what    Indexes your code        │
                 │   worked & failed   1,300+ reusable modules  │
                 │                                             │
                 │   Every completed task makes the next faster │
                 └─────────────────────────────────────────────┘
```

### The Simple Flow

1. You ask for something
2. CLAUDE.md routes to the right tool
3. Work gets done (with atomic commits)
4. Brain learns from result
5. Next time is faster

---

## Installation (2 Steps)

```bash
# Step 1: Clone
git clone https://github.com/DansiDanutz/MyWork-AI.git
cd MyWork-AI

# Step 2: Install
./install.sh          # macOS/Linux
install.bat           # Windows
```

The script installs Python dependencies, sets up the environment, and verifies everything works.

| Step | What Happens |
|---|---|
| 1 | Checks Python 3.9+ and Node.js 18+ |
| 2 | Creates virtual environment |
| 3 | Installs all dependencies |
| 4 | Creates `.env` from template |
| 5 | Runs health check |
| 6 | Shows next steps |

---

## Quick Start

### Create Your First Project

```bash
# Create from template
python tools/mw.py new my-app fastapi

# Navigate to project
cd projects/my-app

# In Claude Code CLI:
/gsd:new-project          # Initialize with discovery
/gsd:plan-phase 1         # Plan first phase
/gsd:execute-phase 1      # Build it
/gsd:verify-work          # Validate
```

### Available Templates

| Template | Stack | Best For |
|---|---|---|
| `basic` | Python only | Scripts, utilities |
| `fastapi` | FastAPI + SQLAlchemy + SQLite | APIs, backends |
| `nextjs` | Next.js + TypeScript + Tailwind | Frontends, SPAs |
| `fullstack` | FastAPI + Next.js | Complete web apps |
| `cli` | Python + Click | Command-line tools |
| `automation` | n8n + Python webhooks | Workflow automation |

```bash
python tools/mw.py new my-api fastapi
python tools/mw.py new my-site nextjs
python tools/mw.py new my-saas fullstack
```

---

## Configuration

After installation, configure your API keys in `.env`:

### Required

```bash
# REQUIRED - You need at least this one
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Optional

```bash
# Other AI Providers
OPENAI_API_KEY=sk-xxxxx
GROQ_API_KEY=gsk_xxxxx

# n8n Workflow Automation
N8N_API_URL=https://your.app.n8n.cloud
N8N_API_KEY=your-n8n-api-key

# GitHub Integration
GITHUB_TOKEN=ghp_xxxxx
```

### MCP Server Configuration

Copy `.mcp.json.example` to `.mcp.json`:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "N8N_API_URL": "https://your-instance.app.n8n.cloud",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Verify Configuration

```bash
python tools/mw.py doctor
```

---

## CLI Reference

### Core Commands

```bash
# Status & Health
mw status                    # Quick health check
mw doctor                    # Full diagnostics with auto-fix

# Projects
mw new <name> [template]     # Create project
mw projects                  # List all projects
mw open <name>               # Open in VS Code

# Knowledge
mw brain search <query>      # Search knowledge vault
mw brain learn               # Run daily learning
mw search <query>            # Search module registry (1,300+ modules)

# Updates
mw update check              # Check for updates
mw update <component>        # Update gsd|autocoder|n8n-skills
```

### GSD Commands

| Command | Purpose |
|---|---|
| `/gsd:new-project` | Initialize with discovery, research, roadmap |
| `/gsd:plan-phase N` | Create detailed task plans for phase N |
| `/gsd:execute-phase N` | Run plans in parallel waves |
| `/gsd:verify-work` | User acceptance testing |
| `/gsd:progress` | Check current status |
| `/gsd:quick` | Ad-hoc tasks with GSD guarantees |
| `/gsd:pause-work` | Save context when stopping |
| `/gsd:resume-work` | Restore context next session |

### Autocoder Commands

```bash
mw ac start <project>        # Start autonomous coding
mw ac stop <project>         # Stop gracefully
mw ac status                 # Check server status
mw ac progress <project>     # View progress
mw ac ui                     # Open web interface
```

---

## Project Structure

```
MyWork-AI/
├── projects/                    # All projects live here
│   ├── task-tracker/            # Production task manager
│   ├── ai-dashboard/            # AI news aggregator
│   └── _template/               # New project template
│
├── tools/                       # CLI and utilities
│   ├── mw.py                    # Unified CLI entry point
│   ├── brain.py                 # Knowledge vault manager
│   ├── module_registry.py       # Code pattern indexer
│   ├── health_check.py          # System diagnostics
│   ├── autocoder_api.py         # Autocoder control
│   └── scaffold.py              # Project templates
│
├── workflows/                   # WAT workflow definitions
│   ├── create_n8n_workflow.md   # n8n workflow SOP
│   ├── gsd_to_autocoder.md      # GSD → Autocoder handoff
│   └── session_handoff.md       # Context preservation
│
├── .planning/                   # Framework-level state
│   ├── BRAIN.md                 # Knowledge vault
│   ├── STATE.md                 # Current context
│   └── codebase/                # Codebase analysis
│
├── CLAUDE.md                    # Master Orchestrator instructions
├── .env.example                 # Environment template
└── .mcp.json.example            # MCP server config template
```

---

## Documentation

| Document | Description |
|---|---|
| [Quick Start Guide](docs/quickstart.md) | Get running fast |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and fixes |
| [FAQ](docs/faq.md) | Frequently asked questions |
| [Architecture](docs/architecture/) | System design deep-dive |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |
| [Security](SECURITY.md) | Security policy and reporting |
| [Changelog](CHANGELOG.md) | Version history |

---

## Security

This framework handles sensitive credentials. Follow these practices:

| File | Purpose | Commit? |
|---|---|---|
| `.env` | API keys and secrets | **Never** |
| `.mcp.json` | MCP server credentials | **Never** |
| `.env.example` | Template (no real values) | Safe |
| `.mcp.json.example` | Template (no real values) | Safe |

Run `mw doctor` regularly to check for exposed secrets. See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/MyWork-AI.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m 'Add amazing feature'

# Push and create PR
git push origin feature/amazing-feature
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Claude Code](https://github.com/anthropics/claude-code) - AI coding assistant and GSD orchestration
- [n8n](https://n8n.io) - Workflow automation platform
- [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) - n8n MCP server (1,084 nodes)
- [n8n-skills](https://github.com/czlonkowski/n8n-skills) - Claude Code skills for n8n

---

<div align="center">

**Built with AI, for AI-assisted development.**

[Report Bug](https://github.com/DansiDanutz/MyWork-AI/issues) | [Request Feature](https://github.com/DansiDanutz/MyWork-AI/issues) | [Discussions](https://github.com/DansiDanutz/MyWork-AI/discussions)

</div>
