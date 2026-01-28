# Stack Research

**Domain:** Task Management Application
**Researched:** 2025-01-24
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
| ------------ | --------- | --------- | ----------------- |
| **Next.js** | 16.1+ | Full-stack ... | Industry st... |
  | **React** | 19.2+ | UI library | Stable rele... |  
  | **TypeScript** | 5.x | Type safety | De facto st... |  
| **Prisma** | 6.19+ | Database ORM | Type-safe d... |
| **PostgreSQL** | 16.x | Database | Production-... |
  | **shadcn/ui** | Latest | UI components | Beautifully... |  
  | **Tailwind ... | 3.x | Styling | Next.js opt... |  

### Supporting Libraries

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
  | **@octokit/... | Latest | GitHub OAuth | Official Gi... |  
| **uploadthi... | Latest | File uploads | Type-safe f... |
  | **zod** | Latest | Validation | Runtime val... |  
| **react-hoo... | Latest | Form handling | Performant ... |
  | **@tanstack... | Latest | Server state | Cache manag... |  
| **date-fns** | Latest | Date utilities | Lightweight... |

### Development Tools

| Tool | Purpose | Notes |
| ------ | --------- | ------- |
| **tsx** | TypeScript runner | Faster than ts-nod... |
  | **ESLint** | Linting | Use Next.js ESLint... |  
  | **Prettier** | Formatting | Consistent code st... |  
  | **Prisma Studio** | Database GUI | Visual data explor... |  
| **Vercel** | Deployment | Zero-config Next.j... |

## Installation

```bash

# Create Next.js app with TypeScript and App Router

npx create-next-app@latest task-tracker --typescript --tailwind --app --turbopack

# Core dependencies

npm install prisma @prisma/client zod react-hook-form @hookform/resolvers
npm install @tanstack/react-query date-fns

# GitHub OAuth

npm install @octokit/oauth-app

# File uploads

npm install uploadthing @uploadthing/react

# shadcn/ui (run after project creation)

npx shadcn@latest init
npx shadcn@latest add button input label card table dialog form

# Dev dependencies

npm install -D tsx @types/node

```markdown

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
| ------------- | ------------- | ------------------------- |
  | **Next.js 16** | Remix 2.5+ | If you prefer nest... |  
| **Prisma** | Drizzle ORM | If you want SQL-fi... |
  | **PostgreSQL** | SQLite | Only for local pro... |  
  | **uploadthing** | AWS S3 + CloudFront | If monthly bandwid... |  
  | **Vercel** | Railway / Render | If you need more c... |  
| **@octokit/oauth-a... | Passport.js | If you need multip... |
| **shadcn/ui** | Chakra UI / Materi... | If you prefer pre-... |

## What NOT to Use

| Avoid | Why | Use Instead |
| ------- | ----- | ------------- |
  | **Next.js Pages Ro... | Legacy router. App... | **Next.js App Rout... |  
  | **Create React App** | Unmaintained since... | **Next.js** or Vit... |  
  | **MongoDB** | Overkill for struc... | **PostgreSQL** |  
  | **Express.js** | Unnecessary with N... | **Next.js API Rout... |  
  | **NextAuth.js v5** | Still in beta (as ... | **Clerk** (managed... |  
| **Moment.js** | Deprecated. Large bundle size. | **date-fns** or **Day.js** |
  | **Cloudinary** | Expensive for simp... | **uploadthing** or... |  
  | **Redux** | Unnecessary comple... | **TanStack Query**... |  

## Stack Patterns by Variant

**If building MVP for quick deployment (RECOMMENDED):**

- Use Vercel for hosting (zero-config, auto-deploy from GitHub)
- Use Vercel Postgres for database (integrated, no separate config)
- Use uploadthing for files (serverless-friendly, simple setup)
- Use shadcn/ui components (copy-paste, instant professional UI)
- Authentication: Clerk (10-minute setup) or custom GitHub OAuth (more control)

**If optimizing for cost at scale (>10K users):**

- Use Railway or self-hosted for compute
- Use managed PostgreSQL (e.g., Supabase, Neon, or AWS RDS)
- Use AWS S3 + CloudFront for files (costs 60-85% less than Cloudinary at

  >2TB/month)

- Authentication: Custom GitHub OAuth implementation (no per-user pricing)

**If prioritizing code ownership and framework portability:**

- Use standard React patterns (avoid Vercel-specific features)
- Use Prisma with raw SQL escape hatches for complex queries
- Use vanilla S3 SDK (not uploadthing) for file storage
- Use shadcn/ui (you own the component code)
- Build custom auth (full control, no vendor lock-in)

## Version Compatibility

| Package A | Compatible With | Notes |
| ----------- | ----------------- | ------- |
  | Next.js 16.x | React 19.2+ | Next.js 16 require... |  
  | Prisma 6.19+ | PostgreSQL 12+ | Prisma 6.16+ is Ru... |  
  | shadcn/ui | Next.js 13+ | Works with App Rou... |  
| @octokit/oauth-app | Node.js 18+ | GitHub's official ... |
  | uploadthing | Next.js 13+ | Designed for App R... |  
  | TanStack Query | React 18+ | Works with React 1... |  
  | TypeScript 5.x | Node.js 18+ | Native TypeScript ... |  

## Critical Configuration Notes

**Next.js + Prisma:**
Add postinstall script to package.json for Vercel deployments:

```json
{
  "scripts": {

```yaml

"postinstall": "prisma generate"

```yaml
  }
}

```yaml

**TypeScript Strict Mode:**
Enable strict mode in tsconfig.json for maximum type safety (critical for brain
reusability):

```json
{
  "compilerOptions": {

```

"strict": true,
"strictNullChecks": true,
"noUncheckedIndexedAccess": true

```yaml
  }
}

```yaml

**ESLint + Prettier:**
Use Next.js ESLint config with TypeScript:

```bash
npm install -D eslint-config-next @typescript-eslint/eslint-plugin

```yaml

**Environment Variables:**
Use .env.local for development (gitignored). Vercel auto-loads these in
production.
Required variables:

- `DATABASE_URL` (PostgreSQL connection string)
- `GITHUB_CLIENT_ID` (OAuth app credentials)
- `GITHUB_CLIENT_SECRET`
- `UPLOADTHING_TOKEN` (if using uploadthing)

## Sources

### HIGH Confidence (Official Documentation)

- [Next.js 16.1.4 Documentation](https://nextjs.org/docs) — Current stable

  version, App Router best practices

- [Next.js 16 Release Blog](https://nextjs.org/blog/next-16) — Turbopack stable,

  React 19 support, proxy.ts

- [React 19.2 Release](https://react.dev/blog/2025/10/01/react-19-2) — Stable

  release with Server Components

- [Prisma Documentation](https://www.prisma.io/docs) — TypeScript ORM, Rust-free

  as of 6.16

- [shadcn/ui Documentation](https://ui.shadcn.com/) — Component library, task

  example available

- [GitHub OAuth Apps

  Documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps)
  — Official OAuth implementation guide

### MEDIUM Confidence (Verified with Multiple Sources)

- [Strapi: React & Next.js in 2025 Best

  Practices](https://strapi.io/blog/react-and-nextjs-in-2025-modern-best-practices)
  — Modern patterns

- [Vercel: React Best

  Practices](https://vercel.com/blog/introducing-react-best-practices) — 10+
  years optimization knowledge

- [Talent500: React & Next.js State,

  Performance](https://talent500.com/blog/modern-frontend-best-practices-with-react-and-next-js-2025/)
  — 2025 standards

- [Backend Stack 2025 - DEV

  Community](https://dev.to/rutvikmakvana4/backend-stack-2025-3nmh) — Node.js
  ecosystem trends

- [Fastify vs Express

  2025](https://medium.com/codetodeploy/express-or-fastify-in-2025-whats-the-right-node-js-framework-for-you-6ea247141a86)
  — Framework comparison

- [PostgreSQL vs SQLite -

  Astera](https://www.astera.com/knowledge-center/postgresql-vs-sqlite/) —
  Database selection criteria

- [Cloudinary vs AWS S3 -

  Bytescale](https://www.bytescale.com/blog/cloudinary-vs-s3/) — Cost analysis
  at
  scale

- [Clerk Auth Guide for Next.js

  2025](https://clerk.com/articles/user-authentication-for-nextjs-top-tools-and-recommendations-for-2025)
  — Authentication options

- [NextAuth vs Clerk

  Comparison](https://medium.com/@sagarsangwan/next-js-authentication-showdown-nextauth-free-databases-vs-clerk-vs-auth0-in-2025-e40b3e8b0c45)
  — Auth stack decision

### Additional References

- [Vercel Next.js + PostgreSQL

  Guide](https://vercel.com/kb/guide/nextjs-prisma-postgres) — Deployment
  patterns

- [Node.js TypeScript Best Practices

  2025](https://medium.com/@chirag.dave/node-js-in-2025-modern-practices-you-should-be-using-65f202c6651d)
  — Modern Node.js patterns

- [Prisma Deep Dive

  2025](https://dev.to/mihir_bhadak/prisma-deep-dive-handbook-2025-from-zero-to-expert-1761)
  — ORM best practices

---
*Stack research for: Task Management Application*
*Researched: 2025-01-24*
*For: MyWork framework proof-of-concept with production-ready code quality*
