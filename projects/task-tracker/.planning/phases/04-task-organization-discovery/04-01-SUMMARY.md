---
phase: 04-task-organization-discovery
plan: 01
subsystem: data-layer
tags: [prisma, postgresql, search, tags, full-text-search, pg_trgm]
requires: [03-core-task-management]
provides:

  - Tag model with many-to-many Task relation
  - PostgreSQL full-text search with tsvector
  - Fuzzy search fallback with pg_trgm
  - Tag CRUD Server Actions
  - DAL functions for search and filtering

affects: [04-02, 04-03, 04-04]
tech-stack:
  added: [pg_trgm]
  patterns:

```markdown

- Generated tsvector columns for automatic search index maintenance
- Weighted full-text search (title=A, description=B)
- Two-tier search (FTS primary, fuzzy fallback)
- Implicit many-to-many relations in Prisma

```yaml

key-files:
  created:

```markdown

- prisma/migrations/20260125200020_add_tags_and_search/migration.sql
- src/app/actions/tags.ts

```yaml

  modified:

```markdown

- prisma/schema.prisma
- src/shared/lib/dal.ts
- src/shared/lib/analytics/types.ts

```yaml

decisions:

  - id: SEARCH-001

```yaml
title: Use PostgreSQL tsvector over external search service
rationale: Validation project scale doesn't justify Elasticsearch/Algolia
complexity
impact: Search integrated into primary database, no additional
infrastructure

```

  - id: SEARCH-002

```yaml
title: Two-tier search strategy (FTS + fuzzy fallback)
rationale: Full-text search for exact matches, trigrams catch typos and
partial terms
impact: Better search UX without requiring exact spelling

```yaml

  - id: SEARCH-003

```yaml
title: Generated tsvector column instead of triggers
rationale: PostgreSQL 12+ native feature, automatic maintenance without
custom code
impact: Cleaner schema, no trigger maintenance burden

```yaml

  - id: TAG-001

```yaml
title: Implicit many-to-many over explicit join table
rationale: Prisma auto-generates _TagToTask, simpler API for basic tagging
impact: Less boilerplate, Prisma handles join operations

```yaml

metrics:
  duration: 5 minutes
  tasks_completed: 4/4
  commits: 4
  files_changed: 5
completed: 2026-01-25
---

# Phase 04 Plan 01: Tag Model and Search Infrastructure Summary

**One-liner:** PostgreSQL full-text search with weighted tsvector, fuzzy trigram
fallback, and flexible tag-based organization via implicit many-to-many
relations.

## What Was Built

### Tag Model

- **User-scoped tags** with color coding for visual categorization
- **Implicit many-to-many** with tasks (Prisma generates `_TagToTask` join table)
- **Unique constraint** on `[userId, name]` prevents duplicate tag names per user
- **Cascade delete** when user is deleted maintains data integrity

### Search Infrastructure

- **pg_trgm extension** enabled for fuzzy search capabilities
- **Generated tsvector column** on tasks table with weighted search:
  - Title matches weighted 'A' (highest priority)
  - Description matches weighted 'B' (secondary)
- **GIN indexes** for optimal search performance:
  - `tasks_search_vector_idx` for full-text search
  - `tasks_title_trgm_idx` for fuzzy title matching
  - `tasks_description_trgm_idx` for fuzzy description matching

### DAL Functions

- `getTagsByUser`: Fetch all user tags alphabetically sorted
- `searchTasks`: Two-tier search with ranking:
  1. Full-text search with `ts_rank` relevance scoring
  2. Fallback to trigram similarity for typos/partial matches
- `filterTasks`: Multi-criteria filtering (status, tags, date range)
- `getTaskWithTags`: Eager-load tags for single task display

### Server Actions

- `createTag`: Name uniqueness validation, default color assignment
- `deleteTag`: Ownership verification, automatic removal from all tasks
- `updateTaskTags`: Set operation for bulk tag replacement
- `addTagToTask`: Connect-or-create pattern for inline tagging

### Analytics Events

Added 4 new event types to analytics schema:

- `tag_created`
- `tag_deleted`
- `task_tags_updated`
- `tag_added_to_task`

## Implementation Approach

**Task 1:** Added Tag model to Prisma schema with implicit m-n relation to Task

- Used `@@unique([userId, name])` for name uniqueness per user
- Color field for future UI visual categorization

**Task 2:** Created migration with PostgreSQL extensions and indexes

- Manual migration file to add pg_trgm extension (not supported by Prisma schema)
- Generated tsvector column using STORED computed column (PostgreSQL 12+ feature)
- Three GIN indexes for optimal search performance

**Task 3:** Implemented DAL functions with two-tier search strategy

- Primary: Full-text search with `websearch_to_tsquery` for semantic matching
- Fallback: Trigram similarity with `%` operator for fuzzy matching
- All functions use React `cache()` for request deduplication

**Task 4:** Created tag Server Actions with comprehensive validation

- Zod schemas for input validation
- Ownership verification on all mutations
- Analytics tracking for brain learning

## Key Technical Decisions

**Why generated tsvector over triggers?**
PostgreSQL 12+ supports GENERATED ALWAYS columns that automatically update when
source columns change. This eliminates trigger maintenance and is cleaner than
manual tsvector management.

**Why weighted search?**
Title matches should rank higher than description matches in search results.
Using `setweight()` with 'A' for title and 'B' for description achieves this.

**Why two-tier search (FTS + fuzzy)?**
Full-text search is fast but requires exact word boundaries. Trigram search
catches typos and partial matches. Try FTS first for speed, fallback to trigrams
for UX.

**Why implicit many-to-many?**
For basic tagging without custom join table fields, Prisma's implicit m-n is
simpler. The auto-generated `_TagToTask` table handles the relationship without
boilerplate.

## Deviations from Plan

None - plan executed exactly as written.

## Testing Notes

**Search verification:**

```sql

-- Test full-text search
SELECT title, ts_rank(search_vector, websearch_to_tsquery('english', 'test')) as rank
FROM tasks WHERE search_vector @@ websearch_to_tsquery('english', 'test');

-- Test fuzzy search
SELECT title, similarity(title, 'tast') as sim
FROM tasks WHERE title % 'tast' ORDER BY sim DESC;

```yaml

**Tag relationship verification:**

```sql

-- Verify implicit join table
SELECT * FROM "_TagToTask" LIMIT 5;

-- Verify cascade delete
DELETE FROM tags WHERE id = 'test-tag-id';
-- Should remove all entries from _TagToTask

```markdown

## Next Phase Readiness

**For 04-02 (Search UI):**

- ✅ `searchTasks` DAL function ready for Server Component consumption
- ✅ Ranking preserved in search results for relevance display
- ✅ Tag filtering ready via `filterTasks`

**For 04-03 (Tag UI):**

- ✅ Tag CRUD Server Actions ready for form submission
- ✅ `getTagsByUser` ready for tag picker components
- ✅ `updateTaskTags` supports multi-select tag management

**For 04-04 (Advanced Filtering):**

- ✅ `filterTasks` supports composite filters (status + tags + date)
- ✅ All filters optional and composable

**Known constraints:**

- Search limited to 50 results (pagination not yet implemented)
- Tag colors defined but not yet used in UI
- Search assumes English language tokenization (pg config)

## Commits

| Hash | Message | Files |
| ------ | --------- | ------- |
| 40dae6e | feat(04-01): add T... | prisma/schema.prisma |
| 1252902 | feat(04-01): add P... | prisma/migrations/... |
| 2f1cd1e | feat(04-01): add D... | src/shared/lib/dal.ts |
| b1c0697 | feat(04-01): add S... | src/app/actions/ta... |

## Brain-Worthy Patterns

**Pattern: Generated tsvector for automatic search index maintenance**

```prisma

-- In migration.sql, not schema.prisma (Prisma doesn't support tsvector)
ALTER TABLE tasks
ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (
  setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('english', coalesce(description, '')), 'B')
) STORED;

```yaml

*Eliminates triggers, automatically updates on INSERT/UPDATE, supports weighted
relevance.*

**Pattern: Two-tier search with graceful degradation**

```typescript

// Try fast FTS first
const ftsResults = await prisma.$queryRaw`...websearch_to_tsquery...`
if (ftsResults.length > 0) return ftsResults

// Fall back to fuzzy search for typos
const fuzzyResults = await prisma.$queryRaw`...similarity...`
return fuzzyResults

```

*Best of both worlds: speed when possible, UX when needed.*

**Pattern: Connect-or-create for inline tag creation**

```typescript

await prisma.task.update({
  where: { id: taskId },
  data: {

```yaml

tags: {
  connectOrCreate: {

```yaml
where: { userId_name: { userId, name: tagName } },
create: { name: tagName, color: '#6b7280', userId }

```markdown

  }
}

```markdown

  }
})

```markdown

*Enables "create tag while tagging task" UX without separate API calls.*

## Validation Checklist

- [x] Tag model exists with implicit m-n to Task
- [x] search_vector tsvector column exists on tasks table
- [x] GIN indexes exist for search_vector, title trigrams, description trigrams
- [x] pg_trgm extension enabled
- [x] DAL functions handle full-text search with fuzzy fallback
- [x] Server Actions for tag CRUD operations work
- [x] All TypeScript types correct
- [x] Prisma schema validates
- [x] TypeScript compiles without errors
- [x] _TagToTask join table created automatically

## Performance Notes

**Execution time:** 5 minutes (start: 1769363948, end: 1769364251)

**Search performance considerations:**

- GIN indexes provide O(log n) search performance
- Generated columns add ~10% overhead on INSERT/UPDATE (negligible for validation

  scale)

- tsvector column storage: ~30% overhead vs raw text (acceptable tradeoff)
- Trigram indexes larger than tsvector indexes but necessary for fuzzy search

**Future optimizations (if needed at scale):**

- Add partial indexes for active tasks only
- Consider pg_trgm similarity threshold tuning
- Implement search result pagination beyond 50 items
