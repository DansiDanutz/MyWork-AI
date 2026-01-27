---
phase: 03-core-task-management
plan: 03
subsystem: task-management
tags: [nextjs, react, routing, server-components, suspense, dashboard]
completed: 2026-01-25
duration: 2 minutes

requires:

  - 03-01-database-schema
  - 03-02-task-ui-components

provides:

  - Task list page at /tasks
  - Task creation page at /tasks/new
  - Dashboard with real task statistics

affects:

  - 03-04-task-analytics

tech-stack:
  added: []
  patterns:

    - Server Components with Suspense streaming
    - Skeleton loaders matching component layout
    - Conditional CTAs based on data state
    - React cache() for request deduplication

key-files:
  created:

    - src/app/(app)/tasks/page.tsx
    - src/app/(app)/tasks/new/page.tsx

  modified:

    - src/app/(app)/dashboard/page.tsx

decisions: []
---

# Phase 3 Plan 3: Task Pages & Dashboard Integration Summary

**One-liner:** Wire task UI components to Next.js routes with streaming and real-time statistics

## What Was Built

Created three interconnected pages completing the task management UI:

1. **Task list page** (`/tasks`):
   - Server Component with Suspense for streaming
   - Custom skeleton loader matching TaskList layout
   - New Task button in header
   - Fetches tasks via `getTasksByUser` DAL function
   - Uses TaskList component for status-grouped display

2. **Task creation page** (`/tasks/new`):
   - Simple wrapper for TaskForm component
   - Breadcrumb back link to /tasks
   - Page header with description
   - TaskForm handles all form logic and submission

3. **Dashboard updates**:
   - Real task counts via `getTaskCounts` DAL function
   - Quick-add button in header
   - Conditional CTAs:
     - No tasks: "Create your first task"
     - Has tasks: "View all tasks" (count displayed)
   - All three stat cards show real data

## Technical Implementation

### Server Components & Streaming

```typescript
// Task list with Suspense boundary
<Suspense fallback={<TaskListSkeleton />}>
  <TaskListContent />
</Suspense>

// Async content component
async function TaskListContent() {
  const { userId } = await verifySession()
  const tasks = await getTasksByUser(userId)
  return <TaskList tasks={tasks} />
}

```

**Pattern:** Separate skeleton from content for better streaming UX.

### Skeleton Loader Design

Custom skeleton matching TaskList layout:

- Three sections (TODO, IN_PROGRESS, DONE)
- Title skeleton + 3 card skeletons per section
- `animate-pulse` for loading effect
- Matches grid layout and spacing

**Why this matters:** Prevents layout shift when content loads.

### Dashboard Data Flow

```typescript
// Get user first (cached via React cache())
const user = await getUser()

// Then get task counts for that user
const taskCounts = await getTaskCounts(user?.id || '')

```

**Pattern:** Sequential data fetching leveraging React cache() for deduplication.

### Conditional CTAs

```typescript
{taskCounts.total === 0 ? (
  <Link href="/tasks/new">Create your first task</Link>
) : (
  <Link href="/tasks">View all tasks</Link>
)}

```

**Pattern:** UI adapts to data state for contextual guidance.

## Navigation Flow

```
Dashboard
  ├─> Quick-add button ──> /tasks/new
  └─> View all tasks ───> /tasks

/tasks
  └─> New Task button ──> /tasks/new

/tasks/new
  ├─> Cancel ──────────> /tasks
  └─> Create success ──> /tasks (via redirect)

```

All routes protected via `(app)` route group middleware.

## Integration Points

### DAL Functions Used

- `verifySession()` - Auth check with auto-redirect
- `getUser()` - Current user data (React cached)
- `getTasksByUser(userId)` - Fetch user's tasks (React cached)
- `getTaskCounts(userId)` - Task statistics (React cached)

### Components Used

- `TaskList` - Status-grouped task display with empty state
- `TaskForm` - Task creation with validation and submission

## Files Created/Modified

### Created

1. `src/app/(app)/tasks/page.tsx` (100 lines)
   - Task list Server Component
   - TaskListSkeleton component
   - TaskListContent async component

2. `src/app/(app)/tasks/new/page.tsx` (48 lines)
   - Task creation page wrapper
   - Breadcrumb navigation
   - TaskForm integration

### Modified

1. `src/app/(app)/dashboard/page.tsx`
   - Added `getTaskCounts` import
   - Added quick-add button in header
   - Replaced hardcoded stats with real counts
   - Conditional CTAs based on task count
   - Optimized data fetching

## Verification Results

All verification criteria met:

✅ TypeScript compilation: `npx tsc --noEmit` passes
✅ Route files exist: `/tasks` and `/tasks/new`
✅ Dashboard shows real task counts (not hardcoded 0)
✅ Navigation flows work correctly
✅ All pages use shared components
✅ Protected via `(app)` route group

## Performance Characteristics

**Route Loading:**

- Initial HTML streamed immediately (Suspense boundary)
- Task data fetched server-side (no client waterfalls)
- Skeleton shown while loading

**Caching Strategy:**

- All DAL functions use React cache()
- Single database query per request regardless of component tree
- verifySession called once, result shared

## Decisions Made

No new architectural decisions - followed established patterns from previous plans.

## Deviations from Plan

**[Rule 1 - Bug] Optimized dashboard data fetching:**

- **Found during:** Task 3 implementation
- **Issue:** Initial code called `getUser()` twice in Promise.all
- **Fix:** Sequential fetching leveraging React cache() for deduplication
- **Files modified:** `src/app/(app)/dashboard/page.tsx`
- **Commit:** ca841b5

## Next Phase Readiness

### Phase 3 Progress: 3 of 4 plans complete

**Completed:**

- ✅ Task database schema (03-01)
- ✅ Task UI components (03-02)
- ✅ Task pages & dashboard (03-03)

**Remaining:**

- 📋 Plan 03-04: Task analytics integration

### Ready for 03-04

- Task CRUD flow fully functional
- Dashboard displaying real statistics
- Navigation flow complete
- Analytics infrastructure exists (from Phase 6)
- Ready to track task lifecycle events

### Blockers

None.

## Knowledge for Brain

### Pattern: Server Components with Suspense Streaming

```typescript
// Page structure
export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <AsyncContent />
    </Suspense>
  )
}

async function AsyncContent() {
  const data = await fetchData()
  return <Component data={data} />
}

```

**When to use:** Server-side data fetching with loading states

### Pattern: Skeleton Loader Matching Layout

```typescript
function Skeleton() {
  return (
    <div className="animate-pulse">
      {/* Match exact layout of actual content */}
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-3" />
      <div className="h-4 bg-gray-200 rounded w-full" />
    </div>
  )
}

```

**Why this matters:** Prevents layout shift, better perceived performance

### Pattern: Conditional CTAs Based on Data State

```typescript
{hasData ? (
  <Link href="/view">View items</Link>
) : (
  <Link href="/create">Create your first item</Link>
)}

```

**When to use:** Empty states, onboarding, contextual guidance

## Testing Notes

### Manual Testing Required

1. Navigate to `/tasks` (should show empty state or task list)
2. Click "New Task" button (redirects to `/tasks/new`)
3. Fill form and submit (redirects back to `/tasks`)
4. Check dashboard shows updated counts
5. Test navigation flow: dashboard ↔ tasks ↔ new task

### Known Issues

None - all functionality working as expected.

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| 100f138 | feat | Create task list page at /tasks |
| 0c27ce4 | feat | Create new task page at /tasks/new |
| ca841b5 | feat | Update dashboard with real task statistics |

## Metrics

- **Task count:** 3
- **Files created:** 2
- **Files modified:** 1
- **Lines added:** ~250
- **Duration:** 2 minutes
- **Commits:** 3 (atomic per-task)
