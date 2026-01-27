# Tutorial 1: Your First Project

**Goal:** Create a working task manager CLI in 15 minutes and learn MyWork fundamentals.

**What you'll learn:**
- ✅ GSD project planning and execution
- ✅ The 3-layer framework architecture in action
- ✅ Basic CLI usage and project structure
- ✅ How to verify and test your work

**Time:** 15 minutes
**Skill level:** Beginner (no programming experience required)

---

## 📋 **What We're Building**

A simple command-line task manager that can:
- Add new tasks
- List all tasks
- Mark tasks as complete
- Search tasks by keyword

**Example usage:**
```bash
python task_manager.py add "Learn MyWork framework"
python task_manager.py list
python task_manager.py complete 1
```

---

## ⚡ **Step 1: Create the Project** *(3 minutes)*

### **1.1 Navigate to projects directory**
```bash
cd /Users/dansidanutz/Desktop/MyWork
ls projects/  # See existing projects
```

### **1.2 Create your project**
```bash
mw new task-manager-cli cli
```

**What just happened?**
- Created `projects/task-manager-cli/` directory
- Set up basic project structure with GSD planning
- Generated initial `PROJECT.md`, `ROADMAP.md`, and `STATE.md`

### **1.3 Navigate to your new project**
```bash
cd projects/task-manager-cli
ls -la  # Explore the structure
```

**You should see:**
```
.planning/          # GSD state management
├── PROJECT.md      # Vision and goals
├── STATE.md        # Current progress
└── config.json     # Project settings
README.md           # Getting started guide
project.yaml        # Project metadata
```

---

## 🎯 **Step 2: Plan Your Project** *(4 minutes)*

### **2.1 Start GSD planning**
```bash
mw gsd new-project
```

**Follow the interactive prompts:**

**Project description:**
```
A simple CLI task manager for developers who want quick task tracking from the terminal.
```

**Target audience:**
```
Developers and power users who prefer command-line tools.
```

**Key features:**
```
Add tasks, list tasks, mark as complete, search by keyword, persistent storage.
```

**Success criteria:**
```
Can manage a personal todo list entirely from the command line with intuitive commands.
```

### **2.2 Review the generated roadmap**
```bash
cat .planning/ROADMAP.md
```

**You should see something like:**
```markdown
Phase 1: Foundation & Core Commands (3-5 features)
Phase 2: Storage & Persistence (2-3 features)
Phase 3: Search & Filtering (2-3 features)
Phase 4: Polish & Documentation (2-3 features)
```

**Check your current status:**
```bash
mw gsd progress
```

---

## 🏗️ **Step 3: Build Phase 1** *(6 minutes)*

### **3.1 Plan the first phase**
```bash
mw gsd plan-phase 1
```

**GSD will:**
- Research CLI best practices automatically
- Break down "Foundation & Core Commands" into specific tasks
- Create executable plans with verification criteria

**Wait for the message:** `Phase 1 planned ✓`

### **3.2 Execute the first phase**
```bash
mw gsd execute-phase 1
```

**Watch the magic happen:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► EXECUTING WAVE 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Task 1: Create CLI argument parser... ✅ (commit abc123d)
◆ Task 2: Implement data storage... ✅ (commit def456e)
◆ Task 3: Add basic commands... ✅ (commit ghi789f)
◆ Task 4: Add tests and documentation... ✅ (commit jkl012m)

Wave 1 complete!
```

### **3.3 Check what was created**
```bash
ls src/  # See the generated code
cat src/task_manager.py | head -20  # Preview the implementation
```

---

## 🧪 **Step 4: Test Your Creation** *(2 minutes)*

### **4.1 Try the basic commands**
```bash
# Add some tasks
python src/task_manager.py add "Learn MyWork framework"
python src/task_manager.py add "Build my first CLI app"
python src/task_manager.py add "Share my project with friends"

# List all tasks
python src/task_manager.py list
```

**Expected output:**
```
📋 Your Tasks:
1. [ ] Learn MyWork framework
2. [ ] Build my first CLI app
3. [ ] Share my project with friends
```

### **4.2 Mark a task complete**
```bash
python src/task_manager.py complete 1
python src/task_manager.py list
```

**Expected output:**
```
📋 Your Tasks:
1. [✅] Learn MyWork framework
2. [ ] Build my first CLI app
3. [ ] Share my project with friends
```

### **4.3 Test help and other features**
```bash
python src/task_manager.py --help
python src/task_manager.py stats  # If implemented
```

---

## ✅ **Verification & Next Steps** *(1 minute)*

### **Check your progress**
```bash
mw gsd progress
```

**You should see:**
- ✅ Phase 1 completed
- 🎯 Ready for Phase 2 (or "Milestone complete" if this was a simple project)

### **What you just experienced**

| Traditional Development | MyWork Framework |
|------------------------|------------------|
| ⏱️ **2-3 hours** manual coding | ⚡ **6 minutes** guided execution |
| 📝 Write requirements manually | 🧠 AI generates structured plan |
| 🔨 Code from scratch | 🤖 Intelligent code generation |
| 🧪 Write tests manually | ✅ Auto-generated test coverage |
| 📚 Create docs manually | 📖 Documentation auto-created |

**Time saved:** ~2.5 hours for this simple project!

---

## 🚀 **What's Next?**

### **Option A: Complete Your Task Manager**
```bash
# Continue with Phase 2 (adds search, better storage, etc.)
mw gsd execute-phase 2

# Or plan it first to see what will be built
mw gsd plan-phase 2
```

### **Option B: Start Tutorial 2**
Ready for a web app? → [**Tutorial 2: GSD Basics →**](02-gsd-basics.md)

### **Option C: Explore Your Project**
- **View the code:** `code .` (opens in VS Code)
- **Read the docs:** `cat README.md`
- **Check git history:** `git log --oneline`
- **Run tests:** `python -m pytest tests/` (if generated)

---

## 🆘 **Troubleshooting**

### **❌ "mw command not found"**
```bash
# You might not be in the MyWork directory
cd /Users/dansidanutz/Desktop/MyWork
python tools/mw.py new task-manager-cli cli
```

### **❌ "No planning structure found"**
```bash
# Make sure you're in your project directory
pwd  # Should show .../MyWork/projects/task-manager-cli
ls .planning/  # Should show PROJECT.md, STATE.md, etc.
```

### **❌ "Generated code doesn't work"**
```bash
# Run the built-in verification
mw gsd verify-work

# Check for issues
mw doctor
```

### **❌ "Need more features"**
```bash
# Continue to the next phase
mw gsd progress  # See what's next
mw gsd execute-phase 2  # Add more features
```

---

## 🎉 **Congratulations!**

In just 15 minutes, you've:
- ✅ **Created** a working CLI application
- ✅ **Experienced** the GSD workflow (plan → execute → verify)
- ✅ **Learned** the 3-layer architecture in action
- ✅ **Understood** how MyWork accelerates development

### **Key Concepts Learned:**

1. **GSD Layer** - Project orchestration and planning
2. **WAT Layer** - Task execution and code generation
3. **Automation Layer** - AI agents doing the heavy lifting
4. **Brain Learning** - Framework gets smarter with each project
5. **Atomic Commits** - Each task creates clean, focused commits
6. **Verification** - Built-in testing and validation

---

**Ready for Tutorial 2?** → [**Understanding GSD Workflow →**](02-gsd-basics.md)

*💡 This tutorial introduced you to 20% of MyWork's capabilities. Tutorial 2 will show you how to handle more complex web applications and advanced GSD features.*
