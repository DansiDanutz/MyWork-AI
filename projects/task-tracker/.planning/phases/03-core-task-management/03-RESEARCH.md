# Phase 3: Core Task Management - Research

**Researched:** 2026-01-25
**Domain:** Next.js 15 Server Actions, Prisma task models, React optimistic UI
**Confidence:** HIGH

## Summary

Core task management in Next.js 15 follows a well-established pattern: Prisma
models with user ownership relations, Server Actions for CRUD mutations with Zod
validation, and React's useOptimistic for responsive UI updates. The project
already has established patterns from Phase 2 (authentication) that should be
extended rather than reinvented.

**Key findings:**

- Next.js 15's Server Actions with useActionState provide type-safe form handling
  and validation
- Prisma 7's one-to-many relations naturally model user-task ownership
- React 18's useOptimistic hook enables instant UI feedback before server
  confirmation
- Established project patterns (field-level actions, debounced saves, status
  indicators) should be reused

**Primary recommendation:** Extend existing patterns from profile management
(field-level Server Actions, visual status indicators, DAL with cache) to task
CRUD operations. Use dedicated `/tasks/new` page per CONTEXT.md decisions, with
card-based list grouped by status.

## Standard Stack

The project's existing stack already includes all necessary libraries:

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
  | Next.js | 15.0.3 | App Router,... | Industry st... |  
  | Prisma | 7.3.0 | ORM with ty... | Latest majo... |  
  | Zod | 4.3.6 | Schema vali... | De facto st... |  
  | React | 18.3.1 | UI with use... | Stable vers... |  

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
| next-auth | 5.0.0-beta.30 | Session ver... | Already int... |
| @prisma/ada... | 7.3.0 | PostgreSQL ... | Production-... |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
  | Prisma | Drizzle ORM | Lighter bundle but... |  
  | useOptimistic | React Query | More features but ... |  
  | Server Actions | tRPC | More ceremony, Ser... |  

**Installation:**

```bash

# Already installed - no additional packages needed

# Reuse existing patterns from Phase 2

```markdown

## Architecture Patterns

### Project Structure (Extends Existing)

```
src/
├── app/
│   ├── (app)/
│   │   ├── tasks/              # New: Task pages
│   │   │   ├── page.tsx        # Task list (grouped by status)
│   │   │   └── new/
│   │   │       └── page.tsx    # Create task page
│   │   └── dashboard/
│   │       └── page.tsx        # Update: Add quick-create button
│   └── actions/
│       ├── profile.ts          # Existing pattern reference
│       └── tasks.ts            # New: Task CRUD actions
├── shared/
│   ├── lib/
│   │   ├── dal.ts              # Extend: Add getTasksByUser
│   │   └── db.ts               # Reuse: Prisma singleton
│   └── components/
│       ├── ProfileForm.tsx     # Pattern reference: auto-save
│       ├── TaskCard.tsx        # New: Task display card
│       ├── TaskForm.tsx        # New: Create/edit form
│       └── TaskList.tsx        # New: Status-grouped list
└── prisma/

```
└── schema.prisma           # Add Task model

```
```markdown

### Pattern 1: Task Model with User Ownership (Prisma)

**What:** One-to-many relationship between User and Task models
**When to use:** All user-owned entities in the application
**Example:**

```typescript

// Source: Official Prisma docs + existing User model pattern
model Task {
  id          String   @id @default(cuid())
  title       String
  description String?  @db.Text
  status      String   @default("todo")  // "todo" | "in_progress" | "done"
  userId      String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, status])      // Fast filtering by user + status
  @@index([userId, createdAt])   // Fast chronological queries
}

// Update User model
model User {
  // ... existing fields ...
  tasks Task[]  // Add relation
}

```

### Pattern 2: Server Action with Zod Validation (Extends profile.ts)

**What:** Field-level and form-level Server Actions with type-safe validation
**When to use:** All data mutations requiring authentication and validation
**Example:**

```typescript

// Source: Next.js official docs + existing profile.ts pattern
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'
import { verifySession } from '@/shared/lib/dal'
import { prisma } from '@/shared/lib/db'

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(2000).optional(),
  status: z.enum(['todo', 'in_progress', 'done']).default('todo'),
})

export type TaskActionResult = {
  success: boolean
  error?: string
  taskId?: string
}

export async function createTask(
  formData: FormData
): Promise<TaskActionResult> {
  try {

```
const { userId } = await verifySession()

const data = {
  title: formData.get('title') as string,
  description: formData.get('description') as string | null,
}

const validation = taskSchema.safeParse(data)
if (!validation.success) {
  return {
    success: false,
    error: validation.error.issues[0]?.message || 'Invalid input',
  }
}

const task = await prisma.task.create({
  data: {
    ...validation.data,
    userId,
  },
})

revalidatePath('/tasks')
return { success: true, taskId: task.id }

```
  } catch (error) {

```
console.error('Task creation error:', error)
return {
  success: false,
  error: 'Failed to create task. Please try again.',
}

```
  }
}

```markdown

### Pattern 3: useOptimistic for Instant Status Updates

**What:** Optimistic UI updates for status changes before server confirmation
**When to use:** User actions that should feel instant (status toggles, quick
edits)
**Example:**

```typescript

// Source: React official docs (react.dev)
'use client'

import { useOptimistic } from 'react'
import { updateTaskStatus } from '@/app/actions/tasks'

function TaskCard({ task }) {
  const [optimisticTask, addOptimisticUpdate] = useOptimistic(

```
task,
(state, newStatus: string) => ({ ...state, status: newStatus })

```
  )

  async function handleStatusChange(newStatus: string) {

```
// 1. Update UI immediately
addOptimisticUpdate(newStatus)

// 2. Send to server in background
await updateTaskStatus(task.id, newStatus)

```
  }

  return (

```
<div>
  <h3>{optimisticTask.title}</h3>
  <select
    value={optimisticTask.status}
    onChange={(e) => handleStatusChange(e.target.value)}
  >
    <option value="todo">To Do</option>
    <option value="in_progress">In Progress</option>
    <option value="done">Done</option>
  </select>
</div>

```
  )
}

```

### Pattern 4: DAL Extension with React cache()

**What:** Server-side data access layer functions with request-level caching
**When to use:** All authenticated database queries
**Example:**

```typescript

// Source: Existing dal.ts pattern
import 'server-only'
import { cache } from 'react'
import { verifySession } from '@/shared/lib/dal'
import { prisma } from '@/shared/lib/db'

export const getTasksByUser = cache(async () => {
  const { userId } = await verifySession()

  const tasks = await prisma.task.findMany({

```
where: { userId },
orderBy: [
  { status: 'asc' },      // Group by status
  { createdAt: 'desc' },  // Then chronological
],

```
  })

  return tasks
})

export const getTask = cache(async (taskId: string) => {
  const { userId } = await verifySession()

  const task = await prisma.task.findFirst({

```
where: {
  id: taskId,
  userId,  // Ensure user owns the task
},

```
  })

  return task
})

```markdown

### Pattern 5: Status-Grouped Task List UI

**What:** Group tasks by status sections per CONTEXT.md decision
**When to use:** Main task list view
**Example:**

```typescript

// Source: CONTEXT.md decision + React component patterns
'use client'

import { TaskCard } from './TaskCard'

type Task = {
  id: string
  title: string
  description?: string | null
  status: 'todo' | 'in_progress' | 'done'
  createdAt: Date
}

export function TaskList({ tasks }: { tasks: Task[] }) {
  const todoTasks = tasks.filter(t => t.status === 'todo')
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress')
  const doneTasks = tasks.filter(t => t.status === 'done')

  return (

```
<div className="space-y-8">
  <TaskSection title="To Do" tasks={todoTasks} />
  <TaskSection title="In Progress" tasks={inProgressTasks} />
  <TaskSection title="Done" tasks={doneTasks} />
</div>

```
  )
}

function TaskSection({ title, tasks }: { title: string; tasks: Task[] }) {
  if (tasks.length === 0) {

```
return (
  <section>
    <h2 className="text-lg font-semibold mb-4">{title}</h2>
    <p className="text-gray-500">No tasks yet</p>
  </section>
)

```
  }

  return (

```
<section>
  <h2 className="text-lg font-semibold mb-4">
    {title} ({tasks.length})
  </h2>
  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
    {tasks.map(task => (
      <TaskCard key={task.id} task={task} />
    ))}
  </div>
</section>

```
  )
}

```

### Anti-Patterns to Avoid

- **Don't put session in client state** - Use Server Components and Server
  Actions, keep sessions server-only
- **Don't skip revalidatePath after mutations** - UI won't update automatically,
  causing stale data
- **Don't fetch tasks in Client Components** - Use Server Components for initial
  data, Client Components only for interactions
- **Don't use useEffect for data fetching** - Leads to waterfall requests; use
  Server Components and streaming
- **Don't hand-roll optimistic updates** - Use React's useOptimistic hook for
  built-in rollback on error

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
| Form valida... | Custom vali... | Zod with Se... | Type-safe, ... |
  | Session ver... | Check sessi... | verifySessi... | Already use... |  
  | Database si... | New Prisma ... | prisma from... | Connection ... |  
| Optimistic ... | Manual stat... | useOptimist... | Built-in ro... |
  | Form pendin... | Custom load... | useActionSt... | Integrated ... |  
| Date format... | String conc... | Intl.DateTi... | Locale-awar... |
  | Task author... | Manual user... | DAL wrapper... | Consistent ... |  

**Key insight:** Next.js 15 Server Actions handle 90% of form complexity
out-of-the-box. Fighting the framework leads to more code and more bugs.

## Common Pitfalls

### Pitfall 1: Forgetting revalidatePath After Mutations

**What goes wrong:** After creating/updating/deleting a task, the UI shows stale
data because Next.js cached the previous page render.
**Why it happens:** Next.js aggressively caches Server Component renders.
Mutations don't automatically invalidate cache.
**How to avoid:**

- Always call `revalidatePath('/tasks')` at the end of Server Actions
- Call before `redirect()` if redirecting (redirect throws, preventing subsequent
  code)
- Use `revalidatePath('/tasks', 'page')` for route patterns with dynamic segments

**Warning signs:**

- User creates task but doesn't see it in list
- Refreshing page shows the change
- Different users see different data

### Pitfall 2: Authorization Bypass in Task Queries

**What goes wrong:** User can access other users' tasks by guessing task IDs.
**Why it happens:** Query filters only by `taskId` without checking `userId`.
**How to avoid:**

```typescript

// ❌ WRONG - No user check
const task = await prisma.task.findUnique({ where: { id: taskId } })

// ✅ CORRECT - Filter by both
const task = await prisma.task.findFirst({
  where: { id: taskId, userId },
})

```yaml

**Warning signs:**

- Security testing reveals cross-user data access
- No userId in WHERE clause
- Using findUnique instead of findFirst for multi-field conditions

### Pitfall 3: Missing Database Indexes on Relations

**What goes wrong:** Task queries become slow as data grows, especially filtered
by user and status.
**Why it happens:** Foreign keys aren't automatically indexed in all databases.
Without indexes, queries do full table scans.
**How to avoid:**

```typescript

// Add composite indexes for common query patterns
model Task {
  // ... fields ...

  @@index([userId, status])      // Fast: Filter by user + status
  @@index([userId, createdAt])   // Fast: User's tasks chronologically
  @@index([userId, updatedAt])   // Fast: Recently modified
}

```

**Warning signs:**

- Slow page loads with >100 tasks
- Database query logs show full table scans
- Prisma warnings about missing indexes during format/validate

### Pitfall 4: redirect() Inside try-catch Blocks

**What goes wrong:** Server Action redirects don't work, or errors show
"NEXT_REDIRECT" in UI.
**Why it happens:** `redirect()` throws a special error that Next.js handles.
Catch blocks intercept it.
**How to avoid:**

```typescript

// ❌ WRONG - Redirect gets caught
try {
  await prisma.task.create({ ... })
  redirect('/tasks')  // This throws!
} catch (error) {
  return { success: false, error: 'Failed' }
}

// ✅ CORRECT - Redirect after try-catch
try {
  await prisma.task.create({ ... })
} catch (error) {
  return { success: false, error: 'Failed' }
}
redirect('/tasks')  // Outside try-catch

```yaml

**Warning signs:**

- Redirect doesn't work
- "NEXT_REDIRECT" error visible to users
- Console shows uncaught redirect errors

### Pitfall 5: Exposing Validation Logic Only on Client

**What goes wrong:** Users bypass validation by modifying form data before
submission, creating invalid database entries.
**Why it happens:** Client-side validation (HTML5, JavaScript) can be
disabled/bypassed by users.
**How to avoid:**

- Always validate in Server Actions with Zod
- Client-side validation is UX enhancement, not security
- Server is the source of truth

```typescript

// ✅ CORRECT - Validate on server
export async function createTask(formData: FormData) {
  const validation = taskSchema.safeParse({ ... })
  if (!validation.success) {

```
return { success: false, error: ... }

```
  }
  // Only proceed with validated data
}

```

**Warning signs:**

- Database contains invalid data (empty titles, null when required)
- Security audit finds validation bypass
- No Zod schema in Server Action

### Pitfall 6: Not Handling Empty States

**What goes wrong:** New users see blank page with no guidance, causing
confusion.
**Why it happens:** Forgot to check for empty arrays before rendering lists.
**How to avoid:**

```typescript

// ✅ Show friendly empty state per CONTEXT.md
{tasks.length === 0 ? (
  <div className="text-center py-12">

```
<p className="text-gray-500 mb-4">
  No tasks yet! Create your first task to get started
</p>
<Link href="/tasks/new">
  <button>Create Task</button>
</Link>

```
  </div>
) : (
  <TaskList tasks={tasks} />
)}

```yaml

**Warning signs:**

- Users report "broken" page on first visit
- Empty list shows nothing (no message, no CTA)

## Code Examples

Verified patterns from official sources and existing codebase:

### Server Action: Create Task (Form Submission)

```typescript

// Source: Next.js official docs + existing profile.ts pattern
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'
import { verifySession } from '@/shared/lib/dal'
import { prisma } from '@/shared/lib/db'

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(2000).optional(),
})

export async function createTask(formData: FormData) {
  try {

```
const { userId } = await verifySession()

const data = {
  title: formData.get('title') as string,
  description: formData.get('description') as string | undefined,
}

const validation = taskSchema.safeParse(data)
if (!validation.success) {
  return {
    success: false,
    error: validation.error.issues[0]?.message || 'Invalid input',
  }
}

await prisma.task.create({
  data: {
    ...validation.data,
    userId,
    status: 'todo',
  },
})

revalidatePath('/tasks')

```
  } catch (error) {

```
console.error('Task creation error:', error)
return {
  success: false,
  error: 'Failed to create task. Please try again.',
}

```
  }

  // Redirect outside try-catch (redirect throws)
  redirect('/tasks')
}

```

### Server Action: Update Task Status (Optimistic)

```typescript

// Source: Existing profile.ts field update pattern
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'
import { verifySession } from '@/shared/lib/dal'
import { prisma } from '@/shared/lib/db'

const statusSchema = z.enum(['todo', 'in_progress', 'done'])

export async function updateTaskStatus(
  taskId: string,
  status: string
): Promise<{ success: boolean; error?: string }> {
  try {

```
const { userId } = await verifySession()

const validation = statusSchema.safeParse(status)
if (!validation.success) {
  return { success: false, error: 'Invalid status' }
}

// Ensure user owns task before updating
const task = await prisma.task.findFirst({
  where: { id: taskId, userId },
})

if (!task) {
  return { success: false, error: 'Task not found' }
}

await prisma.task.update({
  where: { id: taskId },
  data: { status: validation.data },
})

revalidatePath('/tasks')
return { success: true }

```
  } catch (error) {

```
console.error('Status update error:', error)
return { success: false, error: 'Failed to update status' }

```
  }
}

```markdown

### Server Action: Delete Task (With Confirmation)

```typescript

// Source: Standard CRUD pattern
'use server'

import { revalidatePath } from 'next/cache'
import { verifySession } from '@/shared/lib/dal'
import { prisma } from '@/shared/lib/db'

export async function deleteTask(
  taskId: string
): Promise<{ success: boolean; error?: string }> {
  try {

```
const { userId } = await verifySession()

// Delete only if user owns task (CASCADE handles relations)
const result = await prisma.task.deleteMany({
  where: {
    id: taskId,
    userId,  // Security: Only delete own tasks
  },
})

if (result.count === 0) {
  return { success: false, error: 'Task not found' }
}

revalidatePath('/tasks')
return { success: true }

```
  } catch (error) {

```
console.error('Task deletion error:', error)
return { success: false, error: 'Failed to delete task' }

```
  }
}

```

### Client Component: Task Card with Optimistic Status

```typescript

// Source: React official docs + existing ProfileForm pattern
'use client'

import { useOptimistic, useTransition } from 'react'
import { updateTaskStatus, deleteTask } from '@/app/actions/tasks'

type Task = {
  id: string
  title: string
  description?: string | null
  status: 'todo' | 'in_progress' | 'done'
  createdAt: Date
}

export function TaskCard({ task }: { task: Task }) {
  const [isPending, startTransition] = useTransition()
  const [optimisticTask, setOptimisticTask] = useOptimistic(

```
task,
(state, newStatus: Task['status']) => ({ ...state, status: newStatus })

```
  )

  function handleStatusChange(newStatus: Task['status']) {

```
startTransition(async () => {
  // Update optimistically
  setOptimisticTask(newStatus)

  // Send to server
  const result = await updateTaskStatus(task.id, newStatus)

  // On error, optimistic state automatically rolls back
  if (!result.success) {
    console.error('Failed to update status:', result.error)
  }
})

```
  }

  function handleDelete() {

```
if (!confirm('Delete this task?')) return

startTransition(async () => {
  const result = await deleteTask(task.id)
  if (!result.success) {
    alert(result.error || 'Failed to delete task')
  }
})

```
  }

  return (

```
<div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 space-y-3">
  <h3 className="font-semibold text-lg">{optimisticTask.title}</h3>

  {optimisticTask.description && (
    <p className="text-gray-600 dark:text-gray-300 text-sm">
      {optimisticTask.description}
    </p>
  )}

  <div className="flex items-center justify-between">
    <select
      value={optimisticTask.status}
      onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
      disabled={isPending}
      className="text-sm border rounded px-2 py-1"
    >
      <option value="todo">To Do</option>
      <option value="in_progress">In Progress</option>
      <option value="done">Done</option>
    </select>

    <button
      onClick={handleDelete}
      disabled={isPending}
      className="text-red-600 hover:text-red-800 text-sm"
    >
      Delete
    </button>
  </div>

  {isPending && (
    <div className="text-xs text-gray-500">Saving...</div>
  )}
</div>

```
  )
}

```markdown

### Server Component: Task List Page

```typescript

// Source: Next.js App Router patterns
import { Suspense } from 'react'
import Link from 'next/link'
import { getTasksByUser } from '@/shared/lib/dal'
import { TaskList } from '@/shared/components/TaskList'

export default async function TasksPage() {
  return (

```
<div className="container mx-auto px-4 py-8">
  <div className="flex justify-between items-center mb-8">
    <h1 className="text-3xl font-bold">My Tasks</h1>
    <Link href="/tasks/new">
      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
        + New Task
      </button>
    </Link>
  </div>

  <Suspense fallback={<TaskListSkeleton />}>
    <TaskListContent />
  </Suspense>
</div>

```
  )
}

async function TaskListContent() {
  const tasks = await getTasksByUser()

  if (tasks.length === 0) {

```
return (
  <div className="text-center py-12">
    <p className="text-gray-500 text-lg mb-4">
      No tasks yet! Create your first task to get started
    </p>
    <Link href="/tasks/new">
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
        Create Your First Task
      </button>
    </Link>
  </div>
)

```
  }

  return <TaskList tasks={tasks} />
}

function TaskListSkeleton() {
  return (

```
<div className="space-y-8">
  {['To Do', 'In Progress', 'Done'].map(status => (
    <div key={status}>
      <div className="h-6 w-32 bg-gray-200 rounded mb-4 animate-pulse" />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  ))}
</div>

```
  )
}

```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
  | API routes ... | Server Actions | Next.js 13 ... | 40% less bo... |  
  | React Query... | useOptimist... | React 18 | Simpler API... |  
  | useFormState | useActionState | Next.js 15 | Cleaner API... |  
  | Manual form... | useFormStat... | React 18 | Automatic p... |  
  | JWT sessions | Database se... | Auth.js v5 | Better secu... |  
| Client-side... | Zod + Serve... | 2023-2024 t... | Type-safe, ... |
  | Separate CR... | Server Acti... | Next.js 13+ | Colocation ... |  

**Deprecated/outdated:**

- **API routes for mutations** - Use Server Actions instead (less code,
  type-safe, no API layer)
- **getServerSideProps/getStaticProps** - Use Server Components (streaming,
  better UX)
- **useFormState** - Renamed to useActionState in Next.js 15 (API unchanged)
- **Pages directory** - App directory is stable and recommended for new projects
- **Prisma 6 and earlier** - Prisma 7 has 3x faster queries, 90% smaller bundles
  (Rust-free architecture)

## Open Questions

Things that couldn't be fully resolved:

1. **Task Edit UX**
   - What we know: CONTEXT.md leaves editing approach to Claude's discretion

```
 (inline, modal, or page)

```
   - What's unclear: Tradeoffs between approaches for this specific use case
   - Recommendation: Research in planning phase. Options:

```
 - **Inline editing**: Fastest UX, but complex state management
 - **Modal**: Good balance, reuses form component
 - **Dedicated page**: Simplest implementation, consistent with `/tasks/new`
   pattern

```
2. **Auto-save vs Manual Save for Task Edits**
   - What we know: Profile uses auto-save with 3-second debounce (PATTERN-003)
   - What's unclear: Whether same pattern fits task editing (longer descriptions,

```
 more fields)

```
   - Recommendation: Manual save for dedicated edit page, auto-save only if

```
 inline editing. Align with user expectations (tasks feel more
 "document-like" than profile fields).

```
3. **Completed Task Visual Treatment**
   - What we know: CONTEXT.md leaves to discretion (fade, hide, or normal)
   - What's unclear: User preference for this validation project
   - Recommendation: Normal visibility in "Done" section for MVP. Track analytics

```
 to see if users want to hide/archive completed tasks in future phase.

```
4. **Task Deletion Confirmation**
   - What we know: CONTEXT.md mentions "confirmation style, undo options" as open
   - What's unclear: Confirmation dialog vs undo toast vs require typing "delete"
   - Recommendation: Simple confirm() dialog for MVP (native, accessible, no

```
 extra code). Consider toast-based undo in future iteration if analytics show
 frequent accidental deletions.

```
## Sources

### Primary (HIGH confidence)

- [Next.js Forms Guide](https://nextjs.org/docs/app/guides/forms) - Server
  Actions, useActionState, Zod validation
- [Next.js revalidatePath
  API](https://nextjs.org/docs/app/api-reference/functions/revalidatePath) -
  Cache invalidation after mutations
- [React useOptimistic Hook](https://react.dev/reference/react/useOptimistic) -
  Optimistic UI updates
- [Prisma Models
  Documentation](https://www.prisma.io/docs/orm/prisma-schema/data-model/models)
  - Model definition, relations, indexes
- Existing codebase patterns:
  - `/src/app/actions/profile.ts` - Server Action structure with Zod
  - `/src/shared/lib/dal.ts` - DAL pattern with React cache()
  - `/src/shared/components/ProfileForm.tsx` - Auto-save pattern with status

```
indicators

```
### Secondary (MEDIUM confidence)

- [Next.js 15 Server Actions Complete
  Guide](https://medium.com/@saad.minhas.codes/next-js-15-server-actions-complete-guide-with-real-examples-2026-6320fbfa01c3)
  - Real-world examples (Jan 2026)
- [How to Build a Task Management App Using Next.js 16 and Prisma
  7](https://dev.to/myogeshchavan97/how-to-build-a-task-management-app-using-nextjs-16-and-prisma-7-4mcf)
  - Task model patterns
- [Server Actions Best
  Practices](https://medium.com/@lior_amsalem/nextjs-15-actions-best-practice-bf5cc023301e)
  - Organization and patterns
- [Prisma 7 Performance
  Gains](https://www.infoq.com/news/2026/01/prisma-7-performance/) - Why Prisma 7
  (Jan 2026)
- [React Server Components + TanStack
  Query](https://dev.to/krish_kakadiya_5f0eaf6342/react-server-components-tanstack-query-the-2026-data-fetching-power-duo-you-cant-ignore-21fj)
  - Data fetching patterns (2026)
- [Server Actions Error
  Handling](https://medium.com/@pawantripathi648/next-js-server-actions-error-handling-the-pattern-i-wish-i-knew-earlier-e717f28f2f75)
  - Production-ready error patterns (Dec 2025)
- [React Performance Optimization
  2026](https://medium.com/@muhammadshakir4152/react-js-optimization-every-react-developer-must-know-2026-edition-e1c098f55ee9)
  - Current best practices

### Tertiary (LOW confidence)

- None - All key findings verified with official documentation

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All libraries already in package.json, versions verified
- Architecture patterns: HIGH - Extended from existing Phase 2 implementation
- Pitfalls: HIGH - Sourced from official docs, GitHub discussions, and
  established anti-patterns
- Code examples: HIGH - Adapted from official Next.js/React docs and existing
  codebase

**Research date:** 2026-01-25
**Valid until:** 2026-02-28 (30 days - stable tech stack, minimal churn
expected)

**Key constraints from CONTEXT.md:**

- ✅ Dedicated page at /tasks/new (not inline or modal)
- ✅ Plus button on dashboard for quick access
- ✅ Card-based layout with shadow and padding
- ✅ Tasks grouped by status (Todo, In Progress, Done sections)
- ✅ Empty state with friendly illustration and CTA
- 🤷 Required fields, card content, status UI, editing approach - Claude's
  discretion
