<div align="center">

```
███╗   ███╗██╗   ██╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗     █████╗ ██╗
████╗ ████║╚██╗ ██╔╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝    ██╔══██╗██║
██╔████╔██║ ╚████╔╝ ██║ █╗ ██║██║   ██║██████╔╝█████╔╝     ███████║██║
██║╚██╔╝██║  ╚██╔╝  ██║███╗██║██║   ██║██╔══██╗██╔═██╗     ██╔══██║██║
██║ ╚═╝ ██║   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗    ██║  ██║██║
╚═╝     ╚═╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
```

# MyWork-AI

### The AI-Powered Development Framework

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-75%20passing-brightgreen.svg)](tests/)
[![Security](https://img.shields.io/badge/security-audited-green.svg)](reports/)

**Build complete applications from idea to marketplace in minutes, not months.**

[Quick Start](#-quick-start) · [Features](#-features) · [Documentation](#-documentation) · [Marketplace](#-marketplace) · [Contributing](#-contributing)

</div>

---

## 🎯 What is MyWork-AI?

MyWork-AI is a unified development framework that combines **project orchestration**, **autonomous coding**, **knowledge management**, and **marketplace distribution** into a single CLI tool.

```
Idea → Enhanced Prompt → GSD Planning → AutoForge Coding → Testing → Marketplace
```

**One command to start. One framework to ship.**

```bash
pip install mywork-ai
mw setup
mw new my-saas fullstack
```

## ⚡ Quick Start

### Installation

```bash
# Install from PyPI
pip install mywork-ai

# Or install from source
git clone https://github.com/DansiDanutz/MyWork-AI.git
cd MyWork-AI
pip install -e .
```

### Your First Project

```bash
# 1. Setup your environment
mw setup

# 2. Learn the workflow
mw guide

# 3. Enhance your idea into a full spec
mw prompt-enhance "build a SaaS invoice tool with Stripe payments"

# 4. Scaffold your project
mw new invoice-app fullstack

# 5. Check framework health
mw status

# 6. View your dashboard
mw dashboard
```

## 🚀 Features

### 🏗️ Project Scaffolding
Create production-ready projects in seconds with 6+ templates:

| Template | Description |
|----------|-------------|
| `basic` | Empty project with GSD structure |
| `fastapi` | FastAPI backend + SQLite + SQLAlchemy |
| `nextjs` | Next.js + TypeScript + Tailwind CSS |
| `fullstack` | FastAPI backend + Next.js frontend |
| `cli` | Python CLI application |
| `automation` | n8n + Python automation |

```bash
mw new my-app fastapi    # Create a FastAPI project
mw new my-site nextjs    # Create a Next.js project
mw new my-saas fullstack # Create a full-stack app
```

### 🧠 Brain — Knowledge Vault
A persistent knowledge system that learns from your work:

```bash
mw brain add lesson "Always validate inputs before DB writes"
mw brain search "deployment"
mw brain stats
mw brain export
```

Features:
- **Semantic search** with TF-IDF ranking
- **Knowledge graph** with relationship detection
- **Auto-learning** from git commits and error patterns
- **Analytics** with growth tracking and quality scores
- **Backup/restore** with timestamped snapshots

### 🔨 GSD — Project Orchestration
*Get Shit Done* — structured project management:

```
/gsd:new-project    → Full planning with requirements & roadmap
/gsd:plan-phase N   → Detailed task plans for each phase
/gsd:execute-phase N → Parallel execution with atomic commits
/gsd:verify-work N  → Quality verification and testing
```

### 🤖 AutoForge — Autonomous Coding
Long-running autonomous coding powered by Claude Agent SDK:

```bash
mw af start my-project   # Start AutoForge
mw af status             # Check progress
mw af stop my-project    # Stop when done
```

### 🔍 Smart Prompt Enhancement
Turn vague ideas into detailed project specs:

```bash
mw prompt-enhance "build me a todo app"
# Outputs: detailed requirements, tech stack, security considerations,
#          testing strategy, 5-phase development roadmap
```

### 🛡️ Security
Built-in security scanning and monitoring:

```bash
python tools/security/code_scanner.py     # Scan code for vulnerabilities
python tools/security/dep_audit.py        # Audit dependencies
python tools/security/infra_scanner.py    # Check infrastructure
python tools/security/generate_report.py  # Full security report
```

### 🎮 Simulation Engine
Test your marketplace with virtual users, credits, and MLM:

```bash
python tools/simulation/run_simulation.py
# Simulates: 20 users, product listings, purchases,
#            MLM commissions (5 levels), credit flows
```

### 🔗 Agent Skills System
Install and manage reusable skills:

```bash
mw skills list           # List installed skills
mw skills install <url>  # Install from GitHub
mw skills create <name>  # Create a new skill
```

Pre-built skills: `code-review`, `security-scan`, `deploy-check`, `doc-generator`

## 📊 CLI Reference

```
mw setup              First-time setup wizard
mw guide              Interactive workflow tutorial
mw status             Quick health check
mw dashboard          Visual framework overview
mw doctor             Full diagnostics
mw report             Detailed health report
mw fix                Auto-fix common issues

mw new <name> <tpl>   Create new project
mw projects           List all projects
mw projects scan      Refresh project registry
mw prompt-enhance     Enhance prompts for GSD

mw brain search <q>   Search knowledge vault
mw brain add <type>   Add knowledge entry
mw brain stats        Brain statistics
mw brain export       Export to markdown

mw af start <proj>    Start AutoForge
mw af status          Check AutoForge status
mw af stop <proj>     Stop AutoForge

mw lint scan          Scan for linting issues
mw lint stats         Linting statistics
mw search <query>     Search module registry
mw skills list        List agent skills
```

## 🏛️ Architecture

```
MyWork-AI/
├── tools/                    # Core framework tools
│   ├── mw.py                # Unified CLI (entry point)
│   ├── brain.py             # Knowledge vault manager
│   ├── brain_search.py      # Semantic search engine
│   ├── brain_graph.py       # Knowledge graph & clustering
│   ├── brain_learner.py     # Auto-learning engine
│   ├── scaffold.py          # Project scaffolding
│   ├── health_check.py      # System diagnostics
│   ├── autoforge_api.py     # AutoForge integration
│   ├── module_registry.py   # Reusable code index
│   ├── security/            # Security scanning suite
│   ├── simulation/          # Marketplace simulation
│   ├── skills/              # Agent skills framework
│   └── e2e/                 # End-to-end test suite
├── workflows/               # Workflow templates
│   ├── code_review.md
│   ├── deploy_to_vercel.md
│   ├── release.md
│   └── incident_response.md
├── projects/                # Your projects live here
├── tests/                   # 75+ unit tests
├── .planning/               # Framework state & roadmap
└── reports/                 # Generated reports
```

## 🏪 Marketplace

MyWork-AI includes a full marketplace for selling your projects:

- **Frontend**: Next.js on Vercel
- **Backend**: FastAPI on Railway
- **Features**: Credits system, MLM referrals (5 levels), Stripe payments, seller verification

[Visit Marketplace →](https://frontend-hazel-ten-17.vercel.app)

## 📈 Quality Metrics

| Metric | Value |
|--------|-------|
| Unit Tests | 75/75 passing ✅ |
| User Simulations | 30/30 completed ✅ |
| Security Issues | 0 critical ✅ |
| CLI Commands | 20+ all working ✅ |
| Response Time | <15s per command ✅ |
| Package Size | 106 KB ✅ |

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/DansiDanutz/MyWork-AI.git
cd MyWork-AI
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run security scan
python tools/security/generate_report.py

# Run simulation
python tools/simulation/run_simulation.py
```

## 📋 Documentation

- [CLAUDE.md](CLAUDE.md) — Master orchestrator instructions
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [SECURITY.md](SECURITY.md) — Security policy
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
- [STRATEGY.md](STRATEGY.md) — Project strategy

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Run tests (`pytest tests/ -v`)
4. Commit your changes (`git commit -m 'feat: add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## 👨‍💻 Team

- **Dan Sidanutz** — Creator & Owner
- **Dexter** — Senior Developer & Architect
- **Memo** — Developer & Project Manager

---

<div align="center">

**Built with ❤️ by the MyWork-AI team**

[⬆ Back to Top](#mywork-ai)

</div>
