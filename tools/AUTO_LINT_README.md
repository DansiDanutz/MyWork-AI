# Automatic Markdownlint Tools

## 🎯 Overview

Three tools for maintaining professional markdown standards across the MyWork
repository:

1. **`auto_lint_fixer.py`** - Fixes common markdownlint violations
2. **`auto_lint_scheduler.py`** - Runs fixes automatically every 4 hours
3. **`start_auto_linter.sh`** - Background startup script

## ✅ Fixed Violation Types

| Rule | Description | Auto-Fixed |
| ------ | ------------- | ------------- |
| **MD022** | Headings without blank lines | ✅ |
| **MD032** | Lists without blank lines | ✅ |
| **MD031** | Code blocks without blank lines | ✅ |
| **MD058** | Tables without blank lines | ✅ |
| **MD047** | Missing trailing newlines | ✅ |

**Not auto-fixed (manual review needed):**

- MD013 (line length) - Often intentional
- MD024 (duplicate headings) - Common in changelogs
- MD040 (fenced code language) - Need specific language
- MD036 (emphasis as heading) - Structural decision

## 🚀 Usage

### One-Time Fix

```bash

# Fix all markdown files once

python3 tools/auto_lint_fixer.py

# See detailed output and summary

```markdown

### Automated Background Fixing

```bash

# Start background service (every 4 hours)

./start_auto_linter.sh

# Check logs

tail -f auto_linter.log

# Stop background service

pkill -f auto_lint_scheduler

```markdown

### Manual Scheduling

```bash

# Run once

python3 tools/auto_lint_scheduler.py

# Run every 4 hours

python3 tools/auto_lint_scheduler.py --daemon

# Custom interval (every 30 minutes)

python3 tools/auto_lint_scheduler.py --daemon --interval 1800

```markdown

## 📊 Recent Results

**Last Run:** Fixed **22,475 violations** across **235 files**

- MD022 (headings): 5,353 fixes
- MD032 (lists): 15,233 fixes
- MD031 (code blocks): 1,225 fixes
- MD058 (tables): 596 fixes
- MD047 (trailing newlines): 68 fixes

## 🔧 How It Works

### `auto_lint_fixer.py`

1. **Scans** all `.md` files (excluding `node_modules`)
2. **Applies fixes** for common violations:
   - Adds blank lines around headings
   - Adds blank lines around lists
   - Adds blank lines around code blocks
   - Fixes trailing newlines
   - Adds blank lines around tables
3. **Reports** summary of fixes applied

### `auto_lint_scheduler.py`

1. **Runs** the lint fixer
2. **Commits** changes automatically with detailed commit messages
3. **Schedules** next run (default: 4 hours)
4. **Logs** all activity for monitoring

## 📁 Files Processed

The tools scan these locations:

```markdown

✅ Root documentation (README.md, CHANGELOG.md, etc.)
✅ docs/ directory (all tutorials, guides, API reference)
✅ examples/ directory (example project documentation)
✅ .planning/ directory (project planning documents)
✅ projects/ subdirectories (individual project docs)
✅ workflows/ directory (framework workflows)
✅ reports/ directory (audit reports)

❌ node_modules/ (excluded)
❌ .git/ (excluded)
❌ __pycache__/ (excluded)

```markdown

## 🎛️ Configuration

### Markdownlint Rules

Uses standard markdownlint rules. To customize, create `.markdownlint.json`:

```json
{
  "MD013": false,
  "MD024": false,
  "MD040": false,
  "MD036": false
}

```markdown

### Automation Settings

Edit `auto_lint_scheduler.py` to change:

- **Interval**: `--interval 14400` (4 hours)
- **Timeout**: `timeout=300` (5 minutes per run)
- **Git behavior**: Automatic commits vs manual review

## 🚨 Safety Features

- **Timeout protection**: Commands timeout after 5 minutes
- **Error handling**: Continues on individual file errors
- **Git safety**: Only commits markdown files
- **Backup**: Original files preserved via git history
- **Encoding safety**: Handles UTF-8 and encoding errors gracefully

## 📝 Monitoring

### Check Status

```bash

# Is auto-linter running?

ps aux | grep auto_lint_scheduler

# View recent activity

tail -20 auto_linter.log

# Check git commits

git log --oneline | grep "auto-lint"

```markdown

### Expected Log Output

```yaml
🔍 [14:32:15] Checking for markdown lint issues...
🔧 Fixed 12 violations in 3 files
   • MD022: 8
   • MD032: 4
✅ Committed 12 fixes
⏰ Sleeping for 4 hours...

```markdown

## 💡 Tips

1. **Run manually** after major documentation changes
2. **Check logs regularly** to ensure automation is working
3. **Review commits** occasionally for unexpected changes
4. **Customize intervals** based on team workflow
5. **Use single runs** during development for immediate feedback

## 🔗 Integration

### With Git Hooks (Optional)

To keep linting out of your day-to-day git flow, hooks are **disabled by
default**.
If you want them, use `mw lint install-hooks` or add the following manually:

```bash

#!/bin/bash

python3 tools/auto_lint_fixer.py

```markdown

### With CI/CD

Add to GitHub Actions workflow:

```yaml

- name: Fix markdown lint issues

  run: python3 tools/auto_lint_fixer.py

```markdown

### With IDE

Configure your IDE to run on save:

```bash
python3 /path/to/MyWork/tools/auto_lint_fixer.py

```yaml

---

**🎉 Result:** Professional markdown standards maintained automatically across
the entire repository!
