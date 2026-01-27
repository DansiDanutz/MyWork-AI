---
phase: 03
plan: 01
subsystem: data-layer
tags: [database, prisma, server-actions, dal, task-management]
requires: [02-authentication]
provides: [task-crud-operations, task-data-access, task-status-management]
affects: [03-02-ui-components, 03-03-pages, dashboard]
tech-stack:
  added: []
  patterns: [server-actions-crud, dal-caching, ownership-verification]
key-files:
  created:

    - src/app/actions/tasks.ts

  modified:

    - prisma/schema.prisma
    - src/shared/lib/dal.ts

decisions:

  - id: TASK-001

    decision: Use TaskStatus enum instead of string for type safety
    rationale: Prevents invalid status values at database and application level

  - id: TASK-002

    decision: Separate updateTaskStatus from updateTask for optimistic UI
    rationale: Status changes are frequent and benefit from separate action with minimal payload

  - id: TASK-003

    decision: Cascade delete tasks when user is deleted
    rationale: Tasks are meaningless without owner, prevents orphaned records
metrics:
  lines-added: 334
  lines-modified: 30
  duration: 3 minutes
  completed: 2026-01-25
---

# Phase 03 Plan 01: Task Database and Server Actions Summary

**One-liner:** Database schema, CRUD Server Actions, and cached DAL functions for complete task lifecycle management with authentication and analytics.

## What Was Built

Created the foundational data layer for task management with proper authentication, validation, and performance optimization:

1. **Database Schema (Prisma)**
   - Task model with title, description, status, timestamps
   - TaskStatus enum (TODO, IN_PROGRESS, DONE) for type safety
   - User relation with cascade delete
   - Composite indexes for performance (userId+status, userId+createdAt)

2. **Server Actions (src/app/actions/tasks.ts)**
   - `createTask`: Create new tasks with validation
   - `updateTask`: Update title/description with ownership check
   - `updateTaskStatus`: Separate action for status changes (optimistic UI support)
   - `deleteTask`: Delete with ownership verification
   - All actions include authentication, analytics tracking, path revalidation

3. **Data Access Layer (src/shared/lib/dal.ts)**
   - `getTasksByUser`: Fetch all tasks sorted by status and date
   - `getTask`: Get single task with ownership verification
   - `getTaskCounts`: Get counts by status for dashboard stats
   - All functions use React cache() for request deduplication

## Technical Implementation

### Authentication Pattern

Every operation verifies user identity:

```typescript
const user = await getUser()
if (!user) {
  return { success: false, error: 'You must be logged in' }
}

```

### Ownership Verification

All queries scope to authenticated user:

```typescript
const task = await prisma.task.findFirst({
  where: { id: taskId, userId: user.id }
})

```

### Analytics Integration

Non-blocking event tracking:

```typescript
trackEvent({
  type: 'task_created',
  userId: user.id,
  properties: { taskId: task.id, hasDescription: !!description }
})

```

### Performance Optimization

- Composite indexes for common query patterns
- React cache() for request deduplication
- Separate status update action for minimal payload

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

| ID | Decision | Impact |
|----|----------|--------|
| TASK-001 | TaskStatus enum instead of string | Type safety at database and application level |
| TASK-002 | Separate updateTaskStatus action | Enables optimistic UI updates for status changes |
| TASK-003 | Cascade delete on user deletion | Prevents orphaned tasks, maintains referential integrity |

## Key Patterns Established

1. **Server Action CRUD Pattern**
   - Authentication with getUser()
   - Zod validation for input data
   - Ownership verification before mutations
   - Analytics tracking with trackEvent()
   - Path revalidation for cache management
   - Consistent ActionResult return type

2. **DAL Caching Pattern**
   - React cache() wrapper for deduplication
   - Error handling with fallback values
   - Ownership filtering in all queries
   - Type safety with Prisma types

3. **Ownership Model**
   - All operations scoped to authenticated user
   - Explicit userId checks before mutations
   - "Task not found or access denied" for unauthorized access
   - Cascade delete maintains data integrity

## What's Next

This plan provides the data foundation. Next plans will add:

- **03-02**: UI components (TaskCard, TaskList, TaskForm)
- **03-03**: Task pages (list, create, dashboard integration)
- **03-04**: Edit page and full CRUD verification

## Brain-Learnable Patterns

**Pattern: Server Action CRUD with Auth**

```typescript
export async function createTask(formData: FormData) {
  // 1. Verify authentication
  const user = await getUser()
  if (!user) return { success: false, error: 'Not authenticated' }

  // 2. Validate input
  const result = Schema.safeParse(data)
  if (!result.success) return { success: false, error: result.error }

  // 3. Create resource
  const resource = await prisma.model.create({ data: { ...data, userId: user.id } })

  // 4. Track analytics (non-blocking)
  trackEvent({ type: 'resource_created', userId: user.id, properties: {...} })

  // 5. Revalidate paths
  revalidatePath('/resources')

  return { success: true, data: { id: resource.id } }
}

```

**Pattern: DAL with Caching and Ownership**

```typescript
export const getResourcesByUser = cache(async (userId: string) => {
  try {
    return await prisma.resource.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' }
    })
  } catch (error) {
    console.error('Error fetching resources:', error)
    return []
  }
})

```

**Pattern: Enum for Status Management**

```prisma
enum ResourceStatus {
  PENDING
  ACTIVE
  COMPLETE
  @@map("resource_status")
}

model Resource {
  status ResourceStatus @default(PENDING)
  @@index([userId, status]) // Composite index for filtered queries
}

```

## Files Created/Modified

**Created:**

- `src/app/actions/tasks.ts` (234 lines) - Server Actions for task CRUD

**Modified:**

- `prisma/schema.prisma` (+29 lines) - Task model and TaskStatus enum
- `src/shared/lib/dal.ts` (+71 lines) - Task DAL functions with caching

## Commits

| Hash | Message | Files |
|------|---------|-------|
| b129966 | feat(03-01): add Task model and TaskStatus enum to schema | prisma/schema.prisma |
| 6cb94aa | feat(03-01): implement Server Actions for task CRUD | src/app/actions/tasks.ts |
| 0848488 | feat(03-01): add task DAL functions with caching | src/shared/lib/dal.ts |

## Verification Status

All verification criteria met:

- ✅ Task model exists in database with TaskStatus enum
- ✅ Server Actions handle create, read, update, delete with auth
- ✅ DAL provides getTasksByUser, getTask, getTaskCounts with caching
- ✅ All operations verify user ownership
- ✅ Analytics tracking integrated
- ✅ TypeScript compiles successfully
- ✅ Database migration applied

## Next Phase Readiness

**Ready for 03-02 (UI Components):**

- Task CRUD actions available for component integration
- DAL functions ready for data fetching
- Task and TaskStatus types available from Prisma client
- Analytics tracking in place for user interaction monitoring

**Blockers:** None

**Notes:**

- All Server Actions follow established patterns from profile.ts
- Analytics events align with existing types from Phase 6
- Performance optimization via composite indexes and caching
- Ready for UI layer to consume data layer
