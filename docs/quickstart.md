# 🚀 Quick Start - Get Running in 5 Minutes

Get MyWork framework up and running with your first project in just 5 minutes.

## 📋 Prerequisites

- **macOS/Linux/Windows** (WSL recommended for Windows)
- **Node.js 18+** and **Python 3.9+**
- **Git** configured with GitHub access
- **5 minutes** of your time

## ⚡ Step 1: Install MyWork (1 minute)

```bash

# Clone the framework

git clone https://github.com/DansiDanutz/MyWork-AI.git MyWork
cd MyWork

# Run the installer (handles Python deps, Node.js tools, environment setup)

chmod +x install.sh && ./install.sh

# Verify installation

python tools/mw.py status

```yaml

**Expected Output:**

```yaml
✅ MyWork Framework Status
├── 🧠 Brain: Ready (253 patterns indexed)
├── 📊 Module Registry: Ready (1,300+ modules)
├── 🔧 Health Check: All systems operational
├── 🤖 Autocoder: Available (not running)
└── 🔗 n8n: MCP server ready

🎯 Ready to create your first project!

```markdown

## 🎯 Step 2: Create Your First Project (2 minutes)

```bash

# Create a simple task manager

python tools/mw.py new task-manager-cli cli

# This will:

# 1. Create projects/task-manager-cli/ directory

# 2. Set up basic project structure

# 3. Initialize GSD planning

# 4. Generate project.yaml metadata

```markdown

**What just happened?**

```text
projects/task-manager-cli/
├── .planning/
│   ├── PROJECT.md        # Vision and goals
│   ├── STATE.md          # Current progress
│   └── config.json       # Project settings
├── README.md             # Getting started guide
├── project.yaml          # Project metadata
└── src/                  # Source code (will be created)

```markdown

## 🏗️ Step 3: Plan Your Project (1 minute)

```bash
cd projects/task-manager-cli

# Start GSD planning workflow

python ../../tools/mw.py gsd new-project

# Follow the interactive prompts:

# 1. Project description: "A simple CLI task manager"

# 2. Target audience: "Developers who want quick task tracking"

# 3. Key features: "Add tasks, list tasks, mark complete, search"

```yaml

**GSD will automatically:**

- Research CLI best practices
- Generate requirements document
- Create 3-4 development phases
- Set up verification criteria

## ⚙️ Step 4: Build Your Project (1 minute)

```bash

# Execute the first phase (usually "Foundation & Setup")

python ../../tools/mw.py gsd execute-phase 1

# GSD will:

# ✅ Create CLI argument parser

# ✅ Set up data storage (JSON file)

# ✅ Implement basic commands (add, list)

# ✅ Add tests and documentation

# ✅ Make atomic commits for each task

```yaml

**Real-time progress:**

```yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► EXECUTING WAVE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Task 1: Create CLI argument parser... ✅ (commit abc123d)
◆ Task 2: Implement data storage... ✅ (commit def456e)
◆ Task 3: Add basic commands... ✅ (commit ghi789f)

Phase 1 complete! Ready for Phase 2: Advanced Features

```markdown

## 🎉 Step 5: Test Your Creation (30 seconds)

```bash

# Your CLI tool is now working!

python src/task_manager.py add "Learn MyWork framework"
python src/task_manager.py add "Build my first app"
python src/task_manager.py list

# Expected output:

# 📋 Your Tasks:

# 1. [ ] Learn MyWork framework

# 2. [ ] Build my first app

python src/task_manager.py complete 1
python src/task_manager.py list

# 📋 Your Tasks:

# 1. [✅] Learn MyWork framework

# 2. [ ] Build my first app

```markdown

## 🎊 Congratulations!

In 5 minutes, you've:

✅ **Installed** the MyWork framework
✅ **Created** a new project with GSD planning
✅ **Built** a working CLI application
✅ **Tested** the generated functionality
✅ **Experienced** the full development workflow

## 🚀 What's Next?

### 🎯 **Complete Your Project**

```bash

# Continue with Phase 2 (usually adds search, persistence, etc.)

python ../../tools/mw.py gsd execute-phase 2

# Verify your work with manual testing

python ../../tools/mw.py gsd verify-work

# Deploy or package your application

python ../../tools/mw.py gsd execute-phase 3

```markdown

### 🧠 **Level Up Your Skills**

- 📖 [**Complete Tutorial Series →**](tutorials/01-first-project.md) - 6

  comprehensive guides

- 🏗️ [**Architecture Deep Dive →**](architecture/overview.md) - Understand the 3

  layers

- 💡 [**Example Projects →**](../examples/) - Study working applications
- 🤖 **Autocoder Integration** - Coming soon

### 🔧 **Explore Advanced Features**

```bash

# Search the knowledge brain for patterns

python tools/mw.py brain search "CLI best practices"

# Find reusable code modules

python tools/mw.py search "argument parser"

# Create visual automation workflows

python tools/mw.py n8n create-workflow

# Launch autonomous coding for complex projects

python tools/mw.py ac start my-big-project --concurrency 3

```markdown

### 🌟 **Join the Community**

- 💬 [**GitHub

  Discussions**](https://github.com/DansiDanutz/MyWork-AI/discussions) - Ask
  questions, share projects

- 🐦 [**Twitter Updates**](https://twitter.com/MyWorkAI) - Latest features and

  showcases

- 📺 [**YouTube Channel**](https://youtube.com/@MyWorkAI) - Video tutorials and

  demos

- 📧 [**Newsletter**](https://mywork.ai/newsletter) - Weekly tips and case studies

## 🆘 Troubleshooting

**❌ Installation fails?**

```bash

# Check system requirements

python --version  # Should be 3.9+
node --version    # Should be 18+

# Try manual installation

python tools/health_check.py fix

```markdown

**❌ GSD command not found?**

```bash

# Verify you're in the right directory

pwd  # Should show .../MyWork/projects/your-project

# Check framework status

python ../../tools/mw.py status

```markdown

**❌ Generated code doesn't work?**

```bash

# Run the verification system

python ../../tools/mw.py gsd verify-work

# Check for common issues

python ../../tools/mw.py doctor

```

**❌ Need more help?**

- 📖 [**FAQ →**](faq.md) - Common questions answered
- 🔧 [**Troubleshooting Guide →**](troubleshooting.md) - Detailed problem-solving
- 💬 [**Get Support →**](https://github.com/DansiDanutz/MyWork-AI/discussions) -

  Community help

---

## 📈 What You Just Experienced

| Traditional Development | MyWork Framework |
| ------------------------ | ------------------ |
| ⏱️ **1-2 hours** manual setup | ⚡ **5 minutes** guided setup |
| 📝 Write project plan manually | 🧠 AI generates structured roadmap |
| 🔨 Code everything from scratch | 🤖 Intelligent code generation |
| 🧪 Write tests manually | ✅ Auto-generated test coverage |
| 📚 Create docs manually | 📖 Documentation auto-created |
| 🔄 Manual git workflows | 🚀 Atomic commits with messages |

**Time saved on this simple project: ~90 minutes**
**For larger projects: 60-80% faster development**

---

*🎯 **Ready for more?** Continue with [**Your First Real Project
→**](tutorials/01-first-project.md) or explore [**Example Applications
→**](../examples/)*
