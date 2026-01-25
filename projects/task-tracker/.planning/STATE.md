# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-24)

**Core value:** Validate that the MyWork framework can deliver production-quality applications with reusable modules that accelerate future development
**Current focus:** Phase 5 - File Attachments (Ready to plan)

## Current Position

Phase: 5 of 8 (File Attachments)
Plan: 3 of 7 in current phase
Status: In progress
Last activity: 2026-01-25 — Completed 05-03-PLAN.md

Progress: [████████░░] 79%

## Performance Metrics

**Velocity:**
- Total plans completed: 24
- Average duration: 7 minutes
- Total execution time: 4.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 | 3 | 18 min | 6 min |
| Phase 2 | 5 | 77 min | 15 min |
| Phase 3 | 4 | 22 min | 5.5 min |
| Phase 4 | 5 | 30 min | 6 min |
| Phase 5 | 2 | 9 min | 4.5 min |
| Phase 6 | 3 | 10 min | 3 min |

**Recent Trend:**
- Last 5 plans: 05-03 (5 min), 05-01 (4 min), 04-05 (5 min), 04-04 (3 min), 04-03 (11 min)
- Trend: Phase 5 maintaining excellent 4-5 min velocity per plan

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table and plan SUMMARY files.
Recent decisions affecting current work:

- **TECH-001** (2026-01-26): Use Next.js 15.5.9 instead of 16.x due to React 19 compatibility issues (patched build)
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
- **TASK-001** (2026-01-25): TaskStatus enum instead of string for type safety at database and application level
- **TASK-002** (2026-01-25): Separate updateTaskStatus action enables optimistic UI updates for status changes
- **TASK-003** (2026-01-25): Cascade delete tasks when user is deleted to prevent orphaned records
- **UI-006** (2026-01-25): Optimistic UI for status updates provides instant feedback before server confirmation
- **UI-007** (2026-01-25): Status dropdown for quick inline status changes without navigation
- **UI-008** (2026-01-25): Delete confirmation dialog prevents accidental task deletion
- **UI-009** (2026-01-25): Done tasks faded but visible maintains task history awareness
- **SEARCH-001** (2026-01-25): Use PostgreSQL tsvector over external search service (validation project scale)
- **SEARCH-002** (2026-01-25): Two-tier search strategy (FTS primary, fuzzy fallback) for better UX
- **SEARCH-003** (2026-01-25): Generated tsvector column instead of triggers (PostgreSQL 12+ native feature)
- **TAG-001** (2026-01-25): Implicit many-to-many over explicit join table (simpler Prisma API)
- **URL-STATE-001** (2026-01-25): Use nuqs for URL state management (type-safe, shareable URLs, back/forward support)
- **DEBOUNCE-001** (2026-01-25): 500ms debounce for search input balances instant feedback with server load
- **FILTER-001** (2026-01-25): Apply filters client-side to search results to preserve FTS ranking
- **UI-010** (2026-01-25): Tag colors assigned randomly from preset palette for visual variety
- **UI-011** (2026-01-25): Max 3 tags visible on task cards with +N more overflow indicator
- **PATTERN-006** (2026-01-25): Autocomplete dropdown with create-on-enter UX pattern
- **PATTERN-007** (2026-01-25): Edit form tag sync with optimistic UI and server rollback on error
- **UI-012** (2026-01-25): EmptyState component provides reusable zero-state UI with customizable icon and CTA
- **UI-013** (2026-01-25): Context-aware empty states: different messages for no tasks vs no results
- **PATTERN-008** (2026-01-25): Integrated wrapper pattern - Client component combines Server Component data
- **QUALITY-001** (2026-01-25): Phase 4 validated for production through comprehensive manual testing
- **FILE-001** (2026-01-26): Content-based MIME validation over client-provided types for security
- **FILE-002** (2026-01-26): 25MB file size limit with 5MB Server Actions threshold (TUS protocol for >5MB)
- **FILE-003** (2026-01-26): FileAttachment with denormalized userId for direct ownership checks
- **FILE-004** (2026-01-26): Cascade delete file attachments when task deleted to prevent orphaned records
- **THUMB-001** (2026-01-25): 200px square WebP thumbnails at 80% quality for optimal compression
- **SECURITY-001** (2026-01-25): Verify ownership on every download request via database query
- Framework validation approach: Task tracker serves as seed data for brain - every working pattern becomes an asset
- GitHub integration mandatory: Essential for tracking which patterns actually work in real usage
- Ship quickly for validation: MVP must be deployed and accessible for real user testing to validate brain learning

### Pending Todos

None yet.

### Blockers/Concerns

None currently. (Build issue resolved by upgrading Next.js to 15.5.9.)

**User setup still required for testing:**
- GitHub OAuth app must be created and credentials added to .env
- AUTH_SECRET must be generated with `npx auth secret`
- Without these, authentication flow will fail at runtime

## Session Continuity

Last session: 2026-01-25 (phase 5 plan 03)
Stopped at: Completed 05-03-PLAN.md
Resume file: None
Next: 05-02 - File storage utilities and TUS upload endpoint (partial - storage already created), or 05-04 - UI components

**Phase 5 Progress:**
- ✅ FileAttachment model with Task cascade delete
- ✅ Content-based MIME validation using magic bytes
- ✅ File size validation (25MB limit, 5MB Server Actions threshold)
- ✅ File upload dependencies installed (react-dropzone, file-type, sharp, tus-*)
- ✅ Next.js configured with 5MB bodySizeLimit
- ✅ Helper utilities: formatFileSize, shouldUseTusProtocol, getExtensionFromMime, isImageMime
- ✅ Thumbnail generator with Sharp (200px WebP)
- ✅ File storage utilities (saveFile, readFile, deleteFile)
- ✅ Server Actions (uploadFile, deleteFileAction, getTaskFiles)
- ✅ Download endpoint at /api/files/download/[id] with authentication
- ✅ DAL file functions (getFilesByTask, getFile, getTaskFileCount, getTaskWithFiles)
- 2 of 7 plans complete (05-01, 05-03)

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
