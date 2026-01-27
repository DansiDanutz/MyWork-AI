# MyWork Framework - Architecture Overview

## 🏗️ System Architecture

MyWork is built on a 3-layer architecture that separates concerns and enables powerful AI-driven development:

```mermaid
graph TB
    subgraph "🧠 USER LAYER"
        USER[👨‍💻 Developer]
        IDEA[💡 Project Idea]
    end

    subgraph "📋 LAYER 1: GSD (Get Shit Done)"
        GSD_NEW[🆕 /gsd:new-project]
        GSD_PLAN[📝 /gsd:plan-phase]
        GSD_EXEC[⚡ /gsd:execute-phase]
        GSD_VERIFY[✅ /gsd:verify-work]

        GSD_NEW --> GSD_PLAN --> GSD_EXEC --> GSD_VERIFY
    end

    subgraph "🔄 LAYER 2: WAT (Workflows/Agents/Tools)"
        subgraph "2A: Workflows"
            WAT_WORKFLOWS[📄 Markdown SOPs<br/>• create_n8n_workflow.md<br/>• use_autocoder.md<br/>• session_handoff.md]
        end

        subgraph "2B: Agents"
            WAT_AGENTS[🤖 AI Decision-Makers<br/>• Read workflows<br/>• Execute tools<br/>• Handle failures]
        end

        subgraph "2C: Tools"
            WAT_TOOLS[🛠️ Python Scripts<br/>• mw.py (unified CLI)<br/>• brain.py<br/>• health_check.py<br/>• autocoder_api.py]
        end
    end

    subgraph "🚀 LAYER 3: AUTOMATION ENGINES"
        AUTOCODER[🤖 Autocoder<br/>Long-running<br/>autonomous coding]
        N8N[🔗 n8n Workflows<br/>Visual automation<br/>2,709 templates]
        INTEGRATIONS[🔌 Integrations<br/>GitHub, Vercel<br/>Various APIs]
    end

    subgraph "🧠 INTELLIGENCE LAYER"
        BRAIN[🧠 Brain<br/>Knowledge vault<br/>Auto-learning]
        REGISTRY[📊 Module Registry<br/>Code indexing<br/>Reusable patterns]
        ANALYTICS[📈 Analytics<br/>Usage tracking<br/>Pattern analysis]
    end

    %% User Flow
    USER --> IDEA
    IDEA --> GSD_NEW

    %% GSD to WAT
    GSD_PLAN --> WAT_WORKFLOWS
    GSD_EXEC --> WAT_AGENTS
    WAT_AGENTS --> WAT_TOOLS

    %% WAT to Automation
    WAT_TOOLS --> AUTOCODER
    WAT_TOOLS --> N8N
    WAT_TOOLS --> INTEGRATIONS

    %% Intelligence Layer Connections
    WAT_TOOLS <--> BRAIN
    WAT_TOOLS <--> REGISTRY
    GSD_EXEC --> ANALYTICS
    AUTOCODER --> ANALYTICS
    N8N --> ANALYTICS

    %% Feedback Loop
    ANALYTICS --> BRAIN
    BRAIN --> WAT_WORKFLOWS
    REGISTRY --> WAT_TOOLS

    classDef userLayer fill:#e1f5fe
    classDef gsdLayer fill:#f3e5f5
    classDef watLayer fill:#e8f5e8
    classDef autoLayer fill:#fff3e0
    classDef intLayer fill:#fce4ec

    class USER,IDEA userLayer
    class GSD_NEW,GSD_PLAN,GSD_EXEC,GSD_VERIFY gsdLayer
    class WAT_WORKFLOWS,WAT_AGENTS,WAT_TOOLS watLayer
    class AUTOCODER,N8N,INTEGRATIONS autoLayer
    class BRAIN,REGISTRY,ANALYTICS intLayer
```

## 🔄 Data Flow & Decision Tree

```mermaid
flowchart TD
    START[🎯 User Request] --> ANALYZE{📊 Analyze Request}

    ANALYZE -->|New Project| NEW_PROJECT[🆕 /gsd:new-project<br/>Research → Requirements → Roadmap]
    ANALYZE -->|Phase Work| PHASE_WORK[📋 /gsd:plan-phase → /gsd:execute-phase]
    ANALYZE -->|Quick Task| QUICK_TASK[⚡ /gsd:quick OR WAT workflow]
    ANALYZE -->|Long Coding| LONG_CODING[🤖 Autocoder with GSD tracking]
    ANALYZE -->|Automation| AUTOMATION[🔗 n8n workflow creation]

    NEW_PROJECT --> PLANNING[📝 Planning Phase]
    PHASE_WORK --> PLANNING

    PLANNING --> EXECUTION{🔄 Execution Strategy}

    EXECUTION -->|< 20 features| GSD_EXECUTION[📋 GSD Phase-by-phase]
    EXECUTION -->|20+ features| AUTOCODER_EXECUTION[🤖 Autocoder autonomous]
    EXECUTION -->|Webhooks/APIs| N8N_EXECUTION[🔗 n8n visual workflows]

    GSD_EXECUTION --> VERIFY[✅ Verify Work]
    AUTOCODER_EXECUTION --> MONITOR[📊 Monitor Progress]
    N8N_EXECUTION --> TEST[🧪 Test Workflow]

    VERIFY --> LEARN[🧠 Brain Learning]
    MONITOR --> LEARN
    TEST --> LEARN

    LEARN --> REGISTRY[📊 Update Module Registry]
    LEARN --> PATTERNS[🔍 Extract Patterns]

    PATTERNS --> IMPROVE[⚡ Improve Framework]
    REGISTRY --> REUSE[♻️ Enable Code Reuse]

    IMPROVE --> START
    REUSE --> START

    classDef start fill:#e1f5fe
    classDef process fill:#f3e5f5
    classDef execution fill:#e8f5e8
    classDef intelligence fill:#fce4ec

    class START start
    class ANALYZE,PLANNING,EXECUTION process
    class GSD_EXECUTION,AUTOCODER_EXECUTION,N8N_EXECUTION execution
    class LEARN,REGISTRY,PATTERNS,IMPROVE intelligence
```

## 🧩 Component Interaction

```mermaid
sequenceDiagram
    participant U as 👨‍💻 User
    participant G as 📋 GSD
    participant W as 🔄 WAT
    participant A as 🤖 Autocoder
    participant N as 🔗 n8n
    participant B as 🧠 Brain
    participant R as 📊 Registry

    Note over U,R: Project Creation Flow

    U->>G: /gsd:new-project "AI Dashboard"
    G->>W: Spawn researchers (4 parallel)
    W->>B: Search existing patterns
    B-->>W: Return relevant knowledge
    W->>G: Research complete
    G->>G: Generate requirements & roadmap
    G->>U: Present plan for approval

    Note over U,R: Phase Execution Flow

    U->>G: /gsd:execute-phase 3
    G->>W: Spawn executor agents (parallel waves)
    W->>A: Hand off to Autocoder (if 20+ features)
    W->>N: Create workflows (if automation needed)

    par Autocoder Work
        A->>A: Generate code autonomously
        A->>B: Log patterns and decisions
    and n8n Work
        N->>N: Process webhooks/APIs
        N->>B: Track usage patterns
    and WAT Work
        W->>W: Execute deterministic tasks
        W->>R: Index new modules
    end

    Note over U,R: Learning & Improvement

    A->>B: "FastAPI + Auth pattern works"
    N->>B: "Webhook validation template effective"
    W->>B: "Auto-save with 3s debounce optimal"

    B->>B: Synthesize learnings
    B->>R: Update module recommendations
    B->>W: Improve future workflows

    R->>U: Suggest reusable code for new projects
```

## 🎯 User Journey Map

```mermaid
journey
    title MyWork Framework User Journey
    section Discovery
      Finds framework: 3: User
      Reads README: 4: User
      Watches demo video: 5: User
    section Onboarding
      Runs quick start: 5: User
      Creates first project: 4: User, Framework
      Completes tutorial: 5: User, Framework
    section Regular Use
      Plans new features: 5: User, GSD
      Executes phases: 4: User, WAT, Autocoder
      Reviews generated code: 4: User, Framework
      Deploys to production: 5: User, Framework
    section Mastery
      Contributes patterns: 5: User, Brain
      Creates workflows: 4: User, WAT
      Mentors new users: 5: User, Community
    section Framework Growth
      Framework learns patterns: 5: Brain
      Suggests improvements: 4: Registry
      Accelerates development: 5: All Components
```

## 🏛️ Architecture Principles

### 1. **Separation of Concerns**
- **GSD**: What to build (orchestration, planning)
- **WAT**: How to build it (execution, tools)
- **Automation**: Scale the building (AI agents, workflows)

### 2. **Progressive Enhancement**
- Start simple (GSD phases)
- Add automation when beneficial (Autocoder for 20+ features)
- Scale with visual tools (n8n for complex integrations)

### 3. **Continuous Learning**
- **Brain** captures what works
- **Registry** indexes reusable code
- **Analytics** measures effectiveness

### 4. **Human-AI Collaboration**
- AI handles repetitive tasks
- Human provides direction and judgment
- Clear handoff points between human and AI work

### 5. **Modularity & Reuse**
- Everything is a reusable module
- Clear interfaces between components
- Plugin architecture for extensions

## 🔧 Technical Stack

| Layer | Technologies | Purpose |
|-------|-------------|---------|
| **Orchestration** | Python, Bash, Markdown | GSD workflow management |
| **Execution** | Python tools, AI agents | Task automation |
| **Code Generation** | Autocoder, OpenAI API | Autonomous coding |
| **Workflow Automation** | n8n, JavaScript, APIs | Visual automation |
| **Data Storage** | SQLite, JSON, Markdown | State and knowledge |
| **Intelligence** | Vector embeddings, Analytics | Learning and patterns |
| **Deployment** | Vercel, GitHub Actions | Production deployment |

## 📊 Performance Characteristics

- **Project Setup**: 2-5 minutes (vs 30-60 min manual)
- **Feature Development**: 60-80% faster than manual coding
- **Code Quality**: Consistent patterns, auto-testing
- **Learning Curve**: 1-2 days to productivity
- **Maintenance**: Self-healing and auto-updating

---

*Next: [Quickstart →](../quickstart.md) | [Tutorials →](../tutorials/index.md) | [CLI Reference →](../api/mw-cli.md)*
