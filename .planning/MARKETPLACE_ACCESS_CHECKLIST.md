# Marketplace Access & Deployment Checklist

Date: January 26, 2026  
Owner: Codex (implementation) + Dansi (product)

This checklist covers everything we must verify now that the Marketplace code
lives in the private `DansiDanutz/Marketplace` repository. It satisfies Phase 1
of the cross-product plan (`.planning/MARKETPLACE_TASKTRACKER_PLAN.md`).

---

## 1. Repository Access & Branch Protection

| Item | Status | Owner | Notes |
| ------ | -------- | ------- | ------- |
  | Maintainer ac... | [x] | Dansi | **Verified 20... |  
  | Branch protec... | [~] | Codex (needs ... | **BLOCKED:** ... |  
  | Deploy bot/se... | [ ] | Dansi | Ensure `marke... |  

## 2. Secret Inventory (CI/CD)

| Target | Secret Name | Where to Configure | Notes |
| -------- | ------------- | -------------------- | ------- |
  | Vercel Fron... | `VERCEL_TOK... | GitHub Acti... | Needed for ... |  
  | Vercel Prot... | `VERCEL_AUT... | GitHub Acti... | Optional bu... |  
  | Railway Bac... | `RAILWAY_TO... | GitHub Acti... | Enables `ra... |  
  | Backend Env... | `DATABASE_U... | Railway var... | Audit via R... |  
  | Marketplace... | `MARKETPLAC... | GitHub Acti... | Default URL... |  

**Current Secret Status (2026-01-26):**

- [ ] Export current secrets from old public repo (if any) and re-import into

  `DansiDanutz/Marketplace`.

- [ ] Document secret owners + rotation cadence in 1Password/Env vault. *(Owner:

  Dansi; due 2026-01-27.)*

**Action Required:** Go to
<https://github.com/DansiDanutz/Marketplace/settings/secrets/actions> and add:

- `VERCEL_TOKEN` - From <https://vercel.com/account/tokens>
- `VERCEL_ORG_ID` - Team ID: `team_Qtajbnyu0ZBt3TGPBIbgiyg1`
- `VERCEL_PROJECT_ID` - Project ID: `prj_VEcrKDCs7ZYOHcfgLYU4ILD592GV`
- `RAILWAY_TOKEN` - From Railway account settings
- `VERCEL_AUTOMATION_BYPASS_SECRET` - Generate secure random string

## 3. GitHub Actions

- [x] **COMPLETED 2026-01-26:** Deploy workflow installed at

  `DansiDanutz/Marketplace/.github/workflows/deploy.yml` (commit `7c9f4cb`)

  - Triggers on push to `main`
  - Includes Vercel frontend deployment
  - Includes smoke test step via MyWork-AI tools checkout
  - Workflow reference: `workflows/marketplace_ci_deploy.md`
- [x] **COMPLETED 2026-01-26:** Post-deploy smoke test step included in workflow
- [ ] Ensure Actions have permissions `contents: read`, `deployments: write`.

  **PENDING:** Configure in Marketplace repo Settings → Actions → General

### Suggested Post-Deploy Step

```text
yaml

- name: Run Marketplace smoke tests

  working-directory: MyWork-AI  # repo checkout path with tools/
  env:

```text

yaml

MARKETPLACE_FRONTEND_URL: <https://frontend-hazel-ten-17.vercel.app>
MARKETPLACE_BACKEND_URL: <https://mywork-ai-production.up.railway.app>
VERCEL_AUTOMATION_BYPASS_SECRET: ${{ secrets.VERCEL_AUTOMATION_BYPASS_SECRET }}

```text
text

  run: |

```text

bash

python tools/smoke_test_marketplace.py

```text
text

```text

text

## 4. Deployment Targets

- [x] Vercel project points to the new private repo (Build & Git shows

  `DansiDanutz/Marketplace`, confirmed via Vercel UI on 2026-01-26).

- [ ] Railway service connected to new repo or manual deploy script updated.

  *(Pending – confirm deploy source or scripted CLI.)*

- [ ] Status page (`https://mywork-marketplace.vercel.app/status`) updated if

  domain changed. *(Pending – verify endpoint + badge.)*

## 5. Monitoring & Logging

- [ ] Alerts: configure Vercel + Railway notifications to Dansi + on-call.
- [ ] Axiom/Logtail (or chosen provider) still receiving logs after repo move.
- [ ] GitHub Action summary posts to Slack/Teams with deploy + smoke status.

## 6. Verification Steps

1. [x] **COMPLETED 2026-01-26:** CI workflow deployed to

`DansiDanutz/Marketplace` (commit `7c9f4cb`). Workflow installed with
`workflow_dispatch` trigger for manual runs.

2. [x] **COMPLETED 2026-01-26:** Vercel dashboard confirms deployment to

`frontend-hazel-ten-17.vercel.app`. Railway backend confirmed healthy at
`mywork-ai-production.up.railway.app/health`.

3. [x] **COMPLETED 2026-01-26 20:52 UTC:** Smoke test passed locally:

```text
yaml
   [OK] frontend root
   [OK] backend root
   [OK] backend health
   [OK] backend products
   All smoke checks passed.

```text

text

4. [ ] Update `.planning/STATE.md` with deployment timestamp and any incidents.

**PENDING:** Will be updated in next commit.

## 7. Owners & Next Actions

- Dansi: confirm repo permissions + secrets migration.
- Codex: keep smoke script + tooling aligned; assist wiring CI.
- Target completion: January 27, 2026.

---

## 8. Brain Webhook Integration (NEW)

- [x] **COMPLETED 2026-01-26:** Brain ingestion endpoint deployed at

  `https://mywork-ai-production.up.railway.app/api/analytics/brain/ingest`
  (commit `8a7127f`)

  - Accepts POST requests from Task Tracker
  - Logs events with `brain_ingest_event` tag
  - Schema: `{id, type, userId, properties, recordedAt, source}`
- [ ] **PENDING:** Configure `BRAIN_WEBHOOK_URL` in Task Tracker Vercel

  environments (Production + Preview + Development)

  - Go to:

```text
text

<https://vercel.com/irises-projects-ce549f63/frontend/settings/environment-variables>

```text

yaml

  - Add variable: `BRAIN_WEBHOOK_URL`
  - Value:

```text
text

`https://mywork-ai-production.up.railway.app/api/analytics/brain/ingest`

```text

yaml

- [ ] **PENDING:** Test webhook by triggering Task Tracker events and verifying

  `brain_ingest_event` logs in Railway
