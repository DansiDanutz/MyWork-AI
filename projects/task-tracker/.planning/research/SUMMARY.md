# Project Research Summary

**Project:** task-tracker
**Domain:** Individual Task Management / Personal Productivity
**Researched:** 2026-01-24
**Confidence:** HIGH

## Executive Summary

This is a task management application for individual productivity, with specific requirements for file attachments and GitHub integration. Expert consensus recommends a modern full-stack JavaScript approach: Next.js 16+ with React 19, TypeScript for type safety, PostgreSQL for multi-user data integrity, and Prisma for type-safe database access. This stack choice prioritizes code reusability for the MyWork framework — strong typing and modular architecture enable brain extraction for future projects.

The recommended approach is a modular monolith with clear layer separation (presentation, application, business logic, data). Start with core task CRUD and authentication, establish production-quality code standards from day one, then layer on file attachments and GitHub integration. This order prevents the most critical pitfall: shipping prototype-level code that can't be reused. Every module must meet production standards initially — no "we'll harden it later" mindset.

Key risks center on integration complexity (GitHub API rate limiting, file upload security) and maintaining module boundaries for reusability. Mitigation: implement rate limit handling and file validation from the start, design database schema with clear module ownership, use repository pattern and dependency injection to prevent tight coupling. The research shows that "looks done but isn't" is the primary failure mode — search without indexes, file upload without validation, state changes without audit trails. Each phase must include security, performance, and reusability validation, not just functional completion.

## Key Findings

### Recommended Stack

Modern JavaScript full-stack with production-grade tooling optimized for code reusability. Next.js 16 with React 19 provides server components and automatic optimization (38% faster initial loads vs React 18). TypeScript 5.x is mandatory for maintainable modules that can be extracted as brains. Prisma 6.19+ delivers type-safe database access and is now Rust-free (TypeScript-only). PostgreSQL 16.x handles multi-user concurrency far better than SQLite (required for deployed task management). shadcn/ui provides accessible components you own and customize — critical for brain reusability since you're not locked into npm package versions.

**Core technologies:**
- **Next.js 16+**: Full-stack framework with stable Turbopack, React 19 support, SSR/SSG built-in — industry standard for rapid MVP with production-ready defaults
- **TypeScript 5.x**: De facto standard for maintainable Node.js, native support in Node.js with experimental flag, critical for brain reusability
- **Prisma 6.19+**: Type-safe ORM with automatic migrations, visual data explorer, gold standard for database access
- **PostgreSQL 16.x**: Production-grade RDBMS with excellent scaling, complex query support, data integrity — required for multi-user concurrent access
- **shadcn/ui**: Beautifully designed accessible components you own (copy-paste, not npm), official task management example available

**Supporting libraries:**
- **@octokit/oauth-app**: Official GitHub OAuth toolset for Node.js, better than generic OAuth for GitHub-specific features
- **uploadthing**: Type-safe file uploads built for Next.js, simpler than AWS S3 for MVP, serverless-friendly
- **zod**: Runtime validation with TypeScript inference, pairs perfectly with tRPC and Prisma
- **@tanstack/react-query**: Server state management with cache, background refetching, optimistic updates — critical for responsive task UX

**What NOT to use:**
- Next.js Pages Router (legacy, use App Router)
- Create React App (unmaintained since 2022)
- MongoDB (overkill for structured task data, relational fits better)
- NextAuth.js v5 (still beta as of Jan 2025, migration painful)
- Redux (unnecessary with React 19 + TanStack Query)

### Expected Features

Research identifies clear tiers: table stakes users expect, differentiators for competitive advantage, and anti-features that create problems.

**Must have (table stakes):**
- Task CRUD (create/edit/delete) — absolute minimum for any task manager
- Task completion toggle — psychological satisfaction is core value prop
- Due dates — time-bound tasks are fundamental to productivity
- Search tasks — users expect instant search as of 2026
- Filter by status/date — view active, completed, overdue
- Priority levels — distinguish urgent from non-urgent
- User accounts — personal task lists require authentication
- Responsive design — mobile support is table stakes, not optional
- Persistent storage — database persistence, not just localStorage
- Task descriptions — details beyond title
- Basic task lists/projects — organization beyond single list

**Should have (competitive advantage):**
- **File attachments** (REQUIRED for this project) — Todoist offers this premium-only, competitors lack it — context without leaving app
- **GitHub integration** (REQUIRED for this project) — usage tracking for technical users, unique differentiator
- Tags/labels — cross-project categorization (defer to v1.1+)
- Keyboard shortcuts — speed for power users (defer to v1.1+)
- Bulk operations — batch edit/delete when users have 50+ tasks (defer to v1.1+)
- Dark mode — user preference, reduces eye strain (defer to v1.1+)
- Subtasks — complex task breakdown (defer to v1.1+ after validation)

**Defer to v2+ (future consideration):**
- Natural language input — high complexity, questionable ROI for MVP
- Offline support — architectural complexity, validate online-first first
- Task templates — unclear value until usage patterns emerge
- Recurring tasks — complex edge cases, manually recreate for MVP
- Real-time collaboration — massive complexity for solo/small team use case

**Anti-features (avoid):**
- Real-time collaboration — adds months of engineering for individual productivity tool, simple sharing with refresh-to-update is adequate
- Gantt charts — project management, not personal task lists, scope creep
- Time tracking built-in — separate concern, adds UI complexity with unclear value
- Custom fields everywhere — analysis paralysis, cluttered UI, users want structure not infinite flexibility
- Gamification — can feel gimmicky, requires careful psychological design
- AI task suggestions — 2026 AI hype, users want control not AI deciding priorities

### Architecture Approach

Standard layered architecture (N-tier) with modular monolith structure. Three-layer separation: routes handle HTTP concerns, controllers transform requests/responses, services contain business logic and coordinate repositories. This enables brain extraction — each layer has clean interfaces and can be tested independently.

**Major components:**
1. **Presentation Layer (React)** — UI components, routing, client state management with Context API, unidirectional data flow
2. **Application Layer (Express.js)** — API routes, middleware chain (auth, validation, error handling), request/response transformation
3. **Business Logic (Services)** — Task operations, validation, authorization, coordination between repositories and external APIs
4. **Data Access (Repositories)** — Database operations abstracted via repository pattern, file storage, GitHub API clients
5. **Integration Services** — GitHub API client with rate limiting, file upload service with security validation

**Key patterns to follow:**
- **Repository Pattern** — abstracts database operations, enables testing and storage backend swapping
- **Service Layer Pattern** — centralizes business logic for reuse across different entry points (API, CLI, background jobs)
- **Middleware Chain** — composable processing pipeline for cross-cutting concerns (auth, validation, logging)
- **DTO (Data Transfer Object)** — separate database schema from API responses, prevents exposing internal fields

**What NOT to do:**
- God controllers — put business logic in services, not controllers
- Premature microservices — start with modular monolith, extract services only at proven scale
- Mix database schema with API responses — exposes sensitive fields, couples API to schema
- No error boundaries — implement centralized error handling from start
- No file validation — validate size, MIME type, scan for malware

### Critical Pitfalls

Research reveals eight critical pitfalls, ranked by impact and frequency in task management projects.

1. **Prototype code shipped to production** — Unstable systems with poor error handling, weak security, duplicated logic. AI-accelerated development makes it tempting to ship fast prototypes directly. **Prevention:** Establish automated guardrails preventing merges without tests/error handling/security. Each module must pass reusability checklist before integration. Never skip error handling or validation in initial implementation.

2. **Tight coupling between modules** — Direct imports, shared global state, framework-specific types exposed across boundaries prevents brain extraction. **Prevention:** Define explicit module boundaries and interfaces before implementation, use dependency injection, keep React/database types within module boundaries, export only public APIs.

3. **Database schema for single use case only** — Schema too specific to task tracker prevents reuse of user management, file storage, activity tracking modules. **Prevention:** Design tables with single responsibilities mapping to reusable modules, separate users table (auth), files table (storage), tasks table (domain-specific), use foreign keys not embedded JSON.

4. **GitHub API rate limiting not handled** — Integration gets banned for continuing requests while rate-limited (1,000 requests/hour with GITHUB_TOKEN). **Prevention:** Always authenticate (5,000 req/hr), check x-ratelimit-remaining header, implement exponential backoff, batch operations, cache GitHub data locally, batch events and sync periodically not per-action.

5. **File upload limits and security not validated** — Large uploads impact performance, malicious files uploaded without validation (25% of phishing uses attachments per Cisco Talos). **Prevention:** Enforce size limits client and server-side, validate extension AND MIME type server-side, scan for malware, store files outside web root with randomized names, use pre-signed URLs for downloads.

6. **Search and filter performance not planned** — Works with 100 tasks, sluggish at 10,000+ tasks due to missing indexes and client-side filtering. **Prevention:** Add database indexes on filterable columns, implement pagination from day one, use database queries not in-memory filtering, test with 10,000+ tasks before shipping.

7. **Vague task state management** — Unclear states, invalid transitions allowed (e.g., "not started" directly to "completed"). **Prevention:** Keep states minimal (TODO, IN_PROGRESS, DONE), define valid transitions explicitly in code, validate server-side, document state meanings.

8. **Missing audit trail for debugging** — Cannot debug production issues, no logging of who did what when. **Prevention:** Log all state changes with user_id/timestamp/old_value/new_value, implement soft deletes (deleted_at) instead of hard deletes, include request IDs for tracing.

## Implications for Roadmap

Based on research, suggested phase structure prioritizes foundation quality, addresses pitfalls early, and builds features in dependency order.

### Phase 1: Foundation & Core Task Management
**Rationale:** Must establish production-quality patterns and infrastructure before any features. Pitfalls research shows prototype code shipped to production is the #1 risk — prevent this by setting standards from day one. Authentication enables all personalized features, task CRUD is the foundation everything builds on.

**Delivers:**
- User registration/login (GitHub OAuth preferred)
- Production-ready infrastructure (error handling, logging, audit trails)
- Task CRUD with proper validation
- Task completion toggle
- Due dates and priority levels
- Basic task lists/projects for organization
- Database schema designed for modularity

**Addresses features:**
- User accounts (table stakes)
- Task CRUD (table stakes)
- Task completion (table stakes)
- Due dates (table stakes)
- Priority levels (table stakes)
- Task lists/organization (table stakes)

**Avoids pitfalls:**
- Pitfall #1 (prototype code) — establish code quality standards and automated checks from start
- Pitfall #2 (tight coupling) — define module boundaries and interfaces upfront
- Pitfall #3 (database schema) — design tables with clear module responsibilities, plan for extraction
- Pitfall #7 (vague states) — implement state machine with validation
- Pitfall #8 (missing audit) — build audit logging infrastructure before CRUD operations

**Research flag:** Standard patterns — skip research-phase. Authentication and CRUD are well-documented with established libraries.

### Phase 2: Search, Filter & Performance
**Rationale:** With core data model stable, implement discovery features with performance considerations built-in from start. Research shows search/filter is table stakes but often implemented without indexes or pagination, causing performance problems at scale.

**Delivers:**
- Full-text search across task titles and descriptions
- Multi-dimensional filtering (status, priority, due date, project)
- Pagination for large task lists
- Database indexes on all filterable columns
- Performance validation with 10,000+ task dataset

**Addresses features:**
- Search tasks (table stakes)
- Filter by status/date (table stakes)

**Avoids pitfalls:**
- Pitfall #6 (search performance) — indexes, pagination, database queries from start, test with realistic dataset

**Uses stack:**
- PostgreSQL full-text search capabilities
- Prisma query builder with filtering

**Research flag:** Standard patterns — skip research-phase. Database search/filter is well-documented.

### Phase 3: File Attachments
**Rationale:** Required per project spec. File management is its own module with clear boundaries (file storage abstraction). Research shows file uploads are often "complete" without security validation — must include MIME validation, size limits, malware scanning from start.

**Delivers:**
- File upload with drag-and-drop UI
- File size limits enforced (client and server)
- MIME type and extension validation server-side
- File metadata storage in separate table (not embedded in tasks)
- File download with proper Content-Disposition headers
- Storage abstraction supporting local/S3 backends

**Addresses features:**
- File attachments (required differentiator)

**Avoids pitfalls:**
- Pitfall #5 (file security) — validation, limits, security checklist before any uploads go to production
- Pitfall #2 (tight coupling) — file service abstracted, works independently of task domain

**Uses stack:**
- uploadthing for MVP (serverless-friendly)
- Design for easy migration to S3 at scale

**Implementation pattern:**
- Repository pattern for file metadata
- Service layer coordinates file storage + database updates
- Separate files table with foreign key to tasks

**Research flag:** Needs phase-specific research. File upload security and validation strategies need deeper investigation (virus scanning options, cloud storage migration patterns).

### Phase 4: GitHub Integration
**Rationale:** Required per project spec. Integration demonstrates external API patterns for brain reusability. Research shows GitHub API rate limiting is frequently mishandled — must implement monitoring, caching, exponential backoff from start.

**Delivers:**
- GitHub OAuth integration for authentication
- Usage event tracking (task created/completed/deleted)
- Rate limit monitoring with alerts before hitting limits
- Exponential backoff retry logic
- Event batching (sync periodically, not per-action)
- GitHub API client as standalone module

**Addresses features:**
- GitHub integration (required differentiator)

**Avoids pitfalls:**
- Pitfall #4 (GitHub rate limiting) — rate limit handling, caching, batching before production usage

**Uses stack:**
- @octokit/oauth-app for OAuth
- @octokit/rest for API calls

**Implementation pattern:**
- Service layer wraps GitHub API
- Event queue for batching
- Separate integration module

**Research flag:** Needs phase-specific research. GitHub API rate limit strategies, webhook setup, event tracking patterns need investigation.

### Phase 5: Polish & Refinement
**Rationale:** After core features work, add usability improvements and responsive design polish. These enhance the experience but aren't blocking for launch.

**Delivers:**
- Responsive design optimized for mobile
- Dark mode support
- Empty state guidance for new users
- Improved task descriptions with markdown formatting
- Visual status indicators (colors, icons)
- Data export/backup functionality

**Addresses features:**
- Responsive design (table stakes)
- Dark mode (nice-to-have)
- Task descriptions enhancement (table stakes improvement)

**Research flag:** Standard patterns — skip research-phase. UI/UX polish uses established libraries (shadcn/ui themes).

### Phase Ordering Rationale

- **Foundation first prevents technical debt:** Establishing production standards, error handling, audit logging, and modular architecture upfront prevents the #1 pitfall (shipping prototype code). You can't "add quality later" — it must be built-in from start.

- **Search after CRUD stabilizes schema:** Can't index efficiently until data model is finalized. Building search early leads to performance problems when schema changes.

- **Integrations after core features work:** File attachments and GitHub integration are complex. Attempting them before authentication and task management are stable leads to scope creep and coupling issues.

- **Polish last enables feedback-driven iteration:** Responsive design and dark mode are important but can be refined based on real usage patterns. Prioritizing them too early wastes effort on features users might not value.

- **Dependency order prevents rework:** User auth → Task CRUD → Search/Filter → File Attachments → GitHub Integration. Each depends on previous phases being stable. Building out of order causes integration friction and refactoring.

### Research Flags

**Phases needing deeper research during planning:**

- **Phase 3 (File Attachments):** Complex security and storage concerns. Need research on:
  - Virus scanning options (ClamAV, cloud services)
  - Cloud storage migration patterns (local → S3)
  - File validation best practices beyond MIME checks
  - Backup and disaster recovery for attachments

- **Phase 4 (GitHub Integration):** External API integration patterns. Need research on:
  - GitHub API rate limit strategies and monitoring tools
  - Webhook setup and event processing
  - OAuth token management and refresh
  - Error handling for GitHub API downtime

**Phases with standard patterns (skip research-phase):**

- **Phase 1 (Foundation):** Well-documented authentication (NextAuth, Passport.js), CRUD patterns established, Prisma documentation comprehensive
- **Phase 2 (Search/Filter):** PostgreSQL full-text search documented, Prisma filtering well-supported
- **Phase 5 (Polish):** shadcn/ui provides theme support, responsive design patterns established

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official documentation for Next.js 16, React 19, Prisma 6.19, PostgreSQL 16. Multiple verified sources confirm 2025/2026 best practices. TypeScript and Prisma critical for reusability. |
| Features | HIGH | Cross-referenced Todoist, Microsoft To Do, Things 3 feature sets with multiple 2026 best practice articles. Clear distinction between table stakes and differentiators. Anti-features identified from project management pitfall research. |
| Architecture | HIGH | Verified patterns from official documentation (Android architecture guide applies to web), production task management systems documented in Medium articles, REST API and database design best practices from authoritative sources. |
| Pitfalls | HIGH | Multiple sources for each pitfall category (task management mistakes, architecture anti-patterns, database design pitfalls, GitHub API rate limiting, file upload security). Cisco Talos data on malicious attachments, Brent Ozar on database development, production-ready code vs prototype clearly distinguished. |

**Overall confidence: HIGH**

All research areas have multiple authoritative sources. Stack recommendations come from official documentation (Next.js, React, Prisma, PostgreSQL). Feature analysis cross-references actual competitor products and 2026 best practice guides. Architecture patterns verified against production systems. Pitfalls documented in both general software engineering sources and task management specific articles.

### Gaps to Address

**Module extraction strategy:** Research covers modular architecture principles but doesn't deeply explore practical extraction patterns for MyWork brains. During implementation, document:
- How to package a module for reuse (directory structure, exports, config)
- Testing strategy for extracted brains (isolated test suite)
- Version compatibility handling across projects using same brain

**Scaling thresholds:** Research identifies scaling bottlenecks (database connections ~5k users, file storage ~10k users) but doesn't specify monitoring thresholds or early warning signals. During Phase 1, establish:
- Performance baseline metrics for each component
- Monitoring alerts for approaching scale limits
- Load testing strategy to validate scaling assumptions

**GitHub integration specifics:** Research identifies rate limiting as critical but doesn't detail optimal batching intervals or event types to track. During Phase 4 planning, determine:
- Which GitHub events provide most value for usage tracking
- Optimal sync frequency balancing freshness vs rate limits
- Local caching strategy for GitHub data

**File storage migration:** Research recommends starting with local storage and migrating to S3 at scale, but doesn't specify migration path. During Phase 3, document:
- Abstraction layer design allowing runtime storage backend selection
- Migration script approach for moving existing files
- Rollback plan if cloud storage migration fails

These gaps are expected — they require implementation context to resolve. Flag them for attention during respective phase planning rather than attempting to resolve in initial research.

## Sources

### Primary (HIGH confidence)

**Official Documentation:**
- Next.js 16.1.4 Documentation — Current stable version, App Router best practices
- React 19.2 Release — Stable release with Server Components
- Prisma Documentation — TypeScript ORM, Rust-free as of 6.16
- PostgreSQL Documentation — Database capabilities and best practices
- shadcn/ui Documentation — Component library with task management example
- GitHub OAuth Apps Documentation — Official OAuth implementation guide
- GitHub REST API Best Practices — Rate limiting, error handling

**Research Domain:**
- [Context7] 5 Essential Features of a Productivity App in 2026
- [Context7] Best task management software in 2026 (features & price compared)
- [Context7] Todoist vs Microsoft To-Do comparison
- [Context7] Task Management Anti-Patterns and Common Mistakes
- [Context7] Software Architecture Anti-Patterns in 2026
- [Context7] Managing GitHub API Rate Limits
- [Context7] Managing File Attachments Security Best Practices

### Secondary (MEDIUM confidence)

**Stack and Technology:**
- Strapi: React & Next.js in 2025 Best Practices
- Vercel: React Best Practices (10+ years optimization knowledge)
- Talent500: React & Next.js State, Performance 2025
- Backend Stack 2025 (Node.js ecosystem trends)
- PostgreSQL vs SQLite comparison (Astera)
- Cloudinary vs AWS S3 cost analysis (Bytescale)

**Architecture and Patterns:**
- Chapter 2: High-Level Design for Task Management System (Medium)
- Building a Full-Stack Task Management App with TypeScript/React/Node (DEV)
- Guide to App Architecture (Android Developers — applicable patterns)
- Modular Frontend Architecture for Long-Term Maintainability (Medium)

**Pitfalls and Anti-Patterns:**
- Production Ready Code vs Vibe Coded Prototype (Arbisoft)
- Technical Debt Strategic Guide 2026 (Monday.com)
- Dark Side of AI Prototyping (Product Release Notes)
- Database Schema Design Pitfalls (Medium)

### Tertiary (LOW confidence)

**Edge Cases and Specific Techniques:**
- No-Code Task Management System (Quixy) — performance considerations
- Microsoft Planner Filtering Performance — optimization strategies
- Database Development with AI in 2026 (Brent Ozar) — testing approaches

---
*Research completed: 2026-01-24*
*Ready for roadmap: yes*
