# Auto-Linting Agent

The Auto-Linting Agent is a tool that fixes code quality issues across your
MyWork framework. It supports multiple linting tools and can run on a schedule
(default: every 4 hours) or in watch mode when you explicitly enable it.

## Features

✨ **Multi-Tool Support**: Markdownlint, Pylint, ESLint, Prettier, Black, Flake8
⏱️ **Scheduled Runs**: Batch-fix issues every 4 hours by default
⚡ **Instant Fixes**: Automatically resolves common linting issues
📊 **Detailed Reporting**: Track linting statistics and improvement over time
🎯 **Smart Filtering**: Configurable ignore patterns and file type handling
🔧 **Framework Integration**: Built into the unified `mw` CLI

## Quick Start

```bash

# Start scheduled linting (every 4 hours)

mw lint start

# Scan all files for linting issues

mw lint scan

# Watch files and auto-fix as you code (optional)

mw lint watch

# Fix all issues in specific directory

mw lint fix --dir projects/my-app

# Show current configuration

mw lint config --show

# Get linting statistics

mw lint stats

```markdown

## How It Works

The Auto-Linting Agent operates in several modes:

### 1. Scheduled Mode (Default)

Runs the lint fixer every 4 hours (configurable). This keeps linting out of
your day-to-day git flow while still maintaining documentation quality.

### 2. Scan Mode

Analyzes all files in a project and applies appropriate linting tools based on
file extensions.

### 3. Watch Mode

Monitors file system changes and automatically runs linting tools when files are
modified. Includes intelligent debouncing to avoid excessive processing.

### 4. Fix Mode

Same as scan mode but focuses on fixing issues rather than just reporting them.

## Supported Tools

| Tool | File Types | Auto-Fix | Purpose |
| ------ | ------------ | ---------- | --------- |
| **Markdownlint** | `.md`, `.mdx` | ✅ | Documentation quality |
| **Black** | `.py` | ✅ | Python code formatting |
  | **Prettier** | `.js`, `.ts... | ✅ | JavaScript/... |  
| **ESLint** | `.js`, `.jsx`, `.ts`, `.tsx` | ✅ | JavaScript code quality |
| **Flake8** | `.py` | ❌ | Python style checking |
| **PyLint** | `.py` | ❌ | Python code analysis |

## Configuration

The linting configuration is stored in `.planning/config/lint.json`. You can
customize it using:

```bash

# Edit configuration in VS Code

mw lint config --edit

# View current configuration

mw lint config --show

```markdown

### Default Configuration

```json
{
  "markdownlint": true,
  "pylint": true,
  "eslint": true,
  "prettier": true,
  "black": true,
  "flake8": true,
  "auto_fix": true,
  "ignore_patterns": [

```markdown

"node_modules/**",
".git/**",
"venv/**",
"__pycache__/**",
".tmp/**"

```markdown

  ]
}

```markdown

### Configuration Options

| Option | Type | Default | Description |
| -------- | ------ | --------- | ------------- |
| `auto_fix` | boolean | `true` | Enable automatic fixing of issues |
| `ignore_patterns` | array | See above | File patterns to ignore |
  | `watch_mode... | number | `2.0` | Delay befor... |  
| `tools.markdownlint.rules` | object | `{}` | Markdownlint rule overrides |
| `tools.black.line_length` | number | `88` | Black line length |
| `tools.prettier.print_width` | number | `100` | Prettier line width |

## Command Reference

### `mw lint scan`

Scans all files for linting issues and applies fixes.

```bash

# Scan entire project

mw lint scan

# Scan specific directory

mw lint scan --dir projects/my-app

# Scan specific file

mw lint scan --file README.md

```markdown

### `mw lint watch`

Starts file watching mode for real-time linting.

```bash

# Watch entire project

mw lint watch

# Watch specific directory

mw lint watch --dir projects/my-app

```yaml

**Watch Mode Features:**

- 🔄 Real-time file monitoring
- ⚡ 2-second debouncing to avoid excessive processing
- 📝 Console feedback on fixes applied
- 🎯 Smart file type detection

### `mw lint fix`

Same as scan but optimized for fixing all issues at once.

```bash

# Fix all issues in project

mw lint fix

# Fix issues in specific directory

mw lint fix --dir projects/my-app

```markdown

### `mw lint config`

Manage linting configuration.

```bash

# Show current configuration

mw lint config --show

# Edit configuration in VS Code

mw lint config --edit

```markdown

### `mw lint stats`

Display linting statistics and history.

```bash
mw lint stats

```yaml

Example output:

```yaml
📊 Auto-Linting Agent Stats:
   Files processed: 147
   Total issues found: 23
   Total issues fixed: 23
   Success rate: 100.0%
   Last run: 2026-01-28T10:30:00

```markdown

## Integration with Framework

The Auto-Linting Agent is fully integrated with the MyWork framework:

### Git Workflows (Optional)

- Git hooks are **disabled by default**
- Use `mw lint install-hooks` to enable pre-commit/pre-push checks
- Use `mw lint uninstall-hooks` to remove them

### Project Structure

- Respects `.gitignore` patterns
- Works with MyWork project structure
- Handles multiple programming languages

### Brain Learning

- Learns from common linting patterns
- Improves configuration over time
- Tracks effectiveness metrics

## Advanced Usage

### Custom Tool Configuration

You can customize individual tools in the configuration:

```json
{
  "tools": {

```

"markdownlint": {
  "enabled": true,
  "auto_fix": true,
  "rules": {

```yaml
"MD013": false,  // Disable line length rule
"MD033": false   // Allow HTML in markdown

```yaml

  }
},
"black": {
  "enabled": true,
  "line_length": 100,
  "target_versions": ["py39", "py310"]
},
"prettier": {
  "enabled": true,
  "print_width": 80,
  "tab_width": 2,
  "use_tabs": false
}

```markdown

  }
}

```markdown

### Programmatic Usage

You can also use the Auto-Linting Agent programmatically:

```python
from tools.auto_linting_agent import AutoLintingAgent, LintConfig

# Create custom configuration

config = LintConfig(

```markdown

markdownlint=True,
auto_fix=True,
ignore_patterns=["custom_ignore/**"]

```markdown

)

# Create agent

agent = AutoLintingAgent(root_dir=".", config=config)

# Lint specific file

results = agent.lint_file("README.md")

# Lint entire directory

results = agent.lint_directory("src/")

# Print summary

agent.print_summary(results)

```

## File Watching Details

The watch mode uses the `watchdog` library for efficient file system monitoring:

- **Recursive monitoring** of all subdirectories
- **Intelligent debouncing** prevents excessive processing
- **File type filtering** only processes relevant files
- **Graceful error handling** continues monitoring on individual failures

### Watch Mode Flow

1. 📁 Monitor file system for changes
2. ⏱️ Apply 2-second debounce delay
3. 🎯 Check if file should be linted
4. 🔧 Apply appropriate linting tools
5. ✅ Report fixes to console
6. 📊 Update statistics

## Troubleshooting

### Common Issues

**Agent not finding files:**

```bash

# Check ignore patterns

mw lint config --show

# Verify file types are supported

mw lint scan --file specific-file.ext

```yaml

**Watch mode not working:**

```bash

# Check if watchdog is installed

pip install watchdog

# Verify permissions

ls -la /path/to/watched/directory

```yaml

**Tools not auto-fixing:**

```bash

# Check if tools are installed

which black
which prettier
which markdownlint

# Install missing tools

npm install -g markdownlint-cli
npm install -g prettier
pip install black flake8

```markdown

### Performance Tuning

For large projects, you can optimize performance:

```json
{
  "ignore_patterns": [

```yaml

"large-directory/**",
"generated/**",
"*.generated.*"

```yaml
  ],
  "watch_mode": {

```yaml

"debounce_seconds": 5.0,
"batch_processing": true

```text
  }
}

```markdown

## Results and Reporting

The agent saves detailed results to `.planning/linting_results.json`:

```json
[
  {

```yaml

"file_path": "/path/to/file.md",
"tool": "markdownlint",
"issues_found": 3,
"issues_fixed": 3,
"success": true,
"messages": ["Fixed 3 markdown issues"],
"timestamp": "2026-01-28T10:30:00.000Z"

```
  }
]

```markdown

This data powers the statistics and helps track improvement over time.

## Best Practices

### Development Workflow

1. **Start watch mode** when beginning work:

   ```bash
   mw lint watch

```yaml

2. **Scan before commits**:

   ```bash
   mw lint scan
   git add .
   git commit -m "Your commit message"

```yaml

3. **Regular maintenance**:

   ```bash

   # Weekly full scan

   mw lint fix

   # Check statistics

   mw lint stats

```markdown

### Configuration Management

- Keep configuration in version control
- Use project-specific overrides when needed
- Document any custom rules or ignore patterns
- Review and update configuration regularly

### Team Collaboration

- Share linting configuration across team
- Include auto-linting in CI/CD pipelines
- Use pre-commit hooks only if your team wants linting in git flow
- Document team-specific linting standards

## Integration Examples

### Pre-commit Hook (Optional)

Hooks are **disabled by default**. Enable them with `mw lint install-hooks`, or
add the following manually:

```bash

#!/bin/sh

echo "Running auto-linting..."
mw lint fix
git add .

```markdown

### VS Code Integration

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [

```yaml

{
  "label": "MyWork: Auto Lint",
  "type": "shell",
  "command": "mw lint scan",
  "group": "build",
  "problemMatcher": []
}

```markdown

  ]
}

```markdown

### CI/CD Pipeline

GitHub Actions example:

```yaml

- name: Run Auto-Linting

  run: |

```bash

pip install -r requirements.txt
mw lint scan
git diff --exit-code  # Fail if linting changed files

```text

```text

The Auto-Linting Agent ensures consistent code quality across your entire MyWork
framework, saving time and maintaining professional standards automatically. 🚀
