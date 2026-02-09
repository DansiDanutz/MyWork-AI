# MyWork Framework Changelog

All notable changes to the MyWork Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
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
