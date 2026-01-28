# Architecture Overview

MyWork Framework is a layered system that routes different types of development
tasks to the appropriate tool or engine.

## System Diagram

```mermaid

graph TB

```
subgraph "User Interface"
    CLI[Claude Code CLI]
    MW[mw.py CLI]
end

subgraph "Master Orchestrator"
    CLAUDE[CLAUDE.md<br/>Decision routing]
end

subgraph "Layer 1: GSD"
    direction TB
    GSD_NEW[new-project]
    GSD_PLAN[plan-phase]
    GSD_EXEC[execute-phase]
    GSD_VERIFY[verify-work]
    GSD_NEW --> GSD_PLAN --> GSD_EXEC --> GSD_VERIFY
end

subgraph "Layer 2: WAT"
    WORKFLOWS[Workflows<br/>SOPs in markdown]
    TOOLS[Tools<br/>Python scripts]
    WORKFLOWS --> TOOLS
end

subgraph "Layer 3: Engines"
    AUTOCODER[Autocoder<br/>Autonomous coding]
    N8N[n8n<br/>Workflow automation]
end

subgraph "Self-Learning"
    BRAIN[Brain<br/>Knowledge vault]
    REGISTRY[Module Registry<br/>Code patterns]
end

CLI --> CLAUDE
MW --> CLAUDE
CLAUDE --> GSD_NEW
CLAUDE --> WORKFLOWS
CLAUDE --> AUTOCODER
CLAUDE --> N8N
GSD_VERIFY --> BRAIN
TOOLS --> REGISTRY

style CLAUDE fill:#4A90D9,stroke:#333,color:#fff
style BRAIN fill:#34A853,stroke:#333,color:#fff
style AUTOCODER fill:#EA4335,stroke:#333,color:#fff
style N8N fill:#EA4B71,stroke:#333,color:#fff

```
```markdown

## Layer Details

### Layer 1: GSD (Get Shit Done)

**Purpose:** Project lifecycle management with phased execution.

**Components:**

- `/gsd:new-project` - Discovery, research, roadmap creation
- `/gsd:plan-phase N` - Detailed task planning for a phase
- `/gsd:execute-phase N` - Parallel execution with atomic commits
- `/gsd:verify-work` - User acceptance testing

**State Files:**

- `.planning/PROJECT.md` - Vision and scope
- `.planning/ROADMAP.md` - Phases and progress
- `.planning/STATE.md` - Current context

### Layer 2: WAT (Workflows, Agents, Tools)

**Purpose:** Deterministic task execution with clear separation of concerns.

**Components:**

- **Workflows** (`workflows/`) - Markdown SOPs defining procedures
- **Agents** - Claude acting as decision-maker
- **Tools** (`tools/`) - Python scripts for execution

**Philosophy:** AI handles reasoning, scripts handle execution. This prevents
accuracy degradation over multi-step processes.

### Layer 3: Automation Engines

**Autocoder:**

- Long-running autonomous coding
- Multi-session persistence
- Best for 20+ feature projects
- Server: `http://127.0.0.1:8889`

**n8n:**

- Visual workflow automation
- 2,709 templates available
- Webhook processing, API integrations
- MCP integration via n8n-mcp

### Self-Learning System

**Brain (Knowledge Vault):**

- Captures lessons learned
- Patterns that work, anti-patterns to avoid
- Auto-learning from completed phases
- File: `.planning/BRAIN.md`

**Module Registry:**

- Indexes reusable code patterns
- 1,300+ modules across projects
- Searchable by keyword or type
- File: `.planning/module_registry.json`

## Decision Flow

```mermaid

flowchart TD

```
A[Request] --> B{Type?}

B -->|New Project| C[GSD]
B -->|Quick Fix| D[GSD Quick]
B -->|Large Feature| E{20+ features?}
B -->|Automation| F[n8n]

E -->|Yes| G[Autocoder]
E -->|No| C

C --> H[Plan → Execute → Verify]
D --> I[Quick task with guarantees]
G --> J[Multi-session coding]
F --> K[Visual workflow]

H --> L[Brain learns]
I --> L
J --> L
K --> L

```

```

## Data Flow

```python
User Request

```
 │
 ▼

```
┌─────────────┐
│   CLAUDE.md │ ← Routes to appropriate layer
└─────────────┘

```
 │
 ├─────────────────┬─────────────────┐
 ▼                 ▼                 ▼

```
┌─────────┐      ┌─────────┐      ┌─────────┐
│   GSD   │      │   WAT   │      │ Engines │
└─────────┘      └─────────┘      └─────────┘

```
 │                 │                 │
 ▼                 ▼                 ▼

```
┌─────────┐      ┌─────────┐      ┌─────────┐
│.planning│      │ tools/  │      │ Project │
│  STATE  │      │ output  │      │  code   │
└─────────┘      └─────────┘      └─────────┘

```
 │                 │                 │
 └────────────────┬┴─────────────────┘
                  ▼
          ┌─────────────┐
          │    Brain    │ ← Learns from all
          └─────────────┘

```

```

## Key Principles

1. **Separation of Concerns** - Reasoning in AI, execution in scripts
2. **Deterministic Tools** - Python scripts for reliable, testable operations
3. **State Preservation** - `.planning/` tracks everything across sessions
4. **Self-Improvement** - Brain learns from every completed task
5. **Parallel Execution** - GSD runs independent tasks concurrently
