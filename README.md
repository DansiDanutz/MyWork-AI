# MyWork-AI

<div align="center">

![PyPI Version](https://img.shields.io/pypi/v/mywork-ai?style=for-the-badge&logo=pypi&logoColor=white)
![Python Version](https://img.shields.io/pypi/pyversions/mywork-ai?style=for-the-badge&logo=python&logoColor=white)
![Downloads](https://img.shields.io/pypi/dm/mywork-ai?style=for-the-badge&color=blue)
![License](https://img.shields.io/github/license/dansidanutz/MyWork-AI?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-424%20passing-brightgreen?style=for-the-badge)

**🤖 Build, Ship & Sell Software Products — From One CLI**

*72+ commands · AI code generation · Agent engine · Marketplace included · n8n automation*

[🚀 Quick Start](#-quick-start) · [🔧 Commands](#-command-reference) · [💡 Examples](#-examples) · [🛒 Marketplace](https://frontend-hazel-ten-17.vercel.app)

</div>

---

## What Is MyWork-AI?

MyWork-AI is a **complete development framework** that takes you from idea to shipped product to revenue. It combines project scaffolding, AI code generation, security scanning, n8n workflow automation, deployment tools, and a marketplace — all from a single `mw` command.

```
pip install mywork-ai → mw setup → mw new → build → mw deploy → mw marketplace publish
```

**This isn't another code assistant.** It's the full pipeline.

---

## 🚀 Quick Start

```bash
# Install
pip install mywork-ai

# Set up (configures API keys, preferences)
mw setup

# Create a project with AI (generates real code, not templates!)
mw new --ai "invoice API with PDF export and email delivery"

# Or use templates
mw new my-api fastapi

# Check health
cd my-project && mw doctor

# Run the AI agent built into your project
mw agent run agent.yaml

# Deploy
mw deploy
```

### ✨ AI Agent Engine (NEW in v2.7.0)

```bash
# Create an AI agent
mw agent init customer-bot

# Run it (CLI chat with tool calling)
mw agent run customer-bot.yaml

# Run with web UI
mw agent run customer-bot.yaml --web
# → Open http://localhost:8080

# Supports 100+ models: OpenAI, Claude, DeepSeek, Gemini, Ollama, Mistral...
```

Agent config is a simple YAML file:
```yaml
name: Code Reviewer
model: deepseek/deepseek-chat
instructions: |
  Review code for bugs, security issues, and improvements.
tools:
  - name: read_file
    description: Read a source file
    parameters:
      path: {type: string, description: "File path"}
    command: "cat '{path}'"
```

**You're live in 5 minutes.**

---

## ✨ Why MyWork-AI?

| Feature | MyWork-AI | Cursor | Aider | Zapier/Make |
|---------|-----------|--------|-------|-------------|
| CLI-first (any editor) | ✅ | ❌ | ✅ | ❌ |
| Project scaffolding | ✅ 12 templates | ❌ | ❌ | ❌ |
| AI code generation | ✅ | ✅ | ✅ | ❌ |
| Security scanning | ✅ | ❌ | ❌ | ❌ |
| n8n workflow automation | ✅ 16 commands | ❌ | ❌ | ✅ (paid) |
| Deployment pipeline | ✅ Multi-platform | ❌ | ❌ | ❌ |
| Cost tracking (AI APIs) | ✅ | ❌ | ❌ | ❌ |
| Secrets vault | ✅ Encrypted | ❌ | ❌ | ❌ |
| Product marketplace | ✅ Built-in | ❌ | ❌ | ✅ (paid) |
| Open source & free | ✅ | 💰 | 💰 | 💰 |

---

## 🔥 Core Features

### 🏗️ Project Scaffolding
```bash
mw new my-app basic        # Simple Python project
mw new my-api fastapi       # REST API with FastAPI
mw new my-saas saas         # Full SaaS with auth, billing, dashboard
mw new my-bot chatbot       # AI chatbot with conversation memory
mw new my-tool cli          # Command-line tool with arg parsing
mw new my-scraper scraper   # Web scraper with data export
mw new my-dash dashboard    # Analytics dashboard
mw new my-auto automation   # Task automation with scheduling
```

Each template includes: project structure, `.env.example`, tests, CI config, README, and `.planning/` directory with roadmap.

### 🤖 AI-Powered Development
```bash
mw ai generate     # Create complete files from natural language
mw ai refactor     # AST-based code improvements
mw ai review       # Automated code review
mw prompt-enhance  # Improve rough prompts for better AI output
mw context         # Build smart context for AI assistants
```

### ⚡ n8n Workflow Automation (16 Commands)
```bash
mw n8n setup       # One-command n8n install (Docker or npm)
mw n8n status      # Check n8n health
mw n8n list        # List all workflows
mw n8n import      # Import workflow from JSON
mw n8n export      # Export workflow
mw n8n activate    # Activate/deactivate workflows
mw n8n exec        # Execute a workflow
mw n8n test        # Validate workflow before deploy
mw n8n templates   # Browse 2,700+ community templates
mw n8n config      # Manage n8n configuration
```

### 🛡️ Security & Quality
```bash
mw security        # Full security scan (OWASP checks)
mw secrets set/get # Encrypted secrets vault (Fernet)
mw env audit       # Environment variable security scan
mw deps            # Dependency vulnerability check
mw health          # Project health score (0-100)
mw doctor          # Comprehensive diagnostics
mw selftest        # Framework self-check (11 checks)
```

### 🚀 DevOps & Deployment
```bash
mw deploy          # Multi-platform (Vercel, Railway, Docker)
mw ci              # Auto-generate GitHub Actions CI/CD
mw launch          # Pre-launch checklist with countdown
mw release         # Version bump + changelog + publish
mw backup          # Project backup & restore
```

### 💰 Cost & Analytics
```bash
mw cost estimate   # Estimate AI API costs for your project
mw cost track      # Running cost tracker across all providers
mw cost budget     # Set monthly budget alerts
mw cost report     # Monthly breakdown by model/provider
mw benchmark       # Code performance profiling
mw stats           # Project statistics dashboard
mw recap           # Daily/weekly productivity summaries
```

### 🛒 Marketplace
```bash
mw marketplace browse   # Browse products
mw marketplace search   # Search by keyword
mw marketplace publish  # Publish your project for sale
mw marketplace install  # Download & install a product
mw clone <product>      # Clone a marketplace product
```

---

## 🔧 Command Reference

<details>
<summary><strong>📋 All 67+ Commands</strong> (click to expand)</summary>

```bash
# Core
mw setup, mw init, mw new, mw status, mw doctor, mw health, mw selftest

# AI & Code Generation
mw ai generate, mw ai refactor, mw ai review, mw ai optimize
mw context, mw prompt-enhance

# Project Planning (GSD)
mw gsd new, mw gsd status, mw gsd progress

# Automation (n8n)
mw n8n setup, mw n8n status, mw n8n list, mw n8n import, mw n8n export
mw n8n activate, mw n8n exec, mw n8n test, mw n8n config, mw n8n templates

# AutoForge (Autonomous Coding)
mw af start, mw af status, mw af queue

# Marketplace
mw marketplace browse, mw marketplace publish, mw marketplace install
mw marketplace search, mw marketplace status, mw clone

# Analysis & Metrics
mw stats, mw benchmark, mw recap, mw todo, mw snapshot

# Security & Quality
mw security, mw secrets, mw deps, mw env, mw audit, mw lint

# DevOps & Deployment
mw deploy, mw ci, mw release, mw launch, mw backup, mw clean

# Cost Tracking
mw cost estimate, mw cost track, mw cost budget, mw cost report

# Git & Collaboration
mw git summary, mw changelog, mw share export, mw share import

# Knowledge Vault
mw brain search, mw brain add, mw brain stats

# Documentation & Onboarding
mw tour, mw demo, mw guide, mw quickstart, mw docs, mw links

# Utilities
mw version, mw upgrade, mw config, mw ecosystem, mw webhook test
mw templates, mw cron, mw monitor
```

</details>

---

## 💡 Examples

### Build a SaaS App
```bash
mw new invoicer saas
cd invoicer
mw doctor          # Check project health
mw security        # Security scan
mw deploy          # Ship it
```

### Automate with n8n
```bash
mw n8n setup                    # Install n8n
mw n8n import lead-nurture.json # Import workflow
mw n8n test lead-nurture.json   # Validate it
mw n8n activate 1               # Go live
```

### Sell on Marketplace
```bash
mw marketplace publish   # Package & list your project
# Set price, description, tags
# Buyers get: mw clone <your-product>
```

### Track AI Costs
```bash
mw cost estimate   # "Estimated $47/mo based on 15 API calls detected"
mw cost budget --set 50  # Alert when approaching $50/mo
mw cost report     # Monthly breakdown: GPT-4 $23, Claude $18, Gemini $6
```

---

## 🏗️ Installation

### Requirements
- **Python**: 3.9+
- **OS**: Linux, macOS, Windows
- **Optional**: Git, Docker, Node.js (for n8n features)

### Install
```bash
# From PyPI (recommended)
pip install mywork-ai

# Development version
pip install git+https://github.com/dansidanutz/MyWork-AI.git

# Verify
mw version
mw selftest
```

---

## 📊 Stats

- **72+ CLI commands** across 12 categories
- **424 automated tests** passing
- **12 project templates** (basic → full SaaS)
- **16 n8n commands** for workflow automation
- **13 marketplace products** live
- **2,700+ n8n templates** browseable
- **v2.8.0** on PyPI

---

## 🤝 Contributing

```bash
git clone https://github.com/dansidanutz/MyWork-AI.git
cd MyWork-AI
pip install -e .[dev]
pytest  # Run all 133 tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

<div align="center">

**⭐ Star us on GitHub if MyWork-AI helps you build faster!**

[⭐ Star on GitHub](https://github.com/DansiDanutz/MyWork-AI) · [🛒 Marketplace](https://frontend-hazel-ten-17.vercel.app) · [📦 PyPI](https://pypi.org/project/mywork-ai/)

*Built by [DansiDanutz](https://github.com/DansiDanutz)*

</div>
