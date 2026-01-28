# Python Tools API Reference

Complete Python API reference for MyWork framework tools. All tools are located
in the `tools/` directory and can be imported or executed directly.

## 📚 Tool Categories

### 🧠 Intelligence & Learning

| Tool | Purpose | Key Functions |
| ------ | --------- | --------------- |
  | `brain.py` | Knowledge vault ma... | `search()`, `add_k... |  
  | `brain_learner.py` | Automatic pattern ... | `analyze_commits()... |  
  | `module_registry.py` | Code module indexing | `scan_projects()`,... |  

### 🔧 System Management

| Tool | Purpose | Key Functions |
| ------ | --------- | --------------- |
| `mw.py` | Unified CLI interface | `main()`, `route_command()` |
| `health_check.py` | System diagnostics | `check_all()`, `fix_issues()` |
  | `auto_update.py` | Framework updates | `check_updates()`,... |  

### 🚀 Project & Automation

| Tool | Purpose | Key Functions |
| ------ | --------- | --------------- |
| `scaffold.py` | Project creation | `create_project()`, `apply_template()` |
| `autocoder_api.py` | Autocoder control | `start_project()`, `get_progress()` |
  | `n8n_api.py` | n8n workflow manag... | `create_workflow()... |  

### ⚙️ Configuration & Utilities

| Tool | Purpose | Key Functions |
| ------ | --------- | --------------- |
  | `config_manager.py` | Configuration hand... | `load_config()`, `... |  
| `git_utils.py` | Git operations | `commit_changes()`, `create_branch()` |
| `file_utils.py` | File system operations | `copy_template()`, `safe_write()` |

## 🎯 Quick Examples

### Search Knowledge Brain

```python
from tools.brain import search_knowledge, add_pattern

# Search for patterns

results = search_knowledge("authentication patterns")
for pattern in results:

```
print(f"📋 {pattern.title}: {pattern.description}")

```
# Add new knowledge

add_pattern(

```
title="JWT Best Practice",
description="Always validate tokens server-side",
pattern_type="security",
confidence=0.95

```
)

```markdown

### Create New Project

```python
from tools.scaffold import create_project

# Create project from template

project = create_project(

```
name="my-api",
template="fastapi",
path="./projects",
gsd_enabled=True,
autocoder_ready=True

```
)

print(f"✅ Created {project.path}")

```

### Check System Health

```python
from tools.health_check import run_diagnostics, fix_issues

# Run full diagnostic

results = run_diagnostics()

for check in results.checks:

```
status = "✅" if check.passed else "❌"
print(f"{status} {check.name}: {check.message}")

```
# Auto-fix issues

if results.has_errors:

```
fix_results = fix_issues(results.errors)
print(f"🔧 Fixed {fix_results.fixed_count} issues")

```
```markdown

### Control Autocoder

```python
from tools.autocoder_api import AutocoderClient

# Initialize client

client = AutocoderClient("http://127.0.0.1:8888")

# Start autonomous coding

session = client.start_project(

```
project_name="my-app",
concurrency=3,
model="claude-opus-4-5-20251101"

```
)

# Monitor progress

while not session.is_complete():

```
progress = client.get_progress(session.id)
print(f"Progress: {progress.percentage}% - {progress.current_task}")
time.sleep(30)

```

```

## 📖 Common Patterns

### Error Handling

```python
from tools.exceptions import MyWorkError, ProjectNotFoundError

try:

```
result = some_framework_operation()

```
except ProjectNotFoundError as e:

```
print(f"❌ Project error: {e.message}")

# Handle missing project

```
except MyWorkError as e:

```
print(f"⚠️ Framework error: {e.message}")

# Handle framework-specific issues

```
except Exception as e:

```
print(f"🔥 Unexpected error: {e}")

# Handle unexpected issues

```
```markdown

### Configuration Management

```python
from tools.config_manager import load_project_config, get_framework_setting

# Load project-specific configuration

config = load_project_config("./projects/my-app")
print(f"GSD mode: {config.gsd.mode}")
print(f"Autocoder enabled: {config.autocoder.enabled}")

# Get framework-wide settings

brain_enabled = get_framework_setting("brain.auto_learning", default=True)
update_check = get_framework_setting("updates.auto_check", default=False)

```

### Logging & Output

```python
import tools.logger as log

# Standard logging

log.info("Starting project creation...")
log.success("✅ Project created successfully!")
log.warning("⚠️ Template outdated, using fallback")
log.error("❌ Failed to initialize GSD")

# Progress indicators

with log.progress("Scanning modules...") as progress:

```
for i, module in enumerate(modules):
    progress.update(f"Processing {module.name}")

    # Do work

    progress.advance()

```
# Rich output formatting

log.table("Project Status", [

```
["Name", "Status", "Progress"],
["my-app", "Building", "73%"],
["api-server", "Complete", "100%"]

```
])

```markdown

## 🔧 Tool Initialization

### Framework Setup

```python
import os
import sys

# Add tools to path

sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))

# Initialize framework

from tools.framework import initialize_framework

framework = initialize_framework(

```
root_path=os.getcwd(),
auto_update=True,
brain_learning=True

```
)

print(f"🚀 Framework initialized: {framework.version}")

```

### Environment Variables

```python
import os
from tools.config_manager import validate_environment

# Required environment variables

required_vars = [

```
'MYWORK_ROOT',        # Framework root directory
'ANTHROPIC_API_KEY',  # For AI operations
'GITHUB_TOKEN',       # For git operations

```
]

# Optional environment variables

optional_vars = {

```
'OPENAI_API_KEY': 'Alternative AI provider',
'VERCEL_TOKEN': 'For deployment operations',
'N8N_API_KEY': 'For n8n workflow management'

```
}

# Validate environment

env_status = validate_environment(required_vars, optional_vars)
if not env_status.is_valid:

```
print(f"❌ Missing: {', '.join(env_status.missing_required)}")
sys.exit(1)

```
print("✅ Environment validated")

```markdown

## 📊 Data Models

All tools use consistent data models for type safety and clarity:

```python
from tools.models import (

```
Project, ProjectConfig, ProjectStatus,
KnowledgePattern, BrainEntry,
HealthCheck, DiagnosticResult,
AutocoderSession, ProgressUpdate

```
)

# Project data

project = Project(

```
name="my-app",
path="./projects/my-app",
template="fastapi",
config=ProjectConfig(
    gsd_enabled=True,
    autocoder_ready=True,
    brain_learning=True
),
status=ProjectStatus.ACTIVE

```
)

# Knowledge pattern

pattern = KnowledgePattern(

```
title="FastAPI Auth Middleware",
description="JWT validation with session fallback",
pattern_type="security",
code_snippet="@app.middleware('http')\nasync def auth_middleware...",
confidence=0.95,
usage_count=5,
success_rate=1.0

```
)

```

## 🧪 Testing

### Unit Testing

```python
import unittest
from tools.brain import search_knowledge
from tools.test_utils import mock_knowledge_base

class TestBrainSearch(unittest.TestCase):

```
def setUp(self):
    self.mock_brain = mock_knowledge_base([
        {"title": "Auth Pattern", "type": "security"},
        {"title": "React Hook", "type": "frontend"}
    ])

def test_search_by_type(self):
    results = search_knowledge("auth", pattern_type="security")
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0].title, "Auth Pattern")

```
if __name__ == '__main__':

```
unittest.main()

```
```markdown

### Integration Testing

```python
from tools.integration_test import IntegrationTest

class TestProjectCreation(IntegrationTest):

```
def test_full_project_lifecycle(self):

    # Create project

    project = self.create_test_project("test-app", "fastapi")
    self.assertTrue(project.exists())

    # Initialize GSD

    gsd_result = self.run_gsd_init(project)
    self.assertTrue(gsd_result.success)

    # Verify structure

    self.assert_project_structure(project, "fastapi")

    # Cleanup

    self.cleanup_project(project)

```

```

## 🔗 Integration Points

### With GSD Skills

```python
from tools.gsd_integration import execute_gsd_command

# Execute GSD commands programmatically

result = execute_gsd_command(

```
skill="gsd:plan-phase",
args="3",
project_path="./projects/my-app"

```
)

if result.success:

```
print(f"✅ Phase 3 planned: {result.plans_created} plans")

```
else:

```
print(f"❌ Planning failed: {result.error}")

```
```markdown

### With n8n Workflows

```python
from tools.n8n_integration import create_workflow_from_template

# Create n8n workflow

workflow = create_workflow_from_template(

```
template_id=1234,  # From n8n.io
name="GitHub Webhook Handler",
environment_vars={
    "WEBHOOK_SECRET": "example-secret",
    "GITHUB_TOKEN": "github_token_example"
}

```
)

print(f"🔗 Workflow created: {workflow.url}")

```

## 📚 Advanced Usage

### Custom Tool Development

```python
from tools.base import BaseTool
from tools.decorators import requires_project, logs_execution

class CustomTool(BaseTool):

```
"""Custom tool for specialized operations."""

@requires_project
@logs_execution
def custom_operation(self, project_path: str, options: dict):
    """Perform custom operation on project."""

    # Load project

    project = self.load_project(project_path)

    # Validate options

    self.validate_options(options, required=['param1'])

    # Perform work

    result = self.do_work(project, options)

    # Update brain if successful

    if result.success:
        self.brain.add_pattern(
            title=f"Custom operation on {project.name}",
            pattern=result.pattern,
            confidence=0.8
        )

    return result

```
# Usage

tool = CustomTool()
result = tool.custom_operation("./projects/my-app", {"param1": "value"})

```markdown

---

## 📖 Individual Tool Documentation

Tool entrypoints inside `tools/`:

### Intelligence & Learning

- 🧠 `brain.py` - Knowledge vault and pattern management
- 📖 `brain_learner.py` - Automatic learning from projects
- 📊 `module_registry.py` - Code module indexing and search

### System Management

- ⚡ `mw.py` - Unified command-line interface
- 🔧 `health_check.py` - System diagnostics and repair
- 🔄 `auto_update.py` - Framework component updates

### Project & Automation

- 🏗️ `scaffold.py` - Project creation and templating
- 🤖 `autocoder_api.py` - Autonomous coding control
- 🔗 `n8n_api.py` - Visual workflow automation

### Configuration & Utilities

- ⚙️ `config_manager.py` - Configuration management
- 📂 `git_utils.py` - Git operation utilities
- 📁 `file_utils.py` - File system helpers

---

*💡 **Pro Tip:** All tools support `--help` flag when used from command line, and
include detailed docstrings for Python usage.*
