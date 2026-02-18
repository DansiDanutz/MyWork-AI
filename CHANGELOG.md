## [3.0.0] - 2026-02-18

### Added
- **`mw build-and-sell`** — One command: idea → plan → build → test → package → marketplace-ready product (also `mw bas` / `mw sell`)
- All 4 phases of the upgrade plan COMPLETE
- Full pipeline: 51 seconds from idea to sellable product

### Changed
- Total commands: **77+**
- Major version bump — framework is feature-complete for v3

---

## [2.9.0] - 2026-02-18

### Added
- **`mw tui`** — Interactive TUI dashboard with Rich (one-key actions: new, plan, execute, deploy, sell, test, git, health)
- **`mw web`** — Browser dashboard at localhost:9000 (project overview, marketplace stats, pipeline visualization, run commands from browser)
- Phase 3 of upgrade plan COMPLETE

### Changed
- Total commands: **74+**

---

## [2.8.0] - 2026-02-18

### Added
- **`mw plan`** — AI Project Planner: describe your idea → AI generates REQUIREMENTS.md, ROADMAP.md, and AI_SPEC.json with phased tasks, tech stack, and pricing
- **`mw execute`** — AI-Powered Build Execution: reads the plan, generates code phase-by-phase (main.py, requirements, Dockerfile, docker-compose, setup.sh, README, LICENSE), auto-commits each phase
- **Full `mw plan` → `mw execute` → `mw marketplace publish` pipeline** — from idea to sellable product in minutes
- **`mw stats --json`** — machine-readable output for stats command
- **Enhanced `mw stats`** — contributors, project age, most active day, top languages with visual bars

### Fixed
- datetime import in execute command scope

### Changed
- Total commands: **72+**
- Tests: **140 passing**
- Now supports full GSD-style AI-driven workflow: plan → discuss → execute → publish

---

## [2.7.0] - 2026-02-17

### Added
- **`mw new --ai`** — AI-powered project generation: describe idea → AI spec → scaffold → custom code generation → working project
- **`mw agent`** — Nanobot-inspired AI agent engine (agent.yaml configs, multi-provider LLM)
- **Multi-provider AI support** — LiteLLM → DeepSeek → OpenRouter → Gemini fallback chain
- **AI code generation in `mw new`** — generates real FastAPI endpoints from AI spec
- **`mw loc` / `mw lines`** — Lines of code counter by language

### Changed
- Total commands: **70+**

---

## [2.6.0] - 2026-02-16

### Added
- **6 Competitive Features**: `mw webhook test`, `mw secrets`, `mw cost`, `mw templates browse`, `mw share`, `mw cron`
- **Marketplace Publisher**: `tools/marketplace_publisher.py` — multi-platform product listing tool
- **10 Landing Pages**: Professional dark-theme pages for all products + mega bundle
- **Cost Tracking**: AI API cost estimation across GPT-4, Claude, Gemini, DeepSeek — unique feature no competitor has
- **Encrypted Secrets Vault**: `mw secrets set/get/list/delete/export` with Fernet encryption
- **Webhook Testing**: `mw webhook test` — local HTTP listener for webhook debugging

### Fixed
- **Packaging**: Now ships ALL 134 .py files (was only 11 — tour, demo, audit were broken from pip install)
- **Version Detection**: `mw version` shows correct version from pip install (was "vunknown")
- **Duplicate Function Bug**: Fixed `_detect_project_type` collision that broke 26 tests
- **CI Pipeline**: Updated to use `ruff` instead of `flake8`

### Changed
- Total commands: **67+** (was 61)
- Tests: **133/133 passing**
- Setup.py rewritten: proper `packages=["tools"]` instead of manual `py-modules` list
- GitHub description & topics updated for discoverability
- README completely rewritten with accurate stats and marketplace focus

---

## [2.5.0] - 2026-02-15

### Added
- **6 Competitive CLI Features**: webhook, secrets, cost, templates, share, cron commands
- Total commands: 67 (from 61)

---

## [2.4.0] - 2026-02-15

### Added
- **n8n Integration**: 16 new `mw n8n` commands (setup, status, list, import, export, activate, deactivate, delete, exec, executions, logs, config, test)
- **GSD Planning**: `mw gsd` commands for project planning (new, status, progress, quick)
- **AutoForge Registration**: `mw af` / `mw autoforge` commands properly wired
- **Marketplace Automation**: `mw marketplace publish` now auto-uploads to R2 and lists via API
- **Workflow Validation**: `mw n8n test` validates workflow JSON locally before deploy
- **n8n Docker Setup**: `mw n8n setup` installs n8n via Docker or npm automatically
- **SaaS Template**: `mw new my-app saas` — full-stack SaaS with auth, billing, dashboard
- **Launch Command**: `mw launch` — pre-launch checklist with countdown
- **Clone Command**: `mw clone <product>` — clone marketplace products
- **Analytics Setup**: `mw analytics setup <provider>` — PostHog, GA, Mixpanel

### Fixed
- All 133 tests passing
- README accuracy
- CI/CD pipeline

---

## [2.3.3] - 2026-02-14

### Features
- `mw deps audit` — dependency security scanner
- GSD command + register af/autoforge/gsd/plan in dispatcher
- `mw time` developer time tracking
- `mw doctor` — diagnose common project issues

---

## [2.3.0] - 2026-02-13

### Initial Release
- Core framework with 38+ CLI commands
- Brain knowledge vault
- Project scaffolding (12 templates)
- Security scanning
- AI code generation
- Marketplace integration
- n8n workflow automation basics
