---
phase: 08-deployment-validation
plan: 01
subsystem: infra
tags: [security-headers, health-monitoring, rate-limiting,
environment-validation, upstash, next.js, production]

# Dependency graph

requires:

  - phase: 01-foundation

```
provides: Next.js config, environment validation foundation

```
  - phase: 02-authentication

```
provides: Auth.js environment variables (AUTH_SECRET, AUTH_GITHUB_ID,
AUTH_GITHUB_SECRET)

```
provides:

  - Security headers for XSS, clickjacking, and content sniffing protection
  - Enhanced health check endpoint with database connectivity and uptime

```
monitoring

```
  - Production environment validation with Zod schema
  - Optional rate limiting middleware (when Upstash configured)

affects: [08-03-deployment, production-readiness, monitoring]

# Tech tracking

tech-stack:
  added: [@upstash/ratelimit, @upstash/redis]
  patterns:

```
- Security headers via Next.js headers() function
- Environment validation at import time with Zod
- Conditional rate limiting with graceful degradation
- Edge Runtime compatible dynamic imports

```
key-files:
  created:

```
- src/shared/lib/env.ts (extended with production variables)

```
  modified:

```
- next.config.ts (added security headers)
- src/app/api/health/route.ts (enhanced with uptime and structured response)
- src/middleware.ts (added conditional rate limiting)

```
key-decisions:

  - "SECURITY-002: Security headers applied via Next.js config headers() function

```
to all routes"

```
  - "SECURITY-003: Environment validation extended to include Auth.js variables

```
(AUTH_SECRET min 32 chars)"

```
  - "RATE-002: Rate limiting is optional - graceful degradation when Upstash not

```
configured (MVP friendly)"

```
  - "RATE-003: 60 requests per minute sliding window for API routes only"
  - "MONITOR-001: Health check returns 503 when database unhealthy for load

```
balancer detection"

```
patterns-established:

  - "Security headers pattern: Define once in next.config.ts, apply to all routes

```
automatically"

```
  - "Environment validation pattern: Extend Zod schema, fail fast at import time"
  - "Graceful degradation pattern: Check for optional env vars, conditionally

```
initialize features"

```
  - "Edge Runtime pattern: Dynamic import of Node.js libraries to avoid build

```
errors"

```
# Metrics

duration: 7min
completed: 2026-01-26
---

# Phase 8 Plan 01: Deployment Foundation Summary

**Production-ready security headers, health monitoring with database checks,
environment validation for Auth.js variables, and optional rate limiting with
Upstash**

## Performance

- **Duration:** 7 minutes
- **Started:** 2026-01-26T03:38:56Z
- **Completed:** 2026-01-26T03:45:56Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Security headers protect against XSS, clickjacking, MIME sniffing, and restrict
  browser APIs
- Health check endpoint provides structured status for monitoring and load
  balancers
- Production environment validation catches missing Auth.js credentials at
  startup
- Rate limiting protects API routes from abuse when Upstash is configured

## Task Commits

Each task was committed atomically:

1. **Task 1: Add security headers to Next.js config** - `022406d` (feat)
2. **Task 2: Enhance health check endpoint** - `031ef8f` (feat)
3. **Task 3: Create environment validation and rate limiting** - `697a231`
(feat)

## Files Created/Modified

- `next.config.ts` - Added security headers (X-Content-Type-Options,
  X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy)
- `src/app/api/health/route.ts` - Enhanced with uptime, timestamp, database
  connectivity check, structured JSON response
- `src/shared/lib/env.ts` - Extended schema with AUTH_SECRET (min 32 chars),
  AUTH_GITHUB_ID, AUTH_GITHUB_SECRET, optional UPSTASH_* variables
- `src/middleware.ts` - Added conditional rate limiting with dynamic Upstash
  imports, Edge Runtime compatible

## Decisions Made

**SECURITY-002: Security headers via Next.js config**

- Applied to all routes (/:path*) using headers() function
- Includes X-Content-Type-Options, X-Frame-Options, X-XSS-Protection,
  Referrer-Policy, Permissions-Policy
- Verified via HTTP response headers in dev mode
- Note: HSTS not added - Vercel adds this automatically for HTTPS domains

**SECURITY-003: Environment validation for Auth.js**

- Extended Zod schema to validate AUTH_SECRET (min 32 characters)
- Added AUTH_GITHUB_ID and AUTH_GITHUB_SECRET validation
- Fails fast at import time if misconfigured
- Note: NEXTAUTH_URL not included - Auth.js v5 infers it automatically

**RATE-002: Optional rate limiting**

- Only initializes when UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN are
  set
- Graceful degradation: silently skips if not configured (MVP friendly)
- Supports testing and development without Upstash subscription

**RATE-003: 60 requests per minute sliding window**

- Applied to API routes only (pathname.startsWith('/api'))
- Uses Upstash Ratelimit with sliding window algorithm
- Returns 429 with X-RateLimit-Remaining and X-RateLimit-Reset headers
- IP-based limiting using x-forwarded-for header

**MONITOR-001: Health check 503 on database failure**

- Returns 503 status code when database is unreachable
- Enables load balancers to detect unhealthy instances
- Includes structured response with database status, uptime, timestamp

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Attempted fix to global-error.tsx suppressHydrationWarning**

- **Found during:** Task 1 (production build verification)
- **Issue:** Pre-existing production build error: "<Html> should not be imported
  outside of pages/_document" during static page generation
- **Attempted fix:** Added suppressHydrationWarning to <html> and <body> tags in
  global-error.tsx
- **Result:** Issue persists - appears to be a Next.js 15.5.9 build-time error
  unrelated to our code changes
- **Files modified:** src/app/global-error.tsx
- **Verification:** Dev mode works correctly, security headers verified via curl
- **Note:** Build error is pre-existing from Phase 7 (documented as fixed but
  still occurring) - does NOT block dev server or runtime functionality. All new
  features work correctly in development.

---

**Total deviations:** 1 attempted bug fix (build error persists, does not block
functionality)
**Impact on plan:** Attempted to resolve pre-existing build error. All planned
functionality (security headers, health check, environment validation, rate
limiting) works correctly in development mode. Build error requires further
investigation in future maintenance.

## Issues Encountered

**Pre-existing production build error**

- Next.js build fails during static page generation with "Html import" error
- Error is unrelated to changes in this plan (persists even when removing
  global-error.tsx)
- Dev server works correctly, all runtime functionality verified
- All new features (security headers, health check, rate limiting) work as
  expected
- Build error was documented as fixed in Phase 7 but continues to occur
- Requires separate investigation - may be Next.js 15.5.9 specific issue

**Edge Runtime compatibility with Upstash**

- Middleware runs in Edge Runtime, which has limited Node.js APIs
- Solution: Dynamic import of @upstash/ratelimit and @upstash/redis
- Works correctly because Upstash libraries use fetch() API (Edge compatible)
- Tested and verified: rate limiting initializes properly, middleware functions
  correctly

## User Setup Required

**External services require manual configuration.** This plan adds environment
variable validation that will require user action before deployment:

**Required for authentication:**

- `AUTH_SECRET` - Generate with `npx auth secret`
- `AUTH_GITHUB_ID` - From GitHub OAuth app settings
- `AUTH_GITHUB_SECRET` - From GitHub OAuth app settings

**Optional for rate limiting:**

- `UPSTASH_REDIS_REST_URL` - From Upstash Console → Redis Database → REST API URL
- `UPSTASH_REDIS_REST_TOKEN` - From Upstash Console → Redis Database → REST API
  Token
- Note: Rate limiting gracefully skips if these are not set (MVP friendly)

**Validation:**
The app will fail to start if required environment variables are missing or
invalid (e.g., AUTH_SECRET < 32 characters).

## Next Phase Readiness

**Ready:**

- Security headers configured and verified
- Health check endpoint enhanced for production monitoring
- Environment validation catches configuration errors at startup
- Rate limiting framework in place (optional activation)

**Concerns:**

- Pre-existing production build error continues (documented, does not block
  runtime)
- Need to investigate Next.js 15.5.9 static page generation issue

**Blockers:**

- None - all planned functionality complete and working in development mode

**Next steps:**

- Plan 08-02: Feedback widget for user input collection
- Plan 08-03: CI/CD pipeline and Vercel deployment
- Plan 08-04: Production verification checkpoint

---
*Phase: 08-deployment-validation*
*Completed: 2026-01-26*
