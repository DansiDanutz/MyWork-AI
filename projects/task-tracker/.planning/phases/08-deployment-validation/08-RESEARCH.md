# Phase 8: Deployment & Validation - Research

**Researched:** 2026-01-26
**Domain:** Next.js 15 production deployment, PostgreSQL hosting, monitoring, and user feedback collection
**Confidence:** HIGH

## Summary

Deploying a Next.js 15 application with PostgreSQL to production in 2026 involves choosing between specialized platforms (Vercel for frontend, Railway/Neon for backend+database) or all-in-one solutions. The standard approach is Vercel for Next.js frontend paired with Neon or Supabase for serverless PostgreSQL, with built-in monitoring via Vercel Speed Insights for Core Web Vitals and custom analytics for usage pattern tracking. Feedback collection is achieved through lightweight React components that integrate directly into the application.

Based on the context decisions (open access, direct GitHub login, framework validation focus), the recommended stack is:

- **Hosting**: Vercel (Next.js optimized, zero-config deployment)
- **Database**: Neon (serverless PostgreSQL with branching, scales to zero)
- **Monitoring**: Vercel Speed Insights + PostHog (pattern tracking)
- **Feedback**: Upstash Feedback Widget (self-hosted, Redis-backed)
- **CI/CD**: GitHub Actions for automated deployment pipeline

**Primary recommendation:** Deploy on Vercel with Neon PostgreSQL, use Vercel's built-in analytics for Core Web Vitals, add PostHog for framework pattern tracking, and integrate Upstash Feedback Widget for direct user input.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vercel | Platform | Next.js hosting | Created by Next.js team, zero-config, edge optimization, best integration |
| Neon | Platform | Serverless PostgreSQL | Auto-scaling, scales to zero, instant branching, modern developer experience |
| Vercel Speed Insights | Built-in | Core Web Vitals monitoring | Zero-config on Vercel, real user metrics, Next.js specific metrics |
| GitHub Actions | Platform | CI/CD automation | Native GitHub integration, free for public repos, extensive ecosystem |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PostHog | Latest | Product analytics | Framework pattern tracking, user behavior analysis |
| Upstash Feedback | Latest | Feedback widget | Self-hosted feedback, Redis-backed, Next.js optimized |
| @upstash/ratelimit | Latest | Rate limiting | Prevent abuse during validation period |
| Prisma Deploy | 7.x | Database migrations | Production migration management |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vercel | Railway | Railway handles full-stack better but lacks Next.js edge optimization |
| Neon | Supabase | Supabase adds auth/storage/realtime but more complex for simple PostgreSQL needs |
| Vercel Insights | Plausible | Plausible is privacy-focused but requires separate setup and costs |
| PostHog | Google Analytics | GA has larger ecosystem but heavier and less dev-friendly |
| Upstash Feedback | Happy React | Happy React is commercial with surveys but overkill for simple feedback |

**Installation:**

```bash

# Production dependencies (already in project)

npm install @upstash/ratelimit

# Feedback widget

npm install @upstash/feedback

# Analytics (if using PostHog)

npm install posthog-js

```

## Architecture Patterns

### Recommended Deployment Architecture

```
GitHub Repository
    ↓
GitHub Actions (CI/CD)
    ↓
Vercel (Frontend + API Routes)
    ↓
Neon (PostgreSQL Database)
    ↓
Upstash Redis (Rate Limiting + Feedback)

```

### Pattern 1: Zero-Downtime Deployment with Health Checks

**What:** Ensure new deployment is healthy before routing traffic
**When to use:** All production deployments
**Example:**

```typescript
// app/api/health/route.ts
// Source: https://blog.logrocket.com/how-to-implement-a-health-check-in-node-js/
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // Check database connectivity
    await prisma.$queryRaw`SELECT 1`;

    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    });
  } catch (error) {
    return NextResponse.json(
      { status: 'unhealthy', error: 'Database connection failed' },
      { status: 503 }
    );
  }
}

```

### Pattern 2: Environment Variable Management

**What:** Separate build-time and runtime configuration
**When to use:** All Next.js deployments
**Example:**

```bash

# .env.local (development)

DATABASE_URL="postgresql://user:pass@localhost:5432/db"
NEXTAUTH_SECRET="dev-secret"
NEXTAUTH_URL="http://localhost:3000"

# Vercel Environment Variables (production)

# DATABASE_URL → Production Neon connection string

# NEXTAUTH_SECRET → Generated secure secret

# NEXTAUTH_URL → https://your-app.vercel.app

```

**Important:** `NEXT_PUBLIC_*` variables are baked into build, all others are server-only.

### Pattern 3: Database Migration in Production

**What:** Safe migration deployment using Prisma
**When to use:** Database schema changes
**Example:**

```yaml

# .github/workflows/deploy.yml

# Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-database-changes-with-prisma-migrate

name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Setup Node.js

        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies

        run: npm ci

      - name: Run migrations

        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: npx prisma migrate deploy

      - name: Deploy to Vercel

        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}

```

### Pattern 4: Core Web Vitals Monitoring

**What:** Track real user performance metrics
**When to use:** All production deployments
**Example:**

```typescript
// app/layout.tsx
// Source: https://nextjs.org/docs/pages/api-reference/functions/use-report-web-vitals
import { sendToAnalytics } from '@/lib/analytics';

export function reportWebVitals(metric: any) {
  // Send to analytics endpoint
  sendToAnalytics(metric);

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(metric);
  }
}

```

### Pattern 5: User Feedback Collection

**What:** In-app feedback widget for validation
**When to use:** Validation phase, beta testing
**Example:**

```typescript
// components/FeedbackWidget.tsx
// Source: https://upstash.com/blog/feedback-widget
import { Feedback } from '@upstash/feedback';

export function FeedbackWidget() {
  return (
    <Feedback
      email="user@example.com" // From session
      metadata={{
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
      }}
    />
  );
}

```

### Pattern 6: Rate Limiting for Abuse Prevention

**What:** Prevent API abuse during validation period
**When to use:** Public endpoints, validation phase
**Example:**

```typescript
// lib/rate-limit.ts
// Source: https://upstash.com/blog/nextjs-ratelimiting
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
});

// Usage in API route
export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for') ?? 'anonymous';
  const { success } = await ratelimit.limit(ip);

  if (!success) {
    return new Response('Too many requests', { status: 429 });
  }

  // Process request
}

```

### Pattern 7: Framework Pattern Tracking

**What:** Track which MyWork framework patterns users actually use
**When to use:** Validation phase
**Example:**

```typescript
// lib/pattern-tracker.ts
import { posthog } from 'posthog-js';

export function trackPatternUsage(pattern: string, metadata?: Record<string, any>) {
  posthog.capture('pattern_used', {
    pattern,
    ...metadata,
    timestamp: new Date().toISOString(),
  });
}

// Usage
trackPatternUsage('task_create', { hasAttachments: true });
trackPatternUsage('search_filter', { filterType: 'status' });
trackPatternUsage('file_upload', { uploadMethod: 'tus' });

```

### Anti-Patterns to Avoid

- **Building at runtime**: Next.js requires `next build` before `next start`, never run dev in production
- **Hardcoded secrets**: Never commit `.env` files or secrets to git
- **Direct database access**: Always use Prisma client, never raw connection strings in client code
- **Missing error boundaries**: Production needs error boundaries to prevent white screens
- **No health checks**: Without health checks, bad deployments can take down the site
- **Trusting client data**: Always validate and authorize on server side (CVE-2025-29927)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Core Web Vitals tracking | Custom performance monitoring | Vercel Speed Insights | Built-in, zero-config, Next.js specific metrics (hydration, route changes) |
| Database migrations in prod | Manual SQL scripts | `prisma migrate deploy` | Tracks migration history, prevents conflicts, rollback support |
| Rate limiting | In-memory counters | @upstash/ratelimit | Distributed, works with serverless, multiple algorithms |
| Feedback forms | Custom form + email | Upstash Feedback Widget | Redis-backed, Slack integration, screenshot support |
| User analytics | Custom event tracking | PostHog or Vercel Analytics | Session replay, funnel analysis, feature flags |
| File upload resumability | Custom chunking | TUS protocol (@tus/server) | Resumable uploads, handles network failures, 20GB+ files |
| Security headers | Manual configuration | Next.js security headers | CSP, HSTS, X-Content-Type-Options built-in |
| Environment validation | Manual checks | Zod schema validation | Type-safe, catches config errors at startup |

**Key insight:** Deployment and monitoring infrastructure is complex with many edge cases (distributed systems, serverless constraints, cross-region latency). Use battle-tested tools that handle these automatically.

## Common Pitfalls

### Pitfall 1: Build-Time Environment Variables

**What goes wrong:** NEXT_PUBLIC_ variables are baked into the build, changing them in Vercel doesn't update deployed app
**Why it happens:** Next.js replaces NEXT_PUBLIC_ variables at build time with their values
**How to avoid:**

- Only use NEXT_PUBLIC_ for truly public values (API endpoints, feature flags)
- Use server-side environment variables for secrets and dynamic config
- Rebuild after changing any NEXT_PUBLIC_ variable

**Warning signs:** Changed environment variable but app still shows old value

### Pitfall 2: Missing Prisma Generation in Production

**What goes wrong:** `prisma` package is in devDependencies, production build fails with "Cannot find module '@prisma/client'"
**Why it happens:** Production installs only dependencies, not devDependencies
**How to avoid:**

- Add `"postinstall": "prisma generate"` to package.json scripts
- Move `prisma` to `dependencies` (not devDependencies)
- Or add `npm install prisma --save` (not --save-dev)

**Warning signs:** Local works fine, Vercel build fails on Prisma imports

### Pitfall 3: Database Connection Pooling Exhaustion

**What goes wrong:** "Too many connections" errors in serverless environment
**Why it happens:** Each serverless function creates new Prisma client, exhausting connection pool
**How to avoid:**

- Use connection pooling with Neon (built-in) or PgBouncer
- Configure Prisma connection limit: `connection_limit=10`
- Use Prisma's recommended singleton pattern for client instantiation

**Warning signs:** Works with low traffic, fails under load

### Pitfall 4: Missing Security Headers

**What goes wrong:** App vulnerable to XSS, clickjacking, content sniffing attacks
**Why it happens:** Next.js doesn't set security headers by default
**How to avoid:**

```typescript
// next.config.js
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
];

module.exports = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
};

```

**Warning signs:** Security audit tools flag missing headers

### Pitfall 5: Middleware Authentication Bypass (CVE-2025-29927)

**What goes wrong:** Critical vulnerability allows complete bypass of middleware security checks
**Why it happens:** Manipulation of `x-middleware-subrequest` header bypasses authentication
**How to avoid:**

- Upgrade to Next.js 15.2.3+, 14.2.25+, 13.5.9+, or 12.3.5+ immediately
- Re-verify authorization in Server Actions, don't trust middleware alone
- Validate user permissions before every sensitive operation

**Warning signs:** CVSS 9.1 critical vulnerability, must patch immediately

### Pitfall 6: File Upload Without Size Limits

**What goes wrong:** Users upload huge files, exhaust disk space or bandwidth quota
**Why it happens:** TUS protocol supports resumable uploads but doesn't enforce size limits by default
**How to avoid:**

- Configure max upload size in TUS server (e.g., 20GB limit)
- Add rate limiting to upload endpoints
- Monitor storage usage and set alerts

**Warning signs:** Sudden spike in storage costs or bandwidth

### Pitfall 7: No Rollback Plan

**What goes wrong:** Bad deployment breaks production, no way to quickly recover
**Why it happens:** Assumed deployment would always succeed
**How to avoid:**

- Keep previous deployment accessible (Vercel does this automatically)
- Test migrations on staging database first
- Use instant rollback feature on platform (Vercel: redeploy previous version)
- Implement health checks that auto-fail bad deployments

**Warning signs:** Deployment succeeds but app is broken, no quick recovery path

## Code Examples

Verified patterns from official sources:

### Production-Ready Health Check Endpoint

```typescript
// app/api/health/route.ts
// Source: https://blog.logrocket.com/how-to-implement-a-health-check-in-node-js/
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  const checks = {
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    database: 'unknown' as 'healthy' | 'unhealthy' | 'unknown',
  };

  try {
    // Check database connectivity
    await prisma.$queryRaw`SELECT 1`;
    checks.database = 'healthy';

    return NextResponse.json({
      status: 'healthy',
      checks,
    });
  } catch (error) {
    checks.database = 'unhealthy';

    return NextResponse.json(
      {
        status: 'unhealthy',
        checks,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    );
  }
}

```

### Safe Database Migration Deployment

```bash

# Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-database-changes-with-prisma-migrate

# In CI/CD pipeline (GitHub Actions)

npx prisma migrate deploy

# This command:

# - Compares applied migrations against migration history

# - Applies pending migrations in order

# - Warns if any migrations have been modified

# - Does NOT reset database or detect drift

```

### Environment Variable Validation at Startup

```typescript
// lib/env.ts
// Source: https://nextjs.org/docs/pages/guides/environment-variables
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXTAUTH_URL: z.string().url(),
  GITHUB_ID: z.string(),
  GITHUB_SECRET: z.string(),
  UPSTASH_REDIS_REST_URL: z.string().url().optional(),
  UPSTASH_REDIS_REST_TOKEN: z.string().optional(),
});

export const env = envSchema.parse(process.env);

```

### Feedback Widget Integration

```typescript
// components/FeedbackButton.tsx
// Source: https://upstash.com/blog/feedback-widget
'use client';

import { Feedback } from '@upstash/feedback';
import { useSession } from 'next-auth/react';

export function FeedbackButton() {
  const { data: session } = useSession();

  return (
    <Feedback
      email={session?.user?.email || 'anonymous'}
      metadata={{
        userId: session?.user?.id,
        page: window.location.pathname,
        userAgent: navigator.userAgent,
      }}
      user={session?.user?.name || 'Anonymous User'}
    />
  );
}

```

### Rate Limiting Middleware

```typescript
// middleware.ts
// Source: https://upstash.com/blog/edge-rate-limiting
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10 s'),
});

export async function middleware(request: NextRequest) {
  // Apply rate limiting to API routes only
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';
    const { success, pending, limit, reset, remaining } = await ratelimit.limit(ip);

    if (!success) {
      return NextResponse.json(
        { error: 'Too many requests' },
        {
          status: 429,
          headers: {
            'X-RateLimit-Limit': limit.toString(),
            'X-RateLimit-Remaining': remaining.toString(),
            'X-RateLimit-Reset': reset.toString(),
          },
        }
      );
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};

```

### Analytics Integration (PostHog)

```typescript
// app/providers.tsx
// Source: https://posthog.com/tutorials/nextjs-analytics
'use client';

import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';
import { useEffect } from 'react';

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      capture_pageview: false, // We'll manually capture
    });
  }, []);

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}

// Usage for pattern tracking
import { usePostHog } from 'posthog-js/react';

export function TaskList() {
  const posthog = usePostHog();

  const handleCreateTask = async () => {
    // ... create task logic

    // Track pattern usage
    posthog.capture('pattern_used', {
      pattern: 'task_create',
      hasAttachments: false,
      category: 'work',
    });
  };

  return <button onClick={handleCreateTask}>Create Task</button>;
}

```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual deploys via FTP/SSH | Git-based continuous deployment | ~2020 | Zero-config deploys, instant rollback |
| Environment vars in code | Platform environment management | ~2018 | Secrets never in git, per-environment config |
| Traditional VPS hosting | Serverless/edge platforms | ~2019 | Auto-scaling, pay-per-use, global distribution |
| Self-hosted PostgreSQL | Managed serverless databases | ~2021 | Auto-scaling, branching, zero-downtime |
| Manual performance testing | Real User Monitoring (RUM) | ~2019 | Track actual user experience, not synthetic tests |
| Polyfill-heavy bundles | Modern baseline (ES2020+) | Next.js 15 (2024) | Smaller bundles, faster loads |
| Client-side auth checks only | Server-side verification required | CVE-2025-29927 (2025) | Re-verify in every Server Action |

**Deprecated/outdated:**

- **next export for static hosting**: Use `output: 'export'` in next.config.js instead
- **API routes in pages/api**: App Router recommends route handlers (app/api/route.ts)
- **getServerSideProps**: Use Server Components in App Router instead
- **Custom server (server.js)**: Use Next.js standalone mode or middleware instead
- **Middleware-only auth**: Must re-verify in Server Actions due to CVE-2025-29927

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal validation period duration**
   - What we know: Need enough data to validate framework patterns, but not so long that feedback becomes stale
   - What's unclear: Specific timeframe depends on user acquisition rate
   - Recommendation: Start with 2-week validation window, extend if user count < 20 active users

2. **Usage quotas for free tier validation**
   - What we know: Vercel free tier allows 100GB bandwidth/month, Neon free tier allows 0.5GB storage
   - What's unclear: Whether free tier is sufficient or need to upgrade during validation
   - Recommendation: Start free, monitor metrics, upgrade if hitting limits (unlikely for validation phase)

3. **Domain strategy for validation vs production**
   - What we know: Can use free .vercel.app subdomain or custom domain
   - What's unclear: Whether validation should use temporary domain or final production domain
   - Recommendation: Use .vercel.app for validation (e.g., task-tracker-validation.vercel.app), move to custom domain after validation success

4. **Framework pattern prioritization**
   - What we know: Should track authentication, CRUD operations, file uploads, search/filter patterns
   - What's unclear: Which patterns are most valuable for MyWork framework learning
   - Recommendation: Track all major interactions, analyze after validation to identify highest-value patterns

5. **Data persistence strategy post-validation**
   - What we know: Validation data is valuable for framework learning
   - What's unclear: Whether to reset database after validation or keep production data
   - Recommendation: Keep validation data, clearly mark as "validation period" in analytics for future filtering

## Sources

### Primary (HIGH confidence)

- [Next.js Official Documentation - Analytics](https://nextjs.org/docs/pages/guides/analytics)
- [Next.js Official Documentation - Environment Variables](https://nextjs.org/docs/pages/guides/environment-variables)
- [Next.js Official Documentation - Production Checklist](https://nextjs.org/docs/app/guides/production-checklist)
- [Prisma Documentation - Deploying Database Changes](https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-database-changes-with-prisma-migrate)
- [Prisma Documentation - Development and Production](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production)
- [Vercel Documentation - Custom Domains](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
- [Railway Documentation - Public Domains](https://docs.railway.com/reference/public-domains)
- [TUS Protocol Official Site](https://tus.io/)

### Secondary (MEDIUM confidence)

- [Vercel vs Railway vs Kuberns Comparison 2026](https://kuberns.com/blogs/post/railway-vs-vercel-vs-kuberns/)
- [Deploying Full Stack Apps in 2026](https://www.nucamp.co/blog/deploying-full-stack-apps-in-2026-vercel-netlify-railway-and-cloud-options)
- [Best PostgreSQL Hosting Providers 2026](https://northflank.com/blog/best-postgresql-hosting-providers)
- [Complete Next.js Security Guide 2025](https://www.turbostarter.dev/blog/complete-nextjs-security-guide-2025-authentication-api-protection-and-best-practices)
- [Next.js Security Checklist](https://blog.arcjet.com/next-js-security-checklist/)
- [CVE-2025-29927 Next.js Header Injection Vulnerability](https://www.averlon.ai/blog/nextjs-cve-2025-29927-header-injection)
- [Upstash Feedback Widget Blog](https://upstash.com/blog/feedback-widget)
- [PostHog Next.js Tutorial](https://posthog.com/tutorials/nextjs-analytics)
- [Upstash Rate Limiting Blog](https://upstash.com/blog/nextjs-ratelimiting)
- [LogRocket Health Check Implementation](https://blog.logrocket.com/how-to-implement-a-health-check-in-node-js/)

### Tertiary (LOW confidence)

- [GitHub Actions Next.js Deployment Guide 2025](https://ayyaztech.com/blog/auto-deploy-nextjs-with-github-actions-complete-cicd-guide-2025) - Community guide, not official
- [TUS Node.js Server 2.0.0 Blog](https://tus.io/blog/2025/03/25/tus-node-server-v200) - Future-dated article (March 2025), may not be released yet

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Vercel and Neon are well-documented, widely adopted for Next.js in 2026
- Architecture: HIGH - Patterns verified with official Next.js, Prisma, and Vercel documentation
- Monitoring: HIGH - Vercel Speed Insights is built-in, PostHog has Next.js-specific guides
- Security: HIGH - CVE-2025-29927 is documented, security headers are standard practice
- Pitfalls: MEDIUM - Based on official docs and community experiences, some edge cases may exist

**Research date:** 2026-01-26
**Valid until:** 2026-02-25 (30 days - stable ecosystem, but monitoring for Next.js 15.x updates)

---

**Note for planner:** This research assumes the existing tech stack (Next.js 15.5.9, Prisma 7, PostgreSQL, GitHub OAuth) continues into deployment. The CONTEXT.md decisions (open access, direct GitHub login, framework validation focus) heavily influence the recommendations toward Vercel's simplicity and PostHog's pattern tracking capabilities.
