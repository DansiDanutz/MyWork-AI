---
phase: 07
plan: 01
type: execute
subsystem: ui-performance
tags: [loading-states, skeleton-screens, nextjs, ux, performance]

requires:

  - phase: 05

```yaml
deliverable: File attachments UI components

```yaml

  - phase: 04

```yaml
deliverable: Task management UI patterns

```

provides:

  - Route-level loading states for all main routes
  - Reusable skeleton components matching actual UI structure
  - Immediate visual feedback during navigation
  - Seamless page transitions without blank screens

affects:

  - future: Dashboard Analytics

```yaml
why: Loading states provide baseline for progressive enhancement

```yaml

  - future: Error Boundaries

```yaml
why: Loading/error states form complete resilience layer

```

tech-stack:
  added: []
  patterns:

```markdown

- Route-level loading.tsx files for Next.js App Router
- Skeleton screen pattern matching actual layouts
- Server Component loading states (no 'use client')
- Tailwind animate-pulse for loading animations

```yaml

key-files:
  created:

```markdown

- src/shared/components/skeletons/TaskCardSkeleton.tsx
- src/shared/components/skeletons/TaskListSkeleton.tsx
- src/shared/components/skeletons/index.ts
- src/app/(app)/loading.tsx
- src/app/(app)/dashboard/loading.tsx
- src/app/(app)/tasks/loading.tsx
- src/app/(app)/tasks/[id]/edit/loading.tsx
- src/app/(app)/tasks/new/loading.tsx
- src/app/(app)/settings/loading.tsx
- src/app/(app)/settings/profile/loading.tsx

```

  modified: []

decisions:

  - id: LOADING-001

```yaml
date: 2026-01-26
choice: Route-level loading.tsx over component-level Suspense boundaries
why: Next.js automatically shows loading.tsx during navigation without
explicit Suspense wrappers
impact: Simpler mental model, automatic behavior for all routes
alternatives: Component-level Suspense boundaries (more granular but more
complex)

```yaml

  - id: SKELETON-001

```yaml
date: 2026-01-26
choice: Match actual layout structure in skeleton screens
why: Provides visual continuity and reduces layout shift during hydration
impact: Better perceived performance, professional UX
alternatives: Generic spinners (faster to build but less polished)

```

metrics:
  duration: 3 minutes
  tasks: 2
  commits: 2
  files_changed: 10
  tests_added: 0
  completed: 2026-01-26
---

# Phase 07 Plan 01: Route Loading States Summary

**One-liner:** Next.js route-level loading.tsx files with skeleton screens
matching actual layouts for immediate navigation feedback

## What Was Built

Created comprehensive loading state system for all main application routes:

### Reusable Skeleton Components

- **TaskCardSkeleton**: Matches TaskCard structure (status badge, title, tags,

  description, date, file indicator, actions)

- **TaskListSkeleton**: 3 sections with 3 cards each in responsive grid layout
- **Export barrel**: Clean imports from `@/shared/components/skeletons`

### Route Loading Files

1. **App Shell** (`(app)/loading.tsx`): Generic centered spinner for app-level

loading

2. **Dashboard** (`dashboard/loading.tsx`): Header + 3-stat grid + quick actions
3. **Tasks Page** (`tasks/loading.tsx`): Search bar + filter sidebar + 3-section

task list

4. **Task Edit** (`tasks/[id]/edit/loading.tsx`): Breadcrumbs + form fields

(title, description, status, tags, files)

5. **Task New** (`tasks/new/loading.tsx`): Back link + page header + form fields
6. **Settings** (`settings/loading.tsx`): Navigation sidebar + content area
7. **Profile** (`settings/profile/loading.tsx`): Avatar + name + bio fields

## Key Implementation Details

### Pattern: Route-Level Loading

```tsx

// Next.js automatically shows loading.tsx during navigation
// No explicit Suspense wrappers needed
export default function Loading() {
  return <div className="...">skeleton content</div>
}

```markdown

### Skeleton Fidelity

Each loading skeleton matches its corresponding page:

- Same grid layouts (`md:grid-cols-2 lg:grid-cols-3`)
- Same component structure (headers, forms, cards)
- Same spacing and padding
- Dark mode support via Tailwind dark: variants

### Animation

- Used Tailwind's `animate-pulse` for subtle loading animation
- Gray-200 (light) / Gray-700 (dark) backgrounds for skeleton elements
- Consistent animation timing across all skeletons

## Decisions Made

### LOADING-001: Route-Level vs Component-Level

**Decision:** Use Next.js route-level loading.tsx files

**Reasoning:**

- Automatic behavior during navigation
- No explicit Suspense boundaries needed
- Simpler mental model for developers
- Covers entire route segment

**Alternative Considered:** Component-level Suspense boundaries

- Pros: More granular control, can show partial content
- Cons: More complex, requires explicit wrappers everywhere
- Why rejected: For validation project scale, route-level sufficient

### SKELETON-001: Layout Matching

**Decision:** Skeleton screens match actual layout structure

**Reasoning:**

- Reduces Cumulative Layout Shift (CLS)
- Provides visual continuity
- Professional perceived performance
- Users know what's loading

**Alternative Considered:** Generic spinners

- Pros: Faster to implement
- Cons: Looks unfinished, causes layout shift
- Why rejected: Doesn't meet quality bar for production validation

## Task Breakdown

### Task 1: Reusable Skeleton Components

**Files:** TaskCardSkeleton.tsx, TaskListSkeleton.tsx, index.ts
**Commit:** 294430b

Created reusable building blocks:

- TaskCardSkeleton matches TaskCard exactly (status, title, tags, description,

  actions)

- TaskListSkeleton uses TaskCardSkeleton to render 3 sections
- Export barrel for clean imports

### Task 2: Route-Level Loading Files

**Files:** 7 loading.tsx files across app routes
**Commit:** 5c6f762

Implemented loading states for:

- App shell (generic spinner)
- Dashboard (stats grid)
- Tasks page (search + filters + list)
- Task edit/new (forms)
- Settings pages (sidebar + content)

## Testing Performed

### Manual Verification

✅ TypeScript compilation passes (no errors)
✅ All 7 loading.tsx files exist in correct locations
✅ All files export default Loading() function
✅ Skeleton components use proper Tailwind classes
✅ Dark mode classes present on all skeletons

### What Would Be Tested in Browser

(Manual testing recommended but not required for this plan):

- Navigate between routes → loading states appear immediately
- Skeleton layouts match actual pages
- No blank screens during navigation
- Smooth transitions from loading to content
- Dark mode toggle → skeletons adapt

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**This plan completes:** Loading state foundation

**Next steps (Phase 07 remaining plans):**

1. **07-02**: React.lazy() for code splitting dashboard analytics
2. **07-03**: Optimize images with Next.js Image component
3. **07-04**: Error boundaries for graceful error handling
4. **07-05**: Performance monitoring and optimization

**Blockers/Concerns:** None

**Dependencies satisfied:** ✅ All file attachment UI components from Phase 05
exist

## Files Changed

### Created (10 files)

- `src/shared/components/skeletons/TaskCardSkeleton.tsx` (52 lines)
- `src/shared/components/skeletons/TaskListSkeleton.tsx` (28 lines)
- `src/shared/components/skeletons/index.ts` (7 lines)
- `src/app/(app)/loading.tsx` (17 lines)
- `src/app/(app)/dashboard/loading.tsx` (49 lines)
- `src/app/(app)/tasks/loading.tsx` (70 lines)
- `src/app/(app)/tasks/[id]/edit/loading.tsx` (68 lines)
- `src/app/(app)/tasks/new/loading.tsx` (58 lines)
- `src/app/(app)/settings/loading.tsx` (40 lines)
- `src/app/(app)/settings/profile/loading.tsx` (40 lines)

### Modified

None

## Commits

1. **294430b** - feat(07-01): create reusable skeleton components
2. **5c6f762** - feat(07-01): add loading.tsx files for all main routes

## Lessons Learned

### What Worked Well

- **Skeleton pattern**: Matching actual layouts provides professional UX
- **Route-level loading**: Next.js automatic behavior simplifies implementation
- **Reusable components**: TaskCardSkeleton DRY principle applied
- **TypeScript**: Caught no errors (clean implementation)

### Patterns to Extract for Brain

1. **Route-level loading.tsx pattern** for Next.js App Router
2. **Skeleton screen matching layout structure** for perceived performance
3. **Tailwind animate-pulse** for loading animations
4. **Dark mode skeleton colors** (gray-200/gray-700)

### Future Improvements

- Could add Suspense boundaries within pages for more granular loading
- Could measure actual loading times and CLS metrics
- Could add loading progress indicators for long operations
- Could implement skeleton variations based on viewport size

## Production Readiness

### ✅ Complete

- Route-level loading states for all main routes
- Skeleton screens match actual layouts
- Dark mode support
- TypeScript compilation passes

### 🔄 Deferred (Future Plans)

- Component-level Suspense boundaries (if needed for granularity)
- Loading progress indicators (Phase 07 remaining plans)
- Performance metrics collection (Phase 07 remaining plans)

### 📊 Quality Metrics

- **Code Quality:** Clean, no TypeScript errors
- **UX Quality:** Professional skeleton screens
- **Performance:** Immediate feedback on navigation
- **Maintainability:** Reusable skeleton components

---

**Status:** ✅ Complete
**Duration:** 3 minutes
**Next:** Plan 07-02 (Code splitting)
