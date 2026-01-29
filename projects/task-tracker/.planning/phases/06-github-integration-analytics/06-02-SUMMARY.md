---
phase: 06-github-integration-analytics
plan: 02
subsystem: analytics
tags: [github-api, rate-limiting, caching, etag, api-integration]
status: complete
requires: [02-01]
provides:

  - GitHub API client with rate limit handling
  - ETag-based caching for API efficiency
  - User enrichment functions

affects: [06-03]
decisions:

  - CACHE-001: 24-hour in-memory cache for GitHub user data (validation project

```text
scale)

```yaml

  - RATE-001: Warn at 100 remaining requests, graceful degradation on exhaustion
  - PATTERN-005: ETag-based conditional requests to minimize rate limit

```text
consumption

```yaml

tech-stack:
  added: []
  patterns:

```markdown

- In-memory Map cache with TTL for API responses
- ETag caching pattern for GitHub API
- Graceful degradation with stale data fallback

```yaml

key-files:
  created:

```markdown

- src/shared/lib/analytics/github.ts
- src/shared/lib/analytics/index.ts
- src/shared/lib/analytics/__tests__/github.test.ts

```

  modified: []
metrics:
  duration: 3 min
  completed: 2026-01-25
---

# Phase 06 Plan 02: GitHub API Integration Summary

**One-liner:** GitHub API client with rate limit monitoring, ETag caching, and
graceful degradation for user enrichment data.

## What Was Built

Created a production-ready GitHub API integration for fetching enriched user
data (repos, activity patterns) with comprehensive rate limit handling:

1. **Rate Limit Monitoring**: Parse `x-ratelimit-*` headers, warn when low,

graceful degradation on exhaustion

2. **ETag Caching**: Support `If-None-Match` headers - 304 responses don't count

against rate limits

3. **24-Hour Cache**: In-memory Map cache reduces API calls for validation

project scale

4. **Timeout Protection**: 5-second timeout prevents hanging requests
5. **Helper Functions**: Token retrieval from Prisma, user enrichment

convenience wrapper

### Key Implementation Details

**Rate Limit Headers Parsed:**

- `x-ratelimit-limit`: Total allowed requests
- `x-ratelimit-remaining`: Requests left in current window
- `x-ratelimit-reset`: Unix timestamp when limit resets
- `x-ratelimit-used`: Requests consumed

**Caching Strategy:**

- First request: Fetch data, cache with ETag
- Subsequent requests within 24h: Return cached data (no API call)
- After 24h: Send `If-None-Match` with cached ETag
  - 304 response: Extend cache TTL, no rate limit cost
  - 200 response: Update cache with fresh data

**Graceful Degradation:**

- Rate limit exhausted (403/429): Return cached data if available, else null
- Network error: Return cached data if available, else null
- Timeout (5s): Return cached data if available, else null

## Commits

| Commit | Type | Description |
| -------- | ------ | ------------- |
| d332fd8 | feat | Implement GitHub API client with rate limit handling |
| 2f0c583 | feat | Add analytics barrel export for GitHub functions |
| a3812f8 | test | Add type-checking test for GitHub API client |

## Files Changed

**Created:**

- `src/shared/lib/analytics/github.ts` (208 lines) - Core GitHub API client
- `src/shared/lib/analytics/index.ts` (11 lines) - Barrel exports
- `src/shared/lib/analytics/__tests__/github.test.ts` (29 lines) - Type tests

## Decisions Made

### CACHE-001: 24-Hour In-Memory Cache

**Decision:** Use Map with 24-hour TTL for GitHub user data caching
**Context:** Research suggests 24h cache for user profile enrichment data
**Alternatives:**

- Redis cache: Production-grade but overkill for validation project
- Database cache: Adds query overhead without benefit at this scale
- Shorter TTL: More API calls without meaningful freshness gain

**Outcome:** In-memory Map is sufficient for validation project, easily upgraded
to Redis if scale requires

### RATE-001: Rate Limit Warning Threshold

**Decision:** Log warning when remaining requests drop below 100
**Context:** GitHub allows 5,000 requests/hour; need early warning before
exhaustion
**Rationale:** 100 requests = 2% of limit, provides buffer to investigate/adjust
before hitting zero
**Outcome:** Proactive monitoring without false alarms during normal operation

### PATTERN-005: ETag-Based Conditional Requests

**Decision:** Always send `If-None-Match` header with cached ETag
**Context:** GitHub API spec: 304 responses don't count against rate limit
**Impact:** Massive rate limit savings - cache validation is free
**Implementation:** Store ETag from response headers, send with subsequent
requests

## Next Phase Readiness

**Blockers:** None

**Risks:**

- Cache stampede: If cache expires during high traffic, many requests hit API

  simultaneously

  - Mitigation: Add jitter to TTL in production (not needed for validation

```text
project)

```yaml

- Memory usage: Map cache grows unbounded if many users
  - Mitigation: Add LRU eviction or max size limit if needed

**Dependencies Satisfied:**

- Phase 2 OAuth provides `access_token` in Account model ✓
- Prisma schema includes Account.access_token field ✓

**Ready for:**

- Plan 06-03: Export API endpoint can now fetch enriched GitHub data for brain

  analysis

## Brain Learning Opportunities

**Reusable Patterns Captured:**

1. **GitHub API Rate Limit Pattern** (HIGH value)
   - Parse `x-ratelimit-*` headers
   - Warn at threshold, degrade gracefully on exhaustion
   - Use ETag caching for free cache validation
   - Applicable to: Any GitHub API integration, similar to other rate-limited

```text
 APIs

```markdown

2. **In-Memory Cache with TTL** (MEDIUM value)
   - Map-based cache with timestamp tracking
   - Stale-while-revalidate pattern (return old data on error)
   - Applicable to: Any external API with rate limits, validation projects

3. **Server-Only Module Testing** (MEDIUM value)
   - Type-only tests for server-only modules
   - Document runtime testing approach
   - Applicable to: All Next.js server-side modules

**Known Limitations:**

- In-memory cache doesn't survive server restarts (Redis would)
- No request coalescing (multiple concurrent requests for same user duplicate API

  calls)

- No cache warming strategy (first request always hits API)

**Production Considerations:**

- Replace Map with Redis for multi-instance deployments
- Add cache warming on app startup for known-active users
- Implement request coalescing with promise deduplication
- Add distributed locking for cache updates

## Testing Notes

**Manual Testing Required:**

1. Create Server Action or API route that calls `enrichUser(userId)`
2. Check console for rate limit warnings
3. Verify ETag headers in request/response
4. Confirm graceful degradation when rate limited

**Type Tests Passing:**

- ✓ Functions properly exported from barrel
- ✓ TypeScript types correctly inferred
- ✓ Test runs without requiring database/runtime

**Integration Testing:**

- Deferred to runtime - requires Next.js server environment
- Test via Server Actions or API routes with authenticated user

## Dependencies

**Required by this plan:**

- Prisma client (already in use)
- Auth.js Account model with access_token field (Phase 2)
- TypeScript 5.x (already configured)

**Required for next plans:**

- None - GitHub client is self-contained utility

## Metrics

**Effort:**

- Planning: N/A (autonomous plan)
- Implementation: 3 minutes
- Testing: Included in implementation
- Total: 3 minutes

**Complexity:**

- TypeScript: 208 LOC for core client
- Functions: 5 exported functions
- Cache logic: Single Map with TTL

**Quality:**

- Type safety: Full TypeScript coverage
- Error handling: Graceful degradation on all error paths
- Logging: Warning and error logging for observability
- Testing: Type tests passing, runtime deferred to integration

---

*Completed: 2026-01-25*
*Next: Plan 06-03 - Export API endpoint and data retention*
