# Master Orchestrator Brain

> A living knowledge vault that grows with every project.
> Last updated: 2026-01-28

---

## How This Works

This file is the Master Orchestrator's persistent memory. It contains:

- **Lessons learned** from real projects
- **Patterns that work** (tested and proven)
- **Anti-patterns to avoid** (mistakes not to repeat)
- **Tool wisdom** (tips and tricks discovered)
- **Integration insights** (how things connect)

### Rules for This File

1. **Add** when you discover something useful
2. **Update** when you find a better way
3. **Delete** when something becomes outdated or wrong
4. **Tag** entries with `[TESTED]`, `[EXPERIMENTAL]`, or `[DEPRECATED]`
5. **Date** significant updates

---

## Lessons Learned

### Project Management

| Lesson | Context | Date |
|--------|---------|------|
  | [T] Always check `.p... | Prevents duplicate e... | 2026-01-24 |  
  | [T] Run module regis... | Found 1,347 reusable... | 2026-01-24 |  
  | [T] GSD phases shoul... | Large phases cause c... | 2026-01-24 |  

### Code Quality

| Lesson | Context | Date |
|--------|---------|------|
  | [T] Never hardcode A... | Security vulnerabili... | 2026-01-24 |  
  | [T] Read from .env f... | Secure and configurable | 2026-01-24 |  

### Tool Usage

| Lesson | Context | Date |
|--------|---------|------|
  | [T] Use `npx` for n8... | Avoids stale cached ... | 2026-01-24 |  
  | [T] Check Autocoder ... | Prevents corruption | 2026-01-24 |  

---

## Patterns That Work

### Project Setup Pattern

```bash

1. mw new <name> <template>     # Scaffold with template
2. cd projects/<name>           # Enter project
3. /gsd:new-project            # Initialize GSD state
4. mw search "relevant keywords" # Find reusable modules
5. /gsd:plan-phase 1           # Plan first phase

```text

**Status:** [TESTED] | **Added:** 2026-01-24

### Debug Pattern

```bash

1. Check error message carefully
2. Search module registry for similar patterns
3. Check if issue exists in other projects
4. Fix in isolation, test, then integrate
5. Document fix in BRAIN.md if novel

```text

**Status:** [TESTED] | **Added:** 2026-01-24

### Context Recovery Pattern

```bash

1. Read .planning/STATE.md
2. Read .planning/ROADMAP.md (current phase)
3. Check git log for recent commits
4. Run mw status for system health
5. Continue from documented state

```text

**Status:** [TESTED] | **Added:** 2026-01-24

### Safe Update Pattern

```bash

1. python tools/auto_update.py check  # See what's available
2. python tools/auto_update.py status # Current versions
3. Ensure Autocoder server is stopped
4. python tools/auto_update.py update <component>
5. python tools/health_check.py       # Verify nothing broke
6. python tools/auto_update.py rollback <component> # If needed

```text

**Status:** [TESTED] | **Added:** 2026-01-24

---

## Anti-Patterns to Avoid

### Never Do These

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
  | Building without s... | Wastes time reinve... | `mw search "keywor... |  
  | Hardcoding paths in ... | Breaks portability | Use Path variables f... |  
  | Skipping GSD state... | Lose context betwe... | Always update STAT... |  
  | Running git comman... | May commit unwante... | Always `git status... |  
  | Updating dependencie... | Can break everything | Use `auto_update.py`... |  
  | Editing production... | Risk of breaking l... | Copy, edit, test, ... |  

### Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Forgot to activate venv | `ModuleNotFoundError` | `source venv/bin/activate` |
| Port already in use | `Address already in use` | `lsof -i :<port>` then kill |
| Stale node_modules | Mysterious JS errors | `rm -rf node_modules && npm ci` |
  | Git merge conflicts ... | GSD state corrupted | Manually resolve, pr... |  

---

## Tool Wisdom

### mw (Unified CLI)

- `mw status` is your morning coffee - run it daily
- `mw search` before `mw new` - don't rebuild what exists
- `mw doctor` when anything feels wrong

### GSD

- `/gsd:discuss-phase` before `/gsd:plan-phase` - saves rework
- `/gsd:pause-work` before stopping - preserves context
- `/gsd:verify-work` after execution - catches issues early

### Autocoder

- Start with `--concurrency 1` until confident in spec
- Use `--yolo` only for prototypes, never production
- Monitor with `mw ac status` during long runs
- WebSocket at `ws://127.0.0.1:8888/ws/projects/{name}` for real-time

### n8n

- ALWAYS search templates first (2,709 available)
- Validate nodes before building workflow
- Never trust default parameter values
- Test with sample data before activating

### Module Registry

- Scan after completing any project
- Export to markdown for easy browsing
- Search by type when you know what you need: `list component`

---

## Integration Insights

### GSD + Autocoder

- Autocoder needs app_spec.txt, GSD produces PLAN.md
- Use `/gsd-to-autocoder-spec` to convert
- Track Autocoder progress in STATE.md
- 20+ features = Autocoder territory

### GSD + n8n

- Track workflow IDs in GSD plans
- n8n handles automation, GSD handles code
- Webhooks connect them: n8n triggers → API → updates

### Module Registry + Scaffolding

- Registry learns from completed projects
- Scaffolding creates starting points
- Together: don't start from zero, start from best practices

---

## Performance Tips

### Speed Optimizations

| Tip | Impact | Verified |
|-----|--------|----------|
| Use `--concurrency 3` for Autocoder when specs are solid | 3x faster | Yes |
| Run module registry scan in background | Non-blocking | Yes |
| Use health_check quick mode for daily checks | 5x faster | Yes |
| Parallel tool calls when independent | Significant | Yes |

### Resource Management

- Clear `.tmp/` periodically
- Watch disk space with `mw doctor`
- Kill zombie processes: `lsof -i :8888`

---

## Project-Specific Insights

### ai-dashboard

- Uses FastAPI + Next.js pattern
- Scheduler runs scrapers on intervals
- No auth yet - add before public deployment
- 88 modules indexed, reusable for similar projects

### Autocoder (my-games)

- 1,259 modules - rich source of patterns
- Parallel orchestrator is 53KB of logic
- Security module has command allowlist
- Good example of large Python project structure

---

## Pending Experiments

| Experiment | Hypothesis | Status |
|------------|------------|--------|
  | Auto-scan after git ... | Would keep registry ... | [IDEA] |  
| Weekly brain cleanup | Remove [DEPRECATED] entries automatically | [IDEA] |
  | Cross-project depend... | Know when updating o... | [IDEA] |  

---

## Changelog

| Date | Change | Category |
| 2026-01-28 | Auto-learning: 15 entries | Learning |

| 2026-01-27 | Auto-learning: 14 entries | Learning |
|------|--------|----------|
| 2026-01-24 | Initial brain created | Setup |
| 2026-01-24 | Added security lesson about hardcoded keys | Lessons |
| 2026-01-24 | Added module registry insights | Tools |
| 2026-01-24 | Added all patterns and anti-patterns | Patterns |

---

## Meta

### How to Update This File

**Adding a lesson:**

```bash
python tools/brain.py add lesson "Your lesson here" \
    --context "Where you learned it"
```text

**Adding a pattern:**

```bash
python tools/brain.py add pattern "Pattern name" --steps "1. First\n2. Second"
```text

**Marking something deprecated:**

```bash
python tools/brain.py deprecate "entry identifier"

```text

**Cleaning up:**

```bash
python tools/brain.py cleanup  # Removes [DEPRECATED] entries

```text

**Reviewing:**

```bash
python tools/brain.py review   # Shows entries needing attention

```text
