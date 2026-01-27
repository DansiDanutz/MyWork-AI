# MyWork Framework - Frequently Asked Questions

## 🚀 **Getting Started**

### **Q: I'm completely new to MyWork. Where should I start?**

**A:** Follow this exact path:

1. **5-minute start:** [Quick Start Guide](quickstart.md) - Install and create your first project
2. **Learn the basics:** [Tutorial 1: Your First Project](tutorials/01-first-project.md) - Build a CLI task manager
3. **Understand the system:** [Architecture Overview](architecture/overview.md) - Learn the 3 layers
4. **Try a web app:** [Tutorial 2: GSD Basics](tutorials/02-gsd-basics.md) - Build a todo web app

You'll be productive within 30 minutes.

### **Q: What's the difference between MyWork and other frameworks?**

**A:** MyWork is **AI-first development infrastructure**:

| Traditional Frameworks | MyWork Framework |
|------------------------|------------------|
| 🔧 **Tools** - You write all the code | 🧠 **Intelligence** - AI writes most code |
| 📝 **Documentation** - You plan manually | 🗺️ **Roadmaps** - AI generates structured plans |
| 🐛 **Debug** - You fix issues manually | ✅ **Verification** - Built-in quality gates |
| 🔄 **Refactor** - Expensive to change | 🎯 **Adaptive** - Changes are easy |

### **Q: Do I need to know programming to use MyWork?**

**A:** **No programming experience required!**

- **Describe what you want** - MyWork generates the code
- **Review and test** - You verify it works as expected
- **Deploy and iterate** - Framework handles technical details

However, programming knowledge helps you:
- Customize generated code
- Debug complex issues
- Add advanced features

## 🏗️ **Using GSD (Get Shit Done)**

### **Q: What exactly is GSD and when should I use it?**

**A:** GSD is the **project orchestration layer**. Use it for:

- ✅ **New projects** from scratch
- ✅ **Major features** (5+ tasks)
- ✅ **Complex planning** (multiple phases)
- ✅ **Quality assurance** (verification needed)

**Don't use GSD for:**
- ❌ Quick bug fixes
- ❌ Single-file changes
- ❌ Configuration updates

### **Q: My GSD planning feels too complex. Can I simplify it?**

**A:** Yes! Try these approaches:

```bash
# 1. Skip research if you know the domain
mw gsd plan-phase 1 --skip-research

# 2. Use quick mode for simple tasks
mw gsd quick

# 3. Adjust planning depth in config
# Edit .planning/config.json:
{
  "mode": "fast",        // vs "thorough"
  "research": false,     // Skip automatic research
  "verification": false  // Skip verification loops
}
```

### **Q: How do I know if a phase is too big or too small?**

**A:** **Good phase sizes:**

- **Small (1-2 hours):** 3-5 features, 1-2 plans
- **Medium (4-6 hours):** 6-10 features, 2-4 plans
- **Large (1-2 days):** 10-15 features, 4-6 plans

**Too big indicators:**
- More than 6 plans in a phase
- Estimated time over 2 days
- Multiple independent concerns mixed together

**Fix:** Split into smaller phases.

### **Q: Can I change requirements mid-project?**

**A:** Absolutely! GSD is designed for change:

```bash
# Pause current work
mw gsd pause-work

# Add new requirements
# Edit .planning/REQUIREMENTS.md

# Add new phases
mw gsd add-phase

# Insert urgent work
mw gsd insert-phase 2.5

# Resume with new plan
mw gsd resume-work
```

## 🤖 **Autocoder Integration**

### **Q: When should I use Autocoder vs GSD?**

**A:** Decision tree:

```
How many features?
├── < 10 features → Use GSD
├── 10-20 features → GSD with Autocoder for complex parts
└── 20+ features → Full Autocoder

How long will it take?
├── < 2 hours → Use GSD
├── 2-8 hours → GSD or Autocoder
└── 8+ hours → Autocoder (multi-session)

How familiar is the domain?
├── Well-known → GSD is fine
├── Some unknowns → GSD with research
└── Lots of unknowns → Autocoder exploration
```

### **Q: Autocoder is too slow. How can I speed it up?**

**A:** Several options:

```bash
# 1. Increase concurrency (more parallel agents)
mw ac start my-project --concurrency 5

# 2. Skip testing for speed (YOLO mode)
mw ac start my-project --concurrency 3 --yolo

# 3. Use faster model
mw ac start my-project --model claude-haiku

# 4. Reduce scope (fewer features)
# Edit your app_spec.txt to focus on core features first
```

### **Q: How do I monitor Autocoder progress?**

**A:** Multiple ways:

```bash
# 1. Check progress in terminal
mw ac progress my-project

# 2. Follow progress continuously
mw ac progress my-project --follow

# 3. Open web UI for visual monitoring
mw ac ui

# 4. Check project files directly
ls projects/my-project/src/
```

## 🔗 **n8n Workflow Automation**

### **Q: I'm new to n8n. What should I know?**

**A:** n8n is **visual workflow automation**:

- **Use for:** Webhooks, API integration, data processing, scheduled tasks
- **Don't use for:** User interfaces, complex business logic
- **Think:** "If This Then That" but much more powerful

**Start here:**
- Browse [2,709 templates](https://n8n.io/workflows/)
- Practice with [Tutorial 2: GSD Basics](tutorials/02-gsd-basics.md)

### **Q: How do I connect GSD projects with n8n?**

**A:** Common patterns:

1. **GSD builds app → n8n handles webhooks:**
   ```bash
   # GSD builds your API
   mw gsd plan-phase 2  # API development

   # n8n processes webhooks
   # Use create_n8n_workflow.md workflow
   ```

2. **n8n triggers GSD deployments:**
   - GitHub webhook → n8n → trigger deployment
   - Form submission → n8n → create GSD task

3. **Data flows through n8n:**
   - User action → GSD app → n8n → external services

## 🛠️ **Troubleshooting**

### **Q: Something is broken. How do I diagnose issues?**

**A:** Follow this checklist:

```bash
# 1. Run health check (fixes most issues)
mw doctor

# 2. Check framework status
mw status

# 3. Look at recent work
mw gsd progress

# 4. Check for pending issues
cat .planning/STATE.md

# 5. Verify environment
mw doctor --check dependencies
```

### **Q: GSD execution failed. What now?**

**A:** Debugging steps:

```bash
# 1. Check what failed
cat .planning/phases/[phase]/[phase]-VERIFICATION.md

# 2. Look at the last plan that ran
ls .planning/phases/[phase]/
cat .planning/phases/[phase]/[plan]-SUMMARY.md

# 3. Check git history for clues
git log --oneline -10

# 4. Create gap closure plans
mw gsd plan-phase [phase] --gaps
```

### **Q: Generated code doesn't match my style. How do I fix this?**

**A:** Set preferences before planning:

```bash
# 1. Discuss implementation preferences
mw gsd discuss-phase [next-phase]

# 2. Add coding standards to context
# During discussion, specify:
# - Code formatting preferences
# - Naming conventions
# - Library preferences
# - Architecture patterns

# 3. Plan with your preferences
mw gsd plan-phase [phase]
```

### **Q: MyWork is using too much disk space. How do I clean up?**

**A:** Cleanup commands:

```bash
# 1. Clean temporary files
rm -rf .tmp/*

# 2. Clean old planning artifacts
# (Be careful - only if you're sure)
rm -rf .planning/archive/*

# 3. Clean node_modules in projects
find projects/ -name "node_modules" -type d -exec rm -rf {} +

# 4. Clean Python caches
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 📊 **Best Practices**

### **Q: How should I organize multiple projects?**

**A:** Recommended structure:

```
MyWork/
├── projects/
│   ├── personal/           # Personal projects
│   │   ├── task-manager/
│   │   └── blog/
│   ├── work/              # Work projects
│   │   ├── api-service/
│   │   └── dashboard/
│   └── experiments/       # Learning/testing
│       ├── ai-experiments/
│       └── tutorials/
├── templates/             # Your custom templates
└── workflows/             # Custom workflows
```

### **Q: How do I share projects with my team?**

**A:** Team collaboration options:

1. **Share the entire project:**
   ```bash
   # Project includes all planning and code
   git clone <your-project-repo>
   cd project-name
   mw gsd progress  # See current state
   ```

2. **Share just the planning:**
   ```bash
   # Send .planning/ directory
   # Others can execute the plans
   mw gsd execute-phase [current-phase]
   ```

3. **Share templates:**
   ```bash
   # Create reusable template from project
   cp -r projects/my-success templates/my-template
   # Others can use: mw new their-project my-template
   ```

### **Q: Should I commit .planning/ files to git?**

**A:** **Yes, definitely!**

✅ **Commit these:**
- `PROJECT.md` - Project vision
- `ROADMAP.md` - Development phases
- `REQUIREMENTS.md` - Feature specifications
- Phase plans and summaries
- `STATE.md` - Current progress

❌ **Don't commit:**
- Temporary files (.tmp)
- Large binary artifacts
- API keys in planning docs

**Why commit planning?**
- Team can see project vision and progress
- New team members understand the roadmap
- Planning history helps debug issues
- Cross-session continuity when switching machines

## 🎓 **Learning Resources**

### **Q: I want to understand how MyWork works under the hood. Where do I start?**

**A:** Technical deep dive path:

1. **[Architecture Overview](architecture/overview.md)** - Understand the 3 layers
2. **[Python API Reference](api/tools/)** - See the actual tools
3. **[Example Projects](../examples/)** - Learn the automation patterns
4. **[Framework Source Code](https://github.com/DansiDanutz/MyWork-AI)** - Study the implementation

### **Q: How can I contribute to MyWork?**

**A:** Many ways to help:

1. **Report issues:** [GitHub Issues](https://github.com/MyWork-AI/framework/issues)
2. **Share examples:** Add to `examples/` directory
3. **Improve docs:** Fix typos, add clarifications
4. **Create templates:** Add new project templates
5. **Build integrations:** Connect with other tools

### **Q: Where can I get help that's not in this FAQ?**

**A:** Support channels:

- 💬 **[GitHub Discussions](https://github.com/MyWork-AI/framework/discussions)** - Community Q&A
- 🐛 **[GitHub Issues](https://github.com/MyWork-AI/framework/issues)** - Bug reports
- 📧 **[Email Support](mailto:support@mywork.ai)** - Direct help
- 📺 **[YouTube Channel](https://youtube.com/@MyWorkAI)** - Video tutorials
- 🐦 **[Twitter](https://twitter.com/MyWorkAI)** - Updates and tips

---

## 💡 **Pro Tips**

### **Speed up development:**
- Use `mw search "keyword"` before building anything new
- Run `mw brain learn` after completing work to capture patterns
- Keep `mw status` bookmarked for quick health checks

### **Avoid common mistakes:**
- Don't skip verification - it catches issues early
- Don't make phases too large - keep under 2 days of work
- Don't ignore health check warnings - fix them before they compound

### **Maximize framework intelligence:**
- Let GSD research for you instead of skipping it
- Use the brain search before planning new features
- Review module registry for reusable patterns

---

*💬 **Still have questions?** Ask in [GitHub Discussions](https://github.com/MyWork-AI/framework/discussions) - the community is helpful and responsive!*
