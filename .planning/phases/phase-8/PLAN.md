# Phase 8 — Payments, Credits, Escrow

Date: 2026-01-26
Owner: Dansi (Product) + Codex (Implementation)

## Objective

Unify payments, credits, and escrow so every order is consistent, auditable, and
reversible.

## Scope

- Credits ledger as single source of truth
- Stripe orders and credit orders share the same lifecycle
- Escrow holds and releases are automated
- Refunds + reversals fully reconcile

## Workstreams & Tasks

### P8-A — Ledger & Order Reconciliation

1. Add ledger entries for Stripe purchases
2. Add refund/reversal ledger entries
3. Ensure orders always reconcile to ledger totals

### P8-B — Escrow Automation

1. Scheduled job: release escrow after `ESCROW_DAYS`
2. Update order + ledger status
3. Notify seller on release

### P8-C — Refund & Dispute Flow

1. Refund triggers ledger reversal
2. Credit refunds handled consistently
3. Audit log for manual admin adjustments

### P8-D — Config Validation + Reliability

1. Startup config checks for required env vars
2. Runtime health checks + alerts for failures

## Acceptance Criteria

- All orders (Stripe + credits) have matching ledger entries
- Escrow releases automatically and updates ledger + order
- Refunds update ledger and order with no manual fixes
- Production startup fails fast with clear config errors

## Risks

- Partial implementation can desync ledger and orders.
- Escrow jobs can double-release without idempotency.

## Mitigations

- Idempotent ledger entries using order IDs.
- Locking or “already released” checks in escrow job.

## Deliverables

- Code + migrations
- Test plan / smoke checklist
- Updated docs
