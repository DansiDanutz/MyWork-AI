# Phase 4: Task Organization & Discovery - Research

**Researched:** 2026-01-25
**Domain:** Full-text search, categorization, filtering, and bulk operations in
Next.js 15 + PostgreSQL
**Confidence:** HIGH

## Summary

Research focused on implementing efficient task organization and search
capabilities in a Next.js 15/PostgreSQL/Prisma stack. The standard approach
combines PostgreSQL's native full-text search (tsvector + GIN indexes) for
semantic search, pg_trgm extension for fuzzy matching, URL-based filter state
management with nuqs library, and React 19's useOptimistic for instant UI
feedback during bulk operations.

For task organization, the consensus favors a flexible tagging system over rigid
hierarchical categories, allowing tasks to belong to multiple organizational
contexts. Search should use PostgreSQL's full-text search for speed and
relevance ranking, with pg_trgm as a fallback for typo tolerance. Filter state
lives in the URL for shareability and bookmarking, managed by the nuqs library
for type safety.

**Primary recommendation:** Use PostgreSQL tsvector with GIN indexes for
full-text search (fast, semantic), add pg_trgm extension for fuzzy matching
(typo-tolerant), implement many-to-many tags via implicit Prisma relations,
manage filter state in URL with nuqs library, and use Server Actions with
debounced input for instant search feedback.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
| PostgreSQL ... | Native | Full-text s... | 99.7% faste... |
  | pg_trgm ext... | Native | Fuzzy searc... | Handles typ... |  
| Prisma Type... | 5.19.0+ | Type-safe r... | Official Pr... |
| nuqs | 2.x | Type-safe U... | Like useSta... |
| react-highl... | 2.x | Search resu... | Lightweight... |

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
| use-debounce | 10.x | Debounced s... | Reduce data... |
| Prisma impl... | Native | Many-to-man... | When no ext... |
  | GIN indexes | PostgreSQL | Index for t... | Required fo... |  

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
  | nuqs | useSearchParams + ... | nuqs provides type... |  
  | tsvector | ILIKE with pg_trgm... | ILIKE doesn't scal... |  
  | TypedSQL | Raw $queryRaw with... | TypedSQL provides ... |  
| Implicit m-n | Explicit join tabl... | Explicit allows me... |

**Installation:**

```bash
npm install nuqs use-debounce react-highlight-words zod

```yaml

PostgreSQL extensions (via migration):

```sql

CREATE EXTENSION IF NOT EXISTS pg_trgm;

```markdown

## Architecture Patterns

### Recommended Project Structure

```text
src/
├── app/
│   └── dashboard/
│       └── tasks/
│           ├── page.tsx              # Task list with URL-based filters
│           ├── search-params.ts      # nuqs parser definitions
│           └── components/
│               ├── TaskFilters.tsx   # Filter sidebar
│               ├── TaskSearchBar.tsx # Debounced search input
│               └── TaskBulkActions.tsx # Checkbox + bulk ops
├── modules/
│   └── task/
│       ├── task-dal.ts               # Data access layer
│       ├── task-actions.ts           # Server Actions
│       ├── task-search.sql           # TypedSQL query files
│       └── schemas/
│           └── task-filters.ts       # Zod schemas for filters
└── lib/

```text

└── search/

```text
├── highlight-utils.ts        # Text highlighting helpers
└── search-utils.ts           # Query building utilities

```text

```text

```

### Pattern 1: PostgreSQL Full-Text Search with TypedSQL

**What:** Use tsvector column with GIN index for fast, ranked full-text search
**When to use:** Searching task titles, descriptions, and other text content
**Example:**

```typescript

// prisma/schema.prisma
model Task {
  id          String     @id @default(cuid())
  title       String     @db.VarChar(255)
  description String?    @db.Text
  // ... other fields

  @@index([userId, status])
}

// Migration: Add tsvector + GIN index via raw SQL
// prisma/migrations/XXX_add_fulltext_search/migration.sql
-- Add generated tsvector column (weighted: title=A, description=B)
ALTER TABLE tasks
ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(description, '')), 'B')
) STORED;

-- Create GIN index for fast search
CREATE INDEX tasks_search_vector_idx ON tasks USING GIN(search_vector);

-- Create trigram index for fuzzy search fallback
CREATE INDEX tasks_title_trgm_idx ON tasks USING GIN(title gin_trgm_ops);
CREATE INDEX tasks_description_trgm_idx ON tasks USING GIN(description gin_trgm_ops);

// TypedSQL query: prisma/sql/searchTasks.sql
-- @param {String} $1:searchQuery
-- @param {String} $2:userId
SELECT
  id, title, description, status, "createdAt", "updatedAt",
  ts_rank(search_vector, websearch_to_tsquery('english', $1)) as rank
FROM tasks
WHERE
  "userId" = $2 AND
  search_vector @@ websearch_to_tsquery('english', $1)
ORDER BY rank DESC, "createdAt" DESC
LIMIT 50;

// src/modules/task/task-dal.ts
import { searchTasks } from '@prisma/client/sql';

export async function searchTasksFTS(userId: string, query: string) {
  return await prisma.$queryRawTyped(searchTasks(query, userId));
}

```markdown

### Pattern 2: URL-Based Filter State with nuqs

**What:** Store filter state in URL params for shareability and bookmarking
**When to use:** Any filtering UI (search, status, tags, date ranges)
**Example:**

```typescript

// src/app/dashboard/tasks/search-params.ts
import { parseAsString, parseAsArrayOf, parseAsStringEnum } from 'nuqs';
import { TaskStatus } from '@prisma/client';

export const taskSearchParams = {
  search: parseAsString.withDefault(''),
  status: parseAsArrayOf(parseAsStringEnum(Object.values(TaskStatus))).withDefault([]),
  tags: parseAsArrayOf(parseAsString).withDefault([]),
  sortBy: parseAsStringEnum(['createdAt', 'updatedAt', 'title']).withDefault('createdAt'),
  sortOrder: parseAsStringEnum(['asc', 'desc']).withDefault('desc'),
};

// src/app/dashboard/tasks/page.tsx
'use client';
import { useQueryStates } from 'nuqs';
import { taskSearchParams } from './search-params';

export default function TasksPage() {
  const [filters, setFilters] = useQueryStates(taskSearchParams);

  // filters.search, filters.status, etc. are fully typed
  // setFilters({ search: 'new query' }) updates URL automatically

  return (

```javascript

<TaskSearchBar
  value={filters.search}
  onChange={(search) => setFilters({ search })}
/>

```markdown

  );
}

```markdown

### Pattern 3: Debounced Search with Server Actions

**What:** Debounce search input to reduce database queries, use Server Actions
for fetching
**When to use:** Live search that queries on every keystroke
**Example:**

```typescript

// src/app/dashboard/tasks/components/TaskSearchBar.tsx
'use client';
import { useDebouncedCallback } from 'use-debounce';
import { searchTasksAction } from '@/modules/task/task-actions';

export function TaskSearchBar({ value, onChange }: Props) {
  const [results, setResults] = useState<Task[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const debouncedSearch = useDebouncedCallback(async (query: string) => {

```javascript

if (!query.trim()) {
  setResults([]);
  return;
}

setIsSearching(true);
try {
  const tasks = await searchTasksAction(query);
  setResults(tasks);
} finally {
  setIsSearching(false);
}

```javascript
  }, 300); // 300ms recommended by Next.js docs

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {

```javascript

const newValue = e.target.value;
onChange(newValue);
debouncedSearch(newValue);

```text
  };

  return (

```

<div className="relative">
  <input

```text
type="search"
value={value}
onChange={handleChange}
placeholder="Search tasks..."

```bash

  />
  {isSearching && <Spinner />}
</div>

```markdown

  );
}

```markdown

### Pattern 4: Many-to-Many Tags with Implicit Relations

**What:** Use Prisma's implicit m-n for tags without extra metadata
**When to use:** Simple tagging where you don't need to track who/when assigned
tags
**Example:**

```typescript

// prisma/schema.prisma
model Task {
  id          String   @id @default(cuid())
  title       String
  tags        Tag[]    // Implicit m-n relation
  // ...
}

model Tag {
  id          String   @id @default(cuid())
  name        String   @unique
  color       String?  // Optional color for UI
  tasks       Task[]   // Implicit m-n relation
  createdAt   DateTime @default(now())

  @@index([name]) // Fast lookups
}

// Prisma auto-generates join table: _TaskToTag

// src/modules/task/task-dal.ts
export async function createTaskWithTags(userId: string, data: CreateTaskInput) {
  return await prisma.task.create({

```yaml

data: {
  title: data.title,
  description: data.description,
  userId: userId,
  tags: {

```
connectOrCreate: data.tagNames.map(name => ({
  where: { name },
  create: { name },
})),

```yaml

  },
},
include: { tags: true },

```javascript
  });
}

export async function filterTasksByTags(userId: string, tagIds: string[]) {
  return await prisma.task.findMany({

```yaml

where: {
  userId,
  tags: {

```yaml
some: {
  id: { in: tagIds },
},

```

  },
},
include: { tags: true },

```text
  });
}

```markdown

### Pattern 5: Bulk Operations with useOptimistic

**What:** Instant UI updates during bulk operations using React 19's
useOptimistic
**When to use:** Bulk status changes, bulk tag assignments, bulk deletions
**Example:**

```typescript

// src/app/dashboard/tasks/components/TaskBulkActions.tsx
'use client';
import { useOptimistic } from 'react';
import { bulkUpdateStatusAction } from '@/modules/task/task-actions';

export function TaskBulkActions({ selectedIds, tasks }: Props) {
  const [optimisticTasks, updateOptimisticTasks] = useOptimistic(

```javascript

tasks,
(state, { ids, status }: { ids: string[], status: TaskStatus }) => {
  return state.map(task =>

```yaml
ids.includes(task.id) ? { ...task, status } : task

```text

  );
}

```
  );

  async function handleBulkStatusChange(status: TaskStatus) {

```yaml

// Optimistic update (instant UI)
updateOptimisticTasks({ ids: selectedIds, status });

// Server Action (actual update)
try {
  await bulkUpdateStatusAction(selectedIds, status);
} catch (error) {
  // React automatically reverts optimistic update on error
  toast.error('Failed to update tasks');
}

```html

  }

  return (

```html

<DropdownMenu>
  <DropdownMenuItem onClick={() => handleBulkStatusChange('IN_PROGRESS')}>

```html

Mark as In Progress

```html

  </DropdownMenuItem>
  {/* ... */}
</DropdownMenu>

```
  );
}

```markdown

### Pattern 6: Search Result Highlighting

**What:** Highlight matching text in search results with <mark> tags
**When to use:** Showing why a result matched the query
**Example:**

```typescript

// src/lib/search/highlight-utils.ts
export function highlightMatches(text: string, query: string): string {
  if (!query.trim()) return text;

  // Escape regex special characters
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapedQuery})`, 'gi');

  return text.replace(regex, '<mark>$1</mark>');
}

// src/app/dashboard/tasks/components/TaskCard.tsx
import Highlighter from 'react-highlight-words';

export function TaskCard({ task, searchQuery }: Props) {
  return (

```html

<div>
  <h3>

```text
<Highlighter
  searchWords={[searchQuery]}
  autoEscape
  textToHighlight={task.title}
/>

```html

  </h3>
  <p>

```bash
<Highlighter
  searchWords={[searchQuery]}
  autoEscape
  textToHighlight={task.description || ''}
/>

```

  </p>
</div>

```markdown

  );
}

```markdown

### Anti-Patterns to Avoid

- **Don't use ILIKE for search at scale:** ILIKE '%term%' doesn't scale past

  10,000 rows and can't use indexes effectively. Use full-text search instead.

- **Don't put filter state in React state only:** Users can't share/bookmark

  filtered views. Always use URL params as single source of truth.

- **Don't skip debouncing on search input:** Hitting the database on every

  keystroke wastes resources and degrades performance. Use 300-500ms debounce.

- **Don't concatenate user input in raw SQL:** Use parameterized queries via

  TypedSQL or $queryRaw with template tags to prevent SQL injection.

- **Don't create explicit join tables unless needed:** Prisma's implicit m-n is

  simpler and sufficient when you don't need extra metadata on the relationship.

- **Don't ignore empty states:** When filters return no results, show helpful

  guidance (broaden search, clear filters, suggest alternatives).

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
| Full-text s... | Custom ILIK... | PostgreSQL ... | ILIKE doesn... |
  | Fuzzy search | Levenshtein... | pg_trgm ext... | Trigrams ha... |  
  | URL state m... | Manual URLS... | nuqs library | Type safety... |  
| Search high... | Regex repla... | react-highl... | Handles edg... |
| Debounced s... | Custom useE... | use-debounc... | Handles cle... |
| Many-to-man... | Explicit Pr... | Implicit m-... | Simpler API... |

**Key insight:** PostgreSQL's built-in full-text search is production-grade and
scales to millions of rows with proper indexing. Don't build custom search logic
or reach for Elasticsearch until you've exhausted PostgreSQL's capabilities.

## Common Pitfalls

### Pitfall 1: Not Creating GIN Indexes for tsvector

**What goes wrong:** Full-text search works but is slow (sequential scans),
queries take seconds instead of milliseconds.
**Why it happens:** Developers add tsvector columns but forget the GIN index, or
create indexes incorrectly.
**How to avoid:** Always create GIN index on tsvector columns. Test with EXPLAIN
ANALYZE to verify index usage.
**Warning signs:**

- Query times increase linearly with table size
- EXPLAIN shows "Seq Scan" instead of "Bitmap Index Scan"
- Queries take >100ms on tables with >10k rows

```sql

-- WRONG: No index
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

-- RIGHT: With GIN index
ALTER TABLE tasks ADD COLUMN search_vector tsvector;
CREATE INDEX tasks_search_vector_idx ON tasks USING GIN(search_vector);

```markdown

### Pitfall 2: Using ILIKE for Search Instead of Full-Text Search

**What goes wrong:** Search is slow, no relevance ranking, misses variations
(running vs run).
**Why it happens:** ILIKE seems simpler and works well with small datasets
during development.
**How to avoid:** Start with full-text search from the beginning. Only use ILIKE
for exact prefix matching (e.g., username autocomplete).
**Warning signs:**

- Search results aren't ranked by relevance
- Users complain about "why didn't this match?"
- Query times increase as data grows

```typescript

// WRONG: ILIKE doesn't scale
await prisma.task.findMany({
  where: {

```yaml

OR: [
  { title: { contains: query, mode: 'insensitive' } },
  { description: { contains: query, mode: 'insensitive' } },
],

```yaml
  },
});

// RIGHT: Full-text search with ranking
await prisma.$queryRawTyped(searchTasks(query, userId));

```markdown

### Pitfall 3: Storing Filter State Only in React State

**What goes wrong:** Users can't share filtered views, hitting back button loses
filters, page refresh resets everything.
**Why it happens:** React state is familiar and seems easier than URL
management.
**How to avoid:** Use URL params as single source of truth for all filter state.
Use nuqs for type-safe management.
**Warning signs:**

- Users ask "how do I share this filtered view?"
- Back button doesn't restore previous filter state
- Page refresh loses all filters

```typescript

// WRONG: React state only
const [filters, setFilters] = useState({ status: [], tags: [] });

// RIGHT: URL state
const [filters, setFilters] = useQueryStates(taskSearchParams);

```markdown

### Pitfall 4: No Debouncing on Search Input

**What goes wrong:** Excessive database queries, poor performance, rate limiting
issues.
**Why it happens:** Developers implement "live search" without considering query
frequency.
**How to avoid:** Always debounce search input by 300-500ms using use-debounce
library.
**Warning signs:**

- Database shows spike in queries during typing
- Search feels laggy or unresponsive
- Backend rate limiting triggers

```typescript

// WRONG: Query on every keystroke
const handleChange = async (e) => {
  const results = await searchTasks(e.target.value);
  setResults(results);
};

// RIGHT: Debounced
const debouncedSearch = useDebouncedCallback(async (query) => {
  const results = await searchTasks(query);
  setResults(results);
}, 300);

```markdown

### Pitfall 5: Using Explicit Many-to-Many When Implicit Would Suffice

**What goes wrong:** More complex API, extra boilerplate, harder to maintain.
**Why it happens:** Developers assume explicit join tables are always needed or
follow outdated patterns.
**How to avoid:** Use implicit m-n unless you need to store metadata (who
assigned, when assigned, etc.) on the relationship.
**Warning signs:**

- Join table model has no fields beyond the two IDs
- Queries become verbose with nested includes
- Simple operations require multiple database calls

```typescript

// WRONG: Explicit join table with no extra fields
model TaskTag {
  taskId String
  tagId  String
  task   Task   @relation(fields: [taskId], references: [id])
  tag    Tag    @relation(fields: [tagId], references: [id])
  @@id([taskId, tagId])
}

// RIGHT: Implicit m-n
model Task {
  id   String @id
  tags Tag[]
}
model Tag {
  id    String @id
  tasks Task[]
}

```markdown

### Pitfall 6: Forgetting Empty States for Search/Filters

**What goes wrong:** Users see blank screen with no guidance when filters return
no results, confusion about whether something broke.
**Why it happens:** Developers focus on happy path and forget edge cases.
**How to avoid:** Always implement empty states with helpful guidance (clear
filters, broaden search, suggested alternatives).
**Warning signs:**

- User reports "the app is broken" when they've filtered everything out
- No visual indication when search returns zero results
- Users don't know how to recover from empty state

```typescript

// WRONG: Just shows nothing
{tasks.length === 0 ? null : <TaskList tasks={tasks} />}

// RIGHT: Helpful empty state
{tasks.length === 0 ? (
  <EmptyState

```

title="No tasks found"
description="Try broadening your search or clearing some filters"
action={<Button onClick={clearFilters}>Clear Filters</Button>}

```yaml
  />
) : (
  <TaskList tasks={tasks} />
)}

```markdown

## Code Examples

Verified patterns from official sources:

### Full-Text Search with TypedSQL (Prisma Official Docs)

```typescript

// Source: https://www.prisma.io/docs/orm/prisma-client/using-raw-sql/typedsql

// 1. Create TypedSQL query file: prisma/sql/searchTasks.sql
-- @param {String} $1:searchQuery
-- @param {String} $2:userId
SELECT
  id, title, description, status, "createdAt", "updatedAt",
  ts_rank(search_vector, websearch_to_tsquery('english', $1)) as rank
FROM tasks
WHERE
  "userId" = $2 AND
  search_vector @@ websearch_to_tsquery('english', $1)
ORDER BY rank DESC, "createdAt" DESC
LIMIT 50;

// 2. Generate TypedSQL types
// npx prisma generate --sql

// 3. Use in code with full type safety
import { searchTasks } from '@prisma/client/sql';
import prisma from '@/lib/db';

export async function searchTasksDAL(userId: string, query: string) {
  // Fully typed result based on SELECT columns
  const results = await prisma.$queryRawTyped(searchTasks(query, userId));
  return results;
}

```markdown

### URL State with nuqs (nuqs Official Docs)

```typescript

// Source: https://nuqs.dev/

// 1. Define parsers with defaults
import { parseAsString, parseAsArrayOf, parseAsStringEnum } from 'nuqs';

const searchParams = {
  q: parseAsString.withDefault(''),
  status: parseAsArrayOf(parseAsStringEnum(['TODO', 'IN_PROGRESS', 'DONE'])).withDefault([]),
  page: parseAsInteger.withDefault(1),
};

// 2. Use in component (fully typed)
'use client';
import { useQueryStates } from 'nuqs';

export default function TasksPage() {
  const [filters, setFilters] = useQueryStates(searchParams);

  // filters.q: string
  // filters.status: ('TODO' | 'IN_PROGRESS' | 'DONE')[]
  // filters.page: number

  return (

```javascript

<input
  value={filters.q}
  onChange={(e) => setFilters({ q: e.target.value })}
/>

```markdown

  );
}

```markdown

### Debounced Search (Next.js Official Docs)

```typescript

// Source: https://nextjs.org/learn/dashboard-app/adding-search-and-pagination

'use client';
import { useDebouncedCallback } from 'use-debounce';
import { useSearchParams, usePathname, useRouter } from 'next/navigation';

export default function Search() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();

  const handleSearch = useDebouncedCallback((term: string) => {

```javascript

const params = new URLSearchParams(searchParams);
if (term) {
  params.set('query', term);
} else {
  params.delete('query');
}
replace(`${pathname}?${params.toString()}`);

```text
  }, 300);

  return (

```

<input
  placeholder="Search tasks..."
  onChange={(e) => handleSearch(e.target.value)}
  defaultValue={searchParams.get('query')?.toString()}
/>

```markdown

  );
}

```markdown

### Many-to-Many with Connect/Create (Prisma Official Docs)

```typescript

// Source: https://www.prisma.io/docs/orm/prisma-client/queries/relation-queries

// Create task with tags (create new tags or connect existing)
const task = await prisma.task.create({
  data: {

```yaml

title: 'Build search feature',
userId: userId,
tags: {
  connectOrCreate: [

```yaml
{
  where: { name: 'feature' },
  create: { name: 'feature', color: '#3b82f6' },
},
{
  where: { name: 'urgent' },
  create: { name: 'urgent', color: '#ef4444' },
},

```yaml

  ],
},

```yaml
  },
  include: { tags: true },
});

// Update task tags (disconnect old, connect new)
await prisma.task.update({
  where: { id: taskId },
  data: {

```

tags: {
  set: [], // Clear existing
  connect: newTagIds.map(id => ({ id })), // Connect new ones
},

```javascript
  },
});

// Find tasks by tags (tasks with ANY of these tags)
const tasks = await prisma.task.findMany({
  where: {

```yaml

tags: {
  some: {

```yaml
id: { in: tagIds },

```yaml

  },
},

```yaml
  },
  include: { tags: true },
});

```

### Checkbox Selection with Indeterminate State (React Official Patterns)

```typescript

// Source: https://www.patternfly.org/patterns/bulk-selection/

'use client';
import { useState, useRef, useEffect } from 'react';

export function TaskList({ tasks }: { tasks: Task[] }) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const headerCheckboxRef = useRef<HTMLInputElement>(null);

  // Update header checkbox indeterminate state
  useEffect(() => {

```javascript

if (!headerCheckboxRef.current) return;

const allSelected = selectedIds.size === tasks.length;
const someSelected = selectedIds.size > 0 && selectedIds.size < tasks.length;

headerCheckboxRef.current.checked = allSelected;
headerCheckboxRef.current.indeterminate = someSelected;

```javascript
  }, [selectedIds, tasks.length]);

  const toggleAll = () => {

```javascript

if (selectedIds.size === tasks.length) {
  setSelectedIds(new Set());
} else {
  setSelectedIds(new Set(tasks.map(t => t.id)));
}

```javascript
  };

  const toggleOne = (id: string) => {

```javascript

const newSelected = new Set(selectedIds);
if (newSelected.has(id)) {
  newSelected.delete(id);
} else {
  newSelected.add(id);
}
setSelectedIds(newSelected);

```html

  };

  return (

```html

<table>
  <thead>

```
<tr>
  <th>

```text

<input
  ref={headerCheckboxRef}
  type="checkbox"
  onChange={toggleAll}
/>

```
  </th>
  <th>Title</th>
</tr>

```html

  </thead>
  <tbody>

```javascript
{tasks.map(task => (
  <tr key={task.id}>

```

<td>
  <input

```
type="checkbox"
checked={selectedIds.has(task.id)}
onChange={() => toggleOne(task.id)}

```
  />
</td>
<td>{task.title}</td>

```html

  </tr>
))}

```html

  </tbody>
</table>

```
  );
}

```markdown

### Empty State Component (Design System Best Practices)

```typescript

// Source: https://carbondesignsystem.com/patterns/empty-states-pattern/

export function EmptyState({
  title,
  description,
  illustration,
  action,
}: EmptyStateProps) {
  return (

```html

<div className="flex flex-col items-center justify-center py-12 text-center">
  {illustration && (

```html

<div className="mb-4 text-gray-400">
  {illustration}
</div>

```html

  )}

  <h3 className="mb-2 text-lg font-semibold text-gray-900">

```text
{title}

```

  </h3>

  {description && (

```html

<p className="mb-4 max-w-sm text-sm text-gray-600">
  {description}
</p>

```bash

  )}

  {action && (

```html

<div className="mt-4">
  {action}
</div>

```

  )}
</div>

```markdown

  );
}

// Usage examples
<EmptyState
  title="No tasks found"
  description="Try adjusting your search or filters to find what you're looking for"
  action={<Button onClick={clearFilters}>Clear all filters</Button>}
/>

<EmptyState
  title="You don't have any tasks yet"
  description="Create your first task to get started with organizing your work"
  action={<Button onClick={openCreateDialog}>Create Task</Button>}
/>

```markdown

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
| Elasticsear... | PostgreSQL ... | 2020-2023 | Simpler sta... |
| ILIKE for f... | pg_trgm ext... | Always reco... | 10-100x fas... |
| Manual useS... | nuqs library | 2023-2024 | Type safety... |
  | Prisma $que... | Prisma Type... | 2024 (v5.19.0) | Native type... |  
| Explicit m-... | Implicit m-... | Prisma 2.x+ | Simpler API... |
  | React state... | URL state w... | Next.js 13+... | Shareable U... |  

**Deprecated/outdated:**

- **Elasticsearch for basic search**: Overkill for most apps. PostgreSQL FTS

  handles 10M+ rows efficiently with proper indexing.

- **LIKE/ILIKE for search at scale**: Doesn't use indexes, no ranking, no

  semantic understanding. Use FTS instead.

- **useSearchParams with manual parsing**: Error-prone, no type safety. Use nuqs

  for URL state.

- **$queryRawUnsafe**: SQL injection risk. Use TypedSQL or $queryRaw with

  template tags.

- **Explicit join tables by default**: Over-engineering. Use implicit m-n unless

  you need metadata.

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal search_vector update strategy**
   - What we know: Generated columns (STORED) are simplest but require PostgreSQL

```yaml
 12+. Triggers are alternative.

```yaml

   - What's unclear: Performance impact of generated columns on write-heavy

```yaml
 workloads vs trigger maintenance overhead.

```yaml

   - Recommendation: Start with generated columns (simpler), monitor write

```
 performance, switch to triggers only if bottleneck identified.

```yaml

2. **When to add fuzzy search fallback**
   - What we know: pg_trgm handles typos well but is slower than FTS. Can run

```yaml
 both queries and combine results.

```yaml

   - What's unclear: At what point does fuzzy fallback overhead outweigh UX

```yaml
 benefit? Depends on user typing accuracy.

```yaml

   - Recommendation: Implement FTS first, add fuzzy fallback only if users report

```yaml
 "why didn't this match?" issues.

```yaml

3. **Filter combination logic (AND vs OR)**
   - What we know: Most apps use AND for different filter types (status AND

```
 tags), OR within same type (tag1 OR tag2).

```yaml

   - What's unclear: User preference - some domains prefer OR everywhere for

```yaml
 broader results.

```yaml

   - Recommendation: Implement AND between types, OR within types initially. Add

```yaml
 toggle if users request different behavior.

```yaml

4. **Bulk operation size limits**
   - What we know: PostgreSQL handles large IN clauses well, but network payload

```yaml
 and transaction time can be issues.

```yaml

   - What's unclear: Optimal limit before breaking into batches (100? 1000?

```
 5000?).

```yaml

   - Recommendation: Start with 1000 item limit, show warning above 100 selected

```markdown

 items, measure actual performance.

```markdown

## Sources

### Primary (HIGH confidence)

- [Prisma TypedSQL

  Documentation](https://www.prisma.io/docs/orm/prisma-client/using-raw-sql/typedsql)

  - Official TypedSQL guide
- [Prisma Many-to-Many

  Relations](https://www.prisma.io/docs/orm/prisma-schema/data-model/relations/many-to-many-relations)

  - Official m-n docs
- [Next.js Official Tutorial: Search and

  Pagination](https://nextjs.org/learn/dashboard-app/adding-search-and-pagination)

  - Debouncing patterns
- [PostgreSQL Full-Text Search

  Documentation](https://www.postgresql.org/docs/current/textsearch-tables.html)

  - tsvector and GIN indexes
- [PostgreSQL pg_trgm

  Documentation](https://www.postgresql.org/docs/current/pgtrgm.html) - Trigram
  extension

- [nuqs Documentation](https://nuqs.dev/) - Type-safe URL state
- [React 19 useOptimistic

  Documentation](https://react.dev/reference/react/useOptimistic) - Official
  hook
  docs

### Secondary (MEDIUM confidence)

- [PostgreSQL Full-Text Search Best

  Practices](https://www.pedroalonso.net/blog/postgres-full-text-search/) -
  Production patterns

- [Bulletproof Full-Text Search with

  Prisma](https://medium.com/@chauhananubhav16/bulletproof-full-text-search-fts-in-prisma-with-postgresql-tsvector-without-migration-drift-c421f63aaab3)

  - Migration drift solutions
- [Managing Advanced Search Param

  Filtering](https://aurorascharff.no/posts/managing-advanced-search-param-filtering-next-app-router/)

  - Next.js 15 patterns
- [PatternFly Bulk

  Selection](https://www.patternfly.org/patterns/bulk-selection/) - Checkbox
  patterns

- [LogRocket Empty States Best

  Practices](https://blog.logrocket.com/ui-design-best-practices-loading-error-empty-state-react/)

  - UI patterns
- [Understanding Postgres GIN Indexes](https://pganalyze.com/blog/gin-index) -

  Performance characteristics

### Tertiary (LOW confidence)

- [PostgreSQL FTS Performance

  Tuning](https://medium.com/@jramcloud1/20-postgresql-17-performance-tuning-full-text-search-index-tsvector-ece3b576a37b)

  - PostgreSQL 17 specific
- [Next.js in 2026 Industry

  Overview](https://www.nucamp.co/blog/next.js-in-2026-the-full-stack-react-framework-that-dominates-the-industry)

  - Ecosystem trends
- [Task Management Categories vs Tags](https://clickup.com/blog/task-categories/)
  - Product design patterns

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All recommendations from official docs or widely-adopted

  libraries with strong community support

- Architecture: HIGH - Patterns verified in Next.js/Prisma official documentation

  and production apps

- Pitfalls: HIGH - Common mistakes documented across multiple sources and design

  system guides

**Research date:** 2026-01-25
**Valid until:** 60 days (stable stack - PostgreSQL FTS, Prisma, Next.js
patterns rarely change)
