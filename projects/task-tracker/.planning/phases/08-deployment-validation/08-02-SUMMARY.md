---
phase: 08-deployment-validation
plan: 02
subsystem: ui
tags: [feedback, analytics, user-input, client-component, server-actions]

# Dependency graph

requires:

  - phase: 06-analytics-privacy

    provides: Analytics infrastructure with trackEvent function and analytics_events table
provides:

  - Floating feedback widget accessible on all pages
  - Feedback Server Action storing feedback via analytics
  - Anonymous and authenticated feedback support

affects: [08-03-documentation, 08-04-deployment-prep]

# Tech tracking

tech-stack:
  added: []
  patterns:

    - Feedback widget with slide-up form UX pattern
    - Reuse analytics infrastructure for new event types
    - Fixed-position overlay components for global features

key-files:
  created:

    - src/shared/actions/feedback.ts
    - src/shared/components/FeedbackWidget.tsx

  modified:

    - src/app/layout.tsx
    - src/shared/lib/analytics/types.ts
    - src/shared/components/index.ts

key-decisions:

  - "Allow anonymous feedback (userId nullable) for validation user input"
  - "Store feedback via analytics infrastructure (feedback_submitted event)"
  - "500 character limit balances detail with brevity"
  - "Auto-close form after successful submission for clean UX"

patterns-established:

  - "Floating widget pattern: fixed bottom-right, expands on click"
  - "Reuse analytics for feedback: adds new event type to discriminated union"
  - "Form validation client-side + server-side for UX and security"

# Metrics

duration: 2min
completed: 2026-01-26
---

# Phase 8 Plan 02: Feedback Widget Summary

**Floating feedback widget with type selector (bug/idea/other) storing feedback via analytics_events table**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-26T05:51:08Z
- **Completed:** 2026-01-26T05:53:26Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- In-app feedback collection without external tools (Hotjar, Canny, etc.)
- Anonymous and authenticated feedback support for maximum capture
- Feedback stored in analytics_events for later review and validation
- Zero-friction UX: floating button accessible from any page

## Task Commits

Each task was committed atomically:

1. **Task 1: Create feedback Server Action with analytics tracking** - `d3fd8a3` (feat)
2. **Task 2: Create FeedbackWidget component** - `0028fad` (feat)
3. **Task 3: Integrate FeedbackWidget into root layout** - `4db3e89` (feat)

**Additional fix:** `e97afd6` (fix: suppressHydrationWarning in global-error.tsx)

## Files Created/Modified

- `src/shared/actions/feedback.ts` - Server Action to submit feedback via trackEvent
- `src/shared/components/FeedbackWidget.tsx` - Floating feedback button and form component
- `src/shared/lib/analytics/types.ts` - Added FeedbackSubmittedEventSchema
- `src/app/layout.tsx` - Added FeedbackWidget to root layout
- `src/shared/components/index.ts` - Exported FeedbackWidget
- `src/app/global-error.tsx` - Added suppressHydrationWarning attributes

## Decisions Made

**FEEDBACK-001** (2026-01-26): Allow anonymous feedback (userId nullable)

- **Rationale:** Maximize feedback capture during validation phase - users may not be logged in or may prefer anonymity
- **Impact:** Analytics event accepts null userId, Server Action doesn't require session

**FEEDBACK-002** (2026-01-26): Store feedback via analytics infrastructure

- **Rationale:** Reuse existing trackEvent function and analytics_events table rather than creating separate feedback table
- **Impact:** Feedback is just another analytics event (type: 'feedback_submitted') - can be queried alongside other analytics

**FEEDBACK-003** (2026-01-26): 500 character limit for feedback text

- **Rationale:** Balances detail (enough to describe an issue or idea) with brevity (keeps feedback focused)
- **Impact:** Client-side and server-side validation enforces limit, character counter visible to users

**UX-002** (2026-01-26): Auto-close form after successful submission

- **Rationale:** Clean UX - success message shows briefly (3 seconds) then form closes automatically
- **Impact:** Reduces clutter, indicates completion, ready for next feedback submission

## Deviations from Plan

**1. [Rule 1 - Bug] Added suppressHydrationWarning to global-error.tsx**

- **Found during:** Task 3 (dev server startup)
- **Issue:** Next.js App Router requires suppressHydrationWarning on html/body tags in global-error.tsx to prevent hydration warnings
- **Fix:** Added suppressHydrationWarning to html and body tags, updated comments
- **Files modified:** src/app/global-error.tsx
- **Verification:** Dev server starts without hydration warnings
- **Committed in:** e97afd6 (fix commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Minor Next.js best practice fix. No scope creep.

## Issues Encountered

None - all tasks executed as planned.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Feedback widget ready for production validation
- Analytics infrastructure proven reusable for new event types
- User can now submit feedback from any page in the app
- Feedback data stored in analytics_events table (query with type = 'feedback_submitted')

**Blockers:** None

**Validation checklist for Phase 8 completion:**

- [x] Feedback button visible on all pages
- [x] Form allows type selection (bug/idea/other)
- [x] Submission stores feedback via analytics
- [x] Anonymous and authenticated feedback both work
- [ ] Production deployment (08-03, 08-04 remaining)

---
*Phase: 08-deployment-validation*
*Completed: 2026-01-26*
