# Phase 2: Authentication & Profiles - Research

**Researched:** 2026-01-24
**Domain:** Next.js 15 Authentication with GitHub OAuth
**Confidence:** HIGH

## Summary

This phase implements authentication and profile management using GitHub OAuth
in a Next.js 15 application. The standard approach in 2026 is to use Auth.js v5
(formerly NextAuth.js) with the Prisma adapter for database-backed sessions.
Auth.js provides a complete authentication solution with built-in GitHub OAuth
support, automatic CSRF protection, and seamless Next.js App Router integration.

The research focused on three critical areas: (1) Auth.js v5 implementation with
Next.js 15 and Prisma 7, (2) GitHub OAuth configuration including scopes and
rate limit handling, and (3) profile management patterns including auto-save and
avatar uploads. The user context decisions are locked: GitHub OAuth is
mandatory, sessions last 24 hours with silent refresh, profile fields auto-save,
and GitHub data takes precedence over custom data.

**Primary recommendation:** Use Auth.js v5 (`next-auth@beta`) with Prisma
adapter for database sessions, implement conditional requests with ETags for
GitHub API caching, and use Server Actions for profile updates with optimistic
UI patterns.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
| next-auth | v5 (beta) | Authenticat... | Official Au... |
  | @auth/prism... | latest | Session sto... | Official ad... |  
  | jose | latest | JWT operations | Recommended... |  
  | bcrypt | latest | Password ha... | Industry st... |  

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
  | @vercel/blob | latest | Avatar storage | File upload... |  
  | uploadthing | latest | Alternative... | Better for ... |  
  | zod | ^4.3.6 | Validation | Already in ... |  
| react-hook-... | latest | Form state ... | Optional fo... |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
  | Auth.js v5 | Better Auth | Better Auth is new... |  
| Database sessions | JWT-only sessions | JWT is simpler but... |
  | Vercel Blob | Cloudflare R2 / S3 | R2/S3 have no file... |  

**Installation:**

```bash
npm install next-auth@beta @auth/prisma-adapter jose bcrypt
npm install @vercel/blob  # for avatar uploads
npm install -D @types/bcrypt

```markdown

## Architecture Patterns

### Recommended Project Structure

```
src/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts          # Auth.js route handlers
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx              # Login page
│   │   └── welcome/
│   │       └── page.tsx              # Post-OAuth onboarding
│   ├── (app)/
│   │   └── settings/
│   │       └── profile/
│   │           └── page.tsx          # Profile management
│   └── actions/
│       └── profile.ts                # Server Actions for profile updates
├── lib/
│   ├── auth.ts                       # Auth.js configuration
│   ├── dal.ts                        # Data Access Layer (authorization)
│   └── session.ts                    # Session utilities (if using JWT)
└── middleware.ts                     # Auth middleware for route protection

```markdown

### Pattern 1: Auth.js Configuration with GitHub OAuth

**What:** Central auth configuration with GitHub provider and Prisma adapter
**When to use:** Always - this is the foundation of the authentication system
**Example:**

```typescript

// lib/auth.ts
// Source: https://authjs.dev/reference/nextjs
import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [

```
GitHub({
  clientId: process.env.AUTH_GITHUB_ID!,
  clientSecret: process.env.AUTH_GITHUB_SECRET!,
  authorization: {
    params: {
      // Scopes: user profile + email + repo read access
      scope: "read:user user:email repo"
    }
  }
})

```
  ],
  session: {

```
strategy: "database",  // Use database sessions (not JWT)
maxAge: 24 * 60 * 60,  // 24 hours (per user context)
updateAge: 60 * 60,    // Refresh every hour (silent refresh)

```
  },
  callbacks: {

```
async session({ session, user }) {
  // Add user ID to session
  session.user.id = user.id
  return session
},
async redirect({ url, baseUrl }) {
  // Redirect to welcome after OAuth (per user context)
  if (url.startsWith(baseUrl)) return url
  return `${baseUrl}/welcome`
}

```
  },
  pages: {

```
signIn: '/login',
error: '/login',  // Redirect errors to login (per user context)

```
  }
})

```

### Pattern 2: Data Access Layer (DAL) with Authorization

**What:** Centralized authorization checks using React cache() to prevent
duplicate queries
**When to use:** Every Server Component, Server Action, and Route Handler that
needs auth
**Example:**

```typescript

// lib/dal.ts
// Source: https://nextjs.org/docs/app/building-your-application/authentication
import 'server-only'
import { cache } from 'react'
import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'

export const verifySession = cache(async () => {
  const session = await auth()

  if (!session?.user?.id) {

```
redirect('/login')

```
  }

  return { isAuth: true, userId: session.user.id }
})

export const getUser = cache(async () => {
  const session = await verifySession()

  const user = await prisma.user.findUnique({

```
where: { id: session.userId },
select: {
  id: true,
  name: true,
  email: true,
  image: true,
  // Don't select sensitive fields
}

```
  })

  return user
})

```markdown

### Pattern 3: Auto-Save Profile Pattern with Server Actions

**What:** Debounced auto-save using Server Actions with optimistic UI updates
**When to use:** Profile editing, any form that auto-saves (per user context)
**Example:**

```typescript

// app/actions/profile.ts
// Source: https://darius-marlowe.medium.com/smarter-forms-in-react-building-a-useautosave-hook-with-debounce-and-react-query-d4d7f9bb052e
'use server'

import { verifySession } from '@/lib/dal'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function updateProfile(formData: FormData) {
  const session = await verifySession()

  const name = formData.get('name') as string
  const bio = formData.get('bio') as string

  await prisma.user.update({

```
where: { id: session.userId },
data: { name, bio }

```
  })

  revalidatePath('/settings/profile')
  return { success: true }
}

// Client component with debounced auto-save
'use client'

import { useTransition } from 'react'
import { useDebounce } from '@/hooks/useDebounce'

export function ProfileForm({ user }) {
  const [isPending, startTransition] = useTransition()

  const handleChange = useDebounce((e: React.ChangeEvent<HTMLInputElement>) => {

```
const formData = new FormData()
formData.set(e.target.name, e.target.value)

startTransition(async () => {
  await updateProfile(formData)
})

```
  }, 3000)  // 3 second debounce (standard pattern)

  return (

```
<form>
  <input name="name" defaultValue={user.name} onChange={handleChange} />
  {isPending && <span>Saving...</span>}
</form>

```
  )
}

```

### Pattern 4: GitHub API Caching with Conditional Requests

**What:** ETags and conditional requests to avoid rate limits (GitHub gives 304
responses for free)
**When to use:** Any GitHub API calls that fetch profile/repo data
**Example:**

```typescript

// lib/github.ts
// Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api

interface CacheEntry {
  data: any
  etag: string
  lastModified: string
}

const cache = new Map<string, CacheEntry>()

export async function fetchGitHubData(
  url: string,
  accessToken: string
) {
  const cached = cache.get(url)

  const headers: HeadersInit = {

```
'Authorization': `Bearer ${accessToken}`,
'Accept': 'application/vnd.github.v3+json'

```
  }

  // Add conditional request headers
  if (cached) {

```
if (cached.etag) headers['If-None-Match'] = cached.etag
if (cached.lastModified) headers['If-Modified-Since'] = cached.lastModified

```
  }

  const response = await fetch(url, { headers })

  // 304 Not Modified - no rate limit impact!
  if (response.status === 304 && cached) {

```
return cached.data

```
  }

  // Store new etag/last-modified
  const etag = response.headers.get('etag') || ''
  const lastModified = response.headers.get('last-modified') || ''
  const data = await response.json()

  cache.set(url, { data, etag, lastModified })
  return data
}

```markdown

### Pattern 5: Middleware for Route Protection

**What:** Optimistic auth checks in middleware for protected routes
**When to use:** Route-level protection (lightweight cookie checks only, no DB
queries)
**Example:**

```typescript

// middleware.ts
// Source: https://nextjs.org/docs/app/building-your-application/authentication
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { auth } from '@/lib/auth'

export async function middleware(req: NextRequest) {
  const session = await auth()
  const path = req.nextUrl.pathname

  const protectedRoutes = ['/settings', '/dashboard']
  const publicRoutes = ['/login', '/']

  const isProtected = protectedRoutes.some(route => path.startsWith(route))
  const isPublic = publicRoutes.includes(path)

  // Redirect unauthenticated users to login
  if (isProtected && !session?.user) {

```
return NextResponse.redirect(new URL('/login', req.url))

```
  }

  // Redirect authenticated users away from login
  if (isPublic && session?.user && path === '/login') {

```
return NextResponse.redirect(new URL('/dashboard', req.url))

```
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
}

```

### Anti-Patterns to Avoid

- **Querying database in middleware:** Middleware runs on every request including
  prefetches, causing performance issues. Use cookie-based checks only.
- **Storing sensitive data in session payload:** Never store PII, passwords, or
  tokens in JWT payload. Store only user ID and minimal metadata.
- **Not using Data Access Layer:** Calling `auth()` directly in components leads
  to duplicate queries. Use DAL with `cache()` for deduplication.
- **Manual CSRF tokens:** Auth.js includes CSRF protection by default. Don't
  build custom CSRF handling.
- **Polling GitHub API:** Use webhooks or aggressive caching with ETags. Polling
  burns rate limits (5,000/hour for authenticated users).

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
  | OAuth flow | Custom GitH... | Auth.js Git... | Handles sta... |  
  | Session man... | Custom JWT ... | Auth.js wit... | Handles ses... |  
  | Password ha... | Custom cryp... | bcrypt or a... | Proper salt... |  
  | File uploads | Custom mult... | Vercel Blob... | Handles pro... |  
  | Rate limiti... | Custom requ... | Conditional... | GitHub does... |  
  | Form deboun... | Manual setT... | useDebounce... | Handles cle... |  
| Auto-save r... | Timestamp-b... | React Query... | FIFO execut... |

**Key insight:** Authentication is a security-critical domain with decades of
attack patterns (CSRF, session fixation, timing attacks, token leakage). Auth.js
encodes these defenses by default. Custom auth implementations inevitably
rediscover these vulnerabilities the hard way.

## Common Pitfalls

### Pitfall 1: Missing AUTH_SECRET in Production

**What goes wrong:** Auth.js throws runtime error "AUTH_SECRET is not set" in
production
**Why it happens:** Environment variable not set in deployment platform (Vercel,
etc.)
**How to avoid:** Generate secret with `npx auth secret`, add to `.env.local`
AND deployment environment variables
**Warning signs:** Works locally but fails in preview/production deployments

### Pitfall 2: GitHub OAuth Scope Limitations

**What goes wrong:** Can't get read-only access to repos, requesting `repo`
scope grants full read/write
**Why it happens:** GitHub OAuth doesn't offer read-only repo scope (known
limitation)
**How to avoid:** Accept that `repo` scope grants write access, or use GitHub
Apps instead of OAuth Apps for fine-grained permissions
**Warning signs:** Users concerned about granting write access during OAuth flow

### Pitfall 3: Session Cookie Not Updating in Middleware

**What goes wrong:** Session refresh logic in middleware doesn't persist updated
cookies
**Why it happens:** Server Components can't set cookies during render,
middleware cookie updates aren't automatic
**How to avoid:** Auth.js handles session refresh automatically via `updateAge`
- don't try to manually refresh in middleware
**Warning signs:** Session expires despite user activity, manual cookie setting
in middleware

### Pitfall 4: GitHub API Rate Limit Exhaustion

**What goes wrong:** Hitting 5,000 requests/hour limit, users get stale profile
data
**Why it happens:** Fetching fresh GitHub data on every page load without
caching
**How to avoid:** (1) Use conditional requests with ETags (304 responses are
free), (2) Cache GitHub data in database, (3) Refresh only on login (per user
context), (4) Use webhooks for repo updates
**Warning signs:** `x-ratelimit-remaining: 0` in response headers, 403 rate
limit errors

### Pitfall 5: Auto-Save Race Conditions

**What goes wrong:** User types "Hello World" but "Hello" saves last,
overwriting "Hello World"
**Why it happens:** HTTP requests complete out-of-order, last response
overwrites latest input
**How to avoid:** Use queued mutations (React Query) or timestamps with conflict
resolution, debounce at least 1-3 seconds
**Warning signs:** Intermittent data loss, saved state doesn't match last user
input

### Pitfall 6: Vercel Blob 4.5MB Server Upload Limit

**What goes wrong:** Large avatar uploads fail with size limit errors
**Why it happens:** Vercel limits server-side uploads to 4.5MB (undocumented but
consistent)
**How to avoid:** Use `clientUploads: true` for uploads >4.5MB (uploads directly
from browser to Blob storage)
**Warning signs:** Uploads work locally but fail on Vercel, size-related errors
in production

### Pitfall 7: Not Handling OAuth Errors

**What goes wrong:** User denies OAuth permissions or OAuth fails, gets stuck on
blank page
**Why it happens:** No error handling for OAuth callback failures
**How to avoid:** Set `pages.error: '/login'` in Auth.js config (per user
context), display error message from URL params
**Warning signs:** Users report "blank page" after clicking "Login with GitHub"

### Pitfall 8: Prisma Adapter Schema Mismatch

**What goes wrong:** Auth.js fails with "column does not exist" errors
**Why it happens:** Prisma schema doesn't match Auth.js adapter requirements
(missing fields like `emailVerified`, wrong field types)
**How to avoid:** Copy exact schema from Auth.js Prisma adapter docs, run
`prisma migrate dev` after changes
**Warning signs:** Database errors mentioning `Account`, `Session`, or `User`
table columns

## Code Examples

Verified patterns from official sources:

### Prisma Schema for Auth.js

```prisma

// Source: https://authjs.dev/getting-started/adapters/prisma

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String?   @unique
  emailVerified DateTime?
  image         String?

  // Custom fields (per user context)
  bio           String?
  customAvatar  String?  // URL to uploaded avatar (overrides GitHub image)

  accounts      Account[]
  sessions      Session[]
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model VerificationToken {
  identifier String
  token      String
  expires    DateTime

  @@unique([identifier, token])
}

```markdown

### Auth.js Route Handler

```typescript

// app/api/auth/[...nextauth]/route.ts
// Source: https://authjs.dev/reference/nextjs

import { handlers } from "@/lib/auth"

export const { GET, POST } = handlers

```

### Server Component with DAL

```typescript

// app/settings/profile/page.tsx
// Source: https://nextjs.org/docs/app/building-your-application/authentication

import { verifySession, getUser } from '@/lib/dal'
import { ProfileForm } from './ProfileForm'

export default async function ProfilePage() {
  await verifySession()  // Redirects if not authenticated
  const user = await getUser()  // Cached, won't query DB twice

  return (

```
<div>
  <h1>Profile Settings</h1>
  <ProfileForm user={user} />
</div>

```
  )
}

```markdown

### useDebounce Hook

```typescript

// hooks/useDebounce.ts
// Source: https://darius-marlowe.medium.com/smarter-forms-in-react-building-a-useautosave-hook-with-debounce-and-react-query-d4d7f9bb052e

import { useEffect, useCallback, useRef } from 'react'

export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>()

  const debouncedCallback = useCallback((...args: Parameters<T>) => {

```
if (timeoutRef.current) {
  clearTimeout(timeoutRef.current)
}

timeoutRef.current = setTimeout(() => {
  callback(...args)
}, delay)

```
  }, [callback, delay])

  useEffect(() => {

```
return () => {
  if (timeoutRef.current) {
    clearTimeout(timeoutRef.current)
  }
}

```
  }, [])

  return debouncedCallback as T
}

```

### GitHub API Rate Limit Monitoring

```typescript

// lib/github.ts
// Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

export async function checkRateLimit(accessToken: string) {
  const response = await fetch('https://api.github.com/rate_limit', {

```
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Accept': 'application/vnd.github.v3+json'
}

```
  })

  const data = await response.json()

  return {

```
limit: data.resources.core.limit,        // 5000 for authenticated
remaining: data.resources.core.remaining,
reset: new Date(data.resources.core.reset * 1000),  // UTC timestamp

```
  }
}

```markdown

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
| NextAuth.js... | Auth.js v5 ... | 2024-2025 | New `auth()... |
| JWT-only se... | Database se... | 2024+ | Can track a... |
| Manual OAut... | Built-in CS... | Always in A... | No need to ... |
  | Polling Git... | Conditional... | 2023+ (docs... | 304 respons... |  
| Manual debo... | React Query... | 2024-2025 | FIFO execut... |
| Server-side... | Client-side... | 2025+ (Verc... | Bypasses se... |

**Deprecated/outdated:**

- **`NEXTAUTH_*` environment variables:** Now use `AUTH_*` prefix (Auth.js v5
  migration)
- **Credentials provider without JWT:** Database sessions can't work with
  credentials provider unless JWT is enabled (Auth.js limitation)
- **Middleware with database queries:** Next.js App Router middleware should only
  do cookie checks (performance)
- **`repo` scope for read-only access:** GitHub OAuth doesn't support read-only
  repo scope; use GitHub Apps for fine-grained permissions

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal GitHub data refresh cadence**
   - What we know: User context says "sync every login", conditional requests are

```
 free (304 responses)

```
   - What's unclear: Should we also refresh on interval (e.g., hourly) or only on

```
 explicit user actions?

```
   - Recommendation: Start with login-only refresh, add background refresh if

```
 users report stale data

```
2. **Avatar upload size validation**
   - What we know: Vercel Blob has 4.5MB server limit, client uploads bypass this
   - What's unclear: Should we enforce a client-side size limit? If so, what's

```
 reasonable?

```
   - Recommendation: Enforce 5MB client-side limit (covers profile photos,

```
 prevents abuse), use client uploads

```
3. **Session refresh UX during auto-save**
   - What we know: Sessions refresh silently every hour (`updateAge: 3600`),

```
 auto-save happens every 3 seconds

```
   - What's unclear: If session expires during typing, does auto-save fail

```
 gracefully or lose data?

```
   - Recommendation: Test session expiry during active editing, may need to

```
 handle 401 by saving to localStorage

```
4. **GitHub webhook integration scope**
   - What we know: User context mentions "bidirectional sync" with GitHub repos
   - What's unclear: Is webhook setup part of Phase 2 or deferred to later phase?
   - Recommendation: Confirm with user - context says "deferred decisions"

```
 includes "advanced webhook integration"

```
## Sources

### Primary (HIGH confidence)

- Auth.js Next.js Reference: <https://authjs.dev/reference/nextjs>
- Auth.js Prisma Adapter: <https://authjs.dev/getting-started/adapters/prisma>
- Next.js Authentication Docs:
  <https://nextjs.org/docs/app/building-your-application/authentication>
- GitHub OAuth Scopes:
  <https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps>
- GitHub API Rate Limits:
  <https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>
- GitHub API Best Practices:
  <https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api>

### Secondary (MEDIUM confidence)

- Top 5 Authentication Solutions for Next.js 2026:
  <https://workos.com/blog/top-authentication-solutions-nextjs-2026>
- Next.js 15 Tutorial File Upload with Server Actions:
  <https://strapi.io/blog/epic-next-js-15-tutorial-part-5-file-upload-using-server-actions>
- React Auto-Save with Debounce and React Query:
  <https://darius-marlowe.medium.com/smarter-forms-in-react-building-a-useautosave-hook-with-debounce-and-react-query-d4d7f9bb052e>
- React Query Autosave: Preventing Data Loss & Race Conditions:
  <https://www.pz.com.au/avoiding-race-conditions-and-data-loss-when-autosaving-in-react-query>

### Tertiary (LOW confidence)

- Auth.js vs BetterAuth Comparison:
  <https://www.wisp.blog/blog/authjs-vs-betterauth-for-nextjs-a-comprehensive-comparison>
  (WebSearch only, marked for validation)
- Common Next.js & NextAuth Authentication Pitfalls:
  <https://infinitejs.com/posts/nextjs-nextauth-auth-pitfalls/> (WebSearch only,
  marked for validation)

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Auth.js is official and widely documented for Next.js
  15, Prisma adapter is official
- Architecture: HIGH - Patterns verified from official Next.js docs and Auth.js
  reference
- Pitfalls: MEDIUM - Combination of official docs (rate limits, env vars) and
  community reports (Vercel upload limit, race conditions)

**Research date:** 2026-01-24
**Valid until:** 2026-02-24 (30 days - Auth.js v5 is stable beta, unlikely to
change significantly)
