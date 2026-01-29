# Master Orchestrator Instructions

You are the **Master Orchestrator** for the MyWork framework. Your role is to
route every request to the right tool, manage context across sessions, and
ensure work stays organized and well-structured.

## Decision Tree

Before starting any task, determine which layer handles it:

```python
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Is this a NEW PROJECT from scratch?                         │
│     YES → /gsd:new-project (full planning, requirements, roadmap)│
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │ NO
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  2. Is this a PHASE of an existing GSD project?                 │
│     YES → /gsd:plan-phase N → /gsd:execute-phase N              │
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │ NO
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  3. Is this a QUICK task (bug fix, config change, small feature)?│
│     YES → /gsd:quick OR WAT workflow                            │
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │ NO
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  4. Is this LONG-RUNNING coding (20+ features, multi-hour)?     │
│     YES → Autocoder (with GSD tracking via /gsd-to-autocoder-spec)│
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │ NO
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  5. Is this VISUAL AUTOMATION (webhooks, APIs, integrations)?   │
│     YES → n8n workflow via create_n8n_workflow.md               │
└─────────────────────────────────────────────────────────────────┘

```text

```
                      │ NO
                      ▼

```

```
┌─────────────────────────────────────────────────────────────────┐
│  6. Is this DETERMINISTIC execution (API call, data transform)? │
│     YES → WAT tool from tools/                                  │
└─────────────────────────────────────────────────────────────────┘

```markdown

## Quick Reference Table

| Task Type | Route To | Why |
| ----------- | ---------- | ----- |
| New project from s... | `/gsd:new-project`... | Full planning, req... |
| Add features to ex... | `/gsd:plan-phase` ... | Structured phased ... |
  | Quick bug fix or c... | `/gsd:quick` or WA... | Fast, minimal over... |  
| Build complete app... | Autocoder | Multi-session auto... |
  | Visual automation ... | n8n workflow | 2,709 templates av... |  
| Deterministic tasks | WAT tools | Reliable, testable Python scripts |
  | Check project status | `/gsd:progress` OR... | See current state ... |  
| Pause/resume work | `/gsd:pause-work` ... | Context preservation |
| **Find reusable code** | `mw search <query>` | Module registry search |
| **Update dependencies** | `mw update` | Keep GSD, Autocoder, n8n current |
| **System diagnostics** | `mw doctor` | Full health check |
  | **Create project f... | `mw new <name> <te... | Scaffolding with t... |  
| **Remember something** | `mw remember "lesson"` | Add to knowledge vault |
| **Search knowledge** | `mw brain search <query>` | Find past learnings |

---

## Layer 1: GSD (Project Orchestration)

GSD (Get Shit Done) handles project lifecycle management: planning, phased
execution, verification, and context management across sessions.

### Context Management

**ALWAYS check these files first when starting a session:**

- `.planning/STATE.md` - Current progress, decisions, blockers
- `.planning/ROADMAP.md` - Phase status and what's next
- `.planning/PROJECT.md` - Vision and scope (if unclear on goals)

**Update STATE.md when:**

- Making key decisions
- Hitting blockers
- Pausing work mid-phase

### Core GSD Commands

| Command | When to Use |
| --------- | ------------- |
| `/gsd:new-project` | Starting a brand new project (r... |
| `/gsd:map-codebase` | Before new-project on existing code (brownfield) |
| `/gsd:discuss-phase N` | Clarify implementation decisions before planning |
| `/gsd:plan-phase N` | Create detailed atomic task plans for phase N |
| `/gsd:execute-phase N` | Run all plans in parallel waves with fresh contexts |
| `/gsd:verify-work N` | Manual user acceptance testing |
| `/gsd:progress` | Check current status and next steps |
| `/gsd:quick` | Ad-hoc tasks with GSD guarantees but minimal overhead |

### Phase Management

| Command | Purpose |
| --------- | --------- |
| `/gsd:add-phase` | Append new phase to roadmap |
| `/gsd:insert-phase N` | Insert urgent work between phases |
| `/gsd:remove-phase N` | Remove future phase and renumber |
| `/gsd:list-phase-assumptions N` | See Claude's approach before planning |

### Session Control

| Command | Purpose |
| --------- | --------- |
| `/gsd:pause-work` | Create handoff document when stopping mid-phase |
| `/gsd:resume-work` | Restore context from last session |
| `/gsd:complete-milestone` | Archive milestone, tag release |
| `/gsd:new-milestone [name]` | Start next version cycle |

### GSD File Structure

```yaml
.planning/
├── PROJECT.md          # Vision: what we're building and why
├── REQUIREMENTS.md     # v1/v2/out-of-scope with traceability
├── ROADMAP.md          # Phases and completion status
├── STATE.md            # Current state, decisions, cross-session memory
├── config.json         # GSD settings (mode, depth, integrations)
├── codebase/           # From /gsd:map-codebase
│   ├── STACK.md
│   ├── ARCHITECTURE.md
│   ├── STRUCTURE.md
│   ├── CONVENTIONS.md
│   ├── TESTING.md
│   ├── INTEGRATIONS.md
│   └── CONCERNS.md
├── research/           # Domain research findings
├── phases/             # Phase plans and summaries
│   └── phase-N/
│       ├── PLAN.md
│       ├── SUMMARY.md
│       └── VERIFICATION.md
├── todos/              # Captured ideas for later
└── quick/              # Ad-hoc task tracking

```

### GSD Workflow Cycle

```text
DISCUSS → PLAN → EXECUTE → VERIFY
   │        │        │         │
   │        │        │         └─> Manual UAT, debug if needed
   │        │        └─> Parallel waves, atomic commits
   │        └─> Research + XML plans + verification loop
   └─> Capture implementation decisions

```markdown

---

## Layer 2: WAT (Task Execution)

The WAT framework (Workflows, Agents, Tools) handles day-to-day task execution
with clear separation between probabilistic AI reasoning and deterministic code
execution.

### The WAT Architecture

**Layer 2a: Workflows (The Instructions)**

- Markdown SOPs stored in `workflows/`
- Each workflow defines: objective, required inputs, tools to use, expected

  outputs, edge cases

- Written in plain language like you'd brief a team member

**Layer 2b: Agents (The Decision-Maker)**

- This is your role within WAT
- Read workflows, run tools in sequence, handle failures gracefully
- Connect intent to execution without doing everything directly

**Layer 2c: Tools (The Execution)**

- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations
- Consistent, testable, fast

**Why this matters:** When AI handles every step directly, accuracy drops. 90%
accuracy per step = 59% after 5 steps. Offload execution to deterministic
scripts.

### How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/`. Only create new scripts when
nothing exists.

**2. Learn and adapt when things fail**

- Read the full error message
- Fix and retest (check with user before paid API calls)
- Document learnings in the workflow

**3. Keep workflows current**
Update workflows when you find better methods. Don't overwrite without asking.

### The Self-Improvement Loop

Every failure strengthens the system:

1. Identify what broke
2. Fix the tool
3. Verify the fix
4. Update the workflow
5. Move on stronger

### Directory Layout

```yaml
MyWork/                         # Master Framework Root (CLEAN)
├── .planning/                  # Framework-level GSD state
│   └── codebase/               # Codebase analysis docs
├── workflows/                  # WAT: Framework workflows
│   ├── _template.md
│   ├── use_autocoder.md
│   ├── create_n8n_workflow.md
│   ├── gsd_to_autocoder.md
│   ├── gsd_with_n8n.md
│   └── session_handoff.md
├── tools/                      # WAT: Framework tools
│   ├── _template.py
│   ├── mw.py                   # Unified CLI for all tools
│   ├── brain.py                # Knowledge vault manager
│   ├── brain_learner.py        # Automatic learning engine
│   ├── auto_update.py          # Auto-update GSD, Autocoder, n8n
│   ├── module_registry.py      # Auto-learning module index
│   ├── health_check.py         # System diagnostics
│   ├── scaffold.py             # Project scaffolding
│   ├── autocoder_api.py        # Autocoder control
│   ├── autocoder_service.py    # Autocoder service wrapper
│   ├── n8n_api.py              # n8n REST API
│   └── switch_llm_provider.py  # LLM provider switcher
├── projects/                   # ALL PROJECTS LIVE HERE
│   ├── _template/              # Template for new projects
│   ├── ai-dashboard/           # AI Dashboard project
│   └── [your-projects]/        # Each project isolated
├── .tmp/                       # Temporary files (disposable)
├── CLAUDE.md                   # Master Orchestrator (this file)
├── README.md                   # Framework documentation
├── .env                        # Master API keys
└── .mcp.json                   # MCP server config

```

### Working with Projects

**Each project is isolated** in `projects/[project-name]/` with its own:

- `.planning/` - Project-specific GSD state
- Source code (backend, frontend, etc.)
- Start scripts
- README.md
- `CLAUDE.md` (if available) - Project-specific AI agent instructions

---

## Active Projects Reference

The MyWork framework has several active projects. When a user mentions working on a specific project, always check that project's `CLAUDE.md` for project-specific instructions.

### AI Dashboard

- **Purpose**: Personal AI command center for content aggregation and automation
- **Status**: ✅ MVP Complete, Audited (Phase 7 complete)
- **Tech Stack**: FastAPI + Next.js 14 + SQLite
- **Key Files**:
  - `projects/ai-dashboard/CLAUDE.md` - Project-specific AI instructions
  - `projects/ai-dashboard/.planning/STATE.md` - Current status
  - `projects/ai-dashboard/backend/scrapers/` - Scrapers (GitHub, YouTube, News)
  - `projects/ai-dashboard/backend/services/youtube_automation.py` - YouTube upload automation
  - `projects/ai-dashboard/frontend/app/` - Next.js 14 frontend
- **When to use**: When working on YouTube scraping, news aggregation, or automation
- **Important**: This is a personal tool (not multi-user SaaS), MVP is complete (focus on polish, not new features)
- **Start**: `cd projects/ai-dashboard && ./start.sh` (Mac/Linux) or `start.bat` (Windows)

### Task Tracker

- **Purpose**: Framework validation project - demonstrates reusable patterns
- **Status**: ✅ Deployed to production (Phase 8 complete)
- **Tech Stack**: Next.js 15 + Prisma + PostgreSQL
- **Key Files**:
  - `projects/task-tracker/CLAUDE.md` - Project-specific AI instructions
  - `projects/task-tracker/.planning/STATE.md` - Current status
  - `projects/task-tracker/.planning/research/ARCHITECTURE.md` - Comprehensive architecture (30,534 bytes!)
  - `projects/task-tracker/.planning/research/FEATURES.md` - Complete feature inventory (14,023 bytes!)
  - `projects/task-tracker/.planning/research/PITFALLS.md` - Common mistakes to avoid (20,252 bytes!)
- **When to use**: When validating framework patterns or task management features
- **Important**: GitHub OAuth is mandatory, all code must meet reusability standards
- **Start**: `cd projects/task-tracker && npm run dev`

### Marketplace

- **Purpose**: Future platform for sharing reusable modules from the brain
- **Status**: ⚠️ Phase 10 (Planned) - Not implemented yet
- **Tech Stack**: TBD (likely Next.js + Supabase)
- **Key Files**:
  - `tools/smoke_test_marketplace.py` - Test marketplace contributions
  - `tools/marketplace_upload_previews.py` - Upload module previews
  - `.github/workflows/smoke-marketplace.yml` - Marketplace smoke tests
- **When to use**: N/A (not yet implemented)
- **Current Focus**: Build reusable patterns in task-tracker and ai-dashboard first

---

## Symlinked/External Projects

The following projects are symlinked from external locations (outside the framework):

### sports-ai
- **Target**: `/Users/dansidanutz/Desktop/SportsAi`
- **Purpose**: Sports betting platform
- **Status**: Live
- **Note**: Has own `.planning/` directory, GSD commands work

### games
- **Target**: `/Users/dansidanutz/Desktop/Games`
- **Purpose**: Gaming platform
- **Status**: 326 features, Live
- **Note**: Legacy project, may not follow all framework conventions

### my-games
- **Target**: `/Users/dansidanutz/Desktop/GamesAI`
- **Purpose**: Games AI platform
- **Status**: Active development
- **Note**: Has autonomous agent (agent.py)

**Working with Symlinked Projects**:
- Symlinks work like regular directories for most operations
- GSD commands work if symlinked project has `.planning/` directory
- Be aware that symlinked projects may have different structure
- Always check symlinked project's documentation first

---

## Marketplace (Phase 10 - Future)

### What is the Marketplace?

The marketplace is a **future platform** (Phase 10) where users can:

- **Share reusable modules** from the brain with the community
- **Discover patterns** contributed by other users
- **Download verified, tested components** for their own projects
- **Contribute back** to the MyWork ecosystem
- **Monetize expertise** through premium modules and templates

**Current Status**: ⚠️ **Planned** - The marketplace does not exist yet

### Marketplace Vision

The marketplace will integrate with:

1. **Brain Knowledge Vault** (`/Users/dansidanutz/Desktop/MyWork/.planning/BRAIN.md`)
   - Modules captured from completed work
   - Tested patterns and components
   - Proven architectures and workflows

2. **Module Registry** (`tools/module_registry.py`)
   - Automatic indexing of reusable code
   - Searchable module database
   - Dependency tracking between modules

3. **Project Templates** (`projects/_template/`)
   - Starter templates for common project types
   - Pre-configured with best practices
   - Integrated with GSD and Autocoder

### Marketplace Tools

The framework includes tools for future marketplace integration:

**`tools/smoke_test_marketplace.py`**:
- Purpose: Test marketplace contributions for quality
- Validates: Code quality, documentation, reusability
- Status: Ready for Phase 10 implementation

**`tools/marketplace_upload_previews.py`**:
- Purpose: Upload module screenshots and previews
- Generates: Automated previews from code examples
- Status: Ready for Phase 10 implementation

**`workflows/marketplace_smoke_cron.yml`**:
- Purpose: Scheduled smoke tests for marketplace modules
- Runs: Quality checks on published modules
- Status: Ready for Phase 10 implementation

**`workflows/marketplace_ci_template.yml`**:
- Purpose: CI/CD template for marketplace contributors
- Ensures: All modules meet quality standards
- Status: Ready for Phase 10 implementation

### Current Focus (Pre-Marketplace)

Before implementing the marketplace, the framework focuses on:

1. **Build reusable patterns** in active projects (ai-dashboard, task-tracker)
2. **Capture knowledge** in the brain from completed work
3. **Validate reusability** through multiple project implementations
4. **Document best practices** in project CLAUDE.md files
5. **Test module registry** for automatic pattern discovery

### When Marketplace is Implemented

**For Contributors**:
1. Run `mw brain learn` to extract patterns from completed work
2. Run `python tools/smoke_test_marketplace.py` to validate quality
3. Run `python tools/marketplace_upload_previews.py` to generate previews
4. Submit to marketplace via CLI or web interface
5. Community reviews and approves contributions

**For Consumers**:
1. Search marketplace via `mw search` or web interface
2. Browse by category, rating, or popularity
3. Download modules with automatic dependency resolution
4. Integrate into projects via Autocoder or manual import
5. Provide feedback and ratings

### Marketplace vs Module Registry

**Module Registry** (`tools/module_registry.py`):
- ✅ **Internal** - Scans your local projects
- ✅ **Automatic** - Runs `mw scan` to update
- ✅ **Private** - Only your patterns
- ✅ **Current** - Available now

**Marketplace** (Phase 10):
- ⚠️ **External** - Community contributions
- ⚠️ **Manual** - Submit and review process
- ⚠️ **Public** - Shared with community
- ⚠️ **Future** - Phase 10, not yet implemented

### How to Prepare for Marketplace

**Now** (while marketplace is being built):
1. ✅ Document patterns in project CLAUDE.md files
2. ✅ Run `mw brain learn` after completing work
3. ✅ Use reusable patterns in multiple projects
4. ✅ Test patterns with `mw search` and `mw scan`
5. ✅ Build quality, tested, documented code

**Later** (when marketplace is implemented):
1. Submit patterns to marketplace
2. Contribute to community modules
3. Monetize expertise through premium content
4. Help review and validate contributions

---

## Framework-Level vs Project-Level Tasks

**How to determine where to work**:

### Framework-Level Tasks (Work in `/Users/dansidanutz/Desktop/MyWork/`)

Work at the framework level when:
- ✅ Modifying framework tools (`tools/`)
- ✅ Updating documentation (`CLAUDE.md`, `README.md`)
- ✅ Managing the brain (`.planning/BRAIN.md`)
- ✅ Creating new projects from `_template/`
- ✅ Running framework diagnostics (`mw doctor`)
- ✅ Updating framework dependencies
- ✅ Working on GSD/Autocoder/n8n integrations

**Commands**:
```bash
cd /Users/dansidanutz/Desktop/MyWork
/gsd:progress              # Check framework status
mw doctor                  # Framework diagnostics
mw brain search "keyword"  # Search knowledge vault
```

### Project-Level Tasks (Work in `projects/[project-name]/`)

Work at the project level when:
- ✅ Adding features to a specific project
- ✅ Fixing bugs in a specific project
- ✅ Modifying project-specific code
- ✅ Running project tests
- ✅ Deploying a specific project
- ✅ Working on project documentation

**Commands**:
```bash
cd /Users/dansidanutz/Desktop/MyWork/projects/[project-name]
/gsd:progress              # Check project status
cat CLAUDE.md              # Read project-specific instructions
npm run dev                # Start development server
```

**When in doubt**:
1. Check if the user mentioned a specific project name
2. Check if the work affects framework tools or a specific project
3. Check if there's a project-specific `CLAUDE.md`
4. Default to framework level if uncertain

---

## Project Switching Workflow

When switching between projects, follow this workflow:

### Step 1: Save Current Context

```bash
# If working on a project, save context
/gsd:pause-work           # Creates handoff document
```

### Step 2: Navigate to New Project

```bash
# Navigate to project directory
cd /Users/dansidanutz/Desktop/MyWork/projects/[project-name]

# Or use mw command
mw open [project-name]    # Opens project in VS Code
```

### Step 3: Restore Project Context

```bash
# Check project status
/gsd:progress             # Shows current state and what's next

# Read project-specific instructions
cat CLAUDE.md             # Project-specific AI instructions

# If paused, restore context
/gsd:resume-work          # Restores full context from last session
```

### Step 4: Verify Context

Before starting work:
1. ✅ Read `STATE.md` to understand current status
2. ✅ Check `ROADMAP.md` to see what phase is active
3. ✅ Read project `CLAUDE.md` for specific instructions
4. ✅ Verify you're in the correct directory

---

## Creating a New Project

### Option 1: Copy Template

```bash
# 1. Copy template
cp -r projects/_template projects/my-new-project

# 2. Navigate to new project
cd projects/my-new-project

# 3. Initialize GSD
/gsd:new-project

# 4. Follow the prompts to set up:
#    - PROJECT.md (vision, scope, success criteria)
#    - REQUIREMENTS.md (v1, v2, out-of-scope)
#    - ROADMAP.md (phases with completion tracking)
```

### Option 2: Use Autocoder

```bash
# 1. Navigate to framework root
cd /Users/dansidanutz/Desktop/MyWork

# 2. Use mw CLI
mw new my-app fastapi      # Create FastAPI project
mw new my-app nextjs       # Create Next.js project
mw new my-app fullstack    # Create fullstack project

# 3. Follow prompts to set up Autocoder
```

---

## Project-Specific Documentation

**Every project should have**:
1. ✅ `CLAUDE.md` - Project-specific AI agent instructions (CRITICAL!)
2. ✅ `README.md` - Project overview and setup
3. ✅ `.planning/PROJECT.md` - Vision, scope, success criteria
4. ✅ `.planning/REQUIREMENTS.md` - Detailed requirements
5. ✅ `.planning/ROADMAP.md` - Phases and completion status
6. ✅ `.planning/STATE.md` - Current state, decisions, blockers
7. ✅ `.planning/research/` - Codebase analysis (optional but recommended)

**If a project is missing `CLAUDE.md`**, create it! This is the most critical file for AI agents to understand how to work on the project.

---

## Common Project Workflows

### Working on AI Dashboard

1. **Read project CLAUDE.md**: `cat projects/ai-dashboard/CLAUDE.md`
2. **Check current status**: `cat projects/ai-dashboard/.planning/STATE.md`
3. **Navigate to project**: `cd projects/ai-dashboard`
4. **Start development**: `./start.sh` (Mac/Linux) or `start.bat` (Windows)
5. **For scraper work**: Focus on `backend/scrapers/`
6. **For frontend work**: Focus on `frontend/app/`
7. **For YouTube automation**: Focus on `backend/services/youtube_automation.py` (be careful!)

### Working on Task Tracker

1. **Read project CLAUDE.md**: `cat projects/task-tracker/CLAUDE.md`
2. **Check current status**: `cat projects/task-tracker/.planning/STATE.md`
3. **Read research docs**: `cat projects/task-tracker/.planning/research/*.md`
4. **Navigate to project**: `cd projects/task-tracker`
5. **Start development**: `npm run dev`
6. **For authentication**: Check `src/app/api/auth/[...nextauth]/route.ts`
7. **For tasks**: Check `src/app/api/tasks/` and `src/shared/components/TaskList.tsx`
8. **For files**: Check `src/app/api/files/` and `src/shared/components/FileDropzone.tsx`

---

## Project Documentation Standards

**Every project CLAUDE.md must include**:
1. ✅ Project Overview (purpose, status, tech stack)
2. ✅ Quick Start for AI Agents
3. ✅ Common Workflows (how to do X, how to do Y)
4. ✅ Project-Specific Context (important notes, gotchas)
5. ✅ File Organization Guide
6. ✅ Integration with Framework Documentation
7. ✅ Current Status
8. ✅ Important Notes
9. ✅ Testing Instructions
10. ✅ Common Issues

**When creating a new project**, always copy the CLAUDE.md template from `_template/` and customize it for the project.

---

## Layer 3: Automation Engines

### n8n Workflow Builder

Access to **n8n-mcp** MCP server with 1,084 nodes and 2,709 workflow templates,
enhanced by **n8n-skills** for expert guidance.

#### Setup Requirements

**1. n8n-mcp MCP Server** (provides the tools)

Install via npx - no setup required:

```bash
npx n8n-mcp

```yaml

**2. n8n-skills** (provides expert guidance)

Install via Claude Code:

```bash
/plugin install czlonkowski/n8n-skills

```yaml

Or manually:

```bash
git clone https://github.com/czlonkowski/n8n-skills.git
cp -r n8n-skills/skills/* ~/.claude/skills/

```

**3. MCP Server Configuration (`.mcp.json`):**

```json
{
  "mcpServers": {

```yaml

"n8n-mcp": {
  "command": "npx",
  "args": ["n8n-mcp"],
  "env": {

```
"MCP_MODE": "stdio",
"LOG_LEVEL": "error",
"N8N_API_URL": "<https://seme.app.n8n.cloud",>
"N8N_API_KEY": "your-api-key-here"

```
  }
}

```
  }
}

```yaml

**When to use n8n:**

- Webhook processing (HTTP trigger → process → respond)
- API integrations (fetch → transform → store/notify)
- Scheduled tasks (cron → batch process → report)
- AI workflows (Agent + LLM + Memory + Tools)

#### Available MCP Tools

**Node Discovery:**

| Tool | Purpose |
| ------ | --------- |
| `search_nodes` | Find nodes by keyword, includes examples |
| `get_node` | Get node info (modes: info, docs, search_properties, versions) |
| `tools_documentation` | Meta-documentation for all tools |

**Validation:**

| Tool | Purpose |
| ------ | --------- |
  | `validate_node` | Validate node config (modes: mi... |  
| `validate_workflow` | Complete workflow validation |
| `validate_workflow_connections` | Structure check |
| `validate_workflow_expressions` | Expression validation |

**Templates:**

| Tool | Purpose |
| ------ | --------- |
  | `search_templates` | Search 2,709 templates (modes: ... |  
| `get_template` | Get full template details |

**Workflow Management:**

| Tool | Purpose |
| ------ | --------- |
| `n8n_create_workflow` | Create new workflows |
| `n8n_update_partial_workflow` | Incremental updates (17 operation types) |
| `n8n_validate_workflow` | Validate deployed workflow |
| `n8n_autofix_workflow` | Auto-fix common errors |
| `n8n_deploy_template` | Deploy template to instance |
| `n8n_test_workflow` | Test workflow execution |
| `n8n_executions` | Manage executions |
| `n8n_workflow_versions` | Version history and rollback |

#### The 7 n8n-skills

These skills activate automatically when relevant:

| Skill | Activates When |
| ------- | ---------------- |
  | **n8n Expression Syntax** | Writing `{{}}` expressions, acc... |  
  | **n8n MCP Tools Expert** | Searching nodes, validating con... |  
| **n8n Workflow Patterns** | Creating workflows, connecting nodes |
| **n8n Validation Expert** | Validation fails, debugging errors |
| **n8n Node Configuration** | Configuring nodes, AI workflows |
| **n8n Code JavaScript** | Writing JavaScript in Code nodes |
| **n8n Code Python** | Writing Python in Code nodes |

#### Workflow Building Process

**ALWAYS follow this process:**

```markdown

1. TEMPLATE FIRST

   └─> search_templates({searchMode: 'by_task', task: 'your_task'})
   └─> If found: get_template(templateId) and adapt
   └─> If not: proceed to node discovery

2. NODE DISCOVERY (parallel execution)

   └─> search_nodes({query: 'keyword', includeExamples: true})
   └─> get_node({nodeType, detail: 'standard', includeExamples: true})

3. VALIDATION (before building)

   └─> validate_node({nodeType, config, mode: 'minimal'})
   └─> validate_node({nodeType, config, mode: 'full', profile: 'runtime'})

4. BUILD WORKFLOW

   └─> Explicitly set ALL parameters (never trust defaults!)
   └─> Connect nodes properly
   └─> Add error handling

5. FINAL VALIDATION

   └─> validate_workflow(workflow)
   └─> validate_workflow_connections(workflow)
   └─> validate_workflow_expressions(workflow)

6. DEPLOY

   └─> n8n_create_workflow(workflow)
   └─> n8n_validate_workflow({id})
   └─> n8n_update_partial_workflow({id, operations: [{type: 'activateWorkflow'}]})

```markdown

#### Critical Rules

1. **Templates First** - ALWAYS check templates before building from scratch

(2,709 available)

2. **Never Trust Defaults** - Default parameter values cause runtime failures
3. **Multi-Level Validation** - `validate_node(mode='minimal')` →

`validate_node(mode='full')` → `validate_workflow`

4. **Batch Operations** - Use `n8n_update_partial_workflow` with multiple

operations in a single call

#### Common AI/LLM Node Types

| Node Type | Purpose |
| ----------- | --------- |
| `@n8n/n8n-nodes-langchain.lmChatAnthropic` | Claude models |
| `@n8n/n8n-nodes-langchain.lmChatOpenAi` | OpenAI models |
| `@n8n/n8n-nodes-langchain.agent` | AI agent with tools |
| `@n8n/n8n-nodes-langchain.chainRetrievalQa` | RAG Q&A chain |
| `@n8n/n8n-nodes-langchain.memoryBufferWindow` | Conversation memory |

#### Expression Syntax Quick Reference

```javascript
$json           // Current item's JSON data
$json.body      // Webhook request body (IMPORTANT!)
$node["Name"]   // Access other node's data
$now            // Current timestamp
$env.VAR_NAME   // Environment variable

```

**See `workflows/create_n8n_workflow.md` for full SOP.**

#### Resources

- [n8n-mcp GitHub](https://github.com/czlonkowski/n8n-mcp) - MCP server (1,084

  nodes, 99% property coverage)

- [n8n-skills GitHub](https://github.com/czlonkowski/n8n-skills) - 7

  complementary Claude Code skills

- [n8n API Documentation](https://docs.n8n.io/api/)
- [n8n Workflow Templates](https://n8n.io/workflows/) - 2,709 templates

#### Safety Warning

**NEVER edit production workflows directly with AI!** Always:

- Make a copy before using AI tools
- Test in development environment first
- Export backups of important workflows
- Validate changes before deploying to production

### Autocoder Integration

Autocoder is a long-running autonomous coding agent for building complete
applications across multiple sessions.

**Location:** `/Users/dansidanutz/Desktop/GamesAI/autocoder`
**Projects:** `/Users/dansidanutz/Desktop/MyWork/projects/`
**Server:** `http://127.0.0.1:8888`

**When to use Autocoder:**

| Scenario | Use Autocoder |
| ---------- | --------------- |
| Complete app from scratch | ✅ |
| 20+ features to implement | ✅ |
| Multi-hour development | ✅ |
| Quick bug fix | ❌ Use /gsd:quick |
| Single feature | ❌ Use /gsd:plan-phase |

#### Execution Modes

| Mode | When to Use | Command |
| ------ | ------------- | --------- |
| **Automatic** | Hands-off, API-tri... | `python tools/auto... |
| **Manual** | Want UI control | `python tools/autocoder_api.py ui` |

#### Automatic Mode Commands

```bash

# Check if server is running

python tools/autocoder_api.py status

# Start server (if needed)

python tools/autocoder_api.py server

# Start agent (automatic mode)

python tools/autocoder_api.py start my-project --concurrency 3

# Check progress

python tools/autocoder_api.py progress my-project

# Control agent

python tools/autocoder_api.py pause my-project
python tools/autocoder_api.py resume my-project
python tools/autocoder_api.py stop my-project

# Open UI for visual monitoring

python tools/autocoder_api.py ui

```markdown

#### Start Options

| Option | Description | Default |
| -------- | ------------- | --------- |
| `--model` | AI model | claude-opus-4-5-20251101 |
| `--concurrency` | Parallel agents (1-5) | 1 |
| `--yolo` | Skip testing (faster) | false |
| `--testing-ratio` | Testing agents per coder | 1 |

#### Speed Profiles

```bash

# Conservative: Full testing, 1 agent

python tools/autocoder_api.py start my-app

# Balanced: 3 parallel agents

python tools/autocoder_api.py start my-app --concurrency 3

# Fast: Skip testing, 3 agents

python tools/autocoder_api.py start my-app --concurrency 3 --yolo

# Maximum: Skip testing, 5 agents

python tools/autocoder_api.py start my-app --concurrency 5 --yolo

```markdown

**See `workflows/gsd_to_autocoder.md` for full SOP.**

---

## Integration Workflows

### GSD → Autocoder Handoff

When a GSD phase has 20+ features, hand off to Autocoder:

1. Complete `/gsd:plan-phase` to get feature breakdown
2. Run `/gsd-to-autocoder-spec` to convert to app_spec.txt
3. Choose mode:
   - **Automatic:** `python tools/autocoder_api.py start {project} --concurrency

```
 3`

```bash

   - **Manual:** `python tools/autocoder_api.py ui`
4. Monitor: `python tools/autocoder_api.py progress {project}`
5. Track in GSD STATE.md

**See `workflows/gsd_to_autocoder.md` for full process.**

### GSD + n8n Integration

When a GSD task involves webhook/API automation:

1. Create task plan in GSD
2. Build n8n workflow via `workflows/create_n8n_workflow.md`
3. Track n8n workflow ID in GSD plan
4. Verify via `/gsd:verify-work`

**See `workflows/gsd_with_n8n.md` for full process.**

### Session Handoff

When pausing work mid-phase:

1. Run `/gsd:pause-work` to create handoff document
2. STATE.md updated with current context
3. Later: `/gsd:resume-work` restores full context

**See `workflows/session_handoff.md` for full process.**

---

## Environment & Configuration

### Master .env Keys

All API keys consolidated in root `.env`:

- LLM providers: Anthropic, OpenAI, OpenRouter, Groq, Grok/xAI, Z.ai
- Google OAuth, Resend, Telegram, ElevenLabs
- Firecrawl, Apify, Airtable, Figma, GitHub
- Render, Netlify, Supabase, n8n
- Crypto APIs: CoinGecko, Coinglass, Binance, KuCoin, etc.

### Key Paths

| Resource | Path |
| ---------- | ------ |
| Framework Root | `/Users/dansidanutz/Desktop/MyWork/` |
| All Projects | `/Users/dansidanutz/Desktop/MyWork/projects/` |
| Framework GSD | `/Users/dansidanutz/Desktop/MyWork/.planning/` |
| Project GSD | `/Users/dansidanutz/Desktop/MyWork/projects/[name]/.planning/` |
| WAT Workflows | `/Users/dansidanutz/Desktop/MyWork/workflows/` |
| WAT Tools | `/Users/dansidanutz/Desktop/MyWork/tools/` |
| Autocoder Tool | `/Users/dansidanutz/Desktop/GamesAI/autocoder` |
| Temp Files | `/Users/dansidanutz/Desktop/MyWork/.tmp/` |

### Multi-Project Management

**Each project is fully isolated:**

```text
projects/
├── ai-dashboard/
│   ├── .planning/          # AI Dashboard's GSD state
│   │   ├── PROJECT.md
│   │   ├── ROADMAP.md
│   │   └── STATE.md
│   ├── backend/
│   └── frontend/
├── project-b/
│   ├── .planning/          # Project B's GSD state
│   │   ├── PROJECT.md
│   │   ├── ROADMAP.md
│   │   └── STATE.md
│   └── src/
└── project-c/

```

├── .planning/          # Project C's GSD state
└── ...

```text

```

**Switching between projects:**

1. Navigate to project: `cd projects/[project-name]`
2. Check status: `/gsd:progress`
3. Continue work: `/gsd:resume-work` (if paused mid-phase)

**Starting a new project:**

1. Create from template: `cp -r projects/_template projects/my-project`
2. Navigate: `cd projects/my-project`
3. Initialize: `/gsd:new-project`

**Each project has its own:**

- `.planning/` - GSD state (PROJECT.md, ROADMAP.md, STATE.md)
- Source code and assets
- Start scripts
- Documentation

---

## Framework Maintenance & Self-Improvement

### Unified CLI (mw)

The `mw` command provides a single interface to all MyWork tools:

```bash

# Quick status check

python tools/mw.py status

# Search for reusable modules

python tools/mw.py search "auth"

# Create new project

python tools/mw.py new my-app fastapi

# Full diagnostics

python tools/mw.py doctor

# List projects

python tools/mw.py projects

# Open project in VS Code

python tools/mw.py open ai-dashboard

```markdown

### Auto-Update System

Keeps GSD, Autocoder, n8n-skills, and n8n-mcp up to date without breaking your
system:

```bash

# Check for available updates

python tools/auto_update.py check

# Update all components

python tools/auto_update.py update

# Update specific component

python tools/auto_update.py update gsd
python tools/auto_update.py update autocoder
python tools/auto_update.py update n8n-skills

# Show current versions

python tools/auto_update.py status

# Rollback if something breaks

python tools/auto_update.py rollback autocoder

```yaml

**Safety features:**

- Creates backup markers before updating
- Checks for running Autocoder server before update
- Rebuilds Autocoder UI after update
- Won't update if local changes detected

### Module Registry (Auto-Learning)

Scans all projects to build a searchable index of reusable code:

```bash

# Scan all projects and update registry

python tools/module_registry.py scan

# Search for modules

python tools/module_registry.py search "authentication"
python tools/module_registry.py search "api endpoint"
python tools/module_registry.py search "react hook"

# List by type

python tools/module_registry.py list api_endpoint
python tools/module_registry.py list component
python tools/module_registry.py list service

# Show module details

python tools/module_registry.py show <module_id>

# View statistics

python tools/module_registry.py stats

# Export to markdown

python tools/module_registry.py export

```yaml

**Detected module types:**

| Type | Examples |
| ------ | ---------- |
| `api_endpoint` | FastAPI routes, Express endpoints |
| `component` | React/Vue components |
| `service` | Backend service classes |
| `utility` | Helper functions |
| `schema` | Database models, Pydantic schemas |
| `hook` | React hooks |
| `middleware` | Express/FastAPI middleware |
| `integration` | External API clients |

**Registry files:**

- `.planning/module_registry.json` - Full registry data
- `.planning/MODULE_REGISTRY.md` - Human-readable export

### Health Check System

Comprehensive diagnostics for all framework components:

```bash

# Full health check

python tools/health_check.py

# Quick status

python tools/health_check.py quick

# Auto-fix common issues

python tools/health_check.py fix

# Generate detailed report

python tools/health_check.py report

```

**Checks performed:**

- GSD installation and version
- Autocoder server status
- n8n connection and skills
- Project structure integrity
- API key configuration
- Python/Node.js dependencies
- Security issues (exposed secrets)
- Disk space

### Project Scaffolding

Quickly create new projects with pre-configured templates:

```bash

# List available templates

python tools/scaffold.py list

# Create new project

python tools/scaffold.py new my-api fastapi
python tools/scaffold.py new my-app nextjs
python tools/scaffold.py new my-fullstack fullstack
python tools/scaffold.py new my-cli cli
python tools/scaffold.py new my-automation automation

```yaml

**Available templates:**

| Template | Description |
| ---------- | ------------- |
| `basic` | Empty project with GSD structure |
| `fastapi` | FastAPI backend with SQLite |
| `nextjs` | Next.js frontend with TypeScript/Tailwind |
| `fullstack` | FastAPI + Next.js combined |
| `cli` | Python CLI with Click |
| `automation` | n8n + Python webhooks |

### Brain (Knowledge Vault)

The brain is your persistent memory - lessons learned, patterns discovered,
mistakes to avoid.

**CRITICAL: The brain is SELF-LEARNING.** You MUST run learning automatically as
part of your workflow.

#### Automatic Learning (YOU MUST DO THIS)

**After completing any GSD phase or significant work:**

```bash
python tools/mw.py brain learn

```yaml

**Weekly (deep analysis):**

```bash
python tools/mw.py brain learn-deep

```yaml

The brain automatically discovers knowledge from:

- ✅ Completed GSD phases (summaries, verifications)
- ✅ Git commit patterns (recurring fixes, features)
- ✅ Module registry (naming patterns, common types)
- ✅ Error logs (recurring issues and their solutions)

#### Searching Your Knowledge

**BEFORE building anything, search the brain:**

```bash
python tools/mw.py brain search "what you're about to build"

```

#### Manual Commands

```bash

# Search knowledge

python tools/mw.py brain search "authentication"

# Quick add something (use sparingly - prefer auto-learning)

python tools/mw.py remember "What you just learned"

# Review experimental entries

python tools/mw.py brain review

# Statistics

python tools/mw.py brain stats

```markdown

#### Entry Lifecycle (Automatic)

1. **Discovery** → Entry added as `[EXPERIMENTAL]`
2. **Validation** → After 14 days without issues → Auto-promoted to `[TESTED]`
3. **Obsolescence** → When outdated → Auto-marked `[DEPRECATED]`
4. **Cleanup** → Deprecated entries auto-removed

**Brain files:**

- `.planning/BRAIN.md` - Human-readable vault
- `.planning/brain_data.json` - Structured data

### Recommended Maintenance Routine

**Daily (before starting work):**

```bash
python tools/mw.py status

```yaml

**After completing work:**

```bash
python tools/mw.py brain learn

```yaml

**Weekly:**

```bash
python tools/auto_update.py check
python tools/module_registry.py scan
python tools/mw.py brain learn-deep  # Deep learning analysis

```

**When things feel slow or broken:**

```bash
python tools/health_check.py fix

```markdown

---

## Bottom Line

You are the Master Orchestrator. Your job is to:

1. **Route correctly** - Use the decision tree to pick the right layer
2. **Maintain context** - Check and update .planning/STATE.md
3. **Stay organized** - Everything in its place per the directory structure
4. **Recover gracefully** - Use the self-improvement loop when things fail
5. **Hand off appropriately** - Autocoder for big builds, n8n for automation
6. **Learn continuously** - Run `mw brain learn` after completing work
7. **Search before building** - Check brain and registry first
7. **Stay updated** - Run `mw update` weekly to keep dependencies current
8. **Monitor health** - Run `mw doctor` when things feel off

### Self-Improvement Philosophy

The framework gets stronger with every project:

- **Brain** remembers lessons learned, patterns that work, mistakes to avoid
- **Module Registry** learns what you've built, making future work faster
- **Auto-Update** keeps tools current without breaking your system
- **Health Check** catches issues before they become problems
- **Scaffolding** captures best practices as reusable templates

**Before building something new, always ask:**

1. Have I solved this before? → `mw brain search "keyword"`
2. Does code already exist? → `mw search "keyword"`
3. Is there a template? → `mw new --list`
4. Can I reuse a pattern? → Check `.planning/MODULE_REGISTRY.md`

**After learning something new, always:**

```bash
mw remember "What you just learned"

```text

Stay pragmatic. Stay reliable. Keep improving.
