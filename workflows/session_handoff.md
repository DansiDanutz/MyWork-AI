# Workflow: Session Handoff

## Objective

Preserve context when pausing work mid-phase and restore it seamlessly when
resuming.

## When to Use

- Stopping work mid-phase (end of day, context switch)
- Need to hand off to another session/context
- Long-running task needs to be paused
- Before clearing context with `/clear`

## When NOT to Use

- Phase is complete (use `/gsd:complete-milestone` instead)
- Just checking status (use `/gsd:progress`)
- Starting fresh work (no handoff needed)

## Prerequisites

- GSD project initialized
- Work in progress on a phase
- `.planning/STATE.md` exists

## Process

### Step 1: Pause Work

When you need to stop mid-phase:

```yaml
/gsd:pause-work

```

This creates a handoff document capturing:

- Current phase and task
- What was just completed
- What's next
- Any blockers or decisions needed
- Relevant file paths

### Step 2: Review Handoff

The command updates `.planning/STATE.md` with:

```markdown

## Session Handoff

**Created:** 2026-01-24T15:30:00Z
**Phase:** 3
**Task:** 3.2 - Implement user authentication

### Completed This Session

- Set up auth middleware
- Created login endpoint
- Added JWT token generation

### Next Steps

1. Implement logout endpoint
2. Add token refresh logic
3. Write auth tests

### Blockers

- Need to decide on token expiry time (1h vs 24h)

### Key Files

- `src/middleware/auth.ts` - Auth middleware (modified)
- `src/routes/auth.ts` - Auth routes (new)
- `src/utils/jwt.ts` - JWT helpers (new)

### Notes

- Using jose library for JWT (not jsonwebtoken)
- Token stored in httpOnly cookie

```markdown

### Step 3: Confirm Save

Verify STATE.md was updated:

```bash
cat .planning/STATE.md | head -50

```

### Step 4: Safe to Exit

Now you can:

- Close the session
- Clear context with `/clear`
- Switch to different work
- Hand off to someone else

---

## Resuming Work

### Step 1: Resume Session

When starting a new session:

```yaml
/gsd:resume-work

```

This:

1. Reads `.planning/STATE.md`
2. Loads the handoff context
3. Reads relevant files mentioned
4. Presents summary of where you left off

### Step 2: Review Context

You'll see:

- What phase/task you were on
- What was completed
- What's next
- Any pending decisions

### Step 3: Continue Work

Either:

- Continue with next task
- Address any blockers first
- Ask clarifying questions if needed

### Step 4: Clear Handoff

Once you've resumed and made progress:

- STATE.md handoff section auto-updates
- Or manually clear if fully caught up

## Manual Handoff (Without Commands)

If GSD commands unavailable, manually update STATE.md:

```markdown

## Session Handoff

**Created:** [timestamp]
**Phase:** [N]
**Task:** [current task]

### Completed This Session

- [list items]

### Next Steps

1. [next task]
2. [following task]

### Key Files

- `path/to/file.ts` - [description]

```markdown

## Expected Outputs

- `.planning/STATE.md` updated with handoff section
- Clear context for next session
- No lost work or forgotten decisions

## Error Handling

- **Handoff incomplete**: Manually add missing context to STATE.md
- **Resume fails to load**: Read STATE.md directly, continue manually
- **Conflicting state**: Check git history, resolve manually

## Best Practices

1. **Pause at natural breaks** - End of task, not mid-implementation
2. **Be specific** - Include file paths, line numbers if relevant
3. **Note decisions** - Especially pending ones that need input
4. **List blockers** - So next session can address them first
5. **Keep it current** - Update STATE.md as you progress, not just at pause

## Notes

- Handoff is automatic with `/gsd:pause-work`
- STATE.md is the single source of truth
- Git commits also help track progress
- Consider committing before pausing for safety
