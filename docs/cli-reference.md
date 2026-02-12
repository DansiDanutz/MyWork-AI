# MyWork CLI Reference

> Complete reference for all `mw` commands. Install: `pip install mywork-ai`

## Quick Start

```bash
pip install mywork-ai
mw setup          # First-time wizard
mw guide          # Interactive tutorial
mw status         # Health check
```

---

## Project Management

### `mw new <name> <template>`
Create a new project from a template.

**Templates:** `fastapi`, `flask`, `react`, `nextjs`, `cli`, `library`

```bash
mw new my-api fastapi      # Scaffold a FastAPI project
mw new my-app nextjs       # Scaffold a Next.js project
mw new my-tool cli          # Scaffold a CLI tool
```

### `mw init`
Initialize the current directory as a MyWork project. Creates `.mw/` config, `.env`, and `README.md`.

```bash
cd existing-project
mw init
```

### `mw projects`
List, scan, and export all registered projects.

```bash
mw projects                 # List all projects
mw projects scan            # Scan for new projects
mw projects export          # Export project data
```

### `mw open <project>`
Open a project in VS Code.

### `mw cd <project>`
Print the `cd` command to navigate to a project directory.

---

## Development Workflow

### `mw test [project]`
Universal test runner — auto-detects Python (pytest), Node (jest/vitest), Rust (cargo), Go, Ruby.

```bash
mw test                     # Run tests in current directory
mw test --coverage          # With coverage report
mw test --watch             # Watch mode
mw test --verbose           # Verbose output
```

### `mw lint`
Auto-linting with watch mode.

```bash
mw lint scan                # Scan for lint issues
mw lint watch               # Auto-fix as you code
mw lint stats               # Linting statistics
```

### `mw git`
Smart git operations with AI-powered commit messages.

```bash
mw git commit               # AI-generated commit message
mw git commit --push        # Commit and push
```

### `mw hook`
Git hooks management.

```bash
mw hook install              # Install pre-commit hooks
mw hook list                 # List active hooks
mw hook remove               # Remove hooks
mw hook create <name>        # Create custom hook
```

### `mw changelog`
Generate changelog from git history.

---

## AI-Powered Tools

### `mw ai`
AI coding assistant (requires API key in `.env`).

```bash
mw ai ask "How do I handle auth in FastAPI?"
mw ai explain src/main.py   # Explain code
mw ai fix src/buggy.py       # Fix bugs
mw ai refactor src/old.py    # Refactoring suggestions
mw ai test src/utils.py      # Generate tests
mw ai commit                 # AI commit message
mw ai commit --push          # Commit + push
```

### `mw review`
AI-powered code review.

```bash
mw review src/main.py        # Review specific file
mw review --diff             # Review current git diff
mw review --staged           # Review staged changes
```

### `mw prompt-enhance`
Enhance rough prompts into detailed GSD-ready specifications.

```bash
mw prompt-enhance "build a todo app with auth"
```

### `mw docs generate <project>`
Auto-generate documentation for a project using AI.

---

## Deployment & Operations

### `mw deploy <project>`
Deploy to cloud platforms.

```bash
mw deploy my-app --platform vercel
mw deploy my-app --platform railway
mw deploy my-app --platform render
mw deploy my-app --platform docker
```

### `mw monitor`
Check deployment health and uptime.

```bash
mw monitor                   # Show deployment history
mw monitor --check           # Health check all URLs
```

### `mw release`
Automate version releases.

```bash
mw release patch             # 1.0.0 → 1.0.1
mw release minor             # 1.0.0 → 1.1.0
mw release major             # 1.0.0 → 2.0.0
```

### `mw ci`
Generate CI/CD pipeline configurations.

```bash
mw ci                        # Auto-detect and generate
mw ci --platform github      # GitHub Actions
mw ci --platform gitlab      # GitLab CI
```

---

## Knowledge & Brain

### `mw brain`
Knowledge vault for storing and retrieving reusable patterns, solutions, and notes.

```bash
mw brain search "auth"       # Search knowledge base
mw brain add "tag" "content" # Add knowledge entry
mw brain stats               # Knowledge statistics
mw brain export              # Export all entries
```

### `mw search <query>`
Search the module registry for reusable components.

```bash
mw search "authentication"
mw search "database"
```

---

## Environment & Configuration

### `mw env`
Manage environment variables across projects.

```bash
mw env list                  # List all variables (masked)
mw env get API_KEY           # Get specific variable
mw env set API_KEY=value     # Set variable
mw env rm API_KEY            # Remove variable
mw env diff                  # Compare .env vs .env.example
mw env validate              # Validate required vars exist
mw env export                # Export as shell commands
mw env init                  # Create .env from .env.example
```

### `mw config`
Manage framework configuration.

```bash
mw config                    # Show current config
mw config set key=value      # Set config value
```

---

## Diagnostics & Health

### `mw status`
Quick health overview of all framework components.

### `mw doctor`
Full system diagnostics — checks Python, dependencies, services, and configuration.

### `mw report`
Detailed health report with recommendations.

### `mw fix`
Auto-fix common issues found by `mw doctor`.

### `mw audit`
Comprehensive project quality audit — generates a report card with scores.

### `mw project-health <project>`
Check health score (0-100) for a specific project.

### `mw security <project>`
Run security scanner — checks for vulnerabilities, secrets, and misconfigurations.

---

## Plugins & Extensions

### `mw plugin`
Extensible plugin system.

```bash
mw plugin list               # List installed plugins
mw plugin install <source>   # Install from git URL or local path
mw plugin uninstall <name>   # Remove plugin
mw plugin enable <name>      # Enable plugin
mw plugin disable <name>     # Disable plugin
mw plugin create <name>      # Create new plugin template
```

---

## Integrations

### `mw af` (AutoForge)
AutoForge integration for autonomous project building.

```bash
mw af status                 # Check AutoForge status
mw af start <project>        # Start AutoForge on project
mw af stop                   # Stop AutoForge
```

### `mw n8n`
n8n workflow automation integration.

### `mw api`
Scaffold and manage FastAPI projects with auto-generated CRUD endpoints.

```bash
mw api new my-api            # Create new FastAPI project
mw api crud users            # Generate CRUD for 'users' model
```

### `mw workflow`
Execute multi-step YAML workflows.

```bash
mw workflow run pipeline.yml  # Execute workflow
mw wf run pipeline.yml        # Short alias
```

---

## Utilities

### `mw backup`
Backup all projects and brain data.

### `mw clean`
Clean temporary files across all projects.

### `mw stats`
Framework-wide statistics.

### `mw ecosystem`
Show all live app URLs and ecosystem overview.

### `mw links`
Show useful framework links.

### `mw credits`
Credits ledger management (Phase 8 Payments).

### `mw update`
Check and apply updates for framework components.

### `mw version`
Show version, Python version, and platform info.

```bash
mw version
mw -v
mw --version
```

---

## Global Options

All commands support:
- `--help` / `-h` — Show command help
- Most commands auto-detect project type and context

## Configuration

MyWork looks for configuration in:
1. `.mw/config.json` (project-level)
2. `~/.mywork/config.json` (user-level)
3. Environment variables (`MW_*` prefix)
