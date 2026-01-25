# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-24)

**Core value:** Validate that the MyWork framework can deliver production-quality applications with reusable modules that accelerate future development
**Current focus:** Phase 2 - Authentication & Profiles (Complete)

## Current Position

Phase: 2 of 8 (Authentication & Profiles)
Plan: 5 of 5 in current phase
Status: Phase complete
Last activity: 2026-01-25 — Completed 02-05-PLAN.md (Dashboard and OAuth flow verification)

Progress: [███░░░░░░░] 38%

## Performance Metrics

**Velocity:**
- Total plans completed: 13
- Average duration: 13 minutes
- Total execution time: 2.9 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 | 3 | 18 min | 6 min |
| Phase 2 | 5 | 77 min | 15 min |
| Phase 6 | 3 | 10 min | 3 min |

**Recent Trend:**
- Last 5 plans: 02-03 (50 min), 02-04 (4 min), 02-05 (5 min), 06-01 (3 min), 06-02 (3 min)
- Trend: Phase 2 complete with excellent velocity after initial setup (avg 15 min/plan)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table and plan SUMMARY files.
Recent decisions affecting current work:

- **TECH-001** (2026-01-24): Use Next.js 15.0.3 instead of 16.x due to React 19 compatibility issues
- **ARCH-001** (2026-01-24): Modular monolith architecture for clean module extraction to framework brain
- **TECH-002** (2026-01-24): TypeScript strict mode enabled for type safety across entire application
- **TECH-003** (2026-01-24): Prisma 7 with PostgreSQL adapter for database connection pooling
- **CONFIG-001** (2026-01-24): Local PostgreSQL user 'dansidanutz' instead of 'postgres'
- **CONFIG-002** (2026-01-24): Remove NODE_ENV from .env files - Next.js manages it automatically
- **PATTERN-001** (2026-01-24): Prisma singleton pattern with globalThis for connection pool management
- **PATTERN-002** (2026-01-24): Environment validation for user-controlled variables only, framework-managed accessed directly
- **AUTH-001** (2026-01-24): Database sessions over JWT for better security and revocation capability
- **AUTH-002** (2026-01-24): GitHub OAuth with repo read scope for future GitHub integration features
- **AUTH-003** (2026-01-24): 24-hour session expiry with 1-hour silent refresh for security/UX balance
- **AUTH-004** (2026-01-24): Use React cache() in DAL for request deduplication
- **AUTH-005** (2026-01-24): Middleware only checks session cookie, not database (performance)
- **PATTERN-003** (2026-01-24): 3000ms debounce delay for auto-save pattern
- **UI-001** (2026-01-24): Server Actions for OAuth to keep credentials server-side
- **UI-002** (2026-01-24): Conditional homepage CTAs based on auth state
- **UI-003** (2026-01-24): Post-OAuth redirect to /welcome for onboarding
- **AUTO-SAVE-001** (2026-01-24): 3-second debounce for profile updates balances responsiveness and server load
- **UI-004** (2026-01-24): Separate debounced functions per field for TypeScript type safety
- **PATTERN-004** (2026-01-24): Field-level Server Actions enable granular auto-save without full form submission
- **UI-005** (2026-01-24): Visual status indicators (saving/saved/error) for auto-save user feedback
- **CACHE-001** (2026-01-25): 24-hour in-memory cache for GitHub user data (validation project scale)
- **RATE-001** (2026-01-25): Warn at 100 remaining requests, graceful degradation on exhaustion
- **PATTERN-005** (2026-01-25): ETag-based conditional requests to minimize rate limit consumption
- **DATA-001** (2026-01-25): 90-day retention period balances brain learning with GDPR compliance
- **EXPORT-001** (2026-01-25): Export API requires authentication to prevent unauthorized data access
- **QUERY-001** (2026-01-25): Summary mode for quick analytics overview without full export
- Framework validation approach: Task tracker serves as seed data for brain - every working pattern becomes an asset
- GitHub integration mandatory: Essential for tracking which patterns actually work in real usage
- Ship quickly for validation: MVP must be deployed and accessible for real user testing to validate brain learning

### Pending Todos

None yet.

### Blockers/Concerns

**Build Issue (critical for deployment):**
- Next.js 15.0.3 has a webpack bundling bug causing production builds to fail
- Error: Pages Router components incorrectly bundled in App Router builds
- Workaround: Development server works correctly
- Resolution needed: Either wait for Next.js fix or find Edge Runtime workaround
- Impact: Cannot deploy to production until resolved

**User setup still required for testing:**
- GitHub OAuth app must be created and credentials added to .env
- AUTH_SECRET must be generated with `npx auth secret`
- Without these, authentication flow will fail at runtime

## Session Continuity

Last session: 2026-01-25 (phase 2 completion)
Stopped at: Completed 02-05-PLAN.md (Dashboard and OAuth flow verification)
Resume file: None
Next: Phase 2 complete - ready for Phase 3 (Core Task Management)

**Phase 2 Achievement:**
- Complete authentication system with GitHub OAuth
- User profile management with auto-save
- Session persistence (24-hour expiry)
- Route protection and error handling
- All 5 plans completed, human verification passed

Config (if exists):
{
  "mode": "yolo",
  "depth": "comprehensive",
  "parallelization": true,
  "commit_docs": true,
  "model_profile": "balanced",
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true
  }
}
