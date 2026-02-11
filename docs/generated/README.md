# MyWork-AI

> Auto-generated documentation by MyWork AI Doc Generator
> Generated: 2026-02-11 07:08

## Overview

| Metric | Value |
|--------|-------|
| Language | Python |
| Framework | FastAPI |
| Source Files | 182 |
| Lines of Code | 51,909 |
| Features | pytest |

## Project Structure

```
MyWork-AI/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── PULL_REQUEST_TEMPLATE.md
├── .planning/
│   ├── audits/
│   ├── business/
│   ├── codebase/
│   ├── config/
│   ├── listings/
│   ├── phases/
│   ├── AUDIT_REPORT_2026-01-29.md
│   ├── AUDIT_SUMMARY_2026-01-29.md
│   ├── BRAIN.md
│   ├── brain_data.json
│   ├── brain_index.json
│   ├── ENHANCED_PROMPT.md
│   ├── LAUNCH_READINESS_PLAN.md
│   ├── linting_results.json
│   ├── MARKETPLACE_ACCESS_CHECKLIST.md
│   ├── MARKETPLACE_FIRST_LISTING_PLAN.md
│   ├── module_registry.json
│   ├── MODULE_REGISTRY.md
│   ├── PROJECT.md
│   ├── project_registry.json
│   ├── PROJECT_REGISTRY.md
│   ├── REQUIREMENTS.md
│   ├── ROADMAP.md
│   └── STATE.md
├── assets/
│   ├── screenshots/
│   └── logo.txt
├── backups/
│   └── brain/
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── generated/
│   ├── landing/
│   ├── tools/
│   ├── tutorials/
│   ├── faq.md
│   ├── index.md
│   ├── quickstart.md
│   └── troubleshooting.md
├── examples/
│   ├── cli-task-manager/
│   ├── fastapi-example.md
│   ├── fullstack-example.md
│   ├── marketplace-example.md
│   ├── nextjs-example.md
│   ├── README.md
│   └── saas-example.md
├── exports/
│   ├── BRAIN_EXPORT_20260209_000109.md
│   ├── BRAIN_EXPORT_20260209_003049.csv
│   ├── BRAIN_EXPORT_20260209_003049.md
│   ├── BRAIN_EXPORT_20260209_003127.csv
│   ├── BRAIN_EXPORT_20260209_003127.md
│   ├── BRAIN_EXPORT_20260209_145120.md
│   ├── BRAIN_EXPORT_20260209_145127.csv
│   ├── BRAIN_EXPORT_20260209_145127.md
│   ├── BRAIN_EXPORT_20260209_180117.md
│   └── BRAIN_EXPORT_20260209_180125.csv
├── projects/
│   ├── _template/
│   ├── ai-dashboard/
│   ├── api-hub/
│   ├── big-project/
│   ├── blog-platform/
│   ├── task-tracker/
│   └── README.md
├── reports/
│   ├── app_status_check.md
│   ├── e2e_report_2026-02-09.md
│   ├── e2e_summary_2026-02-09.json
│   ├── FRAMEWORK_AUDIT_2026-01-26.md
│   ├── framework_simulation_2025-02-09.md
│   ├── FULL_AUDIT_2026-01-27.md
│   ├── FULL_AUDIT_2026-01-28.md
│   ├── MARKETPLACE_LISTING_STATUS.md
│   ├── MARKETPLACE_QA_2026-01-27.md
│   ├── MARKETPLACE_QA_TEMPLATE.md
│   ├── security_audit_2026-02-09.md
│   ├── simulation_report_2026-02-09.json
│   ├── simulation_report_2026-02-09.md
│   ├── simulation_report_2026-02-10.json
│   ├── simulation_report_2026-02-10.md
│   ├── SPORTSAI_LISTING_ASSETS_2026-01-27.md
│   ├── SPORTSAI_SCREENSHOT_GUIDE.md
│   ├── SPORTSAI_SUPPORT_POLICY.md
│   └── STRATEGIC_AUDIT_2026-01-27.md
├── simulation_workspace/
│   └── empty_projects_test/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent_response.md
│   ├── test_analytics.py
│   ├── test_auto_linting.md
│   ├── test_autoforge.py
│   ├── test_brain.py
│   ├── test_brain_quality.py
│   ├── test_brain_search.py
│   ├── test_config.py
│   ├── test_health_check.py
│   ├── test_integration.py
│   ├── test_module_registry.py
│   ├── test_mw_cli.py
│   ├── test_perfect_agent.md
│   ├── test_performance.py
│   └── test_scaffold.py
├── tools/
│   ├── e2e/
│   ├── projects/
│   ├── qa/
│   ├── security/
│   ├── simulation/
│   ├── skills/
│   ├── tools/
│   ├── _template.py
│   ├── ai_docs.py
│   ├── ai_review.py
│   ├── analytics.py
│   ├── auto_lint_fixer.py
│   ├── AUTO_LINT_README.md
│   ├── auto_lint_scheduler.py
│   ├── AUTO_LINTER_README.md
│   ├── auto_linting_agent.py
│   ├── auto_update.py
│   ├── autocoder_api.py
│   ├── autocoder_service.py
│   ├── autoforge_api.py
│   ├── autoforge_service.py
│   ├── brain.py
│   ├── brain_graph.py
│   ├── brain_learner.py
│   ├── brain_quality.py
│   ├── brain_search.py
│   ├── brain_semantic.py
│   ├── brain_sync.py
│   ├── config.py
│   ├── credits_ledger.py
│   ├── dep_checker.py
│   ├── deploy.py
│   ├── DEPLOYMENT_GUIDE.md
│   ├── doc_generator.py
│   ├── error_handling_improvements.py
│   ├── health_check.py
│   ├── INTEGRATION_GUIDE.md
│   ├── lint_watcher.py
│   ├── marketplace_upload_previews.py
│   ├── module_registry.py
│   ├── mw.py
│   ├── n8n_api.py
│   ├── perfect_auto_agent.py
│   ├── project_archive.py
│   ├── project_compare.py
│   ├── project_health.py
│   ├── project_registry.py
│   ├── requirements.txt
│   ├── scaffold.py
│   ├── smoke_test_ai_dashboard.py
│   ├── smoke_test_marketplace.py
│   ├── smoke_test_task_tracker.py
│   ├── start_auto_linter.bat
│   ├── start_auto_linter.sh
│   ├── switch_llm_provider.py
│   ├── test_auto_linting.py
│   ├── test_brain_semantic.py
│   ├── test_brain_webhook.py
│   ├── test_credits_ledger.py
│   └── workflow_engine.py
├── workflows/
│   ├── _template.md
│   ├── autocoder_feature_verification.md
│   ├── code_review.md
│   ├── create_n8n_workflow.md
│   ├── deploy_to_vercel.md
│   ├── framework_maintenance.md
│   ├── getting_started.md
│   ├── gsd_to_autocoder.md
│   ├── gsd_with_n8n.md
│   ├── incident_response.md
│   ├── marketplace_ci_template.yml
│   ├── marketplace_smoke_cron.yml
│   ├── release.md
│   ├── session_handoff.md
│   └── use_autocoder.md
├── .env
├── .env.example
├── .gitignore
├── .gitleaks.toml
├── .mcp.json.example
├── .pre-commit-config.yaml
├── .security_baseline.json
├── CHANGELOG.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── ECOSYSTEM.md
├── FAQ.md
├── install.bat
├── install.sh
├── LICENSE
├── pyproject.toml
├── QUICK_START.md
├── README.md
├── ROADMAP.md
├── SECURITY.md
├── setup.py
├── start_auto_linter.sh
├── STATE.md
├── STRATEGY.md
├── TROUBLESHOOTING.md
├── USE_CASES.md
└── vercel.json
```

## Installation

```bash
pip install -r requirements.txt
```

Or install as package:
```bash
pip install .
```

## API Endpoints

| Method | Path | File |
|--------|------|------|
| `GET` | `type` | `tools/ai_review.py` |
| `GET` | `staged` | `tools/ai_review.py` |
| `GET` | `file` | `tools/ai_review.py` |
| `GET` | `language` | `tools/ai_review.py` |
| `GET` | `lines` | `tools/ai_review.py` |
| `GET` | `review` | `tools/ai_review.py` |
| `GET` | `scripts` | `tools/deploy.py` |
| `GET` | `dependencies` | `tools/deploy.py` |
| `GET` | `devDependencies` | `tools/deploy.py` |
| `GET` | `main` | `tools/deploy.py` |
| `GET` | `MYWORK_ROOT` | `tools/config.py` |
| `GET` | `AUTOCODER_ROOT` | `tools/config.py` |
| `GET` | `AUTOCODER_SERVER` | `tools/config.py` |
| `GET` | `MYWORK_ROOT` | `tools/mw.py` |
| `GET` | `projects` | `tools/mw.py` |
| `GET` | `type` | `tools/mw.py` |
| `GET` | `status` | `tools/mw.py` |
| `GET` | `marketplace` | `tools/mw.py` |
| `GET` | `brain_contribution` | `tools/mw.py` |
| `GET` | `entries` | `tools/mw.py` |
| `GET` | `MYWORK_ROOT` | `tools/autoforge_api.py` |
| `GET` | `passes` | `tools/autoforge_api.py` |
| `GET` | `in_progress` | `tools/autoforge_api.py` |
| `GET` | `status` | `tools/autoforge_api.py` |
| `GET` | `mcpServers` | `tools/n8n_api.py` |
| `GET` | `n8n-mcp` | `tools/n8n_api.py` |
| `GET` | `env` | `tools/n8n_api.py` |
| `GET` | `N8N_API_URL` | `tools/n8n_api.py` |
| `GET` | `N8N_API_KEY` | `tools/n8n_api.py` |
| `GET` | `data` | `tools/n8n_api.py` |
| `GET` | `status` | `tools/smoke_test_marketplace.py` |
| `GET` | `status` | `tools/smoke_test_marketplace.py` |
| `GET` | `MYWORK_ROOT` | `tools/project_archive.py` |
| `GET` | `name` | `tools/project_archive.py` |
| `GET` | `version` | `tools/project_archive.py` |
| `GET` | `dependencies` | `tools/project_archive.py` |
| `GET` | `devDependencies` | `tools/project_archive.py` |
| `GET` | `scripts` | `tools/project_archive.py` |
| `GET` | `access_count` | `tools/brain_quality.py` |
| `GET` | `access_count` | `tools/brain_quality.py` |
| `GET` | `MYWORK_ROOT` | `tools/autocoder_service.py` |
| `GET` | `AUTOFORGE_ROOT` | `tools/autocoder_service.py` |
| `GET` | `error` | `tools/auto_lint_scheduler.py` |
| `GET` | `total_fixes` | `tools/auto_lint_scheduler.py` |
| `GET` | `files_fixed` | `tools/auto_lint_scheduler.py` |
| `GET` | `total_fixes` | `tools/auto_lint_scheduler.py` |
| `GET` | `MYWORK_ROOT` | `tools/auto_update.py` |
| `GET` | `AUTOCODER_ROOT` | `tools/auto_update.py` |
| `GET` | `dependencies` | `tools/auto_update.py` |
| `GET` | `installed_version` | `tools/auto_update.py` |

## Modules

- **`examples/cli-task-manager/src/models.py`** — Task data models for the CLI Task Manager. (277 lines)
- **`examples/cli-task-manager/src/storage.py`** — Task storage and persistence layer for the CLI Task Manager. (430 lines)
- **`examples/cli-task-manager/src/task_manager.py`** — Simple Task Manager CLI - Built with MyWork Framework (352 lines)
- **`projects/ai-dashboard/backend/database/db.py`** — 0 classes, 4 functions (76 lines)
- **`projects/ai-dashboard/backend/database/models.py`** — 5 classes, 0 functions (181 lines)
- **`projects/ai-dashboard/backend/main.py`** — 10 classes, 21 functions (463 lines)
- **`projects/ai-dashboard/backend/scrapers/github_trending.py`** — 1 classes, 0 functions (276 lines)
- **`projects/ai-dashboard/backend/scrapers/news_aggregator.py`** — 1 classes, 0 functions (301 lines)
- **`projects/ai-dashboard/backend/scrapers/youtube_scraper.py`** — 1 classes, 0 functions (333 lines)
- **`projects/ai-dashboard/backend/scripts/youtube_upload_smoke.py`** — YouTube Upload Smoke Test (142 lines)
- **`projects/ai-dashboard/backend/services/prompt_optimizer.py`** — 3 classes, 0 functions (166 lines)
- **`projects/ai-dashboard/backend/services/scheduler_service.py`** — 1 classes, 0 functions (123 lines)
- **`projects/ai-dashboard/backend/services/youtube_automation.py`** — 1 classes, 0 functions (478 lines)
- **`projects/api-hub/backend/database/db.py`** — API Hub Database Configuration (25 lines)
- **`projects/api-hub/backend/database/models.py`** — API Hub Database Models (37 lines)
- **`projects/api-hub/backend/main.py`** — API Hub — Centralized API Key Manager (219 lines)
- **`projects/api-hub/backend/schemas.py`** — API Hub Pydantic Schemas (65 lines)
- **`projects/api-hub/tests/test_api.py`** — API Hub Tests — Full CRUD + Usage + Dashboard (153 lines)
- **`projects/big-project/backend/database/db.py`** — Database configuration. (17 lines)
- **`projects/big-project/backend/database/models.py`** — Database models. (12 lines)
- **`projects/big-project/backend/main.py`** — big-project API (36 lines)
- **`projects/blog-platform/backend/database/db.py`** — Database configuration. (17 lines)
- **`projects/blog-platform/backend/database/models.py`** — Database models. (12 lines)
- **`projects/blog-platform/backend/main.py`** — blog-platform API (36 lines)
- **`setup.py`** — MyWork-AI Framework Setup (97 lines)
- **`tests/__init__.py`** — MyWork-AI Framework Tests (5 lines)
- **`tests/conftest.py`** — Pytest Configuration and Fixtures (145 lines)
- **`tests/test_analytics.py`** — Tests for analytics engine. (70 lines)
- **`tests/test_autoforge.py`** — Tests for AutoForge integration modules. (180 lines)
- **`tests/test_brain.py`** — Tests for brain.py (326 lines)

---

*Documentation generated by [MyWork AI](https://github.com/DansiDanutz/MyWork-AI) `mw docs`*
