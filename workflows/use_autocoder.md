# Workflow: Use Autocoder for Application Development

## Objective

Build complete applications using the Autocoder autonomous coding agent for
multi-session development.

## When to Use This Workflow

- Building a complete application from scratch
- Project requires 20+ features
- Multi-hour/multi-session development expected
- Cost optimization is important (use z.ai provider)

## When NOT to Use

- Quick bug fixes (use direct coding)
- Single feature additions
- Code review or refactoring
- Simple scripts or utilities

## Prerequisites

- Autocoder installed at `/Users/dansidanutz/Desktop/GamesAI/autocoder`
- Terminal alias `autocoder` configured
- LLM provider configured in Autocoder's `.env`

## Process

### Phase 1: Requirements Gathering

1. Understand what the user wants to build
2. Identify target audience
3. List core features and functionality
4. Determine technology preferences (or use defaults)

### Phase 2: Create Project Spec

1. Start Autocoder UI: `autocoder`
2. Create new project in UI
3. **IMPORTANT:** Set project path to MyWork projects folder:

```text
   /Users/dansidanutz/Desktop/MyWork/projects/{project-name}

   ```

4. Use `/create-spec` command with the project path
5. Walk through the interactive specification wizard:
   - Project name and description
   - Core features (the main work)
   - User accounts/authentication needs
   - Data models and relationships
   - UI/UX requirements
5. Review generated `app_spec.txt`

### Phase 3: Start Development

1. Click "Start" in Autocoder UI
2. First session: Initializer agent creates features database
3. Subsequent sessions: Coding agent implements features
4. Monitor progress via Kanban board

### Phase 4: Monitor and Adjust

- Watch feature completion in UI
- Review agent output for issues
- Pause with Ctrl+C if intervention needed
- Resume by re-running start script

### Phase 5: Handoff

When Autocoder completes:

1. Review generated code in
`/Users/dansidanutz/Desktop/MyWork/projects/{project-name}/`
2. Run the application: `./init.sh` or `npm install && npm run dev`
3. Test functionality
4. Hand back to user with summary

## LLM Provider Options

| Provider | Config | Best For |
| ---------- | -------- | ---------- |
| Z.ai (Default) | Active in .env | Long sessions, cost savings |
| Claude Native | Comment out ANTHROPIC_* vars | Highest quality |

To switch providers, edit `/Users/dansidanutz/Desktop/GamesAI/autocoder/.env`

## Modes

### Standard Mode (Default)

- Full Playwright browser testing
- Regression testing
- Best for production quality

### YOLO Mode

```bash
python autonomous_agent_demo.py --project-dir {name} --yolo

```markdown

- Skip browser testing
- Faster iteration
- Use for prototyping

### Parallel Mode

```bash
python autonomous_agent_demo.py --project-dir {name} --parallel --max-concurrency 3

```

- Multiple concurrent agents
- Faster completion
- Higher resource usage

## Expected Outputs

- Complete application source code in
  `/Users/dansidanutz/Desktop/MyWork/projects/{project-name}/`
- SQLite database with feature tracking (`features.db`)
- Git repository with commits
- Running application (after init.sh)

## Path Configuration

- **Autocoder Tool:** `/Users/dansidanutz/Desktop/GamesAI/autocoder` (do not
  move)
- **Your Projects:** `/Users/dansidanutz/Desktop/MyWork/projects/`
- **Environment Variable:** `MYWORK_PROJECTS_PATH` in `.env`

## Error Handling

- If agent crashes: Check UI for error, restart with same project
- If feature fails: Agent will skip and retry later
- If stuck: Pause, review code, resume or adjust spec

## Notes

- First session takes several minutes (appears unresponsive)
- Each feature takes 5-15 minutes
- Full app (50 features) = many hours across sessions
- Progress webhooks sent to n8n for monitoring
