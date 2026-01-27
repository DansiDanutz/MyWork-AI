# MyWork Framework + Marketplace Full Audit Report

Date: 2026-01-27

## Scope

- **Included**: MyWork framework repo (`tools/`, `workflows/`, `docs/`, `tests/`, `.planning/`).
- **Marketplace**: Only the **integration assets** in this repo (CI templates, smoke/QA scripts, access checklist).
- **Not included**: The Marketplace application code (lives in private repo `DansiDanutz/Marketplace`).

## Method

- Static code review of framework tools and marketplace integration artifacts.
- Test execution: `pytest -q` in repo root.
- **Network-dependent smoke/QA scripts were not executed** in this environment.

---

## Executive Summary

- The framework is functional but **tests are currently failing** due to regressions in **Brain** and **Module Registry** components.
- Marketplace integration has CI/QA scaffolding and smoke checks but **relies on pending secret/configuration work** and **lacks verified alerting**.
- Immediate priorities: fix Brain data compatibility, repair Module Registry scanning, and harden environment-root handling.

---

## Test Status (2026-01-27)

**Command:** `pytest -q`

- **24 passed**, **10 failed**
- Failures are concentrated in `tests/test_brain.py` and `tests/test_module_registry.py`.

### Failed tests (summary)

- Brain loading and stats
- BrainEntry initialization (missing `references` field)
- Module registry loading and search

---

## Findings (Severity Ranked)

### High

1) **Brain data incompatibility (tests + runtime)**

- **Evidence**: `BrainEntry` dataclass does **not** accept a `references` field, but `brain_data.json` and tests include it. `BrainManager.load()` catches `TypeError` and silently skips entries, leaving an empty brain.
- **Impact**: Brain data fails to load; knowledge base appears empty; test suite fails; downstream Brain sync/learning likely degraded.
- **Fix**:
  - Add `references: int = 0` to `BrainEntry`.
  - Make `BrainEntry.from_dict()` tolerant to unknown keys (filter or `**{k:v for k in data if k in fields}`).
  - Add a small migration step to normalize existing JSON and prevent silent failures.

2) **Module Registry scan is effectively broken**

- **Evidence**: `ProjectScanner.scan_project()` has a mis-indented `try` block. It calls `scan_file()` **outside** the file loop, so most files are skipped. In some cases it only scans the last file; in other cases it scans nothing at all.
- **Impact**: Registry becomes stale/empty; search results unreliable; tests fail; cross-project reuse suffers.
- **Fix**:
  - Fix indentation so `scan_file()` runs **inside** the file iteration loop.
  - Add a unit test asserting that a simple project scan yields at least one module.

---

### Medium

1) **Tests failing due to configuration root caching**

- **Evidence**: Tests set `MYWORK_ROOT`, then import tools. Tools use cached `config.MYWORK_ROOT`, which does not update once loaded. `BrainManager` and `ModuleRegistry` then load from the wrong path.
- **Impact**: Failing tests; reduced reliability in multi-root or dynamic environments (e.g., when running tools against different roots in the same process).
- **Fix**:
  - Refactor tools to derive root at runtime (call `config.get_mywork_root()` or pass root into manager constructors).
  - In tests, explicitly reload `config` before importing tool modules.

2) **Marketplace QA/Smoke pipeline lacks version pinning**

- **Evidence**: `workflows/marketplace_ci_template.yml` installs `vercel@latest` and `@railway/cli` without pinning.
- **Impact**: Workflow breaks when upstream CLI changes.
- **Fix**:
  - Pin CLI versions (e.g., `vercel@<known-good>`, `@railway/cli@<known-good>`).

3) **Network QA is fragile (no retries/backoff)**

- **Evidence**: `tools/qa/check_backend_health.py` and `tools/qa/check_frontend_routes.py` fail hard on a single network blip.
- **Impact**: CI flakes, false negatives.
- **Fix**:
  - Add retry logic with backoff for transient failures.
  - Optionally mark smoke/QA as “soft-fail” in cron, with alerting.

4) **Hard-coded production endpoint in `test_brain_webhook.py`**

- **Evidence**: Script posts directly to production by default.
- **Impact**: Accidental prod writes/noise if invoked locally.
- **Fix**:
  - Read endpoint from env var and require explicit confirmation or `--prod` flag.

---

### Low

1) **Security scanning is basic**

- **Evidence**: `health_check.py` uses simple pattern checks; no dedicated secret scanner.
- **Impact**: Low probability of missing secrets; no automated history scanning.
- **Fix**: Add optional `gitleaks` or `trufflehog` integration to `mw doctor`.

2) **Brain markdown update is shallow**

- **Evidence**: `_update_brain_md()` only updates “Last updated” line; it does not sync entries.
- **Impact**: BRAIN.md can drift from actual JSON state.
- **Fix**: Either rebuild sections or clearly state that BRAIN.md is manual.

---

## Marketplace Integration Status (from this repo)

- **CI templates exist**: `workflows/marketplace_ci_template.yml`, `workflows/marketplace_smoke_cron.yml`.
- **QA scripts exist**: `tools/smoke_test_marketplace.py`, `tools/qa/check_backend_health.py`, `tools/qa/check_frontend_routes.py`.
- **Access checklist exists**: `.planning/MARKETPLACE_ACCESS_CHECKLIST.md` documents pending steps.

### Key Gaps (per checklist)

- Pending secret migration + ownership documentation.
- Branch protection not enforced (private repo limitation).
- Deploy bot/service account not confirmed.
- Railway deploy source not confirmed.
- Monitoring/alerting not configured for smoke failures.

**Note:** Marketplace app code was not audited here. A follow-up audit in `DansiDanutz/Marketplace` is required for backend auth, payments, and data access review.

---

## Recommendations (Prioritized)

1) **Fix Brain data compatibility** and make loader tolerant to unknown fields.
2) **Repair Module Registry scanning** and add a regression test.
3) **Normalize root handling** so tools honor `MYWORK_ROOT` at runtime.
4) **Pin CI tool versions** and add retries for QA scripts.
5) **Complete Marketplace access checklist** and verify secret migration + deploy source.
6) **Add secret scanning** (optional) to health checks.

---

## Appendix: Test Output Summary

- `tests/test_brain.py`: failures in load, update, stats, and BrainEntry initialization (missing `references`).
- `tests/test_module_registry.py`: failures in load, search, get_by_type/project/stats (registry empty).

---

## Post-Fix Status (2026-01-27)

**Changes applied:**

- Added `references` field to `BrainEntry`, and made `from_dict()` ignore unknown keys to restore compatibility.
- Made Brain and Module Registry resolve paths per instance to respect `MYWORK_ROOT` in tests and multi-root runs.
- Fixed Module Registry scan indentation so files are actually scanned.

**Re-test:** `pytest -q`  
**Result:** **34 passed**, **0 failed**  
**Notes:** Pytest-asyncio warns about `asyncio_default_fixture_loop_scope` being unset (non-failing).

If you want, I can now:

- Implement the fixes (BrainEntry compatibility + module scan indentation + config root handling).
- Re-run tests and update this report with a **post-fix** status section.
- Start the Marketplace repo audit once access is available.
