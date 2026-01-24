# Workflow: GSD with n8n Integration

## Objective
Execute GSD tasks that involve visual workflow automation using n8n, tracking the workflow within the GSD phase structure.

## When to Use
- GSD task requires webhook processing
- Task involves API integrations between services
- Need scheduled/triggered automation
- Building notification pipelines
- AI-powered workflow automation

## When NOT to Use
- Simple API calls (use WAT tools directly)
- No trigger/automation needed (just code it)
- One-time data transformation (use Python tool)

## Prerequisites
- GSD project initialized
- n8n-mcp MCP server connected
- n8n API credentials in `.env`

## Process

### Step 1: Identify n8n Task in GSD Plan
During `/gsd:plan-phase`, when a task requires automation:

```xml
<task type="n8n">
  <name>Create Slack notification workflow</name>
  <trigger>Webhook from monitoring service</trigger>
  <action>Transform payload, send to Slack channel</action>
  <verify>POST to webhook triggers Slack message</verify>
</task>
```

### Step 2: Build n8n Workflow
Follow `workflows/create_n8n_workflow.md`:

1. **Template First**
   ```
   search_templates({searchMode: 'by_task', task: 'slack notification webhook'})
   ```

2. **Build or Adapt**
   - Use template if found
   - Otherwise build from nodes

3. **Validate**
   ```
   validate_workflow(workflow)
   ```

4. **Deploy**
   ```
   n8n_create_workflow(workflow)
   ```

### Step 3: Record in GSD
Update the task plan with workflow details:

```markdown
## Task: Slack Notification Workflow

**n8n Workflow ID:** wf-abc123
**Webhook URL:** https://seme.app.n8n.cloud/webhook/monitoring-slack
**Status:** Active

### Verification
- [x] Webhook receives POST
- [x] Payload transformed correctly
- [x] Slack message sent to #alerts
```

### Step 4: Test via GSD Verification
```bash
# Test the webhook
curl -X POST https://seme.app.n8n.cloud/webhook/monitoring-slack \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "message": "GSD verification"}'
```

### Step 5: Update GSD State
In `.planning/STATE.md`:

```markdown
## Active n8n Workflows

| Phase | Task | Workflow ID | Status |
|-------|------|-------------|--------|
| 3 | Slack notifications | wf-abc123 | Active |
| 3 | Daily report | wf-def456 | Active |
```

### Step 6: Complete Phase
When phase complete:
```
/gsd:verify-work N
```

Include n8n workflow verification in UAT checklist.

## n8n + GSD Patterns

### Pattern 1: Progress Notifications
Send GSD phase progress to external channels:
```
GSD Execute → Webhook → n8n → Slack/Email/Telegram
```

### Pattern 2: Triggered Automation
External events trigger GSD-tracked workflows:
```
External Service → n8n Webhook → Transform → Action
(Tracked in GSD STATE.md)
```

### Pattern 3: Scheduled Reports
Cron-triggered data aggregation:
```
Schedule Trigger → Fetch Data → Transform → Report
(Tracked as GSD recurring task)
```

## Expected Outputs
- n8n workflow deployed and active
- Workflow ID recorded in GSD plan/state
- Verification tests passing
- STATE.md updated with workflow status

## Error Handling
- **Workflow fails validation**: Use `n8n_autofix_workflow`
- **Webhook not responding**: Check n8n execution logs
- **Need to update**: Use `n8n_update_partial_workflow`
- **Rollback needed**: Use `n8n_workflow_versions`

## Notes
- Always validate before deploying
- Never trust default parameters
- Test webhooks before marking task complete
- Keep workflow IDs in STATE.md for reference
