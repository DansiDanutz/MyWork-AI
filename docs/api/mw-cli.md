# MyWork CLI Reference (`mw`)

Complete reference for all MyWork command-line interface commands.

## 📋 Command Overview

| Command | Purpose | Example |
| --------- | --------- | --------- |
| [`mw status`](#mw-status) | Framework health check | `mw status` |
| [`mw new`](#mw-new) | Create new project | `mw new my-app fastapi` |
| [`mw search`](#mw-search) | Search module registry | `mw search "auth"` |
| [`mw brain`](#mw-brain) | Knowledge management | `mw brain learn` |
| [`mw ac`](#mw-ac-a... | Autocoder control | `mw ac start my-pr... |
| [`mw doctor`](#mw-doctor) | System diagnostics | `mw doctor --fix` |
| [`mw update`](#mw-update) | Update framework | `mw update --check` |

## 🔍 `mw status`

Display comprehensive framework status and health information.

### Syntax

```bash
mw status [options]

```markdown

### Options

| Option | Description | Default |
| -------- | ------------- | --------- |
| `--verbose, -v` | Show detailed component status | `false` |
| `--json` | Output in JSON format | `false` |

### Examples

**Basic status check:**

```bash
mw status

```yaml

```yaml
✅ MyWork Framework Status
├── 🧠 Brain: Ready (253 patterns indexed)
├── 📊 Module Registry: Ready (1,300+ modules)
├── 🔧 Health Check: All systems operational
├── 🤖 Autocoder: Available (not running)
└── 🔗 n8n: MCP server ready

```yaml

**Verbose output:**

```bash
mw status --verbose

```text

```yaml
🔍 Detailed Framework Status

📊 Module Registry:
  └── Indexed: 1,347 modules across 23 languages
  └── Last scan: 2026-01-27 14:30:22
  └── Coverage: backend (567), frontend (421), utils (359)

🧠 Brain Knowledge:
  └── Patterns: 253 tested, 67 experimental
  └── Learnings: 89 architectural, 164 implementation
  └── Vault size: 2.3MB (text), 4.7MB (embeddings)

🤖 Autocoder Status:
  └── Server: Available at http://127.0.0.1:8888
  └── Version: 2.4.1
  └── Active projects: 0
  └── Total sessions: 47 (avg 2.3h each)

```markdown

## 🆕 `mw new`

Create a new project from templates with optional framework integration.

### Syntax

```bash
mw new <project_name> [template] [options]

```markdown

### Parameters

| Parameter | Description | Required |
| ----------- | ------------- | ---------- |
| `project_name` | Name of the new project | ✅ Yes |
| `template` | Template type to use | ❌ No (default: `basic`) |

### Templates

| Template | Description | Technologies |
| ---------- | ------------- | -------------- |
| `basic` | Empty project with GSD | Markdown, Git |
| `cli` | Command-line tool | Python, Click, Pytest |
| `fastapi` | REST API backend | Python, FastAPI, SQLite |
| `nextjs` | Frontend application | Next.js, TypeScript, Tailwind |
| `fullstack` | Complete web app | FastAPI + Next.js |
| `automation` | n8n + Python webhooks | n8n, Python, Docker |

### Options

| Option | Description | Default |
| -------- | ------------- | --------- |
| `--no-gsd` | Skip GSD initialization | `false` |
| `--autocoder` | Set up for Autocoder use | `false` |
| `--force, -f` | Overwrite existing directory | `false` |

### Examples

**Basic project:**

```bash
mw new my-project

# Creates: projects/my-project/ with basic structure

```yaml

**CLI tool with GSD:**

```bash
mw new task-cli cli

# Creates: projects/task-cli/ with Python CLI template

```yaml

**FastAPI backend ready for Autocoder:**

```bash
mw new my-api fastapi --autocoder

# Creates: projects/my-api/ with FastAPI + Autocoder config

```yaml

**Force overwrite existing:**

```bash
mw new existing-project nextjs --force

# Overwrites: projects/existing-project/ with new template

```markdown

### Output Structure

```python
projects/my-project/
├── .planning/
│   ├── PROJECT.md          # Generated from user input
│   ├── STATE.md            # Initial project state
│   └── config.json         # GSD configuration
├── README.md               # Template-specific guide
├── project.yaml            # Metadata and dependencies
├── .gitignore              # Template-appropriate ignores
└── src/                    # Template-specific structure

```text

└── [template files]

```

```markdown

## 🔍 `mw search`

Search the module registry for reusable code patterns and components.

### Syntax

```bash
mw search <query> [options]

```markdown

### Parameters

| Parameter | Description | Required |
| ----------- | ------------- | ---------- |
| `query` | Search terms or pattern | ✅ Yes |

### Options

| Option | Description | Default |
| -------- | ------------- | --------- |
| `--type, -t` | Filter by module type | All types |
| `--language, -l` | Filter by programming language | All languages |
| `--limit, -n` | Maximum results to show | `20` |
| `--detail, -d` | Show detailed information | `false` |
| `--copy` | Copy result to clipboard | `false` |

### Module Types

- `api_endpoint` - REST/GraphQL API routes
- `component` - UI components (React, Vue, etc.)
- `service` - Business logic classes
- `utility` - Helper functions
- `schema` - Database models, validation
- `hook` - React hooks, composables
- `middleware` - Request/response processors
- `integration` - External API clients

### Examples

**Basic search:**

```bash
mw search "authentication"

```yaml

```yaml
🔍 Found 12 modules matching "authentication":

1. 🔐 auth-middleware (Python) - FastAPI JWT middleware

   └── projects/task-tracker/src/shared/middleware/auth.ts
   └── Used in: 3 projects | Rating: ⭐⭐⭐⭐⭐

2. 🔐 github-auth-action (TypeScript) - GitHub OAuth Server Action

   └── projects/task-tracker/src/shared/lib/auth.ts
   └── Used in: 2 projects | Rating: ⭐⭐⭐⭐⭐

3. 🔐 session-dal (TypeScript) - Database session management

   └── projects/ai-dashboard/src/lib/dal/sessions.ts
   └── Used in: 2 projects | Rating: ⭐⭐⭐⭐

```yaml

**Filtered search:**

```bash
mw search "api" --type api_endpoint --language python --limit 5

```yaml

**Detailed view:**

```bash
mw search "auth middleware" --detail

```yaml

```yaml
🔐 auth-middleware (Python)
Path: projects/task-tracker/src/shared/middleware/auth.ts
Type: middleware | Language: python | Size: 187 lines

Description:
FastAPI middleware for JWT token validation with session fallback

Usage:
from shared.middleware.auth import AuthMiddleware
app.add_middleware(AuthMiddleware, secret="<YOUR_SECRET>")

Dependencies:

- fastapi
- python-jose[cryptography]
- python-multipart

Used in projects:

- task-tracker (primary implementation)
- api-server (adapted version)
- auth-service (extended version)

Pattern confidence: ⭐⭐⭐⭐⭐ (5 successful integrations)

```markdown

## 🧠 `mw brain`

Interact with the MyWork knowledge vault and learning system.

### Syntax

```bash
mw brain <command> [options]

```markdown

### Commands

#### `mw brain search`

Search accumulated knowledge and patterns.

```bash
mw brain search <query> [--type pattern|decision|lesson]

```yaml

**Examples:**

```bash
mw brain search "database migrations"
mw brain search "React performance" --type pattern

```markdown

#### `mw brain learn`

Trigger automatic learning from recent work.

```bash
mw brain learn [--deep] [--project <name>]

```yaml

**Options:**

- `--deep` - Perform comprehensive analysis (slower, more thorough)
- `--project <name>` - Learn from specific project only

**Examples:**

```bash
mw brain learn                    # Quick learning from recent activity
mw brain learn --deep             # Deep analysis (weekly recommended)
mw brain learn --project my-api   # Learn from specific project

```markdown

#### `mw brain stats`

Show brain statistics and growth metrics.

```bash
mw brain stats [--breakdown]

```

**Example output:**

```yaml
🧠 Brain Statistics

Knowledge Base:
├── 📝 Total entries: 253
├── 🧪 Experimental: 67 (pending validation)
├── ✅ Tested: 186 (production-ready)
├── 🗑️ Deprecated: 14 (outdated patterns)

Learning Sources:
├── 📊 GSD completions: 89 patterns extracted
├── 🔄 Git commits: 164 decisions captured
├── 🧪 Error resolutions: 45 lessons learned
├── 👥 Manual entries: 23 user contributions

Growth Metrics:
├── 📈 This week: +12 new patterns
├── 🎯 Accuracy: 94% (user validation feedback)
├── ♻️ Reuse rate: 67% (patterns used in new projects)
└── 🚀 Time savings: ~3.2 hours/week average

```markdown

#### `mw brain remember`

Manually add knowledge to the brain.

```bash
mw brain remember "<knowledge>" [--type <type>] [--project <name>]

```yaml

**Examples:**

```bash
mw brain remember "Always validate file uploads with content-based MIME detection"
mw brain remember "React Context causes re-renders - use zustand for performance" --type pattern

```markdown

## 🤖 `mw ac` (Autocoder Control)

Control the Autocoder autonomous coding system.

### Syntax

```bash
mw ac <command> [options]

```markdown

### Commands

#### `mw ac start`

Start autonomous coding on a project.

```bash
mw ac start <project> [--concurrency <n>] [--model <model>] [--yolo]

```yaml

**Parameters:**

- `project` - Project name in `projects/` directory

**Options:**

- `--concurrency <n>` - Number of parallel agents (1-5, default: 1)
- `--model <model>` - AI model to use (default: claude-opus-4-5-20251101)
- `--yolo` - Skip testing for faster development
- `--testing-ratio <n>` - Testing agents per coding agent (default: 1)

**Examples:**

```bash
mw ac start my-app                           # Conservative: 1 agent, full testing
mw ac start my-app --concurrency 3          # Balanced: 3 agents with testing
mw ac start my-app --concurrency 5 --yolo   # Fast: 5 agents, no testing

```markdown

#### `mw ac status`

Check Autocoder server and project status.

```bash
mw ac status [project]

```yaml

**Examples:**

```bash
mw ac status              # Show server status
mw ac status my-app       # Show specific project status

```markdown

#### `mw ac progress`

Monitor project development progress.

```bash
mw ac progress <project> [--follow]

```yaml

**Options:**

- `--follow, -f` - Continuously update progress display

**Example output:**

```yaml
🤖 Autocoder Progress: my-app

📊 Overall Progress: [████████░░] 82% complete

📋 Current Tasks:
├── ✅ Database schema design (completed)
├── ✅ API endpoint structure (completed)
├── 🔄 User authentication (in progress, Agent 2)
├── ⏳ Frontend components (queued)
└── ⏳ Testing suite (queued)

⚡ Performance:
├── 🏃 Active agents: 3/3
├── ⏱️ Time elapsed: 2h 34m
├── 📈 Features completed: 23/28
├── 🧪 Tests passing: 89/94 (95%)

🎯 Estimated completion: 34 minutes

```markdown

#### `mw ac pause/resume`

Control project execution.

```bash
mw ac pause <project>     # Pause all agents on project
mw ac resume <project>    # Resume paused project
mw ac stop <project>      # Stop and cleanup project

```markdown

#### `mw ac ui`

Launch the Autocoder web interface.

```bash
mw ac ui [--port <port>]

```yaml

Opens browser to `http://localhost:8888` for visual monitoring.

## 🔧 `mw doctor`

System diagnostics and automatic issue resolution.

### Syntax

```bash
mw doctor [options]

```markdown

### Options

| Option | Description |
| -------- | ------------- |
| `--fix` | Automatically fix detected issues |
| `--report` | Generate detailed diagnostic report |
| `--check <component>` | Check specific component only |

### Components

- `dependencies` - Python/Node.js packages
- `permissions` - File system access
- `services` - Autocoder, n8n servers
- `projects` - Project structure validation
- `config` - Configuration files

### Examples

**Basic health check:**

```bash
mw doctor

```

```yaml
🔍 MyWork Framework Diagnostics

✅ Python Dependencies: All required packages installed
✅ Node.js Dependencies: All packages up to date
✅ File Permissions: Read/write access confirmed
❌ Autocoder Server: Not responding on port 8888
⚠️  Project Structure: 2 projects have outdated templates
✅ Configuration: All config files valid

Issues found: 1 error, 1 warning
Run 'mw doctor --fix' to attempt automatic repairs.

```yaml

**Auto-fix issues:**

```bash
mw doctor --fix

```text

```markdown

🔧 Fixing detected issues...

🤖 Starting Autocoder server...
   └── Server started on port 8888 ✅

📁 Updating project templates...
   └── Updated projects/old-project/project.yaml ✅
   └── Updated projects/legacy-app/.gitignore ✅

✅ All issues resolved! Framework is healthy.

```markdown

## 🔄 `mw update`

Update framework components and dependencies.

### Syntax

```bash
mw update [component] [options]

```markdown

### Components

- `all` - Update everything (default)
- `gsd` - GSD skills and workflows
- `autocoder` - Autocoder system
- `n8n-skills` - n8n integration
- `n8n-mcp` - n8n MCP server

### Options

| Option | Description |
| -------- | ------------- |
| `--check` | Check for updates without installing |
| `--force` | Force update even if no changes detected |
| `--rollback <component>` | Rollback to previous version |

### Examples

**Check for updates:**

```bash
mw update --check

```text

```yaml
🔍 Update Status:

✅ GSD: Up to date (v1.2.0)
🔄 Autocoder: Update available (v2.4.1 → v2.5.0)
✅ n8n-skills: Up to date (v1.1.2)
🔄 n8n-mcp: Update available (v0.8.3 → v0.8.5)

Run 'mw update' to install available updates.

```yaml

**Update specific component:**

```bash
mw update autocoder

```yaml

**Rollback if issues:**

```bash
mw update --rollback autocoder

```markdown

## 🌐 Global Options

Available for all `mw` commands:

| Option | Description | Example |
| -------- | ------------- | --------- |
| `--help, -h` | Show command help | `mw search --help` |
| `--version, -v` | Show version info | `mw --version` |
| `--quiet, -q` | Minimal output | `mw status --quiet` |
| `--verbose` | Detailed output | `mw brain learn --verbose` |
| `--no-color` | Disable colored output | `mw status --no-color` |
| `--config <file>` | Use custom config file | `mw new --config custom.json` |

## 🔗 Exit Codes

| Code | Meaning |
| ------ | --------- |
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Permission denied |
| `4` | Network/connectivity issue |
| `5` | Service unavailable (Autocoder, n8n) |

## 📖 Additional Resources

- [**Python API Reference →**](tools/) - Direct tool usage
- [**Quickstart Guide →**](../quickstart.md) - Practical setup
- [**Architecture Overview →**](../architecture/overview.md) - System design
- [**Troubleshooting →**](../troubleshooting.md) - Common issues

---

*💡 **Pro Tip:** Use `mw <command> --help` for detailed help on any command,
including examples and advanced options.*
