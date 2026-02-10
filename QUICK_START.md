# 🚀 Quick Start Guide

Get up and running with MyWork-AI in 3 simple steps and start building 10x faster.

---

## ⚡ 3 Steps to Your First Project

### Step 1: Install & Setup (60 seconds)

```bash
# Install MyWork-AI
pip install mywork-ai

# Run first-time setup
mw setup
```

**What this does:**
- ✅ Verifies Python 3.11+ requirement
- ✅ Creates `.env` file for your API keys
- ✅ Sets up planning directory structure
- ✅ Runs health check to ensure everything works

### Step 2: Create Your First Project (30 seconds)

```bash
# Enhance your idea into a detailed specification
mw prompt-enhance "build a todo app with user authentication"

# Create the project (choose your template)
mw new my-todo-app fullstack
```

**Available Templates:**
- `basic` - Simple project structure
- `fastapi` - FastAPI web service with database
- `nextjs` - Next.js frontend application
- `fullstack` - FastAPI backend + Next.js frontend
- `cli` - Command-line tool with Click framework
- `automation` - n8n workflows + Python scripts

### Step 3: Start Building (30 seconds)

```bash
# Navigate to your project
cd projects/my-todo-app

# Let AutoForge handle the heavy lifting
mw af start my-todo-app

# Monitor progress with the dashboard
mw dashboard
```

**🎉 Congratulations!** You now have a complete project with:
- ✅ Project structure and boilerplate code
- ✅ 5-phase development roadmap
- ✅ Technical specifications and requirements
- ✅ Security considerations checklist
- ✅ Testing framework setup
- ✅ Autonomous development in progress

---

## 📚 Common Workflows

### 🔍 **Workflow 1: Building a SaaS Application**

```bash
# 1. Generate detailed requirements
mw prompt-enhance "build a SaaS invoice tool with Stripe payments and team collaboration"

# 2. Create full-stack project
mw new invoice-saas fullstack

# 3. Review the auto-generated plan
cd projects/invoice-saas
cat .planning/PROJECT.md
cat .planning/ROADMAP.md

# 4. Start autonomous development
mw af start invoice-saas

# 5. Monitor progress
mw af status
mw af progress invoice-saas
```

### 🤖 **Workflow 2: Building a CLI Tool**

```bash
# 1. Create CLI project
mw new deploy-helper cli

# 2. Navigate and explore structure
cd projects/deploy-helper
ls -la

# 3. Start coding with Brain assistance
mw brain search "CLI best practices"
mw brain search "argument parsing"

# 4. Add learnings as you work
mw brain add "Use Click for robust CLI argument parsing"
```

### 🔌 **Workflow 3: Building an API Service**

```bash
# 1. Enhance your API concept
mw prompt-enhance "build a REST API for user management with JWT auth and PostgreSQL"

# 2. Create FastAPI project
mw new user-api fastapi

# 3. Review generated structure
cd projects/user-api
tree .

# 4. Let AutoForge handle boilerplate
mw af start user-api

# 5. Check security compliance
mw security scan
```

### 🧠 **Workflow 4: Learning & Knowledge Management**

```bash
# Search your accumulated knowledge
mw brain search "authentication"
mw brain search "database optimization"
mw brain search "deployment"

# Add new learnings
mw brain add lesson "Always validate input before database writes"
mw brain add pattern "Use Redis for session storage in high-traffic apps"
mw brain add mistake "Never commit API keys to git - learned the hard way"

# Review what needs attention
mw brain review

# Let Brain auto-learn from your work
mw brain learn  # Daily learning extraction
mw brain learn-deep  # Weekly deep analysis
```

---

## 🛠️ Essential Commands

### Project Management
```bash
mw projects                  # List all your projects
mw projects scan             # Refresh project registry
mw new <name> <template>     # Create new project
mw open <name>               # Open project in VS Code
```

### Health & Diagnostics
```bash
mw status                    # Quick health check
mw dashboard                 # Interactive overview
mw doctor                    # Full system diagnostics
mw fix                       # Auto-fix common issues
```

### AutoForge (Autonomous Coding)
```bash
mw af start <project>        # Start AutoForge
mw af status                 # Check all AutoForge projects
mw af progress <project>     # Detailed progress report
mw af pause <project>        # Pause development
mw af resume <project>       # Resume development
mw af stop <project>         # Stop AutoForge
```

### Brain (Knowledge Management)
```bash
mw brain search <query>      # Search knowledge vault
mw brain add <content>       # Quick add a lesson
mw brain stats               # Brain statistics
mw brain export              # Export to markdown
```

### Quality & Security
```bash
mw lint scan                 # Code quality check
mw lint fix                  # Auto-fix linting issues
mw security scan             # Security audit
mw security report           # Detailed security report
```

---

## ❓ FAQ

### **Q: What Python version do I need?**
A: Python 3.11 or higher. MyWork-AI uses modern Python features and requires the latest stable version.

### **Q: Do I need API keys to get started?**
A: Not required for basic functionality! You can create projects, use the Brain, and explore templates without any API keys. API keys are only needed for:
- AutoForge (Claude API for autonomous coding)
- Advanced Brain features (OpenAI for semantic search)

### **Q: Can I use my existing projects?**
A: Yes! You can import existing projects:
```bash
# Copy your project to the MyWork projects directory
cp -r /path/to/existing/project projects/my-existing-project

# Scan to register it
mw projects scan

# Optionally add GSD planning structure
cd projects/my-existing-project
mkdir -p .planning
# Add PROJECT.md and ROADMAP.md manually or let AutoForge help
```

### **Q: How does AutoForge compare to GitHub Copilot?**
A: Different tools for different jobs:
- **GitHub Copilot**: Code completion and suggestions while you type
- **AutoForge**: Long-running autonomous agent that builds entire features, handles project structure, and follows your roadmap

They work great together! Use Copilot for day-to-day coding and AutoForge for larger tasks.

### **Q: Is my data secure?**
A: Yes, your data stays local:
- ✅ All projects stored locally in `projects/`
- ✅ Brain knowledge vault stored locally
- ✅ No telemetry or tracking
- ✅ API keys stored in `.env` (never transmitted except to respective services)

### **Q: How do I update MyWork-AI?**
A: Simple update command:
```bash
pip install --upgrade mywork-ai
mw status  # Verify everything still works
```

### **Q: Can I use this in a team?**
A: Absolutely! MyWork-AI works great for teams:
- **Shared Brain**: Export/import knowledge between team members
- **Consistent Structure**: All projects follow the same GSD methodology
- **Version Control**: Everything is git-friendly
- **Documentation**: Auto-generated docs keep everyone aligned

### **Q: What if I get stuck?**
A: Multiple layers of support:
1. **Built-in help**: `mw <command> --help` for any command
2. **Interactive guide**: `mw guide` for workflow tutorial  
3. **Diagnostics**: `mw doctor` identifies and suggests fixes
4. **Community**: [GitHub Discussions](https://github.com/DansiDanutz/MyWork-AI/discussions)
5. **Documentation**: Check [CLAUDE.md](CLAUDE.md) for detailed instructions

---

## 🐛 Troubleshooting

### **Installation Issues**

```bash
# Problem: pip install fails
# Solution: Ensure you have Python 3.11+
python --version  # Should show 3.11 or higher

# Problem: Command 'mw' not found
# Solution: Check your PATH or use full path
pip show mywork-ai  # Find installation location
python -m mywork_ai.mw status  # Use as module

# Problem: Permission errors on macOS/Linux
# Solution: Use user installation
pip install --user mywork-ai
```

### **Project Creation Issues**

```bash
# Problem: Templates not found
# Solution: Update to latest version
pip install --upgrade mywork-ai

# Problem: Project directory already exists
# Solution: Use different name or remove existing
rm -rf projects/my-project  # Be careful!
mw new my-project-v2 fastapi
```

### **AutoForge Issues**

```bash
# Problem: AutoForge won't start
# Solution: Check API configuration
cat .env  # Verify CLAUDE_API_KEY is set
mw doctor  # Run full diagnostics

# Problem: AutoForge seems stuck
# Solution: Check progress and restart if needed
mw af progress my-project
mw af stop my-project
mw af start my-project
```

### **Brain Issues**

```bash
# Problem: Search returns no results
# Solution: Add some knowledge first
mw brain add "My first lesson learned today"
mw brain search "lesson"

# Problem: Brain seems slow
# Solution: Check database and rebuild if needed
mw brain stats  # Check entry count
mw brain cleanup  # Remove duplicates
```

---

## 🎯 Next Steps

Once you're comfortable with the basics:

1. **📖 Read the Documentation**
   - [CLAUDE.md](CLAUDE.md) - Master orchestrator instructions
   - [ECOSYSTEM.md](ECOSYSTEM.md) - Complete ecosystem overview
   - [CHANGELOG.md](CHANGELOG.md) - Latest features and changes

2. **🛒 Explore the Marketplace**
   - [Browse Projects](https://frontend-hazel-ten-17.vercel.app)
   - Buy ready-made solutions
   - Sell your own projects

3. **🤝 Join the Community**
   - Share your projects in the marketplace
   - Contribute to the framework
   - Help other developers

4. **⚡ Advanced Features**
   - Set up automated linting: `mw lint install-hooks`
   - Configure security scanning: `mw security configure`
   - Set up team workflows: `mw team init`

---

<div align="center">

**🚀 Ready to build something amazing?**

```bash
pip install mywork-ai && mw setup
```

**[Browse Marketplace →](https://frontend-hazel-ten-17.vercel.app)** | **[View All Live Apps →](#)** | **[Read Full Docs →](README.md)**

</div>