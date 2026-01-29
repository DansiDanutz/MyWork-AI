# Framework Maintenance Workflow

## Objective

Keep the MyWork framework healthy, updated, and continuously learning from
projects.

## When to Use

- Starting a new work session
- Weekly maintenance routine
- When something feels broken or slow
- After completing a major project

---

## Quick Start Commands

```bash

# Single command for everything

python tools/mw.py doctor

# Or individual checks

python tools/mw.py status           # Quick overview
python tools/auto_update.py check   # Check for updates
python tools/module_registry.py scan # Index all modules

```markdown

---

## Daily Routine (Before Starting Work)

### 1. Quick Status Check

```bash
python tools/mw.py status

```yaml

This shows:

- GSD installation status
- Autocoder server status
- n8n connection status

### 2. Review Any Issues

If warnings or errors appear, either:

- Fix immediately: `python tools/health_check.py fix`
- Note for later if non-blocking

---

## Weekly Maintenance

### 1. Check for Updates

```bash
python tools/auto_update.py check

```yaml

If updates available:

```bash

# Update everything safely

python tools/auto_update.py update

# Or update specific components

python tools/auto_update.py update gsd
python tools/auto_update.py update autocoder
python tools/auto_update.py update n8n-skills

```markdown

### 2. Scan Projects for New Modules

```bash
python tools/module_registry.py scan

```yaml

This indexes:

- API endpoints
- React/Vue components
- Backend services
- Utility functions
- Database schemas
- And more...

### 3. Export Registry (Optional)

```bash
python tools/module_registry.py export

```markdown

Creates `.planning/MODULE_REGISTRY.md` for easy browsing.

---

## When Something Breaks

### 1. Run Full Diagnostics

```bash
python tools/health_check.py

```markdown

### 2. Auto-Fix Common Issues

```bash
python tools/health_check.py fix

```yaml

This can fix:

- Missing directories
- Stale caches
- Common configuration issues

### 3. Generate Report for Complex Issues

```bash
python tools/health_check.py report

```markdown

Creates detailed markdown report in `.tmp/`.

### 4. Rollback if Update Caused Issues

```bash
python tools/auto_update.py rollback autocoder
python tools/auto_update.py rollback gsd

```markdown

---

## After Completing a Project

### 1. Scan to Index New Modules

```bash
python tools/module_registry.py scan

```markdown

### 2. Review What Was Built

```bash
python tools/module_registry.py stats

```markdown

### 3. Export for Future Reference

```bash
python tools/module_registry.py export

```markdown

---

## Finding Reusable Code

Before building something new:

### 1. Search the Registry

```bash

# Search by keyword

python tools/module_registry.py search "authentication"
python tools/module_registry.py search "api endpoint"
python tools/module_registry.py search "form validation"

```markdown

### 2. List by Type

```bash
python tools/module_registry.py list component
python tools/module_registry.py list service
python tools/module_registry.py list utility

```markdown

### 3. View Module Details

```bash
python tools/module_registry.py show <module_id>

```

Shows:

- File location
- Dependencies
- Tags
- How to open in editor

---

## Creating New Projects

### 1. List Templates

```bash
python tools/scaffold.py list

```markdown

### 2. Create Project

```bash
python tools/scaffold.py new my-project <template>

```yaml

Templates:

- `basic` - Empty with GSD structure
- `fastapi` - Python API backend
- `nextjs` - React frontend
- `fullstack` - API + Frontend
- `cli` - Command-line tool
- `automation` - n8n + webhooks

### 3. Initialize GSD

```bash
cd projects/my-project
/gsd:new-project

```markdown

---

## Troubleshooting

### GSD Not Found

```bash

# Check installation

ls ~/.claude/commands/gsd/

# Reinstall if missing

/install gsd

```markdown

### Autocoder Won't Start

```bash

# Check server status

python tools/autocoder_api.py status

# Check for port conflicts

lsof -i :8888

# Kill stuck process if needed

kill -9 <PID>

```markdown

### n8n Connection Failed

```bash

# Check .mcp.json configuration

cat .mcp.json

# Verify API key is set

grep N8N_API_KEY .env

```markdown

### Module Registry Empty

```bash

# Ensure projects exist

ls projects/

# Run scan with verbose output

python tools/module_registry.py scan

```markdown

---

## Best Practices

1. **Run status check daily** - Catches issues early
2. **Update weekly** - Stay current, avoid breaking changes piling up
3. **Scan after each project** - Build the knowledge base
4. **Search before building** - Don't reinvent the wheel
5. **Fix issues immediately** - Small problems compound into big ones

---

## Related Workflows

- `use_autocoder.md` - Long-running coding sessions
- `create_n8n_workflow.md` - Building automations
- `session_handoff.md` - Preserving context across sessions
