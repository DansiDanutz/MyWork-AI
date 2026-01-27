# Workflow: GSD to Autocoder Handoff

## Objective

Convert a GSD phase plan into an Autocoder app specification when the phase has 20+ features, enabling autonomous multi-session development.

## When to Use

- Phase has 20+ features identified in `/gsd:plan-phase`
- Multi-hour/multi-session development expected
- Cost optimization is important (Autocoder uses Z.ai by default)
- Building a complete application or major subsystem

## When NOT to Use

- Phase has <20 features (use `/gsd:execute-phase` directly)
- Quick fixes or single features (use `/gsd:quick`)
- Tight timeline requiring immediate iteration

## Prerequisites

- GSD project initialized (`.planning/PROJECT.md` exists)
- Phase planned via `/gsd:plan-phase N`
- Autocoder installed at `/Users/dansidanutz/Desktop/GamesAI/autocoder`

---

## Execution Modes

### Choose Your Mode

| Mode | When to Use | How |
|------|-------------|-----|
| **Automatic** | Hands-off, let it run | API-triggered, monitor via tool |
| **Manual** | Want UI control | Start via Autocoder UI |

---

## Process

### Step 1: Verify Phase is Ready

```bash

# Check phase plan exists

ls .planning/phases/phase-N/PLAN.md

# Review feature count

grep -c "feature\|task" .planning/phases/phase-N/PLAN.md

```

If feature count > 20, proceed with handoff.

### Step 2: Run Conversion Skill

```
/gsd-to-autocoder-spec

```

This skill:

1. Reads `.planning/codebase/` for tech stack context
2. Reads `.planning/phases/phase-N/PLAN.md` for features
3. Converts to Autocoder's `app_spec.txt` format
4. Generates `initializer_prompt.md` with feature count
5. Places files in `projects/{project-name}/prompts/`

### Step 3: Choose Execution Mode

---

## Option A: AUTOMATIC MODE (Recommended)

### A1. Ensure Server is Running

```bash

# Check status

python tools/autocoder_api.py status

# Start server if needed

python tools/autocoder_api.py server

```

### A2. Start Agent Automatically

```bash

# Start with default settings (1 agent, with testing)

python tools/autocoder_api.py start {project-name}

# Start with parallel agents (faster, more resources)

python tools/autocoder_api.py start {project-name} --concurrency 3

# Start in YOLO mode (skip testing, fastest)

python tools/autocoder_api.py start {project-name} --yolo --concurrency 3

```

### A3. Monitor Progress

```bash

# Check progress anytime

python tools/autocoder_api.py progress {project-name}

# Example output:

# {

#   "total": 45,

#   "passing": 12,

#   "in_progress": 2,

#   "pending": 31,

#   "agent_status": "running"

# }

# Progress: 12/45 features (26.7%)

```

### A4. Control Agent

```bash

# Pause if needed

python tools/autocoder_api.py pause {project-name}

# Resume later

python tools/autocoder_api.py resume {project-name}

# Stop completely

python tools/autocoder_api.py stop {project-name}

```

### A5. Open UI for Visual Monitoring (Optional)

```bash

# Open browser to Autocoder UI

python tools/autocoder_api.py ui

```

---

## Option B: MANUAL MODE

### B1. Open Autocoder UI

```bash

# Open UI in browser

python tools/autocoder_api.py ui

# OR start directly

cd /Users/dansidanutz/Desktop/GamesAI/autocoder
python start_ui.py

```

### B2. In the Autocoder UI:

1. Select the project from the list
2. Configure settings (model, concurrency, YOLO mode)
3. Click "Start"
4. Monitor progress visually
5. Click "Stop" when done

---

## Step 4: Track in GSD

Update `.planning/STATE.md`:

```markdown

## Active Handoff

- Phase: N
- Autocoder Project: /Users/dansidanutz/Desktop/MyWork/projects/{project-name}
- Execution Mode: Automatic | Manual
- Status: In Progress
- Features: {total} (from app_spec.txt)
- Started: {timestamp}

```

### Step 5: Monitor Progress

**Automatic Mode:**

```bash

# Quick check

python tools/autocoder_api.py progress {project-name}

# Continuous monitoring (run in separate terminal)

watch -n 30 "python tools/autocoder_api.py progress {project-name}"

```

**Manual Mode:**

- Check Autocoder UI for feature completion
- Watch the live output in the UI

**Webhook Notifications (Optional):**
Set `PROGRESS_N8N_WEBHOOK_URL` in `.env` for n8n notifications.

### Step 6: Complete Handoff

When Autocoder finishes:

1. Review generated code in `projects/{project-name}/`
2. Run the application to verify
3. Update GSD:

   ```
   /gsd:verify-work N

   ```

4. Mark phase complete in ROADMAP.md

---

## API Reference

### Available Commands

| Command | Description |
|---------|-------------|
| `status` | Check if Autocoder server is running |
| `server` | Start Autocoder server |
| `ui` | Open Autocoder UI in browser |
| `start {project}` | Start agent (automatic mode) |
| `stop {project}` | Stop running agent |
| `pause {project}` | Pause agent |
| `resume {project}` | Resume paused agent |
| `progress {project}` | Get feature progress |
| `list` | List all registered projects |

### Start Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model` | Model to use | claude-opus-4-5-20251101 |
| `--concurrency` | Parallel coding agents | 1 |
| `--yolo` | Skip testing (faster) | false |
| `--testing-ratio` | Testing agents per coding agent | 1 |

### Examples

```bash

# Conservative: 1 agent, full testing

python tools/autocoder_api.py start my-app

# Balanced: 3 parallel agents

python tools/autocoder_api.py start my-app --concurrency 3

# Fast: 3 agents, skip testing

python tools/autocoder_api.py start my-app --concurrency 3 --yolo

# Maximum speed: 5 agents, skip testing

python tools/autocoder_api.py start my-app --concurrency 5 --yolo

```

---

## Expected Outputs

- `app_spec.txt` in Autocoder project
- `initializer_prompt.md` with correct feature count
- Working application in `projects/{project-name}/`
- GSD STATE.md updated throughout

## Error Handling

- **Server not running**: `python tools/autocoder_api.py server`
- **Conversion fails**: Check `.planning/phases/phase-N/PLAN.md` format
- **Autocoder crashes**: Check logs, restart with same project
- **Feature fails**: Autocoder retries automatically (up to 3 times)
- **Need to pause**: `python tools/autocoder_api.py pause {project}`

## Notes

- Autocoder uses Claude Opus 4.5 by default
- Server runs at http://127.0.0.1:8888
- First session: Initializer creates features (takes several minutes)
- Each feature: 5-15 minutes depending on complexity
- WebSocket available at ws://127.0.0.1:8888/ws/projects/{name}
