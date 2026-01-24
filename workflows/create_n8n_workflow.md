# Workflow: Create n8n Workflow

## Objective
Design and deploy a production-ready n8n workflow using the n8n-mcp MCP server tools.

## Required Inputs
- **workflow_purpose**: What the workflow should accomplish
- **trigger_type**: webhook | schedule | manual | event
- **integrations_needed**: List of services/nodes required

## Prerequisites
- n8n-mcp MCP server configured and running
- n8n-skills installed (`/plugin install czlonkowski/n8n-skills`)
- N8N_API_URL and N8N_API_KEY set in environment

## Tools Used
- `search_templates` - Find existing templates first
- `get_template` - Get template details
- `search_nodes` - Discover available nodes
- `get_node` - Get node configuration details
- `validate_node` - Validate node configuration
- `validate_workflow` - Validate complete workflow
- `n8n_create_workflow` - Deploy workflow
- `n8n_update_partial_workflow` - Make incremental updates
- `n8n_validate_workflow` - Post-deployment validation
- `n8n_autofix_workflow` - Auto-fix common issues

## Steps

### Phase 1: Template Discovery (ALWAYS FIRST)

1. **Search for existing templates**
   ```
   search_templates({searchMode: 'by_task', task: 'your_task_here'})
   search_templates({searchMode: 'by_metadata', complexity: 'simple'})
   search_templates({searchMode: 'by_nodes', nodeTypes: ['required-node-type']})
   ```

2. **If template found**
   ```
   get_template(templateId, {mode: 'full'})
   ```
   - Adapt template to requirements
   - Skip to Phase 3 (Validation)

3. **If no template found**
   - Proceed to Phase 2

### Phase 2: Node Discovery & Configuration

1. **Search for required nodes** (execute in parallel)
   ```
   search_nodes({query: 'node_type_1', includeExamples: true})
   search_nodes({query: 'node_type_2', includeExamples: true})
   ```

2. **Get node details** (execute in parallel)
   ```
   get_node({nodeType: 'type1', detail: 'standard', includeExamples: true})
   get_node({nodeType: 'type2', detail: 'standard', includeExamples: true})
   ```

3. **Build node configurations**
   - ALWAYS set ALL parameters explicitly
   - NEVER rely on default values
   - Use examples from get_node response

### Phase 3: Validation

1. **Validate individual nodes** (minimal check first)
   ```
   validate_node({nodeType: 'type', config: {...}, mode: 'minimal'})
   ```

2. **Full validation with runtime profile**
   ```
   validate_node({nodeType: 'type', config: {...}, mode: 'full', profile: 'runtime'})
   ```

3. **Fix ALL errors before proceeding**

### Phase 4: Build Workflow

1. **Assemble workflow structure**
   - Create nodes array with validated configs
   - Map connections between nodes
   - Add error handling paths

2. **Validate complete workflow**
   ```
   validate_workflow(workflow)
   validate_workflow_connections(workflow)
   validate_workflow_expressions(workflow)
   ```

### Phase 5: Deploy

1. **Create workflow**
   ```
   n8n_create_workflow(workflow)
   ```

2. **Post-deployment validation**
   ```
   n8n_validate_workflow({id: workflowId})
   ```

3. **Auto-fix if needed**
   ```
   n8n_autofix_workflow({id: workflowId})
   ```

4. **Activate workflow**
   ```
   n8n_update_partial_workflow({
     id: workflowId,
     operations: [{type: 'activateWorkflow'}]
   })
   ```

### Phase 6: Test

1. **Test execution**
   ```
   n8n_test_workflow({workflowId})
   ```

2. **Check execution status**
   ```
   n8n_executions({action: 'list', workflowId: workflowId})
   ```

## Expected Outputs
- Workflow deployed and active in n8n
- Workflow ID for future reference
- Test execution successful

## Critical Rules

1. **Templates First** - Always search 2,709 templates before building from scratch
2. **Never Trust Defaults** - Explicitly set ALL parameters
3. **Parallel Execution** - Run independent operations simultaneously
4. **Silent Execution** - Execute tools without commentary, respond after completion
5. **Multi-Level Validation** - minimal → full → workflow

## Edge Cases

- **Missing credentials**: Check n8n credentials exist before referencing
- **Rate limits**: Add Wait nodes between external API calls
- **Large data**: Use Split In Batches for processing many items
- **IF node routing**: Use `branch: "true"` or `branch: "false"` in connections
- **Webhook data access**: Data is under `$json.body`, not `$json`

## Connection Syntax Reference

```json
// Standard connection
{
  "type": "addConnection",
  "source": "source-node-id",
  "target": "target-node-id",
  "sourcePort": "main",
  "targetPort": "main"
}

// IF node TRUE branch
{
  "type": "addConnection",
  "source": "if-node-id",
  "target": "success-handler",
  "sourcePort": "main",
  "targetPort": "main",
  "branch": "true"
}

// IF node FALSE branch
{
  "type": "addConnection",
  "source": "if-node-id",
  "target": "failure-handler",
  "sourcePort": "main",
  "targetPort": "main",
  "branch": "false"
}
```

## Notes
- The n8n-mcp server provides access to 1,084 nodes and 2,709 templates
- n8n-skills activate automatically to provide expert guidance
- Always make a copy of production workflows before AI editing
- Test in development environment first
