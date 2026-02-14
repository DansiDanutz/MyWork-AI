# MyWork-AI Changelog

All notable changes to MyWork-AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),




## [2.3.2] - 2026-02-14

### ✨ Features
- feat: add mw deps audit — dependency security scanner (Memo)
- feat: add GSD command + register af/autoforge/gsd/plan in dispatcher (Memo)
- feat: add 'mw time' developer time tracking command (Memo)
- feat: add mw doctor command — diagnose common project issues (4 tests) (Memo)

### 🐛 Bug Fixes
- Fix: Add mw completion alias for shell autocompletion (Memo)
- Fix: Add mw completion alias for shell completions (Memo)
- fix: cmd_doctor + cmd_deploy + error handling improvements (Memo)
- fix: resolve security scanner hanging due to regex backtracking (Memo)
- fix: resolve 3 critical UX issues in MyWork-AI (Memo)
- fix: update doctor tests to match new output format and increase test timeout (Memo)
- fix: security — remove tests_backup from git, add noqa:security to scanner patterns (Memo)

### 📚 Documentation
- Docs: Add first-time UX sprint test reports (Memo)

### 📦 Other
- release: v2.3.1 — GSD, enhanced setup/tour, marketplace, templates (Memo)
- Enhanced setup and tour integration (Memo)
- 🚀 RELEASE v2.3.0: Professional README + Enhanced PyPI Metadata (Memo)
- Add comprehensive user journey test report (Memo)
- Enhanced CI/CD: Add PyPI publishing workflow and setup documentation (Memo)
- Deploy documentation site to Vercel and update README (Memo)
- Clean up README: Remove dead URLs (Analytics Dashboard, Website) (Memo)
- Enhance mw doctor with comprehensive diagnostics (Memo)

## [2.3.0] - 2026-02-14

### ✨ Features
- feat: add mw insights — tech debt, hotspots, coverage & contributor analysis (10 tests) (Memo)
- feat: achieve 100/100 health score — add lock file, editorconfig, fix lock detection (Memo)
- feat: add mw badge — auto-generate shields.io badges + README updater (11 tests) (Memo)
- feat: add mw test doctor — find hanging/broken tests automatically (Memo)
- feat: add mw tree — smart project tree with git status, icons, .gitignore support (15 tests) (Memo)
- feat: add mw plugin system — extend mw with custom commands (create/install/remove/run) (Memo)
- feat: add mw git standup/contributors/summary subcommands + fix project_archive Tuple import (Memo)
- feat: add mw test-coverage — analyze test gaps, scaffold missing tests (43% → 100% file coverage) (Memo)
- feat: add mw env — environment variable manager (audit, compare, template, secrets scan) (Memo)
- feat: add mw health — instant project health score (0-100) with grade, bar chart, and recommendations (Memo)
- feat: add mw profile — command profiler with CPU/memory/IO stats, history, Python cProfile support (Memo)
- feat: add mw ci status — live GitHub Actions status checker; fix CI/CD pipeline (flake8→ruff), fix security scan false positives (Memo)
- feat: add mw bench — code benchmarking with stats, baselines, and comparisons (Memo)
- feat: add mw secrets — encrypted secrets vault with set/get/inject/audit (Memo)
- feat: add mw depgraph — dependency graph analyzer with cycle detection, DOT/JSON export, and stats (Memo)
- feat: add mw metrics — code metrics dashboard (LOC, complexity, quality score, tech debt) (Memo)
- feat: add mw upgrade — self-upgrade from GitHub or PyPI with version check (Memo)
- feat: add mw watch — smart file watcher with auto-test (Memo)
- feat: add mw context — smart context builder for AI coding assistants (Memo)
- feat: add mw todo — scan codebase for TODO/FIXME/HACK/XXX comments (9 tests) (Memo)
- feat: add mw ai refactor-static — AST-based code refactoring analyzer (Memo)
- feat: add mw ai optimize — AST-based Python performance analyzer (Memo)
- feat: add mw ai generate — create complete files from natural language descriptions (Memo)
- feat: add mw ci — auto-generate CI/CD pipelines from project analysis (Memo)
- feat: add mw selftest — quick installation verification (<1s, 8 checks, JSON output for CI) (Memo)
- feat: redesign web dashboard with modern UI, tabs, brain search, git stats, auto-refresh (Memo)
- feat: enhanced mw changelog — conventional commit parsing, scoped groups, breaking changes, JSON output, stats (Memo)
- feat: add mw pair — live AI pair programming with file watching (Memo)
- feat: add mw demo — live interactive demo showcasing all framework features (Memo)
- feat: add mw tour — interactive 2-minute onboarding for new users (Memo)
- feat: enhance mw init with smart auto-detection (language, framework, tooling) (Memo)
- feat: add mw recap — productivity summary command (daily/weekly/custom) (Memo)
- feat: add mw api — REST API server for programmatic framework access (Memo)
- feat: add mw check — quality gate command (lint+test+types+security+git) (Memo)
- feat: add mw migrate — universal database migration manager (Memo)
- feat: enhanced docs site with mobile menu, TOC, copy buttons, hero section, animations (Memo)
- feat: add mw docs site — static documentation site generator with 10 pages, dark theme, search, and full command reference (Memo)
- feat: add mw deps — comprehensive dependency management (list, outdated, audit, tree, licenses, why, size, cleanup, export) (Memo)
- feat: add mw snapshot (project metrics tracking) + fix health check server mode (Memo)
- feat: add mw ai review, doc, changelog — 3 new AI-powered commands (Memo)
- feat: add mw run — universal task runner (discovers npm/make/cargo/procfile + custom tasks) (Memo)
- feat: add mw completions - shell autocompletion for bash/zsh/fish (Memo)

### 🐛 Bug Fixes
- Fix critical syntax errors and improve error handling (Memo)
- Fix MyWork CLI error handling and help system (Memo)
- fix(ci): replace flake8 with ruff in CI pipeline (Memo)
- fix: security hardening — replace os.system with subprocess.run, sanitize test secrets, enable SSL verification, clean example placeholders (Memo)
- fix: resolve CI failures — ruff output format + security scan .env pattern (Memo)
- fix: add missing Tuple import in project_archive.py (fixes test collection error) (Memo)
- fix: update version test to 2.1.0, add --timeout=30 to mw test runner (Memo)
- fix: rewrite test_bench.py to match actual bench.py API (6/6 pass) (Memo)
- fix: resolve import errors + flaky tests (Memo)

### 📚 Documentation
- docs: update STATE.md with mw tree addition (Memo)
- docs: update STATE.md with mw context addition (Memo)
- docs: update STATE.md with mw todo addition (Memo)
- docs: update README badges (v2.1.0, 676 tests, selftest verification step) (Memo)
- docs: update STATE.md with mw check (Memo)
- docs: update STATE.md with migrate command (Memo)
- docs: update STATE.md with 2026-02-12 changes (Memo)
- docs: add docstrings to all 16 undocumented functions in mw.py (Memo)
- docs: add comprehensive CLI reference + 25 workflow engine tests (Memo)

### 📦 Other
- Complete comprehensive testing of GROUP 2 Dev Tools commands (Memo)
- 🛡️ Add global exception handling and improve config validation (Memo)
- 🔧 Fix CI/CD: resolve ruff lint errors and security scan false positive (Memo)
- 🧪 Fix hanging tests: MyWork-AI now production ready (Memo)
- 🚀 Release v2.2.0 - Production Ready Package (Memo)
- 🧹 PRODUCTION READY: Code quality & cleanup (Memo)
- Security cleanup: Fix all HIGH/MEDIUM issues, improve score from 0/100 to 94/100 (Memo)
- 🧹 Professional repo cleanup (Memo)
- chore: add .env.example for task-tracker (Memo)

## [2.2.0] - 2026-02-14

### 🐛 Bug Fixes - Production Ready Package
- **CRITICAL:** Fix pip install entry points - `mw status`, `mw doctor` now work when installed from PyPI
- **CRITICAL:** Rewrite run_tool() function to support both development and pip-installed scenarios  
- **PACKAGING:** Add comprehensive MANIFEST.in to include all necessary files in PyPI package
- **PACKAGING:** Fix module import resolution for pip-installed packages vs development environment
- **PACKAGING:** Entry points (`mw --help`, `mw status`, `mw doctor`) now work correctly after `pip install mywork-ai`

### 📦 Package Improvements
- feat: Add proper MANIFEST.in for comprehensive file inclusion in PyPI packages
- fix: Module import strategy now works for both development (file-based) and production (pip-installed) scenarios
- test: Verified `pip install mywork-ai` works correctly from PyPI in clean virtual environment
- docs: Package is now truly production-ready for PyPI distribution

### 🧪 Testing
- test: Validated all key entry points work after pip installation
- test: Confirmed `mw --help`, `mw status`, `mw doctor` function correctly in pip-installed environment


## [2.1.0] - 2026-02-12

### ✨ Features
- feat: add mw plugin - extensible plugin system with install/uninstall/create/security-scan (21 tests) (Memo)
- feat: add mw db - universal database management (status, tables, schema, query, migrate, seed, export, backup/restore) with 33 tests (Memo)
- feat: add mw api - FastAPI project scaffolder with auto CRUD generation (14 tests) (Memo)
- feat: add mw bench - project performance benchmarking with history tracking, comparison, and CI mode (21 tests) (Memo)
- feat: multi-provider AI assistant - support DeepSeek, Gemini, OpenAI + interactive chat mode (Memo)
- feat: add mw serve - web dashboard with project overview, git log, brain stats, command runner (17 tests) (Memo)
- feat: add mw perf - project performance analyzer (deps, files, code quality, startup time, score) (15 tests) (Memo)
- feat: add mw audit - comprehensive project quality report card (10 tests) (Memo)
- feat: add mw hook - git hooks management with install, remove, create, run, status (19 tests) (Memo)
- feat: add mw git - smart git operations with auto-commit, branch, diff, stash, undo, cleanup (18 tests, 317 total) (Memo)
- feat: add mw security - security scanner with secrets, patterns, deps, gitignore checks (18 tests, 299 total) (Memo)
- feat: add mw ai - AI assistant with ask/explain/fix/refactor/test/commit (24 tests, 281 total) (Memo)
- feat: add mw config - configuration management (15 tests, 257 total) (Memo)
- feat: add mw env - environment variable management (23 tests, 242 total) (Memo)
- feat: add mw ci - CI/CD pipeline generator (16 tests, 219 total) (Memo)
- feat: add mw plugin - extensible plugin system (17 tests, 203 total) (Memo)
- feat: add mw deploy + mw monitor commands (11 tests, 186 total) (Memo)
- feat: add mw test (universal test runner) and mw workflow commands (6 tests, 175 total) (Memo)
- feat: add mw docs - auto documentation generator (12 tests, 169 total) (Memo)
- feat: add mw analytics - project insights, complexity, security, git trends (8 tests) (Memo)
- feat: add mw version command with -v/--version flags (Memo)
- feat: Phase 9 brain quality scoring, dedupe, provenance tracking (16 new tests, 149 total) (Memo)
- feat: Phase 8 credits ledger - payments, escrow, refunds, reconciliation (Memo)
- feat: massive UX enhancement - landing page, ecosystem docs, CLI improvements, all live app links (Memo)

### 🐛 Bug Fixes
- fix: repair test_ai_assistant.py - update imports and mocks for _get_provider_key signature (Memo)
- fix: escape quoting in pre-commit hook template (Memo)
- fix: resolve all test failures - 133/133 passing (Memo)
- fix: repair scaffold.py syntax errors - fix mobile template brace nesting (Memo)

### 📚 Documentation
- docs: update STATE.md with mw env addition (Memo)
- docs: update STATE.md with mw ci addition (Memo)
- docs: update STATE.md with mw test/workflow additions (Memo)
- docs: update STATE.md with new test count (84) (Memo)
- docs: professional README, CHANGELOG v2.0.0, world-class repo structure (Memo)

### 🧪 Tests
- test: add 9 brain tests for deprecate, delete, cleanup, filtering, and validation (Memo)

### 📦 Other
- security: remove hardcoded API keys from ai_review.py and ai_docs.py, use env vars (Memo)
- Phase 9: Add semantic search, deduplication, quality scoring & provenance tracking (Memo)

## [2.0.0] - 2026-02-10

### 🚀 Major Release — Production Ready

#### Added
- **`mw setup`** — First-time setup wizard with ASCII art welcome
- **`mw guide`** — Interactive workflow tutorial for new users
- **`mw prompt-enhance`** — Turn rough ideas into GSD-ready specs
- **`mw dashboard`** — Visual framework overview with colors
- **AutoForge integration** — Rebranded from Autocoder, backwards compatible
- **Brain semantic search** — TF-IDF based search with fuzzy matching
- **Brain knowledge graph** — Auto-detect relationships, clustering, ASCII visualization
- **Brain analytics** — Growth tracking, tag clouds, quality scores, staleness reports
- **Agent Skills System** — Install/create/manage skills (Anthropic-compatible)
- **Simulation Engine** — 20 virtual users, MLM (5 levels), virtual credits, product lifecycle
- **Security Scanner** — Code scanner, dependency audit, API tester, infrastructure scanner
- **30 User Simulations** — Beginner/intermediate/advanced scenarios with error handling
- **E2E Test Suite** — GSD, Brain, AutoForge, marketplace smoke tests
- **4 Workflow Templates** — Deploy, code review, release, incident response
- **`--help` for all commands** — Every subcommand now self-documenting
- **Fuzzy command matching** — Typos suggest correct commands
- **Project name validation** — Prevents invalid names with clear guidance
- **Input validation** — Brain entries, search queries, all inputs validated

#### Fixed
- All hanging commands (health check, doctor, report, fix, lint scan)
- Added timeouts to ALL subprocess calls (max 10s)
- npx n8n-mcp uses `--no-install` to prevent download hangs
- Auto-detect available lint tools (skip missing ones)
- Fixed `auto_fix()` function call in health check
- Fixed scaffold.py format string bug with literal braces
- Fixed 6 failing mw_cli tests (SystemExit handling)
- Made watchdog import optional

#### Security
- 0 critical vulnerabilities (down from 4)
- Hardcoded secrets moved to environment variables
- Input validation on all subprocess calls
- Security baseline established for monitoring

#### Quality
- 75/75 unit tests passing
- 30/30 user simulations completed
- Marketplace endpoints healthy (4/4)
- All CLI commands respond in <15s
and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-02-09 - AutoForge & Enhanced UX

### Added

- **Interactive Dashboard**: `mw dashboard` command with beautiful terminal UI

  showing framework metrics, component status, git activity, and disk usage

- **AutoForge Integration**: Complete rebrand from Autocoder to AutoForge with

  reference to <https://github.com/AutoForgeAI/autoforge>

- **Enhanced Brain Search**: Improved search formatting with colored boxes,

  result grouping, and pagination

- **Markdown Export**: `brain export markdown` command to dump knowledge base to

  structured markdown

- **Git Integrity Checks**: Comprehensive repository validation including working

  directory status, remote sync, and configuration

- **Advanced Dependency Monitoring**: Framework-specific package checking with

  version requirements

### Changed

- **Major Rebrand**: All Autocoder references updated to AutoForge throughout

  codebase

- **CLI Commands**: New `mw af` commands replace `mw ac` (backwards compatibility

  maintained)

- **Tool Architecture**: `autocoder_api.py` → `autoforge_api.py`,

  `autocoder_service.py` → `autoforge_service.py`

- **Health Check System**: Enhanced with git repository checks and AutoForge

  connectivity validation

- **Brain Tool UX**: Visual formatting with colored boxes, metadata display, and

  improved search results

### Fixed  

- Brain export method returning None instead of entry list
- Health check method naming consistency
- Git configuration validation and error handling

### Security

- Enhanced security checks for hardcoded secrets in framework files
- Improved .gitignore validation and recommendations

---

## [Previous Releases]

### Added

- **Interactive Dashboard**: New `mw dashboard` command with colored terminal UI

  and metrics

- **Enhanced Brain Search**: Improved formatting with colored boxes and result

  grouping

- **Markdown Export**: Brain knowledge export to structured markdown format
- **Git Integrity Checks**: Repository status, sync validation, and configuration

  checking

- **AutoForge Integration**: Complete rebrand from Autocoder with backwards

  compatibility

- **Advanced Health Checks**: AutoForge connectivity, dependency monitoring,

  framework file validation

- Comprehensive documentation overhaul with visual diagrams
- Progressive tutorial series (6 tutorials from beginner to expert)
- Working example projects with complete source code
- FAQ and troubleshooting guides
- Quick start guide (5-minute onboarding)
- API reference documentation for CLI and Python tools

### Changed

- **Major Rebrand**: All Autocoder references updated to AutoForge
- **CLI Commands**: `mw ac` → `mw af` with backwards compatibility aliases
- **Tool Files**: `autocoder_api.py` → `autoforge_api.py` (with symlinks for

  compatibility)

- **Health Monitoring**: Enhanced dependency checks with framework-specific

  packages

- **Brain Tool**: Improved search output with pagination and visual formatting
- Restructured documentation with `/docs` directory
- Improved framework architecture diagrams using Mermaid.js
- Enhanced CLI reference with examples and troubleshooting

### Fixed

- Brain export functionality (was returning None, now exports properly)
- Health check method name inconsistencies 
- Git configuration validation in health checks
- Documentation gaps identified in framework audit
- Missing visual explanations of 3-layer architecture

## [1.2.0] - 2026-01-27

### New Features

- **GSD (Get Shit Done)** project orchestration layer
  - Automated project planning with AI research
  - Phase-based development with verification gates
  - Cross-session state management and handoff
  - Adaptive planning for changing requirements
- **Autocoder Integration** for autonomous coding
  - Multi-session long-running development
  - Parallel agent execution (1-5 concurrent agents)
  - Progress monitoring and control
  - API and UI interfaces
- **n8n Workflow Automation** with MCP integration
  - 1,084 nodes and 2,709 workflow templates
  - Visual workflow builder integration
  - Expert guidance through n8n-skills
  - Template deployment and auto-fixing
- **Brain Knowledge System** for continuous learning
  - Automatic pattern extraction from completed work
  - Searchable knowledge vault
  - Module registry for code reuse
  - Experience-based recommendations
- **Unified CLI** (`mw` command) for all operations
  - Project creation and scaffolding
  - Health diagnostics and auto-repair
  - Brain search and knowledge management
  - Module registry search and indexing

### Framework Architecture

- **3-Layer Architecture** implemented:
  - **Layer 1: GSD** - Project orchestration and planning
  - **Layer 2: WAT** - Workflows, Agents, and Tools execution
  - **Layer 3: Automation** - Autocoder, n8n, and integrations
- **Intelligence Layer** with brain learning and analytics
- **Modular design** with clear separation of concerns

### Tools & Utilities

- `mw.py` - Unified command-line interface
- `brain.py` - Knowledge vault management
- `brain_learner.py` - Automatic pattern extraction
- `autocoder_api.py` - Autocoder control and monitoring
- `n8n_api.py` - n8n workflow management
- `health_check.py` - System diagnostics and repair
- `scaffold.py` - Project creation from templates
- `module_registry.py` - Code indexing and search
- `auto_update.py` - Framework component updates

### Project Templates

- **CLI** - Command-line tools with Click
- **FastAPI** - REST API backends with SQLite
- **Next.js** - Frontend applications with TypeScript/Tailwind
- **Full-stack** - Complete web applications
- **Automation** - n8n + Python webhook processors

### Integrations

- **Anthropic Claude** - Primary AI model for code generation
- **OpenAI GPT** - Alternative AI provider
- **GitHub** - Repository management and deployment
- **Vercel** - Frontend hosting and deployment
- **Neon/Railway** - Database hosting
- **Upstash** - Redis caching and rate limiting

## [1.1.0] - 2026-01-15

### Implemented

- Initial GSD skill set with basic project orchestration
- Autocoder server integration
- n8n MCP server support
- Basic brain learning system
- Project scaffolding capabilities

### Framework Foundation

- WAT (Workflows, Agents, Tools) architecture
- Python tooling framework
- Git integration and atomic commits
- Cross-session state management

### Core Skills

- `/gsd:new-project` - Project initialization with AI planning
- `/gsd:plan-phase` - Detailed phase planning
- `/gsd:execute-phase` - Parallel task execution
- `/gsd:verify-work` - Manual testing and verification
- `/gsd:progress` - Project status and routing

## [1.0.0] - 2025-12-20

### Initial Release

- Initial release of MyWork Framework
- Basic project structure
- Core tooling foundation
- Git repository setup
- Environment configuration

### Framework Concept

- AI-first development methodology
- Structured project management
- Tool-based automation approach
- Knowledge capture and reuse

---

## Release Notes

### Versioning Strategy

MyWork Framework follows semantic versioning:

- **Major (X.0.0)**: Breaking changes, new architecture
- **Minor (1.X.0)**: New features, capabilities, significant improvements
- **Patch (1.1.X)**: Bug fixes, documentation, minor improvements

### Upgrade Instructions

#### From 1.1.x to 1.2.x

```bash

# Backup existing projects

cp -r projects/ projects-backup/

# Update framework

git pull origin main

# Install new dependencies

pip install -r requirements.txt
npm install  # If using n8n features

# Run health check

python tools/mw.py doctor --fix

# Update existing projects (optional)

cd projects/your-project/
python ../../tools/mw.py gsd progress

```markdown

#### From 1.0.x to 1.1.x

```bash

# Framework was restructured - manual migration required

# See migration guide in docs/migration/1.0-to-1.1.md

```markdown

### Breaking Changes

#### 1.2.0

- **None** - Fully backward compatible with 1.1.x
- New features are additive and don't affect existing workflows

#### 1.1.0

- Moved from basic scripting to skill-based architecture
- Project structure standardized with `.planning/` directories
- Some tool names changed (see migration guide)

### Development Roadmap

#### Upcoming Features (1.3.0)

- **Enhanced AI Models** - Support for more providers (Grok, Gemini)
- **Visual Planning Interface** - Web UI for GSD planning
- **Team Collaboration** - Shared planning and execution
- **Advanced Templates** - Industry-specific project templates
- **Performance Optimization** - Faster execution and reduced token usage

#### Future Vision (2.0.0)

- **Multi-Language Support** - Beyond Python/JS to Go, Rust, etc.
- **Cloud Integration** - Hosted planning and execution
- **Enterprise Features** - SSO, audit logs, compliance
- **Plugin Ecosystem** - Third-party extensions and integrations

### Community

#### Contributors

- **Dan Sidanutz** - Framework architect and lead developer
- **Community Contributors** - Bug reports, feature requests, documentation

#### How to Contribute

1. **Report Issues**: [GitHub

Issues](https://github.com/DansiDanutz/MyWork-AI/issues)

2. **Feature Requests**: [GitHub

Discussions](https://github.com/DansiDanutz/MyWork-AI/discussions)

3. **Code Contributions**: Fork, develop, submit PR
4. **Documentation**: Help improve guides and examples

#### Support Channels

- 💬 **Community**: [GitHub

  Discussions](https://github.com/DansiDanutz/MyWork-AI/discussions)

- 🐛 **Bug Reports**: [GitHub

  Issues](https://github.com/DansiDanutz/MyWork-AI/issues)

- 📧 **Direct Support**: [support@mywork.ai](mailto:support@mywork.ai)
- 📺 **Video Guides**: [YouTube Channel](https://youtube.com/@MyWorkAI)

---

*For detailed migration guides, see the [Migration
Documentation](docs/migration/).*
