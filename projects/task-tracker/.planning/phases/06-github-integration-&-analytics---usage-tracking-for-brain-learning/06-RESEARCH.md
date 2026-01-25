# Phase 6: GitHub Integration & Analytics - Research

**Researched:** 2026-01-25
**Domain:** Analytics, usage tracking, GitHub API integration, asynchronous event processing
**Confidence:** HIGH

## Summary

Phase 6 implements a non-blocking analytics system to capture user behavior patterns for the MyWork framework's brain learning system. The implementation leverages Next.js 15's `after()` API for asynchronous event logging, uses GitHub's REST API with proper rate limit handling, and stores analytics events in PostgreSQL with optimized JSONB indexing.

The standard approach is to:
1. Track events using Next.js 15's `after()` API to avoid blocking user operations
2. Store events in a simple PostgreSQL table with JSONB properties for flexibility
3. Use GitHub's OAuth access tokens (already available from Phase 2) for API calls
4. Implement exponential backoff and ETag caching for rate limit management
5. Design for GDPR compliance with configurable retention periods

**Primary recommendation:** Use Next.js 15's native `after()` API for non-blocking analytics combined with a lean PostgreSQL schema optimized for time-series queries using BRIN indexes. This approach minimizes dependencies, leverages existing infrastructure, and provides complete control over data retention for privacy compliance.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `next/server` (after API) | 15.0.3+ | Non-blocking task execution | Native Next.js feature specifically designed for analytics/logging without blocking responses |
| PostgreSQL + Prisma | 7.3.0 | Event storage | Already in stack, excellent for time-series data with JSONB flexibility |
| GitHub REST API | v3 | User profile enrichment | Already authenticated via Phase 2 OAuth, no additional libraries needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Zod | 4.3.6 | Event validation | Already in stack, validates event payloads before storage |
| `@octokit/rest` | 20.x | GitHub API client | Optional - only if complex API interactions needed beyond basic fetch |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `after()` API | PostHog/Amplitude/Plausible | Third-party tools offer dashboards/UI but add external dependencies and data leaves your control |
| PostgreSQL | MongoDB/ClickHouse | NoSQL offers schema flexibility but adds new database tech; ClickHouse optimizes for analytics but overkill for brain learning needs |
| Direct fetch | `@octokit/rest` | Octokit adds 100KB+ bundle size for minimal benefit when only calling 1-2 endpoints |

**Installation:**
```bash
# No new dependencies needed!
# after() API: Built into Next.js 15.0.3+
# GitHub API: Use native fetch with existing OAuth tokens
# PostgreSQL: Already configured in Phase 1
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── app/
│   ├── actions/
│   │   └── analytics.ts        # Server actions for manual event tracking
│   └── api/
│       └── analytics/
│           ├── track/route.ts  # Optional: Client-side event endpoint
│           └── export/route.ts # Optional: Export data for brain analysis
├── lib/
│   ├── analytics/
│   │   ├── tracker.ts          # Core event tracking logic
│   │   ├── github.ts           # GitHub API integration with rate limiting
│   │   └── types.ts            # Event type definitions
│   └── db/
│       └── queries/
│           └── analytics.ts    # Analytics-specific database queries
└── middleware.ts               # Optional: Middleware for automatic page view tracking
```

### Pattern 1: Non-Blocking Event Tracking with `after()`
**What:** Use Next.js 15's `after()` API to defer analytics logging until after the response is sent to the user
**When to use:** All analytics/logging operations that don't need to affect the response
**Example:**
```typescript
// Source: https://nextjs.org/docs/app/api-reference/functions/after
import { after } from 'next/server'
import { trackEvent } from '@/lib/analytics/tracker'

export async function POST(request: Request) {
  const data = await request.json()

  // Perform primary operation
  const result = await createTask(data)

  // Track event AFTER response is sent (non-blocking)
  after(async () => {
    await trackEvent({
      type: 'task_created',
      userId: result.userId,
      properties: { taskId: result.id, category: data.category }
    })
  })

  return Response.json({ success: true, id: result.id })
}
```

### Pattern 2: GitHub API Rate Limit Handling
**What:** Monitor rate limit headers and implement exponential backoff with ETag caching
**When to use:** All GitHub API calls for enrichment data
**Example:**
```typescript
// Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
import { headers } from 'next/headers'

interface RateLimitInfo {
  limit: number
  remaining: number
  reset: number
}

async function fetchGitHubUser(accessToken: string): Promise<GitHubUser> {
  const response = await fetch('https://api.github.com/user', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/vnd.github.v3+json',
      // ETag caching - 304 responses don't count against rate limit
      'If-None-Match': cachedEtag || ''
    }
  })

  // Extract rate limit info
  const rateLimitInfo: RateLimitInfo = {
    limit: parseInt(response.headers.get('x-ratelimit-limit') || '5000'),
    remaining: parseInt(response.headers.get('x-ratelimit-remaining') || '0'),
    reset: parseInt(response.headers.get('x-ratelimit-reset') || '0')
  }

  // If rate limited, wait until reset time
  if (response.status === 403 && rateLimitInfo.remaining === 0) {
    const waitTime = (rateLimitInfo.reset * 1000) - Date.now()
    throw new Error(`Rate limited. Retry after ${waitTime}ms`)
  }

  // Cache ETag for next request
  const etag = response.headers.get('etag')
  if (etag) cacheEtag(etag)

  if (response.status === 304) {
    return getCachedUser() // Not modified, use cache
  }

  return response.json()
}
```

### Pattern 3: Flexible Event Schema with JSONB
**What:** Store event properties as JSONB for schema flexibility while keeping core fields typed
**When to use:** Analytics events where property structure varies by event type
**Example:**
```typescript
// Prisma schema
model AnalyticsEvent {
  id         String   @id @default(cuid())
  userId     String
  eventType  String   // 'task_created', 'file_uploaded', 'search_performed'
  properties Json     // JSONB - flexible event-specific data
  createdAt  DateTime @default(now())

  user       User     @relation(fields: [userId], references: [id])

  @@index([userId, createdAt]) // Fast user timeline queries
  @@index([eventType, createdAt]) // Fast event type aggregations
  @@index([createdAt]) // BRIN-like pattern for time-series queries
}
```

### Pattern 4: Event Type System with Zod
**What:** Define strict TypeScript types for each event with runtime validation
**When to use:** Ensure type safety across analytics system and validate before storage
**Example:**
```typescript
// Source: https://github.com/colinhacks/zod
import { z } from 'zod'

const TaskCreatedEventSchema = z.object({
  type: z.literal('task_created'),
  userId: z.string(),
  properties: z.object({
    taskId: z.string(),
    category: z.string().optional(),
    fileCount: z.number().optional()
  })
})

const FileUploadedEventSchema = z.object({
  type: z.literal('file_uploaded'),
  userId: z.string(),
  properties: z.object({
    fileId: z.string(),
    taskId: z.string(),
    fileSize: z.number(),
    mimeType: z.string()
  })
})

export const AnalyticsEventSchema = z.discriminatedUnion('type', [
  TaskCreatedEventSchema,
  FileUploadedEventSchema,
  // ... other event types
])

export type AnalyticsEvent = z.infer<typeof AnalyticsEventSchema>
```

### Anti-Patterns to Avoid
- **Blocking user operations for analytics** - Never await analytics calls in user-facing code paths; always use `after()` or background jobs
- **Tracking everything without purpose** - Only track events that inform brain learning; more data ≠ more insights
- **Missing rate limit checks** - Always check GitHub API rate limit headers before making calls; hitting limits breaks user features
- **Over-indexing JSONB columns** - GIN indexes on JSONB have high write overhead; only index frequently queried properties
- **Storing PII without consent** - GDPR requires explicit consent for personal data; anonymize or pseudonymize where possible

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rate limiting logic | Custom rate limiter with timers | GitHub API headers + exponential backoff | GitHub provides x-ratelimit-* headers; custom implementations miss edge cases like secondary limits |
| Analytics dashboards | Custom React dashboard | Export to CSV → brain analysis scripts | Building dashboards is out of scope; brain learning happens in Python/analysis scripts |
| Event batching | Custom queue with batch logic | Direct database inserts with `after()` | PostgreSQL handles concurrent writes well; batching adds complexity without proven benefit at this scale |
| Session tracking | Custom cookie-based sessions | Auth.js session (already implemented) | Phase 2 already provides session management; reuse it |
| Time-series aggregations | Custom SQL aggregation functions | PostgreSQL window functions + date_trunc | PostgreSQL has battle-tested time-series capabilities; custom functions introduce bugs |

**Key insight:** The analytics requirements are simple: log events and make data queryable for brain analysis. Avoid the temptation to build a full analytics platform. The value is in the data structure, not the tooling.

## Common Pitfalls

### Pitfall 1: Blocking User Operations with Analytics Calls
**What goes wrong:** Awaiting analytics API calls or database inserts in user-facing routes adds 50-200ms latency to every operation
**Why it happens:** Developers naturally want to ensure events are tracked before responding
**How to avoid:** Always wrap analytics calls in `after(() => { ... })` so they execute after the response is sent
**Warning signs:** User complaints about slow task creation; server logs showing analytics queries in request timings

### Pitfall 2: GitHub API Rate Limit Exhaustion
**What goes wrong:** Application hits GitHub's 5,000 requests/hour limit and user profile enrichment fails
**Why it happens:** Not caching GitHub user data or making redundant API calls on every event
**How to avoid:**
  - Cache GitHub user data in database with 24-hour TTL
  - Use ETag headers for conditional requests (304 responses don't count against limit)
  - Only enrich data once per user session, not on every event
**Warning signs:** Logs showing 403 errors with "x-ratelimit-remaining: 0"; user profiles not updating

### Pitfall 3: Unbounded JSONB Growth Killing Performance
**What goes wrong:** Storing large file contents or request bodies in JSONB properties causes query performance to degrade over weeks
**Why it happens:** Treating JSONB as a dumping ground for "everything that might be useful"
**How to avoid:**
  - Set strict size limits on `properties` JSONB field (e.g., 5KB max)
  - Store large data (file contents, full request bodies) separately or not at all
  - Only store what's needed for brain pattern analysis
**Warning signs:** Analytics queries taking >1s; database storage growing faster than expected

### Pitfall 4: Missing GDPR Compliance
**What goes wrong:** Storing user email addresses or IP addresses without consent violates GDPR; potential €20M fines
**Why it happens:** Developers don't realize that "analytics" includes personal data requiring consent
**How to avoid:**
  - Use user IDs instead of emails in events
  - Anonymize IP addresses (store first 3 octets only)
  - Implement configurable retention periods (30-90 days for compliance)
  - Add data export endpoint for user requests
**Warning signs:** Legal team raises concerns; users request data deletion and system can't comply

### Pitfall 5: Over-Indexing Small Tables
**What goes wrong:** Creating GIN indexes on JSONB columns with <10K rows adds write overhead without read benefits
**Why it happens:** Premature optimization; developers add indexes "just in case"
**How to avoid:**
  - Start with B-tree indexes on typed columns (userId, eventType, createdAt)
  - Only add JSONB indexes when queries show >100ms execution time
  - Monitor index usage with `pg_stat_user_indexes`
**Warning signs:** Write operations slowing down; database showing high index maintenance time

### Pitfall 6: Cache Stampede on GitHub API Calls
**What goes wrong:** When cache expires, hundreds of concurrent requests hit GitHub API simultaneously, hitting rate limits
**Why it happens:** No locking mechanism when cache misses; all requests attempt to refresh simultaneously
**How to avoid:**
  - Use "stale-while-revalidate" pattern: serve cached data while refreshing in background
  - Implement request coalescing: deduplicate concurrent requests for same resource
  - Add jitter to cache TTLs to avoid synchronized expiration
**Warning signs:** Periodic spikes in GitHub API usage; rate limit errors in bursts

## Code Examples

Verified patterns from official sources:

### Complete Non-Blocking Event Tracker
```typescript
// Source: Next.js 15 documentation + PostgreSQL best practices
// lib/analytics/tracker.ts
import { after } from 'next/server'
import { prisma } from '@/lib/db/prisma'
import { AnalyticsEventSchema } from './types'

export async function trackEvent(event: unknown) {
  // Validate event structure
  const validatedEvent = AnalyticsEventSchema.parse(event)

  // Store in database (async, doesn't block caller)
  await prisma.analyticsEvent.create({
    data: {
      userId: validatedEvent.userId,
      eventType: validatedEvent.type,
      properties: validatedEvent.properties
    }
  })
}

// Usage in Server Actions
export async function createTaskAction(formData: FormData) {
  const task = await createTask(formData)

  // Track AFTER response sent
  after(() => {
    trackEvent({
      type: 'task_created',
      userId: task.userId,
      properties: { taskId: task.id }
    })
  })

  return { success: true, task }
}
```

### GitHub User Enrichment with Rate Limiting
```typescript
// Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
// lib/analytics/github.ts
interface GitHubUserCache {
  data: GitHubUser
  etag: string
  cachedAt: number
}

const userCache = new Map<string, GitHubUserCache>()
const CACHE_TTL = 24 * 60 * 60 * 1000 // 24 hours

export async function enrichUserWithGitHubData(
  userId: string,
  accessToken: string
): Promise<GitHubUser | null> {
  const cached = userCache.get(userId)
  const now = Date.now()

  // Return cached if still valid
  if (cached && (now - cached.cachedAt) < CACHE_TTL) {
    return cached.data
  }

  try {
    const response = await fetch('https://api.github.com/user', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/vnd.github.v3+json',
        'If-None-Match': cached?.etag || ''
      },
      // Prevent hanging requests
      signal: AbortSignal.timeout(5000)
    })

    // Handle rate limiting gracefully
    const remaining = parseInt(
      response.headers.get('x-ratelimit-remaining') || '0'
    )

    if (remaining < 100) {
      console.warn(`GitHub API rate limit low: ${remaining} remaining`)
    }

    if (response.status === 304) {
      // Not modified, extend cache
      if (cached) {
        userCache.set(userId, { ...cached, cachedAt: now })
        return cached.data
      }
    }

    if (response.status === 403 || response.status === 429) {
      const resetTime = parseInt(
        response.headers.get('x-ratelimit-reset') || '0'
      )
      console.error(
        `GitHub API rate limited. Resets at ${new Date(resetTime * 1000)}`
      )
      return cached?.data || null // Return stale data if available
    }

    const data = await response.json()
    const etag = response.headers.get('etag') || ''

    userCache.set(userId, { data, etag, cachedAt: now })
    return data

  } catch (error) {
    console.error('GitHub API error:', error)
    return cached?.data || null // Graceful degradation
  }
}
```

### Event Queries for Brain Analysis
```typescript
// Source: PostgreSQL documentation + analytics best practices
// lib/db/queries/analytics.ts
export async function getUserEventTimeline(
  userId: string,
  days: number = 30
) {
  return prisma.analyticsEvent.findMany({
    where: {
      userId,
      createdAt: {
        gte: new Date(Date.now() - days * 24 * 60 * 60 * 1000)
      }
    },
    orderBy: { createdAt: 'desc' },
    select: {
      eventType: true,
      properties: true,
      createdAt: true
    }
  })
}

export async function getFeatureUsageStats(eventType: string) {
  // Use raw SQL for complex aggregations
  return prisma.$queryRaw`
    SELECT
      DATE_TRUNC('day', "createdAt") as date,
      COUNT(*) as event_count,
      COUNT(DISTINCT "userId") as unique_users
    FROM "AnalyticsEvent"
    WHERE "eventType" = ${eventType}
      AND "createdAt" >= NOW() - INTERVAL '30 days'
    GROUP BY DATE_TRUNC('day', "createdAt")
    ORDER BY date DESC
  `
}

export async function exportEventsForBrain(
  startDate: Date,
  endDate: Date
) {
  // Export format optimized for brain analysis scripts
  return prisma.analyticsEvent.findMany({
    where: {
      createdAt: {
        gte: startDate,
        lte: endDate
      }
    },
    select: {
      eventType: true,
      properties: true,
      createdAt: true,
      user: {
        select: {
          id: true // Only user ID, no PII
        }
      }
    },
    orderBy: { createdAt: 'asc' }
  })
}
```

### GDPR-Compliant Data Retention
```typescript
// Source: https://usercentrics.com/knowledge-hub/gdpr-data-retention/
// lib/analytics/retention.ts
const DEFAULT_RETENTION_DAYS = 90 // GDPR-safe default

export async function purgeExpiredEvents() {
  const cutoffDate = new Date(
    Date.now() - DEFAULT_RETENTION_DAYS * 24 * 60 * 60 * 1000
  )

  const result = await prisma.analyticsEvent.deleteMany({
    where: {
      createdAt: {
        lt: cutoffDate
      }
    }
  })

  console.log(`Purged ${result.count} events older than ${DEFAULT_RETENTION_DAYS} days`)
  return result
}

// Run as scheduled job (e.g., daily cron)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom event queue systems | Next.js 15 `after()` API | Nov 2024 (Next.js 15.1 stable) | Eliminates need for external queue infrastructure; analytics built into framework |
| Client-side analytics only | Server-side + client hybrid | 2023+ | Better data quality, resistant to ad blockers, captures server action events |
| Separate analytics database | Single PostgreSQL for app + analytics | 2025+ | Simplified infrastructure, JSONB enables flexible schemas without schema migrations |
| Third-party analytics SaaS | Self-hosted with export capabilities | GDPR era (2018+) | Full data control, privacy compliance, no external dependencies for brain learning |
| Polling GitHub API | ETag-based conditional requests | Always recommended | 304 responses don't count against rate limits; massive savings on quota |

**Deprecated/outdated:**
- **Next.js Middleware for analytics** - While still supported, `after()` API is more efficient and doesn't add middleware overhead to every request
- **Custom error boundaries for event tracking** - Next.js 15 added `onRequestError` hook for better error tracking integration
- **@vercel/analytics** - Vercel's analytics package; ties you to Vercel platform and sends data externally (conflicts with brain learning goal)
- **React Context for event tracking** - Server Actions + `after()` eliminates need for client-side tracking context in most cases

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal retention period for brain learning**
   - What we know: GDPR allows up to 26 months with proper consent; analytics platforms typically use 90 days default
   - What's unclear: How long does the brain learning system need data before patterns are extracted?
   - Recommendation: Start with 90-day retention, make configurable, extend if brain analysis shows longer periods improve pattern quality

2. **Event sampling vs. full tracking**
   - What we know: High-traffic apps sample events (e.g., 10%) to reduce storage costs
   - What's unclear: At what scale does sampling become necessary? Will brain learning need 100% data fidelity?
   - Recommendation: Track 100% initially; add sampling configuration if database exceeds 1M events/month

3. **Real-time vs. batch export for brain**
   - What we know: Brain analysis scripts could pull data real-time (API) or batch (daily export)
   - What's unclear: Brain architecture hasn't specified preferred data ingestion method
   - Recommendation: Implement both - API endpoint for real-time queries, scheduled export for batch analysis

4. **Multi-project pattern aggregation**
   - What we know: Brain should learn from patterns across all MyWork projects
   - What's unclear: Should events include project metadata? How to correlate patterns across projects?
   - Recommendation: Add `projectId` to events, defer cross-project aggregation to brain analysis layer

## Sources

### Primary (HIGH confidence)
- [Next.js `after()` API Documentation](https://nextjs.org/docs/app/api-reference/functions/after) - Official Next.js 15 feature documentation
- [Next.js Analytics Guide](https://nextjs.org/docs/pages/guides/analytics) - Official framework analytics guidance
- [GitHub REST API Rate Limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) - Authoritative GitHub API documentation
- [GitHub REST API Best Practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api) - Official GitHub guidance
- [Prisma Documentation](https://www.prisma.io/docs/orm/prisma-schema) - Prisma schema and querying documentation

### Secondary (MEDIUM confidence)
- [Event Storage in Postgres](https://dev.to/kspeakman/event-storage-in-postgres-4dk2) - Verified PostgreSQL event schema patterns
- [BRIN Indexes in PostgreSQL](https://www.sqlpassion.at/archive/2026/01/19/brin-indexes-in-postgresql/) - Time-series indexing strategy
- [GDPR Data Retention Best Practices](https://usercentrics.com/knowledge-hub/gdpr-data-retention/) - Compliance guidance
- [PostgreSQL JSONB Indexing](https://www.tigerdata.com/learn/how-to-index-json-columns-in-postgresql) - Performance optimization
- [API Rate Limiting Best Practices 2025](https://zuplo.com/learning-center/10-best-practices-for-api-rate-limiting-in-2025) - Verified rate limiting patterns

### Tertiary (LOW confidence)
- [Next.js Server Actions Analytics Patterns](https://medium.com/@beenakumawat002/next-js-app-router-advanced-patterns-for-2026-server-actions-ppr-streaming-edge-first-b76b1b3dcac7) - Community patterns (Medium article)
- [Event Tracking Schema Design](https://snowplow.io/blog/event-data-structure) - General analytics schema guidance (not Next.js-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Next.js 15 `after()` API is official, PostgreSQL + Prisma already in use
- Architecture: HIGH - Patterns verified with official documentation and real-world implementations
- Pitfalls: MEDIUM - Common issues documented across multiple sources, some inferred from general analytics experience

**Research date:** 2026-01-25
**Valid until:** 2026-02-24 (30 days - analytics space stable, Next.js 15 mature)
