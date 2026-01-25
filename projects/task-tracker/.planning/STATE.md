# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-24)

**Core value:** Validate that the MyWork framework can deliver production-quality applications with reusable modules that accelerate future development
**Current focus:** Phase 2 - Authentication & Profiles

## Current Position

Phase: 2 of 8 (Authentication & Profiles)
Plan: 4 of 5 in current phase
Status: In progress
Last activity: 2026-01-24 — Completed 02-04-PLAN.md (Profile settings, auto-save, user menu, logout)

Progress: [█████░░░░░] 80%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: 18 minutes
- Total execution time: 2.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 | 3 | 18 min | 6 min |
| Phase 2 | 4 | 96 min | 24 min |

**Recent Trend:**
- Last 5 plans: 02-01 (8 min), 02-02 (34 min), 02-03 (50 min), 02-04 (4 min)
- Trend: TypeScript fixes were quick (4 min) - velocity improving as framework issues resolved

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

Last session: 2026-01-24 (phase 2 execution)
Stopped at: Completed 02-04-PLAN.md (Profile settings with auto-save)
Resume file: None
Next: 02-05-PLAN.md (Dashboard and full OAuth verification)

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
