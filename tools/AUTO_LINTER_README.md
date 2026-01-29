# Auto-Linting Scheduler 🎯

**Status: ✅ ACTIVE - Scheduled markdown fixes every 4 hours**

The MyWork Framework includes a scheduled auto-linting system that keeps
markdown files healthy without interfering with day-to-day git workflows.
Linting is **out of the git flow by default** and runs on a schedule.

## 🚀 Quick Start (For All Users)

### Enable Scheduled Auto-Linting

```bash

# Start the lint scheduler (runs every 4 hours)

mw lint start

# Install git hooks (optional; keeps linting out by default)

mw lint install-hooks

# Check status

mw lint status

```markdown

That's it! Scheduled markdown fixes are now running without disrupting your
commit/push workflow.

## 🎯 What It Does

### Automatic Fixing (12+ Rules)

The auto-linter automatically fixes these markdown violations:

- **MD013**: Line length enforcement
- **MD022**: Heading blank line spacing
- **MD031**: Fenced code block spacing
- **MD032**: List spacing
- **MD034**: Bare URL wrapping
- **MD036**: Emphasis-as-heading conversion
- **MD040**: Code language specification
- **MD046**: Indented to fenced code blocks
- **MD047**: Trailing newlines
- **MD051**: Link fragment validation
- **MD058**: Table spacing
- **MD060**: Table column style with pipe spacing

### Reliable by Design

- ✅ **Robust Error Handling**: Never crashes or stops on problematic files
- ✅ **Self-Healing**: Fixes issues created during processing
- ✅ **Cross-Platform**: Works on macOS, Linux, and Windows
- ✅ **Git-Friendly**: Hooks are optional and disabled by default

## 📋 Available Commands

```bash

# Scheduled Linting Management

mw lint start                 # Start scheduler (every 4 hours)
mw lint stop                  # Stop scheduler
mw lint status                # Check scheduler status
mw lint install-hooks         # Optional: add git hooks
mw lint uninstall-hooks       # Remove git hooks

# Manual Operations

mw lint scan                  # Scan all files once
mw lint fix                   # Fix all issues once
mw lint watch                 # Watch files manually
mw lint config --show         # Show configuration
mw lint stats                 # Show statistics

```markdown

## 🔧 How It Works

### Scheduled Mode (Default)

When you run `mw lint start`, the scheduler:

1. **Runs every 4 hours** (configurable)
2. **Fixes markdownlint violations** in batch
3. **Keeps linting out of git flow** by default
4. **Logs results** for visibility

### Watch Mode (Optional)

If you want real-time fixes while editing:

- Run `mw lint watch` to start a file watcher
- This is **optional** and not enabled by default

### Git Hook Mode (Optional)

When you run `mw lint install-hooks`, git operations will:

1. **Pre-commit**: Fix all markdown files before committing
2. **Pre-push**: Verify markdown quality before pushing
3. **Auto-fix**: Resolve any issues and prompt for review

## 💡 For All Users

### New Team Members

New team members can enable scheduled linting by running:

- `mw lint start` (runs every 4 hours)
- `mw lint install-hooks` only if they want lint checks in git operations

### Existing Team Members

Existing team members can enable it by running:

```bash
mw lint start           # Enable automatic fixing
mw lint install-hooks   # Optional: enable git integration

```markdown

### CI/CD Integration

Add to your CI pipeline:

```bash

# Check markdown quality in CI

python3 tools/auto_lint_fixer.py .
markdownlint . || exit 1

```markdown

## 🎯 Benefits

### For Users

- **Zero manual work**: Markdown issues fixed automatically
- **Perfect quality**: Always 0 markdownlint violations
- **No interruptions**: Fixes happen transparently
- **Universal**: Works the same for everyone

### For Teams

- **Consistent quality**: All documentation is consistently formatted
- **No review delays**: Markdown issues never block PRs
- **Reduced maintenance**: No manual markdown cleanup needed
- **Professional appearance**: All docs look polished

### For Projects

- **Documentation quality**: Consistent markdown enhances project credibility
- **Automation**: One less thing to worry about
- **Scalability**: Works for projects of any size
- **Reliability**: Never breaks or stops working

## 🔍 Technical Details

### Architecture

```text
Scheduled Runs → Auto-Fixer → Consistent Markdown

```text

 ↓              ↓             ↓              ↓

```markdown

Git Commits → Git Hooks (Optional) → Auto-Fixer → Clean Commits

```markdown

### Files

- `auto_lint_fixer.py` - Markdown fixing engine
- `auto_lint_scheduler.py` - Scheduled runner (default every 4 hours)
- `auto_linting_agent.py` - Optional file watcher
- `lint_watcher.py` - Scheduler manager
- `start_auto_linter.sh/bat` - Cross-platform startup scripts
- `mw.py lint` - User-friendly management commands

### Zero Configuration

The auto-linter works out of the box with no configuration needed. It
intelligently:

- Detects all markdown files
- Applies appropriate fixes based on content
- Handles edge cases gracefully
- Never corrupts files

## 🚀 Deployment

### For Framework Administrators

To ensure all users get scheduled auto-linting:

1. **Enable by default in new projects:**

   ```bash

   # Add to project templates

   mw lint start

   # Optional: mw lint install-hooks

```yaml

2. **Include in setup instructions:**

   ```bash

   # Add to onboarding docs

   git clone <project>
   cd <project>
   mw lint start

```yaml

3. **CI/CD validation:**

   ```bash

   # Ensure markdown quality in CI

   python3 tools/auto_lint_fixer.py .
   markdownlint . || exit 1

```markdown

### For Project Owners

Enable scheduled markdown quality for your entire team:

```bash
mw lint start           # Start monitoring
mw lint install-hooks   # Set up git integration
git add .git/hooks/     # Commit hooks for all users
git commit -m "feat: add scheduled auto-linting for docs"
git push

```markdown

Now every team member gets automatic markdown fixing!

## ✅ Success Metrics

Perfect auto-linting is working when:

- ✅ `markdownlint .` returns 0 violations across all files
- ✅ `mw lint status` shows auto-linter is running
- ✅ Markdown files are automatically fixed as you type/save
- ✅ Git commits never fail due to markdown issues
- ✅ All team members have consistent markdown quality

---

**The Perfect Auto-Linting Agent: Because markdown quality should be automatic,
not optional.**
