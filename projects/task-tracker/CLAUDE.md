# Task Tracker - AI Agent Instructions

## Project Purpose

**This is a framework validation project** - its primary goal is to prove the MyWork framework can deliver production-ready applications with reusable patterns.

**Key Principle**: Every feature must demonstrate genuine user value AND technical reusability for the brain.

---

## Quick Start for AI Agents

When working on the Task Tracker:

1. **Check current state**: Read `.planning/STATE.md` (Phase 8 complete, deployed to production)
2. **Understand architecture**: Read `.planning/research/ARCHITECTURE.md` (30,534 bytes - comprehensive!)
3. **Review features**: Check `.planning/research/FEATURES.md` (14,023 bytes - complete inventory)
4. **Avoid pitfalls**: Read `.planning/research/PITFALLS.md` (20,252 bytes - learn from mistakes)
5. **Use GSD commands**: `/gsd:progress`, `/gsd:plan-phase N`, `/gsd:execute-phase N`

**Start Commands**:
```bash
cd projects/task-tracker

# First time setup
npm install
npx prisma generate
npx prisma migrate dev

# Start development
npm run dev        # Start on http://localhost:3000
```

---

## Common Workflows

### Adding a New Feature

**When to use**: User wants to add new functionality

**Before You Start**:
1. Check `REQUIREMENTS.md` - Is this feature in scope?
2. Verify it demonstrates reusability - Can this pattern be reused in other projects?
3. Check `FEATURES.md` - Is it already implemented?

**Steps**:
1. **Plan with GSD**: Use `/gsd:plan-phase N` to create detailed plan
2. **Execute with GSD**: Use `/gsd:execute-phase N` to implement in parallel waves
3. **Document patterns**: Add to brain for future reuse
4. **Test thoroughly**: Use `/gsd:verify-work N` for user acceptance testing

**Example**:
```bash
/gsd:plan-phase 9    # Plan Phase 9: New Feature
/gsd:execute-phase 9 # Execute Phase 9
/gsd:verify-work 9  # Verify the implementation
```

---

### Working on Authentication

**When to use**: User wants to modify auth system

**Key Files**:
- `src/app/api/auth/[...nextauth]/route.ts` - NextAuth configuration
- `prisma/schema.prisma` - User and Account models
- `src/shared/lib/auth.ts` - Auth utilities

**How it Works**:
- Uses **NextAuth.js** with GitHub OAuth
- GitHub OAuth is **mandatory** for authentication
- User data stored in PostgreSQL via Prisma
- Session managed via JWT tokens

**Steps to Modify**:
1. Check `src/app/api/auth/[...nextauth]/route.ts` for current config
2. Add new providers if needed (Google, etc.)
3. Update session callbacks if changing session data
4. Test OAuth flow thoroughly
5. Check database models in `prisma/schema.prisma`

**Common Tasks**:
- Add new OAuth provider → Add to `providers` array in `[...nextauth]/route.ts`
- Modify session data → Update `session()` callback
- Add user profile fields → Update `User` model in `schema.prisma`

---

### Working on Tasks

**When to use**: User wants to modify task management features

**Key Files**:
- `src/app/api/tasks/` - Task CRUD API endpoints
- `src/app/tasks/` - Task pages
- `src/app/(app)/tasks/` - App-shell task pages
- `src/shared/components/TaskList.tsx` - Task list component
- `src/app/actions/tasks.ts` - Server actions for tasks

**Database Schema**:
```prisma
model Task {
  id          String   @id @default(uuid())
  title       String
  description String?
  completed   Boolean  @default(false)
  dueDate     DateTime?
  priority    Priority @default(MEDIUM)
  tags        Tag[]
  files       File[]
  userId      String
  user        User     @relation(...)
}
```

**Steps to Modify**:
1. **API Layer**: Add/modify endpoints in `src/app/api/tasks/`
2. **Server Actions**: Add/modify actions in `src/app/actions/tasks.ts`
3. **Components**: Update UI components in `src/shared/components/`
4. **Pages**: Update pages in `src/app/tasks/` or `src/app/(app)/tasks/`
5. **Database**: Update schema in `prisma/schema.prisma` (if needed)

**Common Tasks**:
- Add new task field → Update `Task` model, migrate database, update UI
- Add task filter → Add filter logic in API, update component
- Add task sorting → Add sorting logic, update UI

---

### Working on File Uploads

**When to use**: User wants to modify file attachment features

**Key Files**:
- `src/app/api/files/upload/route.ts` - File upload endpoint
- `src/app/api/files/download/[id]/route.ts` - File download endpoint
- `src/app/api/files/thumbnail/[...path]/route.ts` - Thumbnail generation
- `src/shared/components/FileDropzone.tsx` - Upload component
- `src/shared/lib/file-storage.ts` - File storage logic
- `src/shared/lib/file-validation.ts` - File validation logic

**How it Works**:
1. User selects files via `FileDropzone` component
2. Files validated client-side (size, type)
3. Uploaded to server via `/api/files/upload`
4. Server validates again, generates thumbnails
5. Files stored in local filesystem (configurable)
6. File metadata stored in database

**Steps to Modify**:
1. **File validation**: Update `src/shared/lib/file-validation.ts`
2. **Storage logic**: Update `src/shared/lib/file-storage.ts`
3. **Upload endpoint**: Modify `src/app/api/files/upload/route.ts`
4. **UI component**: Update `src/shared/components/FileDropzone.tsx`
5. **Database**: Update `File` model if needed

---

### Working on Tags

**When to use**: User wants to modify tagging system

**Key Files**:
- `src/app/api/tags/` - Tag API endpoints
- `src/app/actions/tags.ts` - Tag server actions
- `src/shared/components/TagInput.tsx` - Tag input component
- `src/shared/components/TagBadge.tsx` - Tag display component

**Database Schema**:
```prisma
model Tag {
  id    String @id @default(uuid())
  name  String @unique
  color String @default("#3B82F6")
  tasks Task[]
}
```

**Common Tasks**:
- Add tag color picker → Update `TagInput` component
- Add tag categories → Update `Tag` model, add category field
- Add tag suggestions → Add endpoint for tag suggestions

---

### Working on Search

**When to use**: User wants to modify search functionality

**Key Files**:
- `src/app/api/search/route.ts` - Search API endpoint
- `src/app/actions/search.ts` - Search server actions
- `src/shared/components/TaskSearchBar.tsx` - Search input component
- `src/app/tasks/search-params.ts` - Search parameter utilities

**How it Works**:
- Full-text search across task titles and descriptions
- Filter by tags, completion status, priority
- Sort by due date, priority, created date
- Server-side search via Prisma queries

**Steps to Modify**:
1. **Search logic**: Update `src/app/api/search/route.ts`
2. **Query building**: Update Prisma queries
3. **UI component**: Update `TaskSearchBar.tsx`
4. **URL params**: Update `search-params.ts` utilities

---

## Important Notes

### This is a Validation Project

- **Primary goal**: Prove framework can build production apps
- **Secondary goal**: Build useful task management features
- **Focus on patterns**: Every feature should demonstrate reusability
- **Quality over quantity**: Better to have fewer, polished features

### Deployed to Production

- **Live URL**: https://task-tracker-production.vercel.app
- **Database**: Production PostgreSQL on Railway
- **Be careful**: Breaking changes affect real users
- **Test first**: Always test locally before deploying

### GitHub OAuth is Mandatory

- **No email/password**: Only GitHub OAuth
- **No social login**: No Google, Facebook, etc.
- **Why?**: Simplicity and validation focus
- **User must have GitHub account**: Required to use app

### Reusability Standards

Every feature must:
1. **Solve real user problem**: Genuine value
2. **Use reusable pattern**: Can be applied to other projects
3. **Be well-tested**: Tests demonstrate reliability
4. **Be documented**: Added to brain for reuse

---

## Research Documentation

This project has **excellent** research documentation. Always check these first:

### `.planning/research/ARCHITECTURE.md` (30,534 bytes)
**What it contains**:
- System architecture overview
- Component relationships
- Data flows
- Technology choices
- Deployment architecture
- Security considerations

**When to read**:
- Before making architectural changes
- Before adding new features
- When understanding how components interact

### `.planning/research/FEATURES.md` (14,023 bytes)
**What it contains**:
- Complete feature inventory
- Feature descriptions
- Implementation status
- Dependencies between features
- Feature complexity ratings

**When to read**:
- When planning new features
- When checking if feature exists
- When understanding feature relationships

### `.planning/research/PITFALLS.md` (20,252 bytes)
**What it contains**:
- Common mistakes made during development
- Solutions and workarounds
- Lessons learned
- Things to avoid

**When to read**:
- **READ THIS FIRST** before starting work
- When encountering strange bugs
- When looking for best practices
- To learn from past mistakes

### `.planning/research/STACK.md` (8,707 bytes)
**What it contains**:
- Complete tech stack
- Package versions
- Why each technology was chosen
- Alternatives considered

**When to read**:
- When adding dependencies
- When understanding tech choices
- When upgrading packages

---

## File Organization Guide

### Project Structure

```
task-tracker/
├── src/
│   ├── app/
│   │   ├── (app)/           # App-shell pages (authenticated)
│   │   │   ├── dashboard/   # Dashboard page
│   │   │   ├── tasks/       # Task pages
│   │   │   └── settings/    # Settings pages
│   │   ├── (auth)/          # Auth pages (unauthenticated)
│   │   │   ├── login/       # Login page
│   │   │   └── welcome/     # Welcome page
│   │   ├── api/             # API endpoints
│   │   │   ├── auth/        # NextAuth
│   │   │   ├── tasks/       # Task CRUD
│   │   │   ├── files/       # File operations
│   │   │   ├── tags/        # Tag operations
│   │   │   └── search/      # Search
│   │   ├── actions/         # Server actions
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── shared/
│   │   ├── components/      # Shared components
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── FileDropzone.tsx
│   │   │   ├── TagInput.tsx
│   │   │   └── ...
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities
│   │   │   ├── auth.ts      # Auth utilities
│   │   │   ├── db.ts        # Database client
│   │   │   ├── file-storage.ts
│   │   │   └── ...
│   │   └── types/           # TypeScript types
│   └── middleware.ts        # NextAuth middleware
├── prisma/
│   ├── schema.prisma        # Database schema
│   └── migrations/          # Database migrations
└── tests/                   # Tests
```

---

## Integration with Framework Documentation

This `CLAUDE.md` is **project-specific** and works with the framework `CLAUDE.md`:

1. **Framework CLAUDE.md** (`/Users/dansidanutz/Desktop/MyWork/CLAUDE.md`):
   - How to use GSD commands
   - How to use framework tools (mw, brain, etc.)
   - General patterns and workflows

2. **This CLAUDE.md** (project-specific):
   - How to work on task-tracker specifically
   - Project-specific workflows
   - File organization
   - Important notes

**When to use which**:
- Use framework CLAUDE.md for: GSD commands, framework tools, general patterns
- Use this CLAUDE.md for: task-tracker specific work, file locations, workflows
- Use research docs for: Deep understanding of architecture, features, pitfalls

---

## Current Status

Check `.planning/STATE.md` for latest status, but generally:
- ✅ Phase 1: Foundation Setup (Complete)
- ✅ Phase 2: Authentication & Profiles (Complete)
- ✅ Phase 3: Core Task Management (Complete)
- ✅ Phase 4: Task Organization & Discovery (Complete)
- ✅ Phase 5: File Attachments (Complete)
- ✅ Phase 6: GitHub Integration & Analytics (Complete)
- ✅ Phase 7: Performance & Quality (Complete)
- ✅ Phase 8: Deployment & Validation (Complete)
- ✅ Deployed to production
- ✅ All audits passed

**Current focus**: Polish, bug fixes, optimization - NOT new features

---

## Testing

**Run Tests**:
```bash
npm test                # Run all tests
npm test -- --watch     # Watch mode
npm test -- --coverage  # With coverage
```

**Manual Testing**:
1. Start dev server: `npm run dev`
2. Open browser: `http://localhost:3000`
3. Test all features manually
4. Check console for errors

**E2E Testing**:
```bash
npm run test:e2e       # Run E2E tests
```

---

## Common Issues

### Database Issues
- **Problem**: Prisma client not generated
- **Solution**: Run `npx prisma generate`

- **Problem**: Database schema out of sync
- **Solution**: Run `npx prisma migrate dev`

### Authentication Issues
- **Problem**: GitHub OAuth not working
- **Solution**: Check `.env` has `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`

- **Problem**: Not authenticated after login
- **Solution**: Check NextAuth configuration in `src/app/api/auth/[...nextauth]/route.ts`

### File Upload Issues
- **Problem**: File upload failing
- **Solution**: Check file size limits in `src/shared/lib/file-validation.ts`

- **Problem**: Thumbnails not generating
- **Solution**: Check Sharp is installed (`npm install sharp`)

---

## When in Doubt

1. **Check research docs first**: `.planning/research/ARCHITECTURE.md`, `FEATURES.md`, `PITFALLS.md`
2. Check `.planning/STATE.md` for current status
3. Check `.planning/PROJECT.md` for project vision
4. Check `.planning/REQUIREMENTS.md` for what's in scope
5. Check framework CLAUDE.md for general patterns
6. Check this CLAUDE.md for project-specific instructions

---

## Summary

This is a **framework validation project** that demonstrates the MyWork framework can build production-ready applications.

**Key Principles**:
- Quality over quantity
- Reusable patterns over one-off solutions
- Polish over new features
- Production-ready code over prototypes

**Focus on**:
- ✅ Bug fixes
- ✅ Performance improvements
- ✅ UX polish
- ✅ Testing
- ❌ NOT new features (unless they demonstrate critical patterns)

**Remember**: Every feature should be reusable in future projects. That's the whole point!

---

## Additional Resources

- **Framework Docs**: `/Users/dansidanutz/Desktop/MyWork/CLAUDE.md`
- **Project Planning**: `.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`
- **Research Docs**: `.planning/research/ARCHITECTURE.md`, `FEATURES.md`, `PITFALLS.md`
- **Current Status**: `.planning/STATE.md`

When working on this project, **always check the research docs first** - they contain invaluable information!
