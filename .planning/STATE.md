# MyWork Framework State

Date: 2026-01-26

## Current Status
- Marketplace + Brain + Credits are live and healthy.
- Backend fixed for reserved SQLAlchemy field.
- Credits UI and submission audit UX are updated.
- Marketplace codebase lives in the private `DansiDanutz/Marketplace` repo with public Vercel/Railway deploys.
- Marketplace access checklist drafted in `.planning/MARKETPLACE_ACCESS_CHECKLIST.md`; smoke test (`tools/smoke_test_marketplace.py`) passes as of 2026-01-26.
- **Task Tracker deployed to Vercel** (2026-01-26): https://task-tracker-weld-delta.vercel.app
  - CI/CD workflow "Deploy Task Tracker to Vercel" is live and tested
  - Smoke tests pass: `/api/health` returns 200 OK with database connection validated
  - Production UI loads with "Task Tracker" branding confirmed

## Current Phase
- Phase 8 (Payments/Credits/Escrow) is in progress.

## Recent Decisions
- Brain access is subscription-gated.
- Repo snapshots are used for delivery artifacts.
- Credits top-ups are supported through Stripe checkout.
- Stripe orders now create ledger entries for reconciliation.
- Escrow release tooling added for scheduled execution.

## Blockers
- None at the moment.

## Next Action
- Execute Phase 8 plan in `.planning/phases/phase-8/PLAN.md`.
- Follow the cross-product roadmap in `.planning/MARKETPLACE_TASKTRACKER_PLAN.md` to keep Marketplace private, deployed, and paired with the Task Tracker rollout.
- Finish the Marketplace access checklist (repo permissions + CI/CD secrets) and wire post-deploy smoke tests from the private repo.
