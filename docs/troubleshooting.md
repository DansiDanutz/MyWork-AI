# MyWork Framework - Troubleshooting Guide

## 🚨 **Emergency Quick Fixes**

### **🔴 Something is broken and I need to work NOW**

```bash

# 1. Try the universal fix (solves 80% of issues)

mw doctor --fix

# 2. Check what's actually broken

mw status --verbose

# 3. If still broken, reset to known good state

git status  # See what changed
git checkout .  # WARNING: Loses uncommitted changes

```

### **🔴 Can't run any MyWork commands**

```bash

# 1. Verify you're in the right directory

pwd  # Should show .../MyWork
ls -la  # Should see tools/ and projects/ directories

# 2. Check Python and dependencies

python --version  # Should be 3.9+
python tools/mw.py status  # Try direct invocation

# 3. If still failing, reinstall

chmod +x install.sh && ./install.sh

```

---

## 🔍 **Diagnostic Tools**

### **Health Check (Start Here)**

```bash

# Quick health check

mw doctor

# Detailed diagnostic

mw doctor --report

# Auto-fix common issues

mw doctor --fix

# Check specific component

mw doctor --check dependencies
mw doctor --check services
mw doctor --check projects

```

### **Framework Status**

```bash

# Quick status

mw status

# Detailed status with versions

mw status --verbose

# JSON output for scripting

mw status --json

```

### **Project Status**

```bash

# Check current project progress

mw gsd progress

# See detailed project state

cat .planning/STATE.md

# Check for pending work

ls .planning/phases/*/

```

---

## 📋 **Common Issues & Solutions**

### **🔧 Installation & Setup Issues**

#### **Problem: "mw command not found"**

**Symptoms:**

```bash
$ mw status
bash: mw: command not found

```

**Solutions:**

1. **Use direct path:**

   ```bash
   cd /Users/dansidanutz/Desktop/MyWork
   python tools/mw.py status

   ```

2. **Add to PATH (optional):**

   ```bash

   # Add to ~/.bashrc or ~/.zshrc

   export PATH="/Users/dansidanutz/Desktop/MyWork/tools:$PATH"
   alias mw="python /Users/dansidanutz/Desktop/MyWork/tools/mw.py"

   ```

3. **Use full commands:**

   ```bash
   python tools/mw.py status
   python tools/mw.py new my-project

   ```

#### **Problem: Python dependency errors**

**Symptoms:**

```bash
ModuleNotFoundError: No module named 'click'
ModuleNotFoundError: No module named 'rich'

```

**Solution:**

```bash

# Install missing dependencies

pip install -r requirements.txt

# Or install specific packages

pip install click rich requests

# Verify installation

python -c "import click; print('Click installed')"

```

#### **Problem: Permission denied errors**

**Symptoms:**

```bash
Permission denied: '/Users/dansidanutz/Desktop/MyWork/tools/mw.py'

```

**Solution:**

```bash

# Fix file permissions

chmod +x tools/mw.py
chmod +x install.sh

# Or run with python directly

python tools/mw.py status

```

### **🚀 GSD (Planning & Execution) Issues**

#### **Problem: "No planning structure found"**

**Symptoms:**

```bash
$ mw gsd progress
No planning structure found.
Run /gsd:new-project to start a new project.

```

**Solutions:**

1. **Check you're in a project directory:**

   ```bash
   pwd  # Should be in projects/your-project/
   ls -la .planning/  # Should exist with files

   ```

2. **Initialize GSD if missing:**

   ```bash
   mw gsd new-project

   ```

3. **Navigate to correct project:**

   ```bash
   cd projects/your-project-name/
   mw gsd progress

   ```

#### **Problem: GSD execution fails or hangs**

**Symptoms:**

- Plans start executing but never complete
- Error messages about missing files
- Processes appear stuck

**Solutions:**

1. **Check current phase status:**

   ```bash
   cat .planning/STATE.md
   ls .planning/phases/*/

   ```

2. **Look for error details:**

   ```bash

   # Check the last plan that ran

   ls .planning/phases/[phase]/ -la
   cat .planning/phases/[phase]/[plan]-SUMMARY.md

   ```

3. **Resume from checkpoint:**

   ```bash
   mw gsd resume-work

   ```

4. **Re-run specific phase:**

   ```bash
   mw gsd execute-phase [phase-number]

   ```

5. **Create gap closure plans:**

   ```bash
   mw gsd plan-phase [phase] --gaps

   ```

#### **Problem: Planning generates unclear or wrong requirements**

**Symptoms:**

- Generated roadmap doesn't match your vision
- Requirements are too vague or too specific
- Missing key features you mentioned

**Solutions:**

1. **Re-run with more specific input:**

   ```bash

   # Delete current planning

   rm -rf .planning/

   # Start over with clearer descriptions

   mw gsd new-project

   # Provide more detailed, specific answers

   ```

2. **Use discussion mode first:**

   ```bash
   mw gsd discuss-phase [phase]

   # Clarify implementation approach before planning

   ```

3. **Manually edit requirements:**

   ```bash

   # Edit the generated requirements

   nano .planning/REQUIREMENTS.md
   nano .planning/PROJECT.md

   # Then re-plan phases

   mw gsd plan-phase [phase]

   ```

### **🤖 Autocoder Issues**

#### **Problem: "Autocoder server not responding"**

**Symptoms:**

```bash
$ mw ac status
❌ Autocoder Server: Not responding on port 8888

```

**Solutions:**

1. **Start the server:**

   ```bash
   mw ac server

   ```

2. **Check if port is in use:**

   ```bash
   lsof -i :8888

   # If something else is using it, kill it or use different port

   ```

3. **Reset server:**

   ```bash
   pkill -f autocoder  # Kill any existing processes
   mw ac server --port 8889  # Start on different port

   ```

#### **Problem: Autocoder runs out of memory or crashes**

**Symptoms:**

- Browser shows "Server Error"
- Autocoder stops mid-execution
- Very slow performance

**Solutions:**

1. **Reduce concurrency:**

   ```bash
   mw ac start my-project --concurrency 1  # Instead of 3-5

   ```

2. **Use smaller model:**

   ```bash
   mw ac start my-project --model claude-haiku  # Instead of opus

   ```

3. **Check system resources:**

   ```bash
   top  # Check CPU/memory usage
   df -h  # Check disk space

   ```

4. **Restart Autocoder:**

   ```bash
   mw ac stop my-project
   mw ac server  # Restart server
   mw ac start my-project --concurrency 1

   ```

### **🔗 n8n Integration Issues**

#### **Problem: "n8n MCP server not found"**

**Symptoms:**

```bash
n8n tools not available
MCP server connection failed

```

**Solutions:**

1. **Install n8n MCP server:**

   ```bash
   npx n8n-mcp

   ```

2. **Check MCP configuration:**

   ```bash
   cat .mcp.json  # Should have n8n-mcp entry

   ```

3. **Test n8n connection:**

   ```bash

   # Try basic n8n command

   python -c "from tools.n8n_api import *; print('n8n tools available')"

   ```

#### **Problem: n8n workflow creation fails**

**Symptoms:**

- Workflows fail validation
- Nodes don't connect properly
- Runtime errors in workflows

**Solutions:**

1. **Start with templates:**

   ```bash

   # Search for similar templates first

   # Use n8n-skills: search_templates, get_template

   ```

2. **Validate before deploying:**

   ```bash

   # Always validate workflows before deployment

   # Use validate_workflow tool

   ```

3. **Check node configurations:**

   ```bash

   # Verify all required parameters are set

   # Use validate_node tool for each node

   ```

### **💾 Data & File Issues**

#### **Problem: Git repository issues**

**Symptoms:**

```bash
fatal: not a git repository
Your branch is behind 'origin/main'

```

**Solutions:**

1. **Initialize git if needed:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"

   ```

2. **Sync with remote:**

   ```bash
   git fetch origin
   git merge origin/main

   ```

3. **Reset to clean state:**

   ```bash
   git status  # See what's changed
   git stash   # Save changes temporarily
   git pull    # Get latest
   git stash pop  # Restore changes

   ```

#### **Problem: Disk space full**

**Symptoms:**

```bash
OSError: [Errno 28] No space left on device

```

**Solutions:**

1. **Clean MyWork temporary files:**

   ```bash
   rm -rf .tmp/*
   rm -rf projects/*/node_modules/
   find . -name "__pycache__" -exec rm -rf {} +

   ```

2. **Clean system temporary files:**

   ```bash

   # macOS

   rm -rf ~/Library/Caches/*

   # Linux

   rm -rf /tmp/*

   ```

3. **Archive old projects:**

   ```bash

   # Move completed projects to archive

   mkdir archive
   mv projects/completed-project archive/

   ```

---

## 🔧 **Advanced Troubleshooting**

### **Debug Mode & Logging**

#### **Enable detailed logging:**

```bash

# Set debug environment variables

export MYWORK_DEBUG=1
export LOG_LEVEL=DEBUG

# Run commands with verbose output

mw status --verbose
mw gsd execute-phase 1 --verbose

```

#### **Check log files:**

```bash

# Framework logs

cat .tmp/mywork.log

# Project-specific logs

cat .planning/debug.log

# Git history for clues

git log --oneline -20

```

### **Configuration Issues**

#### **Reset configuration to defaults:**

```bash

# Backup current config

cp .planning/config.json .planning/config.json.backup

# Reset to defaults

cat > .planning/config.json << 'EOF'
{
  "mode": "balanced",
  "research": true,
  "verification": true,
  "brain_learning": true,
  "commit_planning_docs": true
}
EOF

```

#### **Check environment variables:**

```bash

# Required variables

echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:10}..."
echo "MYWORK_ROOT: $MYWORK_ROOT"

# Optional variables

echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..."
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:0:10}..."

```

### **Performance Issues**

#### **Framework running slowly:**

1. **Check resource usage:**

   ```bash
   top -p $(pgrep -f python)

   ```

2. **Reduce AI calls:**

   ```bash

   # Use fast mode

   echo '{"mode": "fast"}' > .planning/config.json

   # Skip research

   mw gsd plan-phase 1 --skip-research

   ```

3. **Clear caches:**

   ```bash
   rm -rf .tmp/cache/
   rm -rf ~/.cache/anthropic/

   ```

#### **Large project optimization:**

1. **Use selective execution:**

   ```bash

   # Execute specific plans only

   mw gsd execute-phase 1  # Just one phase

   ```

2. **Break into smaller phases:**

   ```bash

   # Split large phases

   mw gsd insert-phase 2.1  # Insert between phases

   ```

---

## 🆘 **When All Else Fails**

### **Nuclear Reset (Lose all progress)**

```bash

# 1. Backup current state

cp -r .planning/ .planning-backup/
git add . && git commit -m "backup before reset"

# 2. Reset framework

rm -rf .planning/
git checkout .

# 3. Restart project

mw gsd new-project

```

### **Partial Reset (Keep some progress)**

```bash

# Keep project definition but reset execution

rm -rf .planning/phases/
rm .planning/STATE.md

# Regenerate roadmap

mw gsd new-project --resume

```

### **Get Help**

If you're still stuck:

1. **Gather diagnostic info:**

   ```bash
   mw doctor --report > debug_report.txt
   mw status --verbose >> debug_report.txt
   cat .planning/STATE.md >> debug_report.txt

   ```

2. **Ask for help:**
   - 💬 **[GitHub Discussions](https://github.com/DansiDanutz/MyWork-AI/discussions)** - Attach debug report
   - 🐛 **[GitHub Issues](https://github.com/DansiDanutz/MyWork-AI/issues)** - If it's a bug
   - 📧 **[Email Support](mailto:support@mywork.ai)** - For urgent issues

3. **Include this info:**
   - What you were trying to do
   - What happened instead
   - Error messages (full text)
   - Your debug_report.txt
   - Steps to reproduce

---

## ✅ **Prevention**

### **Avoid future issues:**

1. **Run regular maintenance:**

   ```bash

   # Weekly

   mw doctor
   mw update --check
   mw brain learn

   # After each project

   git status  # Commit your work
   mw status   # Verify everything is healthy

   ```

2. **Keep backups:**

   ```bash

   # Backup important projects

   tar -czf project-backup.tar.gz projects/important-project/

   # Use git properly

   git add . && git commit -m "Checkpoint"

   ```

3. **Monitor health:**

   ```bash

   # Add to your shell profile

   alias mw-check="cd /Users/dansidanutz/Desktop/MyWork && mw status"

   # Run before starting work

   mw-check

   ```

---

*💡 **Pro Tip:** Most issues are environmental (wrong directory, missing dependencies, configuration). The diagnostic commands above will catch 90% of problems.*
