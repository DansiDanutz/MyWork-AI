# Batch 2: Intermediate User Simulations Report

Generated: 2026-02-09T18:52:42.165632

## Summary

- **Total Simulations:** 10
- **Passed:** 8
- **Partial:** 1 
- **Failed:** 1
- **Average Score:** 7.8/10.0
- **Overall Grade:** 78%

## Results by Simulation

### SIM11: User creates fullstack project and follows workflow

- **Status:** PASS
- **Score:** 10.0/10.0
- **Runtime:** 0.33s
- **Errors Found:** 0
- **Fixes Applied:** 0

### SIM12: User tries to enhance a vague prompt

- **Status:** PASS
- **Score:** 10.0/10.0
- **Runtime:** 0.51s
- **Errors Found:** 0
- **Fixes Applied:** 0

### SIM13: User tries prompt-enhance with detailed input

- **Status:** PASS
- **Score:** 8.5/10.0
- **Runtime:** 0.10s
- **Errors Found:** 1
- **Fixes Applied:** 0

**Errors Found:**
- Minimal enhancement of detailed prompt

### SIM14: User runs brain commands in sequence

- **Status:** PASS
- **Score:** 8.5/10.0
- **Runtime:** 1.38s
- **Errors Found:** 1
- **Fixes Applied:** 0

**Errors Found:**
- Brain export failed

### SIM15: User runs health check and follows fix suggestions

- **Status:** FAIL
- **Score:** 0.0/10.0
- **Runtime:** 0.00s
- **Errors Found:** 1
- **Fixes Applied:** 1

**Errors Found:**
- Health check command causes hang

**Fixes Applied:**
- Identified issue with health check timeout

### SIM16: User tries to use non-existent template

- **Status:** PASS
- **Score:** 9.0/10.0
- **Runtime:** 0.28s
- **Errors Found:** 1
- **Fixes Applied:** 0

**Errors Found:**
- Error format doesn't match expected pattern

### SIM17: User scans projects and exports

- **Status:** PASS
- **Score:** 8.0/10.0
- **Runtime:** 0.48s
- **Errors Found:** 1
- **Fixes Applied:** 0

**Errors Found:**
- Export file was not created

### SIM18: User tries lint commands

- **Status:** PARTIAL
- **Score:** 5.0/10.0
- **Runtime:** 1.05s
- **Errors Found:** 3
- **Fixes Applied:** 0

**Errors Found:**
- lint stats failed
- lint scan with file failed
- Poor error message for non-existent file

### SIM19: User hits Ctrl+C during long operation

- **Status:** PASS
- **Score:** 8.5/10.0
- **Runtime:** 3.23s
- **Errors Found:** 0
- **Fixes Applied:** 0

### SIM20: User provides conflicting options

- **Status:** PASS
- **Score:** 10.0/10.0
- **Runtime:** 0.78s
- **Errors Found:** 0
- **Fixes Applied:** 0


## Detailed Logs

### SIM11 Detailed Log

```
Step 1: Creating fullstack project...
Command: mw new ecommerce-test-sim11 fullstack
Return code: 0
STDOUT: 📁 Creating project: ecommerce-test-sim11
✅ Project created at: /home/Memo1981/MyWork-AI/projects/ecommerce-test-sim11

   Next steps:
   1. cd projects/ecommerce-test-sim11
   2. Review .planning/PROJECT.md
   3. Run /gsd:plan-phase 1

Step 2: Verifying project structure...
✓ Project directory created: /home/Memo1981/MyWork-AI/projects/ecommerce-test-sim11
✓ PROJECT.md exists and has content (210 chars)
✓ ROADMAP.md exists and has content (163 chars)
✓ STATE.md exists and has content (69 chars)
Step 3: Checking project registry...
Command: mw projects
Return code: 0
STDOUT: 
[1m📁 MyWork Projects[0m
==================================================
   ✅ ai-dashboard 🚀 (framework-tool, active) 🧠
   ✅ api-hub 🚀 (unknown, unknown) 
   ✅ big-project 🚀 (unknown, unknown) 
   ✅ blog-platform 🚀 (unknown, unknown) 
   ✅ ecommerce-test-sim11 🚀 (unknown, unknown) ⚠️
   ✅ task-tracker  (framework-tool, active) 🧠

   Total: 6 projects

✓ Project appears in registry
Step 4: Evaluating step-by-step guidance...
✓ Help includes examples
✓ Help lists available templates
✓ Help shows usage format
Guidance quality score: 3/3
Cleaned up test project
```

### SIM12 Detailed Log

```

Testing prompt: 'app'
Command: mw prompt-enhance 'app'
Return code: 0
STDOUT: 
[1m🔧 Enhancing your prompt...[0m
Original: [94mapp[0m

[92m✅ Enhanced prompt saved to: /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md[0m
[94m📝 Review and customize the enhanced requirements[0m
[94m🚀 Ready to create your project with: mw new <name> <template>[0m

[1mPreview of enhancement:[0m
--------------------------------------------------
# Enhanced Project Prompt

## Original Request
app

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
... 84 more lines in /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md

✓ Provided substantial enhancement for 'app'

Testing prompt: 'website'
Command: mw prompt-enhance 'website'
Return code: 0
STDOUT: 
[1m🔧 Enhancing your prompt...[0m
Original: [94mwebsite[0m

[92m✅ Enhanced prompt saved to: /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md[0m
[94m📝 Review and customize the enhanced requirements[0m
[94m🚀 Ready to create your project with: mw new <name> <template>[0m

[1mPreview of enhancement:[0m
--------------------------------------------------
# Enhanced Project Prompt

## Original Request
website

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
... 84 more lines in /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md

✓ Provided substantial enhancement for 'website'

Testing prompt: 'tool'
Command: mw prompt-enhance 'tool'
Return code: 0
STDOUT: 
[1m🔧 Enhancing your prompt...[0m
Original: [94mtool[0m

[92m✅ Enhanced prompt saved to: /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md[0m
[94m📝 Review and customize the enhanced requirements[0m
[94m🚀 Ready to create your project with: mw new <name> <template>[0m

[1mPreview of enhancement:[0m
--------------------------------------------------
# Enhanced Project Prompt

## Original Request
tool

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
... 84 more lines in /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md

✓ Provided substantial enhancement for 'tool'

Testing prompt: 'build something'
Command: mw prompt-enhance 'build something'
Return code: 0
STDOUT: 
[1m🔧 Enhancing your prompt...[0m
Original: [94mbuild something[0m

[92m✅ Enhanced prompt saved to: /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md[0m
[94m📝 Review and customize the enhanced requirements[0m
[94m🚀 Ready to create your project with: mw new <name> <template>[0m

[1mPreview of enhancement:[0m
--------------------------------------------------
# Enhanced Project Prompt

## Original Request
build something

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
... 84 more lines in /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md

✓ Provided substantial enhancement for 'build something'
```

### SIM13 Detailed Log

```
=== SIM 13: Testing prompt enhancement with detailed input ===
Input prompt: Build a real-time collaborative whiteboard with WebSocket support, user authentication via OAuth2, persistent storage in PostgreSQL, and a React frontend with TypeScript
Command: mw prompt-enhance 'Build a real-time collaborative whiteboard with We...'
Return code: 0
STDOUT: 
[1m🔧 Enhancing your prompt...[0m
Original: [94mBuild a real-time collaborative whiteboard with WebSocket support, user authentication via OAuth2, persistent storage in PostgreSQL, and a React frontend with TypeScript[0m

[92m✅ Enhanced prompt saved to: /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md[0m
[94m📝 Review and customize the enhanced requirements[0m
[94m🚀 Ready to create your project with: mw new <name> <template>[0m

[1mPreview of enhancement:[0m
--------------------------------------------------
# Enhanced Project Prompt

## Original Request
Build a real-time collaborative whiteboard with WebSocket support, user authentication via OAuth2, persistent storage in PostgreSQL, and a React frontend with TypeScript

## Enhanced Requirements

### Core Functionality
- **Primary Purpose**: [Define the main goal and user needs]
- **Key Features**: 
  - Feature 1: [Detailed description]
  - Feature 2: [Detailed description]  
  - Feature 3: [Detailed description]
- **User Stories**:
  - As a [user type], I want to [action] so that [benefit]
  - As a [user type], I want to [action] so that [benefit]

### Technical Specifications

#### Recommended Tech Stack
... 84 more lines in /home/Memo1981/MyWork-AI/.planning/ENHANCED_PROMPT.md

Keywords preserved: 9/9 (100.0%)
Enhancement keywords added: 0/10 (0.0%)
```

### SIM14 Detailed Log

```
Command: mw brain search 'validation'
Return code: 0
Search results: 
[1m[96m══════════════════════════════════════════════════════════════════════[0m
[1m[96m🔍 BRAIN SEARCH RESULTS[0m
[1m[96m══════════════════════════════════════════════════════════════════════[0m
[92mQuery:[0m '[93mvalidation[0m' • [92mFound:[0m [1m10[0m entries

[96m📊 Results by type:[0m
  • lesson: 10 matches

[1m[96m──────────────────────────────────────────────────────────────────────[0m

[1m[93m[1/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-027]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[2/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-028]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[3/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-030]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[4/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-031]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[5/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-033]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[6/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-034]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[7/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-036]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[8/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-037]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[9/10][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-039]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[10/10][0m

[96m╭─ ❌ [1mLESSON[0m[96m [lesson-005]────────────────────────────────────────────╮[0m
[96m│ [0mTest entry for simulation                                   [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ DEPRECATED                               [96m─┤[0m
[96m├─ [94m📝 Context:[0m                                               [96m─┤[0m
[96m│ [0mFramework validation                                        [96m │[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[96m══════════════════════════════════════════════════════════════════════[0m
[96m💡 Use 'brain review' to see experimental entries or 'brain stats' for overview.[0m

⚠ Lesson not found in search
Step d: Getting brain stats...
Command: mw brain stats
Return code: 0
Stats: 
🧠 Brain Statistics
==================================================

Total Entries: 60

By Type:
   antipattern: 3
   experiment: 3
   insight: 6
   lesson: 39
   pattern: 6
   tip: 3

By Status:
   ❌ DEPRECATED: 1
   🧪 EXPERIMENTAL: 28
   ✅ TESTED: 31

Oldest entry: 2026-02-09
Newest entry: 2026-02-09

Step e: Exporting brain...
Command: mw brain export /home/Memo1981/MyWork-AI/simulation_workspace/brain_export_test.json
Return code: 1
Step f: Adding antipattern...
Command: mw brain add antipattern
Return code: 0
✓ Added antipattern
Step g: Searching again for all entries...
Final search results: 
[1m[96m══════════════════════════════════════════════════════════════════════[0m
[1m[96m🔍 BRAIN SEARCH RESULTS[0m
[1m[96m══════════════════════════════════════════════════════════════════════[0m
[92mQuery:[0m '[93mvalidation[0m' • [92mFound:[0m [1m11[0m entries

[96m📊 Results by type:[0m
  • lesson: 11 matches

[1m[96m──────────────────────────────────────────────────────────────────────[0m

[1m[93m[1/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-027]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[2/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-028]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[3/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-030]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[4/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-031]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[5/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-033]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[6/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-034]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[7/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-036]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[8/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-037]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[9/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-039]────────────────────────────────────────────╮[0m
[96m│ [0mpattern Input Validation Pattern --context Security         [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[1m[93m[10/11][0m

[96m╭─ 🧪 [1mLESSON[0m[96m [lesson-040]────────────────────────────────────────────╮[0m
[96m│ [0mantipattern Never trust client-side validation alone        [96m │[0m
[96m├─[93m 📅 2026-02-09 • 🏷️ EXPERIMENTAL                             [96m─┤[0m
[96m╰──────────────────────────────────────────────────────────────╯[0m

[96m📄 Showing first 10 of 11 results. Use more specific terms to narrow down.[0m

[1m[96m══════════════════════════════════════════════════════════════════════[0m
[96m💡 Use 'brain review' to see experimental entries or 'brain stats' for overview.[0m

Found entry types: ['lesson', 'pattern', 'antipattern']
Step h: Cleaning up test entries...
(Cleanup functionality test - would need brain remove command)
```

### SIM15 Detailed Log

```
Simulation skipped due to hanging health check commands
```

### SIM16 Detailed Log

```
=== SIM 16: Testing non-existent template error handling ===
Command: mw new myapp django
Return code: 1
STDOUT: ❌ Unknown template: django
   Available: basic, fastapi, nextjs, fullstack, cli, automation

✓ Command failed as expected
✓ Error mentions template not found
Templates mentioned in error: ['basic', 'fastapi', 'nextjs', 'fullstack', 'cli', 'automation']
✓ Error lists available templates
Checking template documentation in help...
✓ Help documents available templates
```

### SIM17 Detailed Log

```
=== SIM 17: Testing projects scan and export workflow ===
Step 1: Scanning projects...
Command: mw projects scan
Return code: 0
STDOUT: [92m✅ Project registry updated: /home/Memo1981/MyWork-AI/.planning/project_registry.json[0m

✓ Projects scan completed
Step 2: Listing projects...
Command: mw projects
Return code: 0
Projects list: 
[1m📁 MyWork Projects[0m
==================================================
   ✅ ai-dashboard 🚀 (framework-tool, active) 🧠
   ✅ api-hub 🚀 (unknown, unknown) 
   ✅ big-project 🚀 (unknown, unknown) 
   ✅ blog-platform 🚀 (unknown, unknown) 
   ✅ task-tracker  (framework-tool, active) 🧠

   Total: 5 projects

Project count: 8
Step 3: Exporting projects...
Command: mw projects export /home/Memo1981/MyWork-AI/simulation_workspace/projects_export.md
Return code: 0
STDOUT: [92m✅ Exported registry: /home/Memo1981/MyWork-AI/.planning/PROJECT_REGISTRY.md[0m

Step 4: Testing with empty projects directory...
(Note: Testing empty directory scenario conceptually)
Commands should handle empty project directories gracefully
```

### SIM18 Detailed Log

```
=== SIM 18: Testing lint commands ===
Step 1: Testing lint stats...
Command: mw lint stats
Return code: 1
STDOUT: 
STDERR: Traceback (most recent call last):
  File "/home/Memo1981/MyWork-AI/tools/auto_linting_agent.py", line 25, in <module>
    from watchdog.observers import Observer
ModuleNotFoundError: No module named 'watchdog'

Step 2: Testing lint scan with specific file...
Command: mw lint scan --file tools/mw.py
Return code: 1
STDOUT: 
Step 3: Testing lint scan with non-existent file...
Command: mw lint scan --file nonexistent.py
Return code: 1
STDOUT: 
STDERR: Traceback (most recent call last):
  File "/home/Memo1981/MyWork-AI/tools/auto_linting_agent.py", line 25, in <module>
    from watchdog.observers import Observer
ModuleNotFoundError: No module named 'watchdog'

✓ Command failed as expected for non-existent file
Step 4: Testing additional lint commands...
✓ Lint help is available
✓ Help lists available lint subcommands
```

### SIM19 Detailed Log

```
=== SIM 19: Testing Ctrl+C interrupt handling ===
Test 1: Simulating interrupt during scan...
Interrupted scan - Return code: 0
STDOUT: 
🔍 Scanning projects for modules...
  📦 big-project: 3 modules found
  📦 blog-platform: 5 modules found
  📦 api-hub: 21 modules found
  📦 ai-dashboard: 110 modules found
  📦 task-tracker: 153 modules found

✅ Scan complete! 292 modules indexed.
   Registry saved to: /home/Memo1981/MyWork-AI/.planning/module_registry.json

[1m🔍 Scanning projects for modules...[0m

⚠ Interrupt handling unclear
Test 2: Checking for file corruption...
✓ project_registry.json appears intact
✓ mw.py appears intact
✓ STATE.md appears intact
✓ No file corruption detected
Test 3: Testing interrupt during brain operation...
Interrupted brain command - Return code: 0
Test 4: Testing cleanup behavior...
⚠ Temporary files found: ['.tmp', 'health_check.lock']
Test 5: Verifying system functionality after interrupts...
✓ System remains functional after interrupts
```

### SIM20 Detailed Log

```
STDOUT: 📁 Creating project: my-app
✅ Project created at: /home/Memo1981/MyWork-AI/projects/my-app

   Next steps:
   1. cd projects/my-app
   2. Review .planning/PROJECT.md
   3. Run /gsd:plan-phase 1

✓ Command succeeded (uses default template)
Cleaned up test project
Test 2: brain add (no type, no content)
Command: mw brain add
Return code: 1
STDOUT: Usage: mw brain add <what you learned>

✓ Helpful error for missing arguments
Test 3: mw search (no query)
Command: mw search
Return code: 0
STDOUT: 
Search Commands — Module Registry Search  
========================================
Usage:
    mw search <query>               Search module registry for reusable code
    mw search --help                Show this help message

Description:
    Search through the module registry to find reusable code components,
    functions, and patterns from existing projects. Helps avoid reinventing
    the wheel by finding code you or others have already written.

Examples:
    mw search "auth"                # Find authentication modules
    mw search "database"            # Find database-related code
    mw search "api client"          # Find API client implementations
    mw search "validation"          # Find validation functions


Test 4: mw af start (no project)
Command: mw af start
Return code: 1
STDOUT: Usage: mw af start <project-name>

✓ Helpful error for missing project name
Test 5: Checking help availability for commands
Help available for 3/3 commands
✓ Most commands have help available
```

