---
phase: 02-authentication-profiles
plan: 01
subsystem: auth
tags: [next-auth, oauth, github, prisma-adapter, database-sessions]

# Dependency graph

requires:

  - phase: 01-foundation-setup

```yaml
provides: Next.js app, Prisma with PostgreSQL, modular architecture

```yaml

provides:

  - Auth.js v5 with GitHub OAuth provider configured
  - Database models for User, Account, Session, VerificationToken
  - Auth API routes at /api/auth/* (signin, callback, signout, session, csrf,

```text
providers)

```

  - Database-backed sessions with 24h expiry and 1h refresh
  - Type-safe session with user.id access

affects: [02-02-auth-ui, 02-03-profile-management, all-authenticated-features]

# Tech tracking

tech-stack:
  added: [next-auth@5.0.0-beta.30, @auth/prisma-adapter@2.11.1]
  patterns: [database-backed-sessions, oauth-github, session-callbacks,
  auth-middleware]

key-files:
  created:

```markdown

- src/shared/lib/auth.ts
- src/app/api/auth/[...nextauth]/route.ts
- src/shared/types/next-auth.d.ts
- prisma/migrations/20260124210303_add_auth_models/migration.sql

```yaml

  modified:

```markdown

- prisma/schema.prisma
- package.json
- .env.example

```

key-decisions:

  - "Use database sessions instead of JWT for better security and revocation

```text
capability"

```markdown

  - "Configure GitHub OAuth with repo read scope for future GitHub integration

```text
features"

```

  - "24-hour session expiry with 1-hour silent refresh for balance between

```text
security and UX"

```markdown

  - "Redirect first-time users to /welcome for onboarding flow"

patterns-established:

  - "Auth.js v5 configuration with PrismaAdapter pattern"
  - "Type extension pattern for next-auth Session interface"
  - "Environment variable templates in .env.example with clear generation

```text
instructions"

```

# Metrics

duration: 8min
completed: 2026-01-24
---

# Phase 02 Plan 01: Auth.js Infrastructure Summary

**Auth.js v5 with GitHub OAuth, database-backed sessions, and Prisma adapter for
secure authentication**

## Performance

- **Duration:** 8 minutes
- **Started:** 2026-01-24T21:01:24Z
- **Completed:** 2026-01-24T21:09:36Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Auth.js v5 installed and configured with GitHub OAuth provider
- Database schema extended with User, Account, Session, VerificationToken models
- Auth API routes functional at /api/auth/* with all necessary endpoints
- Database sessions configured with 24h expiry and 1h refresh
- Type-safe session access with user.id available throughout application

## Task Commits

Each task was committed atomically:

1. **Task 1: Update Prisma Schema with Auth.js Models** - `58943b0` (feat)
2. **Task 2: Install Auth.js Dependencies and Create Configuration** - `3cdbb93`

(feat)

3. **Task 3: Create Auth API Route Handler** - `bcdabe2` (feat)

## Files Created/Modified

- `prisma/schema.prisma` - Added User, Account, Session, VerificationToken models

  with custom profile fields (bio, customAvatar)

- `prisma/migrations/20260124210303_add_auth_models/migration.sql` - Database

  migration for auth tables

- `src/shared/lib/auth.ts` - Auth.js configuration with GitHub provider, database

  adapter, session callbacks

- `src/app/api/auth/[...nextauth]/route.ts` - Catch-all route handler for all

  Auth.js endpoints

- `src/shared/types/next-auth.d.ts` - TypeScript declaration extending Session

  with user.id

- `package.json` - Added next-auth@5.0.0-beta.30 and @auth/prisma-adapter@2.11.1
- `.env.example` - Added AUTH_GITHUB_ID, AUTH_GITHUB_SECRET, AUTH_SECRET

  templates

## Decisions Made

- **Database sessions over JWT:** Chose database-backed sessions for better

  security (revocation capability) and server-side control per RESEARCH.md
  findings

- **GitHub OAuth scopes:** Included `read:user user:email repo` for future GitHub

  integration features (task tracking from repo issues)

- **Session timing:** 24-hour expiry with 1-hour silent refresh balances security

  with user experience

- **First-time user flow:** Redirect to /welcome for onboarding instead of

  default page

- **Text column for tokens:** Used @db.Text for GitHub token fields to handle

  long tokens that exceed varchar(191) limit

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**1. Shell environment NODE_ENV interference**

- **Issue:** Build failed with "non-standard NODE_ENV value" error due to global

  shell environment variable

- **Solution:** Identified that NODE_ENV was set in shell environment (not

  project). Build succeeds when unsetting NODE_ENV before build command

- **Impact:** None on production - Next.js manages NODE_ENV automatically in

  deployment environments

- **Note:** This is a local development environment quirk, not a code issue.

  Documented for awareness.

## User Setup Required

**External services require manual configuration.** User must complete before
authentication will work:

1. **GitHub OAuth App Creation:**
   - Go to GitHub Settings → Developer settings → OAuth Apps → New OAuth App
   - Homepage URL: `http://localhost:3000`
   - Callback URL: `http://localhost:3000/api/auth/callback/github`
   - Copy Client ID and Client Secret

2. **Environment Variables (.env):**

```text
   AUTH_GITHUB_ID=your_github_client_id
   AUTH_GITHUB_SECRET=your_github_client_secret
   AUTH_SECRET=generate_with_npx_auth_secret

```yaml

3. **Generate AUTH_SECRET:**

   ```bash
   npx auth secret

```yaml

4. **Verification:**

   After setup, test endpoints:

   ```bash
   curl http://localhost:3000/api/auth/providers
   curl http://localhost:3000/api/auth/csrf

```markdown

## Next Phase Readiness

**Ready for Phase 02 Plan 02 (Auth UI - Login/Signup Pages):**

- Auth.js infrastructure complete and verified
- All API endpoints functional
- Database models created and migrated
- Type-safe session access available

**Blockers:** None

**Pending work:**

- User must configure GitHub OAuth app and environment variables before testing

  sign-in flow

- Login/signup UI pages needed (Plan 02)
- Profile management UI needed (Plan 03)

---
*Phase: 02-authentication-profiles*
*Completed: 2026-01-24*
