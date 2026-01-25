# Pitfalls Research

**Domain:** Task Management Application
**Researched:** 2026-01-24
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Prototype Code Shipped to Production

**What goes wrong:**
Prototype-level code shipped into production creates unstable systems with poor error handling, weak security, duplicated logic, and inadequate testing. This makes modules impossible to reuse without extensive refactoring.

**Why it happens:**
AI-accelerated development and time pressure make it tempting to ship fast prototypes directly to production. Teams skip the hardening phase between MVP and production, thinking "it works" is sufficient.

**How to avoid:**
- Establish automated guardrails that prevent merging to production without tests, error handling, and security checks
- Document hardening requirements explicitly in phase acceptance criteria
- For MyWork framework: Each module must pass reusability checklist before integration
- Never skip error handling, input validation, or security controls in initial implementation

**Warning signs:**
- No error boundaries or try-catch blocks
- Hard-coded values instead of configuration
- Missing tests for core functionality
- "TODO" comments for security or validation
- Database queries without parameterization
- No logging or monitoring instrumentation

**Phase to address:**
Phase 1 (Foundation) - Establish code quality standards and automated checks from day one. Every initial implementation must meet production standards.

---

### Pitfall 2: Tight Coupling Between Modules

**What goes wrong:**
Modules become interdependent with direct imports, shared global state, and framework-specific types exposed across boundaries. This prevents extracting modules for reuse in other MyWork projects.

**Why it happens:**
Developers prematurely generalize components with single use cases or take shortcuts by accessing other modules' internals directly instead of defining clean interfaces.

**How to avoid:**
- Define explicit module boundaries and interfaces before implementation
- Use dependency injection instead of direct imports
- Keep framework-specific types (React components, database entities) within module boundaries
- Export only public APIs, hide implementation details
- For file attachments: Create storage abstraction that works with any backend (local, S3, etc.)
- For GitHub integration: Isolate API calls behind service interface

**Warning signs:**
- Import statements reaching across multiple module levels
- Circular dependencies between modules
- Database entities exposed in API responses
- React components imported into business logic
- Multiple modules sharing same global state
- Changes in one module breaking tests in unrelated modules

**Phase to address:**
Phase 1 (Foundation) - Define module architecture with clear boundaries. Phase 2+ reviews enforce interface contracts.

---

### Pitfall 3: Database Schema for Single Use Case Only

**What goes wrong:**
Database schema designed too specifically for task tracker prevents reuse. Common issues: task queues implemented with table locking that breaks at scale, lack of partitioning causing slow queries, over-denormalization creating data redundancy.

**Why it happens:**
Teams ignore database goals beyond immediate requirements, failing to plan for extraction into reusable user management, file storage, or activity tracking modules.

**How to avoid:**
- Design tables with clear single responsibilities that map to reusable modules
- Separate concerns: users table (auth module), files table (storage module), tasks table (domain-specific)
- Use foreign keys, not embedded JSON, for relationships between reusable entities
- Plan for partitioning on large tables (tasks, activity logs) from the start
- Document purpose of each table and which module it belongs to
- Avoid task queues in database tables - use proper queue service if needed

**Warning signs:**
- User data duplicated across multiple tables
- File metadata embedded in task records instead of separate table
- Task-specific fields in user or file tables
- Queries requiring joins across 5+ tables for simple operations
- No indexes on frequently queried columns
- Lack of created_at/updated_at timestamps

**Phase to address:**
Phase 1 (Foundation) - Schema design review focused on modularity and reusability before any migrations.

---

### Pitfall 4: GitHub API Rate Limiting Not Handled

**What goes wrong:**
Integration gets banned from GitHub API for continuing requests while rate-limited. Using GITHUB_TOKEN exhausts 1,000 requests/hour limit quickly. Analytics fail when rate limit exceeded.

**Why it happens:**
Developers make multiple individual API calls instead of batching, don't implement retry logic with exponential backoff, ignore rate limit response headers, or use unauthenticated requests (60/hour limit).

**How to avoid:**
- Always authenticate requests (5,000 requests/hour for authenticated users)
- Check `x-ratelimit-remaining` header before each request
- Implement exponential backoff when `retry-after` header present
- Batch operations instead of individual calls
- Cache GitHub data locally instead of repeated API calls
- Monitor rate limit usage with alerts before hitting limits
- Consider GitHub App if serving organization (scales with repos/users)
- For usage tracking: Batch events and sync periodically, not per-action

**Warning signs:**
- Making GitHub API call on every user action
- No retry logic for rate limit errors (429 status)
- Not checking response headers
- Using unauthenticated requests
- No caching layer for GitHub data
- Multiple individual calls where batch endpoint exists

**Phase to address:**
Phase 2 (GitHub Integration) - Rate limiting handling must be implemented before any GitHub API usage goes to production.

---

### Pitfall 5: File Upload Limits and Security Not Validated

**What goes wrong:**
Large file uploads impact performance and exhaust storage. Malicious files uploaded without validation. File extensions and MIME types not verified, enabling security exploits.

**Why it happens:**
Teams prioritize "file upload works" over security and resource management. According to Cisco Talos, 25% of phishing incidents involve malicious attachments.

**How to avoid:**
- Enforce file size limits before upload starts (reject large files client-side)
- Validate both file extension AND MIME type server-side (don't trust client)
- Scan uploaded files for malware if handling untrusted user content
- Store files outside web root with randomized names
- Use pre-signed URLs for downloads instead of direct file access
- Implement virus scanning for production deployment
- For MyWork framework: File storage module must include validation by default

**Warning signs:**
- No file size limits enforced
- Only checking file extension, not MIME type
- Files stored in publicly accessible directory
- Original filenames preserved
- No virus scanning
- Missing Content-Security-Policy headers
- Files served with inline disposition (should be attachment)

**Phase to address:**
Phase 1 (File Attachments) - Security validation must be part of initial file upload implementation, not added later.

---

### Pitfall 6: Search and Filter Performance Not Planned

**What goes wrong:**
Search and filter work fine with 100 tasks, then system becomes sluggish at 10,000+ tasks. Queries without indexes cause full table scans. Users report slow performance as task volume scales.

**Why it happens:**
Developers test with small datasets and don't plan for indexing. Filters implemented with client-side JavaScript instead of database queries. No pagination on search results.

**How to avoid:**
- Add database indexes on all filterable columns (status, category, assigned_user, created_at)
- Implement pagination from day one (limit results to 50-100 per page)
- Use database query builder for filters, not in-memory filtering
- Test with realistic dataset (10,000+ tasks) before shipping
- For text search: Use database full-text search or dedicated search engine (not LIKE queries)
- Monitor query performance and add EXPLAIN ANALYZE to CI/CD

**Warning signs:**
- No indexes on filterable columns
- Loading all tasks into memory then filtering in JavaScript
- No pagination on task lists
- Using LIKE '%term%' queries without full-text index
- Search taking >500ms with moderate dataset
- N+1 queries when loading tasks with related data

**Phase to address:**
Phase 2 (Search/Filter) - Performance testing with large dataset required before phase completion.

---

### Pitfall 7: Vague Task State Management

**What goes wrong:**
Task states are unclear or overly complex. Users confused about what state means. State transitions not validated, allowing invalid flows (e.g., directly from "not started" to "completed" without "in progress").

**Why it happens:**
Common task management mistake: lack of clear state definitions. Teams implement too many states or allow all state transitions without business logic validation.

**How to avoid:**
- Keep states minimal and clearly defined (e.g., TODO, IN_PROGRESS, DONE)
- Define valid state transitions explicitly in code
- Validate state changes server-side (don't trust client)
- Add "reason" or "notes" field for state changes that need context
- For MyWork framework: State machine logic should be reusable module
- Document state meanings in user-facing help text

**Warning signs:**
- More than 5 task states
- Any state can transition to any other state
- No validation on state changes
- State transitions not logged for audit
- Users reporting confusion about what states mean
- State names unclear (e.g., "pending" vs "waiting" vs "blocked")

**Phase to address:**
Phase 1 (Core Task Management) - State machine implementation with validation before any task creation features.

---

### Pitfall 8: Missing Audit Trail for Debugging

**What goes wrong:**
Cannot debug production issues because no logging of who did what when. Cannot track down why task disappeared or who deleted it. User disputes cannot be resolved.

**Why it happens:**
Teams focus on happy path functionality and skip audit logging. Logging added as afterthought when first production issue occurs.

**How to avoid:**
- Log all state changes with user_id, timestamp, old_value, new_value
- For critical operations (delete, assign, status change): Create audit log entries
- Include request IDs in logs to trace operations across services
- For MyWork framework: Audit logging should be infrastructure-level concern, not per-feature
- Implement soft deletes (deleted_at column) instead of hard deletes
- Log GitHub API calls for rate limit debugging

**Warning signs:**
- No created_by/updated_by columns in tables
- Hard deletes instead of soft deletes
- No change history for critical fields
- Cannot answer "who changed this task last week?"
- No correlation IDs in logs
- Production debugging requires adding logging and redeploying

**Phase to address:**
Phase 1 (Foundation) - Audit logging infrastructure before any CRUD operations.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Storing files in database BLOBs | Simpler deployment, no external storage | Database bloat, slow queries, expensive backups, not reusable | Never for production; only during proof-of-concept |
| Using task status as string instead of enum | Flexible, easy to add new statuses | Typos cause bugs, impossible to enforce transitions, query performance | Never; enums/constants are trivial to set up |
| Global state for user session | Quick to implement | Cannot reuse modules, testing difficult, race conditions | Never; use proper state management from start |
| Frontend-only validation | Faster initial development | Security vulnerabilities, data corruption | Never; server validation is mandatory |
| Hardcoded GitHub token in code | Works during development | Security breach when committed, cannot reuse module | Development only with .env.example documentation |
| No database migrations | Simpler local development | Cannot deploy updates, schema drift across environments | Never; migrations are foundation |
| Embedding file paths in task records | Avoids JOIN queries | Cannot change storage backend, breaks when moving files | Never; use foreign keys |
| Using Array/JSON column for tags | Avoids many-to-many table | Cannot query efficiently, violates normalization, not reusable | Only if tags are purely display metadata with no filtering |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub API | Making call per user action, ignoring rate limits | Batch operations, implement exponential backoff, cache responses, monitor x-ratelimit-remaining |
| File Storage | Storing in local filesystem without abstraction | Abstract storage interface supporting local/S3/Azure from start |
| Email Notifications | Sending directly from app code | Use queue service (background job) with retry logic |
| Database | Direct SQL queries in route handlers | Repository pattern or ORM, prepared statements only |
| Authentication | Rolling custom auth system | Use established library (Passport.js, NextAuth, etc.) |
| Session Management | Storing sessions in memory | Use database or Redis for session store (required for horizontal scaling) |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all tasks for filtering in frontend | Works fine during development | Use database queries with indexes, implement pagination | >1,000 tasks per user |
| N+1 queries when loading tasks with users/files | Slow API responses | Use JOIN queries or eager loading, batch data loading | >100 tasks loaded at once |
| No indexes on search columns | Slow search | Add indexes during migration, not after performance issues | >10,000 total tasks |
| Full table scan for dashboard stats | Dashboard takes >5 seconds | Use aggregate queries with indexes, consider materialized views | >50,000 tasks |
| Real-time updates via polling every second | High server load, battery drain | Use WebSockets or Server-Sent Events, or poll every 30s minimum | >100 concurrent users |
| Storing file metadata in separate API calls | Many round trips for task list | Include file count/size in task query response | >10 files per task on average |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Not validating file MIME types | Malicious file upload exploits (25% of phishing uses attachments) | Server-side validation of extension AND MIME type, virus scanning |
| Allowing access to any task by ID | Users can access other users' tasks by guessing IDs | Check task ownership on every query, use WHERE user_id = current_user |
| Exposing GitHub tokens in frontend code | Token leakage allows unauthorized repo access | Store tokens server-side only, use server-to-server API calls |
| No CSRF protection on state changes | Attackers can change task status via forged requests | Implement CSRF tokens on all POST/PUT/DELETE endpoints |
| Using sequential task IDs | Information leakage (competitor sees you have 50 tasks) | Use UUIDs or non-sequential IDs |
| No rate limiting on login/API | Brute force attacks, API abuse | Implement rate limiting on authentication and API endpoints |
| Inline file display in browser | XSS via malicious SVG/HTML files | Force download with Content-Disposition: attachment |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Overwhelming task lists without prioritization | Users don't know what to work on first | Implement priority field, default sort by priority + due date |
| Vague task descriptions with no context | Team members confused about what to do | Require task description field, add support for markdown formatting |
| No empty state guidance | Blank screen confuses new users | Show onboarding message with "Create your first task" action |
| Too many required fields on task creation | Friction prevents quick task capture | Only title required, everything else optional |
| No keyboard shortcuts | Power users frustrated by mouse-only interface | Implement common shortcuts (N for new, E for edit, etc.) |
| Filter UI complexity | Users can't find tasks they're looking for | Provide preset filters (My tasks, Due today, etc.) alongside custom |
| No visual task status indicators | Users must read status text | Use color coding and icons for status |
| Cluttered attachment list | Hard to identify which file is which | Show file type icon, size, and upload date |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **File Upload:** Often missing MIME type validation, size limits, virus scanning - verify security checklist completed
- [ ] **Search:** Often missing indexes, pagination, performance testing - verify works with 10,000+ tasks
- [ ] **GitHub Integration:** Often missing rate limit handling, retry logic, error handling - verify rate limit tests pass
- [ ] **Task Deletion:** Often missing soft delete, cascade handling, audit logging - verify can recover deleted tasks
- [ ] **User Authentication:** Often missing session timeout, CSRF protection, rate limiting - verify security audit completed
- [ ] **Module Extraction:** Often missing clear interfaces, configuration abstraction - verify module can run standalone
- [ ] **Error Handling:** Often missing user-friendly messages, logging, monitoring - verify all error paths tested
- [ ] **State Transitions:** Often missing validation, audit trail - verify invalid transitions blocked

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Tight coupling between modules | HIGH | 1. Map all dependencies, 2. Define interfaces, 3. Refactor incrementally, 4. Add integration tests |
| No database indexes | LOW | 1. Identify slow queries, 2. Add indexes via migration, 3. Verify performance improvement |
| GitHub rate limit exceeded | LOW | 1. Implement caching layer, 2. Add exponential backoff, 3. Monitor rate limit headers |
| Prototype code in production | HIGH | 1. Add tests for existing behavior, 2. Refactor with tests passing, 3. Add error handling |
| File security issues | MEDIUM | 1. Audit existing files, 2. Add validation to upload endpoint, 3. Implement virus scanning |
| Missing audit trail | MEDIUM | 1. Add audit columns via migration, 2. Update all state change code, 3. Backfill what's possible |
| Poor search performance | MEDIUM | 1. Add indexes, 2. Implement pagination, 3. Consider full-text search engine |
| Vague state management | LOW | 1. Define state machine, 2. Add validation, 3. Migrate existing data if needed |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Prototype code shipped | Phase 1 (Foundation) | Automated code quality checks pass, no TODOs in production code |
| Tight coupling | Phase 1 (Foundation) | Module dependency diagram shows clean boundaries |
| Database schema not reusable | Phase 1 (Foundation) | Schema review confirms modular design, foreign keys not embedded data |
| GitHub rate limiting | Phase 2 (GitHub Integration) | Rate limit test suite passes, monitoring alerts configured |
| File upload security | Phase 1 (File Attachments) | Security checklist completed, MIME validation tests pass |
| Search performance | Phase 2 (Search/Filter) | Performance test with 10,000 tasks <500ms |
| Vague state management | Phase 1 (Core Tasks) | State machine tests validate transitions, documentation clear |
| Missing audit trail | Phase 1 (Foundation) | Audit log entries created for all state changes |

## Sources

**Task Management Pitfalls:**
- [Common Task Management Mistakes - Workast](https://www.workast.com/blog/common-task-management-mistakes-and-how-to-avoid-them/)
- [Task Management Apps: 10 Common Mistakes - Captain Time](https://captaintime.com/task-management-apps-10-common-mistakes/)
- [LinkedIn: Common Task Management Pitfalls](https://www.linkedin.com/advice/1/what-some-common-task-management-pitfalls-mistakes)

**Architecture Anti-Patterns:**
- [Software Architecture Anti-Patterns in 2026 - Medium](https://medium.com/@Adem_Korkmaz/software-architecture-anti-patterns-10-big-mistakes-we-somehow-still-make-in-2026-aeac8e0841f5)
- [Modular Frontend Architecture - Medium](https://kodekx-solutions.medium.com/modular-frontend-architecture-long-term-maintainability-tips-a7296ee56b2c)
- [Building Reusable React Components 2026 - Medium](https://medium.com/@romko.kozak/building-reusable-react-components-in-2026-a461d30f8ce4)

**Database Design Pitfalls:**
- [Database Schema Design Pitfalls - Medium](https://yu-ishikawa.medium.com/database-schema-design-for-data-engineering-essential-pitfalls-and-best-practices-9d3d8e3eba6d)
- [How to Design Task Management System - Medium](https://medium.com/@koladilip/how-to-design-task-management-system-9349b4152394)
- [Database Development with AI 2026 - Brent Ozar](https://www.brentozar.com/archive/2026/01/database-development-with-ai-in-2026/)

**GitHub API Integration:**
- [Managing GitHub API Rate Limits - Lunar.dev](https://www.lunar.dev/post/a-developers-guide-managing-rate-limits-for-the-github-api)
- [Best Practices for GitHub REST API - GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
- [Avoiding GitHub Rate Limiting - Kubeblogs](https://www.kubeblogs.com/how-to-avoid-github-token-rate-limiting-issues-complete-guide-for-devops-teams/)

**File Upload Security:**
- [Managing File Attachments Security - SoftwareMind](https://softwaremind.com/blog/managing-file-attachments-best-practices-for-cloud-security/)
- [File Storage Best Practices - ManageEngine](https://www.manageengine.com/data-security/best-practices/file-storage-best-practices.html)

**Production vs Prototype:**
- [Production Ready Code vs Vibe Coded Prototype - Arbisoft](https://arbisoft.com/blogs/production-ready-code-vs-vibe-coded-prototype-what-s-the-difference)
- [Technical Debt Strategic Guide 2026 - Monday.com](https://monday.com/blog/rnd/technical-debt/)
- [Dark Side of AI Prototyping - Product Release Notes](https://www.productreleasenotes.com/p/the-dark-side-of-ai-prototyping-technical)

**Performance and Scale:**
- [Task Management Software Performance - Quixy](https://quixy.com/blog/no-code-task-management-system/)
- [Microsoft Planner Filtering Performance - Manuel T. Gomes](https://manueltgomes.com/microsoft/planner/filtering-for-optimal-performance/)

---
*Pitfalls research for: Task Management Application for MyWork Framework*
*Researched: 2026-01-24*
