# Phase 1: Foundation & Setup - Research

**Researched:** 2026-01-24
**Domain:** Next.js full-stack application foundation
**Confidence:** HIGH

## Summary

Foundation setup for a modern Next.js application in 2026 follows a
well-established pattern using Next.js 15/16 with TypeScript, Prisma ORM with
PostgreSQL, and the App Router architecture. The standard approach prioritizes
framework defaults, leverages built-in tooling (Turbopack, ESLint), and uses the
`create-next-app` CLI for initialization.

The research focused on production-ready patterns, particularly emphasizing
reusable module architecture for the MyWork framework's "brain extraction"
requirement (SYS-06). The modular monolith approach emerged as the industry
standard for 2025-2026, organizing code by business domains while maintaining
single-deployment simplicity.

Key findings show that Next.js 16 made Turbopack the default bundler, Prisma 7
introduced breaking changes around configuration files, and the community
consensus strongly favors using established libraries over building custom
solutions for authentication, validation, and form handling.

**Primary recommendation:** Use `create-next-app@latest --yes` for framework
defaults, organize with feature-based modular structure, implement Prisma
singleton pattern for database connections, and follow the verification protocol
for migrations.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
| Next.js | 15.x/16.x | Full-stack ... | Official re... |
  | TypeScript | 5.x | Static typing | Automatical... |  
| Prisma ORM | 7.x | Database ORM | Type-safe q... |
| PostgreSQL | 14+ | Database | Production-... |
  | React | 19.x | UI library | Next.js dep... |  

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
  | Zod | 3.x | Schema vali... | All form in... |  
| eslint-conf... | Latest | ESLint/Pret... | Automatic i... |
| @prisma/client | Matches Prisma | Type-safe D... | Generated f... |
| dotenv | Built-in | Environment... | Next.js loa... |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
| Prisma | Drizzle ORM | Lighter bundle, SQL-like syntax, less mature tooling |
  | PostgreSQL | MySQL/SQLite | SQLite for prototy... |  
  | TypeScript | JavaScript | Faster initial set... |  

**Installation:**

```bash

# Recommended: Use framework defaults

npx create-next-app@latest my-app --yes
cd my-app

# Install Prisma

npm install -D prisma tsx
npm install @prisma/client

# Install Zod for validation

npm install zod

# Initialize Prisma

npx prisma init

```markdown

## Architecture Patterns

### Recommended Project Structure

**Modular Monolith (Feature-Based)**

```markdown

project-root/
├── src/
│   ├── app/                    # Next.js App Router (routes only)
│   │   ├── (auth)/            # Route group for auth pages
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/       # Route group for main app
│   │   │   ├── tasks/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── api/               # API routes
│   │   │   └── tasks/
│   │   │       └── route.ts
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   │
│   ├── modules/               # Business domain modules (reusable for brain)
│   │   ├── auth/
│   │   │   ├── components/    # Auth-specific UI
│   │   │   ├── lib/           # Auth business logic
│   │   │   ├── types/         # Auth TypeScript types
│   │   │   └── index.ts       # Public API
│   │   └── tasks/
│   │       ├── components/
│   │       ├── lib/
│   │       ├── types/
│   │       └── index.ts
│   │
│   ├── shared/                # Cross-cutting concerns
│   │   ├── components/        # Reusable UI primitives
│   │   ├── lib/
│   │   │   ├── db/
│   │   │   │   └── prisma.ts  # Singleton client
│   │   │   └── utils/
│   │   └── types/
│   │
│   └── prisma/
│       ├── schema.prisma
│       ├── migrations/
│       └── seed.ts
│
├── public/                    # Static assets
├── .env                       # Environment variables (gitignored)
├── .env.local                 # Local overrides (gitignored)
├── next.config.ts             # Next.js configuration
├── tsconfig.json              # TypeScript configuration
├── eslint.config.mjs          # ESLint configuration
└── package.json

```markdown

### Pattern 1: Prisma Singleton Client

**What:** Single PrismaClient instance reused across hot reloads
**When to use:** Every Next.js + Prisma project (development and production)
**Example:**

```typescript

// Source: https://www.prisma.io/docs/guides/nextjs
// src/shared/lib/db/prisma.ts

import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
})

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

```yaml

**Why it matters:** Prevents connection pool exhaustion during Next.js hot
reloads. Without this, each file change creates a new PrismaClient with its own
connection pool, quickly exhausting PostgreSQL's connection limit.

### Pattern 2: Environment Variable Validation

**What:** Validate all environment variables at startup using Zod schemas
**When to use:** Every project with environment-dependent configuration
**Example:**

```typescript

// Source: Community best practice 2025
// src/shared/lib/env.ts

import { z } from 'zod'

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NODE_ENV: z.enum(['development', 'test', 'production']),
  // Only NEXT_PUBLIC_ vars are exposed to client
  NEXT_PUBLIC_APP_URL: z.string().url(),
})

export const env = envSchema.parse(process.env)

```yaml

**Why it matters:** Catches configuration errors at startup, not at runtime.
Provides type safety for environment variables and documents required
configuration.

### Pattern 3: Feature Module Public API

**What:** Each module exports a clean public API through index.ts
**When to use:** All business domain modules for brain extraction (SYS-06)
**Example:**

```typescript

// Source: Feature-based architecture pattern 2025
// src/modules/tasks/index.ts

// Export only what other modules need
export { TaskList, TaskCard } from './components'
export { createTask, updateTask, deleteTask } from './lib/actions'
export type { Task, TaskStatus } from './types'

// Internal implementation stays private

```yaml

**Why it matters:** Enables clean extraction to other projects. When building
the MyWork framework brain, modules with clear public APIs can be copied to new
projects with minimal coupling.

### Pattern 4: Server Actions for Mutations

**What:** Use Server Actions for all data mutations in Next.js App Router
**When to use:** Creating, updating, or deleting data
**Example:**

```typescript

// Source: https://nextjs.org/docs/app/guides/forms
// src/modules/tasks/lib/actions.ts

'use server'

import { prisma } from '@/shared/lib/db/prisma'
import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const createTaskSchema = z.object({
  title: z.string().min(1).max(255),
  description: z.string().optional(),
})

export async function createTask(formData: FormData) {
  // Always validate on server
  const validated = createTaskSchema.parse({

```yaml

title: formData.get('title'),
description: formData.get('description'),

```javascript
  })

  const task = await prisma.task.create({

```yaml

data: validated,

```yaml
  })

  // Revalidate cache
  revalidatePath('/tasks')

  return { success: true, task }
}

```markdown

### Pattern 5: TypeScript Path Aliases

**What:** Use `@/*` import aliases configured by create-next-app
**When to use:** All imports (framework default since 2025)
**Example:**

```typescript

// Source: https://nextjs.org/docs/app/building-your-application/configuring/absolute-imports-and-module-aliases

// ❌ Avoid relative paths
import { prisma } from '../../../shared/lib/db/prisma'
import { Button } from '../../shared/components/Button'

// ✅ Use path aliases
import { prisma } from '@/shared/lib/db/prisma'
import { Button } from '@/shared/components/Button'

```

**Configuration (automatic in tsconfig.json):**

```json
{
  "compilerOptions": {

```yaml

"baseUrl": ".",
"paths": {
  "@/*": ["./src/*"]
}

```markdown

  }
}

```markdown

### Anti-Patterns to Avoid

- **Creating multiple PrismaClient instances:** Leads to connection pool

  exhaustion. Always use singleton pattern.

- **Mixing Server and Client Components incorrectly:** Adding 'use client' at

  root forces entire tree to client. Push 'use client' to leaf components.

- **Using useEffect for data fetching:** Causes flash of empty content, slower

  load times. Use Server Components or Server Actions instead.

- **Storing secrets in client-exposed variables:** Never prefix secrets with

  NEXT_PUBLIC_. Only server-side code can access non-prefixed env vars.

- **Hand-rolling authentication:** Custom auth costs $250k-500k initial

  investment. Use Auth.js, Clerk, or WorkOS instead.

- **Skipping migration files in git:** Migrations are your database's source of

  truth. Always commit `prisma/migrations/` directory.

- **Technical layering (models/, views/, controllers/):** Organize by

  feature/domain for better reusability and brain extraction.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
  | Authentication | Custom logi... | Auth.js, Cl... | Security vu... |  
  | Form Valida... | Custom rege... | Zod, Yup sc... | Handles nes... |  
  | Environment... | Manual proc... | Zod schema ... | Fails fast ... |  
  | Database Mi... | Manual SQL ... | Prisma Migrate | Tracks migr... |  
  | API Input V... | if/else cha... | Zod schemas... | Type safety... |  
  | CSRF Protec... | Custom toke... | Auth.js (bu... | Handles edg... |  
  | Session Man... | Custom cook... | Auth.js, ir... | Secure defa... |  
  | Image Optim... | Custom resi... | Next.js Ima... | Automatic l... |  

**Key insight:** In the modern JavaScript ecosystem, most infrastructure
concerns have battle-tested solutions. Custom implementations introduce security
risks, maintenance burden, and delay feature development. The MyWork framework
emphasizes using established libraries to accelerate new projects.

## Common Pitfalls

### Pitfall 1: Connection Pool Exhaustion in Development

**What goes wrong:** Database errors "Too many clients already" during
development with hot reload
**Why it happens:** Each hot reload creates a new PrismaClient instance with its
own connection pool (default: num_cpus * 2 + 1). Old connections don't close,
exhausting PostgreSQL's max_connections.
**How to avoid:**

- Implement Prisma singleton pattern (see Pattern 1)
- Store client on globalThis in development
- Configure connection pool limits in DATABASE_URL:

  `postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=20`

**Warning signs:**

- Error messages containing "too many clients"
- Database refusing new connections
- Need to restart PostgreSQL to recover

### Pitfall 2: Environment Variable Visibility

**What goes wrong:** Secrets exposed to client-side JavaScript bundle
**Why it happens:** Variables prefixed with `NEXT_PUBLIC_` are embedded in
client bundle. Developers prefix secrets to make them "work" in components,
unknowingly exposing them.
**How to avoid:**

- Never prefix API keys, database URLs, or secrets with `NEXT_PUBLIC_`
- Use Server Components or Server Actions to access server-only env vars
- Validate env vars with Zod schema at startup (catches missing vars early)
- Check build output: `grep -r "your-secret" .next/` should return nothing

**Warning signs:**

- API keys visible in browser DevTools Network tab
- Secrets in .next/static/ files
- Auth tokens in client-side JavaScript

### Pitfall 3: Migration Workflow Confusion

**What goes wrong:** Database schema out of sync with codebase, merge conflicts
in migration files
**Why it happens:** Developers use `prisma db push` in development instead of
`prisma migrate dev`, skip committing migrations, or don't understand the
development vs. production workflow.
**How to avoid:**

- **Development:** Always use `npx prisma migrate dev --name descriptive_name`
- **Production:** Always use `npx prisma migrate deploy` (in CI/CD pipeline)
- Never use `db push` except for rapid prototyping (it skips migration history)
- Commit entire `prisma/migrations/` directory to git
- Run `prisma migrate dev` before switching branches with schema changes

**Warning signs:**

- "Schema drift detected" errors
- Missing tables in production
- Git conflicts in schema.prisma but no migration files
- Team members with different database states

### Pitfall 4: Server/Client Component Boundary Mistakes

**What goes wrong:** Server Components become Client Components unintentionally,
losing benefits of server-side rendering
**Why it happens:** Adding 'use client' at the top of a parent component forces
entire subtree to client-side, even if children could be server components.
**How to avoid:**

- Start with Server Components by default (no directive needed)
- Only add 'use client' to leaf components that need interactivity
- Composition pattern: Pass Server Components as children to Client Components
- Use Server Actions for mutations instead of client-side fetch()

**Warning signs:**

- API calls happening from browser (check Network tab)
- Environment variables not accessible (server-only vars don't work in client)
- Waterfall requests (client fetching data that could be server-rendered)

### Pitfall 5: Ignoring TypeScript Errors in Development

**What goes wrong:** Type errors accumulate, production build fails unexpectedly
**Why it happens:** Next.js dev server shows warnings but continues running.
Developers ignore red squiggles, accumulate type errors, and discover issues
only when deploying.
**How to avoid:**

- Enable strict mode in tsconfig.json (create-next-app default)
- Run `npm run build` locally before pushing
- Set up pre-commit hook: `tsc --noEmit`
- Configure CI to fail on TypeScript errors
- Use ESLint rule: `@typescript-eslint/no-explicit-any` to prevent escape hatches

**Warning signs:**

- Many `any` types in codebase
- Build succeeds locally but fails in CI
- Runtime errors that TypeScript should have caught

### Pitfall 6: Prisma Schema Changes Without Migration

**What goes wrong:** Local database works but production breaks, team members
have different schemas
**Why it happens:** Running `prisma db push` or manually editing the database
bypasses migration history
**How to avoid:**

- Always change schema in `schema.prisma` first
- Always run `prisma migrate dev` to create migration file
- Commit migration files immediately
- Never edit migration files after they're committed
- Use `prisma migrate reset` to start fresh if drift occurs

**Warning signs:**

- "Migration has already been applied" errors
- Prisma generates migration but says "no changes detected"
- Production schema doesn't match schema.prisma

## Code Examples

### Initial Setup Commands

```bash

# Source: https://nextjs.org/docs/app/getting-started/installation

# Create Next.js app with recommended defaults

npx create-next-app@latest task-tracker --yes
cd task-tracker

# Install Prisma dependencies

npm install -D prisma tsx
npm install @prisma/client

# Install validation library

npm install zod

# Initialize Prisma

npx prisma init

# This creates:

# - prisma/schema.prisma

# - .env (with DATABASE_URL placeholder)

```markdown

### Configure Environment Variables

```bash

# Source: https://nextjs.org/docs/pages/guides/environment-variables

# .env.local (not committed to git)

DATABASE_URL="postgresql://user:password@localhost:5432/tasktracker?schema=public"
NODE_ENV="development"

# Server-only variables (no prefix)

AUTH_SECRET="fake123"

# Client-exposed variables (NEXT_PUBLIC_ prefix)

NEXT_PUBLIC_APP_URL="http://localhost:3000"

```markdown

### Initial Prisma Schema

```prisma

// Source: https://www.prisma.io/docs/guides/nextjs
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Example model for validation
model Task {
  id          String   @id @default(cuid())
  title       String   @db.VarChar(255)
  description String?  @db.Text
  status      String   @default("todo") @db.VarChar(50)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@index([status])
}

```markdown

### Run First Migration

```bash

# Source: https://www.prisma.io/docs/orm/prisma-migrate/getting-started

# Create and apply migration

npx prisma migrate dev --name init

# This does three things:

# 1. Creates SQL migration file in prisma/migrations/

# 2. Applies migration to database

# 3. Generates Prisma Client in node_modules/@prisma/client

# Verify schema is applied

npx prisma studio  # Opens browser UI to inspect database

```markdown

### Start Development Server

```bash

# Source: https://nextjs.org/docs/app/api-reference/turbopack

# Next.js 16+ (Turbopack is default)

npm run dev

# Server starts at http://localhost:3000

# Turbopack provides faster hot reload than webpack

# File changes reflect immediately in browser

```markdown

### Verify Setup Checklist

```typescript

// Source: Production checklist 2025
// Test file: src/app/api/health/route.ts

import { prisma } from '@/shared/lib/db/prisma'
import { NextResponse } from 'next/server'

export async function GET() {
  try {

```javascript

// Verify database connection
await prisma.$queryRaw`SELECT 1`

// Verify environment variables loaded
const hasDbUrl = !!process.env.DATABASE_URL

return NextResponse.json({
  status: 'ok',
  database: 'connected',
  environment: process.env.NODE_ENV,
  hasDbUrl,
})

```text
  } catch (error) {

```

return NextResponse.json({
  status: 'error',
  message: error instanceof Error ? error.message : 'Unknown error',
}, { status: 500 })

```yaml
  }
}

```yaml

Test by visiting: `http://localhost:3000/api/health`

Expected response:

```json
{
  "status": "ok",
  "database": "connected",
  "environment": "development",
  "hasDbUrl": true
}

```markdown

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
  | Pages Router | App Router | Next.js 13 ... | Server Comp... |  
  | Webpack only | Turbopack d... | Next.js 16 ... | 10x faster ... |  
  | Prisma conf... | prisma.conf... | Prisma 7 (N... | datasource.... |  
  | Custom .d.t... | Zod schema ... | Community s... | Runtime val... |  
  | getServerSi... | Server Comp... | Next.js 13 ... | Simpler API... |  
  | API routes ... | Server Actions | Next.js 14 ... | Progressive... |  
| Manual path... | Default @/*... | create-next... | Zero config... |

**Deprecated/outdated:**

- **Pages Router for new projects:** Still supported but App Router is

  recommended default. Use Pages Router only for incremental migration or
  specific edge cases.

- **prisma db push for development:** Use `prisma migrate dev` instead. db push

  skips migration history, causing team sync issues.

- **next.config.js (CommonJS):** Prefer `next.config.ts` (TypeScript) or

  `next.config.mjs` (ESM) for type safety.

- **experimental.turbopack config:** Moved to top-level `turbopack` key in

  Next.js 16.

- **Custom authentication from scratch:** Industry moved to managed auth

  providers (Auth.js, Clerk, WorkOS) due to security complexity.

## Open Questions

1. **PostgreSQL Connection Pooling Strategy**
   - What we know: Prisma supports connection pooling via Prisma Accelerate or

```text
 direct connection string params

```yaml

   - What's unclear: Optimal pool size for development vs. production, whether to

```text
 use Accelerate for this project

```yaml

   - Recommendation: Start with default connection pool (num_cpus * 2 + 1), add

```text
 explicit `connection_limit=10` in development DATABASE_URL, defer Accelerate
 until production deployment

```

2. **Module Boundary Enforcement**
   - What we know: TypeScript path aliases and index.ts exports create public

```text
 APIs

```python

   - What's unclear: How to prevent developers from importing internal files

```text
 directly (e.g., `@/modules/tasks/lib/internal` instead of `@/modules/tasks`)

```yaml

   - Recommendation: Document convention in ARCHITECTURE.md, consider ESLint

```text
 plugin `eslint-plugin-boundaries` for enforcement, validate during code
 review

```yaml

3. **Prisma 7 Breaking Changes Impact**
   - What we know: Prisma 7 moved datasource.url to prisma.config.ts, introduced

```text
 Rust-free client

```

   - What's unclear: Whether to use Prisma 6 (stable, widely documented) or

```text
 Prisma 7 (latest, fewer examples)

```yaml

   - Recommendation: Use Prisma 6.x for this project (proven stable), monitor

```text
 Prisma 7 adoption, plan migration when ecosystem documentation catches up

```yaml

4. **Environment Variable Validation Timing**
   - What we know: Zod validation should happen at startup
   - What's unclear: Best location to trigger validation (middleware, layout,

```text
 separate script)

```yaml

   - Recommendation: Create `src/shared/lib/env.ts` that validates on import,

```python
 import it in root layout.tsx to ensure validation before any route handler
 executes

```

## Sources

### Primary (HIGH confidence)

- Next.js Official Documentation -

  [Installation](https://nextjs.org/docs/app/getting-started/installation) -
  Verified CLI setup, configuration options

- Next.js Official Documentation - [Project

  Structure](https://nextjs.org/docs/app/getting-started/project-structure) -
  Verified folder organization, special files

- Next.js Official Documentation - [TypeScript

  Configuration](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript)

  - Verified tsconfig setup
- Next.js Official Documentation - [Environment

  Variables](https://nextjs.org/docs/pages/guides/environment-variables) -
  Verified NEXT_PUBLIC_ behavior

- Next.js Official Documentation - [Forms and

  Mutations](https://nextjs.org/docs/pages/building-your-application/data-fetching/forms-and-mutations)

  - Verified Server Actions pattern
- Next.js Official Documentation - [Path

  Aliases](https://nextjs.org/docs/app/building-your-application/configuring/absolute-imports-and-module-aliases)

  - Verified @/* alias configuration
- Next.js Official Documentation -

  [Turbopack](https://nextjs.org/docs/app/api-reference/turbopack) - Verified
  default bundler status in v16

- Prisma Official Documentation - [Next.js

  Guide](https://www.prisma.io/docs/guides/nextjs) - Verified Prisma setup,
  singleton pattern

- Prisma Official Documentation - [Migrations Getting

  Started](https://www.prisma.io/docs/orm/prisma-migrate/getting-started) -
  Verified migrate dev workflow

- Prisma Official Documentation - [Development and

  Production](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production)

  - Verified deployment workflow

### Secondary (MEDIUM confidence)

- [How To Set Up Next.js 15 For Production In

  2025](https://janhesters.com/blog/how-to-set-up-nextjs-15-for-production-in-2025)

  - Verified ESLint/Prettier setup
- [Prisma ORM Production Guide: Next.js Complete Setup

  2025](https://www.digitalapplied.com/blog/prisma-orm-production-guide-nextjs)
  -
  Verified connection pooling recommendations

- [Scaling React & Next.js Apps: A Feature-Based

  Architecture](https://medium.com/@nishibuch25/scaling-react-next-js-apps-a-feature-based-architecture-that-actually-works-c0c89c25936d)

  - Verified modular structure pattern
- [The Ultimate Guide to Software Architecture in

  Next.js](https://dev.to/shayan_saed/the-ultimate-guide-to-software-architecture-in-nextjs-from-monolith-to-microservices-i2c)

  - Verified modular monolith approach
- [Optimizing Connection Pools with PrismaClient Singleton

  Pattern](https://dev.to/_877737de2d34ff8c6265/optimizing-connection-pools-with-prismaclient-singleton-pattern-in-nextjs-3emf)

  - Verified connection pool exhaustion issue
- [User Authentication for Next.js: Top Tools

  2025](https://clerk.com/articles/user-authentication-for-nextjs-top-tools-and-recommendations-for-2025)

  - Verified custom auth cost analysis
- [Complete Next.js Security Guide

  2025](https://www.turbostarter.dev/blog/complete-nextjs-security-guide-2025-authentication-api-protection-and-best-practices)

  - Verified security best practices
- [5 Mistakes Beginners Make with

  Next.js](https://javascript.plainenglish.io/5-mistakes-beginners-make-with-next-js-and-how-to-avoid-them-2025-shit-68959119a612)

  - Verified common pitfalls
- [All 29 Next.js Mistakes Beginners

  Make](https://dev.to/azeem_shafeeq/all-29-nextjs-mistakes-beginners-make-56nj)

  - Cross-verified pitfall patterns
- [Prisma Pitfalls: Top Errors & Pro

  Fixes](https://medium.com/@nui_x/prisma-pitfalls-top-errors-pro-fixes-you-cant-ignore-852a0fe87565)

  - Verified Prisma 7 breaking changes

### Tertiary (LOW confidence)

- Various Stack Overflow discussions on Prisma connection pooling (not linked,

  used for pattern validation only)

- Community blog posts on TypeScript configuration (cross-verified with official

  docs)

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All recommendations verified with official documentation

  and multiple authoritative sources

- Architecture patterns: HIGH - Official Next.js docs confirm project structure,

  community consensus on modular monolith for 2025

- Pitfalls: HIGH - Verified through official documentation, multiple recent

  articles (2025), and official error references

- Code examples: HIGH - All examples sourced from official documentation or

  verified production setups

**Research date:** 2026-01-24
**Valid until:** 2026-02-23 (30 days, stable technologies with predictable
release cycles)

**Notes:**

- Next.js 16 stable as of October 2025, widespread adoption in January 2026
- Prisma 7 released November 2025, consider using Prisma 6.x for stability
- All environment variable patterns verified against Next.js 15/16 behavior
- Modular architecture patterns specifically selected for MyWork framework

  reusability (SYS-06)
