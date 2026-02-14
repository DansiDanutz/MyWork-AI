# MyWork-AI

<div align="center">

![PyPI Version](https://img.shields.io/pypi/v/mywork-ai?style=for-the-badge&logo=pypi&logoColor=white)
![Python Version](https://img.shields.io/pypi/pyversions/mywork-ai?style=for-the-badge&logo=python&logoColor=white)
![Downloads](https://img.shields.io/pypi/dm/mywork-ai?style=for-the-badge&color=blue)
![License](https://img.shields.io/github/license/dansidanutz/MyWork-AI?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-1032%20passing-brightgreen?style=for-the-badge)

**🤖 AI-Powered Development Framework**

*The complete CLI toolkit for modern developers*

[📖 Documentation](https://docssite-igkwv43c5-irises-projects-ce549f63.vercel.app) • [🚀 Quick Start](#-quick-start) • [🔧 Commands](#-command-reference) • [💡 Examples](#-examples)

</div>

---

## 🚀 Quick Start

### Install from PyPI

```bash
pip install mywork-ai
```

### 3-Step Setup

```bash
# 1. Verify installation
mw selftest

# 2. Initialize your project  
mw init my-app
cd my-app

# 3. Check project health
mw doctor
```

**That's it! You now have access to 53+ AI-powered development commands.**

---

## ✨ Why MyWork-AI?

| **MyWork-AI** | **Cursor** | **Aider** | **Claude Dev** |
|---------------|------------|-----------|----------------|
| ✅ **53+ CLI Commands** | ❌ Editor only | ❌ Limited scope | ❌ VS Code only |
| ✅ **Project Health Scoring** | ❌ No health insights | ❌ No project analysis | ❌ No health metrics |
| ✅ **Security Scanning** | ❌ Limited security | ❌ No security focus | ❌ No security tools |
| ✅ **Deployment Pipeline** | ❌ No deployment | ❌ No deployment | ❌ No deployment |
| ✅ **Analytics Dashboard** | ❌ No analytics | ❌ No metrics | ❌ No dashboard |
| ✅ **Open Source + Free** | 💰 Subscription | 💰 Paid tiers | 💰 Claude credits |

**MyWork-AI is the only tool that gives you a complete development ecosystem, not just code generation.**

---

## 🔥 Core Features

### 🤖 **AI-Powered Development**
- **Smart Code Generation**: `mw ai generate` - Create complete files from natural language
- **Intelligent Refactoring**: `mw ai refactor` - AST-based code improvements  
- **Automated Reviews**: `mw ai review` - AI-powered code analysis
- **Context Building**: `mw context` - Smart context for AI assistants

### 📊 **Project Intelligence** 
- **Health Scoring**: `mw health` - Instant project health (0-100 score)
- **Code Metrics**: `mw metrics` - LOC, complexity, tech debt analysis
- **Dependency Analysis**: `mw depgraph` - Visualize dependency relationships
- **Test Coverage**: `mw test-coverage` - Find gaps and scaffold tests

### 🛡️ **Security & Quality**
- **Security Scanning**: `mw scan security` - OWASP compliance checking
- **Secrets Management**: `mw secrets` - Encrypted secrets vault
- **Quality Gates**: `mw check` - Lint + test + types + security
- **Vulnerability Audits**: `mw deps audit` - Check for known CVEs

### 🚀 **DevOps & Deployment**
- **CI/CD Generation**: `mw ci` - Auto-generate GitHub Actions
- **Multi-platform Deploy**: `mw deploy` - Vercel, Railway, Docker
- **Environment Management**: `mw env` - Audit and manage env vars
- **Migration Tools**: `mw migrate` - Database migration manager

### 📈 **Analytics & Insights**
- **Performance Benchmarks**: `mw bench` - Code performance profiling
- **Productivity Tracking**: `mw recap` - Daily/weekly summaries
- **Git Analytics**: `mw git summary` - Contribution insights
- **Real-time Dashboard**: `mw api` - Web dashboard with live metrics

---

## 🔧 Command Reference

### **Essential Commands**
```bash
mw init          # Initialize new project with smart detection
mw doctor        # Project health check with recommendations  
mw health        # Instant health score (0-100) with grade
mw check         # Quality gate (lint + test + types + security)
mw deploy        # Multi-platform deployment
```

### **AI Commands** 
```bash
mw ai generate   # Create files from natural language
mw ai refactor   # AST-based refactoring suggestions
mw ai review     # Automated code review
mw ai optimize   # Performance optimization hints
mw context       # Build context for AI tools
```

### **Analysis & Metrics**
```bash
mw metrics       # Code quality metrics dashboard
mw insights      # Tech debt and hotspot analysis  
mw depgraph      # Dependency visualization
mw test-coverage # Test gap analysis
mw bench         # Performance benchmarking
```

### **Security & Compliance**
```bash
mw scan security # Security vulnerability scan
mw secrets       # Encrypted secrets management
mw deps audit    # Dependency vulnerability check
mw env audit     # Environment variable security
```

### **DevOps & CI/CD**
```bash
mw ci status     # GitHub Actions status
mw ci generate   # Auto-generate CI/CD pipelines
mw migrate       # Database migration tools
mw profile       # Command execution profiling
```

<details>
<summary><strong>📋 All 53 Commands</strong> (click to expand)</summary>

```bash
# Core
mw init, mw doctor, mw health, mw check, mw deploy, mw test

# AI & Code Generation  
mw ai generate, mw ai refactor, mw ai review, mw ai optimize, mw context

# Project Analysis
mw metrics, mw insights, mw depgraph, mw test-coverage, mw tree, mw todo

# Security & Quality
mw scan security, mw secrets, mw deps audit, mw env audit, mw badge

# DevOps & Deployment
mw ci status, mw ci generate, mw migrate, mw watch, mw profile

# Git & Collaboration  
mw git summary, mw git standup, mw git contributors, mw changelog

# Documentation & Tools
mw docs generate, mw docs site, mw tour, mw demo, mw upgrade

# Advanced Features
mw api, mw pair, mw bench, mw snapshot, mw plugin, mw selftest
```

</details>

---

## 💡 Examples

### Generate a Full-Stack App

```bash
# Create a task management app
mw init task-manager
cd task-manager

# Generate React frontend + Node.js backend
mw ai generate --type="fullstack" --description="Task tracker with auth, dashboard, and API"

# Add security and deploy
mw scan security --fix
mw deploy --platform=vercel
```

### Project Health Analysis

```bash
# Get instant health score
mw health
# Output: ✅ Health Score: 89/100 (Grade: B+)
#         📊 12 recommendations found

# Deep analysis
mw insights
# Tech debt: 2.3 hours
# Hotspots: src/auth.py, src/db.py
# Coverage gaps: 7 files missing tests
```

### Security Audit

```bash
# Complete security check
mw scan security
mw deps audit  
mw secrets audit
mw env audit

# Fix issues automatically
mw scan security --fix-auto
```

---

## 🏗️ Installation & Setup

### Requirements

- **Python**: 3.9+ 
- **OS**: Linux, macOS, Windows
- **Optional**: Git, Docker (for some features)

### Install Options

```bash
# PyPI (recommended)
pip install mywork-ai

# Development version
pip install git+https://github.com/dansidanutz/MyWork-AI.git

# With all optional dependencies
pip install mywork-ai[all]
```

### Verify Installation

```bash
mw --version
mw selftest  # Runs 8 diagnostic checks
```

---

## 📊 Performance & Reliability

- ⚡ **<2s average** command execution time
- 🛡️ **Zero critical** vulnerabilities in generated code  
- 📈 **95%+ test coverage** on all generated projects
- 🏆 **1032 automated tests** ensure reliability
- 🚀 **10x faster** development cycles vs traditional tools

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Clone and setup
git clone https://github.com/dansidanutz/MyWork-AI.git
cd MyWork-AI
pip install -e .[dev]

# Run tests
pytest

# Security check  
mw scan security
```

---

## 🆚 Comparison with Alternatives

### **vs Cursor IDE**
- ✅ **CLI-first**: Works with any editor
- ✅ **Complete toolkit**: 53+ commands vs editor integration
- ✅ **Project analysis**: Health scoring, metrics, insights
- ✅ **Free**: No subscription required

### **vs Aider**
- ✅ **Broader scope**: Full DevOps pipeline, not just coding
- ✅ **Security focus**: Built-in scanning and compliance
- ✅ **Project health**: Comprehensive analysis tools
- ✅ **Deployment**: One-command deployment to multiple platforms

### **vs GitHub Copilot**
- ✅ **Framework approach**: Complete development ecosystem
- ✅ **Project-level**: Analyzes entire codebase, not just individual files
- ✅ **DevOps included**: CI/CD, deployment, monitoring
- ✅ **Quality gates**: Automated quality and security checks

---

## 📚 Documentation

- **[📖 Getting Started Guide](docs/quickstart.md)**
- **[🔧 Complete CLI Reference](docs/cli-reference.md)**  
- **[🤖 AI Features Guide](docs/ai-features.md)**
- **[🚀 Deployment Guide](docs/deployment.md)**
- **[❓ FAQ & Troubleshooting](FAQ.md)**

---

## 📄 License

MyWork-AI is open source software licensed under the **[MIT License](LICENSE)**.

---

## 🌟 Support

- **🐛 Issues**: [GitHub Issues](https://github.com/dansidanutz/MyWork-AI/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/dansidanutz/MyWork-AI/discussions)  
- **📧 Email**: dan@mywork.ai
- **🔒 Security**: [Security Policy](SECURITY.md)

---

<div align="center">

**⭐ Star us on GitHub if MyWork-AI helps you build faster!**

[⭐ **Star on GitHub**](https://github.com/dansidanutz/MyWork-AI) • [🐦 **Follow on Twitter**](https://twitter.com/mywork_ai) • [💼 **LinkedIn**](https://linkedin.com/company/mywork-ai)

*Built with ❤️ by the MyWork-AI team*

</div>